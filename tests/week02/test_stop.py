"""Unit tests for composable stop conditions.

These run without a provider: a stop condition is a pure-ish function of one
step, so it can be tested like a parser. Ordering matters because the first halt
wins; that is asserted explicitly.
"""

from __future__ import annotations

import pytest
from agentlab.loop.stop import (
    AnyOf,
    FinishReasonStop,
    PredicateStop,
    RepeatedToolCallStop,
    StepState,
)
from agentlab.types import CompletionResponse, Message, ToolCall, Usage

pytestmark = pytest.mark.week


def _text_state(*, step: int = 1, finish_reason: str = "stop") -> StepState:
    response = CompletionResponse(
        message=Message.assistant("some text"),
        finish_reason=finish_reason,
    )
    return StepState(step=step, response=response, messages=[response.message], usage=Usage())


def _tool_state(
    *,
    step: int = 1,
    name: str = "lookup",
    arguments: dict | None = None,
    finish_reason: str = "tool_calls",
) -> StepState:
    call = ToolCall(id=f"call_{step}", name=name, arguments=arguments or {"q": "x"})
    response = CompletionResponse(
        message=Message.assistant(None, [call]),
        finish_reason=finish_reason,
    )
    return StepState(step=step, response=response, messages=[response.message], usage=Usage())


def test_finish_reason_stop_halts_on_configured_reason() -> None:
    condition = FinishReasonStop("length", "content_filter")

    decision = condition.check(_text_state(finish_reason="length"))

    assert decision.stop is True
    assert decision.reason == "length"


def test_finish_reason_stop_continues_for_other_reasons() -> None:
    condition = FinishReasonStop("length", "content_filter")

    decision = condition.check(_text_state(finish_reason="stop"))

    assert decision.stop is False
    assert decision.reason is None


def test_predicate_stop_halts_with_custom_reason() -> None:
    condition = PredicateStop(lambda state: state.step >= 2, reason="enough_steps")

    assert condition.check(_text_state(step=1)).stop is False
    halted = condition.check(_text_state(step=2))
    assert halted.stop is True
    assert halted.reason == "enough_steps"


def test_any_of_returns_first_matching_reason() -> None:
    first_stops = AnyOf(
        FinishReasonStop("length"),
        PredicateStop(lambda state: True, reason="always"),
    )
    second_stops = AnyOf(
        PredicateStop(lambda state: True, reason="always"),
        FinishReasonStop("length"),
    )
    state = _text_state(finish_reason="length")

    assert first_stops.check(state).reason == "length"
    assert second_stops.check(state).reason == "always"


def test_any_of_continues_when_no_condition_matches() -> None:
    condition = AnyOf(
        FinishReasonStop("length"),
        PredicateStop(lambda state: False, reason="never"),
    )

    decision = condition.check(_text_state())

    assert decision.stop is False


def test_repeated_tool_call_stop_halts_on_nth_identical_request() -> None:
    condition = RepeatedToolCallStop(max_repeats=3)

    decisions = [condition.check(_tool_state(step=step)) for step in range(1, 4)]

    assert [decision.stop for decision in decisions] == [False, False, True]
    assert decisions[-1].reason == "stuck:repeated_tool_calls"


def test_repeated_tool_call_stop_resets_when_the_request_changes() -> None:
    condition = RepeatedToolCallStop(max_repeats=3)
    arguments = [{"q": "a"}, {"q": "a"}, {"q": "b"}, {"q": "b"}, {"q": "b"}]

    decisions = [
        condition.check(_tool_state(step=index, arguments=args))
        for index, args in enumerate(arguments, start=1)
    ]

    assert [decision.stop for decision in decisions] == [False, False, False, False, True]


def test_repeated_tool_call_stop_ignores_and_resets_on_text_responses() -> None:
    condition = RepeatedToolCallStop(max_repeats=2)

    first = condition.check(_tool_state(step=1))
    text = condition.check(_text_state(step=2))
    after_text = condition.check(_tool_state(step=3))

    assert first.stop is False
    assert text.stop is False
    assert after_text.stop is False
