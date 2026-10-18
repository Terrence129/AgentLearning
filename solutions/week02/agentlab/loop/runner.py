"""Reference solution -- week 2: run configuration and result type.

The runner is deliberately thin: it opens the conversation, wraps the loop in a
trace envelope, and converts ``LoopOutcome`` into one ``AgentResult``. Keeping
policy (how a system prompt is written, which tools exist) out of this file is
what lets weeks 4-9 reuse it without editing it.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentlab.budget import Budget
from agentlab.errors import AgentError
from agentlab.loop.react import StepRecord, run_loop
from agentlab.providers.base import Provider
from agentlab.tools.registry import ToolRegistry
from agentlab.trace import TraceEvent, Tracer
from agentlab.types import Message, Usage

#: Default step ceiling for a run.
DEFAULT_MAX_STEPS = 10


@dataclass(slots=True)
class AgentResult:
    """The outcome of one agent run. Never an exception for expected stops."""

    answer: str
    steps: list[StepRecord]
    usage: Usage
    stop_reason: str
    trace_events: list[TraceEvent]
    error: AgentError | None = None


def _last_assistant_text(messages: list[Message]) -> str:
    for message in reversed(messages):
        if message.role == "assistant" and message.content:
            return message.content
    return ""


class AgentRunner:
    """Runs a goal end-to-end with one provider and one tool registry."""

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
        """Run one goal and return its ``AgentResult``."""
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")

        messages: list[Message] = []
        if system_prompt is not None:
            messages.append(Message.system(system_prompt))
        messages.append(Message.user(goal))

        tracer = self.tracer or Tracer()
        trace_events: list[TraceEvent] = [
            tracer.emit("run_start", "agent_run", {"goal": goal, "max_steps": self.max_steps})
        ]

        outcome = run_loop(
            self.provider,
            self.registry,
            messages,
            tracer=tracer,
            budget=self.budget,
            max_steps=self.max_steps,
        )
        trace_events.extend(outcome.events)

        trace_events.append(
            tracer.emit(
                "run_end",
                "agent_run",
                {
                    "stop_reason": outcome.stop_reason,
                    "steps": len(outcome.steps),
                    "input_tokens": outcome.usage.input_tokens,
                    "output_tokens": outcome.usage.output_tokens,
                    "error": type(outcome.error).__name__ if outcome.error is not None else None,
                },
            )
        )

        return AgentResult(
            answer=_last_assistant_text(outcome.messages),
            steps=outcome.steps,
            usage=outcome.usage,
            stop_reason=outcome.stop_reason,
            trace_events=trace_events,
            error=outcome.error,
        )
