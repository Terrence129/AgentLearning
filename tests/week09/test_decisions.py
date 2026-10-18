"""Tests for the typed decision union and its presentation budgets (week 9)."""

from __future__ import annotations

import pytest
from agentlab.capstone.decisions import (
    DECISION_KINDS,
    PresentationBudgetError,
    PresentationBudgets,
    decision_to_wire,
    enforce_presentation_budgets,
    parse_decision,
)
from agentlab.errors import SchemaValidationError

pytestmark = pytest.mark.week


def wire(**overrides: object) -> dict[str, object]:
    """A valid direct_answer payload, with overrides."""
    payload: dict[str, object] = {
        "kind": "direct_answer",
        "headline": "Refund approved for order ORD-1",
        "answer": "The refund is approved. It settles in three days.",
    }
    payload.update(overrides)
    return payload


def valid_wires() -> list[dict[str, object]]:
    """One valid payload per decision kind, used for union coverage."""
    return [
        {
            "kind": "clarification_prompt",
            "headline": "Which customer?",
            "question": "Which customer should the refund go to?",
            "options": ["Acme", "Globex"],
        },
        {
            "kind": "direct_answer",
            "headline": "Refund approved",
            "answer": "The refund is approved. It settles in three days.",
        },
        {
            "kind": "analysis_conclusion",
            "headline": "Deal is margin-negative",
            "conclusion": "At a 30% discount the deal loses money. The floor is 15%.",
        },
        {
            "kind": "recommendation",
            "headline": "Cap discount at 12%",
            "recommendation": "Offer 12%, not 30%.",
            "rationale": "Protects margin while keeping the customer.",
            "confidence": 0.72,
        },
        {
            "kind": "action_proposal",
            "headline": "Apply a 12% discount",
            "capability_id": "apply_discount",
            "arguments": {"order_id": "ORD-1", "percent": 12},
        },
        {
            "kind": "approval_required",
            "headline": "Discount needs approval",
            "proposal_id": "prop-1",
            "reason": "Any discount above 10% needs a manager.",
        },
        {
            "kind": "execution_result",
            "headline": "Discount applied",
            "status": "executed",
            "reference": "ORD-1",
        },
        {
            "kind": "limitation",
            "headline": "Cannot price custom orders",
            "reason": "No pricing capability exists for custom orders.",
            "missing": ["price_custom_order"],
        },
    ]


@pytest.mark.parametrize("payload", valid_wires(), ids=lambda p: str(p["kind"]))
def test_parse_covers_every_declared_kind(payload: dict[str, object]) -> None:
    decision = parse_decision(payload)
    assert decision.kind == payload["kind"]
    assert decision.kind in DECISION_KINDS


def test_parse_exposes_kind_specific_fields() -> None:
    decision = parse_decision(valid_wires()[3])  # recommendation
    assert decision.recommendation == "Offer 12%, not 30%."
    assert decision.confidence == pytest.approx(0.72)

    proposal = parse_decision(valid_wires()[4])  # action_proposal
    assert proposal.capability_id == "apply_discount"
    assert proposal.arguments == {"order_id": "ORD-1", "percent": 12}


def test_parse_rejects_unknown_kind() -> None:
    with pytest.raises(SchemaValidationError) as caught:
        parse_decision({"kind": "essay", "headline": "Thoughts"})
    assert any("kind" in problem for problem in caught.value.errors)


def test_parse_rejects_missing_required_field() -> None:
    payload = {
        "kind": "recommendation",
        "headline": "Cap discount",
        "recommendation": "Offer 12%.",
        "rationale": "Protects margin.",
    }
    with pytest.raises(SchemaValidationError) as caught:
        parse_decision(payload)
    assert any("confidence" in problem for problem in caught.value.errors)


def test_parse_rejects_unknown_field() -> None:
    with pytest.raises(SchemaValidationError) as caught:
        parse_decision(wire(confidence=0.5))
    assert any("confidence" in problem for problem in caught.value.errors)


def test_parse_rejects_non_object_payload() -> None:
    with pytest.raises(SchemaValidationError):
        parse_decision(["not", "a", "mapping"])  # type: ignore[arg-type]


def test_parse_rejects_out_of_range_confidence() -> None:
    payload = dict(valid_wires()[3])
    payload["confidence"] = 1.5
    with pytest.raises(SchemaValidationError):
        parse_decision(payload)


def test_parse_rejects_unknown_status() -> None:
    payload = dict(valid_wires()[6])
    payload["status"] = "done"
    with pytest.raises(SchemaValidationError):
        parse_decision(payload)


@pytest.mark.parametrize("payload", valid_wires(), ids=lambda p: str(p["kind"]))
def test_wire_round_trip(payload: dict[str, object]) -> None:
    first = parse_decision(payload)
    as_wire = decision_to_wire(first)
    assert as_wire["kind"] == payload["kind"]
    assert isinstance(as_wire.get("next_moves", []), list)
    assert parse_decision(as_wire) == first


def test_budget_accepts_a_ui_shaped_decision() -> None:
    decision = parse_decision(valid_wires()[1])  # direct_answer, 2 sentences
    assert enforce_presentation_budgets(decision) is decision


def test_budget_rejects_a_long_headline() -> None:
    decision = parse_decision(
        wire(headline="one two three four five six seven eight nine ten eleven twelve thirteen")
    )
    with pytest.raises(PresentationBudgetError) as caught:
        enforce_presentation_budgets(decision)
    assert any("headline" in violation for violation in caught.value.violations)


def test_budget_rejects_too_many_next_moves() -> None:
    decision = parse_decision(wire(next_moves=["one", "two", "three", "four", "five"]))
    with pytest.raises(PresentationBudgetError) as caught:
        enforce_presentation_budgets(decision)
    assert any("next_moves" in violation for violation in caught.value.violations)


def test_budget_rejects_too_many_question_options() -> None:
    payload = dict(valid_wires()[0])
    payload["options"] = ["A", "B", "C", "D"]
    with pytest.raises(PresentationBudgetError) as caught:
        enforce_presentation_budgets(parse_decision(payload))
    assert any("options" in violation for violation in caught.value.violations)


def test_budget_rejects_a_three_sentence_meaning() -> None:
    decision = parse_decision(wire(answer="The refund is approved. It settles in three days. Thank you."))
    with pytest.raises(PresentationBudgetError) as caught:
        enforce_presentation_budgets(decision)
    assert any("sentences" in violation for violation in caught.value.violations)


def test_budget_collects_all_violations_at_once() -> None:
    decision = parse_decision(
        wire(
            headline="one two three four five six seven eight nine ten eleven twelve thirteen",
            next_moves=["a", "b", "c", "d", "e"],
            answer="One. Two. Three.",
        )
    )
    with pytest.raises(PresentationBudgetError) as caught:
        enforce_presentation_budgets(decision)
    assert len(caught.value.violations) >= 3


def test_budget_honours_custom_limits() -> None:
    decision = parse_decision(wire(headline="Refund approved for order ORD-1"))
    with pytest.raises(PresentationBudgetError):
        enforce_presentation_budgets(decision, PresentationBudgets(max_headline_words=3))
