# 09 — Production: Durability, Cost, and the Checks That Matter

> **Week 9 and beyond · just-in-time concept note.** Read before the capstone (~25 min). This note is about the runs that don't complete — and the readiness checks you are allowed to skip. **Reads with:** [research 03 §4–8](../research/03-production-evals-ops.md) · **Lab:** `week09-capstone`.

## The failure mode this prevents

The agent loop lives inside a request handler. At step 7 of 9 the platform deploys, the worker is recycled, the run is lost — and the client, seeing a timeout, retries. The write tool was not idempotent, so the refund executes twice. Meanwhile the invoice is 4× the estimate and nobody can attribute it to a tenant, prompt version or tool, because cost was logged as one number per day.

Production readiness is four disciplines: **durability** (runs survive), **idempotency** (side effects happen once), **cost control** (spend is attributable and bounded), **tenant isolation** (one customer cannot break another). The 38-check list in research 03 is the full map; this note is the short path.

## If you remember five things

> 1. **An agent loop is a workflow, not a request.** Persist state, use activities, survive restarts, suspend on humans.
> 2. **Every side-effecting call needs an idempotency key persisted before the call.**
> 3. **Cost is input tokens × context length × turns** — cache, compact and route before optimising milliseconds.
> 4. **The 15-minute serverless limit is shorter than many agent runs**, so separate API, orchestration, execution and sandbox tiers.
> 5. **For a single-team product, 12 of 38 readiness checks carry most of the risk.** Do those; defer the rest deliberately.

## The model in one page

### Durable execution: the loop is a workflow

An agent loop holds state — conversation, step index, budget consumed, pending tool calls, approval status — and its steps fail independently: model timeouts, tool rate limits, humans taking hours. Keeping that state in a process is the design error.

Temporal documents the right model: the loop is a Workflow, each model and tool call is an Activity, a crash resumes the conversation instead of restarting it, and human-in-the-loop is a durable Signal plus Timer ([Temporal](https://docs.temporal.io/evaluate/use-cases-design-patterns), accessed 2026-10-18). On AWS, a Lambda invocation is capped at **15 minutes** (90 for managed-instance async), while durable functions allow 30,000 operations per execution and MicroVMs run up to 8 hours ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18).

Minimum viable durability: a **run table** (status, step, budget, trace ref), a **checkpoint per step**, a **resume endpoint**, **CAS on resume** so a double-callback cannot double-execute, and a **deadline sweeper**. Prefer Temporal's .NET SDK or durable functions over building this.

### Idempotency and at-most-once

Idempotency is a storage problem before it is a retry problem:

- Derive the key from `(run_id, step_no, tool, canonical_args_hash)`; canonicalise arguments (sorted keys, normalized types) or the same call yields different keys.
- **Persist before invoking**, in a store with a uniqueness constraint. On retry, return the stored result or a stable rejection.
- **Same key + different arguments is an error**, never a re-execution with new arguments.
- An approval is **consumed** when it executes, so a replayed approval cannot execute twice.

Test it the boring way: same key twice → one side effect; mutated arguments → rejection.

### Cost and latency levers, in order

Prompt caching is the biggest lever. Cache reads cost **0.1×** input (0.05× on Anthropic's Opus/Sonnet 5.5-class, 0.025× on Fable/Mythos 5.1-class); writes cost **1.25×**; TTLs are 5 minutes (1 hour at 2×) on Anthropic and 30 minutes on current OpenAI models. A documented multi-turn agent pattern reports **>90% cache-hit** ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18).

Order of attack, highest leverage first:

1. **Measure** cost per successful task and cache-hit rate per tenant.
2. **Stabilise the prefix**: static content first (instructions, tools, examples), dynamic last, append rather than rewrite.
3. **Cap budgets** per run, user and tenant — enforced at the gateway, not in the prompt ([budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/), accessed 2026-10-18).
4. **Compact** long runs: summarise history, clear stale tool output.
5. **Route**: cheap model for classification/extraction/easy turns, escalate on confidence or failure.
6. **Batch** non-interactive work — evals, nightly summaries, backfills — at provider discounts.

Cached input still counts toward rate limits ([OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18). Latency levers (parallel tools, streaming, deferred loading) improve UX but rarely fix cost.

### Deployment topology and multi-tenancy

Four tiers: **stateless API/edge** (auth, licensing, streaming, no loop), **orchestrator** (durable engine owns run state), **execution workers** (tool calls; scale on queue depth, not CPU), **sandbox** (ephemeral, egress-restricted). Add circuit breakers per provider+model — a throttled model is not a throttled platform — plus per-tenant rate limits and single-flight caching at the gateway.

Isolation spans more than a `WHERE tenant_id`: data (tenant ID bound by the platform, never by model arguments), credentials (per-tenant secrets and OAuth grants), compute (tenant-scoped queues so batch cannot starve interactive traffic), memory/retrieval (partitioned indexes and namespaces), caches/billing (per-customer cache-accounting keys so cost is attributable), and audit (tenant-scoped views plus platform copy). Put licensing and quota at **ingress**, before any model call, so the cheapest denial never spends tokens.

### The 12 checks that matter for a single-team product

The full 38-item list is in [research 03 §8](../research/03-production-evals-ops.md). A small team cannot ship all 38 in a quarter. These 12 carry most of the incident risk; the rest mostly prevent procurement conversations.

**Evidence (3).** (1) A private eval set of 30+ cases from real requests, versioned. (2) pass^k gated in CI, not just pass@1. (3) Every incident becomes a regression case; golden traces replayed on prompt/model changes.

**Security (3).** (4) A lethal-trifecta audit per agent — at least one leg removed or gated. (5) Irreversible actions require a bound approval with a concrete action diff. (6) An audit log separate from debug traces, append-only.

**Reliability (4).** (7) Long loops run on a durable engine with replay. (8) An idempotency key persisted before every tool call. (9) HITL is durable suspend/resume, never a held thread or request. (10) Per-model/tool timeouts and a per-run wall-clock deadline.

**Observability and cost (2).** (11) Tenant ID, prompt version, model and cost on every span, with a cache-hit-rate SLO. (12) Hard token/$ caps per run, user and tenant, enforced at the gateway.

Defer deliberately: ISO/IEC 42001 and NIST AI RMF crosswalks, a full AI-BOM, SCIM and audit export, a registry beyond a spreadsheet — until a customer or regulation forces them. One exception: if you sell into the EU, record AI Act classification and oversight evidence now, because the 2027 high-risk deadline is about evidence you should already be generating.

## Common misconceptions

| Misconception | Reality |
|---|---|
| "Durable execution is overkill for a two-minute agent." | It is about surviving deploys, retries and human waits, not duration. |
| "Retries are safe because the tool is read-only." | Money moves through writes; that is where idempotency is mandatory. |
| "Caching is automatic, so there is nothing to do." | Hits depend on prefix stability; if you cannot report hit rate, you do not know. |
| "Batch is for big data jobs." | Eval suites and nightly summaries are batch work. |
| "Multi-tenancy is a column in the query." | It is also queues, keys, caches, memory, budgets and audit. |

## How this shows up in SendOS

- **`CaseRuntime` + `DecisionTask` is the durability spine — built but dark.** CAS reserve → suspend → resume plus a deadline worker exists but is not wired (`.../Domain/CaseRuntime/**`; `.../Infrastructure/CaseRuntime/**`; [research 05 §2.5](../research/05-sendos-concept-map.md)). Wiring it is the fastest credible contribution in the repo.
- **`ActionIdempotencyStore` and the approval-consumed flag are the at-most-once pattern.** With stable replay-rejection codes (`Application/Approval/ApprovalCheckpoint.cs:341-412`), this is exactly what your lab reproduces.
- **Budget-aware routing is already coded.** `HandleRoutedAsync` filters candidates by cost/latency/attempts with fail-safe budget checks; `BudgetGuard`/`IterationBudget` enforce ceilings (`apps/Send.Model.Adapter/src/.../Handlers/CompletionHandler.cs:60-210`). Read it as the production form of your week-8 `ratelimit.py`.
- **The resilience stack is composition.** `Send.Intelligence.Gateway` layers tiered cache, circuit breaker, per-connector rate limiter, single-flight and idempotency (`apps/Send.Intelligence.Gateway/src/**`) — your weeks 7–8 primitives assembled into one call path.

## Check yourself

1. Where does loop state live if the process dies at step 7, and what must persist to resume without a duplicate side effect?
2. Derive an idempotency key for a tool call. What happens when the same key arrives with different arguments?
3. Your agent's cost doubled after a prompt change while quality stayed flat. Which three metrics do you inspect first?
4. Why does a 15-minute Lambda limit force a different topology even if runs usually finish in 30 seconds?
5. Which two of the 12 checks would you cut for a two-week prototype, and what risk do you accept?

## Reading

- [Temporal — use cases and design patterns](https://docs.temporal.io/evaluate/use-cases-design-patterns) — agents as workflows, HITL as signals and timers.
- [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) — exact multipliers, TTLs and prefix rules.
- [AWS Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) — the 15-minute wall and 2026 durable/MicroVM options.
- [Research 03 §4–8](../research/03-production-evals-ops.md) — the full production and governance map.
- **Companion book:** *AI Agents in Depth* v2.0, ch.9 §9.1–9.3 (experience → knowledge → instructions → programs → parameters; "done ≠ progress") + ch.7 §7.6/§7.9 (model selection, cost, benchmark→roadmap). The theory behind this repo's trace→eval→publish loop. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).
