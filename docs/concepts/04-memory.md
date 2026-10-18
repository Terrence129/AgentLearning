# 04 — Memory

> **Week 4 · just-in-time concept note.** Read after [03 — Context Engineering](./03-context-engineering.md), before the [context & memory lab](../../labs/week04-context-memory/README.md) (~25 min). Context engineering keeps one run coherent; memory is what survives between runs — and it is the feature most often built before it is understood.

## The failure mode this prevents

The agent that remembers the wrong thing. A semantic store picks up "enterprise discount cap is 25%" from a March call; the policy changes in June; in August the agent recalls the fact confidently and proposes a 25% discount. A human approver catches it — or does not. The mirror-image failure is the agent that remembers nothing: every session re-asks for the account ID, the order number, the constraint the customer already stated. And the most expensive failure is the memory project that never pays off: a vector database bolted on, six weeks of work, no measurable lift — because nobody built a cross-session eval, so nobody could tell whether recall helped or just added tokens and staleness.

Memory done well is narrow, explicit and governed: four kinds with different schemas, provenance on every fact, consolidation that prefers appending over rewriting, and a clear answer to *when not to build it*.

## If you remember five things

> 1. **Four kinds, four designs.** Working (the window), episodic (what happened — append-only trace), semantic (facts with provenance), procedural (how to do things — versioned assets/skills). Conflating them is the root design error.
> 2. **Memory is a policy plus a tool surface, not a vector database.** MemGPT's paging, Letta's memory blocks and Anthropic's memory tool are three versions of "the model performs explicit memory operations you can audit".
> 3. **Consolidation wins or loses the feature.** Extract, dedupe, resolve contradictions, delete — incrementally. Summarise-only pipelines lose detail (brevity bias) and degrade across rewrites (context collapse).
> 4. **Provenance and authority are non-negotiable.** Every remembered fact carries source, time, version and tenant; semantic memory must never outrank published policy or an authoritative metric.
> 5. **Do not build memory until a cross-session eval exists** and stateless alternatives are exhausted. Most product "memory" requirements are better served by a retrieval index or a notes file.

## The model in one page

### Four kinds of memory

| Kind | Question it answers | Store | Retention | Why it cannot be merged |
|---|---|---|---|---|
| Working | what is true *now* in this run? | context window | the run | evicted by design; compaction is its management |
| Episodic | what happened, in order? | append-only trace / event log | days–months | audit + replay require immutability |
| Semantic | what is true about the user/org/domain? | vector + KV + graph | long | needs contradiction resolution and versioning |
| Procedural | how do we do this task? | skills, playbooks, prompts, code | versioned | must be reviewed/published, never model-writable |

An append-only trace is episodic memory. A published prompt is procedural memory. A pgvector index over documents is **retrieval**, not memory — it has no notion of what the agent learned or when it became stale.

### The lineage: paging, blocks, files

**MemGPT** `[foundational]` framed the LLM as an OS managing limited main memory, paging between a main context, recall storage (conversation history) and archival storage (vector DB) through function calls, with interrupts for memory pressure and self-directed edits ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)). **Letta** turns this into read/write *memory blocks* plus background ("sleep-time") reorganisation between turns. **Anthropic's memory tool** is the minimal version: a client-side file directory the model can create, read, update and delete, where *you* own the storage and persistence, paired with context editing ([Anthropic, 2025-09](https://claude.com/resources/articles/context-management)).

The shared lesson is more important than any of the implementations: **memory operations are explicit, typed and auditable**. The model calls `memory.write(...)`, not "the system silently embeds the turn". If you build the week-4 module this way, you can test it, scope it per tenant, delete it on request, and trace why a fact was recalled.

### Retrieval is a component, not the answer

The lab builds retrieval from scratch: chunking, an embedding interface (deterministic fake for tests, one real provider for behaviour), cosine similarity in numpy, then a SQLite store — with a written comparison to pgvector. Design choices that matter:

- **Hybrid beats pure vector** in enterprise text: lexical match for IDs, product codes and names; semantic for paraphrase. Rerank the top 20 to the top 5 rather than retrieving 5 straight away.
- **Retrieval quality dominates window size.** On LongMemEval, focused inputs (~300 tokens) beat full histories (~113k tokens) for every model family tested ([Chroma, 2025](https://www.trychroma.com/research/context-rot)). The win is not "more history", it is "the right 300 tokens".
- **Budget the result.** Retrieval returns tokens into an already-tight context budget; set `top_k` and a token cap per query, and return references before bodies when the model may not need the body.

Retrieval answers "*what documents are relevant?*". Memory answers "*what does this agent know, from experience, that is still true?*" The second needs provenance and a write policy; the first does not.

### Consolidation: where memory quality is won

A write path, not a dump:

```text
candidate = extract_facts(turn)               # typed: subject, predicate, value, scope
for fact in candidate:
    fact.provenance = {source, tool, run_id, ts, asset_version}
    existing = store.search(fact.subject)
    if conflict(existing, fact):  store.mark_conflict(...)   # never silently overwrite
    elif duplicate(existing, fact): store.reinforce(existing, fact.provenance)
    else: store.append(fact)
```

Two named pathologies to design against: **brevity bias** (concise summaries drop domain insight) and **context collapse** (iterative rewriting erodes detail). ACE's fix is structured, **incremental** updates that preserve detailed knowledge instead of rewriting whole contexts ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618), ICLR 2026). Concretely: append facts and curate periodically; never let a summariser be the only copy of a decision.

Design the **subtraction** path from day one: contradiction marking, TTLs, tenant-scoped deletion, "forget this user". A memory store you cannot delete from is a compliance liability, not a feature.

### Benchmarks and honest numbers

- **LongMemEval** ([arXiv:2410.10813](https://arxiv.org/abs/2410.10813)) is the reference conversational long-term-memory suite — and the benchmark behind the focused-context result above.
- **Mem0** reports production-oriented extraction/consolidation gains at lower token cost ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413)); it is vendor-authored, so read the method and treat exact deltas as optimistic.
- **No public benchmark measures organisational memory**: permissions, retention, cross-tenant isolation, authority. That risk is yours to measure.

A credible local measurement set: cross-session task success with vs without memory; **stale-answer rate** (facts contradicted by the current authoritative source); recalled-token cost per task; and deletion correctness (does "forget" remove the fact from every store?).

### When NOT to build memory

1. The task is stateless or single-session (most back-office automation).
2. You have no eval that measures cross-session success — you cannot tell whether memory helps.
3. You cannot say what must **never** be remembered (PII, secrets, regulated data) or how deletion works.
4. A retrieval index over existing knowledge already answers the need (that is not agent memory).
5. The "memory" would be an unversioned prompt blob — that is procedural memory; make it a reviewed, versioned asset.
6. Tenant scoping and provenance are unsolved — a shared memory pool across tenants is a data breach waiting to happen.

### Memory and the learning loop

Episodic memory (traces) is the substrate; **learning** is the process that turns it into procedural memory. That process — trace → distill → candidate → eval → human publish — is week 7's learning-loop material. SendOS names the pieces: append-only `Outcome_Trace`, a five-dimension evaluator, an evidence gate (sample ≥ 30, confidence ≥ 0.7, quality ≥ 0.5), and a **submit-only** promoter: a model can create a `Draft`, never a `Published` asset ([research 05 §2.4](../research/05-sendos-concept-map.md)). The safety property is the point: memory may remember, but only humans promote policy.

## Common misconceptions

| Misconception | Reality |
|---|---|
| "A vector DB is memory." | That is retrieval. Memory needs write policy, provenance, contradiction handling, retention and deletion. |
| "More remembered context is better." | Stale and contradictory facts are worse than none; context rot applies to recalled content too. |
| "Memory should be invisible and automatic." | Invisible memory is untestable and unauditable. Expose explicit operations you can trace. |
| "Summaries are a safe way to persist knowledge." | Summaries lose detail (brevity bias) and degrade under repeated rewriting (context collapse). Append + curate. |
| "One store for everything." | Episodic, semantic and procedural have different schemas, retention and review processes. |
| "Memory is a user-private feature." | In an enterprise platform it is tenant-scoped, authority-governed data. Over-sharing is a governance bug. |

## How this shows up in SendOS

- **Episodic memory is literally an append-only log.** `Outcome_Trace` has a closed 21-event lifecycle, store-assigned monotonic `Sequence`, and a DB trigger that denies `UPDATE`/`DELETE` ([research 05 §2.4](../research/05-sendos-concept-map.md)). If the trace cannot be replayed, it cannot be trusted as memory — immutability precedes every learning mechanism built on it.
- **Semantic memory has an authority hierarchy.** The published `BusinessSemanticDefinition` is tenant-authoritative; user overlays are additive and can never override the metric formula ([research 05 §2.3](../research/05-sendos-concept-map.md)). That is the enterprise version of this note's rule: remembered facts never outrank published, versioned definitions.
- **Procedural memory is a published asset, not a model write.** The distillation/evidence-gate/publish pipeline keeps candidates as diffs against a base version and requires a human approval row before `Published` ([research 05 §4.3](../research/05-sendos-concept-map.md)). Your week-4 consolidation rule is the miniature of that gate.

## Check yourself

1. Which memory kind does an append-only trace implement, and why does immutability matter *before* building consolidation or learning on top?
2. Why must semantic memory never outrank a published definition? What mechanism could enforce it, and what happens if that mechanism lives only in the prompt?
3. What are ACE's two named failure modes, and what design choice in your write path avoids them?
4. Name three measurements you would need before adding memory to an agent, and what each is protecting against.
5. A user invokes "forget me". What must your design guarantee across episodic, semantic and procedural stores — and which one is hardest to satisfy?

## Reading

- [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) (2023) — the memory hierarchy and paging model; short and still the best framing.
- [Mem0: production long-term memory](https://arxiv.org/abs/2504.19413) (2025) — extraction/consolidation with cost and latency numbers; read critically.
- [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618) (ICLR 2026) — evolving playbooks, brevity bias and context collapse.
- [A-MEM: Agentic Memory](https://arxiv.org/abs/2502.12110) (2025) — Zettelkasten-style linked notes; a useful contrast to flat vector memory.
