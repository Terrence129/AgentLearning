# The Learning Plan

**Learner:** Terrence (Yaqi) Chen — full-stack engineer (Java/Spring, C#/.NET, React/TS, AWS), intern on SendOS.
**Constraints:** 8–12 h/week alongside an internship and NUS coursework. Python primary, C# bridge.
**Horizon:** 9 working weeks + 1 buffer week (~90–110 hours). **Started:** 2026-10-18.
**Goal:** go from "I have called LLM APIs" to "I can design, build, evaluate, secure and operate an agent system — and I can read SendOS's agent runtime with expert eyes."

---

## 1. Outcome map

You named four goals. They are not equally served by every week, so the plan weights them explicitly:

| Goal | How the plan serves it | Weeks |
|---|---|---|
| **A. Contribute meaningfully to SendOS faster** | Every week has a SendOS bridge: the same mechanism rebuilt in miniature, then located in the real repo. Capstone is a Mini-SendOS. | 1–9, strongest 3, 6, 7, 8 |
| **B. Be hireable as an AI/agent engineer** | Public portfolio: 8 green test suites, a traced agent, an eval report, a capstone demo + architecture write-up. | 2–9 |
| **C. Build your own agent product** | Weeks 2–8 cumulatively produce the platform; week 9 ships a web UI and a real end-to-end domain workflow. | 6–9 |
| **D. Deep technical mastery / research fluency** | From-scratch builds, weekly paper reading (1 must-read + 1 optional), and a "re-derive from memory" final. | 1–10 |

**Conflict rule:** when short on time, protect A and D (the compounding ones). B and C are outputs of doing A+D well, not separate tracks.

---

## 2. Design principles

1. **From scratch first, frameworks second.** You implement the provider seam, loop, compaction, MCP discovery, and eval harness yourself. In weeks 6–9 you then read framework source (LangGraph, OpenAI Agents SDK, Microsoft Agent Framework) and recognise every abstraction.
2. **Tests are the specification.** Each week has a test suite that fails before you build and passes when you are done. It removes the "did I learn it?" ambiguity that kills self-study.
3. **70 / 20 / 10.** 70% building, 20% reading, 10% reflecting and writing. Reading without a build is entertainment.
4. **Vertical slices.** Each week's code is reused by the next; the capstone is the composition of weeks 1–8, not a ninth unrelated project.
5. **Trace before you optimise.** From week 2 every run emits structured events. By week 7 you already own the data needed for evals.
6. **The six runtime duties.** Research identifies the harness — not the model — as the real differentiator, and decomposes it into six duties: *observation, context, control, action, state, verification*. Every week maps to at least one; weeks 2, 6 and 8 exist specifically because action and verification are separate duties, not afterthoughts. See [`docs/research/01-agent-architecture-sota.md`](../research/01-agent-architecture-sota.md) §0–1.
7. **Least autonomy that passes the eval.** Prefer a workflow over an agent, one agent over many, a deterministic check over a model call. Weeks 6–8 make this measurable instead of ideological.
8. **Spaced repetition over cramming.** 5 flashcards + a 150-word teach-back every week. [`docs/glossary.md`](../glossary.md) is the canonical term list.

---

## 3. Phase structure

```
Phase 1  FOUNDATIONS (weeks 1–3)      Build the primitive: model, loop, tools, typed output.
Phase 2  CAPABILITY  (weeks 4–6)      Make it capable: context, memory, interoperability, planning.
Phase 3  PRODUCTION  (weeks 7–9)      Make it trustworthy: evals, security, governance, capstone.
Buffer   CONSOLIDATION (week 10)      Re-derive from memory, portfolio, interviews.
```

Each week is a contract:

- **Inputs:** previous week's green tests, this week's brief and concept note.
- **Outputs:** green `tests/weekNN`, a lab artifact, a weekly review, 5 flashcards.
- **Gate:** you cannot start week N+1 until week N's gate passes (see [`CHECKPOINTS.md`](CHECKPOINTS.md)).

---

## 4. Week-by-week

### Week 0 — Setup and baseline (3 h)

**Objective:** a working environment and an honest baseline.

- Run `.\tasks.ps1 setup`; fix `doctor` until clean.
- Run `pytest` (foundation green) and `pytest -m week` (all lab tests red — expected).
- Make one live call with a throwaway script; record tokens and cost in `notes/week00-baseline.md`, and record latency from the CLI's wall-clock/elapsed time (the provider adapter returns `Usage` only — latency is measured by the caller's span and, from week 2, by the `model_call` trace event's `duration_ms`).
- Write your baseline answers: what is a token, why does streaming exist, what can go wrong in a retry.

**Gate:** `doctor` clean, foundation tests green, one recorded live call with cost.
**Research:** read [`docs/research/04-learning-resources.md`](../research/04-learning-resources.md) §"2026 state of play".

---

### Week 1 — The model, demystified (8–10 h)

**Objective:** stop treating the API as magic. Understand the wire format, streaming, retries and the provider seam.

**Build** (`agentlab/providers/openai_compat.py`):
1. `_build_payload` — message/tool mapping, omit empty fields, `extra` override last.
2. `_parse_response` — choices, tool calls, usage, raw payload retention.
3. `complete` — POST, retry 429/5xx/transport with `Retry-After` + exponential backoff + jitter, error taxonomy.
4. `stream` — SSE parsing with fragmented frames, delta assembly, usage + `done` events.

**Lab deliverable:** `agentlab chat` streams responses and prints per-turn token/cost. `pytest tests/week01 -m week` green.

**Concepts to be able to explain:** tokens vs characters, context window, system/user/assistant/tool roles, temperature/top-p, `finish_reason`, prompt caching, why retries belong in the adapter, why streaming is a protocol not a feature.

**Reading (2 h):** provider API reference (OpenAI *and* DeepSeek — compare), research 02 §3 (model-provider capabilities).

**SendOS bridge (30 min):** `apps/Send.Model.Adapter` structure; identify the three things your provider seam does that its adapters also do, and the two it does not (budget-aware routing, structured completion — you build those in weeks 3 and 8).

**Stretch:** add an Anthropic adapter (different system-prompt placement, content blocks, tool schema) behind the same `Provider` protocol.

---

### Week 2 — Tools and the agent loop (10–12 h)

**Objective:** build the loop yourself. This is the single most important week.

**Build** (`agentlab/loop/`, `agentlab/tools/builtin.py`):
- `ToolRegistry` usage: pydantic input models → JSON Schema → handler, errors-as-observations, output truncation (provided infra; you extend it).
- `react.py`: model → tool calls → execute → tool messages → repeat; `max_steps`, token/cost budget checks at the *top* of each iteration; stop conditions; step-level trace events.
- `runner.py`: run config, result type (final answer, steps, usage, trace ref, stop reason), `MaxStepsExceeded` partial results.
- `builtin.py`: `calculator`, `read_file`, `list_dir` (sandboxed to a workspace), `write_file` (marked `is_write=True`), `search_text`.
- A CLI agent (`agentlab chat --tools`) with `/trace` to show the last run's events.

**Lab deliverable:** agent completes 5 golden tasks (arithmetic, file read, multi-step edit, graceful tool error, budget stop) with a complete trace. `pytest tests/week02 -m week` green.

**Concepts:** native tool calling vs ReAct text parsing, parallel tool calls, observation formatting, loop termination, budget enforcement, error recovery, the difference between "agent" and "workflow".

**Reading (2 h):** research 01 §1–2; Anthropic *Building effective agents* (linked in research 04).

**SendOS bridge:** `CapabilityDefinition`, capability registry, `DirectCapabilityHandler`; compare their typed execution plan with your loop. Note what SendOS adds: risk level, approval requirement, read vs write.

**Stretch:** implement the loop twice — text-parsed ReAct and native tool calling — and write 150 words on when each is preferable.

---

### Week 3 — Structured output, prompts as assets, deterministic tests (8–10 h)

**Objective:** make model output a typed contract instead of a paragraph.

**Build** (`agentlab/schemas/`):
- `structured.py`: pydantic → JSON Schema → constrained request; validate; **never** surface invalid output as valid.
- `repair.py`: one repair retry that feeds validation errors back; bounded attempts; metrics on failure rate.
- `prompts.py`: versioned prompt templates (`id`, `version`, `render`), so a prompt change is a reviewable diff. The version bump *is* the immutable edit — there is no separate content hash to drift out of sync.
- A typed `Decision` family in the spirit of SendOS: `ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal` with presentation budgets (headline ≤ 12 words, ≤ 2 sentences of meaning, ≤ 4 next moves).
- Cassette-based tests: record one real interaction, replay in CI. **Scrub before committing:** recorded bodies can contain personal data, tenant identifiers, secrets and cost metadata — redact or synthesise them, and never record with a production key.

**Lab deliverable:** `StructuredExtractor(provider).extract(messages, DecisionUnion) -> ExtractionResult[Decision]` with schema enforcement, bounded repair, and a failure-rate report over 20 cases. `pytest tests/week03 -m week` green, offline.

**Concepts:** JSON mode vs structured outputs vs grammar-constrained decoding, schema design for models, discriminated unions, retry economics, prompt versioning, replay testing.

**Reading (2 h):** research 01 §3 (context engineering) + research 02 §3; provider structured-output docs.

**SendOS bridge:** `IStructuredCompletionHandler`, `JsonSchemaValidator` (hand-rolled subset), `DecisionInteraction` family, `PresentationBudgetEnforcer`. Note their choice: validate-after rather than impossible-to-emit — and when that is the right trade.

**Stretch:** measure the schema failure rate for three levels of nesting depth; write up when hand-rolled validation beats provider-native schemas.

---

### Week 4 — Context engineering and memory (10–12 h)

**Objective:** treat context as a budget. Make a long task survive without losing state.

**Build** (`agentlab/context/`):
- `window.py`: token estimation, priority classes (pinned constraints > task state > recent turns > observations > history), budget policy.
- `compaction.py`: summarise old turns into a bounded "carry-forward" note; prune stale tool outputs; verify task state survives (a post-compaction retention test).
- `retrieval.py`: chunking, a from-scratch embedding interface (deterministic fake + one real provider), cosine search with numpy, then a sqlite-backed store; compare with pgvector in a note.
- `memory.py`: episodic (run summaries), semantic (facts with provenance), working (scratchpad); consolidation rule; when NOT to add memory.

**Lab deliverable:** the week-2 agent completes a 20-turn research task under a 12k-token budget with measurable retention, plus a cost comparison before/after. **Retention target:** ≥ 90% of pinned constraints and task state survive compaction. Treat that threshold as a *local invariant you define and test*, not a published benchmark — the point is that you chose a number, measured it, and can detect a regression.

**Concepts:** context rot, attention budget, progressive disclosure, filesystem-as-context, sub-agent context isolation, RAG vs long context, memory benchmarks, provenance.

**Reading (2 h):** research 01 §3–4 (read the context-rot section twice); Anthropic context-management write-up.

**SendOS bridge:** `Send.Context.Gateway`, the "least-context envelope" (`SpecialistContext`), semantic retriever + pgvector adapter. Their guarantee is *data minimisation*, not maximal recall — different objective from a chatbot.

**Stretch:** intentionally poison the context with a contradicting instruction and design a defence.

---

### Week 5 — MCP and interoperability (8–10 h)

**Objective:** stop writing bespoke integrations. Build both sides of the protocol.

> **Important:** the MCP spec was redesigned in 2026 and is now **stateless** — the `initialize` handshake and session ids were **removed**, `server/discover` is mandatory, and `_meta` carries version negotiation. Read the current changelog *before* coding; most tutorials in the wild still describe the removed 2025 flow. Deployed servers may lag the spec, so your lab brief must state which revision it implements. See research 01 §10 and research 02 §1.

**Build** (`agentlab/mcp/`):
- `server.py`: expose 3 tools + 1 resource over stdio; JSON-RPC framing; capability declaration; error codes.
- `client.py`: connect, discover capabilities, map remote tools into `ToolRegistry`, invoke, handle failures/timeouts.
- `security.py`: server trust list, tool-description digest pinning, allowlist, "never pass through user tokens".
- Wire the client into the week-2 loop and use a remote tool inside a multi-step task.

**Lab deliverable:** a working MCP server (`python -m agentlab.mcp.server`) + client that completes a task using a remote tool; a security checklist pass. `pytest tests/week05 -m week` green.

**Concepts:** hosts/clients/servers, tools vs resources vs prompts, transports (stdio vs streamable HTTP), auth (OAuth, audience binding), tool poisoning, confused deputy, MCP vs A2A vs plain function calling.
**Reading (2 h):** the current MCP spec + changelog; research 02 §1.

**SendOS bridge:** connector manifests → registry (`ICapabilityManifestProvider`) vs MCP discovery; execution origin stamping; where a standard protocol would reduce SendOS's bespoke connector surface, and where it would not (governed entitlements).

**Stretch:** expose your agent itself over A2A and explain what the agent card must and must not reveal.

---

### Week 6 — Planning, orchestration and human approval (10–12 h)

**Objective:** learn when to use more than one agent — and how to keep a human in the loop safely.

**Build** (`agentlab/orchestrator/`):
- `plan.py`: typed plan (workstreams, dependencies, acceptance criteria), validate (acyclic, closed kinds), replan on failure.
- `specialist.py`: sub-agents with isolated context, narrow tool sets, structured hand-off artifacts (never full transcripts).
- `orchestrator.py`: route by topology — one capability node → direct call; one reasoning node → single specialist; ≥2 connected nodes → one squad; ≥2 components → multi-squad. Unbacked shape → limitation, never a guessed smaller shape. (This is SendOS's `TopologyClassifier` rule, rebuilt.)
- `approval.py`: proposal persisted **before** approval; `ApprovalBinding` (actor, tenant, action hash, authority snapshot, expiry); state machine; at-most-once execution; replay and post-approval-edit rejection.
- Budget per workstream, aggregated at the orchestrator.

**Lab deliverable:** mini-Squad for a business decision ("should we discount this deal?") with: meta-orchestrator → 1–2 specialists → typed decision → approval-gated write → audit row. A test proves an edited/replayed/expired approval cannot execute. `pytest tests/week06 -m week` green.

**Concepts:** orchestrator-worker, handoff vs manager, context isolation, plan-and-execute vs ReAct, topology-driven shape selection, smallest sufficient shape, HITL as durable suspend/resume, approval binding.

**Reading (2 h):** research 01 §6 + §2; Section 4.1/4.5 of [`docs/sendos/CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md).

**SendOS bridge:** decision-first runtime, `ExecutionPlan`, `ExecutionShape`, `ApprovalCheckpoint`, `EffectiveAuthority`, ADR-0001 (topology selection). This is the highest-value week for your day job — plan to demo the miniature to your team.

**Stretch:** implement durable suspend/resume (SQLite + resume on callback, CAS against double-resume). This is SendOS's unwired `CaseRuntime`; a working miniature is a credible contribution proposal.

---

### Week 7 — Evals and observability (8–10 h)

**Objective:** turn "it seems better" into a regression gate.

**Build** (`agentlab/evals/`):
- `dataset.py`: eval cases as versioned data (JSONL) with inputs, rubric, weights, expected constraints.
- `harness.py`: run an agent factory over a dataset; capture traces + outputs; score with deterministic checks first; write a report.
- `judges.py`: rubric-based LLM judge with forced JSON; measure agreement against 20–30 human labels; report pass@1 and **pass^k** (reliability across repeats).
- `report.py`: markdown/HTML report with regressions, cost, latency, failure taxonomy.
- CI gate: fail when a metric drops below baseline.

**Lab deliverable:** an eval suite of ≥ 25 cases for weeks 2–6 agents; a baseline report; three real regressions found by changing a prompt; judge agreement ≥ 80% with your labels. `pytest tests/week07 -m week` green.

**Concepts:** outcome vs trajectory evals, pass^k, judge bias/calibration, eval leakage, deterministic-first scoring, what benchmarks (SWE-bench/TAU-bench/GAIA/Terminal-Bench) actually measure, trace schema design, OTel GenAI semconv status.

**Reading (2 h):** research 03 §1–2; Hamel Husain on evals (research 04).

**SendOS bridge:** `Outcome_Trace` append-only contract, 5-dimension `Evaluator`, `Distillation`/`Trainer` learning loop, publish gate. Note the gap research-05 flags: trace→candidate→publish is the most obviously unwired mechanism — your miniature is a design sketch for it.

**Stretch:** implement an OTel exporter for your trace events and view one run in a local collector.

---

### Week 8 — Security, governance, cost, reliability (8–10 h)

**Objective:** assume the model will be manipulated, and design so it does not matter.

**Build** (`agentlab/guard/`):
- `injection.py`: direct/indirect injection handling — untrusted-content delimiting, instruction hierarchy, output vetting; the "lethal trifecta" test.
- `sandbox.py`: tool execution confined by path allowlist, size/time limits, and a subprocess or container boundary; write tools declare `is_write` and require approval.
- `authority.py`: deny-by-default intersection over independent sources; model output can never widen permission; per-tenant scoping.
- `audit.py`: append-only action log with before/after evidence and correlation ids.
- `ratelimit.py` + budget routing: per-tenant quotas, cost/latency-aware model routing with fail-safe budget checks, fallback on transient failures only.
- Red-team suite: ≥ 10 attacks (prompt injection via tool output, tool poisoning, path traversal, token passthrough, approval replay, budget exhaustion, data exfiltration).

**Lab deliverable:** attack suite with before/after results; every write action gated and audited; a `SECURITY.md` threat model. `pytest tests/week08 -m week` green.

**Concepts:** indirect injection, lethal trifecta, confused deputy, least privilege, sandboxing, approval binding, audit vs debug traces, prompt caching economics, durable execution, multi-tenant isolation, EU AI Act timeline (GPAI live since Aug 2026; high-risk Dec 2027).

**Reading (2 h):** research 03 §3–7 + checklist; OWASP GenAI Top 10 2026.

**SendOS bridge:** the "governance sandwich", `EffectiveAuthority` nine-source intersection, licensing/quota at ingress, execution origin. SendOS is already ahead here — your job is to understand *why* each control exists, not to reproduce the code.

**Stretch:** write a one-page threat model review of the SendOS approval path and send it to a senior engineer for critique.

---

### Week 9 — Capstone: Mini-SendOS (12–16 h)

**Objective:** compose everything into one honest system, and demonstrate it.

**Build** (`projects/capstone/` + `agentlab/capstone/`, `agentlab/web/`):
1. **Provider layer** — week 1 adapter + a mock provider for demos + budget routing (week 8).
2. **Capability catalogue** — tools with risk level, read/write, approval requirement; merged from two sources with published-wins.
3. **Decision runtime** — typed decision family (week 3) + topology-driven shape selection (week 6) + specialists.
4. **Governance** — fail-closed authority intersection, approval binding + at-most-once, audit log.
5. **Learning loop** — append-only traces (week 7) + eval harness + an evidence gate + a human-approved asset promotion (submit-only).
6. **Surface** — FastAPI + a minimal UI: submit a goal → see the typed decision, the plan, the approval request → approve → see the execution and the audit trail.
7. **Report** — architecture decisions, eval results, cost/latency, threats considered, what you would do next.

**Deliverable:** `scripts/demo_capstone.py` runs the whole flow offline with a mock provider; the web UI runs against a real provider. A 5-minute recorded demo. `projects/portfolio/WRITEUP.md` filled in.

**Gate:** demo works end-to-end; eval suite green; a senior engineer (or me) can follow the trace of one request from ingress to audit row without asking questions.

**SendOS bridge:** produce a 1-page design proposal for one real improvement (recommended: durable suspend/resume for approvals, or trace→candidate evidence gating). Ground it in your capstone.

---

### Week 10 — Consolidation and leverage (4–6 h)

- **Re-derive from memory:** write the agent loop, MCP discovery flow, eval design and approval state machine from a blank file. Compare to your code.
- **Portfolio:** publish the capstone write-up and 2 deep-dive posts (e.g. "approval binding is a security mechanism", "why pass^k beats pass@1").
- **Interview prep:** 30 questions in [`docs/plan/INTERVIEW.md`](INTERVIEW.md) (built from research 01–03).
- **Next-step decision:** agentic RL / fine-tuning, framework specialisation (LangGraph or Microsoft Agent Framework), or productise the capstone.

---

## 5. Time allocation per week (8–12 h)

| Block | Time | What |
|---|---|---|
| Brief + concept note | 45 min | Read lab brief and the week's concept note; write 3 goals |
| Build session 1 | 2–3 h | Core implementation against failing tests |
| Build session 2 | 2–3 h | Finish implementation; make the lab artifact work end-to-end |
| SendOS bridge | 45 min | Read mapped C# code/docs; write 5 bullet comparison |
| Theory + paper | 90 min | One concept note + one must-read paper/essay |
| Review + reflection | 60 min | Green tests, weekly review, 5 flashcards, progress update |
| Stretch (optional) | 1–2 h | Only if the gate is already passed |

The efficiency method (timeboxing, retrieval practice, interleaving, spaced repetition) is in [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md).

---

## 6. Assessment and gates

Each week has three gate conditions (details in [`CHECKPOINTS.md`](CHECKPOINTS.md)):

1. **Green:** `pytest tests/weekNN -m week` passes.
2. **Explain:** 150-word teach-back with no notes, plus answers to the week's quiz.
3. **Transfer:** complete the SendOS bridge note (what matches, what differs, what you would change).

You may not start week N+1 until all three pass. **One grace exception:** when work or coursework interferes, you may carry **one** non-green gate for **one** week, logged as debt in [`PROGRESS.md`](PROGRESS.md) with a repayment date. Two consecutive weeks of debt means you stop and clear it — a half-understood week compounds faster than any other failure mode in this plan. If a week overruns by > 50%, cut the stretch goal, not the gate.

---

## 7. Risks and countermeasures

| Risk | Countermeasure |
|---|---|
| Internship crunch eats the week | Minimum viable week = 2 sessions + tests green; skip theory/stretch, never skip the gate |
| API cost anxiety | All tests are mock-based; live calls are capped at $0.50/run; DeepSeek for high-volume labs |
| Tutorial rabbit hole | The plan's reading list is capped; anything not linked from the week is "later" |
| Framework FOMO | Frameworks arrive in week 6+ as comparison, not as prerequisites |
| "It works but I can't explain it" | The teach-back gate; no exceptions |
| SendOS docs vs code drift | Research-05 §0 records five verified drifts — always trust code over docs |
| Perfectionism on the capstone | Demo script + write-up beats polish; ship at 80% |

---

## 8. What "done" looks like at week 9

You can, without notes:

- Draw the request path of an agent run from ingress to audit row, naming every failure mode and its control.
- Explain why approval must be bound to an action hash and an authority snapshot, and what breaks without it.
- Design an eval suite that would catch a prompt regression before production, including pass^k reasoning.
- Read a new agent framework's source and map its abstractions onto the primitives you built.
- Read SendOS's `DecisionRuntime`/`ApprovalCheckpoint`/`Model.Adapter` and propose a concrete improvement.

And you own: ~4–6k lines of tested Python, 9 lab reports, an eval report, a capstone demo, and a portfolio write-up.

---

## 9. After the course

Three credible directions, in increasing difficulty:

1. **Framework fluency** — reimplement week 6's squad in LangGraph and Microsoft Agent Framework; compare ergonomics (1 week).
2. **Learning loop** — extend the capstone's trace→eval→candidate→publish into a small "self-improving" pipeline with evidence gates (2–3 weeks).
3. **Agentic RL / post-training** — only if the eval and data plumbing above is solid; otherwise you will optimise noise.

Recommended reading order after the course: [`docs/research/04-learning-resources.md`](../research/04-learning-resources.md) §F, then the three must-read papers in §D that you have not yet read.

---

## Appendix — research mapping

| Plan section | Primary sources |
|---|---|
| Week 1–2 | research 01 §1–2, research 02 §3 |
| Week 3 | research 01 §3, research 02 §3 |
| Week 4 | research 01 §3–4 |
| Week 5 | research 02 §1, research 01 §10 |
| Week 6 | research 01 §2, §6; research 05 §4.1, §4.5 |
| Week 7 | research 03 §1–2; research 05 §4.3 |
| Week 8 | research 03 §3–7; research 05 §4.2 |
| Week 9 | research 05 §4 |
| Learning method | research 04 §A, §H |
