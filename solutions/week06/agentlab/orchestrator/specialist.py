"""Specialists: isolated sub-agents with narrow tools and typed hand-offs (week 6).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from agentlab.budget import Budget
from agentlab.errors import AgentError
from agentlab.providers.base import Provider
from agentlab.tools.registry import ToolRegistry, ToolResult
from agentlab.trace import Tracer
from agentlab.types import CompletionRequest, Message


class SpecialistError(AgentError):
    """A specialist failed to produce a valid structured hand-off."""


@dataclass(frozen=True, slots=True)
class ContextEnvelope:
    """The least-context input handed to a specialist."""

    objective: str
    facts: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HandoffArtifact:
    """The structured artifact a specialist returns."""

    specialist: str
    summary: str
    findings: tuple[str, ...] = ()
    confidence: float = 0.0
    artifacts: tuple[str, ...] = ()

    def as_text(self) -> str:
        lines = [f"{self.specialist}: {self.summary}"]
        lines.extend(f"- {finding}" for finding in self.findings)
        if self.artifacts:
            lines.append("references: " + ", ".join(self.artifacts))
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class SpecialistSpec:
    """A specialist's static configuration."""

    name: str
    system_prompt: str
    tools: tuple[str, ...] = ()
    max_steps: int = 4


_HANDOFF_INSTRUCTIONS = (
    "Return ONLY one JSON object with these keys: "
    '"summary" (non-empty string, required), '
    '"findings" (array of strings), '
    '"confidence" (number between 0 and 1), '
    '"artifacts" (array of strings, e.g. document references). '
    "Do not include prose outside the JSON object."
)


class Specialist:
    """A sub-agent with isolated context, a narrow tool set and typed hand-off."""

    def __init__(
        self,
        spec: SpecialistSpec,
        provider: Provider,
        tools: ToolRegistry,
        *,
        tracer: Tracer | None = None,
        budget: Budget | None = None,
    ) -> None:
        self.spec = spec
        self.provider = provider
        self.tools = tools
        self.tracer = tracer
        self.budget = budget

    # -- public ------------------------------------------------------------

    def run(self, envelope: ContextEnvelope) -> HandoffArtifact:
        allowed_tools = self._allowed_tools()
        messages = self._initial_messages(envelope)
        tracer = self.tracer.child(self.spec.name) if self.tracer is not None else None
        if tracer is not None:
            tracer.emit(
                "subagent_start",
                self.spec.name,
                {"objective": envelope.objective, "tools": list(self.spec.tools)},
            )
        artifact = self._loop(messages, allowed_tools)
        if tracer is not None:
            tracer.emit(
                "subagent_end",
                self.spec.name,
                {
                    "summary": artifact.summary,
                    "confidence": artifact.confidence,
                    "findings": len(artifact.findings),
                    "artifacts": len(artifact.artifacts),
                },
            )
        return artifact

    # -- internals ---------------------------------------------------------

    def _allowed_tools(self) -> list:
        tools = []
        for name in self.spec.tools:
            tool = self.tools.get(name)
            if tool is None:
                raise ValueError(f"specialist {self.spec.name!r} names tool {name!r} which is not registered")
            tools.append(tool)
        return tools

    def _initial_messages(self, envelope: ContextEnvelope) -> list[Message]:
        def bullets(values: tuple[str, ...]) -> str:
            if not values:
                return "- (none)"
            return "\n".join(f"- {value}" for value in values)

        task = (
            "## Objective\n"
            f"{envelope.objective}\n\n"
            "## Facts\n"
            f"{bullets(envelope.facts)}\n\n"
            "## Constraints\n"
            f"{bullets(envelope.constraints)}\n\n"
            "## References\n"
            f"{bullets(envelope.references)}\n\n"
            "## Output format\n"
            f"{_HANDOFF_INSTRUCTIONS}"
        )
        return [Message.system(self.spec.system_prompt), Message.user(task)]

    def _loop(self, messages: list[Message], allowed_tools: list) -> HandoffArtifact:
        for _step in range(1, self.spec.max_steps + 1):
            if self.budget is not None:
                self.budget.add_step()
                self.budget.assert_ok(what=f"specialist {self.spec.name}")
            response = self.provider.complete(
                CompletionRequest(
                    messages=list(messages),
                    model=self.provider.model,
                    tools=[tool.spec() for tool in allowed_tools],
                )
            )
            if self.budget is not None:
                self.budget.charge(self.provider.model, response.usage)
                self.budget.assert_ok(what=f"specialist {self.spec.name}")

            if response.tool_calls:
                messages.append(response.message)
                for call in response.tool_calls:
                    if call.name not in self.spec.tools:
                        result = ToolResult.failure(
                            f"tool {call.name!r} is not in this specialist's tool set; refusing to execute it"
                        )
                    else:
                        result = self.tools.invoke(call.name, call.arguments)
                    messages.append(Message.tool_result(call.id, result.as_observation(), call.name))
                continue
            return self._parse_handoff(response.text)

        raise SpecialistError(
            f"specialist {self.spec.name!r} did not produce a hand-off within {self.spec.max_steps} steps"
        )

    def _parse_handoff(self, text: str) -> HandoffArtifact:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: not valid JSON ({exc.msg})"
            ) from exc
        if not isinstance(payload, dict):
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: expected a JSON object"
            )

        summary = payload.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: "
                "'summary' must be a non-empty string"
            )

        findings = payload.get("findings", [])
        if not isinstance(findings, list) or not all(isinstance(finding, str) for finding in findings):
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: "
                "'findings' must be an array of strings"
            )

        artifacts = payload.get("artifacts", [])
        if not isinstance(artifacts, list) or not all(isinstance(artifact, str) for artifact in artifacts):
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: "
                "'artifacts' must be an array of strings"
            )

        confidence = payload.get("confidence", 0.0)
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: 'confidence' must be a number"
            )
        confidence_value = float(confidence)
        if not 0.0 <= confidence_value <= 1.0:
            raise SpecialistError(
                f"specialist {self.spec.name!r} produced an invalid hand-off: "
                f"'confidence' must be in [0, 1], got {confidence_value}"
            )

        return HandoffArtifact(
            specialist=self.spec.name,
            summary=summary.strip(),
            findings=tuple(findings),
            confidence=confidence_value,
            artifacts=tuple(artifacts),
        )
