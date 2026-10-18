"""Structured output: pydantic contract -> JSON Schema -> validate -> repair -- YOUR WEEK 3 BUILD.

Why this exists: a paragraph of prose is not a contract. Downstream code cannot
branch on it, evals cannot score it, and a slightly-wrong answer is
indistinguishable from a catastrophically-wrong one. Typed output fixes that --
but only if invalid output is *never* surfaced as valid. One silently-coerced
field is enough to make a decision system act on fabricated data.

The pipeline is deliberately explicit:

1. declare the contract as a pydantic model;
2. derive JSON Schema and ask the provider for it (``response_format``);
3. parse model text (tolerating markdown fences) and validate;
4. on failure, feed the validation errors back once (bounded; ``repair.py``);
5. report ``ExtractionResult(valid=..., value=None, raw=..., errors=..., repairs=...)``
   -- invalid means ``value is None``, mapped to a metric, never repaired-looking.

The second half of the file is the typed **Decision family**: a discriminated
union of the response shapes a decision system can return, with presentation
budgets enforced structurally (``PresentationBudget``) rather than asked for in
a prompt.

Read first: ``docs/research/01-agent-architecture-sota.md`` §3 (context
engineering), ``docs/research/02-frameworks-protocols.md`` §3 (provider
structured-output capabilities), and ``docs/research/05-sendos-concept-map.md``
§4.4 (schema-gated structured output; validate-after vs constrained decoding).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated, Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, model_validator

from agentlab.providers.base import Provider
from agentlab.schemas.prompts import PromptTemplate
from agentlab.schemas.repair import RepairStats
from agentlab.types import Message

T = TypeVar("T", bound=BaseModel)

#: Matches a fenced JSON block in model output: ``... ```json { ... } ``` ``.
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)

#: System instruction used by the extractor (rendered with the schema name).
STRUCTURED_OUTPUT_PROMPT = PromptTemplate(
    id="structured-output",
    version="1.0.0",
    template=(
        "You are a structured extraction engine. Reply with a single JSON object that "
        "validates against the {schema_name} schema below. No prose. No markdown fences."
    ),
)


def extract_json(raw: str) -> Any:
    """Decode the JSON value contained in raw model text.

    Policy:
    - empty/whitespace output raises ``ValueError("model output is empty")``;
    - if the text contains a fenced code block (`` ```json ... ``` `` or a bare
      fence), decode only the fenced content -- models add fences even when told
      not to;
    - invalid JSON raises ``ValueError("model output is not valid JSON: ...")``;
    - the decoded value is returned as-is; the extractor is responsible for
      requiring a JSON *object* before handing it to pydantic.
    """
    raise NotImplementedError("Week 3 lab: implement extract_json")


def response_format_for(
    model_cls: type[BaseModel],
    *,
    name: str | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    """Build a provider ``response_format`` object for ``model_cls``.

    Shape::

        {
            "type": "json_schema",
            "json_schema": {
                "name": <name or model_cls.__name__>,
                "schema": <pydantic JSON Schema, additionalProperties=False>,
                "strict": <strict>,
            },
        }

    Use the provided ``agentlab.tools.registry.schema_from_model`` so the schema
    is already provider-friendly. ``strict`` is forwarded as a hint only: even
    strict providers are validated locally, because the wire is not the contract.
    """
    raise NotImplementedError("Week 3 lab: implement response_format_for")


@dataclass(slots=True)
class ExtractionResult(Generic[T]):
    """The outcome of one extraction.

    ``valid`` and ``value`` are one contract: ``valid=True`` implies
    ``value is not None``; ``valid=False`` implies ``value is None``. ``raw`` is
    the last raw model text (useful in logs and repair diagnostics), ``errors``
    the final validation problems (empty on success), and ``repairs`` the number
    of repair attempts actually made (0 when the first response was valid).
    """

    valid: bool
    value: T | None
    raw: str
    errors: list[str] = field(default_factory=list)
    repairs: int = 0


class StructuredExtractor(Generic[T]):
    """Turns a provider into a typed extractor for one pydantic model per call.

    Construction is cheap; ``stats`` accumulates across calls so a lab artifact
    can report the schema failure rate instead of claiming "it works".
    """

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

    def extract(
        self,
        messages: list[Message],
        model_cls: type[T],
        *,
        max_repairs: int = 1,
    ) -> ExtractionResult[T]:
        """Ask the model for JSON matching ``model_cls`` and validate it locally.

        Request:
        - messages sent as ``[system instruction, *messages]`` where the system
          message is ``self.prompt`` rendered with the schema name, followed by
          the JSON Schema itself. The caller's ``messages`` list must not be
          mutated.
        - ``CompletionRequest(model=self.provider.model,
          temperature=self.temperature, response_format=response_format_for(model_cls))``.
        - one model call plus at most ``max_repairs`` repair calls.

        Validation:
        - use ``extract_json`` then ``model_cls.model_validate``; non-object JSON
          and pydantic ``ValidationError`` become human-readable error strings;
        - a presentation-budget violation raised as ``SchemaValidationError`` by
          the decision models is also an extraction error (repaired like any
          other schema failure);
        - on failure with repairs remaining, send
          ``[assistant(<invalid raw>), *build_repair_messages(...)]`` and retry;
        - ``ProviderError`` (or any provider failure) propagates: a flaky wire is
          not an invalid schema and must not be recorded as one.

        Result:
        - success -> ``ExtractionResult(valid=True, value=model, raw=<raw>,
          errors=[], repairs=<attempts used>)``;
        - exhaustion -> ``ExtractionResult(valid=False, value=None, raw=<last raw>,
          errors=<last errors>, repairs=<attempts used>)``. Invalid output is
          never returned as valid.
        - ``self.stats.record(repairs=..., valid=...)`` once per call.
        """
        raise NotImplementedError("Week 3 lab: implement StructuredExtractor.extract")


# ---------------------------------------------------------------------------
# Typed decision family (the SendOS DecisionInteraction miniature)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PresentationBudget:
    """Structural limits on a decision message (SendOS: headline <= 12 words, <= 4 next moves).

    Product constraints belong in code, not in a polite paragraph in the prompt:
    a validator produces a measurable failure instead of a silently long answer.
    """

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
        """Every violated budget as one human-readable string (empty list == compliant).

        Rules:
        - ``headline``: at most ``max_headline_words`` whitespace-separated words;
        - ``meaning``: at most ``max_meaning_sentences`` sentences, counting
          non-empty fragments split on ``.``, ``!`` or ``?``;
        - ``next_moves``: at most ``max_next_moves`` entries;
        - ``question_options``: at most ``max_question_options`` entries (only
          clarifications have options; pass nothing for other decisions).

        Each message names the offending field (``"headline: ..."``,
        ``"meaning: ..."``, ``"next_moves: ..."``, ``"question_options: ..."``)
        so both the repair loop and a human can act on it.
        """
        raise NotImplementedError("Week 3 lab: implement PresentationBudget.violations")

    def enforce(
        self,
        *,
        headline: str,
        meaning: str,
        next_moves: Sequence[str],
        question_options: Sequence[str] = (),
    ) -> None:
        """Raise ``agentlab.errors.SchemaValidationError`` when ``violations`` is non-empty.

        ``errors`` on the exception is the violations list; the exception message
        contains those violations too, so ``str(exc)`` is useful in a log.
        """
        raise NotImplementedError("Week 3 lab: implement PresentationBudget.enforce")


DEFAULT_PRESENTATION_BUDGET = PresentationBudget()


class _BudgetedDecision(BaseModel):
    """Base class for every decision variant: budgets are enforced, not requested.

    All variants share ``headline`` (the one-line answer), ``meaning`` (at most
    two sentences of justification) and ``next_moves`` (at most four suggested
    actions). Every subclass adds a required ``kind`` literal so one schema can
    describe the whole family (see ``DecisionUnion``).
    """

    headline: str = Field(min_length=1, description="One-line summary, at most 12 words")
    meaning: str = Field(min_length=1, description="At most two sentences of justification")
    next_moves: list[str] = Field(default_factory=list, description="At most four suggested next actions")

    @model_validator(mode="after")
    def _enforce_presentation_budget(self) -> _BudgetedDecision:
        """Enforce ``DEFAULT_PRESENTATION_BUDGET`` by raising ``SchemaValidationError``.

        The budget checks against ``headline``, ``meaning``, ``next_moves`` and --
        when the variant has an ``options`` field -- also the clarification
        options, so one validator covers the whole family.
        """
        raise NotImplementedError("Week 3 lab: enforce presentation budgets on decisions")


class ClarificationPrompt(_BudgetedDecision):
    """Ask the user ONE clarifying question; the only decision that stops the workflow.

    Implement these additional fields:

    - ``question: str`` -- the single question to ask (required);
    - ``options: list[str]`` -- suggested answers, at most
      ``PresentationBudget.max_question_options`` (default 3); may be empty.
    """

    kind: Literal["clarification"] = "clarification"


class DirectAnswer(_BudgetedDecision):
    """Answer the user directly without invoking a capability.

    Implement these additional fields:

    - ``answer: str`` -- the answer text (required);
    - ``confidence: float`` -- 0.0-1.0, default 1.0.
    """

    kind: Literal["direct_answer"] = "direct_answer"


class Decision(_BudgetedDecision):
    """A state decision on a business object (proceed / hold / decline).

    Implement these additional fields:

    - ``decision: Literal["proceed", "hold", "decline"]`` -- the decision state;
    - ``rationale: str`` -- why this state, in evidence terms (required).
    """

    kind: Literal["decision"] = "decision"


class Recommendation(_BudgetedDecision):
    """Recommend an action without executing it.

    Implement these additional fields:

    - ``recommendation: str`` -- the recommended action (required);
    - ``confidence: float`` -- 0.0-1.0, default 1.0.
    """

    kind: Literal["recommendation"] = "recommendation"


class ActionProposal(_BudgetedDecision):
    """Propose a concrete write action; a human must approve it before execution.

    Implement these additional fields:

    - ``action: str`` -- the capability/tool name to invoke (required);
    - ``parameters: dict[str, Any]`` -- validated tool arguments (default empty);
    - ``requires_approval: Literal[True]`` -- always ``True``. A model may never
      pre-approve its own proposal, so ``False`` must fail validation: authority
      is not something a completion can grant itself.
    """

    kind: Literal["action_proposal"] = "action_proposal"


#: One discriminated union for the whole family; the ``kind`` tag is what makes
#: a single JSON Schema describe five different payload shapes safely.
DecisionUnion = Annotated[
    ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal,
    Field(discriminator="kind"),
]


def decision_schema() -> dict[str, Any]:
    """JSON Schema for ``DecisionUnion`` (discriminated by ``kind``).

    Build it with ``pydantic.TypeAdapter(DecisionUnion).json_schema()``. The
    result must list all five variants and identify ``kind`` as the discriminator,
    which is what you pass to a provider that supports structured outputs.
    """
    raise NotImplementedError("Week 3 lab: implement decision_schema")


def parse_decision(payload: dict[str, Any]) -> DecisionUnion:
    """Validate one payload as a member of ``DecisionUnion``.

    Returns the concrete model instance selected by ``kind``. Raises
    ``pydantic.ValidationError`` for an unknown/missing ``kind``, missing
    required fields, or a presentation-budget violation that surfaces as one.
    Never returns a partially-populated or guessed variant.
    """
    raise NotImplementedError("Week 3 lab: implement parse_decision")
