"""Composable stop conditions for the agent loop -- YOUR WEEK 2 BUILD.

Why this exists: a loop without termination conditions is a ``while True`` with
an invoice attached. Natural termination ("the assistant replied without asking
for a tool") is only one ending; the dangerous ones are silent -- a model that
asks for the same tool forty times, a response truncated by ``max_tokens``, a
content filter that returns an empty turn. Encoding each rule as a small object
keeps the loop itself about control flow and makes every rule unit-testable
without a model.

Read first: ``docs/research/01-agent-architecture-sota.md`` §1.6 (budgets and
termination) and §1.1 (the canonical loop).

The loop calls each condition once per step, in order, after the model call and
before any tool executes. The first ``StopDecision(stop=True)`` wins.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from agentlab.types import CompletionResponse, Message, Usage


@dataclass(slots=True)
class StepState:
    """Everything a stop condition is allowed to look at after one model call."""

    step: int
    """1-based iteration number."""
    response: CompletionResponse
    """The assistant response that just arrived."""
    messages: list[Message]
    """The transcript, including the response."""
    usage: Usage
    """Cumulative usage of the run so far."""


@dataclass(frozen=True, slots=True)
class StopDecision:
    """The verdict of one condition. ``reason`` becomes ``AgentResult.stop_reason``."""

    stop: bool
    reason: str | None = None

    @classmethod
    def continue_(cls) -> StopDecision:
        """The run should keep going."""
        raise NotImplementedError("Week 2 lab: implement StopDecision.continue_")

    @classmethod
    def halt(cls, reason: str) -> StopDecision:
        """The run should stop for ``reason``."""
        raise NotImplementedError("Week 2 lab: implement StopDecision.halt")


class StopCondition(Protocol):
    """A rule that inspects one step and decides whether the run should end."""

    def check(self, state: StepState) -> StopDecision:
        """Return ``halt`` or ``continue_``; must be cheap and side-effect free
        (except for intentional internal bookkeeping such as repeat counting)."""
        ...


class PredicateStop:
    """Stop when a caller-supplied predicate is true.

    Useful for task-specific rules without subclassing anything::

        PredicateStop(lambda state: "DONE" in (state.response.text or ""), reason="done_marker")
    """

    def __init__(self, predicate: Callable[[StepState], bool], *, reason: str = "predicate") -> None:
        self.predicate = predicate
        self.reason = reason

    def check(self, state: StepState) -> StopDecision:
        """``halt(self.reason)`` when ``predicate(state)`` is true."""
        raise NotImplementedError("Week 2 lab: implement PredicateStop.check")


class FinishReasonStop:
    """Stop when the model reports one of the configured finish reasons.

    Example: ``FinishReasonStop("length", "content_filter")`` ends a run whose
    output was truncated or filtered instead of accepting half an answer.
    The stop reason is the finish reason itself (e.g. ``"length"``).
    """

    def __init__(self, *finish_reasons: str) -> None:
        if not finish_reasons:
            raise ValueError("FinishReasonStop needs at least one finish reason")
        self.finish_reasons = frozenset(finish_reasons)

    def check(self, state: StepState) -> StopDecision:
        """``halt(finish_reason)`` when ``state.response.finish_reason`` matches."""
        raise NotImplementedError("Week 2 lab: implement FinishReasonStop.check")


class RepeatedToolCallStop:
    """Stop when the model asks for the exact same tool call ``max_repeats`` times in a row.

    This is the cheap "no progress" detector from research 01 §1.6: a confused
    model can politely repeat one call until the budget is gone. The fingerprint
    is ``(tool name, canonical JSON of arguments)`` for the whole parallel-call
    batch; any change resets the counter. ``max_repeats`` counts *requests*, so
    ``max_repeats=3`` stops on the third identical request.

    Pure text responses (no tool calls) reset the counter -- the loop's natural
    termination handles them.

    The stop reason is ``"stuck:repeated_tool_calls"``.
    """

    def __init__(self, max_repeats: int = 3) -> None:
        if max_repeats < 2:
            raise ValueError("max_repeats must be at least 2")
        self.max_repeats = max_repeats
        self._last_fingerprint: tuple[tuple[str, str], ...] | None = None
        self._repeats = 0

    def check(self, state: StepState) -> StopDecision:
        """Track the fingerprint and stop once the batch has repeated ``max_repeats`` times."""
        raise NotImplementedError("Week 2 lab: implement RepeatedToolCallStop.check")


class AnyOf:
    """Evaluate conditions in order and return the first ``halt`` decision.

    Order matters and is observable: put cheap/urgent rules first. With no
    conditions (or none matching) the decision is ``continue_``.
    """

    def __init__(self, *conditions: StopCondition) -> None:
        self.conditions: tuple[StopCondition, ...] = conditions

    def check(self, state: StepState) -> StopDecision:
        """Return the first condition's halt decision, else ``continue_``."""
        raise NotImplementedError("Week 2 lab: implement AnyOf.check")


#: Conditions the runner applies unless a caller supplies its own tuple.
#: A truncated or filtered response should end the run instead of being treated
#: as a final answer.
DEFAULT_STOP_CONDITIONS: tuple[StopCondition, ...] = (FinishReasonStop("length", "content_filter"),)
