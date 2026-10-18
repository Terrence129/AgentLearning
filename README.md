# AgentLab

> A test-driven, from-scratch curriculum for learning modern **agent-system engineering** — built to run alongside a real enterprise agent platform, not a toy tutorial.

**Owner:** Terrence (Yaqi) Chen · **Started:** 2026-10-18 · **Plan:** 9 weeks × 8–12 h/week

---

## What this is

This repository is two things at once:

1. **A working Python codebase** (`agentlab/`) that you grow one capability at a time: provider adapter → agent loop → structured output → context & memory → MCP → orchestration → evals → guardrails → capstone.
2. **A curriculum** (`docs/plan/`, `labs/`, `tests/`) that tells you exactly what to build, in what order, and how to know you are done.

Every week ships a runnable artifact and a test suite that **defines** the week's deliverable. If `pytest tests/week03 -q` is green, you finished week 3 — no self-assessment required.

```
Week 1  model & provider seam ──►  Week 4  context & memory ──►  Week 7  evals & observability
Week 2  tool calls & agent loop ─►  Week 5  MCP interoperability ► Week 8  security & governance
Week 3  structured output ───────►  Week 6  planning & squads ──► Week 9  capstone: Mini-SendOS
```

---

## Why this shape

Most agent tutorials teach framework APIs. That produces people who can wire a demo and cannot debug one. This curriculum is built on four choices:

| Choice | Why |
|---|---|
| **From scratch first, frameworks second** | You cannot reason about LangGraph/Agents SDK failure modes until you have written the loop yourself. Frameworks appear in weeks 6–9 as *readable* abstractions, not magic. |
| **Tests are the specification** | Agent code is stochastic; its scaffolding need not be. Deterministic mocks (`MockProvider`) make every lab testable offline, with no API key and no flakiness. |
| **Evals from week 7, traces from week 2** | Tracing is how you debug; evals are how you improve. Both are designed in early, not bolted on. |
| **A bridge to your day job** | Every week maps to a real mechanism in the SendOS codebase (`.NET 8/10`), with optional C# equivalents. See [`docs/sendos/`](docs/sendos/README.md). |

The full research basis — 5 deep-research reports, ~20k words with citations — lives in [`docs/research/`](docs/research/README.md).

**Companion textbook:** [*AI Agents in Depth*](docs/books/ai-agents-in-depth/README.md) by Bojie Li (v2.0, 2026, free/Apache-2.0) — deep theory plus 109 experiments, mapped week-by-week in [CHAPTER-MAP.md](docs/books/ai-agents-in-depth/CHAPTER-MAP.md). It supplies the *why*; this repo supplies the tests, governance and SendOS transfer.

---

## Quickstart

```powershell
# from D:\DevRepo\MyProjects\AgentLearning
.\tasks.ps1 setup        # uv + Python 3.12 + deps + .env + doctor
```

Then:

```powershell
.\tasks.ps1 doctor       # check toolchain, keys, dirs
.\tasks.ps1 test         # full suite (foundation should be green; week labs start red on purpose)
.\tasks.ps1 week 1       # only week 1's tests
.\tasks.ps1 chat         # week 1 deliverable once implemented
```

Read **[START-HERE.md](START-HERE.md)** first — it is a 90-minute on-ramp, not a manual.

---

## Repository map

| Path | What lives there |
|---|---|
| [`START-HERE.md`](START-HERE.md) | 90-minute onboarding: setup → first failing test → first fix |
| [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md) | The master 9-week plan: goals, hours, deliverables, exit gates |
| [`docs/plan/WEEKLY-RHYTHM.md`](docs/plan/WEEKLY-RHYTHM.md) | How to study efficiently (retrieval practice, timeboxing, spaced repetition) |
| [`docs/plan/CHECKPOINTS.md`](docs/plan/CHECKPOINTS.md) | Weekly gates, rubrics, and what "done" means |
| [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) | Your progress tracker — update it weekly |
| [`docs/plan/LEARNER-PROFILE.md`](docs/plan/LEARNER-PROFILE.md) | Your starting point, constraints, goals, and API access |
| [`docs/concepts/`](docs/concepts/README.md) | Just-in-time concept notes (one per week), with the minimum theory and the failure modes |
| [`docs/research/`](docs/research/README.md) | The deep-research reports this curriculum was built from |
| [`docs/books/`](docs/books/README.md) | Companion textbooks: assessment, chapter→week map, reading paths |
| [`docs/sendos/`](docs/sendos/README.md) | SendOS concept map, bridge labs, and reading order |
| [`docs/glossary.md`](docs/glossary.md) | Terms you should be able to define without notes |
| [`agentlab/`](agentlab/) | The package you build: providers, loop, tools, context, mcp, orchestrator, evals, guard, capstone |
| [`labs/`](labs/) | Weekly lab briefs: goal, specification, acceptance criteria, stretch |
| [`tests/`](tests/) | The specification. `tests/weekNN/` = that week's exit gate |
| [`solutions/`](solutions/) | Reference implementations — open only after your tests pass |
| [`projects/`](projects/) | Capstone and portfolio deliverables |
| [`dotnet/`](dotnet/README.md) | C# bridge labs: provider/SSE/retry and typed-decision equivalents, mirroring weeks 1 and 3 |
| [`scripts/`](scripts/) | Repo utilities: internal link checker, capstone demo |
| [`templates/`](templates/) | Weekly review, lab notes, ADR, portfolio write-up templates |

---

## The 9 weeks

| Week | Theme | You build | Hours |
|---|---|---|---|
| 0 | Setup & baseline | Working env; first API call; token/cost accounting | 3 |
| 1 | **The model, demystified** | Raw HTTP + SSE + retries + provider seam (`agentlab/providers/`) | 8–10 |
| 2 | **Tools & the agent loop** | Tool registry, ReAct loop, budgets, step traces, terminal agent | 10–12 |
| 3 | **Structured output** | Schema-validated typed decisions, repair loop, prompt versioning, cassettes | 8–10 |
| 4 | **Context & memory** | Token budgeting, compaction, from-scratch vector search, episodic memory | 10–12 |
| 5 | **MCP** | MCP server + client over stdio; tool discovery into your loop; trust model | 8–10 |
| 6 | **Planning & squads** | Orchestrator + specialists, typed plans, isolated contexts, approval checkpoint | 10–12 |
| 7 | **Evals & observability** | Trace store, eval harness, calibrated LLM judge, CI regression gate, dashboard | 8–10 |
| 8 | **Security & governance** | Injection defenses, sandboxed tools, authority checks, audit log, model routing | 8–10 |
| 9 | **Capstone: Mini-SendOS** | Full mini platform + web UI + eval report + architecture write-up | 12–16 |
| 10 | Buffer / consolidation | Re-derive the loop from memory, portfolio, interviews | 4–6 |

Total: **~90–110 hours**. Details, objectives and exit criteria: [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md).

---

## How the learning loop works

Each week has four artifacts, in this order:

1. **Brief** — `labs/weekNN-*/README.md`: concept, specification, acceptance criteria, hints, stretch.
2. **Failing tests** — `tests/weekNN/`: read them before coding. They are the contract.
3. **Build** — write the code in `agentlab/` (or the week's lab directory).
4. **Review** — tests green → write the weekly review from [`templates/weekly-review.md`](templates/weekly-review.md) → add 5 flashcards → update [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md).

Rules that keep this honest:

- **Do not read `solutions/` until your tests pass.** Then read it and diff your design against it.
- **Never copy a tutorial without a test.** If you cannot test it, you do not understand it yet.
- **Every real model call goes through `agentlab.budget.Budget`.** No unbounded loops, ever.
- **One commit per lab step.** The git history is part of the portfolio.
- **Explain it before you ship it.** The weekly review has a "explain to a colleague in 150 words" section. If you cannot, re-read.

---

## SendOS bridge (your day job)

SendOS already contains a sophisticated agent platform: a decision-first reasoning runtime, capability registry, model adapter, governed assets, append-only outcome traces, and a trace→learning loop. This curriculum does not repeat it — it lets you **rebuild the interesting mechanisms in miniature** so the real implementation stops being opaque.

High-value pairings (details in [`docs/sendos/BRIDGE.md`](docs/sendos/BRIDGE.md)):

| You build (Python) | SendOS equivalent (C#) |
|---|---|
| Week 1 provider seam | `Send.Model.Adapter` provider adapters, budget-aware routed completion |
| Week 3 typed decision + repair | `IStructuredCompletionHandler`, `DecisionInteraction`, presentation budgets |
| Week 6 orchestrator + approval gate | Decision-first runtime, `ApprovalCheckpoint`, authoritative execution |
| Week 7 trace → eval | `Outcome_Trace`, 5-dimension `Evaluator`, trace→candidate learning loop |
| Week 8 authority + audit | `EffectiveAuthority` nine-source intersection, governance sandwich |

---

## Requirements

- Windows 11 + PowerShell (Windows PowerShell 5.1 works; PowerShell 7 recommended) — also works on macOS/Linux with `uv` directly
- Python 3.12 (installed automatically by `uv`)
- At least one provider key: **DeepSeek** or **OpenAI** (both configured in `.env.example`)
- ~$2–5 of model spend for the whole curriculum (most labs run on mocks)
- Optional: .NET 10 SDK for the C# bridge labs in [`dotnet/`](dotnet/README.md)

---

## Status

- [x] Foundation: package skeleton, config, tracing, budgets, mock provider, tool registry — 29 tests green
- [x] All 9 lab scaffolds: starter stubs, failing specifications, reference solutions, lab briefs — **563 lab tests**, each independently verified red → green → restored
- [x] Research base (5 reports, ~20k words), companion textbook integrated with a week-by-week chapter map, learning plan, concept notes, glossary, quizzes, flashcards
- [x] SendOS bridge docs + C# bridge labs (dotnet build: 0 warnings, 0 errors; both self-test suites pass)
- [x] Repo integrity: 0 broken internal links, ruff clean, CI workflow in place
- [ ] Week 1 lab — **this is your next action**

Each lab was verified independently: the starter fails for the intended reason, the reference solution passes, and the tree is restored to the learner state. No lab test touches the network.

See [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) for the live tracker you fill in.

---

## License

MIT — this is a personal learning repository. Research reports cite their sources; third-party content remains under its own license.
