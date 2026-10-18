"""Tests for bounded compaction with pinned-state retention (week 4 lab)."""

from __future__ import annotations

from collections.abc import Sequence

import pytest
from agentlab.context.compaction import (
    CARRY_FORWARD_ITEM_ID,
    CompactionPolicy,
    Compactor,
)
from agentlab.context.window import (
    ContextBudgetError,
    ContextItem,
    Priority,
    TokenEstimator,
)

pytestmark = pytest.mark.week


class RecordingSummarizer:
    """Fake summarizer: records every call and replays a fixed reply."""

    def __init__(self, reply: str = "carry-forward: decisions and constraints") -> None:
        self.reply = reply
        self.calls: list[dict] = []

    def summarize(self, items: Sequence[ContextItem], *, objective: str | None = None) -> str:
        self.calls.append({"ids": [item.id for item in items], "objective": objective, "items": list(items)})
        return self.reply


def est() -> TokenEstimator:
    return TokenEstimator()


def history_items(count: int, *, prefix: str = "h") -> list[ContextItem]:
    return [
        ContextItem.history(f"{prefix}{i}", "user", f"history message number {i} with some words")
        for i in range(count)
    ]


def make_input(*, observations_at: tuple[int, ...] = ()) -> list[ContextItem]:
    items = [ContextItem.pinned_constraint("pin", "never refund above $500")]
    for i in range(8):
        if i in observations_at:
            items.append(ContextItem.observation(f"obs{i}", "x" * 400, tool_call_id=f"call_{i}"))
        else:
            items.append(ContextItem.history(f"h{i}", "user", f"history message number {i}"))
    return items


def test_should_compact_is_false_under_budget() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(CompactionPolicy(max_tokens=10_000), summarizer)
    assert compactor.should_compact(history_items(3)) is False


def test_should_compact_is_true_over_budget() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(CompactionPolicy(max_tokens=10), summarizer)
    assert compactor.should_compact(make_input()) is True


def test_under_budget_compaction_is_an_identity_pass() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(CompactionPolicy(max_tokens=10_000), summarizer)
    items = make_input()

    result = compactor.compact(items)

    assert result.items == tuple(items)
    assert result.summary == ""
    assert result.summary_item is None
    assert summarizer.calls == []
    assert result.input_tokens == result.output_tokens > 0


def test_old_items_are_summarised_while_recent_items_stay_verbatim() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(
        CompactionPolicy(max_tokens=80, keep_recent_items=2, max_summary_tokens=64),
        summarizer,
    )
    items = make_input()

    result = compactor.compact(items)

    assert len(summarizer.calls) == 1
    assert summarizer.calls[0]["ids"] == ["h0", "h1", "h2", "h3", "h4", "h5"]
    assert result.summarized_ids == ("h0", "h1", "h2", "h3", "h4", "h5")
    assert [item.id for item in result.items] == ["pin", CARRY_FORWARD_ITEM_ID, "h6", "h7"]
    assert result.items[1].priority is Priority.TASK_STATE
    assert result.items[1].role == "system"
    assert result.summary_item is not None
    assert result.summary_item.content == result.summary


def test_pinned_constraints_survive_compaction() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(CompactionPolicy(max_tokens=60, keep_recent_items=2), summarizer)
    items = make_input()

    result = compactor.compact(items)

    contents = [item.content for item in result.items]
    assert "never refund above $500" in contents
    assert "pin" not in summarizer.calls[0]["ids"]
    assert "pin" in [item.id for item in result.items]


def test_carry_forward_summary_is_hard_bounded() -> None:
    summarizer = RecordingSummarizer(reply="y" * 5_000)
    compactor = Compactor(
        CompactionPolicy(max_tokens=60, keep_recent_items=2, max_summary_tokens=10), summarizer
    )

    result = compactor.compact(make_input())

    assert len(result.summary) <= 10 * 4
    assert est().estimate_text(result.summary) <= 10


def test_objective_is_carried_forward_into_the_note() -> None:
    summarizer = RecordingSummarizer(reply="decisions: discount approved at 10%")
    compactor = Compactor(CompactionPolicy(max_tokens=60, keep_recent_items=2), summarizer)

    result = compactor.compact(make_input(), objective="decide the enterprise discount")

    assert result.summary.startswith("objective: decide the enterprise discount")
    assert summarizer.calls[0]["objective"] == "decide the enterprise discount"


def test_stale_tool_outputs_are_pruned_before_summarising() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(CompactionPolicy(max_tokens=120, keep_recent_items=2), summarizer)
    items = make_input(observations_at=(1,))

    result = compactor.compact(items)

    assert result.pruned_ids == ("obs1",)
    summary_input = {item.id: item for item in summarizer.calls[0]["items"]}
    assert "obs1" in summary_input
    assert summary_input["obs1"].content == "[tool output pruned]"
    assert result.output_tokens < result.input_tokens


def test_tool_output_pruning_can_be_disabled() -> None:
    summarizer = RecordingSummarizer()
    compactor = Compactor(
        CompactionPolicy(max_tokens=120, keep_recent_items=2, prune_tool_outputs=False),
        summarizer,
    )

    result = compactor.compact(make_input(observations_at=(1,)))

    assert result.pruned_ids == ()
    summary_input = {item.id: item for item in summarizer.calls[0]["items"]}
    assert summary_input["obs1"].content == "x" * 400


@pytest.mark.parametrize(
    "policy",
    [
        CompactionPolicy(max_tokens=0),
        CompactionPolicy(max_tokens=100, keep_recent_items=-1),
        CompactionPolicy(max_tokens=100, max_summary_tokens=0),
    ],
)
def test_invalid_compaction_policy_is_rejected(policy: CompactionPolicy) -> None:
    compactor = Compactor(policy, RecordingSummarizer())
    with pytest.raises(ContextBudgetError):
        compactor.compact(make_input())


def test_compaction_shrinks_the_estimated_token_footprint() -> None:
    summarizer = RecordingSummarizer(reply="short note")
    compactor = Compactor(CompactionPolicy(max_tokens=80, keep_recent_items=2), summarizer)
    items = make_input()

    result = compactor.compact(items)

    assert result.output_tokens < result.input_tokens
    assert result.input_tokens == sum(est().estimate_message(item) for item in items)
