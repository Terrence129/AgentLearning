# Interview Preparation

**Use:** answer each question **aloud in 60–90 seconds**, from memory, before reading the model answer. Then compare in one sentence: "what did I miss?" That gap is your flashcard. Re-test the missed ones at day 1, day 3, day 7 (spaced repetition — see [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)).
**Scope:** the 30 questions below cover what an AI/agent-engineer loop actually asks: loop mechanics, context, evals, security, multi-agent trade-offs, MCP and governance. Each maps to a week, so your lab is your evidence.
**Rule:** never answer from vocabulary. Every answer should name a mechanism and one failure mode it prevents. Where possible, add "in my capstone, …" with a number.

---

## Part 1 — 30 questions with model answers

### A. Model & provider layer (Week 1)

**1. A request fails with `finish_reason: "length"`. What do you do?**
Model answer: that is an output-cap stop, not a context overflow. The loop inspects `finish_reason` and decides: raise `max_tokens`, ask for a shorter format, or split the task. In the adapter, this is a typed outcome so callers never treat truncation as success. *Failure mode prevented:* parsing half an answer as if it were complete.

**2. How do you design retries for model calls?**
Model answer: classify first — 429/5xx/transport are retryable; 400/auth/policy are terminal. Then exponential backoff with jitter, honour `Retry-After`, cap attempts and total time, and count retries in the cost/trace record. Retries live in the adapter because the signals are provider-specific. *Failure mode prevented:* retry storms and burning budget on a malformed request.

**3. Why is streaming a protocol rather than a feature?**
Model answer: SSE frames can be fragmented, tool-call arguments arrive in deltas, and failures can occur mid-stream. This forces delta assembly keyed by tool-call id, usage accounting from the final frame, cancellation and timeout handling. Streaming also determines perceived latency (TTFT). *Failure mode prevented:* executing partial JSON from a half-received tool call.

**4. How does prompt caching change prompt design?**
Model answer: only an identical prefix is cached, so stable content (system prompt, tool definitions, policy) goes first and volatile content (timestamps, user input, tool results) last. A timestamp in the system prompt destroys every cache hit. *Failure mode prevented:* paying full price and latency on every turn because a prefix changed.

### B. Loop & tools (Week 2)

**5. Native tool calling or text-parsed ReAct?**
Model answer: native tool calling by default — structured calls with ids remove brittle parsing and let the provider enforce argument shape. Text ReAct remains useful for models/providers without native support, or when you want explicit reasoning text. In my lab I built the loop so the two share one executor. *Failure mode prevented:* regex-parsing tool calls and mis-pairing results.

**6. What are the termination conditions of your loop?**
Model answer: four — final answer with no pending tool calls; `max_steps` reached; budget exhausted; no progress detected. Each produces a typed stop reason, and the max-steps case returns partial results instead of throwing away work. *Failure mode prevented:* infinite loops and silent overspend.

**7. How do tool errors reach the model?**
Model answer: as observations. The executor catches tool exceptions, formats them (type, message, hint), truncates, and returns them as the tool result so the model can retry or choose another tool. Only infrastructure failures that make the loop unable to continue abort. *Failure mode prevented:* one bad path crashing an otherwise recoverable run.

**8. When do you build a workflow instead of an agent?**
Model answer: when the control flow is knowable in advance. Workflows are cheaper, deterministic and easier to eval and audit; agents are for open-ended tasks where the number and nature of steps depend on tool feedback. The rule is "least autonomy that passes the eval". *Failure mode prevented:* using a stochastic planner for a five-step deterministic process.

### C. Structured output (Week 3)

**9. JSON mode vs structured outputs vs constrained decoding?**
Model answer: JSON mode guarantees parseable JSON only; provider structured outputs enforce a schema; constrained decoding makes invalid tokens impossible. Each step buys a stronger guarantee at the cost of portability and schema features. I always validate locally regardless, because "valid" must mean "valid against my contract". *Failure mode prevented:* acting on missing or wrong-typed fields.

**10. How do you handle a schema validation failure?**
Model answer: bounded repair — resend a compact validation error plus the schema, allow one retry, re-validate. If it still fails, return an explicit invalid result: `ExtractionResult(valid=False, value=None, raw=<last raw>, errors=[...])`, and record it in `RepairStats` (failure rate). Schema failures are data, not exceptions; only `ProviderError` propagates. Never coerce or default invalid output into a valid-looking object. *Failure mode prevented:* silent fabrication downstream.

### D. Context & memory (Week 4)

**11. What is context engineering, in one mechanism-level sentence?**
Model answer: selecting the smallest high-signal token set for the next call under a fixed attention budget, by curating system prompt, tools, observations and history rather than appending everything. Concretely: priority classes, compaction, just-in-time retrieval and sub-agent isolation. *Failure mode prevented:* context rot — accuracy dropping as the window fills.

**12. Describe compaction without hand-waving.**
Model answer: when the estimate crosses the budget, summarise the oldest turns into a bounded carry-forward note that explicitly preserves decisions, open problems, constraints and identifiers; prune stale tool outputs; restart the window with that note plus recent turns. Then run a retention test asserting pinned constraints survive. *Failure mode prevented:* losing the task definition at the moment the task gets long.

**13. How do you decide what to remember?**
Model answer: three memories — working (task scratchpad), episodic (per-run summaries), semantic (durable facts with provenance). Consolidation has an explicit rule (e.g. only verified facts with a source and timestamp). Retrieval weights freshness and provenance; cross-tenant memory is never shared. *Failure mode prevented:* stale memory silently overriding fresh evidence.

**14. RAG or agentic search?**
Model answer: RAG when the corpus is document-shaped and queries are known; agentic search (`grep`, SQL, file trees) when knowledge is structured and freshness matters. Both are context-selection strategies; the decision is empirical — measure retrieval hit rate and task success. *Failure mode prevented:* building a vector index that is stale on day two.

### E. MCP & protocols (Week 5)

**15. Explain MCP's architecture and primitives.**
Model answer: a host runs the app and model; clients connect to servers; servers expose tools (actions), resources (data) and prompts (templates) over JSON-RPC, on stdio or streamable HTTP. Discovery is the value: one integration surface instead of bespoke connectors. *Failure mode prevented:* N×M integration explosion.

**16. What are the security risks of MCP, and your controls?**
Model answer: tool poisoning (malicious descriptions injecting instructions), rug pulls (semantic changes after review), confused deputy (server acting with user authority), and token leakage. Controls: server trust list, description/schema digest pinning, audience-bound auth, no user-token passthrough, timeouts and error mapping, and treating every description as untrusted input. *Failure mode prevented:* a third-party server silently gaining authority.

**17. MCP versus plain function calling?**
Model answer: function calling is an in-process request convention between your code and a model provider; MCP is an interoperability protocol across processes and vendors with discovery, auth and transport. Use function calling for local tools, MCP when the tool surface is external or multi-client. *Failure mode prevented:* reinventing a connector per integration.

### F. Orchestration & approval (Week 6)

**18. When does multi-agent actually pay?**
Model answer: when subtasks are genuinely parallelisable, or when a subtask needs an isolated context (deep search, large repo) and returns a distilled artifact; synthesis must be the hard part. Otherwise a single agent with better tools wins on cost, latency and debuggability. *Failure mode prevented:* paying 3× for a topology that only added failure modes.

**19. How does topology-driven shape selection work?**
Model answer: classify the task's topology (one capability node → direct call; one reasoning node → single specialist; connected nodes → one squad; multiple components → multi-squad) and choose the *smallest sufficient shape*. If the task does not fit a backed shape, report a limitation rather than guessing smaller. *Failure mode prevented:* silent under-powering and over-engineering.

**20. What must an approval bind to, and why?**
Model answer: actor, tenant, action hash, authority snapshot and expiry. The hash blocks post-approval edits; the snapshot blocks executing under changed authority; actor/tenant block cross-principal reuse; expiry blocks stale approvals. *Failure mode prevented:* an approved "read" becoming a "refund" before execution.

**21. How do you guarantee at-most-once execution?**
Model answer: a compare-and-swap state machine (proposed → approved → executing → executed) plus an idempotency record keyed by the action id, and rejection of replays and expired approvals. Retries return the prior result rather than executing again. *Failure mode prevented:* duplicate side effects under retries or double-resume.

**22. Why is durable suspend/resume hard?**
Model answer: the run must be persisted (session + proposal + state), a callback must resume the *right* run exactly once, and CAS must reject double-resume; all of it must survive process restarts. A demo approval that blocks a thread is not an approval system. *Failure mode prevented:* approvals lost on deploy, or executed twice on retry.

### G. Evals & observability (Week 7)

**23. Design an eval suite for an agent in one answer.**
Model answer: a versioned dataset of 20–50 cases covering happy paths, each failure category, safety constraints and edge inputs; deterministic checks first; a rubric-based judge calibrated to ≥80% agreement with human labels; outcome *and* selected trajectory metrics; pass@1 and pass^k; cost/latency; a baseline in CI that fails on regression. *Failure mode prevented:* "it feels better" shipping.

**24. How do you trust an LLM judge?**
Model answer: you do not, by default. Force structured output from a rubric, measure agreement against 20–30 human labels, check bias (self-preference, verbosity, position), randomise order, and report agreement alongside every judged metric. Below ~80%, the judge is not a measurement. *Failure mode prevented:* optimising against the judge's bias.

**25. Why pass^k?**
Model answer: pass@1 hides unreliability. An agent at 70% per attempt succeeds on five consecutive attempts only ~17% of the time; production users experience the streak, not the average. pass^k turns reliability into a metric and a CI floor. *Failure mode prevented:* shipping a demo-grade agent as production-ready.

### H. Security & governance (Week 8)

**26. How do you defend against indirect prompt injection?**
Model answer: assume it will succeed. Treat fetched content as data (delimited, never instructions), enforce an instruction hierarchy, vet outputs before acting, and make the blast radius small: least privilege, sandbox, no secrets in the sandbox, and no external-communication tool in the same agent as private data (lethal trifecta). *Failure mode prevented:* data exfiltration through a poisoned document.

**27. What is effective authority, and how is it computed?**
Model answer: the permission set actually enforced for an action — the intersection over independent grants (user, tenant, role, tool policy, risk level), deny-by-default, with the model unable to widen it. One implementation, consulted everywhere. *Failure mode prevented:* privilege escalation via union bugs or model suggestion.

**28. What does a sandbox have to enforce for file/shell tools?**
Model answer: resolved-path allowlist (not string prefixes), symlink escape checks, size/time/CPU limits, a process or container boundary, no secrets in the environment, and write tools gated by approval and audit. *Failure mode prevented:* `../` traversal and shell injection escaping the workspace.

**29. Audit log versus trace?**
Model answer: a trace is a debugging record (steps, timings, payloads, samplable); an audit log is tamper-evident evidence of consequential actions with before/after state, actor, tenant, correlation id and retention policy. They share ids but have different integrity and access requirements. *Failure mode prevented:* being unable to prove what the system did.

### I. Architecture (Week 9)

**30. Walk me through one request in your capstone, ingress to audit row.**
Model answer: ingress → auth/tenant/quota → provider adapter with budget check and typed errors → typed decision (schema validated, repaired once if needed) → topology/shape selection → specialist plan with isolated contexts → any write becomes a proposal → approval bound to actor/tenant/action-hash/authority-snapshot/expiry → at-most-once execution with idempotency record → audit append with before/after and correlation id → trace/outcome emitted for evals. Every arrow has a failure mode and a control; I can show the trace for one real request. *Failure mode prevented:* a system you cannot explain under pressure.

---

## Part 2 — Five system-design prompts

### How the 30-minute design interview is graded

| Dimension | Fail (1) | Pass (2) | Strong (3) |
|---|---|---|---|
| **Requirements** | Starts designing immediately; no questions | Clarifies users, volume, latency/cost, autonomy level | Also separates must-haves from nice-to-haves and states non-goals |
| **Architecture** | One box called "LLM agent" | Clear components, data flow, typed boundaries | Names trade-offs per component, chooses smallest sufficient shape, explains what is deterministic |
| **Failure & security** | "We'll add guardrails" | Names injection, authority, budget, retries, human approval | Threat-models the lethal trifecta, binds approval, isolates credentials, defines fail-open/closed per failure |
| **Evals & ops** | "We'll test it" | Golden set, judge calibration, regression gate, traces | pass^k, cost/latency budgets, failure taxonomy, rollout/rollback |
| **Communication** | Jumps between topics; no summary | Structured, answers follow-ups | States assumptions explicitly, sums up trade-offs and what they would measure first |

**Pass bar:** at least "pass" on all five dimensions and "strong" on two. **Timebox:** 5 min requirements → 10 min architecture → 7 min failure/security → 5 min evals/ops → 3 min summary.

### Prompt 1 — Support agent with refund authority

> "Design an agent that triages support tickets and can issue refunds up to $200. It must handle 50k tickets/day, work in 12 languages, and the CFO wants no unauthorised refunds."

**What a strong answer covers:** workflow-first triage (classification → retrieval → decision), agent only for the ambiguous tail; typed decision family; refund as a capability with risk level; approval binding for above-threshold or low-confidence cases; authority intersection per tenant/agent; idempotency on refund calls; audit row per refund; eval set with a money-loss metric and pass^k; cost routing (cheap model for triage).
**Red flags:** letting the model call the refund API directly; no threshold logic; judge-scored only; no audit.

### Prompt 2 — Contract extraction at 99% field accuracy

> "Design a pipeline that extracts 40 fields from 200k contracts with a 99% accuracy target, and tell me how you would know you hit it."

**What a strong answer covers:** deterministic pre-processing; schema-first extraction with strict validation; confidence + field-level repair; human-review queue for low confidence (sampling strategy); stratified eval set by contract type and field; per-field accuracy and calibration; drift monitoring; cost per 1k pages; how to define "accuracy" against a labelled sample and the statistical power needed.
**Red flags:** "prompt it well and spot-check"; no confidence handling; no stratification; claiming 99% without a labelled sample.

### Prompt 3 — Enterprise learning loop (trace → eval → publish)

> "Design the loop that turns production traces into better agent behaviour, with human control over what ships."

**What a strong answer covers:** append-only trace schema with correlation ids; sampling and PII handling; failure mining/taxonomy; candidate generation (prompt/skill/policy changes); evidence gate (eval suite + pass^k + no safety regression) before promotion; human-approved publish with rollback; provenance and versioning of assets; what is automated vs human; how you avoid leaking production data into evaluation.
**Red flags:** auto-publishing prompt changes; evals from the same traces used to tune; no rollback; no provenance.

### Prompt 4 — MCP integration for 12 internal systems

> "Your company has 12 internal systems (CRM, billing, wiki, ticketing, HR, CI…). Design how agents get tool access, safely."

**What a strong answer covers:** MCP servers per system with least-privilege scopes; host/client architecture; registry of approved servers with owner and risk level; digest pinning and review process; per-user auth via audience-bound tokens (no passthrough); read tools vs write tools with approval; rate limits and timeouts; audit of tool calls; what stays bespoke (governed entitlements, high-risk writes) and why.
**Red flags:** one shared service token for all systems; exposing every tool to every agent; no approval for writes; no trust registry.

### Prompt 5 — Coding agent for CI failures

> "Design an agent that takes a failing CI run on a mid-size repo and proposes a fix. It must be safe to run unattended overnight."

**What a strong answer covers:** context strategy (repo map, failure logs, `grep`/glob, not whole-repo dump); sandbox with no network/secrets, resource caps; plan-and-execute with per-step verification (tests as ground truth); bounded steps/budget; branch + PR output rather than direct push; eval on a held-out set of past CI failures; trajectory eval (did it run tests? respect allowlists?); human review; cost/latency per run.
**Red flags:** direct push to main; network access; no test-based verification; unbounded loops.

---

**Before an interview:** re-read your capstone ADRs (10 min), re-derive the request path on paper (10 min), and rehearse prompts 1 and 3 aloud (15 min). Those three cover most of what the loop will ask.
