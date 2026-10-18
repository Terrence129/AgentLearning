"""Behaviour tests for ``react.run_loop`` -- the loop mechanism itself.

Everything is driven by ``MockProvider``: the tests script *behaviour* ("the
model asks to add, then answers") and assert on observable contracts (the
transcript, the outcome, trace events, budget counters), never on internals.
"""

from __future__ import annotations

from typing import Any

import pytest
from agentlab.budget import Budget
from agentlab.errors import BudgetExceeded, MaxStepsExceeded, ProviderError
from agentlab.loop.react import run_loop
from agentlab.loop.stop import PredicateStop
from agentlab.testing import MemorySink, MockProvider, Tracer, text_turn, tool_turn
from agentlab.tools.registry import Tool, ToolRegistry, schema_from_model
from agentlab.types import Message, Usage
from pydantic import BaseModel

pytestmark = pytest.mark.week


class AddInput(BaseModel):
    a: int
    b: int


def _registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="add",
            description="Add two integers",
            parameters=schema_from_model(AddInput),
            handler=lambda args: args.a + args.b,
            input_model=AddInput,
        )
    )
    return registry


def _run(
    turns: list[Any],
    *,
    registry: ToolRegistry | None = None,
    messages: list[Message] | None = None,
    budget: Budget | None = None,
    max_steps: int = 10,
    tracer: Tracer | None = None,
    stop_conditions: tuple[Any, ...] | None = None,
    repeat_last: bool = False,
) -> tuple[MockProvider, Any]:
    provider = MockProvider(turns, repeat_last=repeat_last)
    outcome = run_loop(
        provider,
        registry if registry is not None else _registry(),
        messages if messages is not None else [Message.user("goal")],
        tracer=tracer,
        budget=budget,
        max_steps=max_steps,
        stop_conditions=stop_conditions,
    )
    return provider, outcome


def test_loop_appends_assistant_then_tool_observations_in_order() -> None:
    _, outcome = _run([tool_turn("add", {"a": 1, "b": 2}), text_turn("the answer is 3")])

    assert outcome.stop_reason == "answer"
    assert [message.role for message in outcome.messages] == ["user", "assistant", "tool", "assistant"]
    tool_message = outcome.messages[2]
    assert tool_message.tool_call_id == "call_1"
    assert tool_message.name == "add"
    assert tool_message.content == "3"
    assert outcome.messages[1].tool_calls[0].arguments == {"a": 1, "b": 2}
    assert len(outcome.steps) == 2
    assert outcome.steps[0].tool_results[0].ok is True
    assert outcome.steps[1].tool_results == []
    assert outcome.error is None


def test_loop_checks_budget_at_top_before_the_next_model_call() -> None:
    provider, outcome = _run(
        [tool_turn("add", {"a": 1, "b": 1}), text_turn("unreachable: budget is gone")],
        budget=Budget(max_steps=1),
    )

    assert outcome.stop_reason == "budget"
    assert len(outcome.steps) == 1
    assert isinstance(outcome.error, BudgetExceeded)
    assert len(provider.calls) == 1  # the second model call never happened


def test_loop_returns_answer_for_text_only_response() -> None:
    _, outcome = _run([text_turn("hello")])

    assert outcome.stop_reason == "answer"
    assert len(outcome.steps) == 1
    assert outcome.messages[-1].content == "hello"
    assert outcome.messages[-1].tool_calls == []


def test_loop_feeds_unknown_tool_error_back_as_observation() -> None:
    provider, outcome = _run([tool_turn("rm_rf", {}), text_turn("I should not have done that.")])

    assert outcome.stop_reason == "answer"
    assert len(provider.calls) == 2
    observation = outcome.messages[2]
    assert observation.role == "tool"
    assert "unknown tool" in (observation.content or "")
    assert outcome.steps[0].tool_results[0].ok is False


def test_loop_executes_parallel_tool_calls_in_request_order() -> None:
    _, outcome = _run(
        [
            tool_turn("add", {"a": 1, "b": 2}, extra_calls=[("add", {"a": 10, "b": 5})]),
            text_turn("done"),
        ]
    )

    tool_messages = [message for message in outcome.messages if message.role == "tool"]
    assert [message.tool_call_id for message in tool_messages] == ["call_1", "call_2"]
    assert [message.content for message in tool_messages] == ["3", "15"]


def test_loop_stops_on_truncated_response_by_default() -> None:
    provider, outcome = _run([text_turn("half an ans", finish_reason="length")])

    assert outcome.stop_reason == "length"
    assert len(provider.calls) == 1
    assert len(outcome.steps) == 1


def test_loop_honours_custom_stop_condition_before_executing_tools() -> None:
    condition = PredicateStop(lambda state: state.step >= 1, reason="custom_stop")
    provider, outcome = _run([tool_turn("add", {"a": 1, "b": 1})], stop_conditions=(condition,))

    assert outcome.stop_reason == "custom_stop"
    assert len(provider.calls) == 1
    assert outcome.steps[0].tool_results == []
    assert len(outcome.messages) == 2  # no tool observation appended


def test_loop_max_steps_carries_partial_result() -> None:
    _, outcome = _run(
        [tool_turn("add", {"a": 1, "b": 1})],
        max_steps=2,
        repeat_last=True,
    )

    assert outcome.stop_reason == "max_steps"
    assert len(outcome.steps) == 2
    assert isinstance(outcome.error, MaxStepsExceeded)
    assert outcome.error.steps == 2
    assert outcome.error.last_message is not None


def test_loop_provider_error_stops_with_error_reason() -> None:
    _, outcome = _run([])

    assert outcome.stop_reason == "error"
    assert isinstance(outcome.error, ProviderError)
    assert outcome.steps == []


def test_loop_charges_budget_for_each_model_call() -> None:
    budget = Budget(max_input_tokens=1_000)
    _, outcome = _run(
        [tool_turn("add", {"a": 1, "b": 1}, usage=Usage(10, 5)), text_turn("done", usage=Usage(4, 2))],
        budget=budget,
    )

    assert budget.used_input_tokens == 14
    assert budget.used_output_tokens == 7
    assert budget.steps == 2
    assert (outcome.usage.input_tokens, outcome.usage.output_tokens) == (14, 7)


def test_loop_emits_step_model_and_tool_trace_events() -> None:
    sink = MemorySink()
    tracer = Tracer(sinks=[sink])
    _, outcome = _run([tool_turn("add", {"a": 1, "b": 2}), text_turn("3")], tracer=tracer)

    kinds = [event.kind for event in outcome.events]
    assert kinds[0] == "step"
    assert kinds.count("model_call") == 2
    assert kinds.count("tool_call") == 1
    assert kinds.count("tool_result") == 1
    assert [event.name for event in outcome.events if event.kind == "step"] == ["step-1", "step-2"]
    model_call = next(event for event in outcome.events if event.kind == "model_call")
    assert model_call.name == "mock"
    assert model_call.data["step"] == 1
    tool_call = next(event for event in outcome.events if event.kind == "tool_call")
    assert tool_call.data["arguments"] == {"a": 1, "b": 2}
    tool_result = next(event for event in outcome.events if event.kind == "tool_result")
    assert tool_result.data["ok"] is True
    # the caller's sink observed the same events the outcome reports
    assert [event.seq for event in sink.events] == [event.seq for event in outcome.events]
