"""Per-tenant rate limits and quotas: protect the shared pool from one tenant.

Research 03 §4.4 is blunt: rate and cost limits belong **at the gateway, per
tenant**, because the failure mode of missing them is "denial of wallet" -- one
runaway agent (or one malicious tenant) consuming the capacity and budget every
other tenant depends on. The model must not be able to talk past the limit, so
the check is code, not a prompt instruction.

The mechanism is a **fixed-window** limiter per tenant, tracking three budgets:

- requests (rate),
- tokens (context growth),
- USD (spend).

A request must be admitted only if *all* configured budgets have room; admission
is atomic ("check then consume") or the accounting drifts under load. Windows
reset on a fixed schedule (``resets_at``) so cost attribution is explainable to
a customer.

Read first: research 03 §4.4 (multi-tenant isolation table) and §5 (hard budget
caps as a cost lever).

Hints:
- Keep one state entry per tenant: window start, request count, tokens, usd.
- On rollover, start a fresh window rather than decaying: fixed windows are
  easier to explain and to test than token buckets.
- ``check`` must not consume; ``charge`` must not partially consume on refusal.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from agentlab.guard.errors import QuotaExceeded


@dataclass(frozen=True, slots=True)
class QuotaPolicy:
    """Limits for one tenant group, over a fixed window.

    Attributes:
        max_requests: requests allowed per window (must be >= 1).
        window_s: window length in seconds (must be > 0).
        max_tokens: optional token budget per window.
        max_usd: optional spend budget per window, in USD.
    """

    max_requests: int
    window_s: float = 60.0
    max_tokens: int | None = None
    max_usd: float | None = None


@dataclass(frozen=True, slots=True)
class QuotaStatus:
    """Current usage snapshot for one tenant."""

    tenant_id: str
    used_requests: int
    used_tokens: int
    used_usd: float
    resets_at: float


@dataclass(slots=True)
class _Window:
    """Mutable accounting for one tenant's current fixed window."""

    start: float
    requests: int = 0
    tokens: int = 0
    usd: float = 0.0


class TenantQuotaLimiter:
    """Fixed-window, per-tenant limiter for requests, tokens and USD.

    Args:
        policy: the limits to enforce.
        clock: epoch-seconds callable, injected for deterministic tests.
    """

    def __init__(self, policy: QuotaPolicy, *, clock: Callable[[], float] = time.time) -> None:
        if policy.max_requests < 1:
            raise ValueError(f"max_requests must be >= 1, got {policy.max_requests}")
        if policy.window_s <= 0:
            raise ValueError(f"window_s must be > 0, got {policy.window_s}")
        self.policy = policy
        self.clock = clock
        self._windows: dict[str, _Window] = {}

    # -- internals ---------------------------------------------------------

    def _validate(self, tenant_id: str) -> None:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id is required: the platform binds the tenant, never the model")

    def _current(self, tenant_id: str) -> _Window | None:
        """Return the live window (rolling it over if stale), or ``None``."""
        window = self._windows.get(tenant_id)
        if window is None:
            return None
        now = float(self.clock())
        if now - window.start >= self.policy.window_s:
            window = _Window(start=now)
            self._windows[tenant_id] = window
        return window

    def _check_room(self, tenant_id: str, window: _Window | None, *, tokens: int, usd: float) -> None:
        requests = (window.requests if window is not None else 0) + 1
        used_tokens = (window.tokens if window is not None else 0) + tokens
        used_usd = (window.usd if window is not None else 0.0) + usd
        if requests > self.policy.max_requests:
            raise QuotaExceeded(
                f"tenant {tenant_id!r} exceeded its request quota "
                f"({self.policy.max_requests} per {self.policy.window_s:g}s)"
            )
        if self.policy.max_tokens is not None and used_tokens > self.policy.max_tokens:
            raise QuotaExceeded(
                f"tenant {tenant_id!r} exceeded its token quota "
                f"({self.policy.max_tokens} per {self.policy.window_s:g}s)"
            )
        if self.policy.max_usd is not None and used_usd > self.policy.max_usd:
            raise QuotaExceeded(
                f"tenant {tenant_id!r} exceeded its usd quota "
                f"(${self.policy.max_usd:g} per {self.policy.window_s:g}s)"
            )

    # -- public API --------------------------------------------------------

    def check(self, tenant_id: str, *, tokens: int = 0, usd: float = 0.0) -> None:
        """Raise ``QuotaExceeded`` if a request would exceed any budget.

        Contract:
            - does **not** consume budget (safe to call for admission control);
            - respects fixed-window rollover using ``clock()``;
            - an empty ``tenant_id`` raises ``ValueError`` (the platform must say
              which tenant is spending, never the model);
            - the error message names the exhausted budget and the tenant.
        """
        self._validate(tenant_id)
        if tokens < 0 or usd < 0:
            raise ValueError("tokens and usd charges must be non-negative")
        self._check_room(tenant_id, self._current(tenant_id), tokens=tokens, usd=usd)

    def charge(self, tenant_id: str, *, tokens: int = 0, usd: float = 0.0) -> None:
        """Check, then consume atomically; refuse without consuming on overflow.

        Contract: same admission rules as ``check``; on success the request,
        ``tokens`` and ``usd`` are added to the current window; on refusal the
        usage is unchanged.
        """
        self._validate(tenant_id)
        if tokens < 0 or usd < 0:
            raise ValueError("tokens and usd charges must be non-negative")
        window = self._current(tenant_id)
        self._check_room(tenant_id, window, tokens=tokens, usd=usd)
        if window is None:
            window = _Window(start=float(self.clock()))
            self._windows[tenant_id] = window
        window.requests += 1
        window.tokens += tokens
        window.usd += usd

    def status(self, tenant_id: str) -> QuotaStatus:
        """Return the current window's usage and reset time.

        Contract: an unseen tenant reports zero usage and ``resets_at =
        clock() + window_s`` (its window has not started). ``ValueError`` for an
        empty ``tenant_id``.
        """
        self._validate(tenant_id)
        now = float(self.clock())
        window = self._current(tenant_id)
        if window is None:
            return QuotaStatus(
                tenant_id=tenant_id,
                used_requests=0,
                used_tokens=0,
                used_usd=0.0,
                resets_at=now + self.policy.window_s,
            )
        return QuotaStatus(
            tenant_id=tenant_id,
            used_requests=window.requests,
            used_tokens=window.tokens,
            used_usd=window.usd,
            resets_at=window.start + self.policy.window_s,
        )
