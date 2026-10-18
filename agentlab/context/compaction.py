"""Compaction: survive a long task without losing what matters (week 4).

Why this module exists
----------------------
Even with a good priority budget (:mod:`agentlab.context.window`), a long task
eventually produces more history than the window can hold. Compaction trades
transcript fidelity for bounded size: old turns become a short carry-forward
summary, stale tool output is pruned, and the pinned constraints and recent
turns survive verbatim. Anthropic measured 84% token reduction over a 100-turn
eval with context editing + memory, and the cheapest safe compaction is
tool-result clearing (docs/research/01-agent-architecture-sota.md §3.4).

What breaks without it
----------------------
- The run dies when the transcript exceeds the context window.
- A naive "drop the oldest messages" loses the goal and the decisions made
  earlier in the run.
- A naive "summarise everything" loses exact constraints ("$500 cap") because
  summaries paraphrase and numbers drift.
- A summary with no size bound simply re-creates the overflow one turn later.

The contract that makes this testable: the summariser is **injected**. Tests
pass a fake summariser and assert *what* was summarised, *what* survived
verbatim, and that the result is bounded.

Read first: docs/research/01-agent-architecture-sota.md §3.4 and §3.5.

Public surface
--------------
``Summarizer``        protocol: turn old items into a short carry-forward note
``CompactionPolicy``  budget, recent window, summary bound, tool pruning
``CompactionResult``  the post-compaction items plus accounting
``Compactor``         decides whether/how to compact a list of context items
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from agentlab.context.window import ContextItem, TokenEstimator

#: Fixed id for the injected carry-forward summary item.
CARRY_FORWARD_ITEM_ID = "carry-forward"


class Summarizer(Protocol):
    """Anything that can compress old context items into a short note.

    Implementations may be a model call (production), a deterministic template,
    or a fake in a test. ``objective`` is the run's goal so the summariser can
    preserve what is relevant instead of summarising uniformly.
    """

    def summarize(self, items: Sequence[ContextItem], *, objective: str | None = None) -> str: ...


@dataclass(frozen=True, slots=True)
class CompactionPolicy:
    """When and how to compact.

    Attributes:
        max_tokens: context budget the compacted result should aim to fit.
        keep_recent_items: number of non-pinned items kept verbatim (the tail).
        max_summary_tokens: hard bound on the carry-forward note.
        prune_tool_outputs: replace stale tool observations with a short
            placeholder before summarising (the cheapest safe compaction).
        pruned_tool_placeholder: text substituted for pruned tool output.
    """

    max_tokens: int = 8_000
    keep_recent_items: int = 6
    max_summary_tokens: int = 256
    prune_tool_outputs: bool = True
    pruned_tool_placeholder: str = "[tool output pruned]"


@dataclass(frozen=True, slots=True)
class CompactionResult:
    """The outcome of one compaction pass.

    Attributes:
        items: post-compaction items: pinned items first, then the carry-forward
            summary, then the recent verbatim tail.
        summary: the bounded carry-forward note (``""`` when nothing was
            summarised).
        summary_item: the injected summary item (``None`` when nothing was
            summarised).
        summarized_ids: ids of items that went into the summary.
        pruned_ids: ids of tool observations replaced by the placeholder before
            summarisation.
        input_tokens: estimated tokens before compaction.
        output_tokens: estimated tokens after compaction.
    """

    items: tuple[ContextItem, ...]
    summary: str
    summary_item: ContextItem | None
    summarized_ids: tuple[str, ...] = ()
    pruned_ids: tuple[str, ...] = ()
    input_tokens: int = 0
    output_tokens: int = 0


class Compactor:
    """Compacts a list of :class:`ContextItem` without losing pinned state.

    Algorithm contract:
        1. If the items already fit ``policy.max_tokens``, return them unchanged;
           the summariser is not called.
        2. Pinned items are never summarised, never pruned, and always survive.
        3. The last ``keep_recent_items`` non-pinned items are kept verbatim.
        4. Older tool observations are replaced by ``pruned_tool_placeholder``
           *before* summarisation, so the summariser never sees megabytes of
           stale tool output.
        5. The summariser is called at most once, with the older non-pinned
           items (already pruned) and the ``objective``.
        6. The carry-forward note is prefixed with the objective when one is
           supplied, then hard-truncated to ``max_summary_tokens``. Truncation
           appends ``"..."`` and never exceeds the bound.
        7. The result carries the summary as a system item with TASK_STATE
           priority placed immediately after the pinned items.
    """

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
        """True when the estimated size exceeds ``policy.max_tokens``."""
        raise NotImplementedError("Week 4 lab: implement Compactor.should_compact")

    def compact(self, items: Sequence[ContextItem], *, objective: str | None = None) -> CompactionResult:
        """Return a compacted copy of ``items``.

        Raises:
            ContextBudgetError: if the policy is invalid (non-positive
                ``max_tokens``, negative ``keep_recent_items``, or
                ``max_summary_tokens < 1``).
        """
        raise NotImplementedError("Week 4 lab: implement Compactor.compact")
