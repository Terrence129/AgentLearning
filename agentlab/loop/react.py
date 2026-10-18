"""The core single-agent loop -- YOUR WEEK 2 BUILD (the most important file).

The canonical loop from research 01 §1.1, reduced to one file:

    budget check at the top
    -> model call
    -> stop conditions
    -> no tool calls?      -> final answer
    -> execute tools       -> append observations -> repeat

Three decisions make this file different from a toy:

1. **Termination is data.** Expected endings are reported in
   ``LoopOutcome.stop_reason`` with a typed cause in ``LoopOutcome.error``;
   they are not exceptions. Programming errors still raise, so bugs stay loud.
2. **The budget check is at the top of the iteration**, before the model call.
   A check after the call always overspends by one call (and its tool effects).
3. **Tool errors are observations.** A failed tool result is appended exactly
   like a successful one, so the model can correct itself. The loop never
   crashes because a tool returned ``ok=False``.

Read first: ``docs/research/01-agent-architecture-sota.md`` §1.1-1.7 and
``docs/concepts/01-agent-loop.md``. Stop rules live in ``agentlab/loop/stop.py``;
the user-facing wrapper lives in ``agentlab/loop/runner.py``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from agentlab.budget import Budget
from agentlab.errors import AgentError
from agentlab.loop.stop import StopCondition
from agentlab.providers.base import Provider
from agentlab.tools.registry import ToolRegistry, ToolResult
from agentlab.trace import TraceEvent, Tracer
from agentlab.types import Message, Usage


@dataclass(slots=True)
class StepRecord:
    """One completed loop iteration: one model call plus the tools it requested."""

    index: int
    """1-based iteration number."""
    assistant: Message
    """The assistant message exactly as it entered the transcript."""
    tool_results: list[ToolResult]
    """One result per requested tool call, in request order. Empty for a final answer."""
    usage: Usage
    """Token usage of this model call only."""
    finish_reason: str
    """The provider finish reason for this call."""


@dataclass(slots=True)
class LoopOutcome:
    """How the loop ended, with enough state to explain and audit the run."""

    messages: list[Message]
    """The full transcript after the run."""
    steps: list[StepRecord]
    """Every completed step, in order."""
    usage: Usage
    """Usage summed over all model calls."""
    stop_reason: str
    """``"answer"`` | ``"budget"`` | ``"max_steps"`` | ``"error"``, or the reason a
    stop condition returned (e.g. ``"length"``, ``"stuck:repeated_tool_calls"``)."""
    events: list[TraceEvent]
    """Trace events emitted by the loop (in order), even when no tracer sinks are attached."""
    error: AgentError | None = None
    """The typed cause when ``stop_reason`` is ``"budget"``, ``"max_steps"`` or
    ``"error"``. ``MaxStepsExceeded`` carries ``steps`` and ``last_message``."""


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
    """Run model -> tools -> observations until the loop terminates.

    Per iteration (1-based), in this exact order:

    1. **Budget check at the top.** If ``budget`` is not ``None``, call
       ``budget.assert_ok(what="agent run")``. A raised
       ``agentlab.errors.BudgetExceeded`` ends the loop with
       ``stop_reason="budget"`` and the exception in ``error`` -- no model call
       is made after the budget is gone.
    2. **Model call.** ``provider.complete(CompletionRequest(messages=...,
       tools=registry.specs(), model=provider.model))``. The assistant message is
       appended to ``messages``. On ``agentlab.errors.AgentError`` end with
       ``stop_reason="error"`` and the exception in ``error``.
    3. **Stop conditions.** Build ``StepState(step=n, response=response,
       messages=messages, usage=running_usage)`` and evaluate
       ``stop_conditions`` (default ``stop.DEFAULT_STOP_CONDITIONS``) in order.
       The first ``halt`` decision ends the loop with that decision's ``reason``.
    4. **Natural answer.** A response with no tool calls ends the loop with
       ``stop_reason="answer"``.
    5. **Tool execution** (only when the response has tool calls). Invoke each
       call through ``registry.invoke`` and append
       ``Message.tool_result(call.id, result.output, name=call.name)`` -- for
       both ``ok=True`` and ``ok=False`` results. Then ``budget.add_step()``.

    ``budget.charge(provider.model, response.usage)`` runs after every successful
    model call, before stop conditions are evaluated.

    If ``max_steps`` iterations complete without termination, stop with
    ``stop_reason="max_steps"`` and ``error=MaxStepsExceeded(steps=len(steps),
    last_message=<last assistant message or None>)`` so callers can render the
    partial run instead of losing it.

    ``messages`` is extended in place (the caller's list is the transcript) and
    also returned in the outcome.

    Trace events, emitted through ``tracer`` when one is supplied and always
    collected into ``outcome.events``:

    ==============  ====================  ====================================================
    ``kind``        ``name``              ``data``
    ==============  ====================  ====================================================
    ``step``        ``f"step-{n}"``       ``{"step": n}``
    ``model_call``  ``provider.name``     step, model, input/output/cached tokens, finish_reason;
                                          ``duration_ms`` set from a wall-clock measurement
    ``tool_call``   tool name             step, tool_call_id, arguments
    ``tool_result`` tool name             step, tool_call_id, ok, truncated, error, chars
    ==============  ====================  ====================================================

    Hints:
    - Use ``tracer.emit(...)``; it returns the event, which is how the loop
      collects them without needing a sink.
    - Never put a ``return`` inside a ``while`` you cannot explain; this function
      has one ``for`` and one outcome per exit path.
    """
    raise NotImplementedError("Week 2 lab: implement run_loop")
