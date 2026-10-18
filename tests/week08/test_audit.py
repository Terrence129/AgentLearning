"""Audit tests: append-only enforcement, hash chain, evidence and correlation ids."""

from __future__ import annotations

import json

import pytest
from agentlab.guard.audit import GENESIS_HASH, AuditLog, AuditRecord
from agentlab.guard.errors import AuditViolation

pytestmark = pytest.mark.week


class _Clock:
    """Injectible clock: the audit log must never read the wall clock in tests."""

    def __init__(self, value: float = 100.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _append(log: AuditLog, *, action: str = "refund.issue", correlation_id: str = "corr-1") -> AuditRecord:
    return log.append(
        tenant_id="tenant-a",
        actor="alice",
        action=action,
        correlation_id=correlation_id,
        decision="allowed",
        before={"order_state": "new"},
        after={"order_state": "refunded"},
        rule_id="policy.refund.v3",
    )


def test_append_assigns_monotonic_sequence_and_hash_chain():
    log = AuditLog(clock=_Clock(100.0))

    first = _append(log)
    second = _append(log, action="refund.settle")

    assert (first.seq, second.seq) == (1, 2)
    assert first.prev_hash == GENESIS_HASH
    assert second.prev_hash == first.record_hash
    assert len(second.record_hash) == 64
    assert len(log.records()) == 2
    assert log.verify_integrity() is True


def test_update_is_rejected_and_recorded():
    log = AuditLog(clock=_Clock(100.0))
    _append(log)

    with pytest.raises(AuditViolation):
        log.update(1, actor="mallory")

    assert log.records()[0].actor == "alice"
    assert len(log.attempts()) == 1
    assert "update" in log.attempts()[0]
    assert log.verify_integrity() is True


def test_delete_is_rejected_and_file_is_unchanged(tmp_path):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, clock=_Clock(100.0))
    _append(log)
    before = path.read_text(encoding="utf-8")

    with pytest.raises(AuditViolation):
        log.delete(1)

    assert path.read_text(encoding="utf-8") == before
    assert "delete" in log.attempts()[0]
    assert len(log.records()) == 1


def test_correlation_ids_link_before_and_after_evidence():
    log = AuditLog(clock=_Clock(100.0))
    _append(log)
    log.append(
        tenant_id="tenant-a",
        actor="system",
        action="refund.result",
        correlation_id="corr-1",
        decision="allowed",
        before={"order_state": "refunded"},
        after={"order_state": "settled"},
    )

    rows = log.find("corr-1")

    assert [row.action for row in rows] == ["refund.issue", "refund.result"]
    assert rows[0].before == {"order_state": "new"}
    assert rows[1].after == {"order_state": "settled"}
    assert log.find("missing") == []


def test_log_persists_and_reloads_from_jsonl(tmp_path):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, clock=_Clock(100.0))
    _append(log)
    _append(log, action="refund.settle")

    reloaded = AuditLog(path)

    assert reloaded.records() == log.records()
    assert reloaded.verify_integrity() is True


def test_tampered_log_fails_integrity_check(tmp_path):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, clock=_Clock(100.0))
    _append(log)
    _append(log, action="refund.settle")
    lines = path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[1])
    tampered["action"] = "refund.reissued"
    lines[1] = json.dumps(tampered)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    reloaded = AuditLog(path)

    assert reloaded.verify_integrity() is False


def test_invalid_decision_is_rejected():
    log = AuditLog(clock=_Clock(100.0))

    with pytest.raises(ValueError, match="decision"):
        log.append(
            tenant_id="tenant-a",
            actor="alice",
            action="refund.issue",
            correlation_id="corr-1",
            decision="maybe",
        )
