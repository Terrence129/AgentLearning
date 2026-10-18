"""Compaction: survive a long task without losing what matters (week 4).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from agentlab.context.window import (
    CHARS_PER_TOKEN,
    ContextBudgetError,
    ContextItem,
    Priority,
    TokenEstimator,
)

CARRY_FORWARD_ITEM_ID = "carry-forward"


class Summarizer(Protocol):
    """Anything that can compress old context items into a short note."""

    def summarize(self, items: Sequence[ContextItem], *, objective: str | None = None) -> str: ...


@dataclass(frozen=True, slots=True)
class CompactionPolicy:
    """When and how to compact."""

    max_tokens: int = 8_000
    keep_recent_items: int = 6
    max_summary_tokens: int = 256
    prune_tool_outputs: bool = True
    pruned_tool_placeholder: str = "[tool output pruned]"


@dataclass(frozen=True, slots=True)
class CompactionResult:
    """The outcome of one compaction pass."""

    items: tuple[ContextItem, ...]
    summary: str
    summary_item: ContextItem | None
    summarized_ids: tuple[str, ...] = ()
    pruned_ids: tuple[str, ...] = ()
    input_tokens: int = 0
    output_tokens: int = 0


def _bound_text(text: str, max_tokens: int) -> str:
    """Hard-bound ``text`` so the token estimator never exceeds ``max_tokens``."""
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[: max_chars - 3] + "..."


class Compactor:
    """Compacts a list of ContextItems without losing pinned state."""

    def __init__(
        self,
        policy: CompactionPolicy,
        summarizer: Summarizer,
        estimator: TokenEstimator | None = None,
    ) -> None:
        self.policy = policy
        self.summarizer = summarizer
        self.estimator = estimator or TokenEstimator()

    def should_compact(self, items: Sequence[ContextItem]) -> bool:
        total = sum(self.estimator.estimate_message(item) for item in items)
        return total > self.policy.max_tokens

    def compact(self, items: Sequence[ContextItem], *, objective: str | None = None) -> CompactionResult:
        self._validate()
        items = list(items)
        input_tokens = sum(self.estimator.estimate_message(item) for item in items)

        if not self.should_compact(items):
            return CompactionResult(
                items=tuple(items),
                summary="",
                summary_item=None,
                input_tokens=input_tokens,
                output_tokens=input_tokens,
            )

        pinned = [item for item in items if item.priority is Priority.PINNED]
        evictable = [item for item in items if item.priority is not Priority.PINNED]
        keep = min(self.policy.keep_recent_items, len(evictable))
        recent = evictable[len(evictable) - keep :] if keep else []
        older = evictable[: len(evictable) - keep]

        pruned_ids: list[str] = []
        summarisable: list[ContextItem] = []
        for item in older:
            if self.policy.prune_tool_outputs and item.priority is Priority.OBSERVATIONS:
                pruned_ids.append(item.id)
                summarisable.append(
                    ContextItem(
                        id=item.id,
                        content=self.policy.pruned_tool_placeholder,
                        priority=item.priority,
                        role=item.role,
                        tool_call_id=item.tool_call_id,
                        name=item.name,
                    )
                )
            else:
                summarisable.append(item)

        summary = ""
        summary_item: ContextItem | None = None
        if summarisable:
            raw = self.summarizer.summarize(summarisable, objective=objective)
            note = f"objective: {objective}\n{raw}" if objective else raw
            summary = _bound_text(note, self.policy.max_summary_tokens)
            summary_item = ContextItem(
                id=CARRY_FORWARD_ITEM_ID,
                content=summary,
                priority=Priority.TASK_STATE,
                role="system",
            )

        result_items = [*pinned, *([summary_item] if summary_item is not None else []), *recent]
        output_tokens = sum(self.estimator.estimate_message(item) for item in result_items)
        return CompactionResult(
            items=tuple(result_items),
            summary=summary,
            summary_item=summary_item,
            summarized_ids=tuple(item.id for item in summarisable),
            pruned_ids=tuple(pruned_ids),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def _validate(self) -> None:
        if self.policy.max_tokens <= 0:
            raise ContextBudgetError(f"compaction: max_tokens must be positive, got {self.policy.max_tokens}")
        if self.policy.keep_recent_items < 0:
            raise ContextBudgetError(
                f"compaction: keep_recent_items must be >= 0, got {self.policy.keep_recent_items}"
            )
        if self.policy.max_summary_tokens < 1:
            raise ContextBudgetError(
                f"compaction: max_summary_tokens must be >= 1, got {self.policy.max_summary_tokens}"
            )
