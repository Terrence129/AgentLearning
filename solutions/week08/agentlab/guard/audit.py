"""Append-only audit log: the evidence you cannot edit after the fact.

Audit is a *separate product* from observability (research 03 §3.4): debug
traces may be sampled, redacted and deleted; the audit log must survive
retention policies, incident reviews and -- eventually -- auditors. The
properties that make it usable as evidence are all structural:

- **Append-only**: there is no update and no delete. The API exposes them only
  so that an attempted mutation is *rejected and recorded* -- an attempted
  deletion is itself an incident worth keeping.
- **Before/after evidence**: every consequential action records the state it
  changed, so a reviewer can reconstruct the effect without replaying the model.
- **Correlation id**: one id links proposal, approval, execution and result, so
  a request can be followed ingress-to-audit-row in one query.
- **Hash chain**: each record hashes the previous record's hash. Anyone editing
  or deleting a line breaks ``verify_integrity``; you cannot silently rewrite
  history even with filesystem access.

Read first: research 03 §2.3 (audit vs debug) and §3.4 (what one audit row
contains: timestamp, tenant, user, agent+version, model+version, tool, redacted
arguments, policy decision + rule id, approver, result, idempotency key, trace id).

Hints:
- Hash a canonical JSON form of the record with ``sort_keys=True`` and compact
  separators, and include the *previous* hash in the payload.
- Keep ``before``/``after`` as plain dicts: JSONL is the storage format, so
  anything not JSON-serialisable will not survive the first export.
- Persist each line immediately; a buffered audit log loses exactly the records
  an incident needs.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentlab.guard.errors import AuditViolation

#: ``prev_hash`` of the first record: a fixed sentinel, never a leftover.
GENESIS_HASH = "0" * 64

#: Decisions an audit row may record.
_DECISIONS: frozenset[str] = frozenset({"allowed", "denied"})

_HASHED_FIELDS: tuple[str, ...] = (
    "seq",
    "ts",
    "tenant_id",
    "actor",
    "action",
    "correlation_id",
    "decision",
    "before",
    "after",
    "rule_id",
    "prev_hash",
)


def _canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _record_hash(**fields: Any) -> str:
    return hashlib.sha256(
        _canonical({name: fields[name] for name in _HASHED_FIELDS}).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """One immutable audit row.

    Attributes:
        seq: store-assigned monotonic sequence, starting at 1.
        ts: epoch seconds from the log's clock (injected in tests).
        tenant_id: tenant the action ran for.
        actor: human or service principal that initiated the action.
        action: what was done, e.g. ``"refund.issue"``.
        correlation_id: joins every row for one request/run.
        decision: ``"allowed"`` or ``"denied"``.
        before: redacted state before the action (``None`` for reads).
        after: redacted state after the action (``None`` when denied).
        rule_id: policy rule that decided, when applicable.
        prev_hash: ``record_hash`` of the previous row (``GENESIS_HASH`` first).
        record_hash: SHA-256 over the row fields plus ``prev_hash``.
    """

    seq: int
    ts: float
    tenant_id: str
    actor: str
    action: str
    correlation_id: str
    decision: str
    before: Mapping[str, Any] | None = None
    after: Mapping[str, Any] | None = None
    rule_id: str | None = None
    prev_hash: str = ""
    record_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready dict of this row (used for persistence and export)."""
        return {
            "seq": self.seq,
            "ts": self.ts,
            "tenant_id": self.tenant_id,
            "actor": self.actor,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "decision": self.decision,
            "before": dict(self.before) if self.before is not None else None,
            "after": dict(self.after) if self.after is not None else None,
            "rule_id": self.rule_id,
            "prev_hash": self.prev_hash,
            "record_hash": self.record_hash,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AuditRecord:
        """Rebuild a row from JSON, preserving the stored hashes verbatim."""
        return cls(
            seq=int(payload["seq"]),
            ts=float(payload["ts"]),
            tenant_id=str(payload["tenant_id"]),
            actor=str(payload["actor"]),
            action=str(payload["action"]),
            correlation_id=str(payload["correlation_id"]),
            decision=str(payload["decision"]),
            before=payload.get("before"),
            after=payload.get("after"),
            rule_id=payload.get("rule_id"),
            prev_hash=str(payload.get("prev_hash", "")),
            record_hash=str(payload.get("record_hash", "")),
        )


class AuditLog:
    """An append-only, hash-chained action log, optionally file-backed.

    Args:
        path: JSONL file to append to and load from. ``None`` keeps the log
            in memory (useful in tests and for per-run logs).
        clock: callable returning epoch seconds. Injected so tests are
            deterministic; production uses ``time.time``.
    """

    def __init__(self, path: str | Path | None = None, *, clock: Callable[[], float] = time.time) -> None:
        self.path = Path(path) if path is not None else None
        self.clock = clock
        self._records: list[AuditRecord] = []
        self._attempts: list[str] = []
        if self.path is not None and self.path.exists():
            self._load()

    def _load(self) -> None:
        assert self.path is not None
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    self._records.append(AuditRecord.from_dict(json.loads(line)))

    def append(
        self,
        *,
        tenant_id: str,
        actor: str,
        action: str,
        correlation_id: str,
        decision: str,
        before: Mapping[str, Any] | None = None,
        after: Mapping[str, Any] | None = None,
        rule_id: str | None = None,
    ) -> AuditRecord:
        """Append one row and return it.

        Contract:
            - ``decision`` must be ``"allowed"`` or ``"denied"`` (``ValueError``);
            - ``seq`` is ``len(records) + 1``; ``ts`` comes from ``clock()``;
            - ``prev_hash`` is the previous row's ``record_hash`` (or
              ``GENESIS_HASH`` for the first row); ``record_hash`` is computed
              over the canonical row including ``prev_hash``;
            - when ``path`` is set, the JSON line is flushed immediately;
            - the returned row is immutable (frozen dataclass).
        """
        if decision not in _DECISIONS:
            raise ValueError(f"audit decision must be one of {sorted(_DECISIONS)}, got {decision!r}")
        seq = len(self._records) + 1
        prev_hash = self._records[-1].record_hash if self._records else GENESIS_HASH
        fields: dict[str, Any] = {
            "seq": seq,
            "ts": float(self.clock()),
            "tenant_id": tenant_id,
            "actor": actor,
            "action": action,
            "correlation_id": correlation_id,
            "decision": decision,
            "before": dict(before) if before is not None else None,
            "after": dict(after) if after is not None else None,
            "rule_id": rule_id,
            "prev_hash": prev_hash,
        }
        record = AuditRecord(**fields, record_hash=_record_hash(**fields))
        self._records.append(record)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
                handle.flush()
        return record

    def records(self) -> list[AuditRecord]:
        """Return a copy of the rows in append order."""
        return list(self._records)

    def find(self, correlation_id: str) -> list[AuditRecord]:
        """Return rows matching ``correlation_id``, in append order."""
        return [record for record in self._records if record.correlation_id == correlation_id]

    def attempts(self) -> list[str]:
        """Return the rejected mutation attempts, oldest first, as log lines."""
        return list(self._attempts)

    def update(self, seq: int, **changes: Any) -> None:
        """Always raise ``AuditViolation``; record the attempt; change nothing."""
        self._attempts.append(
            f"update seq={seq} changes={sorted(changes)} rejected: audit log is append-only"
        )
        raise AuditViolation("audit log is append-only: UPDATE is rejected")

    def delete(self, seq: int) -> None:
        """Always raise ``AuditViolation``; record the attempt; change nothing."""
        self._attempts.append(f"delete seq={seq} rejected: audit log is append-only")
        raise AuditViolation("audit log is append-only: DELETE is rejected")

    def verify_integrity(self) -> bool:
        """Return whether the loaded rows form an intact hash chain.

        Checks: ``seq`` starts at 1 and increments by one; each ``prev_hash``
        equals the previous ``record_hash`` (``GENESIS_HASH`` first); each stored
        ``record_hash`` equals the hash recomputed from the row fields.
        """
        previous = GENESIS_HASH
        for expected_seq, record in enumerate(self._records, start=1):
            if record.seq != expected_seq:
                return False
            if record.prev_hash != previous:
                return False
            fields = {
                "seq": record.seq,
                "ts": record.ts,
                "tenant_id": record.tenant_id,
                "actor": record.actor,
                "action": record.action,
                "correlation_id": record.correlation_id,
                "decision": record.decision,
                "before": dict(record.before) if record.before is not None else None,
                "after": dict(record.after) if record.after is not None else None,
                "rule_id": record.rule_id,
                "prev_hash": record.prev_hash,
            }
            if record.record_hash != _record_hash(**fields):
                return False
            previous = record.record_hash
        return True
