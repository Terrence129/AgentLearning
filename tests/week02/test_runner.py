"""Golden-task tests for ``AgentRunner``: the week 2 acceptance suite.

The plan asks for five golden tasks -- arithmetic, file read, multi-step edit,
graceful tool error, budget stop -- each driven by a scripted provider and a
real built-in tool registry over a temporary workspace. If these pass, the loop
is an agent, not a chat wrapper.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agentlab.budget import Budget
from agentlab.errors import BudgetExceeded, MaxStepsExceeded
from agentlab.loop.runner import AgentRunner
from agentlab.testing import MemorySink, MockProvider, Tracer, text_turn, tool_turn
from agentlab.tools.builtin import build_builtin_tools
from agentlab.tools.registry import ToolRegistry

pytestmark = pytest.mark.week


def _tool_contents(provider: MockProvider, call_index: int) -> list[str]:
    """The tool observations the model saw on the ``call_index``-th model call."""
    messages = provider.calls[call_index].messages
    return [message.content or "" for message in messages if message.role == "tool"]


def test_golden_arithmetic_task(tmp_path: Path) -> None:
    provider = MockProvider(
        [
            tool_turn("calculator", {"expression": "(12 + 8) * 3"}, text="Let me calculate."),
            text_turn("The answer is 60."),
        ]
    )
    result = AgentRunner(provider, build_builtin_tools(tmp_path)).run("What is (12 + 8) * 3?")

    assert result.stop_reason == "answer"
    assert result.answer == "The answer is 60."
    assert result.error is None
    assert len(result.steps) == 2
    assert _tool_contents(provider, 1) == ["60"]


def test_golden_file_read_task(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("the secret word is otter", encoding="utf-8")
    provider = MockProvider(
        [
            tool_turn("read_file", {"path": "notes.txt"}),
            text_turn("It is otter."),
        ]
    )
    result = AgentRunner(provider, build_builtin_tools(tmp_path)).run(
        "Read notes.txt and tell me the secret word."
    )

    assert result.stop_reason == "answer"
    assert result.answer == "It is otter."
    assert _tool_contents(provider, 1) == ["the secret word is otter"]


def test_golden_multi_step_edit_task(tmp_path: Path) -> None:
    provider = MockProvider(
        [
            tool_turn(
                "write_file",
                {"path": "notes/todo.md", "content": "- buy milk\n- ship week 2\n"},
            ),
            tool_turn("read_file", {"path": "notes/todo.md"}, call_id="call_2"),
            text_turn("Updated and verified notes/todo.md."),
        ]
    )
    result = AgentRunner(provider, build_builtin_tools(tmp_path)).run("Create a todo file and verify it.")

    assert result.stop_reason == "answer"
    assert result.answer == "Updated and verified notes/todo.md."
    assert len(result.steps) == 3
    assert (tmp_path / "notes" / "todo.md").read_text(encoding="utf-8") == "- buy milk\n- ship week 2\n"
    assert any("buy milk" in content for content in _tool_contents(provider, 2))


def test_golden_tool_error_is_observable(tmp_path: Path) -> None:
    provider = MockProvider(
        [
            tool_turn("read_file", {"path": "missing.txt"}),
            text_turn("That file does not exist; I did not invent it."),
        ]
    )
    result = AgentRunner(provider, build_builtin_tools(tmp_path)).run("Read missing.txt.")

    assert result.stop_reason == "answer"
    assert result.answer == "That file does not exist; I did not invent it."
    assert result.steps[0].tool_results[0].ok is False
    observations = _tool_contents(provider, 1)
    assert len(observations) == 1
    assert "ERROR" in observations[0]
    assert "missing.txt" in observations[0]


def test_golden_budget_stop_returns_partial_result(tmp_path: Path) -> None:
    provider = MockProvider([tool_turn("list_dir", {"path": "."})], repeat_last=True)
    budget = Budget(max_steps=2)
    result = AgentRunner(provider, build_builtin_tools(tmp_path), budget=budget).run(
        "Keep looking around forever."
    )

    assert result.stop_reason == "budget"
    assert len(result.steps) == 2
    assert isinstance(result.error, BudgetExceeded)
    assert result.answer == ""
    assert len(provider.calls) == 2


def test_runner_opens_with_system_prompt_then_goal() -> None:
    provider = MockProvider([text_turn("ok")])
    AgentRunner(provider, ToolRegistry()).run("hi", system_prompt="be terse")

    opening = provider.calls[0].messages[:2]
    assert [message.role for message in opening] == ["system", "user"]
    assert opening[0].content == "be terse"
    assert opening[1].content == "hi"


def test_runner_emits_run_start_and_run_end_events() -> None:
    sink = MemorySink()
    provider = MockProvider([text_turn("ok")])
    result = AgentRunner(provider, ToolRegistry(), tracer=Tracer(sinks=[sink])).run("hi")

    kinds = [event.kind for event in result.trace_events]
    assert kinds[0] == "run_start"
    assert kinds[-1] == "run_end"
    assert result.trace_events[0].data["goal"] == "hi"
    assert result.trace_events[-1].data["stop_reason"] == "answer"
    assert [event.seq for event in sink.events] == [event.seq for event in result.trace_events]
    assert all(event.run_id == result.trace_events[0].run_id for event in sink.events)


def test_runner_collects_trace_events_without_a_tracer() -> None:
    result = AgentRunner(MockProvider([text_turn("ok")]), ToolRegistry()).run("hi")

    assert [event.kind for event in result.trace_events][0] == "run_start"
    assert [event.kind for event in result.trace_events][-1] == "run_end"


def test_runner_max_steps_returns_partial_answer(tmp_path: Path) -> None:
    provider = MockProvider([tool_turn("list_dir", {"path": "."})], repeat_last=True)
    result = AgentRunner(provider, build_builtin_tools(tmp_path), max_steps=1).run("loop")

    assert result.stop_reason == "max_steps"
    assert len(result.steps) == 1
    assert isinstance(result.error, MaxStepsExceeded)
    assert result.error.steps == 1
