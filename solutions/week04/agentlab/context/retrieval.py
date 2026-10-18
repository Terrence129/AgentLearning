"""From-scratch retrieval: chunks, embeddings, cosine, a sqlite vector store (week 4).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

DEFAULT_DIM = 128

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True, slots=True)
class Chunk:
    """One retrievable piece of a document."""

    chunk_id: str
    doc_id: str
    ordinal: int
    text: str


@dataclass(frozen=True, slots=True)
class SearchHit:
    """A retrieved chunk and its similarity to the query (higher is better)."""

    chunk: Chunk
    score: float


class Embedder(Protocol):
    """Anything that maps text to a fixed-width vector."""

    @property
    def dim(self) -> int: ...

    def embed(self, text: str) -> list[float]: ...


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbedder:
    """Deterministic signed-hashing embedder (a "feature hashing" baseline)."""

    def __init__(self, dim: int = DEFAULT_DIM) -> None:
        if dim <= 0:
            raise ValueError(f"embedding dimension must be positive, got {dim}")
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dim
        for token in tokenize(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            hashed = int.from_bytes(digest, "big")
            index = hashed % self._dim
            sign = -1.0 if (hashed >> 63) & 1 else 1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} != {len(b)}")
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for left, right in zip(a, b, strict=True):
        dot += left * right
        norm_a += left * left
        norm_b += right * right
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    score = dot / (math.sqrt(norm_a) * math.sqrt(norm_b))
    return max(-1.0, min(1.0, score))


def _split_long_words(words: list[str], max_chars: int) -> list[str]:
    """Hard-slice any word longer than ``max_chars`` so every chunk can fit."""
    pieces: list[str] = []
    for word in words:
        if len(word) <= max_chars:
            pieces.append(word)
        else:
            pieces.extend(word[i : i + max_chars] for i in range(0, len(word), max_chars))
    return pieces


def chunk_text(
    text: str,
    *,
    doc_id: str,
    max_chars: int = 320,
    overlap_chars: int = 80,
) -> list[Chunk]:
    if max_chars <= 0:
        raise ValueError(f"max_chars must be positive, got {max_chars}")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError(f"overlap_chars must be in [0, max_chars), got {overlap_chars}")

    words = _split_long_words(text.split(), max_chars)
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    ordinal = 0
    while start < len(words):
        end = start
        length = 0
        while end < len(words):
            candidate = len(words[end]) if length == 0 else length + 1 + len(words[end])
            if candidate > max_chars:
                break
            length = candidate
            end += 1
        content = " ".join(words[start:end])
        chunks.append(Chunk(chunk_id=f"{doc_id}#{ordinal}", doc_id=doc_id, ordinal=ordinal, text=content))
        ordinal += 1
        if end >= len(words):
            break
        next_start = end
        overlap = 0
        while next_start - 1 > start:
            step = len(words[next_start - 1]) + (1 if overlap else 0)
            if overlap + step > overlap_chars:
                break
            next_start -= 1
            overlap += step
        start = max(next_start, start + 1)
    return chunks


class SqliteVectorStore:
    """A tiny persistent vector store backed by sqlite3."""

    def __init__(self, path: str | Path, *, dim: int) -> None:
        if dim <= 0:
            raise ValueError(f"embedding dimension must be positive, got {dim}")
        self._path = str(path)
        self._dim = dim
        connection = sqlite3.connect(self._path)
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    ordinal INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    dim INTEGER NOT NULL
                )
                """
            )
            connection.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            row = connection.execute("SELECT value FROM meta WHERE key = 'dim'").fetchone()
            if row is None:
                connection.execute("INSERT INTO meta (key, value) VALUES ('dim', ?)", (str(dim),))
            elif int(row[0]) != dim:
                raise ValueError(
                    f"vector store at {self._path!r} was created with dim={row[0]}, not dim={dim}"
                )
            connection.commit()
        except ValueError:
            connection.close()
            raise
        self._connection: sqlite3.Connection | None = connection

    def _conn(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("vector store is closed")
        return self._connection

    @property
    def dim(self) -> int:
        return self._dim

    def add(self, chunk: Chunk, embedding: Sequence[float]) -> None:
        if len(embedding) != self._dim:
            raise ValueError(
                f"embedding for {chunk.chunk_id!r} has dimension {len(embedding)}, expected {self._dim}"
            )
        payload = json.dumps([float(value) for value in embedding], separators=(",", ":"))
        try:
            self._conn().execute(
                "INSERT INTO chunks (chunk_id, doc_id, ordinal, text, embedding, dim) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (chunk.chunk_id, chunk.doc_id, chunk.ordinal, chunk.text, payload, self._dim),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"chunk {chunk.chunk_id!r} is already indexed") from exc
        self._conn().commit()

    def get(self, chunk_id: str) -> Chunk | None:
        row = (
            self._conn()
            .execute(
                "SELECT chunk_id, doc_id, ordinal, text FROM chunks WHERE chunk_id = ?",
                (chunk_id,),
            )
            .fetchone()
        )
        if row is None:
            return None
        return Chunk(chunk_id=row[0], doc_id=row[1], ordinal=row[2], text=row[3])

    def count(self) -> int:
        row = self._conn().execute("SELECT COUNT(*) FROM chunks").fetchone()
        return int(row[0])

    def delete_document(self, doc_id: str) -> int:
        cursor = self._conn().execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        self._conn().commit()
        return cursor.rowcount

    def search(self, embedding: Sequence[float], *, k: int = 3) -> list[SearchHit]:
        if k < 1:
            raise ValueError(f"k must be >= 1, got {k}")
        if len(embedding) != self._dim:
            raise ValueError(f"query embedding has dimension {len(embedding)}, expected {self._dim}")
        query = [float(value) for value in embedding]
        hits: list[SearchHit] = []
        rows = (
            self._conn()
            .execute("SELECT chunk_id, doc_id, ordinal, text, embedding FROM chunks ORDER BY chunk_id")
            .fetchall()
        )
        for chunk_id, doc_id, ordinal, text, payload in rows:
            stored = json.loads(payload)
            score = cosine_similarity(query, stored)
            hits.append(SearchHit(chunk=Chunk(chunk_id, doc_id, ordinal, text), score=score))
        hits.sort(key=lambda hit: (-hit.score, hit.chunk.chunk_id))
        return hits[:k]

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> SqliteVectorStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class VectorIndex:
    """Embedder + store facade: the API the rest of the agent should use."""

    def __init__(self, embedder: Embedder, store: SqliteVectorStore) -> None:
        self.embedder = embedder
        self.store = store

    def index_document(self, doc_id: str, text: str, *, max_chars: int = 320, overlap_chars: int = 80) -> int:
        chunks = chunk_text(text, doc_id=doc_id, max_chars=max_chars, overlap_chars=overlap_chars)
        self.store.delete_document(doc_id)
        for chunk in chunks:
            self.store.add(chunk, self.embedder.embed(chunk.text))
        return len(chunks)

    def search(self, query: str, *, k: int = 3) -> list[SearchHit]:
        if k < 1:
            raise ValueError(f"k must be >= 1, got {k}")
        return self.store.search(self.embedder.embed(query), k=k)

    def delete_document(self, doc_id: str) -> int:
        return self.store.delete_document(doc_id)

    def count(self) -> int:
        return self.store.count()
