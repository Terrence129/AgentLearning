# Chapter map — *AI Agents in Depth* → AgentLab weeks

How to read the companion textbook alongside this curriculum without letting it displace the labs.

**Edition pinned:** v2.0, 2026-09-23 (EN/中文). Page numbers refer to the A4 PDF. If your copy is v1.4 or earlier, chapter numbers are shifted by one from ch6 onward — check the edition line on page 2 before trusting these references.

**Default rule:** read the mapped section *before* the week's build (30–60 min), re-read it when a test fails conceptually, and run at most **one** experiment after the gate passes. No lab, no reading.

---

## 1. Week-by-week mapping

| Week | Read (time-boxed) | What it adds beyond this repo | Optional experiment |
|---|---|---|---|
| **0 Setup** | Ch.1 §1.1–1.4, pp. 9–37 (≈50 min) | The `LLM + Context + Tools` formula and the harness framing before you touch code; model-selection criteria | — |
| **1 Provider / model** | Ch.2 §2.2, pp. 40–51 (≈35 min) | The same loop at API level: four roles, tool-call message structure, code walkthrough, how context is composed | Exp 1-1 ★★ *The Critical Role of Context* |
| **2 Loop & tools** | Ch.4 §4.1–4.2, pp. 124–129; §4.4, pp. 131–137 (≈40 min) | Capability-expression forms (dedicated tools vs general executor vs skill), the art of tool descriptions, parameter fidelity, tool-count overflow and discovery | Sch. Ch.4 experiments (5 total) — pick one |
| **3 Structured output** | Ch.2 §2.4, pp. 61–68; Ch.4 §4.2.3, pp. 128–129 (≈30 min) | Prompt-engineering structure, tool-definition design, injection as a context-security problem | Exp 2-4 ★★ *Ablation Study in Prompt Engineering* |
| **4 Context & memory** | Ch.2 §2.3, pp. 51–61; §2.6, pp. 73–79; §2.7, pp. 79–85; Ch.3 §3.1–3.3, pp. 87–121 (≈90 min) | **The biggest gain:** KV-cache/chat-template mechanics, the "Agent status bar", production compression, and memory/RAG as a system rather than a vector store | Exp 2-3 ★★ *Common but Harmful Context Management Patterns*; Exp 3-2 ★★ *Comparing Memory Strategies*; Exp 2-10 ★★★ *Comparison of Context Compression Strategies* |
| **5 MCP** | Ch.4 §4.3, pp. 129–131; §4.4, pp. 131–137; §4.5–4.7, pp. 137–145 (≈40 min) | MCP in the wider tool ecosystem, skills as on-demand lookup, and the three tool classes (perception / execution / collaboration) | Sch. Ch.4 experiments — the MCP one |
| **6 Orchestration** | Ch.10 §10.1–10.2, pp. 336–340; §10.3–10.5, pp. 340–364; Ch.2 §2.7.6, pp. 84–85 (≈60 min) | A decision framework instead of a vibe: shared vs non-shared context × topology, the **information-gain test** for "is multi-agent worth it", six named failure modes, A2A cross-org | Exp 10-1 ★★ *Shared-context role switching*; Exp 10-2 ★★ *Book Translation Agent* |
| **7 Evals & observability** | Ch.7 §7.1–7.5, pp. 224–248; §7.6–7.9, pp. 248–264 (≈80 min) | The strongest complement to our week: pass@k vs **pass^k**, verifier design, judge methods, **failure attribution**, pairwise ranking, **statistical significance**, observability, benchmark→roadmap | Sch. Ch.7 experiments (14 total) — the judge and attribution ones first |
| **8 Security & governance** | Ch.2 §2.4.7, pp. 66–68; Ch.4 constraints/permissions, pp. 125–129 & 139–144; Ch.9 §9.3.2, p. 333 (≈40 min) | Injection as a *context* problem, tool permission/irreversibility, and safety boundaries for self-improving loops | Exp 2-5 ★★ *Prompt Injection Attack and Defense* |
| **9 Capstone** | Ch.9 §9.1–9.3, pp. 314–335; Ch.7 §7.6 & §7.9, pp. 248–257; Ch.5 §5.1, pp. 147–166 (≈70 min) | The theory behind a trace→learning loop (experience → knowledge → instructions → programs → parameters), "done ≠ progress", and the coding-agent harness as a reference architecture | Sch. Ch.9 experiments — the experience-consolidation one |
| **10 / after** | Ch.8 (post-training), Ch.6 (interaction), Ch.5 (coding agents) | The paths this curriculum deliberately defers | Ch.8 experiments only if you plan to train |

Section-to-lab anchors: [weeks in the plan](../../plan/LEARNING-PLAN.md) · [labs](../../../labs/README.md) · [concept notes](../../concepts/README.md).

---

## 2. Reading paths

### Path A — "6 hours, give me the spine" (do this even if you read nothing else)

| Chunk | Pages | Time | Why |
|---|---|---|---|
| Ch.1 all | 9–37 | 50 min | The whole book's vocabulary in one chapter |
| Ch.2 §2.2 + §2.7 | 40–51, 79–85 | 45 min | The loop at API level + how context is compressed |
| Ch.4 §4.2–4.4 | 125–137 | 30 min | What makes a tool good, and what to do at 200 tools |
| Ch.7 §7.2 + §7.5 + §7.8 | 228–248, 253–255 | 50 min | pass^k, judges, failure attribution, observability |
| Ch.10 §10.1–10.2 | 336–340 | 25 min | When multi-agent actually helps (information gain) |

### Path B — "20 hours, the standard pass" (one chapter per week alongside the labs)

Path A + Ch.2 §2.3/§2.6 (KV cache, status bar) + Ch.3 (skim §3.1–3.3) + Ch.7 all + Ch.9 §9.1–9.3 + Ch.10 all, plus 3–5 experiments that match weeks you have already finished.

### Path C — "60+ hours, full course"

Path B + Ch.5 (coding agents) + Ch.6 (interaction; skip §6.5 robotics if uninterested) + Ch.8 (post-training, only if you intend to train/fine-tune) + one experiment per chapter.

### What to skip on a first pass

- **Ch.2 §2.3.1–2.3.5 (KV-cache mechanics):** the book itself says to keep the three conclusions and skip the derivation on a first read. Read it *after* week 4, when you have built compaction and felt the cache cost.
- **Ch.6 §6.5 (robot manipulation):** excellent, but out of scope for this plan.
- **Ch.8 (post-training):** do not read before week 9; it will pull you into training before you can evaluate.

---

## 3. Selected experiments (★ = difficulty)

Run these in a **separate clone** of the book repo — never inside this repo's venv. Exercises marked ★★ or ★★★ assume you have already built the corresponding week.

| Exp | ★ | Topic | Best after |
|---|---|---|---|
| 1-1 | ★★ | The Critical Role of Context | Week 1 |
| 2-3 | ★★ | Common but Harmful Context Management Patterns | Week 4 |
| 2-4 | ★★ | Ablation Study in Prompt Engineering | Week 3 |
| 2-5 | ★★ | Prompt Injection Attack and Defense | Week 8 |
| 2-8 | ★★ | Verifying the Agent Status Bar via Attention Visualization | Week 4 |
| 2-10 | ★★★ | Comparison of Context Compression Strategies | Week 4 |
| 3-2 | ★★ | Comparing Memory Strategies | Week 4 |
| 3-5 | ★★ | Exploring Sparse Retrieval: BM25 from scratch | Week 4 |
| 3-6 | ★★ | Hybrid Retrieval Pipeline: Sparse, Dense, Reranking | Week 4 |
| 3-8 | ★★ | Agentic RAG vs Non-Agentic RAG | Week 4 |
| 3-10 | ★★ | Contextual Retrieval | Week 4 |
| 10-1 | ★★ | Shared-context role switching — system prompt vs Skill | Week 6 |
| 10-2 | ★★ | Book Translation Agent | Week 6 |
| 10-3 | ★★★ | Autonomous Phone and Computer Agents | Week 6 / post-course |

Chapter experiment indexes: [`chapter1/`](https://github.com/bojieli/ai-agent-book/tree/main/chapter1) … [`chapter10/`](https://github.com/bojieli/ai-agent-book/tree/main/chapter10) (each has a `README.en.md`). Ch.4, 5, 6, 7, 8, 9 have 5/16/14/14/19/9 experiments respectively.

---

## 4. Two frameworks, one architecture

The book and this repo describe the same harness at different granularity. Do not treat the lists as competing:

| This repo / research 01 (six runtime duties) | Book (five harness elements, §1.2.6) |
|---|---|
| observation | *(part of interaction / ch6)* |
| context | context management |
| control | constraints |
| action | tool interfaces |
| state | *(implied by context management)* |
| verification | verification and correction |

Use the book's five-element framing to explain the system in an interview; use the six-duty decomposition to decide what to test. Both are correct at their own level.

---

## 5. Known gaps — keep this repo primary

| Topic | Book coverage | Use this repo instead |
|---|---|---|
| Approval binding, authority intersection, at-most-once execution | Light | Weeks 6 & 8 |
| Multi-tenancy, licensing, quota | ~2 mentions | Week 8 + SendOS bridge |
| Hash-chained append-only audit | Logging discussion | Week 8 |
| Schema-validated structured output + bounded repair | Thin | Week 3 |
| Test-driven "done" contract | Experiments, not specs | `tests/weekNN/` |
| SendOS file:line mapping | None | [docs/sendos/](../../sendos/README.md) |
| OTel GenAI semconv | One mention | Week 7 |

---

## 6. How to cite it in your notes

Cite **edition + section + page**, not just "the book":

> Li, *AI Agents in Depth*, v2.0 (2026-09-23), §7.2.2 "Business Reliability: Focus on pass^k", pp. 229–230.

This matters because chapter numbers moved between v1.4 and v2.0, and the English edition is a community translation of the Chinese canonical text.
