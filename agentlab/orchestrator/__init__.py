"""Planning and multi-agent orchestration (week 6).

The theme is *smallest sufficient shape*: most tasks need a workflow, not a
swarm. The lab measures when extra agents help and when they only add latency --
and puts a bound, at-most-once human approval gate in front of every write.

Modules:
    plan.py          typed plans, validation, deterministic ordering, replanning
    specialist.py    isolated sub-agents with narrow tools and typed hand-offs
    orchestrator.py  topology-driven shape selection and plan execution
    approval.py      persisted proposals, bound approvals, at-most-once execution
"""

from __future__ import annotations

from agentlab.orchestrator.approval import (
    ActionHashMismatch,
    ActionProposal,
    ApprovalBinding,
    ApprovalCheckpoint,
    ApprovalError,
    ApprovalExecutionFailed,
    ApprovalExpired,
    ApprovalNotFound,
    ApprovalRecord,
    ApprovalReplayRejected,
    ApprovalState,
    ApprovedAction,
    Authority,
    AuthorityNarrowed,
    ExecutionResult,
    InMemoryProposalStore,
    InsufficientAuthority,
    InvalidApprovalTransition,
    ProposalNotPersisted,
    ProposalStore,
    ProposerCannotApprove,
    TenantMismatch,
    action_hash,
)
from agentlab.orchestrator.orchestrator import (
    CapabilityExecutor,
    ExecutionShape,
    OrchestrationResult,
    Orchestrator,
    ShapeSelection,
    WorkstreamResult,
    classify_shape,
    component_ids,
    select_shape,
)
from agentlab.orchestrator.plan import (
    NodeKind,
    Plan,
    PlanError,
    ReplanDecision,
    Workstream,
    ready_workstreams,
    replan_after_failure,
    topo_order,
    validate_plan,
)
from agentlab.orchestrator.specialist import (
    ContextEnvelope,
    HandoffArtifact,
    Specialist,
    SpecialistError,
    SpecialistSpec,
)

__all__ = [
    "ActionHashMismatch",
    "ActionProposal",
    "ApprovalBinding",
    "ApprovalCheckpoint",
    "ApprovalError",
    "ApprovalExecutionFailed",
    "ApprovalExpired",
    "ApprovalNotFound",
    "ApprovalRecord",
    "ApprovalReplayRejected",
    "ApprovalState",
    "ApprovedAction",
    "Authority",
    "AuthorityNarrowed",
    "CapabilityExecutor",
    "ContextEnvelope",
    "ExecutionResult",
    "ExecutionShape",
    "HandoffArtifact",
    "InMemoryProposalStore",
    "InsufficientAuthority",
    "InvalidApprovalTransition",
    "NodeKind",
    "OrchestrationResult",
    "Orchestrator",
    "Plan",
    "PlanError",
    "ProposalNotPersisted",
    "ProposalStore",
    "ProposerCannotApprove",
    "ReplanDecision",
    "ShapeSelection",
    "Specialist",
    "SpecialistError",
    "SpecialistSpec",
    "TenantMismatch",
    "Workstream",
    "WorkstreamResult",
    "action_hash",
    "classify_shape",
    "component_ids",
    "ready_workstreams",
    "replan_after_failure",
    "select_shape",
    "topo_order",
    "validate_plan",
]
