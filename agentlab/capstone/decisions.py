"""Typed decisions: the capstone's model-facing output contract (week 9).

Why this exists
---------------
The capstone never returns free text from a model. Every model call ends in one
**typed decision** from a closed union, so the API, the UI, the approval gate and
the audit log all speak the same vocabulary. This is week 3's structured-output
lab applied to the whole system, plus SendOS's *presentation budgets*: the UI
contract is enforced in code, not requested in a prompt.

Wire contract (the only place these names are defined)
------------------------------------------------------
Every decision is a JSON object::

    {"kind": "<kind>", "headline": "<short>", "next_moves": ["<move>", ...], ...}

====================  ===============================  =========================
kind                  required fields                  optional fields
====================  ===============================  =========================
clarification_prompt  headline, question               next_moves, options (0-3)
direct_answer         headline, answer                 next_moves
analysis_conclusion   headline, conclusion             next_moves
recommendation        headline, recommendation,        next_moves
                      rationale, confidence
action_proposal       headline, capability_id,         next_moves
                      arguments
approval_required     headline, proposal_id, reason    next_moves
execution_result      headline, status, reference      next_moves
limitation            headline, reason                 next_moves, missing (0-4)
====================  ===============================  =========================

Field types: ``headline``/``question``/``answer``/``conclusion``/
``recommendation``/``rationale``/``reason``/``capability_id``/``proposal_id``/
``reference`` are non-empty strings; ``next_moves``/``options``/``missing`` are
lists of non-empty strings; ``arguments`` is an object; ``confidence`` is a
number in ``[0, 1]``; ``status`` is one of ``"executed"``, ``"failed"``,
``"skipped"``.

Unknown kinds and unknown fields are rejected: this is a *closed* union, and
silently ignoring a typo is how a model-shaped contract rots.

Presentation budgets (part of what you implement)
-------------------------------------------------
- ``headline``: at most ``max_headline_words`` whitespace-separated words (12).
- ``next_moves``: at most ``max_next_moves`` entries (4).
- ``clarification_prompt.options``: at most ``max_question_options`` (3).
- "meaning": the single primary text field per kind (question, answer,
  conclusion, recommendation, reason) is at most ``max_meaning_sentences``
  sentences (2). ``rationale``, ``missing``, ``arguments`` and ``reference``
  are data, not meaning, and are not counted.

Hints
-----
- Split words with ``str.split()`` and count the parts; do not count characters.
- Count sentences by splitting on ``.``, ``!`` or ``?`` followed by whitespace or
  the end of the string; ignore empty segments.
- Collect *all* violations, then raise once, so the caller sees the full list.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from agentlab.errors import AgentError

#: The closed union. A payload whose ``kind`` is not in this tuple is invalid.
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


@dataclass(frozen=True, slots=True)
class PresentationBudgets:
    """UI limits every decision must respect.

    Budgets are deliberately small: a decision is a *rendered artifact*, not a
    reasoning transcript. Rationale lives in the decision, but the headline and
    next moves are what a busy approver actually reads.
    """

    max_headline_words: int = 12
    max_next_moves: int = 4
    max_meaning_sentences: int = 2
    max_question_options: int = 3


class PresentationBudgetError(AgentError):
    """A decision violates one or more presentation budgets.

    ``violations`` holds one human-readable string per broken rule, so callers
    (and the UI) can show exactly what to shorten instead of a generic error.
    """

    def __init__(self, message: str, *, violations: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.violations = list(violations)


@dataclass(frozen=True, slots=True)
class Decision:
    """The shape every decision shares.

    Variants add their required fields (see the module table). You decide how to
    model the variants; this base class exists so type annotations and the
    round-trip contract have something stable to name.
    """

    kind: str
    headline: str
    next_moves: tuple[str, ...]


def parse_decision(payload: Mapping[str, Any]) -> Decision:
    """Validate one wire payload and return the typed decision it describes.

    Contract
    --------
    - ``payload`` must be a mapping whose ``kind`` is one of ``DECISION_KINDS``.
    - The fields required for that kind must be present with the documented
      types; optional collections default to empty.
    - Fields not listed for that kind are rejected (closed union).
    - On any problem raise ``SchemaValidationError`` and put **every** problem
      found in ``.errors`` -- validate fully before raising, do not stop at the
      first missing field.

    Returns the concrete variant (e.g. a direct answer, a recommendation), not a
    plain ``Decision``.
    """
    raise NotImplementedError("Week 9 capstone: implement decisions.parse_decision")


def decision_to_wire(decision: Decision) -> dict[str, Any]:
    """Serialise a typed decision back to its wire payload.

    Contract: ``parse_decision(decision_to_wire(d))`` produces an equal decision.
    Return ``next_moves``/``options``/``missing`` as ``list`` (not ``tuple``) and
    omit empty optional collections. Key order is not significant.
    """
    raise NotImplementedError("Week 9 capstone: implement decisions.decision_to_wire")


def enforce_presentation_budgets(
    decision: Decision,
    budgets: PresentationBudgets | None = None,
) -> Decision:
    """Return ``decision`` unchanged, or raise ``PresentationBudgetError``.

    Contract
    --------
    - Check every rule documented in the module docstring against ``budgets``
      (defaults when omitted).
    - Collect *all* violations before raising; ``.violations`` must be non-empty
      and name the offending field (``headline``, ``next_moves``, ``options``,
      ``sentences``).
    - Valid decisions are returned as-is (same object), so this can sit in a
      pipeline without copying.
    """
    raise NotImplementedError("Week 9 capstone: implement decisions.enforce_presentation_budgets")
