"""Reference solution -- week 2: the agent loop.

The shape is the canonical one from research 01 §1.1. The three invariants the
tests protect are marked with comments: top-of-iteration budget checks,
termination-as-data, and errors-as-observations.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass

from agentlab.budget import Budget
from agentlab.errors import AgentError, BudgetExceeded, MaxStepsExceeded
from agentlab.loop.stop import DEFAULT_STOP_CONDITIONS, StepState, StopCondition
from agentlab.providers.base import Provider
from agentlab.tools.registry import ToolRegistry, ToolResult
from agentlab.trace import TraceEvent, Tracer
from agentlab.types import CompletionRequest, Message, Usage


@dataclass(slots=True)
class StepRecord:
    """One completed loop iteration: one model call plus the tools it requested."""

    index: int
    assistant: Message
    tool_results: list[ToolResult]
    usage: Usage
    finish_reason: str


@dataclass(slots=True)
class LoopOutcome:
    """How the loop ended, with enough state to explain and audit the run."""

    messages: list[Message]
    steps: list[StepRecord]
    usage: Usage
    stop_reason: str
    events: list[TraceEvent]
    error: AgentError | None = None


def run_loop(
    provider: Provider,
    registry: ToolRegistry,
    messages: list[Message],
    *,
    tracer: Tracer | None = None,
    budget: Budget | None = None,
    max_steps: int = 10,
    stop_conditions: Sequence[StopCondition] | None = None,
) -> LoopOutcome:
    """Run model -> tools -> observations until the loop terminates."""
    # A sink-less tracer keeps event collection working for callers that do not
    # care about sinks; the runner passes its own tracer so ids/sequences line up.
    tracer = tracer or Tracer()
    events: list[TraceEvent] = []
    steps: list[StepRecord] = []
    running_usage = Usage()
    conditions = tuple(stop_conditions) if stop_conditions is not None else DEFAULT_STOP_CONDITIONS

    def emit(kind: str, name: str, data: dict[str, object], *, duration_ms: float | None = None) -> None:
        events.append(tracer.emit(kind, name, data, duration_ms=duration_ms))

    def outcome(stop_reason: str, error: AgentError | None = None) -> LoopOutcome:
        return LoopOutcome(
            messages=messages,
            steps=steps,
            usage=running_usage,
            stop_reason=stop_reason,
            events=events,
            error=error,
        )

    for step_number in range(1, max_steps + 1):
        # Invariant 1: check the budget before spending anything on this turn.
        if budget is not None:
            try:
                budget.assert_ok(what="agent run")
            except BudgetExceeded as exc:
                return outcome("budget", exc)

        emit("step", f"step-{step_number}", {"step": step_number})
        request = CompletionRequest(
            messages=messages,
            tools=registry.specs(),
            model=provider.model,
        )

        started = time.perf_counter()
        try:
            response = provider.complete(request)
        except AgentError as exc:
            # Invariant 2: expected failures end the run as data, not exceptions.
            return outcome("error", exc)
        duration_ms = (time.perf_counter() - started) * 1000

        usage = response.usage
        running_usage = running_usage + usage
        if budget is not None:
            budget.charge(provider.model, usage)

        emit(
            "model_call",
            provider.name,
            {
                "step": step_number,
                "model": response.model or provider.model,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cached_input_tokens": usage.cached_input_tokens,
                "finish_reason": response.finish_reason,
            },
            duration_ms=duration_ms,
        )
        messages.append(response.message)

        step = StepRecord(
            index=step_number,
            assistant=response.message,
            tool_results=[],
            usage=usage,
            finish_reason=response.finish_reason,
        )
        steps.append(step)
        if budget is not None:
            budget.add_step()

        state = StepState(
            step=step_number,
            response=response,
            messages=messages,
            usage=running_usage,
        )
        for condition in conditions:
            decision = condition.check(state)
            if decision.stop:
                return outcome(decision.reason or "stop_condition")

        if not response.tool_calls:
            return outcome("answer")

        tool_results: list[ToolResult] = []
        for call in response.tool_calls:
            emit(
                "tool_call",
                call.name,
                {"step": step_number, "tool_call_id": call.id, "arguments": call.arguments},
            )
            result = registry.invoke(call.name, call.arguments)
            # Invariant 3: failures are observations, not crashes.
            emit(
                "tool_result",
                call.name,
                {
                    "step": step_number,
                    "tool_call_id": call.id,
                    "ok": result.ok,
                    "truncated": result.truncated,
                    "error": result.error,
                    "chars": len(result.output),
                },
            )
            messages.append(Message.tool_result(call.id, result.output, name=call.name))
            tool_results.append(result)
        step.tool_results = tool_results

    error = MaxStepsExceeded(
        f"agent run hit its {max_steps}-step ceiling",
        steps=len(steps),
        last_message=steps[-1].assistant if steps else None,
    )
    return outcome("max_steps", error)
