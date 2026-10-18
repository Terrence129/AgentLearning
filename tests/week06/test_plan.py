"""Tests for typed plans, validation, ordering and replanning (week 6 lab)."""

from __future__ import annotations

import pytest
from agentlab.orchestrator.plan import (
    NodeKind,
    Plan,
    PlanError,
    Workstream,
    ready_workstreams,
    replan_after_failure,
    topo_order,
    validate_plan,
)

pytestmark = pytest.mark.week


def capability(id: str, *, depends_on: tuple[str, ...] = (), capability: str = "refund.issue") -> Workstream:
    return Workstream(
        id=id,
        objective=f"capability step {id}",
        kind=NodeKind.CAPABILITY,
        capability=capability,
        depends_on=depends_on,
        acceptance_criteria=("returns a result",),
    )


def reasoning(id: str, *, depends_on: tuple[str, ...] = ()) -> Workstream:
    return Workstream(
        id=id,
        objective=f"reasoning step {id}",
        kind=NodeKind.REASONING,
        depends_on=depends_on,
        acceptance_criteria=("produces a recommendation",),
    )


def plan(*workstreams: Workstream, goal: str = "decide the enterprise discount") -> Plan:
    return Plan(goal=goal, workstreams=tuple(workstreams))


def test_valid_plan_passes_validation_and_lookup() -> None:
    first = capability("gather")
    second = reasoning("analyse", depends_on=("gather",))
    typed_plan = plan(first, second)

    typed_plan.validate()
    validate_plan(typed_plan)

    assert typed_plan.get("gather") == first
    assert typed_plan.get("missing") is None


def test_blank_goal_is_rejected() -> None:
    with pytest.raises(PlanError, match="goal"):
        validate_plan(plan(capability("a"), goal="   "))


def test_empty_plan_is_rejected() -> None:
    with pytest.raises(PlanError, match="at least one"):
        validate_plan(Plan(goal="do something", workstreams=()))


def test_duplicate_workstream_ids_are_rejected() -> None:
    with pytest.raises(PlanError, match="duplicate"):
        validate_plan(plan(capability("a"), reasoning("a")))


def test_unknown_dependency_is_rejected() -> None:
    with pytest.raises(PlanError, match="unknown"):
        validate_plan(plan(capability("a", depends_on=("ghost",))))


def test_dependency_cycle_is_rejected() -> None:
    with pytest.raises(PlanError, match="cycle"):
        validate_plan(
            plan(
                reasoning("a", depends_on=("b",)),
                reasoning("b", depends_on=("a",)),
            )
        )


def test_capability_workstream_must_name_a_capability() -> None:
    broken = Workstream(
        id="a",
        objective="do it",
        kind=NodeKind.CAPABILITY,
        acceptance_criteria=("done",),
    )
    with pytest.raises(PlanError, match="capability"):
        validate_plan(plan(broken))


def test_reasoning_workstream_must_not_name_a_capability() -> None:
    broken = Workstream(
        id="a",
        objective="think",
        kind=NodeKind.REASONING,
        capability="refund.issue",
        acceptance_criteria=("done",),
    )
    with pytest.raises(PlanError, match="reasoning"):
        validate_plan(plan(broken))


def test_unknown_node_kind_is_rejected() -> None:
    broken = Workstream(
        id="a",
        objective="mystery",
        kind="vibes",  # type: ignore[arg-type]
        acceptance_criteria=("done",),
    )
    with pytest.raises(PlanError, match="kind"):
        validate_plan(plan(broken))


def test_acceptance_criteria_are_required() -> None:
    unverifiable = Workstream(id="a", objective="do it", kind=NodeKind.REASONING)
    with pytest.raises(PlanError, match="acceptance"):
        validate_plan(plan(unverifiable))


def test_non_positive_workstream_budget_is_rejected() -> None:
    broke = Workstream(
        id="a",
        objective="do it",
        kind=NodeKind.REASONING,
        acceptance_criteria=("done",),
        budget_usd=0.0,
    )
    with pytest.raises(PlanError, match="budget"):
        validate_plan(plan(broke))


def test_topo_order_respects_dependencies_and_declaration_ties() -> None:
    typed_plan = plan(
        capability("b", depends_on=("a",)),
        capability("a"),
        capability("c"),
    )

    ordered = topo_order(typed_plan)

    assert [workstream.id for workstream in ordered] == ["a", "c", "b"]


def test_ready_workstreams_tracks_completion() -> None:
    typed_plan = plan(
        capability("a"),
        capability("b", depends_on=("a",)),
        capability("c", depends_on=("b",)),
    )

    assert [workstream.id for workstream in ready_workstreams(typed_plan, set())] == ["a"]
    assert [workstream.id for workstream in ready_workstreams(typed_plan, {"a"})] == ["b"]
    assert [workstream.id for workstream in ready_workstreams(typed_plan, {"a", "b"})] == ["c"]
    assert ready_workstreams(typed_plan, {"a", "b", "c"}) == ()


def test_replan_drops_failed_workstream_and_dependents() -> None:
    typed_plan = plan(
        capability("a"),
        capability("b", depends_on=("a",)),
        reasoning("c", depends_on=("b",)),
        capability("independent"),
    )

    decision = replan_after_failure(typed_plan, "b", reason="capability unavailable")

    assert [workstream.id for workstream in decision.plan.workstreams] == ["a", "independent"]
    assert decision.dropped == ("b", "c")
    assert decision.reason == "capability unavailable"
    decision.plan.validate()
    assert typed_plan.get("b") is not None  # the original plan is untouched


def test_replan_raises_when_retries_are_exhausted() -> None:
    typed_plan = plan(capability("a"))
    with pytest.raises(PlanError, match="retry"):
        replan_after_failure(typed_plan, "a", reason="still broken", attempts=2, max_attempts=2)


def test_replan_raises_when_nothing_can_be_salvaged() -> None:
    typed_plan = plan(capability("a"))
    with pytest.raises(PlanError, match="salvage"):
        replan_after_failure(typed_plan, "a", reason="failed")


def test_replan_rejects_unknown_workstream_ids() -> None:
    with pytest.raises(PlanError, match="unknown"):
        replan_after_failure(plan(capability("a")), "ghost", reason="n/a")
