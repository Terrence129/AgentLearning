"""Reference solution -- week 3: validation-error repair and failure metrics.

The repair message is deliberately concrete: the invalid output, the exact
field-level problems, and one instruction. That is the difference between a
retry and a repair -- and ``RepairStats`` is what makes "it usually works" a
number you can put in a report.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentlab.schemas.prompts import PromptTemplate
from agentlab.types import Message

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
    """Turn pydantic ``ValidationError.errors()`` entries into one-line strings."""
    formatted: list[str] = []
    for entry in errors:
        location = ".".join(str(part) for part in entry.get("loc", ())) or "<root>"
        message = entry.get("msg", "invalid value")
        formatted.append(f"{location}: {message}")
    return formatted


def build_repair_messages(
    raw: str,
    errors: list[str],
    *,
    schema_name: str = "the required",
) -> list[Message]:
    """Build the invalid-output turn plus the repair instruction."""
    errors_text = "\n".join(f"- {error}" for error in errors)
    instruction = REPAIR_PROMPT.render(schema_name=schema_name, errors=errors_text)
    return [Message.assistant(raw), Message.user(instruction)]


@dataclass(slots=True)
class RepairStats:
    """Counters that turn "structured output works" into a number."""

    total: int = 0
    clean: int = 0
    repaired: int = 0
    failed: int = 0

    def record(self, *, repairs: int, valid: bool) -> None:
        """Update the counters from one extraction outcome."""
        self.total += 1
        if not valid:
            self.failed += 1
        elif repairs > 0:
            self.repaired += 1
        else:
            self.clean += 1

    @property
    def repair_rate(self) -> float:
        """Fraction of extractions that needed a repair."""
        return self.repaired / self.total if self.total else 0.0

    @property
    def failure_rate(self) -> float:
        """Fraction of extractions that never became valid."""
        return self.failed / self.total if self.total else 0.0
