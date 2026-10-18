"""Tests for isolated specialists and typed hand-offs (week 6 lab)."""

from __future__ import annotations

import json

import pytest
from agentlab.budget import Budget
from agentlab.errors import BudgetExceeded
from agentlab.orchestrator.specialist import (
    ContextEnvelope,
    HandoffArtifact,
    Specialist,
    SpecialistError,
    SpecialistSpec,
)
from agentlab.testing import MemorySink, MockProvider, Tracer, text_turn, tool_turn
from agentlab.tools.registry import Tool, ToolRegistry
from agentlab.types import Usage

pytestmark = pytest.mark.week


def handoff_json(**overrides: object) -> str:
    payload: dict[str, object] = {
        "summary": "Refunds are allowed within 30 days.",
        "findings": ["30-day window", "$500 cap"],
        "confidence": 0.8,
        "artifacts": ["doc://refund-policy"],
    }
    payload.update(overrides)
    return json.dumps(payload)


def make_tools() -> tuple[ToolRegistry, list[tuple[str, dict]]]:
    invoked: list[tuple[str, dict]] = []
    registry = ToolRegistry()

    def search(arguments: dict) -> dict:
        invoked.append(("search", arguments))
        return {"results": ["refund policy: 30 days"]}

    def delete_records(arguments: dict) -> dict:
        invoked.append(("delete_records", arguments))
        return {"deleted": True}

    registry.register(
        Tool(name="search", description="Search docs", parameters={"type": "object"}, handler=search)
    )
    registry.register(
        Tool(
            name="delete_records",
            description="Delete everything",
            parameters={"type": "object"},
            handler=delete_records,
            is_write=True,
        )
    )
    return registry, invoked


def make_specialist(
    *,
    provider: MockProvider | None = None,
    tools: tuple[str, ...] = (),
    max_steps: int = 3,
    budget: Budget | None = None,
    tracer: Tracer | None = None,
) -> tuple[Specialist, MockProvider, list[tuple[str, dict]]]:
    registry, invoked = make_tools()
    provider = provider or MockProvider([text_turn(handoff_json())])
    spec = SpecialistSpec(
        name="researcher",
        system_prompt="You are a policy researcher. Return a JSON hand-off.",
        tools=tools,
        max_steps=max_steps,
    )
    specialist = Specialist(spec, provider, registry, tracer=tracer, budget=budget)
    return specialist, provider, invoked


def envelope() -> ContextEnvelope:
    return ContextEnvelope(
        objective="Check whether the deal can be refunded",
        facts=("The deal closed 12 days ago",),
        constraints=("Never approve a refund over $500",),
        references=("doc://refund-policy",),
    )


def test_specialist_returns_a_validated_handoff() -> None:
    specialist, _, _ = make_specialist()

    artifact = specialist.run(envelope())

    assert artifact.specialist == "researcher"
    assert artifact.summary == "Refunds are allowed within 30 days."
    assert artifact.findings == ("30-day window", "$500 cap")
    assert artifact.confidence == pytest.approx(0.8)
    assert artifact.artifacts == ("doc://refund-policy",)


def test_specialist_receives_only_the_envelope() -> None:
    specialist, provider, _ = make_specialist()

    specialist.run(envelope())

    messages = provider.calls[0].messages
    assert messages[0].role == "system"
    assert messages[0].content == "You are a policy researcher. Return a JSON hand-off."
    user_content = messages[1].content or ""
    for expected in (
        "Check whether the deal can be refunded",
        "The deal closed 12 days ago",
        "Never approve a refund over $500",
        "doc://refund-policy",
    ):
        assert expected in user_content


def test_specialist_exposes_only_the_allowlisted_tools() -> None:
    provider = MockProvider(
        [tool_turn("delete_records", {"all": True}, call_id="call_1"), text_turn(handoff_json())]
    )
    specialist, _, invoked = make_specialist(provider=provider, tools=("search",))

    specialist.run(envelope())

    assert [spec.name for spec in provider.calls[0].tools] == ["search"]
    assert invoked == []  # the forbidden tool never ran
    tool_messages = [m for m in provider.calls[1].messages if m.role == "tool"]
    assert tool_messages
    assert "not in this specialist's tool set" in (tool_messages[0].content or "")


def test_specialist_executes_an_allowed_tool_and_sees_the_result() -> None:
    provider = MockProvider(
        [tool_turn("search", {"query": "refund"}, call_id="call_1"), text_turn(handoff_json())]
    )
    specialist, _, invoked = make_specialist(provider=provider, tools=("search",))

    specialist.run(envelope())

    assert invoked == [("search", {"query": "refund"})]
    tool_messages = [m for m in provider.calls[1].messages if m.role == "tool"]
    assert "refund policy: 30 days" in (tool_messages[0].content or "")


def test_invalid_handoff_json_raises() -> None:
    specialist, _, _ = make_specialist(provider=MockProvider([text_turn("not a hand-off")]))
    with pytest.raises(SpecialistError, match="hand-off"):
        specialist.run(envelope())


def test_handoff_missing_summary_is_rejected() -> None:
    specialist, _, _ = make_specialist(provider=MockProvider([text_turn(json.dumps({"findings": ["x"]}))]))
    with pytest.raises(SpecialistError, match="summary"):
        specialist.run(envelope())


def test_handoff_confidence_out_of_range_is_rejected() -> None:
    specialist, _, _ = make_specialist(provider=MockProvider([text_turn(handoff_json(confidence=1.5))]))
    with pytest.raises(SpecialistError, match="confidence"):
        specialist.run(envelope())


def test_no_handoff_within_the_step_ceiling_raises() -> None:
    provider = MockProvider([tool_turn("search", {"query": "a"}), tool_turn("search", {"query": "b"})])
    specialist, _, _ = make_specialist(provider=provider, tools=("search",), max_steps=2)

    with pytest.raises(SpecialistError, match="steps"):
        specialist.run(envelope())


def test_traces_record_agent_boundaries_not_transcripts() -> None:
    sink = MemorySink()
    tracer = Tracer(run_id="run-6", sinks=[sink])
    specialist, _, _ = make_specialist(tracer=tracer)

    specialist.run(envelope())

    assert [event.kind for event in sink.events] == ["subagent_start", "subagent_end"]
    assert all(event.data["scope"] == "researcher" for event in sink.events)
    end = sink.events[-1].data
    assert end["summary"] == "Refunds are allowed within 30 days."
    assert end["confidence"] == pytest.approx(0.8)
    assert end["findings"] == 2
    assert "messages" not in end
    assert "transcript" not in end


def test_budget_is_charged_and_enforced() -> None:
    provider = MockProvider([text_turn(handoff_json(), usage=Usage(1_000, 100))], model="gpt-4.1-mini")
    budget = Budget(max_usd=0.0001)
    specialist, _, _ = make_specialist(provider=provider, budget=budget)

    with pytest.raises(BudgetExceeded):
        specialist.run(envelope())

    assert budget.used_usd > 0.0001


def test_a_spec_naming_an_unregistered_tool_fails_fast() -> None:
    specialist, _, _ = make_specialist(tools=("ghost_tool",))
    with pytest.raises(ValueError, match="not registered"):
        specialist.run(envelope())


def test_handoff_as_text_is_compact_and_deterministic() -> None:
    artifact = HandoffArtifact(
        specialist="researcher",
        summary="Refunds are allowed within 30 days.",
        findings=("30-day window", "$500 cap"),
        confidence=0.8,
    )

    text = artifact.as_text()

    assert "researcher" in text
    assert "Refunds are allowed within 30 days." in text
    assert "- 30-day window" in text
    assert text == artifact.as_text()
