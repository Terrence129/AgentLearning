"""Typed plans: workstreams, dependencies and validation (week 6).

Why this module exists
----------------------
Most multi-agent failures start before any agent runs: the plan is an
under-specified blob of prose, so nobody can tell whether it is done, which
steps depend on which, or whether it is even executable. A *typed plan* fixes
that. Every workstream declares:

- an ``id`` and an ``objective`` (what "done" means is separate, below);
- a **closed kind**: ``capability`` (something a tool/server can do) or
  ``reasoning`` (something a model must decide);
- explicit ``depends_on`` edges (the topology drives execution order);
- ``acceptance_criteria`` -- testable statements, so "done" is reviewable;
- an optional per-workstream ``budget_usd``.

SendOS's ``ExecutionPlanner``/``TopologyClassifier`` starts from exactly this
shape (docs/research/05-sendos-concept-map.md §4.5; docs/research/01 §6).

What breaks without it
----------------------
- A cycle in the dependency graph is discovered halfway through a run (or
  never, and the orchestrator loops).
- A "capability" step names no capability, so execution falls back to asking a
  model to pretend -- the classic unbacked plan.
- A failed step is retried forever because there is no replan policy.
- Nobody can tell which steps can run in parallel, which is the whole point of
  having more than one agent.

Read first: docs/research/05-sendos-concept-map.md §4.5 and
docs/research/01-agent-architecture-sota.md §6.

Public surface
--------------
``NodeKind``              closed set: capability | reasoning
``Workstream``            one typed step
``Plan``                  goal + workstreams
``PlanError``             raised for any invalid plan
``validate_plan``         structural validation (raises ``PlanError``)
``topo_order``            deterministic dependency order
``ready_workstreams``     steps whose dependencies are complete
``ReplanDecision``        the plan after a failure, plus what was dropped
``replan_after_failure``  drop the failed step and its dependents
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
    """One typed step in a plan.

    Attributes:
        id: unique, stable identifier (used for dependency edges and reporting).
        objective: what this workstream must achieve.
        kind: capability | reasoning.
        capability: required for ``kind == CAPABILITY`` (the capability name the
            orchestrator should bind); must be ``None`` for ``reasoning`` nodes.
        depends_on: ids of workstreams that must complete first.
        acceptance_criteria: one or more testable "done" statements.
        budget_usd: optional USD ceiling for this workstream.
        inputs: static arguments passed to a capability executor.
    """

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
    """A validated-able plan: a goal plus typed workstreams."""

    goal: str
    workstreams: tuple[Workstream, ...] = ()

    def get(self, workstream_id: str) -> Workstream | None:
        """The workstream with this id, or ``None``."""
        raise NotImplementedError("Week 6 lab: implement Plan.get")

    def validate(self) -> None:
        """Validate this plan (see :func:`validate_plan`)."""
        raise NotImplementedError("Week 6 lab: implement Plan.validate")

    def topo_order(self) -> tuple[Workstream, ...]:
        """Workstreams in deterministic dependency order (see :func:`topo_order`)."""
        raise NotImplementedError("Week 6 lab: implement Plan.topo_order")

    def ready(self, completed: Collection[str]) -> tuple[Workstream, ...]:
        """Workstreams whose dependencies are all in ``completed`` and that are
        not themselves in ``completed`` (declaration order)."""
        raise NotImplementedError("Week 6 lab: implement Plan.ready")


def validate_plan(plan: Plan) -> None:
    """Validate the plan's structure.

    Contract (every failure raises ``PlanError`` with a message naming the
    offending workstream):
        - the goal is non-blank;
        - there is at least one workstream;
        - every workstream id is non-blank and unique;
        - every objective is non-blank;
        - ``kind`` is exactly ``CAPABILITY`` or ``REASONING`` (closed set);
        - a capability workstream names a non-blank ``capability``;
        - a reasoning workstream does not name a capability;
        - every dependency refers to a workstream in this plan;
        - the dependency graph is acyclic;
        - every workstream declares at least one acceptance criterion;
        - ``budget_usd``, when set, is positive.
    """
    raise NotImplementedError("Week 6 lab: implement validate_plan")


def topo_order(plan: Plan) -> tuple[Workstream, ...]:
    """Return workstreams in dependency order, deterministic across runs.

    Contract: validates first; ties are broken by declaration order (Kahn's
    algorithm fed in declaration order) so two runs of the same plan always
    schedule identically. Raises ``PlanError`` for an invalid plan.
    """
    raise NotImplementedError("Week 6 lab: implement topo_order")


def ready_workstreams(plan: Plan, completed: Collection[str]) -> tuple[Workstream, ...]:
    """Workstreams that can run now, in declaration order.

    A workstream is ready when every id in ``depends_on`` is in ``completed``
    and it is not itself in ``completed``. Validates the plan first.
    """
    raise NotImplementedError("Week 6 lab: implement ready_workstreams")


@dataclass(frozen=True, slots=True)
class ReplanDecision:
    """The plan after replanning, plus an audit of what was dropped and why.

    Attributes:
        plan: the reduced plan (still valid, still has workstreams).
        dropped: ids removed because they failed or depended on the failure.
        reason: human-readable explanation (carried into the trace/audit row).
    """

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
    """Drop a failed workstream and everything that depends on it.

    Contract:
        - validates the plan; unknown ``failed_id`` raises ``PlanError``;
        - when ``attempts >= max_attempts`` raises ``PlanError`` (retry budget
          exhausted -- replanning is not a licence to loop forever);
        - transitively removes the failed workstream and all dependents (they
          cannot run without it), keeping independent branches untouched;
        - raises ``PlanError`` when no workstreams would remain (a plan that
          cannot be salvaged must be reported, not silently emptied);
        - the returned plan's goal is unchanged and the returned plan validates.
    """
    raise NotImplementedError("Week 6 lab: implement replan_after_failure")
