"""Reference solution -- week 2: composable stop conditions.

Each condition is a tiny, independently testable rule. The loop only knows the
protocol, which is what makes termination auditable: every stop is one decision
with one reason, not a nest of ``break`` statements.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from agentlab.types import CompletionResponse, Message, Usage


@dataclass(slots=True)
class StepState:
    """Everything a stop condition is allowed to look at after one model call."""

    step: int
    response: CompletionResponse
    messages: list[Message]
    usage: Usage


@dataclass(frozen=True, slots=True)
class StopDecision:
    """The verdict of one condition. ``reason`` becomes ``AgentResult.stop_reason``."""

    stop: bool
    reason: str | None = None

    @classmethod
    def continue_(cls) -> StopDecision:
        return cls(stop=False)

    @classmethod
    def halt(cls, reason: str) -> StopDecision:
        return cls(stop=True, reason=reason)


class StopCondition(Protocol):
    """A rule that inspects one step and decides whether the run should end."""

    def check(self, state: StepState) -> StopDecision: ...


class PredicateStop:
    """Stop when a caller-supplied predicate is true."""

    def __init__(self, predicate: Callable[[StepState], bool], *, reason: str = "predicate") -> None:
        self.predicate = predicate
        self.reason = reason

    def check(self, state: StepState) -> StopDecision:
        if self.predicate(state):
            return StopDecision.halt(self.reason)
        return StopDecision.continue_()


class FinishReasonStop:
    """Stop when the model reports one of the configured finish reasons."""

    def __init__(self, *finish_reasons: str) -> None:
        if not finish_reasons:
            raise ValueError("FinishReasonStop needs at least one finish reason")
        self.finish_reasons = frozenset(finish_reasons)

    def check(self, state: StepState) -> StopDecision:
        reason = state.response.finish_reason
        if reason in self.finish_reasons:
            return StopDecision.halt(reason)
        return StopDecision.continue_()


class RepeatedToolCallStop:
    """Stop when the model asks for the exact same tool call batch ``max_repeats`` times in a row."""

    def __init__(self, max_repeats: int = 3) -> None:
        if max_repeats < 2:
            raise ValueError("max_repeats must be at least 2")
        self.max_repeats = max_repeats
        self._last_fingerprint: tuple[tuple[str, str], ...] | None = None
        self._repeats = 0

    def check(self, state: StepState) -> StopDecision:
        calls = state.response.tool_calls
        if not calls:
            self._last_fingerprint = None
            self._repeats = 0
            return StopDecision.continue_()

        fingerprint = tuple(
            sorted((call.name, json.dumps(call.arguments, sort_keys=True, default=str)) for call in calls)
        )
        if fingerprint == self._last_fingerprint:
            self._repeats += 1
        else:
            self._last_fingerprint = fingerprint
            self._repeats = 1
        if self._repeats >= self.max_repeats:
            return StopDecision.halt("stuck:repeated_tool_calls")
        return StopDecision.continue_()


class AnyOf:
    """Evaluate conditions in order and return the first ``halt`` decision."""

    def __init__(self, *conditions: StopCondition) -> None:
        self.conditions: tuple[StopCondition, ...] = conditions

    def check(self, state: StepState) -> StopDecision:
        for condition in self.conditions:
            decision = condition.check(state)
            if decision.stop:
                return decision
        return StopDecision.continue_()


DEFAULT_STOP_CONDITIONS: tuple[StopCondition, ...] = (FinishReasonStop("length", "content_filter"),)
