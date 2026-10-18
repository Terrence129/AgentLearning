"""Reference solution -- week 3: structured output and the typed decision family.

The invariant the whole file protects: **invalid output is never valid**. There
is exactly one construction site for a valid ``ExtractionResult``, and it is
guarded by ``model_validate``. Everything else -- parse failures, validation
errors, presentation-budget violations -- flows out as ``valid=False,
value=None`` plus the raw text and the errors needed to repair or diagnose it.

The repair loop is bounded and stateless: one bad attempt plus ``max_repairs``
repairs, each carrying the invalid output and the exact validation problems.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated, Any, Generic, Literal, TypeVar

from agentlab.errors import SchemaValidationError
from agentlab.providers.base import Provider
from agentlab.schemas.prompts import PromptTemplate
from agentlab.schemas.repair import RepairStats, build_repair_messages, format_validation_errors
from agentlab.tools.registry import schema_from_model
from agentlab.types import CompletionRequest, Message
from pydantic import BaseModel, Field, TypeAdapter, ValidationError, model_validator

T = TypeVar("T", bound=BaseModel)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)

STRUCTURED_OUTPUT_PROMPT = PromptTemplate(
    id="structured-output",
    version="1.0.0",
    template=(
        "You are a structured extraction engine. Reply with a single JSON object that "
        "validates against the {schema_name} schema below. No prose. No markdown fences."
    ),
)


def extract_json(raw: str) -> Any:
    """Decode the JSON value contained in raw model text."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("model output is empty")
    fence = _JSON_FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"model output is not valid JSON: {exc.msg}") from exc


def response_format_for(
    model_cls: type[BaseModel],
    *,
    name: str | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    """Build a provider ``response_format`` object for ``model_cls``."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name or model_cls.__name__,
            "schema": schema_from_model(model_cls),
            "strict": strict,
        },
    }


@dataclass(slots=True)
class ExtractionResult(Generic[T]):
    """The outcome of one extraction: valid+value or invalid+errors, never both."""

    valid: bool
    value: T | None
    raw: str
    errors: list[str] = field(default_factory=list)
    repairs: int = 0


class StructuredExtractor(Generic[T]):
    """Asks the provider for JSON, validates it, and repairs at most ``max_repairs`` times."""

    def __init__(
        self,
        provider: Provider,
        *,
        prompt: PromptTemplate | None = None,
        temperature: float | None = 0.0,
        stats: RepairStats | None = None,
    ) -> None:
        self.provider = provider
        self.prompt = prompt or STRUCTURED_OUTPUT_PROMPT
        self.temperature = temperature
        self.stats = stats or RepairStats()

    # -- public API --------------------------------------------------------

    def extract(
        self,
        messages: list[Message],
        model_cls: type[T],
        *,
        max_repairs: int = 1,
    ) -> ExtractionResult[T]:
        """Ask the model for JSON matching ``model_cls`` and validate it locally."""
        if max_repairs < 0:
            raise ValueError("max_repairs must be >= 0")

        schema = schema_from_model(model_cls)
        instruction = self.prompt.render(schema_name=model_cls.__name__)
        request_messages: list[Message] = [
            Message.system(f"{instruction}\n\nJSON Schema:\n{json.dumps(schema, indent=2, sort_keys=True)}"),
            *messages,
        ]
        response_format = response_format_for(model_cls)

        repairs_used = 0
        raw = ""
        errors: list[str] = []
        while True:
            request = CompletionRequest(
                messages=request_messages,
                model=self.provider.model,
                temperature=self.temperature,
                response_format=response_format,
            )
            response = self.provider.complete(request)
            raw = response.text
            value, errors = self._decode(raw, model_cls)

            if value is not None:
                self.stats.record(repairs=repairs_used, valid=True)
                return ExtractionResult(valid=True, value=value, raw=raw, errors=[], repairs=repairs_used)

            if repairs_used >= max_repairs:
                self.stats.record(repairs=repairs_used, valid=False)
                return ExtractionResult(valid=False, value=None, raw=raw, errors=errors, repairs=repairs_used)

            # The invalid assistant turn is part of the repair messages: the
            # model must see exactly what it is fixing, not a summary of it.
            request_messages = [
                *request_messages,
                *build_repair_messages(raw, errors, schema_name=model_cls.__name__),
            ]
            repairs_used += 1

    # -- validation --------------------------------------------------------

    @staticmethod
    def _decode(raw: str, model_cls: type[T]) -> tuple[T | None, list[str]]:
        """Return ``(value, [])`` or ``(None, errors)``. Never coerces output."""
        try:
            payload = extract_json(raw)
        except ValueError as exc:
            return None, [f"<root>: {exc}"]
        if not isinstance(payload, dict):
            return None, [f"<root>: expected a JSON object, got {type(payload).__name__}"]
        try:
            return model_cls.model_validate(payload), []
        except ValidationError as exc:
            return None, format_validation_errors(exc.errors())
        except SchemaValidationError as exc:
            # Domain validators (presentation budgets) are part of the contract
            # too, so they are repaired like any other schema failure.
            return None, list(exc.errors) or [str(exc)]


# ---------------------------------------------------------------------------
# Typed decision family
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PresentationBudget:
    """Structural limits on a decision message (SendOS: headline <= 12 words, <= 4 next moves)."""

    max_headline_words: int = 12
    max_meaning_sentences: int = 2
    max_next_moves: int = 4
    max_question_options: int = 3

    def violations(
        self,
        *,
        headline: str,
        meaning: str,
        next_moves: Sequence[str],
        question_options: Sequence[str] = (),
    ) -> list[str]:
        """Every violated budget as one human-readable string; empty means compliant."""
        problems: list[str] = []

        headline_words = len(headline.split())
        if headline_words > self.max_headline_words:
            problems.append(
                f"headline: {headline_words} words exceeds the {self.max_headline_words}-word limit"
            )

        sentences = [part for part in re.split(r"[.!?]+", meaning) if part.strip()]
        if len(sentences) > self.max_meaning_sentences:
            problems.append(
                f"meaning: {len(sentences)} sentences exceeds the {self.max_meaning_sentences}-sentence limit"
            )

        if len(next_moves) > self.max_next_moves:
            problems.append(
                f"next_moves: {len(next_moves)} moves exceeds the {self.max_next_moves}-move limit"
            )

        if len(question_options) > self.max_question_options:
            problems.append(
                f"question_options: {len(question_options)} options exceeds the "
                f"{self.max_question_options}-option limit"
            )

        return problems

    def enforce(
        self,
        *,
        headline: str,
        meaning: str,
        next_moves: Sequence[str],
        question_options: Sequence[str] = (),
    ) -> None:
        """Raise ``SchemaValidationError`` when any budget is exceeded."""
        problems = self.violations(
            headline=headline,
            meaning=meaning,
            next_moves=next_moves,
            question_options=question_options,
        )
        if problems:
            raise SchemaValidationError(
                "presentation budget violated: " + "; ".join(problems),
                errors=problems,
            )


DEFAULT_PRESENTATION_BUDGET = PresentationBudget()


class _BudgetedDecision(BaseModel):
    """Base class for every decision variant: budgets are enforced, not requested."""

    headline: str = Field(min_length=1, description="One-line summary, at most 12 words")
    meaning: str = Field(min_length=1, description="At most two sentences of justification")
    next_moves: list[str] = Field(default_factory=list, description="At most four suggested next actions")

    @model_validator(mode="after")
    def _enforce_presentation_budget(self) -> _BudgetedDecision:
        """Enforce ``DEFAULT_PRESENTATION_BUDGET`` for this instance."""
        DEFAULT_PRESENTATION_BUDGET.enforce(
            headline=self.headline,
            meaning=self.meaning,
            next_moves=self.next_moves,
            question_options=getattr(self, "options", ()),
        )
        return self


class ClarificationPrompt(_BudgetedDecision):
    """Ask the user ONE clarifying question; the only decision that stops the workflow."""

    kind: Literal["clarification"] = "clarification"
    question: str = Field(description="The single question to ask the user")
    options: list[str] = Field(default_factory=list, description="Suggested answers (at most three)")


class DirectAnswer(_BudgetedDecision):
    """Answer the user directly without invoking a capability."""

    kind: Literal["direct_answer"] = "direct_answer"
    answer: str = Field(description="The answer text")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Decision(_BudgetedDecision):
    """A state decision on a business object (proceed / hold / decline)."""

    kind: Literal["decision"] = "decision"
    decision: Literal["proceed", "hold", "decline"] = Field(description="The decision state")
    rationale: str = Field(description="Why this state, in evidence terms")


class Recommendation(_BudgetedDecision):
    """Recommend an action without executing it."""

    kind: Literal["recommendation"] = "recommendation"
    recommendation: str = Field(description="The recommended action")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ActionProposal(_BudgetedDecision):
    """Propose a concrete write action; a human must approve it before execution."""

    kind: Literal["action_proposal"] = "action_proposal"
    action: str = Field(description="The capability/tool name to invoke")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Validated arguments for the action")
    requires_approval: Literal[True] = True


DecisionUnion = Annotated[
    ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal,
    Field(discriminator="kind"),
]


def decision_schema() -> dict[str, Any]:
    """JSON Schema for ``DecisionUnion`` (discriminated by ``kind``)."""
    return TypeAdapter(DecisionUnion).json_schema()


def parse_decision(payload: dict[str, Any]) -> DecisionUnion:
    """Validate one payload as a member of ``DecisionUnion``."""
    return TypeAdapter(DecisionUnion).validate_python(payload)
