"""Memory: episodic events, semantic facts with provenance, a working scratchpad (week 4).

Why this module exists
----------------------
The context window is *working memory for one call*. A long-running agent needs
two other kinds, and conflating them is the most common "agent memory" mistake
(docs/research/01-agent-architecture-sota.md §4):

- **episodic memory** -- what happened: run summaries, decisions, failures. This
  is an append-only event log, not a retrieval index.
- **semantic memory** -- what is true: facts about the user/org/domain, each with
  provenance, confidence and a history. New information *supersedes* old facts
  instead of silently overwriting them.
- **working memory** -- the current scratchpad: bounded, run-scoped, erased.

What breaks without it
----------------------
- Facts with no provenance cannot be audited or deleted, so a wrong fact lives
  forever and a privacy request cannot be answered.
- Overwriting facts loses the audit trail; keeping every duplicate makes recall
  contradictory (Mem0's add/update/delete framing exists for exactly this).
- Storing everything (emails, API keys, regulated data) turns memory into a
  compliance incident. "When NOT to add memory" is a policy, not a footnote.
- An unbounded scratchpad is just the context-window overflow again.

Read first: docs/research/01-agent-architecture-sota.md §4 (especially
"Retrieval and consolidation" and "When NOT to build memory").

Public surface
--------------
``MemoryKind``          working | episodic | semantic
``Provenance``          where a memory came from (required for durable memory)
``MemoryRecord``        one stored memory with version/supersession fields
``AuditEntry``          an auditable memory operation (erase/forget)
``ConsolidationReport`` what a consolidation pass merged/kept/forgot
``MemoryPolicy``        the "what must never be remembered" gate
``MemoryPolicyViolation`` raised when a write is refused
``WorkingMemory``       bounded run-scoped scratchpad
``EpisodicMemory``      append-only run summaries
``SemanticMemory``      versioned facts with provenance and consolidation
"""

from __future__ import annotations

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
    """Where a memory came from. Required for anything durable.

    Attributes:
        source: a stable reference, e.g. ``"run:20261018T101500Z-ab12cd34"``,
            ``"doc:refund-policy#3"``, ``"user:alice"``.
        run_id: the agent run that produced it, when applicable.
        actor: who asserted it (``"agent:researcher"``, ``"user:alice"``).
        detail: free-form extras (tool, URL, trace seq...).
    """

    source: str
    run_id: str | None = None
    actor: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MemoryRecord:
    """One stored memory.

    Attributes:
        record_id: store-assigned unique id.
        kind: which memory kind this is.
        key: logical key (semantic memory uses it for supersession).
        content: the memory text.
        provenance: required origin information.
        confidence: 0.0-1.0; consolidation may prefer higher confidence.
        tags: small labels for filtering.
        seq: monotonically increasing insertion sequence (deterministic order).
        version: 1 for a new key, +1 per supersession.
        superseded_by: id of the record that replaced this one, if any.
        active: False once superseded/merged/forgotten.
    """

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
    """The gate every durable memory write must pass.

    This encodes "when NOT to add memory": if you cannot say what must never be
    remembered, you should not be writing memory yet. Defaults reject:

    - content shorter than ``min_content_chars`` (noise: "ok", "yes");
    - a missing/blank ``provenance.source`` (unattributable facts are unevidenced);
    - email addresses, OpenAI-style API keys and US SSNs (PII / secrets);
    - kinds outside ``allowed_kinds``.

    ``forbidden_patterns`` are regular expressions; the default set is
    deliberately small and documented -- extend it per tenant/regime.
    """

    min_content_chars: int = 8
    require_source: bool = True
    allowed_kinds: frozenset[MemoryKind] = field(default_factory=lambda: frozenset(MemoryKind))
    forbidden_patterns: tuple[str, ...] = (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # email
        r"\bsk-[A-Za-z0-9_-]{8,}\b",  # API key shaped secret
        r"\b\d{3}-\d{2}-\d{4}\b",  # US SSN
    )

    def check(self, kind: MemoryKind, content: str, provenance: Provenance) -> None:
        """Raise :class:`MemoryPolicyViolation` if the write must be refused.

        Contract: called by every durable-memory write path *before* storage, so
        a rejected write never leaves a partial record behind.
        """
        raise NotImplementedError("Week 4 lab: implement MemoryPolicy.check")


class WorkingMemory:
    """A bounded, run-scoped scratchpad.

    This is the only memory kind that is intentionally *not* provenance-gated:
    it lives for one run and is discarded. It is still bounded -- an unbounded
    scratchpad is the context overflow problem with extra steps.
    """

    def __init__(self, *, max_chars: int = 2_000) -> None:
        self.max_chars = max_chars
        self._values: dict[str, str] = {}

    def put(self, key: str, value: str) -> None:
        """Set a scratchpad value.

        Replacing an existing key counts only the new value's size.

        Raises:
            ValueError: for a blank key.
            MemoryPolicyViolation: if the total size would exceed ``max_chars``
                (the previous state is left intact).
        """
        raise NotImplementedError("Week 4 lab: implement WorkingMemory.put")

    def get(self, key: str) -> str | None:
        """Read a scratchpad value."""
        raise NotImplementedError("Week 4 lab: implement WorkingMemory.get")

    def delete(self, key: str) -> bool:
        """Delete a key; return True if it existed."""
        raise NotImplementedError("Week 4 lab: implement WorkingMemory.delete")

    def items(self) -> dict[str, str]:
        """A copy of the scratchpad (key -> value)."""
        raise NotImplementedError("Week 4 lab: implement WorkingMemory.items")

    @property
    def usage_chars(self) -> int:
        """Total characters currently stored (keys + values)."""
        raise NotImplementedError("Week 4 lab: implement WorkingMemory.usage_chars")

    def clear(self) -> None:
        """Drop all scratchpad values (end of run)."""
        raise NotImplementedError("Week 4 lab: implement WorkingMemory.clear")


class EpisodicMemory:
    """Append-only run summaries -- the agent's event log.

    One summary per ``run_id``: recording the same run twice raises ``ValueError``
    (idempotent recording is a caller concern; the store stays honest).
    """

    def __init__(self, policy: MemoryPolicy | None = None) -> None:
        self.policy = policy or MemoryPolicy()
        self.audit: list[AuditEntry] = []
        self._records: dict[str, MemoryRecord] = {}
        self._seq = 0

    def record_run(
        self,
        run_id: str,
        summary: str,
        *,
        provenance: Provenance,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
    ) -> MemoryRecord:
        """Record one run summary.

        Raises:
            MemoryPolicyViolation: via :meth:`MemoryPolicy.check`.
            ValueError: if ``run_id`` was already recorded, or ``run_id`` is blank.
        """
        raise NotImplementedError("Week 4 lab: implement EpisodicMemory.record_run")

    def for_run(self, run_id: str) -> MemoryRecord | None:
        """The summary recorded for a run, if any."""
        raise NotImplementedError("Week 4 lab: implement EpisodicMemory.for_run")

    def recent(self, limit: int = 5) -> list[MemoryRecord]:
        """The most recent run summaries, newest first (at most ``limit``)."""
        raise NotImplementedError("Week 4 lab: implement EpisodicMemory.recent")

    def forget_run(self, run_id: str, *, actor: str = "operator") -> bool:
        """Erase one run's summary and append an audit entry; return True if found."""
        raise NotImplementedError("Week 4 lab: implement EpisodicMemory.forget_run")


class SemanticMemory:
    """Versioned facts with provenance, supersession and consolidation.

    Write rules:
        - every write passes :meth:`MemoryPolicy.check` first;
        - a key's first fact gets ``version=1``;
        - re-asserting the *same* content for the same key is idempotent (the
          existing record is returned unchanged -- one fact, one provenance);
        - a *different* content for the same key supersedes the old record: the
          old record stays in history with ``active=False`` and
          ``superseded_by`` pointing at the new one.

    Consolidation:
        - duplicate active facts with identical normalised content but different
          keys are merged into the earliest (highest-confidence) record; the
          others become inactive and are reported in ``ConsolidationReport.merged``.
        - ``erase`` is the memory kill-switch: records are removed, but an
          :class:`AuditEntry` (with the removed record ids) is kept so deletion
          is traceable.
    """

    def __init__(self, policy: MemoryPolicy | None = None) -> None:
        self.policy = policy or MemoryPolicy()
        self.audit: list[AuditEntry] = []
        self._records: dict[str, MemoryRecord] = {}
        self._active_by_key: dict[str, str] = {}
        self._seq = 0

    def remember(
        self,
        key: str,
        content: str,
        *,
        provenance: Provenance,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
    ) -> MemoryRecord:
        """Remember a fact under ``key`` (see class docstring for rules).

        Raises:
            MemoryPolicyViolation: via :meth:`MemoryPolicy.check`.
            ValueError: for a blank key or confidence outside ``[0, 1]``.
        """
        raise NotImplementedError("Week 4 lab: implement SemanticMemory.remember")

    def recall(self, key: str) -> MemoryRecord | None:
        """The active fact for a key, if any."""
        raise NotImplementedError("Week 4 lab: implement SemanticMemory.recall")

    def history(self, key: str) -> list[MemoryRecord]:
        """Every version ever stored for a key, oldest first."""
        raise NotImplementedError("Week 4 lab: implement SemanticMemory.history")

    def facts(self) -> list[MemoryRecord]:
        """All active facts, in insertion order."""
        raise NotImplementedError("Week 4 lab: implement SemanticMemory.facts")

    def consolidate(self) -> ConsolidationReport:
        """Merge duplicate active facts; return the report."""
        raise NotImplementedError("Week 4 lab: implement SemanticMemory.consolidate")

    def erase(self, key: str, *, actor: str = "operator") -> int:
        """Delete every record for a key and append an audit entry; return count."""
        raise NotImplementedError("Week 4 lab: implement SemanticMemory.erase")
