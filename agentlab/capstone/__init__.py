"""Week 9 capstone: Mini-SendOS.

Three modules, built in this order:

- ``decisions`` -- the typed decision union and its presentation budgets.
- ``catalogue`` -- governed capability declarations (published-wins, tenant
  scope, read/write + approval rules, no cross-tenant oracle).
- ``platform``  -- the composition root: goal -> decision -> proposal ->
  approval -> execution -> audit, reusing weeks 1-8.

Start with ``python scripts/demo_capstone.py``: it prints what is missing and
runs the full offline demo once the seams are implemented.
"""

from agentlab.capstone.catalogue import (
    RISK_LEVELS,
    CapabilityCatalogue,
    CapabilityDefinition,
    CapabilityNotAvailable,
    CatalogueError,
    RiskLevel,
)
from agentlab.capstone.decisions import (
    DECISION_KINDS,
    Decision,
    PresentationBudgetError,
    PresentationBudgets,
    decision_to_wire,
    enforce_presentation_budgets,
    parse_decision,
)
from agentlab.capstone.platform import (
    ActionProposal,
    ApprovalDecision,
    ApprovalError,
    AuditRow,
    CapstoneError,
    CapstonePlatform,
    ExecutionError,
    ExecutionReceipt,
    GoalRequest,
    action_digest,
)

__all__ = [
    "DECISION_KINDS",
    "RISK_LEVELS",
    "ActionProposal",
    "ApprovalDecision",
    "ApprovalError",
    "AuditRow",
    "CapabilityCatalogue",
    "CapabilityDefinition",
    "CapabilityNotAvailable",
    "CapstoneError",
    "CapstonePlatform",
    "CatalogueError",
    "Decision",
    "ExecutionError",
    "ExecutionReceipt",
    "GoalRequest",
    "PresentationBudgetError",
    "PresentationBudgets",
    "RiskLevel",
    "action_digest",
    "decision_to_wire",
    "enforce_presentation_budgets",
    "parse_decision",
]
