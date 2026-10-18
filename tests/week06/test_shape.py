"""Tests for topology-driven shape selection (week 6 lab)."""

from __future__ import annotations

import pytest
from agentlab.orchestrator.orchestrator import (
    ExecutionShape,
    classify_shape,
    component_ids,
    select_shape,
)
from agentlab.orchestrator.plan import NodeKind, Plan, PlanError, Workstream

pytestmark = pytest.mark.week


def capability(id: str, *, depends_on: tuple[str, ...] = (), budget_usd: float | None = None) -> Workstream:
    return Workstream(
        id=id,
        objective=f"capability {id}",
        kind=NodeKind.CAPABILITY,
        capability="refund.issue",
        depends_on=depends_on,
        acceptance_criteria=("returns a result",),
        budget_usd=budget_usd,
    )


def reasoning(id: str, *, depends_on: tuple[str, ...] = (), budget_usd: float | None = None) -> Workstream:
    return Workstream(
        id=id,
        objective=f"reasoning {id}",
        kind=NodeKind.REASONING,
        depends_on=depends_on,
        acceptance_criteria=("produces a recommendation",),
        budget_usd=budget_usd,
    )


def plan(*workstreams: Workstream) -> Plan:
    return Plan(goal="decide the enterprise discount", workstreams=tuple(workstreams))


def test_single_capability_classifies_as_direct_capability() -> None:
    assert classify_shape(plan(capability("a"))) is ExecutionShape.DIRECT_CAPABILITY


def test_single_reasoning_classifies_as_direct_specialist() -> None:
    assert classify_shape(plan(reasoning("a"))) is ExecutionShape.DIRECT_SPECIALIST


def test_connected_workstreams_classify_as_single_squad() -> None:
    shape = classify_shape(plan(capability("a"), reasoning("b", depends_on=("a",))))
    assert shape is ExecutionShape.SINGLE_SQUAD


def test_disconnected_components_classify_as_multi_squad() -> None:
    shape = classify_shape(plan(reasoning("a"), reasoning("b")))
    assert shape is ExecutionShape.MULTI_SQUAD


def test_component_ids_are_declaration_ordered() -> None:
    typed_plan = plan(
        reasoning("c"),
        capability("a"),
        reasoning("b", depends_on=("a",)),
    )

    components = component_ids(typed_plan)

    assert components == (("c",), ("a", "b"))


def test_unbacked_shape_returns_a_limitation_and_never_downgrades() -> None:
    selection = select_shape(
        plan(reasoning("a"), reasoning("b")),
        backed_shapes={
            ExecutionShape.DIRECT_CAPABILITY,
            ExecutionShape.DIRECT_SPECIALIST,
            ExecutionShape.SINGLE_SQUAD,
        },
    )

    assert selection.derived is ExecutionShape.MULTI_SQUAD
    assert selection.shape is None
    assert selection.backed is False
    assert selection.limitation is not None
    assert "multi_squad" in selection.limitation
    assert "guess" in selection.limitation


def test_backed_shape_selects_itself() -> None:
    selection = select_shape(plan(reasoning("a"), reasoning("b")))

    assert selection.derived is ExecutionShape.MULTI_SQUAD
    assert selection.shape is ExecutionShape.MULTI_SQUAD
    assert selection.backed is True
    assert selection.limitation is None


def test_single_reasoning_is_not_downgraded_to_a_capability_call() -> None:
    selection = select_shape(plan(reasoning("a")), backed_shapes={ExecutionShape.DIRECT_CAPABILITY})

    assert selection.derived is ExecutionShape.DIRECT_SPECIALIST
    assert selection.shape is None
    assert selection.limitation is not None
    assert "direct_specialist" in selection.limitation


def test_classification_is_independent_of_budgets() -> None:
    cheap = plan(reasoning("a"), reasoning("b"))
    expensive = plan(reasoning("a", budget_usd=100.0), reasoning("b", budget_usd=250.0))

    assert classify_shape(cheap) is classify_shape(expensive)


def test_invalid_plans_raise_before_classification() -> None:
    with pytest.raises(PlanError):
        classify_shape(
            plan(
                reasoning("a", depends_on=("b",)),
                reasoning("b", depends_on=("a",)),
            )
        )
    with pytest.raises(PlanError):
        select_shape(Plan(goal="empty", workstreams=()))
