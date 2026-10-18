"""Tests for priority-aware context-window assembly (week 4 lab)."""

from __future__ import annotations

import pytest
from agentlab.context.window import (
    MESSAGE_OVERHEAD_TOKENS,
    ContextBudgetError,
    ContextItem,
    ContextWindow,
    Priority,
    TokenEstimator,
    WindowPolicy,
)

pytestmark = pytest.mark.week


def est() -> TokenEstimator:
    return TokenEstimator()


def test_estimate_text_rounds_up_to_whole_tokens() -> None:
    estimator = est()
    assert estimator.estimate_text("") == 0
    assert estimator.estimate_text("a") == 1
    assert estimator.estimate_text("abcd") == 1
    assert estimator.estimate_text("abcde") == 2
    assert estimator.estimate_text("a" * 400) == 100


def test_estimate_message_adds_chat_template_overhead() -> None:
    estimator = est()
    item = ContextItem.turn("u1", "user", "abcd")
    assert estimator.estimate_message(item) == 1 + MESSAGE_OVERHEAD_TOKENS


def test_item_constructors_fix_priority_role_and_message_shape() -> None:
    pinned = ContextItem.pinned_constraint("c1", "never refund above $500")
    task = ContextItem.task_state("task", "objective: discount decision")
    turn = ContextItem.turn("u1", "user", "should we discount?")
    observation = ContextItem.observation("obs1", "sales data", tool_call_id="call_1", name="search")
    history = ContextItem.history("h1", "assistant", "earlier answer")

    assert pinned.priority is Priority.PINNED
    assert pinned.role == "system"
    assert task.priority is Priority.TASK_STATE
    assert turn.priority is Priority.RECENT_TURNS
    assert observation.priority is Priority.OBSERVATIONS
    assert observation.role == "tool"
    assert history.priority is Priority.HISTORY

    pinned_message = pinned.to_message()
    tool_message = observation.to_message()
    assert pinned_message.role == "system"
    assert pinned_message.content == "never refund above $500"
    assert tool_message.role == "tool"
    assert tool_message.tool_call_id == "call_1"
    assert tool_message.name == "search"


def test_pinned_constraint_survives_a_tight_budget() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=10))
    pinned = ContextItem.pinned_constraint("cap", "cap $500")
    window.add(pinned)
    for i in range(4):
        window.add(ContextItem.history(f"h{i}", "user", "hi"))

    assembled = window.assemble()

    assert pinned.content in [m.content for m in assembled.messages]
    assert "cap" in assembled.included_ids
    assert set(assembled.dropped) == {"h0", "h1", "h2", "h3"}
    assert not assembled.over_budget


def test_selection_fills_priority_classes_in_order() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=15))
    window.add(ContextItem.pinned_constraint("p", "abcd"))
    window.add(ContextItem.task_state("t", "efgh"))
    window.add(ContextItem.turn("r", "user", "ijkl"))
    window.add(ContextItem.observation("o", "mnop", tool_call_id="call_1"))
    window.add(ContextItem.history("h", "user", "qrst"))

    assembled = window.assemble()

    assert assembled.included_ids == ("p", "t", "r")
    assert assembled.dropped == ("o", "h")
    assert assembled.used_tokens == 15


def test_assembled_messages_preserve_insertion_order() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=1_000))
    window.add(ContextItem.history("h", "assistant", "old answer"))
    window.add(ContextItem.pinned_constraint("p", "never refund above $500"))
    window.add(ContextItem.turn("r", "user", "current question"))

    assembled = window.assemble()

    assert list(assembled.included_ids) == ["h", "p", "r"]
    assert [m.content for m in assembled.messages] == [
        "old answer",
        "never refund above $500",
        "current question",
    ]


def test_within_a_priority_class_newest_items_win() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=10))
    window.add(ContextItem.pinned_constraint("p", "abcd"))
    window.add(ContextItem.history("old", "user", "abcd"))
    window.add(ContextItem.history("new", "user", "efgh"))

    assembled = window.assemble()

    assert "new" in assembled.included_ids
    assert "old" in assembled.dropped


def test_reserve_output_tokens_shrinks_the_input_budget() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=15, reserve_output_tokens=5))
    window.add(ContextItem.pinned_constraint("p", "abcd"))
    window.add(ContextItem.task_state("t", "efgh"))
    window.add(ContextItem.turn("r", "user", "ijkl"))

    assembled = window.assemble()

    assert assembled.budget_tokens == 10
    assert assembled.included_ids == ("p", "t")
    assert "r" in assembled.dropped


def test_pinned_over_budget_is_reported_not_silently_dropped() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=5))
    window.add(ContextItem.pinned_constraint("p1", "abcd"))
    window.add(ContextItem.pinned_constraint("p2", "efgh"))

    assembled = window.assemble()

    assert assembled.included_ids == ("p1", "p2")
    assert assembled.over_budget
    assert assembled.used_tokens > assembled.budget_tokens


def test_invalid_policy_raises_context_budget_error() -> None:
    empty = ContextWindow(WindowPolicy(max_tokens=0))
    with pytest.raises(ContextBudgetError, match="max_tokens"):
        empty.assemble()

    over_reserved = ContextWindow(WindowPolicy(max_tokens=10, reserve_output_tokens=10))
    with pytest.raises(ContextBudgetError, match="reserve_output_tokens"):
        over_reserved.assemble()


def test_duplicate_item_ids_are_rejected() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=1_000))
    window.add(ContextItem.turn("dup", "user", "first"))
    with pytest.raises(ValueError, match="dup"):
        window.add(ContextItem.turn("dup", "user", "second"))


def test_accounting_counts_tokens_in_and_out() -> None:
    window = ContextWindow(WindowPolicy(max_tokens=10))
    pinned = ContextItem.pinned_constraint("p", "abcd")
    kept = ContextItem.task_state("t", "efgh")
    dropped = ContextItem.history("h", "user", "ijkl")
    for item in (pinned, kept, dropped):
        window.add(item)

    assembled = window.assemble()

    assert assembled.used_tokens == sum(est().estimate_message(i) for i in (pinned, kept))
    assert assembled.dropped_tokens == est().estimate_message(dropped)
    assert assembled.budget_tokens == 10
