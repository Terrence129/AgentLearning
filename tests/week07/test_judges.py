"""Judge tests: forced JSON, rubric math, and human-agreement measurement."""

from __future__ import annotations

import json

import pytest
from agentlab.errors import SchemaValidationError
from agentlab.evals.dataset import EvalCase, RubricCriterion
from agentlab.evals.judges import (
    RubricJudge,
    agreement_rate,
    cohen_kappa,
    measure_agreement,
)
from agentlab.testing import MockProvider, text_turn

pytestmark = pytest.mark.week


def _case() -> EvalCase:
    return EvalCase(
        id="case-1",
        input="Refund order 42",
        rubric=[
            RubricCriterion(id="decision", description="States approve or deny", weight=2.0),
            RubricCriterion(id="citation", description="Cites the policy clause", weight=1.0),
        ],
        pass_threshold=0.8,
    )


def _judge_json(scores: dict[str, int], reasons: dict[str, str] | None = None) -> str:
    criteria = [
        {"id": criterion_id, "score": score, "reason": (reasons or {}).get(criterion_id, "because")}
        for criterion_id, score in scores.items()
    ]
    return json.dumps({"criteria": criteria})


def test_judge_sends_rubric_and_forces_json():
    provider = MockProvider([text_turn(_judge_json({"decision": 2, "citation": 1}))])

    verdict = RubricJudge(provider).judge(_case(), "Refund approved. Policy clause 3.2 applies.")

    request = provider.calls[0]
    assert request.response_format == {"type": "json_object"}
    prompt = "\n".join(message.content or "" for message in request.messages)
    assert "States approve or deny" in prompt
    assert "Cites the policy clause" in prompt
    assert "Refund approved. Policy clause 3.2 applies." in prompt
    assert verdict.criterion_scores == {"decision": 2, "citation": 1}
    assert verdict.score == pytest.approx(5 / 6)
    assert verdict.passed is True
    assert verdict.reasons["decision"] == "because"


def test_judge_score_below_threshold_fails():
    provider = MockProvider([text_turn(_judge_json({"decision": 1, "citation": 1}))])

    verdict = RubricJudge(provider).judge(_case(), "Maybe refunded.")

    assert verdict.score == pytest.approx(0.5)
    assert verdict.passed is False


def test_judge_rejects_non_json_output():
    provider = MockProvider([text_turn("The output looks good, 5/5.")])

    with pytest.raises(SchemaValidationError) as excinfo:
        RubricJudge(provider).judge(_case(), "Refund approved.")

    assert excinfo.value.raw == "The output looks good, 5/5."


def test_judge_rejects_missing_criterion():
    provider = MockProvider([text_turn(_judge_json({"decision": 2}))])

    with pytest.raises(SchemaValidationError, match="citation"):
        RubricJudge(provider).judge(_case(), "Refund approved.")


def test_judge_rejects_unknown_criterion_id():
    provider = MockProvider([text_turn(_judge_json({"decision": 2, "citation": 1, "vibes": 2}))])

    with pytest.raises(SchemaValidationError, match="vibes"):
        RubricJudge(provider).judge(_case(), "Refund approved.")


def test_judge_rejects_out_of_range_score():
    provider = MockProvider([text_turn(_judge_json({"decision": 3, "citation": 1}))])

    with pytest.raises(SchemaValidationError, match="score"):
        RubricJudge(provider).judge(_case(), "Refund approved.")


def test_agreement_rate_counts_equal_labels():
    rate = agreement_rate([True, True, False], [True, False, False])

    assert rate == pytest.approx(2 / 3)


def test_agreement_rate_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="length"):
        agreement_rate([True], [True, False])


def test_cohen_kappa_corrects_for_chance():
    # 75% raw agreement, but both labellers mostly say "pass": kappa = 0.5.
    kappa = cohen_kappa([True, True, False, False], [True, True, False, True])

    assert kappa == pytest.approx(0.5)


def test_cohen_kappa_is_one_for_perfect_agreement():
    assert cohen_kappa([True, False, True], [True, False, True]) == pytest.approx(1.0)


def test_measure_agreement_pairs_by_case_id():
    verdicts = {"c1": True, "c2": True, "c3": False}
    labels = {"c1": True, "c2": False, "c3": False}

    report = measure_agreement(verdicts, labels)

    assert report.n == 3
    assert report.agreement == pytest.approx(2 / 3)
    assert report.kappa == pytest.approx(0.4)
    assert report.disagreements == ("c2",)


def test_measure_agreement_rejects_id_mismatch():
    with pytest.raises(ValueError, match="same ids"):
        measure_agreement({"c1": True}, {"c1": True, "c2": False})
