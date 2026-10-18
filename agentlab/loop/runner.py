"""Run configuration and result type for the agent loop -- YOUR WEEK 2 BUILD.

``react.run_loop`` is the mechanism; this module is the product surface. A
caller hands ``AgentRunner`` a goal and gets back one ``AgentResult`` that
answers the questions a human (or an eval harness, or a trace viewer) actually
asks: what did the agent say, how many steps did it take, what did it cost, why
did it stop, and where is the evidence?

Design rules worth copying:

- **Construction is cheap and explicit.** Everything the run needs is injected:
  provider, tools, tracer, budget. No globals, no config files.
- **Partial results are first-class.** A budget stop or step ceiling still
  returns the answer-so-far, the steps taken and the trace, with the typed cause
  in ``error``. Losing the transcript on timeout is a debugging tax.
- **The trace is part of the result**, not a side file, so a test can assert on
  the exact event sequence a run produced.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentlab.budget import Budget
from agentlab.errors import AgentError
from agentlab.loop.react import StepRecord
from agentlab.providers.base import Provider
from agentlab.tools.registry import ToolRegistry
from agentlab.trace import TraceEvent, Tracer
from agentlab.types import Usage

#: Default step ceiling for a run. Enough for a multi-tool task, small enough
#: that a looping model fails the run instead of the wallet.
DEFAULT_MAX_STEPS = 10


@dataclass(slots=True)
class AgentResult:
    """The outcome of one agent run. Never an exception for expected stops."""

    answer: str
    """Last non-empty assistant text in the transcript, or ``""``."""
    steps: list[StepRecord]
    """Every completed loop step, in order."""
    usage: Usage
    """Usage summed over all model calls in the run."""
    stop_reason: str
    """``"answer"`` | ``"budget"`` | ``"max_steps"`` | ``"error"``, or a stop
    condition's reason such as ``"length"``."""
    trace_events: list[TraceEvent]
    """``run_start``, the loop's events, then ``run_end`` -- in order."""
    error: AgentError | None = None
    """Typed cause for non-answer stops (``BudgetExceeded``, ``MaxStepsExceeded``,
    ``ProviderError``, ...), else ``None``."""


class AgentRunner:
    """Runs a goal end-to-end with one provider and one tool registry.

    Usage::

        result = AgentRunner(provider, registry, tracer=Tracer(sinks=[MemorySink()])).run(
            "What is (12 + 8) * 3?",
            system_prompt="You are a careful assistant. Use tools when needed.",
        )
        if result.stop_reason == "answer":
            print(result.answer)

    The runner owns the conversation's opening messages, the trace envelope and
    the translation from ``LoopOutcome`` to ``AgentResult``. It deliberately
    knows nothing about particular tools or vendors.
    """

    def __init__(
        self,
        provider: Provider,
        registry: ToolRegistry,
        tracer: Tracer | None = None,
        budget: Budget | None = None,
        max_steps: int = DEFAULT_MAX_STEPS,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.tracer = tracer
        self.budget = budget
        self.max_steps = max_steps

    def run(self, goal: str, system_prompt: str | None = None) -> AgentResult:
        """Run one goal and return its ``AgentResult``.

        Contract:
        - Opening messages: ``[Message.system(system_prompt)]`` when a system
          prompt is given, then ``Message.user(goal)``. Never an empty goal.
        - Trace envelope: emit ``run_start`` (kind ``run_start``, name
          ``"agent_run"``, data ``{"goal": goal, "max_steps": self.max_steps}``)
          before the first model call and ``run_end`` (same name) after the loop
          with data ``{"stop_reason", "steps", "input_tokens",
          "output_tokens", "error"}`` where ``error`` is the exception class
          name or ``None``.
        - When no tracer is supplied, create one with no sinks: events must still
          be collected into ``trace_events``. When a tracer is supplied, its
          sinks also receive the events.
        - ``answer`` is the last non-empty assistant text in the outcome
          transcript, else ``""`` (partial answers survive budget/step stops).
        - ``stop_reason``, ``usage``, ``steps`` and ``error`` come straight from
          ``react.run_loop``. This method returns, it does not raise, for
          expected terminations; only real programming errors propagate.
        """
        raise NotImplementedError("Week 2 lab: implement AgentRunner.run")
