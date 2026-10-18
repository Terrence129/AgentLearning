"""From-scratch retrieval: chunks, embeddings, cosine, a sqlite vector store (week 4).

Why this module exists
----------------------
Semantic memory is the part of "agent memory" that looks like retrieval: keep
facts/artifacts outside the context window and pull back the few that matter for
this turn. The vocabulary is small -- chunk, embed, cosine, index -- and the
mechanics are easy to treat as magic if you only ever call a vector database.
Building the boring version first (hashing embedder + brute-force cosine +
sqlite) shows exactly what a managed store buys you: recall quality from real
embeddings, approximate-nearest-neighbour speed, and filtering/ops features.

What breaks without it
----------------------
- An index that mixes documents: stale chunks keep surfacing after a document
  is updated or deleted.
- Non-deterministic embeddings make tests (and bug reports) unreproducible.
- Character chunking that splits mid-word or mid-entity produces chunks that
  match no query.
- Similarity that silently returns 0.0 for a dimension mismatch hides a real
  configuration bug until recall quality mysteriously drops.

Read first: docs/research/01-agent-architecture-sota.md §4 (retrieval and
consolidation), and the Anthropic context-management article linked there.

Deliberately *not* included: numpy, an external vector DB, or a real embedding
provider. ``pyproject.toml`` keeps numpy in the optional ``vector`` extra; this
module uses plain Python floats so the week's tests run on the base install.
``sqlite`` is in the standard library. Compare with pgvector in the lab README.

Public surface
--------------
``Chunk``             a piece of a document, with stable ids
``SearchHit``         a retrieved chunk plus its similarity score
``Embedder``          protocol for anything that maps text -> vectors
``HashingEmbedder``   deterministic, dependency-free signed hashing embedder
``tokenize``          the lowercasing word tokenizer used by the embedder
``cosine_similarity`` dependency-free cosine over plain float sequences
``chunk_text``        deterministic, size-bounded, overlapping chunker
``SqliteVectorStore`` persistent store: chunks + embeddings in sqlite
``VectorIndex``       embedder + store facade: index documents, search them
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

#: Default embedding width. Small on purpose: hashing collisions are part of the
#: lesson (a real embedder earns its keep by *semantic* similarity).
DEFAULT_DIM = 128


@dataclass(frozen=True, slots=True)
class Chunk:
    """One retrievable piece of a document.

    Attributes:
        chunk_id: stable id, ``"<doc_id>#<ordinal>"``.
        doc_id: the document this chunk came from.
        ordinal: 0-based position of the chunk within the document.
        text: the chunk content.
    """

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
    """Lowercase word tokens: runs of ``[a-z0-9]``.

    Punctuation is dropped so "refund." and "refund" hash identically.
    """
    raise NotImplementedError("Week 4 lab: implement tokenize")


class HashingEmbedder:
    """Deterministic signed-hashing embedder (a "feature hashing" baseline).

    Algorithm contract:
        - tokenize the text; for every token, hash it with ``hashlib.blake2b``
          (8-byte digest) and map the digest to one dimension;
        - add ``+1`` or ``-1`` to that dimension based on a sign bit of the digest
          (signed hashing reduces collision bias);
        - L2-normalise the vector so cosine is a plain dot product;
        - a text with no tokens maps to the all-zero vector.

    Properties the tests rely on:
        - deterministic across instances and processes (no ``hash()``);
        - unit norm for any non-empty token stream;
        - identical token bags produce identical vectors;
        - unrelated vocabulary produces near-orthogonal vectors.
    """

    def __init__(self, dim: int = DEFAULT_DIM) -> None:
        self._dim = dim

    @property
    def dim(self) -> int:
        """Vector width."""
        raise NotImplementedError("Week 4 lab: implement HashingEmbedder.dim")

    def embed(self, text: str) -> list[float]:
        """Embed one string.

        Raises:
            ValueError: if ``dim`` is not positive (checked on use so the lab
                keeps the constructor side-effect free).
        """
        raise NotImplementedError("Week 4 lab: implement HashingEmbedder.embed")


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity of two equal-length vectors.

    Contract:
        - returns 0.0 if either vector has zero norm (undefined angle);
        - result is clamped to ``[-1.0, 1.0]``;
        - raises ``ValueError`` when lengths differ.
    """
    raise NotImplementedError("Week 4 lab: implement cosine_similarity")


def chunk_text(
    text: str,
    *,
    doc_id: str,
    max_chars: int = 320,
    overlap_chars: int = 80,
) -> list[Chunk]:
    """Split a document into overlapping, size-bounded chunks.

    Contract:
        - whitespace-separated words are kept whole; a word longer than
          ``max_chars`` is hard-sliced (very rare, never loses data);
        - every chunk is non-empty and at most ``max_chars`` characters;
        - consecutive chunks overlap by roughly ``overlap_chars`` characters so
          a sentence spanning a boundary is retrievable from either side;
        - ``ordinal`` is 0-based and contiguous; ids are ``"<doc_id>#<ordinal>"``;
        - empty/whitespace-only text yields ``[]``;
        - raises ``ValueError`` when ``max_chars <= 0`` or
          ``overlap_chars`` is not in ``[0, max_chars)``.
    """
    raise NotImplementedError("Week 4 lab: implement chunk_text")


class SqliteVectorStore:
    """A tiny persistent vector store backed by ``sqlite3``.

    Schema contract (single table is enough):
        ``chunks(chunk_id TEXT PRIMARY KEY, doc_id TEXT, ordinal INT,
                 text TEXT, embedding TEXT, dim INT)``

    The embedding is serialised as JSON text so the database stays inspectable
    with any sqlite client -- a deliberate teaching trade-off (a production
    store would use a packed binary format).

    Contract:
        - the store records its dimension; opening the same file with a
          different dimension raises ``ValueError`` (silent truncation is worse);
        - ``add`` rejects duplicate chunk ids and wrong-length embeddings;
        - ``search`` computes exact cosine against every stored chunk, returning
          at most ``k`` hits sorted by descending score (ties broken by
          ``chunk_id`` so results are deterministic);
        - ``delete_document`` returns the number of chunks removed;
        - ``":memory:"`` is a valid path (used by fast tests);
        - ``close`` is idempotent and the store is a context manager.
    """

    def __init__(self, path: str | Path, *, dim: int) -> None:
        self._path = str(path)
        self._dim = dim

    @property
    def dim(self) -> int:
        """The embedding width this store accepts."""
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.dim")

    def add(self, chunk: Chunk, embedding: Sequence[float]) -> None:
        """Persist one chunk and its embedding."""
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.add")

    def get(self, chunk_id: str) -> Chunk | None:
        """Fetch one chunk by id, or ``None`` when absent."""
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.get")

    def count(self) -> int:
        """Number of stored chunks."""
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.count")

    def delete_document(self, doc_id: str) -> int:
        """Delete every chunk of a document; return how many were removed."""
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.delete_document")

    def search(self, embedding: Sequence[float], *, k: int = 3) -> list[SearchHit]:
        """Exact cosine search over all stored chunks.

        Raises:
            ValueError: for a wrong-length query embedding or ``k < 1``.
        """
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.search")

    def close(self) -> None:
        """Close the underlying connection (idempotent)."""
        raise NotImplementedError("Week 4 lab: implement SqliteVectorStore.close")

    def __enter__(self) -> SqliteVectorStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class VectorIndex:
    """Embedder + store facade: the API the rest of the agent should use.

    Contract:
        - ``index_document`` chunks the text, embeds every chunk and stores it;
          re-indexing a document *replaces* its old chunks (idempotent updates);
          returns the number of chunks indexed;
        - ``search`` embeds the query and returns the top-``k`` hits, best first;
        - ``delete_document`` removes all chunks of a document, returns count;
        - ``count`` is the number of stored chunks.
    """

    def __init__(self, embedder: Embedder, store: SqliteVectorStore) -> None:
        self.embedder = embedder
        self.store = store

    def index_document(self, doc_id: str, text: str, *, max_chars: int = 320, overlap_chars: int = 80) -> int:
        """Chunk, embed and persist a document; return the chunk count."""
        raise NotImplementedError("Week 4 lab: implement VectorIndex.index_document")

    def search(self, query: str, *, k: int = 3) -> list[SearchHit]:
        """Return the best chunks for a query."""
        raise NotImplementedError("Week 4 lab: implement VectorIndex.search")

    def delete_document(self, doc_id: str) -> int:
        """Remove a document's chunks; return the count."""
        raise NotImplementedError("Week 4 lab: implement VectorIndex.delete_document")

    def count(self) -> int:
        """Number of indexed chunks."""
        raise NotImplementedError("Week 4 lab: implement VectorIndex.count")
