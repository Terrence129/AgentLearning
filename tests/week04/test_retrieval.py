"""Tests for from-scratch retrieval: hashing embeddings, cosine, sqlite store (week 4)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from agentlab.context.retrieval import (
    Chunk,
    HashingEmbedder,
    SqliteVectorStore,
    VectorIndex,
    chunk_text,
    cosine_similarity,
    tokenize,
)

pytestmark = pytest.mark.week


def test_tokenize_lowercases_and_keeps_alphanumeric_runs() -> None:
    assert tokenize("Refund POLICY, v2.1!") == ["refund", "policy", "v2", "1"]
    assert tokenize("   ") == []


def test_hashing_embedder_is_deterministic_and_has_fixed_width() -> None:
    first = HashingEmbedder(dim=64)
    second = HashingEmbedder(dim=64)
    vector = first.embed("enterprise refund policy")
    assert first.dim == 64
    assert len(vector) == 64
    assert vector == second.embed("enterprise refund policy")
    assert any(value != 0.0 for value in vector)


def test_hashing_embedder_returns_unit_vectors() -> None:
    embedder = HashingEmbedder(dim=128)
    vector = embedder.embed("annual contract refund policy")
    norm = math.sqrt(sum(value * value for value in vector))
    assert norm == pytest.approx(1.0, abs=1e-9)


def test_hashing_embedder_maps_empty_text_to_zero_vector() -> None:
    embedder = HashingEmbedder(dim=32)
    assert embedder.embed("!!! ???") == [0.0] * 32


def test_cosine_similarity_identity_orthogonality_and_zero_vectors() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([0.0, 1.0], [1.0, 0.0]) == pytest.approx(0.0)
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0
    with pytest.raises(ValueError):
        cosine_similarity([1.0], [1.0, 2.0])


def test_similar_texts_score_higher_than_unrelated_texts() -> None:
    embedder = HashingEmbedder(dim=256)
    a = embedder.embed("enterprise refund policy for annual contracts")
    b = embedder.embed("annual contracts enterprise refund policy")
    c = embedder.embed("singapore weather rain forecast")

    assert cosine_similarity(a, b) > cosine_similarity(a, c)
    assert cosine_similarity(a, c) < 0.5


def test_chunk_text_is_size_bounded_and_ordered() -> None:
    text = " ".join(f"token{i}" for i in range(300))
    chunks = chunk_text(text, doc_id="doc-1", max_chars=120, overlap_chars=40)

    assert len(chunks) > 1
    assert [chunk.ordinal for chunk in chunks] == list(range(len(chunks)))
    assert [chunk.chunk_id for chunk in chunks] == [f"doc-1#{i}" for i in range(len(chunks))]
    assert all(0 < len(chunk.text) <= 120 for chunk in chunks)
    assert all(chunk.doc_id == "doc-1" for chunk in chunks)
    assert chunks[0].text.split()[0] == "token0"
    assert chunks[-1].text.split()[-1] == "token299"


def test_chunk_text_handles_empty_text_and_bad_params() -> None:
    assert chunk_text("   \n\t ", doc_id="empty") == []
    with pytest.raises(ValueError):
        chunk_text("some text", doc_id="d", max_chars=0)
    with pytest.raises(ValueError):
        chunk_text("some text", doc_id="d", max_chars=100, overlap_chars=100)
    with pytest.raises(ValueError):
        chunk_text("some text", doc_id="d", max_chars=100, overlap_chars=-1)


def test_sqlite_store_roundtrips_chunks(tmp_path: Path) -> None:
    store = SqliteVectorStore(tmp_path / "vectors.db", dim=8)
    chunk = Chunk(chunk_id="doc#0", doc_id="doc", ordinal=0, text="refund policy")
    store.add(chunk, [1.0] + [0.0] * 7)

    assert store.count() == 1
    assert store.get("doc#0") == chunk
    assert store.get("missing") is None
    store.close()


def test_sqlite_store_rejects_duplicate_ids_and_wrong_dimensions(tmp_path: Path) -> None:
    store = SqliteVectorStore(tmp_path / "vectors.db", dim=8)
    chunk = Chunk(chunk_id="doc#0", doc_id="doc", ordinal=0, text="refund policy")
    store.add(chunk, [1.0] + [0.0] * 7)

    with pytest.raises(ValueError):
        store.add(chunk, [1.0] + [0.0] * 7)
    with pytest.raises(ValueError):
        store.add(
            Chunk(chunk_id="doc#1", doc_id="doc", ordinal=1, text="other"),
            [1.0, 0.0],
        )
    store.close()


def test_sqlite_store_persists_across_reopen(tmp_path: Path) -> None:
    path = tmp_path / "vectors.db"
    embedder = HashingEmbedder(dim=64)

    with SqliteVectorStore(path, dim=64) as store:
        index = VectorIndex(embedder, store)
        index.index_document("policy", "Refund policy: refunds are available within thirty days.")

    with SqliteVectorStore(path, dim=64) as reopened:
        index = VectorIndex(embedder, reopened)
        hits = index.search("refund policy for enterprise contracts", k=3)

    assert len(hits) == 1
    assert hits[0].chunk.doc_id == "policy"
    assert hits[0].score > 0.0


def test_sqlite_store_reopen_with_different_dimension_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "vectors.db"
    SqliteVectorStore(path, dim=32).close()
    with pytest.raises(ValueError):
        SqliteVectorStore(path, dim=64)


def test_vector_index_returns_best_first_and_respects_k(tmp_path: Path) -> None:
    store = SqliteVectorStore(tmp_path / "vectors.db", dim=64)
    index = VectorIndex(HashingEmbedder(dim=64), store)
    index.index_document(
        "refund",
        "Refund policy: refunds are available within thirty days for enterprise contracts.",
    )
    index.index_document(
        "weather",
        "Singapore weather forecast: rain and thunderstorms are expected in the afternoon.",
    )
    index.index_document("shipping", "Shipping times depend on the destination country.")

    hits = index.search("enterprise refund policy", k=2)

    assert len(hits) == 2
    assert hits[0].chunk.doc_id == "refund"
    assert hits[0].score >= hits[1].score
    store.close()


def test_reindexing_a_document_replaces_its_chunks(tmp_path: Path) -> None:
    store = SqliteVectorStore(tmp_path / "vectors.db", dim=64)
    index = VectorIndex(HashingEmbedder(dim=64), store)

    first = index.index_document("policy", "Refund policy version one applies to all contracts.")
    second = index.index_document("policy", "Refund policy version two applies only to annual contracts.")

    assert first == second == 1
    assert index.count() == 1
    hits = index.search("refund policy", k=5)
    assert "version two" in hits[0].chunk.text
    store.close()


def test_delete_document_removes_only_that_document(tmp_path: Path) -> None:
    store = SqliteVectorStore(tmp_path / "vectors.db", dim=64)
    index = VectorIndex(HashingEmbedder(dim=64), store)
    index.index_document("keep", "Refund policy applies to enterprise contracts.")
    index.index_document("remove", "Shipping times depend on the destination country.")

    removed = index.delete_document("remove")

    assert removed == 1
    assert index.count() == 1
    remaining = index.search("refund policy", k=5)
    assert [hit.chunk.doc_id for hit in remaining] == ["keep"]
    store.close()


def test_search_requires_positive_k(tmp_path: Path) -> None:
    store = SqliteVectorStore(tmp_path / "vectors.db", dim=64)
    index = VectorIndex(HashingEmbedder(dim=64), store)
    with pytest.raises(ValueError):
        index.search("anything", k=0)
    store.close()
