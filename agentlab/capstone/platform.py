"""The capstone platform: Mini-SendOS composition over weeks 1-8 (week 9).

This module is the *composition root*. Every mechanism you built earlier becomes
one seam of one small, governed system:

==================  =========================================================
Seam                Built in      What the capstone reuses
==================  =========================================================
Provider            week 1        ``agentlab.providers.base.Provider``; the demo
                                  passes ``agentlab.testing.MockProvider``
Tool registry       week 2        ``agentlab.tools.registry.ToolRegistry``
Typed decisions     week 3/9      ``agentlab.capstone.decisions``
Context budget      week 4        your ``agentlab.context`` policy, if you wired it
Orchestration       week 6        "smallest sufficient shape": one direct
                                  capability is a workflow, not a squad
Approval gate       week 6        proposal persisted *before* approval, bound to
                                  the action hash and an authority snapshot
Evals + audit       week 7        append-only audit rows you can score later
Guardrails          week 8        deny-by-default: a capability the catalogue did
                                  not grant is not invokable
==================  =========================================================

The lifecycle this module must implement::

    submit_goal -> Decision
        (kind == "action_proposal")
    propose_action -> ActionProposal          # persisted BEFORE approval
    approve -> ApprovalDecision               # proposer != approver, expiry, binding
    execute -> ExecutionReceipt               # at-most-once, audited
    audit_trail -> tuple[AuditRow, ...]       # append-only, monotonically sequenced

Each stub below names the invariant it must preserve and points at the week whose
lab implements the mechanism. Search the repo for the matching pattern before
inventing your own; the capstone is a composition exercise, not a ninth mechanism.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from agentlab.capstone.catalogue import CapabilityCatalogue
from agentlab.capstone.decisions import Decision
from agentlab.errors import AgentError


@dataclass(frozen=True, slots=True)
class GoalRequest:
    """One user goal, already authenticated by the caller (tenant + actor)."""

    goal: str
    tenant_id: str
    actor_id: str


@dataclass(frozen=True, slots=True)
class ActionProposal:
    """A proposed state-changing action, persisted before any human sees it.

    ``action_hash`` binds the approval to *this* capability and *these*
    arguments: an approval for a different hash must never execute.
    ``expires_at`` prevents approvals outliving the context they were granted in.
    """

    proposal_id: str
    capability_id: str
    arguments: dict[str, Any]
    action_hash: str
    tenant_id: str
    actor_id: str
    created_at: datetime
    expires_at: datetime
    status: str = "pending"


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    """A human's decision about one proposal."""

    approval_id: str
    proposal_id: str
    approver_id: str
    approved: bool
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class ExecutionReceipt:
    """What actually happened, with the audit sequence it was recorded at."""

    proposal_id: str
    execution_id: str
    capability_id: str
    status: Literal["executed", "failed", "skipped"]
    detail: str
    audit_seq: int


@dataclass(frozen=True, slots=True)
class AuditRow:
    """One append-only audit row. Never update or delete these."""

    seq: int
    ts: datetime
    event: str
    tenant_id: str
    actor_id: str
    payload: dict[str, Any] = field(default_factory=dict)


class CapstoneError(AgentError):
    """Base class for capstone lifecycle errors."""


class ApprovalError(CapstoneError):
    """The approval is missing, expired, bound to another action, or self-approved."""


class ExecutionError(CapstoneError):
    """The action was already executed, or is not executable in its current state."""


def action_digest(capability_id: str, arguments: Mapping[str, Any]) -> str:
    """Return the stable action hash used to bind an approval to an action.

    Contract: same capability + same *semantic* arguments => same digest; any
    difference in an argument value, capability id, or a different ordering of
    the same arguments => same digest for the ordering case. Hint: sort keys and
    serialise deterministically (``json.dumps(..., sort_keys=True)``), then hash.
    """
    raise NotImplementedError("Week 9 capstone: implement platform.action_digest")


class CapstonePlatform:
    """One governed platform instance. Construct it once per process/tenant set."""

    def __init__(
        self,
        *,
        provider: Any,
        tools: Any,
        catalogue: CapabilityCatalogue,
        tracer: Any | None = None,
        now: Callable[[], datetime] | None = None,
        proposal_ttl: timedelta = timedelta(minutes=15),
    ) -> None:
        """Wire the seams. Concrete implementation is given; use it, don't redo it.

        The in-memory collections below are the persistence layer for the course.
        In a real system they are a database with the same invariants (SendOS
        persists the proposal before approval and refuses replays).
        """
        self.provider = provider
        self.tools = tools
        self.catalogue = catalogue
        self.tracer = tracer
        self._now = now or (lambda: datetime.now(UTC))
        self.proposal_ttl = proposal_ttl
        self._proposals: dict[str, ActionProposal] = {}
        self._approvals: dict[str, ApprovalDecision] = {}
        self._executions: dict[str, ExecutionReceipt] = {}
        self._audit: list[AuditRow] = []

    # -- lifecycle ---------------------------------------------------------
    def submit_goal(self, request: GoalRequest) -> Decision:
        """Turn an authenticated goal into one typed decision.

        Contract
        --------
        - Return a ``Decision`` from ``agentlab.capstone.decisions`` that passes
          ``enforce_presentation_budgets``.
        - What you can honestly determine decides the kind: missing information
          -> ``clarification_prompt``; unsupported request -> ``limitation``;
          a proposed state change -> ``action_proposal``; otherwise an answer.
        - You may use the week-2 loop around ``self.provider``; the demo scripts
          a mock provider for the capstone goal, so do not require live network.
        - Never let a model response bypass the catalogue: a proposal for a
          capability this tenant does not have must become an ``action_proposal``
          that ``propose_action`` rejects, or a ``limitation``.
        """
        raise NotImplementedError("Week 9 capstone: implement CapstonePlatform.submit_goal")

    def propose_action(
        self,
        request: GoalRequest,
        capability_id: str,
        arguments: Mapping[str, Any],
    ) -> ActionProposal:
        """Validate and persist a proposal before any human sees it.

        Contract
        --------
        - Resolve the capability through ``self.catalogue`` for
          ``request.tenant_id``; unavailable => raise or refuse (the catalogue's
          ``CapabilityNotAvailable`` is the fail-closed default).
        - Reject non-write capabilities here: a read does not need a proposal.
        - Persist the proposal *before* returning it, with
          ``action_hash = action_digest(capability_id, arguments)`` and
          ``expires_at = now + self.proposal_ttl``.
        - Append an audit row (``event="proposal_created"``) and return the
          persisted object.
        """
        raise NotImplementedError("Week 9 capstone: implement CapstonePlatform.propose_action")

    def approve(
        self,
        proposal_id: str,
        *,
        approver_id: str,
        approved: bool,
    ) -> ApprovalDecision:
        """Record a human decision, enforcing separation of duties and binding.

        Contract
        --------
        - Unknown proposal => ``ApprovalError``; expired proposal => ``ApprovalError``.
        - ``approver_id == proposal.actor_id`` => ``ApprovalError`` (maker-checker).
        - Persist the decision and append an audit row
          (``approval_granted`` or ``approval_denied``).
        - An approval is bound to ``proposal_id`` + ``proposal.action_hash`` +
          the approver; nothing else may execute it.
        """
        raise NotImplementedError("Week 9 capstone: implement CapstonePlatform.approve")

    def execute(self, proposal_id: str, *, approval_id: str) -> ExecutionReceipt:
        """Execute exactly once, after re-checking authority and binding.

        Contract
        --------
        - Missing proposal/approval, rejected approval, expiry, or a mismatch of
          ``action_hash`` => ``ExecutionError``; nothing executes.
        - A second execute for the same proposal => ``ExecutionError`` (at-most-once).
        - Execute through ``self.tools`` / the capability's declared action and
          record the audit rows ``execution_started`` and ``execution_finished``.
        - Return an ``ExecutionReceipt`` carrying ``audit_seq`` of the final row.
        """
        raise NotImplementedError("Week 9 capstone: implement CapstonePlatform.execute")

    def audit_trail(self) -> tuple[AuditRow, ...]:
        """Return the append-only audit rows in ``seq`` order.

        Contract: rows are never mutated or removed; every lifecycle method above
        appends at least one row; ``seq`` is strictly increasing from 1.
        """
        raise NotImplementedError("Week 9 capstone: implement CapstonePlatform.audit_trail")
