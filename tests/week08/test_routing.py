"""Routing tests: fail-safe budget checks, ordering, transient-only fallback."""

from __future__ import annotations

import pytest
from agentlab.budget import Budget
from agentlab.errors import ProviderError
from agentlab.guard.errors import RequestCancelled, RoutingError
from agentlab.guard.routing import (
    CostAwareRouter,
    ModelCandidate,
    RouteRequest,
    estimate_call_usd,
)
from agentlab.pricing import DEFAULT_PRICES
from agentlab.types import CompletionResponse, Message, Usage

pytestmark = pytest.mark.week

CHEAP = ModelCandidate(
    name="cheap",
    model="gpt-4.1-nano",
    price=DEFAULT_PRICES["gpt-4.1-nano"],
    reliability=0.99,
    p95_latency_ms=400.0,
)
EXPENSIVE = ModelCandidate(
    name="expensive",
    model="gpt-4.1",
    price=DEFAULT_PRICES["gpt-4.1"],
    reliability=0.99,
    p95_latency_ms=1_500.0,
)
REQUEST = RouteRequest(expected_input_tokens=1_000, expected_output_tokens=500)


def _response(model: str = "cheap") -> CompletionResponse:
    return CompletionResponse(
        message=Message.assistant("ok"),
        usage=Usage(input_tokens=1_000, output_tokens=500),
        model=model,
    )


def test_estimate_call_usd_uses_price_and_tokens():
    assert estimate_call_usd(CHEAP, REQUEST) == pytest.approx(0.0003)
    unknown = ModelCandidate(name="unknown", model="mystery-1", price=None)
    assert estimate_call_usd(unknown, REQUEST) is None


def test_select_picks_the_cheapest_viable_candidate():
    router = CostAwareRouter([EXPENSIVE, CHEAP])

    decision = router.select(REQUEST)

    assert decision.candidate.name == "cheap"


def test_declared_order_overrides_price():
    router = CostAwareRouter([CHEAP, EXPENSIVE])
    request = RouteRequest(
        expected_input_tokens=1_000,
        expected_output_tokens=500,
        preferred=("expensive",),
    )

    decision = router.select(request)

    assert decision.candidate.name == "expensive"


def test_unknown_price_candidate_is_excluded():
    unknown = ModelCandidate(name="unknown", model="mystery-1", price=None)
    router = CostAwareRouter([unknown, CHEAP])

    decision = router.select(REQUEST)

    assert decision.candidate.name == "cheap"
    assert decision.excluded["unknown"] == "unknown_price"

    with pytest.raises(RoutingError, match="unknown_price"):
        CostAwareRouter([unknown]).select(REQUEST)


def test_per_request_budget_excludes_expensive_candidate():
    request = RouteRequest(
        expected_input_tokens=1_000,
        expected_output_tokens=500,
        max_usd=0.001,
    )

    decision = CostAwareRouter([EXPENSIVE, CHEAP]).select(request)

    assert decision.candidate.name == "cheap"
    assert decision.excluded["expensive"] == "cost_exceeds_request_budget"


def test_latency_budget_excludes_slow_candidate():
    request = RouteRequest(
        expected_input_tokens=1_000,
        expected_output_tokens=500,
        max_latency_ms=1_000.0,
    )

    decision = CostAwareRouter([EXPENSIVE, CHEAP]).select(request)

    assert decision.candidate.name == "cheap"
    assert decision.excluded["expensive"] == "latency_exceeds_budget"


def test_reliability_floor_excludes_flaky_candidate():
    flaky = ModelCandidate(
        name="flaky",
        model="gpt-4.1-nano",
        price=DEFAULT_PRICES["gpt-4.1-nano"],
        reliability=0.5,
    )
    router = CostAwareRouter([flaky, CHEAP])

    decision = router.select(RouteRequest(min_reliability=0.9, expected_input_tokens=1_000))

    assert decision.candidate.name == "cheap"
    assert decision.excluded["flaky"] == "below_min_reliability"


def test_no_viable_candidate_fails_closed():
    router = CostAwareRouter([EXPENSIVE])
    request = RouteRequest(expected_input_tokens=1_000, max_usd=0.000001)

    with pytest.raises(RoutingError):
        router.select(request)


def test_remaining_budget_excludes_candidates_fail_safe():
    budget = Budget(max_usd=0.0005)
    router = CostAwareRouter([EXPENSIVE, CHEAP], budget=budget)

    decision = router.select(REQUEST)

    assert decision.candidate.name == "cheap"
    assert decision.excluded["expensive"] == "insufficient_budget"

    budget.used_usd = 0.00045  # nearly exhausted: not even the cheap model fits
    with pytest.raises(RoutingError):
        router.select(REQUEST)


def test_transient_failure_falls_back_to_next_candidate():
    attempted: list[str] = []

    def call(candidate: ModelCandidate) -> CompletionResponse:
        attempted.append(candidate.name)
        if candidate.name == "cheap":
            raise ProviderError("rate limited", status=429, retryable=True)
        return _response(candidate.name)

    result = CostAwareRouter([CHEAP, EXPENSIVE]).complete(REQUEST, call)

    assert attempted == ["cheap", "expensive"]
    assert result.model == "expensive"


def test_non_retryable_failure_is_not_retried():
    attempted: list[str] = []

    def call(candidate: ModelCandidate) -> CompletionResponse:
        attempted.append(candidate.name)
        raise ProviderError("invalid request", status=400, retryable=False)

    with pytest.raises(ProviderError):
        CostAwareRouter([CHEAP, EXPENSIVE]).complete(REQUEST, call)

    assert attempted == ["cheap"]


def test_cancellation_is_never_retried():
    attempted: list[str] = []

    def call(candidate: ModelCandidate) -> CompletionResponse:
        attempted.append(candidate.name)
        raise RequestCancelled("user pressed cancel")

    with pytest.raises(RequestCancelled):
        CostAwareRouter([CHEAP, EXPENSIVE]).complete(REQUEST, call)

    assert attempted == ["cheap"]


def test_all_transient_failures_raise_routing_error():
    def call(candidate: ModelCandidate) -> CompletionResponse:
        raise ProviderError("provider down", status=503, retryable=True)

    with pytest.raises(RoutingError):
        CostAwareRouter([CHEAP, EXPENSIVE], max_attempts=2).complete(REQUEST, call)


def test_successful_call_is_charged_to_the_budget():
    budget = Budget(max_usd=1.0)
    router = CostAwareRouter([CHEAP], budget=budget)

    router.complete(REQUEST, lambda candidate: _response(candidate.name))

    assert budget.used_usd == pytest.approx(0.0003)
