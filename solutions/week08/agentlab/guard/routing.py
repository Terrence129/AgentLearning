"""Cost/latency-aware model routing with fail-safe budget checks.

Model choice is a *governance* decision, not a free parameter of the prompt. The
router is the component that decides which model a request may use, and it must
fail closed at every uncertain point (research 05 §4.4, research 03 §5):

- **Unverifiable cost excludes the candidate.** A model with no known price is
  not "probably cheap": if you cannot price the call, you cannot promise the
  budget, so the candidate is skipped (``unknown_price``).
- **Budgets are checked before the call**, from the ``agentlab.budget.Budget``
  accounting the rest of the course uses, plus per-request ``max_usd``. A model
  that would exceed the remaining budget is excluded (``insufficient_budget``).
- **Ordering is policy.** Default is cheapest first; a caller can declare an
  explicit order (``preferred``) that wins over price -- a recorded production
  bug was a "cheapest" router silently ignoring the caller's deliberate order.
- **Fallback only on transient failures.** ``ProviderError(retryable=True)``
  (429/5xx) moves to the next candidate. A terminal error (validation, auth,
  policy denial) propagates immediately. **Cancellation is never retried**: a
  cancelled request must not be resurrected on another model, or the user's
  cancel becomes a suggestion.

Read first: research 05 §4.4 (router invariants) and research 03 §4.2
(retryable vs terminal, circuit breakers) and §5 (model routing/cascade).

Hints:
- Excluding an unpriceable candidate is the same rule as pricing an unknown
  model at 0.0: both are budget lies. One is just louder.
- Rank once, reuse the ranking for both ``select`` and ``complete``.
- Check the budget again before each fallback attempt: earlier attempts spent it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from agentlab.budget import Budget
from agentlab.errors import ProviderError
from agentlab.guard.errors import RequestCancelled, RoutingError
from agentlab.pricing import ModelPrice
from agentlab.types import CompletionResponse

#: ``(candidate) -> response``; raises ``ProviderError`` on failure.
ModelCall = Callable[["ModelCandidate"], CompletionResponse]


@dataclass(frozen=True, slots=True)
class ModelCandidate:
    """One routable model endpoint.

    Attributes:
        name: logical candidate name used in routing reports and tests.
        model: provider model name (used for pricing and the request).
        price: price table entry, or ``None`` when pricing is unknown -- an
            unknown-price candidate is excluded, never assumed free.
        reliability: historical success rate in ``[0, 1]``.
        p95_latency_ms: measured p95 latency for this model+prompt profile.
        task_types: task types this candidate serves; empty means "any".
    """

    name: str
    model: str
    price: ModelPrice | None
    reliability: float = 1.0
    p95_latency_ms: float = 0.0
    task_types: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class RouteRequest:
    """What the caller needs from a model, including budget and ordering.

    Attributes:
        task_type: routing class (``"chat"``, ``"plan"``, ``"extract"``, ...).
        expected_input_tokens: cost estimate input.
        expected_output_tokens: cost estimate output.
        max_usd: per-request cost ceiling (``None`` = no per-request ceiling).
        max_latency_ms: per-request latency ceiling (``None`` = no ceiling).
        min_reliability: reject candidates below this success rate.
        preferred: explicit candidate order that overrides cheapest-first.
    """

    task_type: str = "chat"
    expected_input_tokens: int = 0
    expected_output_tokens: int = 0
    max_usd: float | None = None
    max_latency_ms: float | None = None
    min_reliability: float = 0.0
    preferred: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RouteDecision:
    """The chosen candidate plus why the others were dropped (audit evidence).

    Attributes:
        candidate: the ranked-first viable candidate.
        excluded: candidate name -> exclusion reason, sorted by name.
    """

    candidate: ModelCandidate
    excluded: Mapping[str, str] = field(default_factory=dict)


def estimate_call_usd(candidate: ModelCandidate, request: RouteRequest) -> float | None:
    """Estimated USD for one call, or ``None`` when the price is unknown.

    Uses ``candidate.price`` and the request's expected token counts; cached
    input tokens are not modelled at routing time.
    """
    price = candidate.price
    if price is None:
        return None
    return (
        request.expected_input_tokens / 1_000_000 * price.input_per_mtok
        + request.expected_output_tokens / 1_000_000 * price.output_per_mtok
    )


class CostAwareRouter:
    """Filters, ranks and executes model candidates under budget constraints.

    Args:
        candidates: every model this agent definition may use, in preference
            order for ties.
        budget: optional run/tenant budget; its remaining USD is a hard ceiling.
        max_attempts: maximum fallback attempts for ``complete`` (must be >= 1).
    """

    def __init__(
        self,
        candidates: Sequence[ModelCandidate],
        *,
        budget: Budget | None = None,
        max_attempts: int = 2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {max_attempts}")
        self.candidates = list(candidates)
        self.budget = budget
        self.max_attempts = max_attempts

    # -- filtering and ranking --------------------------------------------

    def _exclusion_reason(self, candidate: ModelCandidate, request: RouteRequest) -> str | None:
        """Why this candidate cannot serve the request, or ``None`` if it can."""
        if candidate.task_types and request.task_type not in candidate.task_types:
            return "task_type_mismatch"
        if candidate.reliability < request.min_reliability:
            return "below_min_reliability"
        if request.max_latency_ms is not None and candidate.p95_latency_ms > request.max_latency_ms:
            return "latency_exceeds_budget"
        cost = estimate_call_usd(candidate, request)
        if cost is None:
            return "unknown_price"
        if request.max_usd is not None and cost > request.max_usd:
            return "cost_exceeds_request_budget"
        if self.budget is not None:
            remaining = self.budget.remaining_usd
            if remaining is not None and cost > remaining:
                return "insufficient_budget"
        return None

    def _ranked(self, request: RouteRequest) -> tuple[list[ModelCandidate], dict[str, str]]:
        viable: list[tuple[ModelCandidate, float]] = []
        excluded: dict[str, str] = {}
        for candidate in self.candidates:
            reason = self._exclusion_reason(candidate, request)
            if reason is not None:
                excluded[candidate.name] = reason
                continue
            cost = estimate_call_usd(candidate, request)
            assert cost is not None  # _exclusion_reason already rejected unknown prices
            viable.append((candidate, cost))
        if not viable:
            raise RoutingError(
                f"no model candidate can serve {request.task_type!r} within budget; "
                f"excluded={dict(sorted(excluded.items()))}"
            )
        preferred_index = {name: index for index, name in enumerate(request.preferred)}
        viable.sort(
            key=lambda item: (
                preferred_index.get(item[0].name, len(preferred_index)),
                item[1],
                item[0].name,
            )
        )
        return [candidate for candidate, _ in viable], excluded

    # -- public API --------------------------------------------------------

    def select(self, request: RouteRequest) -> RouteDecision:
        """Choose the best viable candidate, or raise ``RoutingError``.

        Contract:
            - excludes, with a reason string, candidates that fail task type,
              reliability, latency, per-request ``max_usd``, remaining
              ``Budget`` USD, or have ``price is None`` (reason
              ``"unknown_price"``);
            - ranks by explicit ``preferred`` order first, then by estimated
              cost, then by name;
            - raises ``RoutingError`` when no candidate is viable, with the
              exclusion map in the message (fail closed, never "pick anything").
        """
        ranked, excluded = self._ranked(request)
        return RouteDecision(candidate=ranked[0], excluded=dict(sorted(excluded.items())))

    def complete(self, request: RouteRequest, call: ModelCall) -> CompletionResponse:
        """Call the ranked candidates until one succeeds.

        Contract:
            - transient ``ProviderError(retryable=True)`` falls back to the next
              viable candidate, up to ``max_attempts`` total attempts;
            - non-retryable ``ProviderError`` propagates immediately;
            - ``RequestCancelled`` propagates immediately (never retried/fallback);
            - budget is re-checked before each attempt; unaffordable candidates
              are skipped; ``BudgetExceeded`` from enforcement propagates;
            - a successful response is charged to the budget when one is set;
            - exhausting the attempts raises ``RoutingError`` chaining the last
              provider error.
        """
        ranked, _excluded = self._ranked(request)
        last_error: ProviderError | None = None
        attempts = 0
        for candidate in ranked:
            if attempts >= self.max_attempts:
                break
            if self._exclusion_reason(candidate, request) is not None:
                continue  # budget shrank since the ranking pass
            if self.budget is not None:
                self.budget.assert_ok(what="model routing")
            attempts += 1
            try:
                response = call(candidate)
            except RequestCancelled:
                raise
            except ProviderError as exc:
                last_error = exc
                if not exc.retryable:
                    raise
                continue
            if self.budget is not None:
                price = candidate.price
                assert price is not None
                self.budget.charge(candidate.model, response.usage, {candidate.model: price})
            return response
        raise RoutingError(
            f"all routed model calls failed after {attempts} attempt(s); last error: {last_error}"
        ) from last_error
