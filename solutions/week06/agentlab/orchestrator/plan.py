"""Typed plans: workstreams, dependencies and validation (week 6).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agentlab.errors import AgentError


class PlanError(AgentError):
    """The plan is structurally invalid or cannot be executed as written."""


class NodeKind(StrEnum):
    """The only two kinds of workstream node (closed set)."""

    CAPABILITY = "capability"
    REASONING = "reasoning"


@dataclass(frozen=True, slots=True)
class Workstream:
    """One typed step in a plan."""

    id: str
    objective: str
    kind: NodeKind
    capability: str | None = None
    depends_on: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    budget_usd: float | None = None
    inputs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Plan:
    """A plan: a goal plus typed workstreams."""

    goal: str
    workstreams: tuple[Workstream, ...] = ()

    def get(self, workstream_id: str) -> Workstream | None:
        for workstream in self.workstreams:
            if workstream.id == workstream_id:
                return workstream
        return None

    def validate(self) -> None:
        validate_plan(self)

    def topo_order(self) -> tuple[Workstream, ...]:
        return topo_order(self)

    def ready(self, completed: Collection[str]) -> tuple[Workstream, ...]:
        return ready_workstreams(self, completed)


_VALID_KINDS = (NodeKind.CAPABILITY, NodeKind.REASONING)


def _check_kind(kind: Any) -> None:
    if kind not in _VALID_KINDS:
        raise PlanError(f"workstream kind {kind!r} is not a closed kind (capability | reasoning)")


def validate_plan(plan: Plan) -> None:
    if not plan.goal or not plan.goal.strip():
        raise PlanError("plan goal must not be blank")
    workstreams = list(plan.workstreams)
    if not workstreams:
        raise PlanError("plan must contain at least one workstream")

    ids: list[str] = []
    for workstream in workstreams:
        if not workstream.id or not workstream.id.strip():
            raise PlanError("workstream id must not be blank")
        if workstream.id in ids:
            raise PlanError(f"duplicate workstream id {workstream.id!r}")
        ids.append(workstream.id)
    known = set(ids)

    for workstream in workstreams:
        _check_kind(workstream.kind)
        if not workstream.objective or not workstream.objective.strip():
            raise PlanError(f"workstream {workstream.id!r} objective must not be blank")
        if workstream.kind == NodeKind.CAPABILITY:
            if not workstream.capability or not workstream.capability.strip():
                raise PlanError(f"capability workstream {workstream.id!r} must name a capability")
        elif workstream.capability is not None:
            raise PlanError(f"reasoning workstream {workstream.id!r} must not name a capability")
        if not workstream.acceptance_criteria:
            raise PlanError(f"workstream {workstream.id!r} must declare at least one acceptance criterion")
        if any(not criterion.strip() for criterion in workstream.acceptance_criteria):
            raise PlanError(f"workstream {workstream.id!r} has a blank acceptance criterion")
        if workstream.budget_usd is not None and workstream.budget_usd <= 0:
            raise PlanError(f"workstream {workstream.id!r} budget_usd must be positive")
        for dependency in workstream.depends_on:
            if dependency not in known:
                raise PlanError(f"workstream {workstream.id!r} depends on unknown workstream {dependency!r}")

    _assert_acyclic(workstreams)


def _assert_acyclic(workstreams: list[Workstream]) -> None:
    indegree = {workstream.id: len(set(workstream.depends_on)) for workstream in workstreams}
    children: dict[str, list[str]] = {workstream.id: [] for workstream in workstreams}
    for workstream in workstreams:
        for dependency in set(workstream.depends_on):
            children[dependency].append(workstream.id)
    queue = [workstream.id for workstream in workstreams if indegree[workstream.id] == 0]
    visited = 0
    while queue:
        current = queue.pop(0)
        visited += 1
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(workstreams):
        cyclic = sorted(workstream.id for workstream in workstreams if indegree[workstream.id] > 0)
        raise PlanError("plan dependency graph contains a cycle involving: " + ", ".join(cyclic))


def topo_order(plan: Plan) -> tuple[Workstream, ...]:
    validate_plan(plan)
    workstreams = list(plan.workstreams)
    by_id = {workstream.id: workstream for workstream in workstreams}
    indegree = {workstream.id: len(set(workstream.depends_on)) for workstream in workstreams}
    children: dict[str, list[str]] = {workstream.id: [] for workstream in workstreams}
    for workstream in workstreams:
        for dependency in set(workstream.depends_on):
            children[dependency].append(workstream.id)

    queue = [workstream.id for workstream in workstreams if indegree[workstream.id] == 0]
    ordered: list[Workstream] = []
    while queue:
        current = queue.pop(0)
        ordered.append(by_id[current])
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    return tuple(ordered)


def ready_workstreams(plan: Plan, completed: Collection[str]) -> tuple[Workstream, ...]:
    validate_plan(plan)
    done = set(completed)
    return tuple(
        workstream
        for workstream in plan.workstreams
        if workstream.id not in done and set(workstream.depends_on) <= done
    )


@dataclass(frozen=True, slots=True)
class ReplanDecision:
    """The plan after replanning, plus an audit of what was dropped and why."""

    plan: Plan
    dropped: tuple[str, ...]
    reason: str


def replan_after_failure(
    plan: Plan,
    failed_id: str,
    *,
    reason: str,
    attempts: int = 1,
    max_attempts: int = 2,
) -> ReplanDecision:
    validate_plan(plan)
    if plan.get(failed_id) is None:
        raise PlanError(f"unknown workstream {failed_id!r}; cannot replan it")
    if attempts >= max_attempts:
        raise PlanError(
            f"workstream {failed_id!r} failed {attempts} time(s); retry budget of "
            f"{max_attempts} exhausted, escalating instead of retrying"
        )

    workstreams = list(plan.workstreams)
    dropped = {failed_id}
    changed = True
    while changed:
        changed = False
        for workstream in workstreams:
            if workstream.id in dropped:
                continue
            if any(dependency in dropped for dependency in workstream.depends_on):
                dropped.add(workstream.id)
                changed = True

    remaining = [workstream for workstream in workstreams if workstream.id not in dropped]
    if not remaining:
        raise PlanError(
            f"replanning after {failed_id!r} removed every workstream; the plan cannot be "
            "salvaged and must be reported, not silently emptied"
        )
    reduced = Plan(goal=plan.goal, workstreams=tuple(remaining))
    validate_plan(reduced)
    return ReplanDecision(
        plan=reduced,
        dropped=tuple(workstream.id for workstream in workstreams if workstream.id in dropped),
        reason=reason,
    )
