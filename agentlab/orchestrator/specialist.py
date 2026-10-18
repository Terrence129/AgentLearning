"""Specialists: isolated sub-agents with narrow tools and typed hand-offs (week 6).

Why this module exists
----------------------
A sub-agent is a context firewall, not a second chat window. It should receive
the *least context that lets it do its job*, use *only the tools it needs*, and
return a *structured artifact* -- never its full transcript. Anthropic's
multi-agent research system is the canonical evidence: sub-agents may burn tens
of thousands of tokens and return 1,000-2,000 tokens of distilled result, which
is both compression and separation of concerns
(docs/research/01-agent-architecture-sota.md §3.6). Over-sharing is also a
governance bug: SendOS calls the alternative a "least-context envelope"
(docs/research/05-sendos-concept-map.md §3 topic 8).

What breaks without it
----------------------
- The lead agent's context fills with sub-agent chatter, defeating the point.
- A sub-agent calls a write tool the lead was never authorised to use.
- The next agent receives prose it must re-parse and mis-reads a number.
- A run that should have isolated one tenant's data leaks another's.

The hand-off contract in this lab is deliberately small: a JSON object with
``summary`` (required), ``findings``, ``confidence`` and ``artifacts``. The
specialist loop *validates before returning*: an invalid hand-off raises
``SpecialistError`` rather than crossing the boundary as half-parsed text.

Read first: docs/research/01-agent-architecture-sota.md §3.6 and §6.2.

Public surface
--------------
``ContextEnvelope``   the least-context input: objective, facts, constraints, refs
``HandoffArtifact``   the structured output: summary, findings, confidence, refs
``SpecialistSpec``    identity, instructions, allowed tools, step ceiling
``Specialist``        the isolated mini-loop with a typed hand-off
``SpecialistError``   invalid hand-off / no hand-off within the step ceiling
"""

from __future__ import annotations

from dataclasses import dataclass

from agentlab.budget import Budget
from agentlab.errors import AgentError
from agentlab.providers.base import Provider
from agentlab.tools.registry import ToolRegistry
from agentlab.trace import Tracer


class SpecialistError(AgentError):
    """A specialist failed to produce a valid structured hand-off."""


@dataclass(frozen=True, slots=True)
class ContextEnvelope:
    """The least-context input handed to a specialist.

    There is intentionally no ``transcript`` field: a specialist must be able to
    start from the objective plus the facts it is given. References (paths, URLs,
    ids) let it fetch more just-in-time instead of receiving everything up front.
    """

    objective: str
    facts: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HandoffArtifact:
    """The structured artifact a specialist returns.

    This is the only thing that crosses the context boundary -- the transcript
    stays inside the specialist.
    """

    specialist: str
    summary: str
    findings: tuple[str, ...] = ()
    confidence: float = 0.0
    artifacts: tuple[str, ...] = ()

    def as_text(self) -> str:
        """Compact plain-text rendering for composing a final answer/decision.

        Contract: includes the specialist name, the summary and each finding as
        a bullet; bounded and deterministic (no transcript, no timestamps).
        """
        raise NotImplementedError("Week 6 lab: implement HandoffArtifact.as_text")


@dataclass(frozen=True, slots=True)
class SpecialistSpec:
    """A specialist's static configuration.

    Attributes:
        name: unique name, used in traces and hand-off artifacts.
        system_prompt: the specialist's role and output instructions.
        tools: allowlist of tool names; tools not listed are invisible *and*
            invocations of them are refused.
        max_steps: maximum provider calls before the run is declared failed.
    """

    name: str
    system_prompt: str
    tools: tuple[str, ...] = ()
    max_steps: int = 4


class Specialist:
    """A sub-agent with isolated context, a narrow tool set and typed hand-off.

    Run contract:
        1. Build the prompt from ``spec.system_prompt`` plus the envelope's
           objective/facts/constraints/references. Never accept or forward a full
           transcript.
        2. Expose only the tools named in ``spec.tools`` (missing tools raise
           ``ValueError`` at run time -- a spec that names unregistered tools is a
           wiring bug).
        3. Loop up to ``spec.max_steps`` provider calls. Each iteration:
           charge the optional :class:`Budget` (step + usage) and enforce it.
        4. For tool calls: append the assistant turn and one tool observation per
           call. A call to a tool outside the allowlist becomes an error
           observation and must NOT be executed.
        5. The first assistant turn with no tool calls is the hand-off: it must be
           a JSON object parsing to a :class:`HandoffArtifact`
           (``summary`` required and non-empty; ``findings``/``artifacts`` lists
           of strings; ``confidence`` in ``[0.0, 1.0]``). Invalid -> ``SpecialistError``.
        6. Emit ``subagent_start`` and ``subagent_end`` trace events on a child
           tracer scoped to the specialist. The end event carries the artifact's
           summary/confidence/finding count -- never the transcript.
    """

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

    def run(self, envelope: ContextEnvelope) -> HandoffArtifact:
        """Run the specialist and return its validated hand-off."""
        raise NotImplementedError("Week 6 lab: implement Specialist.run")
