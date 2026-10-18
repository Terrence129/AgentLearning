"""Memory: episodic events, semantic facts with provenance, a working scratchpad (week 4).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agentlab.errors import AgentError


class MemoryPolicyViolation(AgentError):
    """A memory write was refused by policy (PII, secret, missing provenance...)."""


class MemoryKind(StrEnum):
    """The three kinds of memory an agent uses."""

    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Where a memory came from. Required for anything durable."""

    source: str
    run_id: str | None = None
    actor: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MemoryRecord:
    """One stored memory."""

    record_id: str
    kind: MemoryKind
    key: str
    content: str
    provenance: Provenance
    confidence: float = 1.0
    tags: tuple[str, ...] = ()
    seq: int = 0
    version: int = 1
    superseded_by: str | None = None
    active: bool = True


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """One auditable memory operation (for the memory kill-switch)."""

    action: str
    key: str
    record_ids: tuple[str, ...]
    actor: str
    seq: int


@dataclass(frozen=True, slots=True)
class ConsolidationReport:
    """What one consolidation pass did."""

    merged: tuple[str, ...] = ()
    kept: tuple[str, ...] = ()
    forgotten: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MemoryPolicy:
    """The gate every durable memory write must pass."""

    min_content_chars: int = 8
    require_source: bool = True
    allowed_kinds: frozenset[MemoryKind] = field(default_factory=lambda: frozenset(MemoryKind))
    forbidden_patterns: tuple[str, ...] = (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        r"\bsk-[A-Za-z0-9_-]{8,}\b",
        r"\b\d{3}-\d{2}-\d{4}\b",
    )

    def check(self, kind: MemoryKind, content: str, provenance: Provenance) -> None:
        if kind not in self.allowed_kinds:
            raise MemoryPolicyViolation(f"memory kind {kind.value!r} is not allowed by policy")
        if self.require_source and not provenance.source.strip():
            raise MemoryPolicyViolation(
                "memory requires a non-blank provenance source: an unattributable fact is an unevidenced one"
            )
        if len(content.strip()) < self.min_content_chars:
            raise MemoryPolicyViolation(
                f"memory content is too short ({len(content.strip())} < "
                f"{self.min_content_chars} characters); do not store noise"
            )
        for pattern in self.forbidden_patterns:
            if re.search(pattern, content, flags=re.IGNORECASE):
                raise MemoryPolicyViolation(
                    f"memory content matches forbidden pattern {pattern!r}; refusing to store PII or secrets"
                )


class WorkingMemory:
    """A bounded, run-scoped scratchpad."""

    def __init__(self, *, max_chars: int = 2_000) -> None:
        if max_chars <= 0:
            raise ValueError(f"max_chars must be positive, got {max_chars}")
        self.max_chars = max_chars
        self._values: dict[str, str] = {}

    def _usage(self) -> int:
        return sum(len(key) + len(value) for key, value in self._values.items())

    def put(self, key: str, value: str) -> None:
        if not key.strip():
            raise ValueError("working memory key must not be blank")
        previous = self._values.get(key)
        old_cost = len(key) + len(previous) if previous is not None else 0
        new_usage = self._usage() - old_cost + len(key) + len(value)
        if new_usage > self.max_chars:
            raise MemoryPolicyViolation(
                f"working memory scratchpad would exceed {self.max_chars} chars "
                f"({new_usage}); erase something first"
            )
        self._values[key] = value

    def get(self, key: str) -> str | None:
        return self._values.get(key)

    def delete(self, key: str) -> bool:
        return self._values.pop(key, None) is not None

    def items(self) -> dict[str, str]:
        return dict(self._values)

    @property
    def usage_chars(self) -> int:
        return self._usage()

    def clear(self) -> None:
        self._values.clear()


class EpisodicMemory:
    """Append-only run summaries -- the agent's event log."""

    def __init__(self, policy: MemoryPolicy | None = None) -> None:
        self.policy = policy or MemoryPolicy()
        self.audit: list[AuditEntry] = []
        self._by_run: dict[str, MemoryRecord] = {}
        self._seq = 0

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def record_run(
        self,
        run_id: str,
        summary: str,
        *,
        provenance: Provenance,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
    ) -> MemoryRecord:
        if not run_id.strip():
            raise ValueError("run_id must not be blank")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {confidence}")
        if run_id in self._by_run:
            raise ValueError(f"run {run_id!r} is already recorded; episodic memory is append-only")
        self.policy.check(MemoryKind.EPISODIC, summary, provenance)
        seq = self._next_seq()
        record = MemoryRecord(
            record_id=f"episodic-{seq}",
            kind=MemoryKind.EPISODIC,
            key=run_id,
            content=summary,
            provenance=provenance,
            confidence=confidence,
            tags=tuple(tags),
            seq=seq,
        )
        self._by_run[run_id] = record
        return record

    def for_run(self, run_id: str) -> MemoryRecord | None:
        return self._by_run.get(run_id)

    def recent(self, limit: int = 5) -> list[MemoryRecord]:
        if limit < 0:
            raise ValueError(f"limit must be >= 0, got {limit}")
        ordered = sorted(self._by_run.values(), key=lambda record: record.seq, reverse=True)
        return ordered[:limit]

    def forget_run(self, run_id: str, *, actor: str = "operator") -> bool:
        record = self._by_run.pop(run_id, None)
        if record is None:
            return False
        seq = self._next_seq()
        self.audit.append(
            AuditEntry(
                action="forget",
                key=run_id,
                record_ids=(record.record_id,),
                actor=actor,
                seq=seq,
            )
        )
        return True


def _normalise(content: str) -> str:
    """Whitespace/case-insensitive form used for duplicate detection."""
    return " ".join(content.lower().split())


class SemanticMemory:
    """Versioned facts with provenance, supersession and consolidation."""

    def __init__(self, policy: MemoryPolicy | None = None) -> None:
        self.policy = policy or MemoryPolicy()
        self.audit: list[AuditEntry] = []
        self._records: dict[str, MemoryRecord] = {}
        self._active_by_key: dict[str, str] = {}
        self._seq = 0

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def remember(
        self,
        key: str,
        content: str,
        *,
        provenance: Provenance,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
    ) -> MemoryRecord:
        if not key.strip():
            raise ValueError("memory key must not be blank")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {confidence}")
        self.policy.check(MemoryKind.SEMANTIC, content, provenance)

        existing_id = self._active_by_key.get(key)
        if existing_id is not None:
            existing = self._records[existing_id]
            if _normalise(existing.content) == _normalise(content):
                return existing
            seq = self._next_seq()
            record = MemoryRecord(
                record_id=f"semantic-{seq}",
                kind=MemoryKind.SEMANTIC,
                key=key,
                content=content,
                provenance=provenance,
                confidence=confidence,
                tags=tuple(tags),
                seq=seq,
                version=existing.version + 1,
            )
            existing.active = False
            existing.superseded_by = record.record_id
            self._records[record.record_id] = record
            self._active_by_key[key] = record.record_id
            return record

        seq = self._next_seq()
        record = MemoryRecord(
            record_id=f"semantic-{seq}",
            kind=MemoryKind.SEMANTIC,
            key=key,
            content=content,
            provenance=provenance,
            confidence=confidence,
            tags=tuple(tags),
            seq=seq,
        )
        self._records[record.record_id] = record
        self._active_by_key[key] = record.record_id
        return record

    def recall(self, key: str) -> MemoryRecord | None:
        record_id = self._active_by_key.get(key)
        if record_id is None:
            return None
        record = self._records.get(record_id)
        if record is None or not record.active:
            return None
        return record

    def history(self, key: str) -> list[MemoryRecord]:
        records = [record for record in self._records.values() if record.key == key]
        return sorted(records, key=lambda record: record.version)

    def facts(self) -> list[MemoryRecord]:
        return [record for record in self._records.values() if record.active]

    def consolidate(self) -> ConsolidationReport:
        groups: dict[str, list[MemoryRecord]] = {}
        for record in self.facts():
            groups.setdefault(_normalise(record.content), []).append(record)

        merged: list[str] = []
        kept: list[str] = []
        for records in groups.values():
            winner = sorted(records, key=lambda record: (-record.confidence, record.seq))[0]
            kept.append(winner.record_id)
            for record in records:
                if record is winner:
                    continue
                record.active = False
                record.superseded_by = winner.record_id
                merged.append(record.record_id)
                if self._active_by_key.get(record.key) == record.record_id:
                    del self._active_by_key[record.key]
        return ConsolidationReport(merged=tuple(merged), kept=tuple(kept), forgotten=())

    def erase(self, key: str, *, actor: str = "operator") -> int:
        records = [record for record in self._records.values() if record.key == key]
        if not records:
            return 0
        record_ids = tuple(record.record_id for record in records)
        for record_id in record_ids:
            del self._records[record_id]
        self._active_by_key.pop(key, None)
        seq = self._next_seq()
        self.audit.append(AuditEntry(action="erase", key=key, record_ids=record_ids, actor=actor, seq=seq))
        return len(records)
