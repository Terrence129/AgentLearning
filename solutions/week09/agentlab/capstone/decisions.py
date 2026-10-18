"""Reference solution for ``agentlab.capstone.decisions`` (week 9).

Copy into place with::

    Copy-Item solutions/week09/* . -Recurse -Force

Read this only after your own tests pass, or when you are stuck on a contract
question -- the point of the lab is the contract, not this file.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from agentlab.errors import AgentError, SchemaValidationError

DECISION_KINDS: tuple[str, ...] = (
    "clarification_prompt",
    "direct_answer",
    "analysis_conclusion",
    "recommendation",
    "action_proposal",
    "approval_required",
    "execution_result",
    "limitation",
)

STATUSES: tuple[str, ...] = ("executed", "failed", "skipped")

#: Required non-empty string fields per kind (``headline`` handled separately).
_REQUIRED_STRINGS: dict[str, tuple[str, ...]] = {
    "clarification_prompt": ("question",),
    "direct_answer": ("answer",),
    "analysis_conclusion": ("conclusion",),
    "recommendation": ("recommendation", "rationale"),
    "action_proposal": ("capability_id",),
    "approval_required": ("proposal_id", "reason"),
    "execution_result": ("reference",),
    "limitation": ("reason",),
}

#: Optional list-of-strings fields per kind (default: empty tuple).
_OPTIONAL_LISTS: dict[str, tuple[str, ...]] = {
    "clarification_prompt": ("options",),
    "limitation": ("missing",),
}

#: The single "meaning" text field whose sentence count is budgeted.
_PRIMARY_TEXT: dict[str, str] = {
    "clarification_prompt": "question",
    "direct_answer": "answer",
    "analysis_conclusion": "conclusion",
    "recommendation": "recommendation",
    "approval_required": "reason",
    "limitation": "reason",
}


@dataclass(frozen=True, slots=True)
class PresentationBudgets:
    """UI limits every decision must respect."""

    max_headline_words: int = 12
    max_next_moves: int = 4
    max_meaning_sentences: int = 2
    max_question_options: int = 3


class PresentationBudgetError(AgentError):
    """A decision violates one or more presentation budgets."""

    def __init__(self, message: str, *, violations: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.violations = list(violations)


@dataclass(frozen=True, slots=True)
class Decision:
    """The shape every decision shares."""

    kind: str
    headline: str
    next_moves: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClarificationPrompt(Decision):
    question: str
    options: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DirectAnswer(Decision):
    answer: str


@dataclass(frozen=True, slots=True)
class AnalysisConclusion(Decision):
    conclusion: str


@dataclass(frozen=True, slots=True)
class Recommendation(Decision):
    recommendation: str
    rationale: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ActionProposalDecision(Decision):
    capability_id: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ApprovalRequired(Decision):
    proposal_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class ExecutionResult(Decision):
    status: str
    reference: str


@dataclass(frozen=True, slots=True)
class Limitation(Decision):
    reason: str
    missing: tuple[str, ...] = ()


def _is_non_empty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, (list, tuple)):
        return None
    if any(not _is_non_empty_str(item) for item in value):
        return None
    return [str(item) for item in value]


def _validate(payload: Mapping[str, Any]) -> list[str]:
    """Return every problem with ``payload``; empty list means valid."""
    kind = payload.get("kind")
    if not isinstance(kind, str) or kind not in DECISION_KINDS:
        return [f"kind must be one of: {', '.join(DECISION_KINDS)}"]

    errors: list[str] = []
    allowed = {"kind", "headline", "next_moves"}
    allowed.update(_REQUIRED_STRINGS[kind])
    allowed.update(_OPTIONAL_LISTS.get(kind, ()))
    if kind == "recommendation":
        allowed.add("confidence")
    if kind == "action_proposal":
        allowed.add("arguments")
    if kind == "execution_result":
        allowed.add("status")

    unknown = sorted(set(payload) - allowed)
    if unknown:
        errors.append(f"unknown field(s) for {kind}: {', '.join(unknown)}")

    if not _is_non_empty_str(payload.get("headline")):
        errors.append("headline must be a non-empty string")

    for field in _REQUIRED_STRINGS[kind]:
        if not _is_non_empty_str(payload.get(field)):
            errors.append(f"{field} must be a non-empty string")

    if "next_moves" in payload and _string_list(payload["next_moves"]) is None:
        errors.append("next_moves must be a list of non-empty strings")

    for field in _OPTIONAL_LISTS.get(kind, ()):
        if field not in payload:
            continue
        if _string_list(payload[field]) is None:
            errors.append(f"{field} must be a list of non-empty strings")
        elif not payload[field]:
            errors.append(f"{field} must not be empty when present")

    if kind == "recommendation":
        confidence = payload.get("confidence")
        is_number = isinstance(confidence, (int, float)) and not isinstance(confidence, bool)
        if not is_number or not 0.0 <= float(confidence) <= 1.0:  # type: ignore[arg-type]
            errors.append("confidence must be a number between 0 and 1")

    if kind == "action_proposal":
        arguments = payload.get("arguments")
        if not isinstance(arguments, Mapping):
            errors.append("arguments must be an object")

    if kind == "execution_result":
        status = payload.get("status")
        if status not in STATUSES:
            errors.append(f"status must be one of: {', '.join(STATUSES)}")

    return errors


def parse_decision(payload: Mapping[str, Any]) -> Decision:
    """Validate one wire payload and return the typed decision it describes."""
    if not isinstance(payload, Mapping):
        raise SchemaValidationError("decision payload is invalid", errors=["payload must be a JSON object"])

    errors = _validate(payload)
    if errors:
        raise SchemaValidationError("decision payload is invalid", errors=errors)

    kind = str(payload["kind"])
    common: dict[str, Any] = {
        "kind": kind,
        "headline": str(payload["headline"]),
        "next_moves": tuple(payload.get("next_moves") or ()),
    }

    if kind == "clarification_prompt":
        return ClarificationPrompt(
            **common,
            question=str(payload["question"]),
            options=tuple(payload.get("options") or ()),
        )
    if kind == "direct_answer":
        return DirectAnswer(**common, answer=str(payload["answer"]))
    if kind == "analysis_conclusion":
        return AnalysisConclusion(**common, conclusion=str(payload["conclusion"]))
    if kind == "recommendation":
        return Recommendation(
            **common,
            recommendation=str(payload["recommendation"]),
            rationale=str(payload["rationale"]),
            confidence=float(payload["confidence"]),
        )
    if kind == "action_proposal":
        return ActionProposalDecision(
            **common,
            capability_id=str(payload["capability_id"]),
            arguments=dict(payload["arguments"]),
        )
    if kind == "approval_required":
        return ApprovalRequired(
            **common,
            proposal_id=str(payload["proposal_id"]),
            reason=str(payload["reason"]),
        )
    if kind == "execution_result":
        return ExecutionResult(
            **common,
            status=str(payload["status"]),
            reference=str(payload["reference"]),
        )
    return Limitation(
        **common,
        reason=str(payload["reason"]),
        missing=tuple(payload.get("missing") or ()),
    )


def decision_to_wire(decision: Decision) -> dict[str, Any]:
    """Serialise a typed decision back to its wire payload."""
    wire: dict[str, Any] = {
        "kind": decision.kind,
        "headline": decision.headline,
        "next_moves": list(decision.next_moves),
    }
    if isinstance(decision, ClarificationPrompt):
        wire["question"] = decision.question
        if decision.options:
            wire["options"] = list(decision.options)
    elif isinstance(decision, DirectAnswer):
        wire["answer"] = decision.answer
    elif isinstance(decision, AnalysisConclusion):
        wire["conclusion"] = decision.conclusion
    elif isinstance(decision, Recommendation):
        wire["recommendation"] = decision.recommendation
        wire["rationale"] = decision.rationale
        wire["confidence"] = decision.confidence
    elif isinstance(decision, ActionProposalDecision):
        wire["capability_id"] = decision.capability_id
        wire["arguments"] = dict(decision.arguments)
    elif isinstance(decision, ApprovalRequired):
        wire["proposal_id"] = decision.proposal_id
        wire["reason"] = decision.reason
    elif isinstance(decision, ExecutionResult):
        wire["status"] = decision.status
        wire["reference"] = decision.reference
    elif isinstance(decision, Limitation):
        wire["reason"] = decision.reason
        if decision.missing:
            wire["missing"] = list(decision.missing)
    return wire


def _word_count(text: str) -> int:
    return len(text.split())


def _sentence_count(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([part for part in parts if part.strip()])


def enforce_presentation_budgets(
    decision: Decision,
    budgets: PresentationBudgets | None = None,
) -> Decision:
    """Return ``decision`` unchanged, or raise ``PresentationBudgetError``."""
    limits = budgets or PresentationBudgets()
    violations: list[str] = []

    words = _word_count(decision.headline)
    if words > limits.max_headline_words:
        violations.append(f"headline has {words} words (max {limits.max_headline_words})")

    moves = len(decision.next_moves)
    if moves > limits.max_next_moves:
        violations.append(f"next_moves has {moves} entries (max {limits.max_next_moves})")

    if isinstance(decision, ClarificationPrompt):
        options = len(decision.options)
        if options > limits.max_question_options:
            violations.append(f"options has {options} entries (max {limits.max_question_options})")

    meaning_field = _PRIMARY_TEXT.get(decision.kind)
    if meaning_field is not None:
        text = str(getattr(decision, meaning_field, "") or "")
        sentences = _sentence_count(text)
        if sentences > limits.max_meaning_sentences:
            violations.append(
                f"{meaning_field} has {sentences} sentences (max {limits.max_meaning_sentences})"
            )

    if violations:
        raise PresentationBudgetError(
            "decision violates presentation budgets: " + "; ".join(violations),
            violations=violations,
        )
    return decision
