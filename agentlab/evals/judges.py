"""Rubric-based LLM judges -- an instrument that must itself be calibrated.

An LLM judge is a measuring device, not an oracle. The research is clear:
position, verbosity and self-enhancement biases are real, and a judge is only
trustworthy once its agreement with human labels has been measured
(``docs/research/03-production-evals-ops.md`` §1.4).

This module therefore has two halves, and the *second* is the important one:

1. ``RubricJudge`` asks a model to score atomic criteria and **forces JSON**
   (``response_format={"type": "json_object"}``). Output that is not exactly a
   valid verdict raises ``SchemaValidationError`` -- it is never repaired by
   guesswork, because a silently mis-parsed judge is worse than a loud failure.
2. ``measure_agreement`` / ``agreement_rate`` / ``cohen_kappa`` compare judge
   labels against human labels. Agreement is reported next to every judge-based
   metric; an uncalibrated judge is not evidence.

Read first: ``docs/research/03-production-evals-ops.md`` §1.4 and the MT-Bench
paper it cites.
"""

from __future__ import annotations

from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from agentlab.evals.dataset import EvalCase

#: Judge criteria are scored on this inclusive integer scale.
SCORE_MIN = 0
SCORE_MAX = 2


@dataclass(frozen=True, slots=True)
class JudgeVerdict:
    """A parsed, validated judge result.

    Attributes:
        criterion_scores: criterion id -> integer score in ``[0, 2]``, exactly
            the ids declared in the case rubric.
        score: weighted normalized score in ``[0, 1]``:
            ``sum(score_i * weight_i) / (2 * sum(weight_i))``.
        passed: ``score >= case.pass_threshold``.
        reasons: criterion id -> one-line justification from the judge.
        raw: the raw JSON text, kept so judge drift is debuggable.
    """

    criterion_scores: Mapping[str, int]
    score: float
    passed: bool
    reasons: Mapping[str, str] = field(default_factory=dict)
    raw: str = ""


@runtime_checkable
class Judge(Protocol):
    """Anything that can score a case's output against its rubric."""

    def judge(self, case: EvalCase, output: str) -> JudgeVerdict: ...


@dataclass(frozen=True, slots=True)
class AgreementReport:
    """Judge-vs-human calibration result.

    Attributes:
        n: number of labelled items compared.
        agreement: raw agreement in ``[0, 1]`` (fraction of equal labels).
        kappa: Cohen's kappa in ``[-1, 1]`` -- agreement corrected for chance.
            Report both: 90% agreement on a 90/10 dataset can mean kappa ~0.0.
        disagreements: sorted ids where the two labellers differ, so the next
            calibration session has a concrete reading list.
    """

    n: int
    agreement: float
    kappa: float
    disagreements: tuple[str, ...]


class RubricJudge:
    """Scores one case output with a forced-JSON rubric judge.

    Args:
        provider: any object with ``complete(CompletionRequest) ->
            CompletionResponse``; use ``agentlab.testing.MockProvider`` in tests.
        model: model name to request; defaults to the provider's ``model``.
        temperature: sampling temperature. ``0.0`` is the default because a
            judge that changes its mind between runs cannot gate a release.
    """

    def __init__(self, provider: Any, *, model: str | None = None, temperature: float = 0.0) -> None:
        self.provider = provider
        self.model = model
        self.temperature = temperature

    def judge(self, case: EvalCase, output: str) -> JudgeVerdict:
        """Score ``output`` against ``case.rubric`` in exactly one model call.

        Contract:
            - the request sets ``response_format={"type": "json_object"}`` and a
              temperature of ``self.temperature``;
            - the rubric (ids, descriptions, weights) and the output under test
              are both present in the messages sent;
            - the response is one JSON object of the shape
              ``{"criteria": [{"id": str, "score": 0|1|2, "reason": str}], ...}``;
            - every case criterion id appears exactly once, no unknown ids;
            - malformed JSON, missing/extra/duplicate ids, and out-of-range
              scores raise ``SchemaValidationError`` (never a partial verdict);
            - a provider failure propagates as the provider's own error.

        The learner writes the prompt. The tests only pin the observable
        contract above, not the wording.
        """
        raise NotImplementedError("Week 7 lab: implement RubricJudge.judge")


def agreement_rate(human: Sequence[Hashable], judge: Sequence[Hashable]) -> float:
    """Fraction of positions where the two label sequences agree.

    Raises ``ValueError`` when the sequences have different lengths or are empty.
    """
    raise NotImplementedError("Week 7 lab: implement agreement_rate")


def cohen_kappa(human: Sequence[Hashable], judge: Sequence[Hashable]) -> float:
    """Cohen's kappa for two label sequences: chance-corrected agreement.

    ``kappa = (p_observed - p_expected) / (1 - p_expected)``. Returns ``1.0``
    when both labellers assign one category to everything and agree, ``0.0``
    when expected agreement is already ``1.0`` but they disagree.

    Raises ``ValueError`` when the sequences have different lengths or are empty.
    """
    raise NotImplementedError("Week 7 lab: implement cohen_kappa")


def measure_agreement(
    verdicts: Mapping[str, Hashable],
    labels: Mapping[str, Hashable],
) -> AgreementReport:
    """Compare judge verdicts with human labels keyed by the same case ids.

    Pairing by id (not by position) is the point: a label file edited
    independently of the eval run must never silently shift the comparison.

    Raises ``ValueError`` when the key sets differ (message names the missing
    and extra ids) or when there are no items.
    """
    raise NotImplementedError("Week 7 lab: implement measure_agreement")
