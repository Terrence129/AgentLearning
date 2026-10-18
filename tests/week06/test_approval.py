"""Tests for the bound, at-most-once approval checkpoint (week 6 lab).

These tests are the specification. Each one corresponds to an invariant in the
module docstring; together they are the security argument for the whole course.
"""

from __future__ import annotations

from dataclasses import replace

import pytest
from agentlab.errors import AgentError
from agentlab.orchestrator.approval import (
    ActionHashMismatch,
    ActionProposal,
    ApprovalBinding,
    ApprovalCheckpoint,
    ApprovalExecutionFailed,
    ApprovalExpired,
    ApprovalNotFound,
    ApprovalRecord,
    ApprovalReplayRejected,
    ApprovalState,
    ApprovedAction,
    Authority,
    AuthorityNarrowed,
    InMemoryProposalStore,
    InsufficientAuthority,
    InvalidApprovalTransition,
    ProposalNotPersisted,
    ProposerCannotApprove,
    TenantMismatch,
    action_hash,
)
from agentlab.testing import MemorySink, Tracer

pytestmark = pytest.mark.week


# ---------------------------------------------------------------------------
# fixtures and fakes
# ---------------------------------------------------------------------------


class FakeClock:
    """Deterministic clock: expiry needs no sleeps."""

    def __init__(self, now: float = 1_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class RecordingStore(InMemoryProposalStore):
    """Records the order of store calls (to prove save-before-approve)."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, str]] = []

    def save(self, proposal: ActionProposal) -> None:
        self.events.append(("save", proposal.proposal_id))
        super().save(proposal)

    def get(self, proposal_id: str) -> ActionProposal | None:
        self.events.append(("get", proposal_id))
        return super().get(proposal_id)


class ForgetfulStore(InMemoryProposalStore):
    """A store that silently keeps nothing."""

    def save(self, proposal: ActionProposal) -> None:
        pass

    def get(self, proposal_id: str) -> ActionProposal | None:
        return None


class FailingStore(InMemoryProposalStore):
    """A store whose durable write fails."""

    def save(self, proposal: ActionProposal) -> None:
        raise RuntimeError("disk full")

    def get(self, proposal_id: str) -> ActionProposal | None:
        return None


class RecordingExecutor:
    """Records every invocation and returns a deterministic receipt."""

    def __init__(self, output: str = "REFUNDED-123") -> None:
        self.output = output
        self.calls: list[ApprovedAction] = []

    def __call__(self, action: ApprovedAction) -> str:
        self.calls.append(action)
        return self.output


def authority(scopes: tuple[str, ...] = ("discount.apply",), max_amount: float | None = 500.0) -> Authority:
    return Authority(scopes=frozenset(scopes), max_amount_usd=max_amount)


def make_proposal(**overrides: object) -> ActionProposal:
    values: dict[str, object] = {
        "proposal_id": "p-1",
        "tenant": "tenant-a",
        "actor": "agent:planner",
        "action": "apply_discount",
        "arguments": {"deal_id": "deal-42", "percent": 10},
        "rationale": "Deal is at risk; 10% is inside policy.",
        "required_authority": authority(),
        "created_at": 0.0,
    }
    values.update(overrides)
    return ActionProposal(**values)  # type: ignore[arg-type]


def make_binding(
    proposal: ActionProposal,
    *,
    actor: str = "user:alice",
    tenant: str | None = None,
    expires_at: float = 2_000.0,
    snapshot: Authority | None = None,
    hash_value: str | None = None,
) -> ApprovalBinding:
    return ApprovalBinding(
        actor=actor,
        tenant=tenant if tenant is not None else proposal.tenant,
        action_hash=hash_value or action_hash(proposal.action, proposal.arguments, proposal.tenant),
        authority_snapshot=snapshot if snapshot is not None else authority(),
        expires_at=expires_at,
    )


def approved_checkpoint(
    *, tracer: Tracer | None = None, clock: FakeClock | None = None
) -> tuple[ApprovalCheckpoint, ActionProposal, ApprovalRecord, FakeClock]:
    clock = clock or FakeClock()
    checkpoint = ApprovalCheckpoint(clock=clock, tracer=tracer)
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)
    approved = checkpoint.approve(pending.approval_id, make_binding(proposal, expires_at=clock.now + 1_000))
    return checkpoint, proposal, approved, clock


# ---------------------------------------------------------------------------
# invariant 1: persisted before approval
# ---------------------------------------------------------------------------


def test_propose_persists_the_proposal_before_opening_the_approval() -> None:
    store = RecordingStore()
    checkpoint = ApprovalCheckpoint(store=store, clock=FakeClock())

    pending = checkpoint.propose(make_proposal())

    assert store.events == [("save", "p-1")]
    assert store.get("p-1") is not None
    assert pending.state is ApprovalState.PENDING
    assert checkpoint.get(pending.approval_id).state is ApprovalState.PENDING


def test_persistence_failure_means_no_approval_exists() -> None:
    checkpoint = ApprovalCheckpoint(store=FailingStore(), clock=FakeClock())

    with pytest.raises(RuntimeError, match="disk full"):
        checkpoint.propose(make_proposal())

    assert checkpoint.pending() == ()


def test_approve_refuses_a_proposal_that_was_not_persisted() -> None:
    checkpoint = ApprovalCheckpoint(store=ForgetfulStore(), clock=FakeClock())
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)

    with pytest.raises(ProposalNotPersisted, match="persist"):
        checkpoint.approve(pending.approval_id, make_binding(proposal))

    assert checkpoint.get(pending.approval_id).state is ApprovalState.PENDING


def test_approving_an_unknown_approval_is_rejected() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    with pytest.raises(ApprovalNotFound):
        checkpoint.approve("approval-999", make_binding(make_proposal()))


# ---------------------------------------------------------------------------
# invariant 2: the binding is exact
# ---------------------------------------------------------------------------


def test_proposer_cannot_approve_their_own_proposal() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)

    with pytest.raises(ProposerCannotApprove):
        checkpoint.approve(pending.approval_id, make_binding(proposal, actor=proposal.actor))


def test_tenant_mismatch_is_rejected() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)

    with pytest.raises(TenantMismatch):
        checkpoint.approve(pending.approval_id, make_binding(proposal, tenant="tenant-b"))


def test_binding_hash_must_match_the_persisted_proposal() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)
    foreign_hash = action_hash("delete_account", {"tenant": "tenant-a"}, proposal.tenant)

    with pytest.raises(ActionHashMismatch):
        checkpoint.approve(pending.approval_id, make_binding(proposal, hash_value=foreign_hash))


def test_proposal_edited_after_approval_cannot_execute() -> None:
    checkpoint, proposal, approved, _ = approved_checkpoint()
    edited = replace(proposal, arguments={"deal_id": "deal-42", "percent": 100})
    checkpoint.store.save(edited)
    executor = RecordingExecutor()

    with pytest.raises(ActionHashMismatch):
        checkpoint.execute(approved.approval_id, executor=executor, current_authority=authority())

    assert executor.calls == []


# ---------------------------------------------------------------------------
# invariants 5 and 6: expiry and authority
# ---------------------------------------------------------------------------


def test_approver_authority_must_cover_the_required_authority() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)

    with pytest.raises(InsufficientAuthority):
        checkpoint.approve(
            pending.approval_id,
            make_binding(proposal, snapshot=authority(scopes=("refund.issue",))),
        )


def test_expired_binding_cannot_be_approved() -> None:
    clock = FakeClock(now=2_000.0)
    checkpoint = ApprovalCheckpoint(clock=clock)
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)

    with pytest.raises(ApprovalExpired):
        checkpoint.approve(pending.approval_id, make_binding(proposal, expires_at=clock.now - 1))

    assert checkpoint.get(pending.approval_id).state is ApprovalState.EXPIRED


def test_approval_expires_between_approval_and_execution() -> None:
    clock = FakeClock()
    checkpoint = ApprovalCheckpoint(clock=clock)
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)
    approved = checkpoint.approve(pending.approval_id, make_binding(proposal, expires_at=clock.now + 10))
    clock.advance(60)
    executor = RecordingExecutor()

    with pytest.raises(ApprovalExpired):
        checkpoint.execute(approved.approval_id, executor=executor, current_authority=authority())

    assert executor.calls == []
    assert checkpoint.get(approved.approval_id).state is ApprovalState.EXPIRED


def test_authority_narrowing_between_approval_and_execution_blocks() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    proposal = make_proposal()
    pending = checkpoint.propose(proposal)
    broad_snapshot = authority(scopes=("discount.apply", "refund.issue"))
    approved = checkpoint.approve(pending.approval_id, make_binding(proposal, snapshot=broad_snapshot))
    executor = RecordingExecutor()

    with pytest.raises(AuthorityNarrowed):
        checkpoint.execute(
            approved.approval_id,
            executor=executor,
            current_authority=authority(scopes=("discount.apply",)),
        )

    assert executor.calls == []


# ---------------------------------------------------------------------------
# invariant 7: at-most-once execution
# ---------------------------------------------------------------------------


def test_executes_exactly_once_with_a_deterministic_idempotency_key() -> None:
    checkpoint, proposal, approved, clock = approved_checkpoint()
    executor = RecordingExecutor("REFUNDED-123")

    result = checkpoint.execute(approved.approval_id, executor=executor, current_authority=authority())

    assert result.output == "REFUNDED-123"
    assert len(executor.calls) == 1
    action = executor.calls[0]
    assert isinstance(action, ApprovedAction)
    assert action.approval_id == approved.approval_id
    assert action.proposal_id == proposal.proposal_id
    assert action.tenant == proposal.tenant
    assert action.action == proposal.action
    assert action.arguments == proposal.arguments
    assert action.proposer == proposal.actor
    assert action.approver == "user:alice"
    assert approved.approval_id in action.idempotency_key
    assert action.idempotency_key == result.idempotency_key
    assert result.executed_at == clock.now
    assert checkpoint.get(approved.approval_id).state is ApprovalState.EXECUTED
    assert checkpoint.get(approved.approval_id).execution == result


def test_replay_is_rejected_without_a_second_side_effect() -> None:
    checkpoint, _, approved, _ = approved_checkpoint()
    executor = RecordingExecutor()
    checkpoint.execute(approved.approval_id, executor=executor, current_authority=authority())

    with pytest.raises(ApprovalReplayRejected):
        checkpoint.execute(approved.approval_id, executor=executor, current_authority=authority())

    assert len(executor.calls) == 1


def test_executor_failure_marks_failed_and_never_retries() -> None:
    checkpoint, _, approved, _ = approved_checkpoint()
    calls: list[ApprovedAction] = []

    def failing_executor(action: ApprovedAction) -> str:
        calls.append(action)
        raise ValueError("bank down")

    with pytest.raises(ApprovalExecutionFailed, match="bank down"):
        checkpoint.execute(approved.approval_id, executor=failing_executor, current_authority=authority())

    assert len(calls) == 1
    assert checkpoint.get(approved.approval_id).state is ApprovalState.FAILED

    with pytest.raises(AgentError):
        checkpoint.execute(approved.approval_id, executor=failing_executor, current_authority=authority())
    assert len(calls) == 1


def test_pending_approval_cannot_execute() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    pending = checkpoint.propose(make_proposal())
    executor = RecordingExecutor()

    with pytest.raises(InvalidApprovalTransition):
        checkpoint.execute(pending.approval_id, executor=executor, current_authority=authority())

    assert executor.calls == []


# ---------------------------------------------------------------------------
# invariant 8: the state machine
# ---------------------------------------------------------------------------


def test_approving_twice_is_an_invalid_transition() -> None:
    checkpoint, proposal, approved, _ = approved_checkpoint()
    with pytest.raises(InvalidApprovalTransition):
        checkpoint.approve(approved.approval_id, make_binding(proposal))


def test_rejecting_a_pending_approval_blocks_execution() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    pending = checkpoint.propose(make_proposal())

    rejected = checkpoint.reject(pending.approval_id, actor="user:alice", reason="policy")

    assert rejected.state is ApprovalState.REJECTED
    assert rejected.reason == "policy"
    executor = RecordingExecutor()
    with pytest.raises(InvalidApprovalTransition):
        checkpoint.execute(pending.approval_id, executor=executor, current_authority=authority())
    assert executor.calls == []


def test_cancelling_a_pending_approval_removes_it_from_the_queue() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    pending = checkpoint.propose(make_proposal())
    assert len(checkpoint.pending()) == 1

    cancelled = checkpoint.cancel(pending.approval_id, actor="agent:planner")

    assert cancelled.state is ApprovalState.CANCELLED
    assert checkpoint.pending() == ()


def test_revoking_an_approved_approval_blocks_execution() -> None:
    checkpoint, _, approved, _ = approved_checkpoint()

    revoked = checkpoint.revoke(approved.approval_id, actor="user:alice")

    assert revoked.state is ApprovalState.REVOKED
    executor = RecordingExecutor()
    with pytest.raises(InvalidApprovalTransition):
        checkpoint.execute(approved.approval_id, executor=executor, current_authority=authority())
    assert executor.calls == []


def test_pending_lists_only_undecided_approvals() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    first = checkpoint.propose(make_proposal(proposal_id="p-1"))
    second = checkpoint.propose(make_proposal(proposal_id="p-2"))

    assert {record.approval_id for record in checkpoint.pending()} == {
        first.approval_id,
        second.approval_id,
    }

    checkpoint.reject(first.approval_id, actor="user:alice")
    assert [record.approval_id for record in checkpoint.pending()] == [second.approval_id]


# ---------------------------------------------------------------------------
# proposal hygiene and helpers
# ---------------------------------------------------------------------------


def test_duplicate_proposal_ids_are_rejected() -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    checkpoint.propose(make_proposal())

    with pytest.raises(AgentError, match="already"):
        checkpoint.propose(make_proposal())


@pytest.mark.parametrize("field", ["proposal_id", "tenant", "actor", "action"])
def test_blank_proposal_fields_are_rejected(field: str) -> None:
    checkpoint = ApprovalCheckpoint(clock=FakeClock())
    with pytest.raises(AgentError):
        checkpoint.propose(make_proposal(**{field: "  "}))


def test_action_hash_is_canonical_and_argument_sensitive() -> None:
    first = action_hash("apply_discount", {"deal_id": "d", "percent": 10}, "tenant-a")
    reordered = action_hash("apply_discount", {"percent": 10, "deal_id": "d"}, "tenant-a")
    changed = action_hash("apply_discount", {"deal_id": "d", "percent": 20}, "tenant-a")
    other_tenant = action_hash("apply_discount", {"deal_id": "d", "percent": 10}, "tenant-b")

    assert first == reordered
    assert first != changed
    assert first != other_tenant
    assert len(first) == 64


def test_authority_covers_intersects_and_narrows() -> None:
    broad = Authority(scopes=frozenset({"a", "b"}))
    narrow = Authority(scopes=frozenset({"a"}), max_amount_usd=100.0)
    capped = Authority(scopes=frozenset({"a"}), max_amount_usd=500.0)

    assert broad.covers(narrow)
    assert not narrow.covers(broad)
    assert not narrow.covers(capped)  # 100 cap cannot cover a required 500 cap
    assert Authority(scopes=frozenset({"a"})).covers(capped)  # no limit = unlimited
    assert narrow.is_subset_of(broad)
    assert not broad.is_subset_of(narrow)

    intersection = broad.intersect(narrow)
    assert intersection.scopes == frozenset({"a"})
    assert intersection.max_amount_usd == 100.0


# ---------------------------------------------------------------------------
# audit trail
# ---------------------------------------------------------------------------


def test_trace_emits_the_approval_lifecycle() -> None:
    sink = MemorySink()
    tracer = Tracer(run_id="run-approval", sinks=[sink])
    checkpoint, _, approved, _ = approved_checkpoint(tracer=tracer)
    checkpoint.execute(
        approved.approval_id,
        executor=RecordingExecutor(),
        current_authority=authority(),
    )

    assert [event.kind for event in sink.events] == [
        "approval_requested",
        "approval_granted",
        "tool_call",
    ]
    requested, granted, executed = (event.data for event in sink.events)
    assert requested["approval_id"] == approved.approval_id
    assert requested["action"] == "apply_discount"
    assert granted["approver"] == "user:alice"
    assert executed["idempotency_key"]
    assert "arguments" not in executed


def test_trace_emits_denial_events() -> None:
    sink = MemorySink()
    tracer = Tracer(run_id="run-denial", sinks=[sink])
    checkpoint = ApprovalCheckpoint(clock=FakeClock(), tracer=tracer)
    pending = checkpoint.propose(make_proposal())
    checkpoint.reject(pending.approval_id, actor="user:alice", reason="not allowed")

    assert [event.kind for event in sink.events] == ["approval_requested", "approval_denied"]
    assert sink.events[-1].data["reason"] == "not allowed"
