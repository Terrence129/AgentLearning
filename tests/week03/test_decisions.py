"""Tests for the typed decision family and its presentation budgets.

Why a discriminated union: one schema must describe "ask", "answer", "decide",
"recommend" and "propose an action" while still validating each shape exactly.
Why budgets in code: a polite prompt does not stop a 40-word headline; a
validator does, and it produces a measurable failure the repair loop can fix.

The governance invariant is asserted too: an ``ActionProposal`` can never claim
it does not need human approval.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from agentlab.errors import SchemaValidationError
from agentlab.schemas.structured import (
    DEFAULT_PRESENTATION_BUDGET,
    ActionProposal,
    ClarificationPrompt,
    Decision,
    DirectAnswer,
    PresentationBudget,
    Recommendation,
    StructuredExtractor,
    decision_schema,
    parse_decision,
)
from agentlab.testing import MockProvider, text_turn
from agentlab.types import Message
from pydantic import ValidationError

pytestmark = pytest.mark.week


def _words(count: int) -> str:
    return " ".join(f"word{index}" for index in range(count))


def _base_payload(kind: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "kind": kind,
        "headline": "Clear one-line answer",
        "meaning": "One sentence of meaning.",
        "next_moves": [],
    }
    payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# presentation budgets
# ---------------------------------------------------------------------------


def test_presentation_budget_accepts_compliant_message() -> None:
    violations = DEFAULT_PRESENTATION_BUDGET.violations(
        headline=_words(12),
        meaning="One sentence. Two sentences.",
        next_moves=["a", "b", "c", "d"],
        question_options=["yes", "no"],
    )

    assert violations == []


def test_presentation_budget_flags_long_headline() -> None:
    violations = DEFAULT_PRESENTATION_BUDGET.violations(
        headline=_words(13), meaning="One sentence.", next_moves=[]
    )

    assert len(violations) == 1
    assert "headline" in violations[0]


def test_presentation_budget_flags_too_many_meaning_sentences() -> None:
    violations = DEFAULT_PRESENTATION_BUDGET.violations(
        headline="Short", meaning="One. Two. Three.", next_moves=[]
    )

    assert any("meaning" in violation for violation in violations)


def test_presentation_budget_flags_too_many_next_moves() -> None:
    violations = DEFAULT_PRESENTATION_BUDGET.violations(
        headline="Short", meaning="One sentence.", next_moves=["a", "b", "c", "d", "e"]
    )

    assert any("next_moves" in violation for violation in violations)


def test_presentation_budget_flags_too_many_question_options() -> None:
    violations = DEFAULT_PRESENTATION_BUDGET.violations(
        headline="Short",
        meaning="One sentence.",
        next_moves=[],
        question_options=["a", "b", "c", "d"],
    )

    assert any("question_options" in violation for violation in violations)


def test_presentation_budget_enforce_raises_schema_validation_error() -> None:
    budget = PresentationBudget()

    with pytest.raises(SchemaValidationError) as info:
        budget.enforce(headline=_words(13), meaning="One sentence.", next_moves=[])

    assert info.value.errors
    assert "headline" in str(info.value)


# ---------------------------------------------------------------------------
# concrete decisions
# ---------------------------------------------------------------------------


def test_direct_answer_accepts_compliant_payload() -> None:
    answer = DirectAnswer(
        headline="The total is 60",
        meaning="The arithmetic is straightforward.",
        answer="60",
    )

    assert answer.kind == "direct_answer"
    assert answer.answer == "60"
    assert answer.confidence == 1.0


def test_direct_answer_rejects_over_budget_headline() -> None:
    with pytest.raises(SchemaValidationError, match="headline"):
        DirectAnswer(
            headline=_words(13),
            meaning="One sentence of meaning.",
            answer="42",
        )


def test_direct_answer_rejects_over_budget_meaning() -> None:
    with pytest.raises(SchemaValidationError, match="meaning"):
        DirectAnswer(
            headline="Clear headline",
            meaning="One. Two. Three.",
            answer="42",
        )


def test_direct_answer_rejects_too_many_next_moves() -> None:
    with pytest.raises(SchemaValidationError, match="next_moves"):
        DirectAnswer(
            headline="Clear headline",
            meaning="One sentence.",
            answer="42",
            next_moves=["a", "b", "c", "d", "e"],
        )


def test_clarification_rejects_too_many_options() -> None:
    with pytest.raises(SchemaValidationError, match="question_options"):
        ClarificationPrompt(
            headline="Need one detail",
            meaning="The request is ambiguous.",
            question="Which account?",
            options=["a", "b", "c", "d"],
        )


def test_action_proposal_cannot_self_approve() -> None:
    with pytest.raises(ValidationError):
        ActionProposal(
            headline="Send the quote",
            meaning="The customer requested it.",
            action="send_quote",
            requires_approval=False,
        )


def test_action_proposal_defaults_to_requiring_approval() -> None:
    proposal = ActionProposal(
        headline="Send the quote",
        meaning="The customer requested it.",
        action="send_quote",
        parameters={"amount": 100},
    )

    assert proposal.requires_approval is True
    assert proposal.parameters == {"amount": 100}


# ---------------------------------------------------------------------------
# parsing the union
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("payload", "expected_type"),
    [
        (
            _base_payload(
                "clarification",
                question="Which account?",
                options=["Sales", "Support"],
            ),
            ClarificationPrompt,
        ),
        (_base_payload("direct_answer", answer="42"), DirectAnswer),
        (
            _base_payload(
                "decision",
                decision="hold",
                rationale="The margin does not cover the discount.",
            ),
            Decision,
        ),
        (_base_payload("recommendation", recommendation="Renew for 12 months"), Recommendation),
        (
            _base_payload("action_proposal", action="send_quote", parameters={"amount": 100}),
            ActionProposal,
        ),
    ],
)
def test_parse_decision_selects_variant_by_kind(payload: dict[str, Any], expected_type: type) -> None:
    decision = parse_decision(payload)

    assert isinstance(decision, expected_type)
    assert decision.kind == payload["kind"]
    assert decision.headline == payload["headline"]


def test_parse_decision_rejects_unknown_kind() -> None:
    payload = _base_payload("poem")

    with pytest.raises(ValidationError):
        parse_decision(payload)


def test_parse_decision_rejects_missing_kind() -> None:
    with pytest.raises(ValidationError):
        parse_decision({"headline": "x", "meaning": "y"})


def test_decision_schema_is_a_tagged_union() -> None:
    schema = decision_schema()
    serialized = json.dumps(schema)

    for kind in ("clarification", "direct_answer", "decision", "recommendation", "action_proposal"):
        assert kind in serialized
    assert schema["discriminator"]["propertyName"] == "kind"


# ---------------------------------------------------------------------------
# extraction integration
# ---------------------------------------------------------------------------


def test_extract_typed_decision_from_model_output() -> None:
    raw = json.dumps(
        {
            "kind": "direct_answer",
            "headline": "The total is 60",
            "meaning": "The arithmetic is straightforward.",
            "next_moves": [],
            "answer": "60",
        }
    )
    provider = MockProvider([text_turn(raw)])

    result = StructuredExtractor(provider).extract([Message.user("What is 12 * 5?")], DirectAnswer)

    assert result.valid is True
    assert isinstance(result.value, DirectAnswer)
    assert result.value.answer == "60"


def test_extract_rejects_over_budget_decision() -> None:
    raw = json.dumps(
        {
            "kind": "direct_answer",
            "headline": _words(13),
            "meaning": "One sentence of meaning.",
            "answer": "60",
        }
    )
    provider = MockProvider([text_turn(raw)])

    result = StructuredExtractor(provider).extract(
        [Message.user("What is 12 * 5?")], DirectAnswer, max_repairs=0
    )

    assert result.valid is False
    assert result.value is None
    assert any("headline" in error for error in result.errors)
