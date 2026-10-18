"""Topology-driven orchestration: pick the smallest sufficient shape (week 6).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agentlab.budget import Budget
from agentlab.errors import AgentError, BudgetExceeded
from agentlab.orchestrator.approval import ApprovalCheckpoint
from agentlab.orchestrator.plan import (
    NodeKind,
    Plan,
    Workstream,
    topo_order,
    validate_plan,
)
from agentlab.orchestrator.specialist import (
    ContextEnvelope,
    HandoffArtifact,
    Specialist,
)
from agentlab.trace import Tracer

CapabilityExecutor = Callable[[dict[str, Any]], Any]


class ExecutionShape(StrEnum):
    """The four execution shapes the classifier can derive."""

    DIRECT_CAPABILITY = "direct_capability"
    DIRECT_SPECIALIST = "direct_specialist"
    SINGLE_SQUAD = "single_squad"
    MULTI_SQUAD = "multi_squad"


@dataclass(frozen=True, slots=True)
class ShapeSelection:
    """The classifier's answer plus whether the runtime can back it."""

    derived: ExecutionShape
    shape: ExecutionShape | None
    backed: bool
    limitation: str | None
    reason: str


def component_ids(plan: Plan) -> tuple[tuple[str, ...], ...]:
    validate_plan(plan)
    workstreams = list(plan.workstreams)
    parent = {workstream.id: workstream.id for workstream in workstreams}

    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for workstream in workstreams:
        for dependency in workstream.depends_on:
            root, other = find(workstream.id), find(dependency)
            if root != other:
                parent[other] = root

    groups: dict[str, list[str]] = {}
    for workstream in workstreams:
        groups.setdefault(find(workstream.id), []).append(workstream.id)
    declaration_index = {workstream.id: index for index, workstream in enumerate(workstreams)}
    components = sorted(groups.values(), key=lambda ids: min(declaration_index[node] for node in ids))
    return tuple(tuple(ids) for ids in components)


def classify_shape(plan: Plan) -> ExecutionShape:
    validate_plan(plan)
    workstreams = list(plan.workstreams)
    if len(workstreams) == 1:
        only = workstreams[0]
        if only.kind == NodeKind.CAPABILITY:
            return ExecutionShape.DIRECT_CAPABILITY
        return ExecutionShape.DIRECT_SPECIALIST
    if len(component_ids(plan)) >= 2:
        return ExecutionShape.MULTI_SQUAD
    return ExecutionShape.SINGLE_SQUAD


def _derive_reason(plan: Plan, shape: ExecutionShape) -> str:
    components = component_ids(plan)
    return (
        f"derived {shape.value} from {len(plan.workstreams)} workstream(s) in "
        f"{len(components)} connected component(s)"
    )


def select_shape(plan: Plan, *, backed_shapes: Collection[ExecutionShape] | None = None) -> ShapeSelection:
    derived = classify_shape(plan)
    backed = frozenset(ExecutionShape) if backed_shapes is None else frozenset(backed_shapes)
    reason = _derive_reason(plan, derived)
    if derived in backed:
        return ShapeSelection(derived=derived, shape=derived, backed=True, limitation=None, reason=reason)
    limitation = (
        f"plan topology requires the {derived.value} execution shape, which this runtime "
        "does not support; refusing to guess a smaller shape that would silently drop "
        "work"
    )
    return ShapeSelection(derived=derived, shape=None, backed=False, limitation=limitation, reason=reason)


@dataclass(frozen=True, slots=True)
class WorkstreamResult:
    """One workstream's outcome."""

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
    """The outcome of running one plan."""

    goal: str
    selection: ShapeSelection
    workstreams: tuple[WorkstreamResult, ...] = ()
    limitations: tuple[str, ...] = ()
    aggregate_budget: Budget = field(default_factory=Budget)

    @property
    def ok(self) -> bool:
        return (
            self.selection.backed
            and not self.limitations
            and all(result.ok or result.skipped for result in self.workstreams)
        )


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def _accumulate(target: Budget, source: Budget) -> None:
    target.used_usd += source.used_usd
    target.used_input_tokens += source.used_input_tokens
    target.used_output_tokens += source.used_output_tokens
    target.steps += source.steps
    for model in source.unknown_priced_models or ():
        assert target.unknown_priced_models is not None
        target.unknown_priced_models.add(model)


class Orchestrator:
    """Runs typed plans with the smallest shape that can back them."""

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

    # -- public ------------------------------------------------------------

    def run(
        self, plan: Plan, *, envelopes: Mapping[str, ContextEnvelope] | None = None
    ) -> OrchestrationResult:
        validate_plan(plan)
        selection = select_shape(plan, backed_shapes=self.backed_shapes)
        if not selection.backed:
            limitations = (selection.limitation,) if selection.limitation else ()
            return OrchestrationResult(goal=plan.goal, selection=selection, limitations=limitations)

        aggregate = Budget()
        outcomes: dict[str, WorkstreamResult] = {}
        ordered: list[WorkstreamResult] = []
        for workstream in topo_order(plan):
            blocked = [dependency for dependency in workstream.depends_on if not outcomes[dependency].ok]
            workstream_budget = Budget(max_usd=workstream.budget_usd)
            if blocked:
                result = WorkstreamResult(
                    workstream_id=workstream.id,
                    ok=False,
                    kind=workstream.kind,
                    error=(
                        "upstream dependency did not complete: "
                        + ", ".join(f"'{dependency}'" for dependency in blocked)
                    ),
                    skipped=True,
                    budget=workstream_budget,
                )
            elif workstream.kind == NodeKind.CAPABILITY:
                result = self._run_capability(workstream, workstream_budget)
            else:
                result = self._run_specialist(plan, workstream, workstream_budget, envelopes or {}, outcomes)
            outcomes[workstream.id] = result
            ordered.append(result)
            _accumulate(aggregate, workstream_budget)

        return OrchestrationResult(
            goal=plan.goal,
            selection=selection,
            workstreams=tuple(ordered),
            aggregate_budget=aggregate,
        )

    # -- internals ---------------------------------------------------------

    def _run_capability(self, workstream: Workstream, budget: Budget) -> WorkstreamResult:
        capability = workstream.capability or ""
        executor = self.capabilities.get(capability)
        if executor is None:
            return WorkstreamResult(
                workstream_id=workstream.id,
                ok=False,
                kind=workstream.kind,
                error=f"no executor registered for capability {capability!r}",
                budget=budget,
            )
        try:
            output = executor(dict(workstream.inputs))
        except Exception as exc:
            return WorkstreamResult(
                workstream_id=workstream.id,
                ok=False,
                kind=workstream.kind,
                error=f"capability {capability!r} raised {type(exc).__name__}: {exc}",
                budget=budget,
            )
        return WorkstreamResult(
            workstream_id=workstream.id,
            ok=True,
            kind=workstream.kind,
            output=_stringify(output),
            budget=budget,
        )

    def _run_specialist(
        self,
        plan: Plan,
        workstream: Workstream,
        budget: Budget,
        envelopes: Mapping[str, ContextEnvelope],
        outcomes: Mapping[str, WorkstreamResult],
    ) -> WorkstreamResult:
        specialist = self.specialists.get(workstream.id)
        if specialist is None:
            return WorkstreamResult(
                workstream_id=workstream.id,
                ok=False,
                kind=workstream.kind,
                error=f"no specialist registered for workstream {workstream.id!r}",
                budget=budget,
            )
        envelope = envelopes.get(workstream.id)
        if envelope is None:
            facts = tuple(
                f"{dependency}: {outcomes[dependency].output}"
                for dependency in workstream.depends_on
                if outcomes[dependency].output is not None
            )
            envelope = ContextEnvelope(
                objective=workstream.objective,
                facts=facts,
                constraints=(f"plan goal: {plan.goal}",),
            )
        specialist.budget = budget
        try:
            artifact = specialist.run(envelope)
        except BudgetExceeded as exc:
            return WorkstreamResult(
                workstream_id=workstream.id,
                ok=False,
                kind=workstream.kind,
                error=f"budget exceeded: {exc}",
                budget=budget,
            )
        except AgentError as exc:
            return WorkstreamResult(
                workstream_id=workstream.id,
                ok=False,
                kind=workstream.kind,
                error=f"specialist {specialist.spec.name!r} failed: {exc}",
                budget=budget,
            )
        except Exception as exc:
            return WorkstreamResult(
                workstream_id=workstream.id,
                ok=False,
                kind=workstream.kind,
                error=f"specialist {specialist.spec.name!r} crashed: {type(exc).__name__}: {exc}",
                budget=budget,
            )
        return WorkstreamResult(
            workstream_id=workstream.id,
            ok=True,
            kind=workstream.kind,
            output=artifact.as_text(),
            handoff=artifact,
            budget=budget,
        )


__all__ = [
    "CapabilityExecutor",
    "ExecutionShape",
    "OrchestrationResult",
    "Orchestrator",
    "ShapeSelection",
    "WorkstreamResult",
    "classify_shape",
    "component_ids",
    "select_shape",
]
