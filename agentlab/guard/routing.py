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
    raise NotImplementedError("Week 8 lab: implement estimate_call_usd")


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
        raise NotImplementedError("Week 8 lab: implement CostAwareRouter.select")

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
        raise NotImplementedError("Week 8 lab: implement CostAwareRouter.complete")
