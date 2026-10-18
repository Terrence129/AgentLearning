"""Validation-error repair: feed the failure back to the model once -- YOUR WEEK 3 BUILD.

Why this exists: schema-constrained decoding is not universal, and even strict
providers occasionally return output that parses but violates a semantic rule (a
presentation budget, a cross-field invariant). Retrying blindly wastes money;
feeding the *validation errors* back gives the model exactly what it needs to
fix its own mistake. Bounded attempts are the point: unbounded repair is a cost
bug, and hiding the failure rate is an engineering bug.

Read first: ``docs/research/01-agent-architecture-sota.md`` §2 (reflection works
when critique is grounded -- compiler errors, schema violations) and the week 3
lab brief.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentlab.schemas.prompts import PromptTemplate
from agentlab.types import Message

#: The repair instruction sent back after a validation failure.
REPAIR_PROMPT = PromptTemplate(
    id="structured-repair",
    version="1.0.0",
    template=(
        "Your previous reply could not be validated against the {schema_name} schema.\n"
        "Problems:\n{errors}\n\n"
        "Return ONLY a corrected JSON object that fixes every problem. "
        "No prose, no markdown fences."
    ),
)


def format_validation_errors(errors: list[dict[str, Any]]) -> list[str]:
    """Turn pydantic ``ValidationError.errors()`` entries into one-line strings.

    Each entry becomes ``"<location>: <message>"`` where the location is the
    ``loc`` tuple joined with ``"."`` (``("headline",) -> "headline"``,
    ``("items", 0) -> "items.0"``). An empty ``loc`` maps to ``"<root>"``. Order
    is preserved; the result must be directly renderable into the repair prompt.
    """
    raise NotImplementedError("Week 3 lab: implement format_validation_errors")


def build_repair_messages(
    raw: str,
    errors: list[str],
    *,
    schema_name: str = "the required",
) -> list[Message]:
    """Build the two messages that ask the model for one repair.

    Returns ``[Message.assistant(raw), Message.user(<rendered instruction>)]``:

    - ``raw`` is the invalid model output, kept as the assistant turn so the
      model can see *what* it must fix (it is not re-invented from scratch);
    - the user turn is ``REPAIR_PROMPT`` rendered with ``schema_name`` and with
      ``errors`` as a newline-separated bullet list. Every error string appears
      verbatim in the message.
    """
    raise NotImplementedError("Week 3 lab: implement build_repair_messages")


@dataclass(slots=True)
class RepairStats:
    """Counters that turn "structured output works" into a number.

    Call ``record(repairs=<n>, valid=<bool>)`` exactly once per extraction:

    - valid on the first attempt (``repairs == 0``) -> ``clean``
    - valid after one or more repairs -> ``repaired``
    - never valid -> ``failed``

    ``total`` is the number of extractions recorded.
    """

    total: int = 0
    clean: int = 0
    repaired: int = 0
    failed: int = 0

    def record(self, *, repairs: int, valid: bool) -> None:
        """Update the counters from one extraction outcome."""
        raise NotImplementedError("Week 3 lab: implement RepairStats.record")

    @property
    def repair_rate(self) -> float:
        """Fraction of extractions that needed a repair (0.0 when nothing recorded)."""
        raise NotImplementedError("Week 3 lab: implement RepairStats.repair_rate")

    @property
    def failure_rate(self) -> float:
        """Fraction of extractions that never became valid (0.0 when nothing recorded)."""
        raise NotImplementedError("Week 3 lab: implement RepairStats.failure_rate")
