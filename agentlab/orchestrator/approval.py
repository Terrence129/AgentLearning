"""Approval checkpoints: bound, human-in-the-loop, at-most-once writes (week 6).

Why this module exists
----------------------
"AI recommends, a human approves, the backend executes" is the product promise
of every governed agent platform -- and the place where bugs are security bugs.
The dangerous version is a boolean: the model writes ``approved: true`` (or edits
the pending proposal after approval, or the same approval is replayed on retry,
or the approver's authority is revoked before execution). The safe version binds
the decision to what exactly was approved, for whom, with what authority, until
when -- and executes it at most once.
SendOS's ``ApprovalInteraction``/``ApprovalCheckpoint`` implements this shape and
keeps property tests for it (docs/research/05-sendos-concept-map.md §4.1). This
module is the miniature; the invariants below are the product.

What breaks without it
----------------------
- A model-settable "approved" flag: no human ever sees the action.
- Post-approval edits: the human approves "refund $50", the executor runs
  "refund $50,000", because the proposal was mutable after approval.
- Double execution: the retry after a timeout issues the refund twice. Money
  does not have idempotent apologies.
- Approvals outliving authority: the approver's entitlement is narrowed between
  approval and execution, but the approval record still says yes.
- Expired approvals: a queued approval executes a week later.
- Self-approval: the proposer approves its own proposal, which is not a control.

Invariants you must implement and the tests will check:
    1. **Persisted before approval** -- ``propose`` writes the proposal to a
       durable store first; ``approve`` refuses a proposal that is not in the
       store. If persistence fails, no approval is created.
    2. **The binding is exact** -- ``ApprovalBinding`` contains the approver
       ``actor``, ``tenant``, canonical ``action_hash``, ``authority_snapshot``
       and ``expires_at``. A binding whose hash does not match the persisted
       proposal is rejected; editing the proposal after approval blocks execution.
    3. **Separation of duties** -- the proposer cannot be the approver.
    4. **Tenant isolation** -- an approval may only bind a proposal in the same
       tenant.
    5. **Expiry** -- an expired binding cannot be approved or executed.
    6. **Authority** -- the approver's snapshot must cover the action's required
       authority; at execution, the *current* authority must still cover the
       snapshot (narrowing blocks execution).
    7. **At-most-once** -- the execution state is persisted before the executor
       is called; a second ``execute`` on the same approval is rejected and the
       executor is called exactly once. Every effect carries a deterministic
       ``idempotency_key``.
    8. **State machine** -- only valid transitions happen
       (``PENDING -> APPROVED | REJECTED | CANCELLED``,
       ``APPROVED -> EXECUTED | REVOKED``, plus ``EXPIRED`` from either open
       state). Everything else raises ``InvalidApprovalTransition``.

Read first: docs/research/05-sendos-concept-map.md §4.1 and
docs/research/01-agent-architecture-sota.md §6.2-§6.4.

Public surface
--------------
``ApprovalState``        the state machine's states
``Authority``            deny-by-default scopes + amount limit
``ActionProposal``       what the agent wants to do (persisted first)
``action_hash``          canonical hash of action + arguments + tenant
``ApprovalBinding``      who approved what, under what authority, until when
``ApprovalRecord``       persisted approval state + execution record
``ExecutionResult``      the one execution's audit row
``ApprovedAction``       what the executor receives (with idempotency key)
``ProposalStore``        persistence seam (in-memory default; swap for SQL)
``InMemoryProposalStore``
``ApprovalCheckpoint``   propose -> approve/reject -> execute
``*Error``               typed failures for each invariant
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from agentlab.errors import AgentError
from agentlab.trace import Tracer


class ApprovalError(AgentError):
    """Base class for every approval-flow failure."""


class ProposalNotPersisted(ApprovalError):
    """The proposal was never written to the store before approval/execution."""


class ApprovalNotFound(ApprovalError):
    """No approval with this id (a wrong reference never satisfies a check)."""


class ProposerCannotApprove(ApprovalError):
    """Separation of duties: the proposer may not approve their own proposal."""


class TenantMismatch(ApprovalError):
    """The approval binding targets a different tenant than the proposal."""


class ActionHashMismatch(ApprovalError):
    """The approval does not bind the action that is actually persisted."""


class InsufficientAuthority(ApprovalError):
    """The approver's authority snapshot does not cover the required authority."""


class ApprovalExpired(ApprovalError):
    """The approval binding's expiry has passed."""


class AuthorityNarrowed(ApprovalError):
    """Effective authority shrank between approval and execution."""


class ApprovalReplayRejected(ApprovalError):
    """The approval was already executed; at-most-once means no second effect."""


class InvalidApprovalTransition(ApprovalError):
    """The requested state transition is not allowed from the current state."""


class ApprovalExecutionFailed(ApprovalError):
    """The executor raised; the approval is marked FAILED and is not retried."""


class ApprovalState(StrEnum):
    """The approval state machine.

    ``PENDING -> APPROVED | REJECTED | CANCELLED``; ``APPROVED -> EXECUTED |
    REVOKED``; ``PENDING | APPROVED -> EXPIRED``. Terminal states never leave.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REVOKED = "revoked"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Authority:
    """A deny-by-default permission set with an optional amount ceiling.

    ``scopes`` is the set of granted action scopes. ``max_amount_usd`` limits the
    monetary amount; ``None`` means "no amount limit". ``covers`` is the
    subset/superset test the whole approval flow is built on.
    """

    scopes: frozenset[str] = frozenset()
    max_amount_usd: float | None = None

    def covers(self, required: Authority) -> bool:
        """True when this authority grants everything ``required`` needs.

        Contract:
            - every required scope must be present here;
            - a required amount limit must be within this authority's limit;
            - if ``required.max_amount_usd`` is ``None``, no amount is required;
            - ``self.max_amount_usd is None`` means unlimited, so it covers any
              required amount.
        """
        raise NotImplementedError("Week 6 lab: implement Authority.covers")

    def intersect(self, other: Authority) -> Authority:
        """The narrowest authority both sides grant (scopes intersection, min limit)."""
        raise NotImplementedError("Week 6 lab: implement Authority.intersect")

    def is_subset_of(self, other: Authority) -> bool:
        """True when this authority is no wider than ``other``."""
        raise NotImplementedError("Week 6 lab: implement Authority.is_subset_of")


@dataclass(frozen=True, slots=True)
class ActionProposal:
    """What the agent proposes to do; persisted before anyone can approve it.

    Attributes:
        proposal_id: unique id (re-proposing the same id is rejected).
        tenant: tenant scope the action belongs to.
        actor: the proposing principal (agent/employee); cannot be the approver.
        action: the action name, e.g. ``"apply_discount"``.
        arguments: the exact arguments the executor will receive.
        rationale: why the agent recommends the action (audit context).
        required_authority: what authority the action needs.
        created_at: clock timestamp when the proposal was created.
    """

    proposal_id: str
    tenant: str
    actor: str
    action: str
    arguments: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    required_authority: Authority = field(default_factory=Authority)
    created_at: float = 0.0


def action_hash(action: str, arguments: Mapping[str, Any], tenant: str) -> str:
    """Canonical SHA-256 of the proposed action.

    Contract:
        - hashes ``{"action", "arguments", "tenant"}`` as compact JSON with
          sorted keys, so dict key order does not matter;
        - deterministic across processes; 64 hex characters;
        - changes when the action, any argument, or the tenant changes.
    """
    raise NotImplementedError("Week 6 lab: implement action_hash")


@dataclass(frozen=True, slots=True)
class ApprovalBinding:
    """The exact decision a human makes.

    Attributes:
        actor: the approver's principal id (must differ from the proposer).
        tenant: must match the proposal's tenant.
        action_hash: canonical hash of the approved action (see :func:`action_hash`).
        authority_snapshot: the approver's effective authority at approval time;
            execution requires current authority to still cover it.
        expires_at: clock timestamp after which the approval is expired.
    """

    actor: str
    tenant: str
    action_hash: str
    authority_snapshot: Authority
    expires_at: float


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """The audit row for the one allowed execution."""

    approval_id: str
    proposal_id: str
    action: str
    arguments: dict[str, Any]
    output: Any
    idempotency_key: str
    executed_at: float


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """Persisted approval state plus its binding and execution record."""

    approval_id: str
    proposal_id: str
    state: ApprovalState
    created_at: float
    updated_at: float
    binding: ApprovalBinding | None = None
    reason: str | None = None
    execution: ExecutionResult | None = None


@dataclass(frozen=True, slots=True)
class ApprovedAction:
    """What the executor receives -- only after every invariant has passed.

    ``idempotency_key`` is deterministic for the approval, so even a caller that
    ignores ``ApprovalReplayRejected`` cannot produce a second distinct effect at
    a well-behaved downstream system.
    """

    approval_id: str
    proposal_id: str
    tenant: str
    action: str
    arguments: dict[str, Any]
    proposer: str
    approver: str
    idempotency_key: str


class ProposalStore(Protocol):
    """Persistence seam for proposals.

    A production implementation is a transactional SQL table written *before*
    the approval record exists. The important property is that ``save`` is
    durable before ``approve`` returns success; the in-memory default only makes
    the lab testable.
    """

    def save(self, proposal: ActionProposal) -> None: ...

    def get(self, proposal_id: str) -> ActionProposal | None: ...


class InMemoryProposalStore:
    """A dict-backed proposal store (tests default)."""

    def __init__(self) -> None:
        self._proposals: dict[str, ActionProposal] = {}

    def save(self, proposal: ActionProposal) -> None:
        raise NotImplementedError("Week 6 lab: implement InMemoryProposalStore.save")

    def get(self, proposal_id: str) -> ActionProposal | None:
        raise NotImplementedError("Week 6 lab: implement InMemoryProposalStore.get")


class ApprovalCheckpoint:
    """Persist proposals, bind human approvals, execute at most once.

    ``clock`` is injectable so expiry tests are deterministic (no sleeps).
    ``tracer`` receives ``approval_requested`` / ``approval_granted`` /
    ``approval_denied`` / ``tool_call`` events for the audit trail.

    Method contracts:
        ``propose(proposal)``
            - rejects a blank id/tenant/actor/action and a duplicate proposal id;
            - *persists the proposal first* (``store.save``), then creates a
              PENDING approval record and emits ``approval_requested``;
            - returns the PENDING record.
        ``approve(approval_id, binding)``
            - unknown approval -> ``ApprovalNotFound``; non-PENDING ->
              ``InvalidApprovalTransition``;
            - proposal missing from the store -> ``ProposalNotPersisted``;
            - ``binding.actor == proposal.actor`` -> ``ProposerCannotApprove``;
            - tenant mismatch -> ``TenantMismatch``;
            - binding hash != canonical proposal hash -> ``ActionHashMismatch``;
            - binding snapshot does not cover required authority ->
              ``InsufficientAuthority``;
            - ``clock() >= binding.expires_at`` -> mark EXPIRED, emit
              ``approval_denied``, raise ``ApprovalExpired``;
            - otherwise APPROVED, emit ``approval_granted``, return the record.
        ``reject`` / ``cancel`` / ``revoke``
            - PENDING -> REJECTED / CANCELLED; APPROVED -> REVOKED; emit
              ``approval_denied``; invalid source state raises
              ``InvalidApprovalTransition``.
        ``execute(approval_id, executor, current_authority)``
            - unknown -> ``ApprovalNotFound``; state EXECUTED ->
              ``ApprovalReplayRejected``; non-APPROVED -> ``InvalidApprovalTransition``;
            - proposal missing -> ``ProposalNotPersisted``;
            - re-hash the persisted proposal; mismatch -> ``ActionHashMismatch``
              (the proposal was edited after approval);
            - ``clock() >= expires_at`` -> mark EXPIRED, emit denied, raise
              ``ApprovalExpired``;
            - current authority must cover the binding snapshot, else emit denied
              and raise ``AuthorityNarrowed``;
            - mark EXECUTED *before* calling the executor (at-most-once
              reservation), build ``ApprovedAction`` with a deterministic
              idempotency key, call ``executor`` exactly once, persist the
              ``ExecutionResult`` and emit ``tool_call``;
            - if the executor raises, mark FAILED and raise
              ``ApprovalExecutionFailed`` (no retry, no second effect).
        ``get(approval_id)`` and ``pending()``
            - read access for the UI/API and for tests.
    """

    def __init__(
        self,
        *,
        store: ProposalStore | None = None,
        clock: Callable[[], float] | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self.store: ProposalStore = store or InMemoryProposalStore()
        self.clock: Callable[[], float] = clock or time.time
        self.tracer = tracer
        self._approvals: dict[str, ApprovalRecord] = {}
        self._next_id = 0

    def propose(self, proposal: ActionProposal) -> ApprovalRecord:
        """Persist the proposal, then open a PENDING approval."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.propose")

    def approve(self, approval_id: str, binding: ApprovalBinding) -> ApprovalRecord:
        """Bind an approval to the persisted proposal (see class contract)."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.approve")

    def reject(self, approval_id: str, *, actor: str, reason: str = "") -> ApprovalRecord:
        """Reject a PENDING approval."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.reject")

    def cancel(self, approval_id: str, *, actor: str, reason: str = "") -> ApprovalRecord:
        """Cancel a PENDING approval."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.cancel")

    def revoke(self, approval_id: str, *, actor: str, reason: str = "") -> ApprovalRecord:
        """Revoke an APPROVED approval before execution."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.revoke")

    def execute(
        self,
        approval_id: str,
        *,
        executor: Callable[[ApprovedAction], Any],
        current_authority: Authority,
    ) -> ExecutionResult:
        """Execute an approved action exactly once (see class contract)."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.execute")

    def get(self, approval_id: str) -> ApprovalRecord:
        """The current record; raises ``ApprovalNotFound`` when absent."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.get")

    def pending(self) -> tuple[ApprovalRecord, ...]:
        """All approvals still awaiting an approve/reject/cancel decision."""
        raise NotImplementedError("Week 6 lab: implement ApprovalCheckpoint.pending")
