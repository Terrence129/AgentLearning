# Week 4 — Context engineering and memory

> **Lab id:** `week04-context-memory` · **Owned package:** `agentlab/context/`
> **Starter:** the files in `agentlab/context/` (they raise `NotImplementedError`)
> **Reference:** `solutions/week04/agentlab/context/` (copy it in only after trying)
> **Tests:** `tests/week04/`

## 1. Why this week exists

A model has no memory: the prompt *is* the agent's world this turn, and it gets
worse as it grows — context rot degrades accuracy with input length, and a single
distractor is enough to hurt (see
[`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §3.1).
This week you build the two mechanisms that let a long task survive: a
**priority-aware budget** that never evicts pinned constraints, and a
**compaction** pass that replaces old transcript with a bounded carry-forward
summary. You then build the memory substrate — from-scratch retrieval, episodic
events, semantic facts with provenance — so state can live outside the window.

Without this week, a 20-turn task either overflows the provider limit or quietly
forgets the one constraint that mattered ("never refund above $500").

## 2. Prerequisites & time budget

- **Time:** 10–12 h (plan: build ≈ 7 h, reading ≈ 2 h, review ≈ 2 h).
- **Must be green before starting:** `.\tasks.ps1 test` (Windows) / `./tasks.sh test` (macOS/Linux) — the provided foundation.
- **Reading:** `docs/research/01-agent-architecture-sota.md` §3 and §4 (read
  §3.1 twice), plus the Anthropic context-management article linked there.
- **Python:** standard library only — no numpy, no embeddings API, no network.
  `numpy` is an optional extra in `pyproject.toml`; this lab deliberately does
  not need it.

## 3. The spec

Implement every `NotImplementedError` in `agentlab/context/`. Docstrings are the
contract; the tests are the proof.

| File | Public surface | Contract summary |
|---|---|---|
| `window.py` | `Priority`, `ContextItem`, `TokenEstimator`, `WindowPolicy`, `ContextWindow`, `AssembledContext`, `ContextBudgetError` | Deterministic ~4-chars/token estimate with per-message overhead. Assemble under `input_budget = max_tokens - reserve_output_tokens`: PINNED always included, then TASK_STATE, RECENT_TURNS, OBSERVATIONS, HISTORY; newer wins inside a class; selected messages keep insertion order. Duplicate item ids are rejected. Pinned-over-budget is reported (`over_budget`), never silently dropped. |
| `compaction.py` | `Summarizer` (protocol), `CompactionPolicy`, `Compactor`, `CompactionResult`, `CARRY_FORWARD_ITEM_ID` | `should_compact` compares estimated tokens to the policy budget. `compact(items, objective=...)`: pinned items always survive; last `keep_recent_items` survive verbatim; older tool observations are replaced by a placeholder *before* summarisation; the injected summariser is called at most once with the older items and the objective; the carry-forward note is prefixed with the objective and hard-truncated to `max_summary_tokens`; invalid policies raise `ContextBudgetError`. |
| `retrieval.py` | `tokenize`, `HashingEmbedder`, `cosine_similarity`, `chunk_text`, `Chunk`, `SearchHit`, `SqliteVectorStore`, `VectorIndex`, `Embedder` | `[a-z0-9]+` tokenizer; deterministic signed hashing embedder (blake2b, unit-norm, zero vector for no tokens); cosine with zero-vector and dimension-error policy; word-preserving overlapping chunks each ≤ `max_chars`; sqlite store with a recorded dimension (reopen with a different dim raises), duplicate-id and wrong-length rejection, exact top-k search sorted by score then chunk id; `VectorIndex` re-indexing replaces a document. |
| `memory.py` | `MemoryKind`, `Provenance`, `MemoryRecord`, `AuditEntry`, `ConsolidationReport`, `MemoryPolicy`, `MemoryPolicyViolation`, `WorkingMemory`, `EpisodicMemory`, `SemanticMemory` | Working memory is bounded and run-scoped. Episodic memory is append-only (one summary per run) with audited forget. Semantic memory requires provenance, is idempotent for identical content, supersedes on contradiction (old version stays in history), consolidates duplicate facts across keys, and supports audited erase (the memory kill-switch). `MemoryPolicy` rejects short content, missing provenance, emails / API-key-shaped secrets / SSNs, and unlisted kinds. |

`ContextItem.to_message()` must produce the provided `agentlab.types.Message`
shape; tool items use `Message.tool_result(...)` so the provider tool-call link
survives.

## 4. Acceptance criteria

```powershell
# Windows (PowerShell)
# 1. starter is red (it should fail loudly with NotImplementedError)
.\.venv\Scripts\python.exe -m pytest tests/week04 -m week -q

# 2. implement, then re-run until green
.\.venv\Scripts\python.exe -m pytest tests/week04 -m week -q

# 3. lint (line length 110)
.\.venv\Scripts\ruff.exe check agentlab/context tests/week04

# 4. the foundation must stay green
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
# 1. starter is red (it should fail loudly with NotImplementedError)
uv run pytest tests/week04 -m week -q

# 2. implement, then re-run until green
uv run pytest tests/week04 -m week -q

# 3. lint (line length 110)
uv run ruff check agentlab/context tests/week04

# 4. the foundation must stay green
uv run pytest -q
```

Optional (the week's lab deliverable, described in the learning plan): run a
20-turn research task through a small driver under a 12k input-token budget,
record before/after cost, and show that ≥ 90% of pinned constraints survive every
compaction. Keep the driver local — do not edit `tests/week04/` to host it.

## 5. Hints (progressive)

1. **Re-read the contracts.** `window.ContextWindow.assemble` and
   `Compactor.compact` docstrings fully specify ordering and error behaviour;
   implement exactly that before optimising anything.
2. Token arithmetic: tests never hardcode fake budgets for items whose size is
   hard to predict — they compute with `TokenEstimator`. Use the estimator to
   check your own arithmetic instead of counting characters by hand.
3. Compaction ordering is the subtle part: pinned first, then the carry-forward
   system item, then the recent tail. `summarized_ids` is the *older* set only.
4. Bounding the summary: when the note is too long, truncate at
   `max_tokens * CHARS_PER_TOKEN` characters and append `"..."`, reserving the
   three characters so the estimator still lands within the bound.
5. For retrieval, `struct`/`json` both work for storing vectors; readability wins
   in this lab. Always sort search results with a total order (`-score, chunk_id`)
   or ties will flap between runs.
6. `SemanticMemory.remember` returns the *existing* record for an identical
   re-assertion — do not bump the version. Tests distinguish idempotent
   re-assertion from contradiction.
7. Do not import `agentlab.loop`; this week must be green independently.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| `ContextBudgetError: reserve_output_tokens ... leaves no input budget` | You validated `max_tokens` against `reserve_output_tokens` after subtracting, or forgot that `input_budget` is a property with validation. |
| A pinned item is missing from the assembled messages | You filtered/reordered selected items instead of selecting by priority and then emitting in insertion order. `included_ids` should read like the original sequence. |
| Compaction output is *larger* than the input | The fake/real summariser's reply is unbounded, or the summary is placed before pinned items and you forgot to drop the older items entirely. |
| `sqlite3.IntegrityError` escapes `store.add` | The store converts duplicate chunk ids into `ValueError`; check `VectorIndex.index_document` deletes the document before re-adding. |
| `MemoryPolicyViolation` for legit-looking text | The default forbidden patterns are broad on purpose (email / `sk-...` / SSN). Pass the policy explicitly to test a narrower tenant policy. |
| `test_compaction...` sees `summarized_ids` include a recent item | `keep_recent_items` counts *non-pinned* items; slicing `items[-n:]` on the full list is wrong. |

## 7. SendOS bridge

Read (30 min, read-only): `Send.Context.Gateway`, the "least-context envelope"
type (`SpecialistContext`), and the semantic retriever + pgvector adapter in the
SendOS repo. Cross-reference
[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)
§3 topics 8/14 and §4.1. Their guarantee is **data minimisation**, not maximal
recall — a different objective from a chatbot's "remember everything".

Answer in your lab notes:

1. Which fields does `SpecialistContext` carry, and which of them would this
   week's `ContextEnvelope` place in `facts` vs `references`?
2. Where does SendOS decide what context a specialist may see — at plan time, at
   dispatch time, or in the gateway — and what is the failure mode if that
   decision is silently widened?
3. The pgvector adapter is "one real provider" behind an interface. Which parts
   of this week's `Embedder`/`SqliteVectorStore` seam would survive a swap to
   pgvector unchanged, and which would not?

## 8. Stretch (optional)

1. **Real embedder comparison.** Add an `Embedder` implementation backed by a
   real embedding API (behind an env var, no network in tests) and compare
   recall@k with the hashing baseline on 20 hand-labelled queries. Report where
   hashing fails — it should be phrases with no shared vocabulary.
2. **Poisoned context defence.** Add a `ContextItem` class for untrusted content
   and a policy that marks it `UNTRUSTED` (below OBSERVATIONS); prove a planted
   "ignore previous instructions" fact can be evicted while pinned constraints
   survive.

## 9. Reflection (weekly review)

1. **Conceptual:** why is "summarise everything" a worse default than "clear
   tool results first"? What property of summaries makes numbers and constraints
   risky to keep only in prose?
2. **Architectural:** if you had to pick between a bigger context window and
   better retrieval for a 100-turn enterprise task, what evidence would you
   collect before deciding — and which of this week's mechanisms would you keep
   either way?
3. **Transfer:** which part of SendOS would you change first if you owned
   `Send.Context.Gateway`, and what would you measure to prove the change is an
   improvement?
