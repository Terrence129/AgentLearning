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
        self._usage: dict[str, dict[str, float]] = {}

    def check(self, tenant_id: str, *, tokens: int = 0, usd: float = 0.0) -> None:
        """Raise ``QuotaExceeded`` if a request would exceed any budget.

        Contract:
            - does **not** consume budget (safe to call for admission control);
            - respects fixed-window rollover using ``clock()``;
            - an empty ``tenant_id`` raises ``ValueError`` (the platform must say
              which tenant is spending, never the model);
            - the error message names the exhausted budget and the tenant.
        """
        raise NotImplementedError("Week 8 lab: implement TenantQuotaLimiter.check")

    def charge(self, tenant_id: str, *, tokens: int = 0, usd: float = 0.0) -> None:
        """Check, then consume atomically; refuse without consuming on overflow.

        Contract: same admission rules as ``check``; on success the request,
        ``tokens`` and ``usd`` are added to the current window; on refusal the
        usage is unchanged.
        """
        raise NotImplementedError("Week 8 lab: implement TenantQuotaLimiter.charge")

    def status(self, tenant_id: str) -> QuotaStatus:
        """Return the current window's usage and reset time.

        Contract: an unseen tenant reports zero usage and ``resets_at =
        clock() + window_s`` (its window has not started). ``ValueError`` for an
        empty ``tenant_id``.
        """
        raise NotImplementedError("Week 8 lab: implement TenantQuotaLimiter.status")
