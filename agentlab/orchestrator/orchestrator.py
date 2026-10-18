"""Topology-driven orchestration: pick the smallest sufficient shape (week 6).

Why this module exists
----------------------
The default failure mode of multi-agent systems is *too much agent*: a swarm for
a question one tool call could answer, fan-out driven by ambiguity. SendOS's
ADR-0001 replaced that with a pure classifier over the plan topology
(docs/research/05-sendos-concept-map.md §4.5):

    one capability node            -> direct capability call (no model needed)
    one reasoning node             -> one specialist
    >= 2 connected nodes           -> one squad
    >= 2 disconnected components   -> multiple squads

And the crucial safety rule: if the derived shape is not supported by the
runtime, return a **limitation** -- never silently guess a smaller shape. A
plan that needs two squads is not "really" one squad; pretending it is will
produce a confident wrong answer instead of an honest "I cannot do that".

This module is that classifier plus a tiny executor: it can run capability
nodes (functions), reasoning nodes (specialists), and compose the results. The
execution path is deliberately sequential and deterministic -- the lab is about
*shape selection and honest limitations*, not about building a distributed
runtime.

What breaks without it
----------------------
- Agent count becomes a style choice instead of a consequence of the task.
- An unsupported plan is executed with a smaller shape and fails silently.
- A capability-only task pays for a model and a squad it does not need.
- Budgets are unowned: nobody can say which step spent the money.

Read first: docs/research/05-sendos-concept-map.md §4.5 and
docs/research/01-agent-architecture-sota.md §6.

Public surface
--------------
``ExecutionShape``     direct_capability | direct_specialist | single_squad | multi_squad
``ShapeSelection``     derived shape, whether it is backed, and the limitation
``component_ids``      connected components of the workstream graph
``classify_shape``     pure topology -> shape (raises ``PlanError`` if invalid)
``select_shape``       classification + runtime backing check
``WorkstreamResult``   per-workstream outcome, budget and hand-off
``OrchestrationResult`` plan outcome: shape, results, limitations, aggregate budget
``Orchestrator``       executes a plan in dependency order under per-workstream budgets
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agentlab.budget import Budget
from agentlab.orchestrator.approval import ApprovalCheckpoint
from agentlab.orchestrator.plan import NodeKind, Plan
from agentlab.orchestrator.specialist import ContextEnvelope, HandoffArtifact, Specialist
from agentlab.trace import Tracer

#: A capability executor is a plain function: no model, no ambiguity, cheap.
CapabilityExecutor = Callable[[dict[str, Any]], Any]


class ExecutionShape(StrEnum):
    """The four execution shapes the classifier can derive."""

    DIRECT_CAPABILITY = "direct_capability"
    DIRECT_SPECIALIST = "direct_specialist"
    SINGLE_SQUAD = "single_squad"
    MULTI_SQUAD = "multi_squad"


@dataclass(frozen=True, slots=True)
class ShapeSelection:
    """The classifier's answer plus whether the runtime can back it.

    Attributes:
        derived: the shape the plan topology implies.
        shape: the shape that will execute -- ``None`` when unbacked.
        backed: True when ``derived`` is supported by the runtime.
        limitation: honest, user-facing explanation when ``backed`` is False.
        reason: why the classifier derived this shape (for logs/audit).
    """

    derived: ExecutionShape
    shape: ExecutionShape | None
    backed: bool
    limitation: str | None
    reason: str


def component_ids(plan: Plan) -> tuple[tuple[str, ...], ...]:
    """Connected components of the workstream graph.

    Contract:
        - dependency edges are undirected for connectivity purposes;
        - each component's ids are in declaration order; components are ordered
          by the declaration index of their first member;
        - validates the plan first (``PlanError`` for invalid plans).
    """
    raise NotImplementedError("Week 6 lab: implement component_ids")


def classify_shape(plan: Plan) -> ExecutionShape:
    """Derive the execution shape from the plan topology (pure classifier).

    Rule contract (exactly one shape, no importance scores, no budget input):
        - validate the plan first;
        - exactly one workstream -> DIRECT_CAPABILITY for a capability node,
          DIRECT_SPECIALIST for a reasoning node;
        - two or more workstreams in one connected component -> SINGLE_SQUAD;
        - two or more connected components -> MULTI_SQUAD.
    """
    raise NotImplementedError("Week 6 lab: implement classify_shape")


def select_shape(plan: Plan, *, backed_shapes: Collection[ExecutionShape] | None = None) -> ShapeSelection:
    """Classify and check whether this runtime supports the derived shape.

    Contract:
        - ``backed_shapes=None`` means all four shapes are supported;
        - a backed shape returns ``shape=derived``, ``backed=True``,
          ``limitation=None``;
        - an unbacked shape returns ``shape=None``, ``backed=False`` and a
          ``limitation`` that names the derived shape and says the runtime will
          not guess a smaller shape;
        - invalid plans raise ``PlanError`` before any shape decision.
    """
    raise NotImplementedError("Week 6 lab: implement select_shape")


@dataclass(frozen=True, slots=True)
class WorkstreamResult:
    """One workstream's outcome.

    Attributes:
        workstream_id: which step this is.
        ok: whether it completed successfully.
        kind: capability | reasoning.
        output: capability output as text, when applicable.
        handoff: the specialist's structured artifact, when applicable.
        error: failure description (never a traceback dump).
        skipped: True when an upstream dependency failed (not attempted).
        budget: this workstream's own budget ledger.
    """

    workstream_id: str
    ok: bool
    kind: NodeKind
    output: str | None = None
    handoff: HandoffArtifact | None = None
    error: str | None = None
    skipped: bool = False
    budget: Budget = field(default_factory=Budget)


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    """The outcome of running one plan.

    Attributes:
        goal: the plan goal.
        selection: the shape decision (including any limitation).
        workstreams: results in execution order (declaration order for ties).
        limitations: honest constraints; non-empty means "not fully executed".
        aggregate_budget: the sum of every workstream budget.
    """

    goal: str
    selection: ShapeSelection
    workstreams: tuple[WorkstreamResult, ...] = ()
    limitations: tuple[str, ...] = ()
    aggregate_budget: Budget = field(default_factory=Budget)

    @property
    def ok(self) -> bool:
        """True when the shape was backed and every attempted workstream succeeded."""
        raise NotImplementedError("Week 6 lab: implement OrchestrationResult.ok")


class Orchestrator:
    """Runs typed plans with the smallest shape that can back them.

    Construction:
        ``specialists`` maps workstream id -> :class:`Specialist` for reasoning
        nodes; ``capabilities`` maps capability name -> executor for capability
        nodes; ``backed_shapes`` defaults to all four shapes; ``budget`` is an
        optional run-level ceiling (per-workstream budgets are created from
        ``Workstream.budget_usd`` regardless).

    Run contract:
        - validate the plan and select a shape (invalid plan -> ``PlanError``);
        - when the derived shape is unbacked, execute nothing and return the
          limitation in ``OrchestrationResult.limitations``;
        - otherwise execute in dependency order (``plan.topo_order()``);
        - a capability node calls its executor with ``Workstream.inputs``;
        - a reasoning node runs its registered specialist with a least-context
          envelope built from the objective, the plan goal and upstream outputs;
        - a workstream whose dependency failed is ``skipped`` (never guessed);
        - a missing executor/specialist, a specialist failure or an exceeded
          per-workstream budget becomes ``ok=False`` with a short ``error``;
        - upstream outputs are the *only* context that flows between workstreams
          (no transcripts);
        - the aggregate budget sums the per-workstream ledgers;
        - results are returned in execution order, deterministically.
    """

    def __init__(
        self,
        *,
        specialists: Mapping[str, Specialist] | None = None,
        capabilities: Mapping[str, CapabilityExecutor] | None = None,
        approval: ApprovalCheckpoint | None = None,
        backed_shapes: Collection[ExecutionShape] | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self.specialists: dict[str, Specialist] = dict(specialists or {})
        self.capabilities: dict[str, CapabilityExecutor] = dict(capabilities or {})
        self.approval = approval
        self.backed_shapes: frozenset[ExecutionShape] = (
            frozenset(ExecutionShape) if backed_shapes is None else frozenset(backed_shapes)
        )
        self.tracer = tracer

    def run(
        self, plan: Plan, *, envelopes: Mapping[str, ContextEnvelope] | None = None
    ) -> OrchestrationResult:
        """Execute a plan (see class contract)."""
        raise NotImplementedError("Week 6 lab: implement Orchestrator.run")
