"""Typed model output (week 3).

Public surface:

- ``structured.StructuredExtractor`` -- schema-constrained extraction with a
  bounded repair loop and a failure metric
- ``structured.DecisionUnion`` / ``parse_decision`` -- the typed decision family
  with structural presentation budgets
- ``prompts.PromptTemplate`` / ``PromptRegistry`` -- prompts as versioned assets
- ``repair.*`` -- validation-error formatting, repair messages, failure stats

The one invariant that matters: invalid model output is never surfaced as valid.
"""

from agentlab.schemas.prompts import PromptRegistry, PromptRenderError, PromptTemplate
from agentlab.schemas.repair import (
    REPAIR_PROMPT,
    RepairStats,
    build_repair_messages,
    format_validation_errors,
)
from agentlab.schemas.structured import (
    DEFAULT_PRESENTATION_BUDGET,
    STRUCTURED_OUTPUT_PROMPT,
    ActionProposal,
    ClarificationPrompt,
    Decision,
    DecisionUnion,
    DirectAnswer,
    ExtractionResult,
    PresentationBudget,
    Recommendation,
    StructuredExtractor,
    decision_schema,
    extract_json,
    parse_decision,
    response_format_for,
)

__all__ = [
    "DEFAULT_PRESENTATION_BUDGET",
    "REPAIR_PROMPT",
    "STRUCTURED_OUTPUT_PROMPT",
    "ActionProposal",
    "ClarificationPrompt",
    "Decision",
    "DecisionUnion",
    "DirectAnswer",
    "ExtractionResult",
    "PresentationBudget",
    "PromptRegistry",
    "PromptRenderError",
    "PromptTemplate",
    "Recommendation",
    "RepairStats",
    "StructuredExtractor",
    "build_repair_messages",
    "decision_schema",
    "extract_json",
    "format_validation_errors",
    "parse_decision",
    "response_format_for",
]
