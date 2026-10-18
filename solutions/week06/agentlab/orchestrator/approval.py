"""Approval checkpoints: bound, human-in-the-loop, at-most-once writes (week 6).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
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
    """The approval state machine."""

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
    """A deny-by-default permission set with an optional amount ceiling."""

    scopes: frozenset[str] = frozenset()
    max_amount_usd: float | None = None

    def covers(self, required: Authority) -> bool:
        if not required.scopes <= self.scopes:
            return False
        return not (
            required.max_amount_usd is not None
            and self.max_amount_usd is not None
            and self.max_amount_usd < required.max_amount_usd
        )

    def intersect(self, other: Authority) -> Authority:
        limits = [value for value in (self.max_amount_usd, other.max_amount_usd) if value is not None]
        return Authority(
            scopes=self.scopes & other.scopes,
            max_amount_usd=min(limits) if limits else None,
        )

    def is_subset_of(self, other: Authority) -> bool:
        return other.covers(self)


@dataclass(frozen=True, slots=True)
class ActionProposal:
    """What the agent proposes to do; persisted before anyone can approve it."""

    proposal_id: str
    tenant: str
    actor: str
    action: str
    arguments: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    required_authority: Authority = field(default_factory=Authority)
    created_at: float = 0.0


def action_hash(action: str, arguments: Mapping[str, Any], tenant: str) -> str:
    payload = {"action": action, "arguments": dict(arguments), "tenant": tenant}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ApprovalBinding:
    """The exact decision a human makes."""

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
    """What the executor receives -- only after every invariant has passed."""

    approval_id: str
    proposal_id: str
    tenant: str
    action: str
    arguments: dict[str, Any]
    proposer: str
    approver: str
    idempotency_key: str


class ProposalStore(Protocol):
    """Persistence seam for proposals."""

    def save(self, proposal: ActionProposal) -> None: ...

    def get(self, proposal_id: str) -> ActionProposal | None: ...


class InMemoryProposalStore:
    """A dict-backed proposal store (tests default)."""

    def __init__(self) -> None:
        self._proposals: dict[str, ActionProposal] = {}

    def save(self, proposal: ActionProposal) -> None:
        self._proposals[proposal.proposal_id] = proposal

    def get(self, proposal_id: str) -> ActionProposal | None:
        return self._proposals.get(proposal_id)


def _as_text(value: Any) -> Any:
    return value


class ApprovalCheckpoint:
    """Persist proposals, bind human approvals, execute at most once."""

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

    # -- helpers -----------------------------------------------------------

    def _now(self) -> float:
        return float(self.clock())

    def _emit(self, kind: str, name: str, data: dict[str, Any]) -> None:
        if self.tracer is not None:
            self.tracer.emit(kind, name, data)

    def _require(self, approval_id: str) -> ApprovalRecord:
        record = self._approvals.get(approval_id)
        if record is None:
            raise ApprovalNotFound(f"approval {approval_id!r} does not exist")
        return record

    def _put(self, record: ApprovalRecord) -> ApprovalRecord:
        self._approvals[record.approval_id] = record
        return record

    def _transition(
        self,
        record: ApprovalRecord,
        state: ApprovalState,
        *,
        reason: str | None = None,
        binding: ApprovalBinding | None = None,
        execution: ExecutionResult | None = None,
    ) -> ApprovalRecord:
        updated = replace(record, state=state, updated_at=self._now())
        if reason is not None:
            updated = replace(updated, reason=reason)
        if binding is not None:
            updated = replace(updated, binding=binding)
        if execution is not None:
            updated = replace(updated, execution=execution)
        return self._put(updated)

    def _deny(
        self,
        record: ApprovalRecord,
        reason: str,
        *,
        actor: str | None = None,
        state: ApprovalState | None = None,
    ) -> ApprovalRecord:
        updated = (
            self._transition(record, state, reason=reason)
            if state is not None
            else self._put(replace(record, reason=reason, updated_at=self._now()))
        )
        self._emit(
            "approval_denied",
            f"approval:{record.proposal_id}",
            {
                "approval_id": record.approval_id,
                "proposal_id": record.proposal_id,
                "reason": reason,
                "actor": actor,
            },
        )
        return updated

    # -- proposal ----------------------------------------------------------

    def propose(self, proposal: ActionProposal) -> ApprovalRecord:
        if not proposal.proposal_id.strip():
            raise ApprovalError("proposal_id must not be blank")
        if not proposal.tenant.strip():
            raise ApprovalError("proposal tenant must not be blank")
        if not proposal.actor.strip():
            raise ApprovalError("proposal actor must not be blank")
        if not proposal.action.strip():
            raise ApprovalError("proposal action must not be blank")
        if any(record.proposal_id == proposal.proposal_id for record in self._approvals.values()):
            raise ApprovalError(f"proposal {proposal.proposal_id!r} already has an approval")

        # Invariant 1: the proposal is durable *before* any approval exists.
        self.store.save(proposal)

        self._next_id += 1
        now = self._now()
        record = ApprovalRecord(
            approval_id=f"approval-{self._next_id}",
            proposal_id=proposal.proposal_id,
            state=ApprovalState.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._put(record)
        self._emit(
            "approval_requested",
            f"approval:{proposal.action}",
            {
                "approval_id": record.approval_id,
                "proposal_id": proposal.proposal_id,
                "action": proposal.action,
                "actor": proposal.actor,
                "tenant": proposal.tenant,
            },
        )
        return record

    # -- decisions ---------------------------------------------------------

    def approve(self, approval_id: str, binding: ApprovalBinding) -> ApprovalRecord:
        record = self._require(approval_id)
        if record.state is not ApprovalState.PENDING:
            raise InvalidApprovalTransition(
                f"approval {approval_id!r} is {record.state.value}; only a pending approval can be approved"
            )
        proposal = self.store.get(record.proposal_id)
        if proposal is None:
            raise ProposalNotPersisted(
                f"proposal {record.proposal_id!r} is not persisted; refusing to approve an "
                "action that has no durable record"
            )
        if binding.actor == proposal.actor:
            raise ProposerCannotApprove(
                f"approver {binding.actor!r} is the proposer; separation of duties forbids self-approval"
            )
        if binding.tenant != proposal.tenant:
            raise TenantMismatch(
                f"approval tenant {binding.tenant!r} does not match proposal tenant {proposal.tenant!r}"
            )
        expected_hash = action_hash(proposal.action, proposal.arguments, proposal.tenant)
        if binding.action_hash != expected_hash:
            raise ActionHashMismatch(
                "approval binding does not match the persisted proposal; the proposal may "
                "have been edited after the human decided"
            )
        if not binding.authority_snapshot.covers(proposal.required_authority):
            raise InsufficientAuthority(
                f"approver authority {sorted(binding.authority_snapshot.scopes)!r} does not "
                f"cover the action's required authority "
                f"{sorted(proposal.required_authority.scopes)!r}"
            )
        if self._now() >= binding.expires_at:
            self._deny(
                record,
                "approval binding expired before approval",
                actor=binding.actor,
                state=ApprovalState.EXPIRED,
            )
            raise ApprovalExpired(f"approval binding expired at {binding.expires_at}; refusing to approve")

        approved = self._transition(record, ApprovalState.APPROVED, binding=binding)
        self._emit(
            "approval_granted",
            f"approval:{proposal.action}",
            {
                "approval_id": record.approval_id,
                "proposal_id": proposal.proposal_id,
                "approver": binding.actor,
                "tenant": binding.tenant,
                "expires_at": binding.expires_at,
            },
        )
        return approved

    def reject(self, approval_id: str, *, actor: str, reason: str = "") -> ApprovalRecord:
        record = self._require(approval_id)
        if record.state is not ApprovalState.PENDING:
            raise InvalidApprovalTransition(
                f"approval {approval_id!r} is {record.state.value}; only a pending approval can be rejected"
            )
        return self._deny(
            record,
            reason or "rejected by approver",
            actor=actor,
            state=ApprovalState.REJECTED,
        )

    def cancel(self, approval_id: str, *, actor: str, reason: str = "") -> ApprovalRecord:
        record = self._require(approval_id)
        if record.state is not ApprovalState.PENDING:
            raise InvalidApprovalTransition(
                f"approval {approval_id!r} is {record.state.value}; only a pending approval can be cancelled"
            )
        return self._deny(
            record, reason or "cancelled by proposer", actor=actor, state=ApprovalState.CANCELLED
        )

    def revoke(self, approval_id: str, *, actor: str, reason: str = "") -> ApprovalRecord:
        record = self._require(approval_id)
        if record.state is not ApprovalState.APPROVED:
            raise InvalidApprovalTransition(
                f"approval {approval_id!r} is {record.state.value}; only an approved approval can be revoked"
            )
        return self._deny(record, reason or "revoked by approver", actor=actor, state=ApprovalState.REVOKED)

    # -- execution ---------------------------------------------------------

    def execute(
        self,
        approval_id: str,
        *,
        executor: Callable[[ApprovedAction], Any],
        current_authority: Authority,
    ) -> ExecutionResult:
        record = self._require(approval_id)
        if record.state is ApprovalState.EXECUTED:
            raise ApprovalReplayRejected(
                f"approval {approval_id!r} was already executed; at-most-once execution "
                "forbids a second side effect"
            )
        if record.state is not ApprovalState.APPROVED:
            raise InvalidApprovalTransition(
                f"approval {approval_id!r} is {record.state.value}; only an approved approval can be executed"
            )
        binding = record.binding
        if binding is None:  # defensive: an APPROVED record always has a binding
            raise InvalidApprovalTransition(f"approval {approval_id!r} has no binding")
        proposal = self.store.get(record.proposal_id)
        if proposal is None:
            raise ProposalNotPersisted(
                f"proposal {record.proposal_id!r} is not persisted; refusing to execute"
            )
        expected_hash = action_hash(proposal.action, proposal.arguments, proposal.tenant)
        if expected_hash != binding.action_hash:
            raise ActionHashMismatch(
                "the persisted proposal changed after approval; the approval no longer binds "
                "the action that would execute"
            )
        if self._now() >= binding.expires_at:
            self._deny(
                record,
                "approval binding expired before execution",
                state=ApprovalState.EXPIRED,
            )
            raise ApprovalExpired(f"approval binding expired at {binding.expires_at}; refusing to execute")
        if not current_authority.covers(binding.authority_snapshot):
            self._deny(record, "effective authority narrowed between approval and execution")
            raise AuthorityNarrowed(
                "effective authority no longer covers the authority snapshot recorded at "
                "approval time; re-approval is required"
            )

        # Invariant 7: reserve the one execution before the side effect happens.
        idempotency_key = f"{record.approval_id}:{binding.action_hash[:16]}"
        reserved = self._transition(record, ApprovalState.EXECUTED)
        action = ApprovedAction(
            approval_id=record.approval_id,
            proposal_id=proposal.proposal_id,
            tenant=proposal.tenant,
            action=proposal.action,
            arguments=dict(proposal.arguments),
            proposer=proposal.actor,
            approver=binding.actor,
            idempotency_key=idempotency_key,
        )
        try:
            output = executor(action)
        except Exception as exc:
            self._transition(
                reserved,
                ApprovalState.FAILED,
                reason=f"executor raised {type(exc).__name__}: {exc}",
            )
            raise ApprovalExecutionFailed(
                f"execution of approval {approval_id!r} failed: {type(exc).__name__}: {exc}"
            ) from exc

        result = ExecutionResult(
            approval_id=record.approval_id,
            proposal_id=proposal.proposal_id,
            action=proposal.action,
            arguments=dict(proposal.arguments),
            output=output,
            idempotency_key=idempotency_key,
            executed_at=self._now(),
        )
        self._put(replace(reserved, execution=result))
        self._emit(
            "tool_call",
            proposal.action,
            {
                "approval_id": record.approval_id,
                "proposal_id": proposal.proposal_id,
                "action": proposal.action,
                "idempotency_key": idempotency_key,
            },
        )
        return result

    # -- read access -------------------------------------------------------

    def get(self, approval_id: str) -> ApprovalRecord:
        return self._require(approval_id)

    def pending(self) -> tuple[ApprovalRecord, ...]:
        return tuple(record for record in self._approvals.values() if record.state is ApprovalState.PENDING)
