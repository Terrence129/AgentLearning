"""Tests for topology-driven orchestration and per-workstream budgets (week 6 lab)."""

from __future__ import annotations

import json

import pytest
from agentlab.orchestrator.orchestrator import (
    ExecutionShape,
    Orchestrator,
    classify_shape,
)
from agentlab.orchestrator.plan import NodeKind, Plan, PlanError, Workstream
from agentlab.orchestrator.specialist import Specialist, SpecialistSpec
from agentlab.pricing import estimate_cost
from agentlab.testing import MockProvider, text_turn
from agentlab.tools.registry import ToolRegistry
from agentlab.types import Usage

pytestmark = pytest.mark.week


def cap_ws(
    id: str,
    *,
    capability: str = "refund.issue",
    depends_on: tuple[str, ...] = (),
    inputs: dict | None = None,
    budget_usd: float | None = None,
) -> Workstream:
    return Workstream(
        id=id,
        objective=f"capability step {id}",
        kind=NodeKind.CAPABILITY,
        capability=capability,
        depends_on=depends_on,
        acceptance_criteria=("returns a result",),
        inputs=inputs or {},
        budget_usd=budget_usd,
    )


def reason_ws(id: str, *, depends_on: tuple[str, ...] = (), budget_usd: float | None = None) -> Workstream:
    return Workstream(
        id=id,
        objective=f"reasoning step {id}",
        kind=NodeKind.REASONING,
        depends_on=depends_on,
        acceptance_criteria=("produces a recommendation",),
        budget_usd=budget_usd,
    )


def plan(*workstreams: Workstream) -> Plan:
    return Plan(goal="decide the enterprise discount", workstreams=tuple(workstreams))


def make_specialist(
    name: str = "researcher",
    *,
    summary: str | None = None,
    usage: Usage | None = None,
) -> tuple[Specialist, MockProvider]:
    payload = {
        "summary": summary or f"{name} recommendation",
        "findings": [f"{name} finding"],
        "confidence": 0.8,
        "artifacts": [],
    }
    provider = MockProvider(
        [text_turn(json.dumps(payload), usage=usage or Usage(100, 10))],
        model="gpt-4.1-mini",
    )
    spec = SpecialistSpec(name=name, system_prompt=f"You are {name}.", max_steps=2)
    return Specialist(spec, provider, ToolRegistry()), provider


def result_by_id(results) -> dict:
    return {result.workstream_id: result for result in results}


def test_single_capability_plan_runs_without_a_model() -> None:
    invocations: list[dict] = []

    def refund_executor(inputs: dict) -> dict:
        invocations.append(inputs)
        return {"approved": True, "deal": inputs.get("deal")}

    typed_plan = plan(cap_ws("refund", inputs={"deal": "deal-42"}))
    orchestrator = Orchestrator(capabilities={"refund.issue": refund_executor})

    result = orchestrator.run(typed_plan)

    assert result.selection.derived is ExecutionShape.DIRECT_CAPABILITY
    assert result.ok
    assert len(result.workstreams) == 1
    workstream = result.workstreams[0]
    assert workstream.ok
    assert json.loads(workstream.output)["deal"] == "deal-42"
    assert invocations == [{"deal": "deal-42"}]


def test_single_reasoning_plan_runs_one_specialist() -> None:
    specialist, provider = make_specialist("researcher", summary="hold the discount")
    orchestrator = Orchestrator(specialists={"researcher": specialist})

    result = orchestrator.run(plan(reason_ws("researcher")))

    assert result.selection.derived is ExecutionShape.DIRECT_SPECIALIST
    assert result.ok
    assert result.workstreams[0].handoff.summary == "hold the discount"
    assert len(provider.calls) == 1


def test_connected_workstreams_form_a_squad_and_pass_outputs_forward() -> None:
    specialist, provider = make_specialist("analyst", summary="discount is safe")

    def search_executor(inputs: dict) -> dict:
        return {"docs": [f"{inputs['query']}: refunds within 30 days"]}

    typed_plan = plan(
        cap_ws("gather", capability="knowledge.search", inputs={"query": "refund policy"}),
        reason_ws("analyse", depends_on=("gather",)),
    )
    orchestrator = Orchestrator(
        capabilities={"knowledge.search": search_executor},
        specialists={"analyse": specialist},
    )

    result = orchestrator.run(typed_plan)

    assert result.selection.derived is ExecutionShape.SINGLE_SQUAD
    assert result.ok
    assert [item.workstream_id for item in result.workstreams] == ["gather", "analyse"]
    prompt = provider.calls[0].messages[1].content or ""
    assert "refund policy" in prompt
    assert "decide the enterprise discount" in prompt


def test_disconnected_components_run_as_multi_squad_when_backed() -> None:
    first, first_provider = make_specialist("researcher")
    second, second_provider = make_specialist("writer")
    orchestrator = Orchestrator(specialists={"researcher": first, "writer": second})

    result = orchestrator.run(plan(reason_ws("researcher"), reason_ws("writer")))

    assert result.selection.derived is ExecutionShape.MULTI_SQUAD
    assert result.selection.backed
    assert result.ok
    assert len(result.workstreams) == 2
    assert len(first_provider.calls) == len(second_provider.calls) == 1


def test_unbacked_multi_squad_returns_a_limitation_without_executing() -> None:
    first, first_provider = make_specialist("researcher")
    second, second_provider = make_specialist("writer")
    orchestrator = Orchestrator(
        specialists={"researcher": first, "writer": second},
        backed_shapes={
            ExecutionShape.DIRECT_CAPABILITY,
            ExecutionShape.DIRECT_SPECIALIST,
            ExecutionShape.SINGLE_SQUAD,
        },
    )

    result = orchestrator.run(plan(reason_ws("researcher"), reason_ws("writer")))

    assert not result.selection.backed
    assert result.selection.derived is ExecutionShape.MULTI_SQUAD
    assert result.selection.shape is None
    assert result.selection.limitation is not None
    assert "multi_squad" in result.selection.limitation
    assert result.limitations
    assert result.workstreams == ()
    assert not result.ok
    assert first_provider.calls == [] and second_provider.calls == []


def test_unbacked_direct_specialist_returns_a_limitation() -> None:
    specialist, provider = make_specialist("researcher")
    orchestrator = Orchestrator(
        specialists={"researcher": specialist},
        backed_shapes={ExecutionShape.DIRECT_CAPABILITY},
    )

    result = orchestrator.run(plan(reason_ws("researcher")))

    assert result.selection.derived is ExecutionShape.DIRECT_SPECIALIST
    assert not result.selection.backed
    assert "direct_specialist" in (result.selection.limitation or "")
    assert provider.calls == []


def test_dependency_failure_skips_dependents_but_runs_independent_branches() -> None:
    specialist, specialist_provider = make_specialist("analyst")

    def down_executor(inputs: dict) -> dict:
        raise RuntimeError("index down")

    def report_executor(inputs: dict) -> dict:
        return {"report": "ready"}

    typed_plan = plan(
        cap_ws("gather", capability="knowledge.search"),
        reason_ws("analyse", depends_on=("gather",)),
        cap_ws("report", capability="report.render"),
    )
    orchestrator = Orchestrator(
        capabilities={"knowledge.search": down_executor, "report.render": report_executor},
        specialists={"analyse": specialist},
    )

    result = orchestrator.run(typed_plan)
    results = result_by_id(result.workstreams)

    assert [item.workstream_id for item in result.workstreams] == ["gather", "report", "analyse"]
    assert not results["gather"].ok
    assert "index down" in (results["gather"].error or "")
    assert results["report"].ok
    assert results["analyse"].skipped
    assert not results["analyse"].ok
    assert "dependency" in (results["analyse"].error or "").lower()
    assert specialist_provider.calls == []
    assert not result.ok


def test_missing_capability_executor_is_a_reported_error_not_a_crash() -> None:
    orchestrator = Orchestrator()

    result = orchestrator.run(plan(cap_ws("refund", capability="refund.issue")))

    assert not result.ok
    assert "no executor" in (result.workstreams[0].error or "").lower()


def test_missing_specialist_is_a_reported_error_not_a_crash() -> None:
    orchestrator = Orchestrator()

    result = orchestrator.run(plan(reason_ws("writer")))

    assert not result.ok
    assert "no specialist" in (result.workstreams[0].error or "").lower()


def test_per_workstream_budget_is_enforced() -> None:
    specialist, _ = make_specialist("researcher", usage=Usage(1_000, 100))
    orchestrator = Orchestrator(specialists={"researcher": specialist})

    result = orchestrator.run(plan(reason_ws("researcher", budget_usd=0.0001)))

    assert not result.ok
    assert "budget" in (result.workstreams[0].error or "").lower()
    assert result.aggregate_budget.used_usd > 0.0001


def test_aggregate_budget_sums_per_workstream_ledgers() -> None:
    first, _ = make_specialist("researcher", usage=Usage(100, 10))
    second, _ = make_specialist("writer", usage=Usage(100, 10))
    orchestrator = Orchestrator(specialists={"researcher": first, "writer": second})
    typed_plan = plan(
        reason_ws("researcher", budget_usd=1.0),
        reason_ws("writer", budget_usd=1.0),
    )

    result = orchestrator.run(typed_plan)

    expected = estimate_cost("gpt-4.1-mini", Usage(100, 10))
    assert result.aggregate_budget.used_input_tokens == 200
    assert result.aggregate_budget.used_output_tokens == 20
    assert result.aggregate_budget.steps == 2
    assert result.aggregate_budget.used_usd == pytest.approx(2 * expected)


def test_invalid_plan_raises_before_any_execution() -> None:
    broken = plan(reason_ws("a", depends_on=("b",)), reason_ws("b", depends_on=("a",)))
    orchestrator = Orchestrator()

    with pytest.raises(PlanError):
        orchestrator.run(broken)


def test_execution_order_is_deterministic_and_declaration_ordered() -> None:
    called: list[str] = []

    def executor(inputs: dict) -> dict:
        called.append(inputs["name"])
        return {"ok": True}

    typed_plan = plan(
        cap_ws("c", depends_on=("a",), inputs={"name": "c"}),
        cap_ws("a", inputs={"name": "a"}),
        cap_ws("b", inputs={"name": "b"}),
    )
    orchestrator = Orchestrator(capabilities={"refund.issue": executor})

    first = orchestrator.run(typed_plan)
    second = orchestrator.run(typed_plan)

    assert [item.workstream_id for item in first.workstreams] == ["a", "b", "c"]
    assert [item.workstream_id for item in second.workstreams] == ["a", "b", "c"]
    assert called == ["a", "b", "c", "a", "b", "c"]
    assert classify_shape(typed_plan) is ExecutionShape.MULTI_SQUAD
