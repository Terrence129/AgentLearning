"""Tests for working/episodic/semantic memory with provenance and policy (week 4)."""

from __future__ import annotations

import pytest
from agentlab.context.memory import (
    EpisodicMemory,
    MemoryKind,
    MemoryPolicy,
    MemoryPolicyViolation,
    Provenance,
    SemanticMemory,
    WorkingMemory,
)

pytestmark = pytest.mark.week


def provenance(source: str = "run:test-1") -> Provenance:
    return Provenance(source=source, run_id="test-1", actor="agent:researcher")


def test_semantic_memory_remembers_and_recalls_an_active_fact() -> None:
    memory = SemanticMemory()
    record = memory.remember(
        "discount.ceiling",
        "The maximum discount for enterprise deals is 10 percent.",
        provenance=provenance(),
    )

    assert record.kind is MemoryKind.SEMANTIC
    assert record.version == 1
    assert record.active
    assert record.record_id
    assert record.provenance.source == "run:test-1"
    assert memory.recall("discount.ceiling").record_id == record.record_id
    assert [fact.record_id for fact in memory.facts()] == [record.record_id]
    assert memory.recall("missing") is None


def test_reasserting_the_same_fact_is_idempotent() -> None:
    memory = SemanticMemory()
    first = memory.remember(
        "discount.ceiling",
        "The maximum discount for enterprise deals is 10 percent.",
        provenance=provenance(),
    )
    second = memory.remember(
        "discount.ceiling",
        "The maximum discount for enterprise deals is 10 percent.",
        provenance=provenance("run:test-2"),
    )

    assert second.record_id == first.record_id
    assert len(memory.history("discount.ceiling")) == 1
    assert len(memory.facts()) == 1


def test_contradicting_fact_supersedes_but_keeps_history() -> None:
    memory = SemanticMemory()
    old = memory.remember(
        "discount.ceiling",
        "The maximum discount for enterprise deals is 10 percent.",
        provenance=provenance(),
    )
    new = memory.remember(
        "discount.ceiling",
        "The maximum discount for enterprise deals is 20 percent.",
        provenance=provenance("run:test-2"),
    )

    assert new.version == 2
    assert memory.recall("discount.ceiling").record_id == new.record_id
    assert old.active is False
    assert old.superseded_by == new.record_id
    assert [record.version for record in memory.history("discount.ceiling")] == [1, 2]
    assert [fact.record_id for fact in memory.facts()] == [new.record_id]


def test_consolidation_merges_duplicate_facts_across_keys() -> None:
    memory = SemanticMemory()
    high = memory.remember(
        "policy.refund",
        "Refunds are allowed within 30 days of purchase.",
        provenance=provenance(),
        confidence=0.9,
    )
    low = memory.remember(
        "faq.refund",
        "Refunds are allowed within 30 days of purchase.",
        provenance=provenance("doc:faq"),
        confidence=0.4,
    )

    report = memory.consolidate()

    assert set(report.merged) == {low.record_id}
    assert high.record_id in report.kept
    assert [fact.record_id for fact in memory.facts()] == [high.record_id]
    low_record = memory.history("faq.refund")[0]
    assert low_record.active is False


def test_memory_policy_rejects_email_pii() -> None:
    memory = SemanticMemory()
    with pytest.raises(MemoryPolicyViolation, match="forbidden"):
        memory.remember(
            "contact",
            "Ask alice@example.com about the enterprise contract renewal.",
            provenance=provenance(),
        )
    assert memory.facts() == []


def test_memory_policy_rejects_api_key_like_secrets() -> None:
    memory = SemanticMemory()
    with pytest.raises(MemoryPolicyViolation, match="forbidden"):
        memory.remember(
            "provider.key",
            "Use sk-abcdef123456789 for the provider call.",
            provenance=provenance(),
        )


def test_memory_policy_requires_provenance_source() -> None:
    memory = SemanticMemory()
    with pytest.raises(MemoryPolicyViolation, match="provenance"):
        memory.remember(
            "fact",
            "The refund window is thirty days for enterprise contracts.",
            provenance=Provenance(source=""),
        )


def test_memory_policy_rejects_too_short_and_wrong_kind() -> None:
    memory = SemanticMemory()
    with pytest.raises(MemoryPolicyViolation, match="short"):
        memory.remember("fact", "ok", provenance=provenance())

    episodic_only = SemanticMemory(policy=MemoryPolicy(allowed_kinds=frozenset({MemoryKind.EPISODIC})))
    with pytest.raises(MemoryPolicyViolation, match="kind"):
        episodic_only.remember(
            "fact",
            "The refund window is thirty days for enterprise contracts.",
            provenance=provenance(),
        )


def test_erase_removes_facts_and_keeps_an_audit_entry() -> None:
    memory = SemanticMemory()
    memory.remember(
        "customer.email",
        "The contact for the enterprise deal is on the CRM record.",
        provenance=provenance(),
    )

    erased = memory.erase("customer.email", actor="dpo:alice")

    assert erased == 1
    assert memory.recall("customer.email") is None
    assert memory.history("customer.email") == []
    assert memory.facts() == []
    entry = memory.audit[-1]
    assert entry.action == "erase"
    assert entry.key == "customer.email"
    assert entry.actor == "dpo:alice"
    assert len(entry.record_ids) == 1


def test_confidence_outside_unit_interval_is_rejected() -> None:
    memory = SemanticMemory()
    with pytest.raises(ValueError):
        memory.remember(
            "fact",
            "The refund window is thirty days for enterprise contracts.",
            provenance=provenance(),
            confidence=1.5,
        )


def test_episodic_memory_records_runs_newest_first() -> None:
    memory = EpisodicMemory()
    first = memory.record_run(
        "run-1",
        "Researched refund policy; found a 30-day window.",
        provenance=provenance("run:run-1"),
    )
    second = memory.record_run(
        "run-2",
        "Compared discount options for the enterprise deal.",
        provenance=provenance("run:run-2"),
    )

    assert first.kind is MemoryKind.EPISODIC
    assert memory.for_run("run-1").record_id == first.record_id
    assert [record.record_id for record in memory.recent(5)] == [
        second.record_id,
        first.record_id,
    ]
    with pytest.raises(ValueError, match="already"):
        memory.record_run("run-1", "duplicate", provenance=provenance())


def test_episodic_memory_forget_run_is_audited() -> None:
    memory = EpisodicMemory()
    memory.record_run("run-1", "Researched refund policy.", provenance=provenance("run:run-1"))

    assert memory.forget_run("run-1", actor="operator:bob") is True
    assert memory.for_run("run-1") is None
    assert memory.forget_run("run-1") is False
    assert memory.audit[-1].action == "forget"
    assert memory.audit[-1].actor == "operator:bob"


def test_working_memory_is_bounded_and_preserves_state_on_overflow() -> None:
    scratchpad = WorkingMemory(max_chars=20)
    scratchpad.put("a", "12345")
    scratchpad.put("b", "1234567890")
    usage = scratchpad.usage_chars

    with pytest.raises(MemoryPolicyViolation, match="scratchpad"):
        scratchpad.put("c", "123456789012345")

    assert scratchpad.get("c") is None
    assert scratchpad.usage_chars == usage


def test_working_memory_replaces_deletes_and_clears() -> None:
    scratchpad = WorkingMemory(max_chars=100)
    scratchpad.put("plan", "research refund policy")
    scratchpad.put("plan", "short")
    assert scratchpad.usage_chars == len("plan") + len("short")
    assert scratchpad.get("plan") == "short"

    assert scratchpad.delete("plan") is True
    assert scratchpad.delete("plan") is False
    assert scratchpad.items() == {}

    scratchpad.put("x", "1")
    scratchpad.clear()
    assert scratchpad.items() == {}
