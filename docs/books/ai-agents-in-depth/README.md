# AI Agents in Depth — companion textbook

> **《深入理解 AI Agent：设计原理与工程实践》** · Bojie Li (李博杰) · **v2.0, 2026-09-23**
> 382 pp (EN) / 313 pp (ZH) · 10 chapters · **109 experiments** · Apache-2.0 · free

**Verdict: highly useful — adopted as this curriculum's companion textbook.** It is the best single source for the *theory behind* the mechanisms this repo makes you build, and its 109 experiments give you a second implementation of almost every idea, in a different codebase.

It does **not** replace this repo. See [Where it is thinner than this repo](#4-where-it-is-thinner-than-this-repo) — the enterprise governance track and the test-driven build are ours.

---

## 1. Metadata and provenance

| Item | Value |
|---|---|
| Original title | 《深入理解 AI Agent：设计原理与工程实践》 |
| Author | **李博杰 (Bojie Li)** — Pine AI; formerly AI systems research/infra; book grew out of the UCAS AI-Agent course and the Turing "AI Agent Bootcamp" |
| English title | *AI Agents in Depth: Design Principles and Engineering Practice* |
| Edition | **v2.0, 2026-09-23** (Chinese is canonical; English is a community translation, released for the same v2.0 build) |
| Length | 382 pp EN / 313 pp ZH, 10 chapters, ~204k words EN |
| License | **Apache-2.0** (open source, free to redistribute) |
| Official repo | https://github.com/bojieli/ai-agent-book |
| Online reader | https://bojieli.github.io/ai-agent-book/astro/ |
| Release downloads | https://github.com/bojieli/ai-agent-book/releases |
| Companion code | 109 experiments organized `chapter1/` … `chapter10/`, `uv`-based extras per chapter |
| Answer key | `book/reference-answers.md` — reference answers to the "Thought Questions" |
| Local copies | `AI-Agents-in-Depth-en.pdf`, `AI-Agents-in-Depth-zh-CN.pdf` (git-ignored; re-download from the official release if they go stale) |

**Version warning.** v1.4→v2.0 renumbered chapters: the old ch4 async section and old ch9 multimodal content became **new ch6 "Interaction"**, and evaluation/post-training/continual-evolution shifted to **ch7/ch8/ch9**. Any tutorial, summary, or citation that says "chapter 6 is evaluation" is a v1.4 artifact. This repo pins v2.0 numbering.

## 2. Why it is useful (what it adds that we do not have)

1. **The harness, explained as an architecture.** Its framing — `Agent = LLM + Context + Tools`, then `Agent = Model + Harness` with five harness responsibilities — is the conceptual layer under our six runtime duties. It makes the "why" of weeks 1–2 explicit.
2. **Context engineering at the mechanism level.** KV-cache/chat-template mechanics, prompt-cache structure, the "Agent status bar", production-grade hierarchical compression, and sub-agent isolation (ch2). Our week 4 teaches compaction by building it; the book explains *why the cache shape forces the design*.
3. **Memory and knowledge as a system** (ch3): user memory hierarchy, four storage formats, RAG chunking/dense/sparse/hybrid, structured indexing, agentic RAG, contextual retrieval, multimodal memory. Deeper than our week 4 notes.
4. **Tools as a designed surface** (ch4): capability-expression forms, tool-description art, parameter fidelity, MCP, and what to do when the tool catalogue outgrows the context — proactive tool discovery and skills. Directly useful for SendOS's connector/capability catalogue.
5. **Coding agents as the reference architecture** (ch5): harness engineering, failure recovery, search/edit tools, security, "code as a meta-capability". Relevant to SendOS Code Factory and to how you use coding agents daily.
6. **Evaluation done properly** (ch7): τ²-bench task anatomy, pass@k vs **pass^k**, verifier design, contamination, LLM-as-judge, **failure attribution** (locate the first error in a trajectory), pairwise ranking, evaluation-driven model selection, **statistical significance**, observability, benchmark→roadmap. This is the strongest complement to our week 7.
7. **Continual evolution** (ch9): experience → knowledge → instructions → programs → parameters, minimal-diff/provenance discipline, "when done ≠ progress", safety boundaries, sleep learning. This is the general theory behind SendOS's distillation→candidate→human-publish loop.
8. **Multi-agent with a decision framework** (ch10): shared vs non-shared context × topology; an information-gain table for *when* collaboration helps; six named failure modes; A2A for cross-organization. Better than most blog material and a direct complement to week 6.
9. **109 experiments** with ★ difficulty ratings — a second implementation to compare against yours (transfer practice).

## 3. How to use it (do not read it linearly)

The method that matches this repo's learning loop:

1. **Read thin (before the week):** read only the mapped section (see [CHAPTER-MAP.md](CHAPTER-MAP.md)) — 30–60 minutes. You are building a vocabulary, not memorising.
2. **Build (during the week):** do the lab. When a test fails for a *conceptual* reason, re-read the mapped section — now it lands.
3. **Read thick (after the gate):** skim the chapter's other sections and run **one** experiment from it. Compare its implementation to yours: what did the author choose differently, and why?
4. **Never let the book displace the lab.** If a week is short, read nothing and ship green tests.

### Read / skip guidance

- **Must read (all readers):** ch1; ch2 §2.1–2.2 (API-level loop) and §2.7 (compression); ch4 §4.2–4.4; ch7 §7.2, §7.5, §7.8; ch10 §10.1–10.2.
- **Skip on a first pass:** ch2 §2.3 KV-cache mechanics (the book itself says keep only the three conclusions), ch8 (post-training — optional, after the capstone), ch6 §6.5 robotics.
- **Read if you are curious:** ch5 (coding agents), ch6 (voice/computer-use), ch9 (continual evolution — *do* read §9.1–9.3 even if you skip the rest).

## 4. Where it is thinner than this repo

| Topic | Book | This repo |
|---|---|---|
| **Enterprise governance** — approval binding, deny-by-default authority intersection, proposer≠approver, at-most-once execution | Light: permissions, sandboxing, safety boundaries are mentioned; no approval-binding invariants | Weeks 6 & 8, with explicit security tests; mapped to SendOS `ApprovalCheckpoint` / `EffectiveAuthority` |
| **Test-driven build** | Experiments, not specifications; you run demos | **563 failing specs** that define "done" per week |
| **Multi-tenant / licensing / quota** | ~2 mentions of multi-tenancy | Week 8 quotas/tenancy + SendOS licensing bridge |
| **Audit as a mechanism** | Logging/observability discussion | Week 8 hash-chained append-only audit, audit-vs-debug split |
| **Structured output + bounded repair** | Thin (tool schemas, JSON in passing) | Week 3: typed extraction, `ExtractionResult(valid=False)`, repair loop, cassettes |
| **OTel / GenAI semconv** | One mention; observability section is conceptual | Week 7 trace model + exporter stretch |
| **Durable execution / suspend-resume** | Light | Week 6 approval state machine + durable stretch |
| **SendOS mapping** | None | [docs/sendos/](../../sendos/README.md), grounded in file:line |
| **Deep context/KV-cache theory** | **Deep** — use it | Lighter (we build, don't derive) |
| **Post-training / RL** | **Deep (ch8)** | Deferred; optional after week 9 |
| **Coding agents** | **Deep (ch5)** | Not covered |
| **Multi-agent taxonomy + failure modes** | **Deep (ch10)** | Week 6 partial |

**Rule:** use the book for *theory and alternatives*; use this repo for *contracts, tests, governance and SendOS transfer*.

## 5. Keeping the local copy current

The official release always points at the latest build:

- Chinese: `https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf`
- English: `https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-en.pdf`

Check the edition line on page 2 (`版本 v… · 日期`) before trusting a chapter reference. If you update the PDF, re-check [CHAPTER-MAP.md](CHAPTER-MAP.md) for renumbering, then update this README's edition row.

The PDFs are git-ignored: `git check-ignore -v docs/books/ai-agents-in-depth/AI-Agents-in-Depth-en.pdf`.

## 6. Companion code (optional)

```bash
git clone https://github.com/bojieli/ai-agent-book.git
cd ai-agent-book
uv sync --locked --extra ch1     # then ch2 ... ch10
uv run python chapter1/context/main.py
```

Experiments that call models need a key (the book suggests Kimi, GLM, SiliconFlow, DeepSeek, OpenRouter). Run them **outside** this repo to avoid mixing dependency trees; this repo's `.venv` stays minimal on purpose.

## 7. Attribution

© Bojie Li, Apache-2.0. This repo references and quotes short excerpts for teaching; it does not redistribute the book in git. If you reuse figures or substantial text in your own writing, follow the Apache-2.0 terms and cite the author.
