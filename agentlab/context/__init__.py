"""Context engineering and memory (week 4).

The theme: context is a budget, not a bucket. Every token in the prompt must
earn its place against a measurable effect on task success.

Modules:
    window.py      token estimation, priority classes, budgeted assembly
    compaction.py  bounded carry-forward summaries and tool-output pruning
    retrieval.py   from-scratch chunking, hashing embeddings, cosine, sqlite
    memory.py      working / episodic / semantic memory, provenance, policy
"""

from __future__ import annotations

from agentlab.context.compaction import (
    CARRY_FORWARD_ITEM_ID,
    CompactionPolicy,
    CompactionResult,
    Compactor,
    Summarizer,
)
from agentlab.context.memory import (
    AuditEntry,
    ConsolidationReport,
    EpisodicMemory,
    MemoryKind,
    MemoryPolicy,
    MemoryPolicyViolation,
    MemoryRecord,
    Provenance,
    SemanticMemory,
    WorkingMemory,
)
from agentlab.context.retrieval import (
    DEFAULT_DIM,
    Chunk,
    Embedder,
    HashingEmbedder,
    SearchHit,
    SqliteVectorStore,
    VectorIndex,
    chunk_text,
    cosine_similarity,
    tokenize,
)
from agentlab.context.window import (
    CHARS_PER_TOKEN,
    MESSAGE_OVERHEAD_TOKENS,
    AssembledContext,
    ContextBudgetError,
    ContextItem,
    ContextWindow,
    Priority,
    TokenEstimator,
    WindowPolicy,
)

__all__ = [
    "CARRY_FORWARD_ITEM_ID",
    "CHARS_PER_TOKEN",
    "DEFAULT_DIM",
    "MESSAGE_OVERHEAD_TOKENS",
    "AssembledContext",
    "AuditEntry",
    "Chunk",
    "CompactionPolicy",
    "CompactionResult",
    "Compactor",
    "ConsolidationReport",
    "ContextBudgetError",
    "ContextItem",
    "ContextWindow",
    "Embedder",
    "EpisodicMemory",
    "HashingEmbedder",
    "MemoryKind",
    "MemoryPolicy",
    "MemoryPolicyViolation",
    "MemoryRecord",
    "Priority",
    "Provenance",
    "SearchHit",
    "SemanticMemory",
    "SqliteVectorStore",
    "Summarizer",
    "TokenEstimator",
    "VectorIndex",
    "WindowPolicy",
    "WorkingMemory",
    "chunk_text",
    "cosine_similarity",
    "tokenize",
]
