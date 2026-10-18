# 03 — Production Evals, Observability, Security & Operations for Agent Platforms

*Research note, 2026-10-18. Audience: senior Java/C#/React/AWS engineer building an enterprise .NET agent platform with licensing, multi-tenancy, and audit obligations. Citation convention: `(link, accessed 2026-10-18)` — all links were fetched on that date unless a different date is given. **[established]** = vendor docs/standards/peer-reviewed; **[unsettled]** = thin or moving evidence. Numbers marked "~" are practitioner estimates, not guarantees.*

---

## 0. The frame

The hard part of production agents is not model quality; it is **trustworthy behaviour under uncertainty**. Three properties must be engineered, not prompted: you can prove **what the agent did** (traces/audit), that it **still works** (calibrated evals), and that **when the model is fooled, nothing important breaks**. OWASP's 2026 preface puts it bluntly: "Stop trying to build a model that cannot be fooled. Build the system around it, so that when the model is fooled, and it will be, nothing important breaks." ([OWASP GenAI LLM Top 10 2026 preface](https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md), accessed 2026-10-18)

For a .NET platform this maps onto familiar disciplines: evals ≈ acceptance tests, traces ≈ distributed tracing, durable execution ≈ workflow engine, tenancy ≈ SaaS control plane. What is genuinely new: **non-determinism**, **untrusted natural language treated as instructions**, and **cost that scales with behaviour, not requests**.

---

## 1. Evaluation strategy

### 1.1 Decision tree

```
Machine-checkable ground truth?
├─ YES (DB state, test pass, exit code, schema, side-effect)
│   → deterministic assertion on state, not text similarity
│   → if multi-step: score trajectory too (tools, args, policy, steps)
│   → gate on pass^k over k trials, not single-run pass@1
└─ NO (open-ended quality)
    ├─ failure cheap/reversible → sampled human preference + light judge
    └─ failure expensive/regulated → rubric + calibrated judge + human adjudication,
       published with judge-vs-human agreement

Multi-turn / long-horizon?
├─ YES → add goal state, policy compliance, step count, $/task,
│         error recovery, human-intervention rate
└─ NO  → final answer + cost/latency usually suffice

Production traffic?
├─ YES → online eval on sampled traces, A/B, drift alerts
└─ NO  → replay a dataset seeded from real requests, not synthetic happy paths
```

Deterministic assertions are the default; LLM judges are an instrument that must itself be calibrated.

### 1.2 pass@k vs pass^k

`pass@k` ("at least one of k succeeds") is a capability metric. `pass^k` ("all k trials succeed") is a reliability metric — and production cares about reliability. τ-bench introduced pass^k and reported strong function-calling agents succeeding on **<50%** of tasks with **pass^8 < 25%** in retail ([τ-bench](https://arxiv.org/abs/2406.12045), accessed 2026-10-18).

Implications: publish **pass^k (k = 3–8)** for irreversible actions (refunds, provisioning, ticket closure); track **variance across identical trials** — that variance is the real production error rate, and temperature 0 does not remove it at provider scale; budget eval cost as `k × cases × tokens` and use batch + caching to pay for it.

**[established]** pass^k as a reliability metric; **[unsettled]** what k is defensible, and whether k should scale with action consequence.

### 1.3 What to assert on a trajectory

| Dimension | Deterministic check | Why it matters |
|---|---|---|
| Tool selection | Expected/forbidden tool sets | Detects capability creep |
| Tool arguments | JSON schema + business rules + tenant-ID equality | Blocks cross-tenant IDOR at eval time |
| Policy compliance | Rule engine over the trace ("no refund > $500 without approval") | Turns compliance policy into tests |
| Efficiency | Steps, tokens, wall-clock, retries | Cost regression gate |
| Error recovery | Injected tool failure → correct fallback | The behaviour that actually breaks in prod |
| Human handoff | Escalation fires exactly when it should | Protects review capacity and SLA |

OTel models `plan` and `execute_tool` as distinct spans — the right unit of eval granularity ([OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18).

### 1.4 Judge discipline

LLM-as-judge works only as a calibrated instrument. The MT-Bench work documents **position, verbosity, self-enhancement biases and limited reasoning**, while showing strong judges reach >80% human agreement — roughly human-human ([LLM-as-a-Judge](https://arxiv.org/abs/2306.05685), accessed 2026-10-18). Minimum hygiene:

1. Rubric with **atomic criteria** (0–2 each), not one holistic 1–10.
2. **30–50 human-labelled calibration items per rubric**, double-labelled; report agreement/κ; re-calibrate on any judge or prompt change.
3. **Order-swap** pairwise comparisons; randomize length; strip formatting that triggers verbosity bias.
4. **Pin the judge model version**; cache the rubric prefix — a fixed-rubric judge can reach ~70% cache-hit rate ([OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18).
5. Never let a model family judge itself in customer-visible quality metrics.
6. Log judge inputs/outputs into the same trace system or you cannot debug score drift.

### 1.5 Public benchmarks: what they measure

Use these for **model/vendor selection and coding capability**, never as proof your product works. Build a private set from your own incidents.

| Benchmark | Measures | Caveat | Use for |
|---|---|---|---|
| **SWE-bench Verified** | Repo issue → patch, graded by tests; 500 human-confirmed-solvable tasks ([repo](https://github.com/SWE-bench/SWE-bench), accessed 2026-10-18) | Harness/leak sensitivity; Multimodal v2 (480 tasks) open-sourced 2026-09-01 | Shortlisting coding agents |
| **τ-bench** | Tool-agent-user with simulated user; scores final DB state; introduces pass^k ([paper](https://arxiv.org/abs/2406.12045)) | Simulated user ≠ real user | Closest public analogue to enterprise tool use |
| **GAIA** | 466 real-world questions needing browsing/multimodality/tools; 92% human vs 15% GPT-4+plugins; 300 answers held out ([paper](https://arxiv.org/abs/2311.12983), accessed 2026-10-18) | Web drift; time-sensitive | General assistant competence |
| **Terminal-Bench 4.0** | End-to-end terminal tasks; leaderboard reports **resolution rate, cost, tokens** ([tbench.ai](https://www.tbench.ai/), accessed 2026-10-18) | New cost dimension | CLI/devops agents, cost-aware ranking |
| **WebArena / AgentBench** | Browser environments / multi-environment breadth ([WebArena](https://arxiv.org/abs/2307.13854), [AgentBench](https://arxiv.org/abs/2307.10928)) | 2026 leaderboards not re-verified here; orient only | Historical comparison |

**[unsettled]** Leaderboards are contaminated to varying degrees and not comparable across harness versions; a few points of delta is noise.

### 1.6 Online evals and release gates

Make both gates concrete and blocking:

- **Offline (blocking):** pass^k drop >2 points, or p95 cost rise >15%, fails the build.
- **Online (canary 1–5%):** compare task-success proxy, escalation rate, thumbs-down, judge score, refusal rate; auto-rollback on threshold breach.
- **Golden traces as fixtures:** sanitized production traces replayed on every prompt/model change — the highest-ROI eval investment.
- **Incident → test:** every customer-visible failure becomes a regression case within one sprint.

LangSmith, Langfuse, Braintrust and Phoenix all cover datasets + experiments + online scoring, so selection is mostly deployment model and ergonomics. Braintrust documents instrument → observe → annotate → evaluate → deploy with online scoring ([Braintrust evaluate](https://www.braintrust.dev/docs/evaluate/index), accessed 2026-10-18); Langfuse documents online evaluation of production traces, datasets, and LLM-judge/code/human evaluators ([Langfuse](https://langfuse.com/docs), accessed 2026-10-18).

---

## 2. Observability

### 2.1 OTel GenAI conventions: adopt now, pin versions

Two 2026 facts matter operationally. First, **the conventions moved** to `open-telemetry/semantic-conventions-genai`, extending core conventions via Weaver; old doc pages are stubs ([repo README](https://github.com/open-telemetry/semantic-conventions-genai), accessed 2026-10-18). Second, **they are `Development`, not stable** — every agent span and attribute carries a Development badge ([agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18).

Adopt anyway, but **pin the semconv version, emit attributes through one `AgentTelemetry` abstraction in .NET, and never let dashboards query raw attributes directly**. Plan one breaking rename per year; proprietary schemas cost more to unwind.

Spec span taxonomy (all Development): `create_agent`, `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool`, plus skill and command-execution spans, with operation recorded in `gen_ai.operation.name` (same source). Model, provider, agent identity, conversation identity and token usage are modelled; `gen_ai.input.messages` / `gen_ai.output.messages` / `gen_ai.system_instructions` are **opt-in with an explicit PII warning**.

### 2.2 Trace data model sketch

```
Trace (one per user turn / trigger)
└── span invoke_workflow {workflow}              INTERNAL
    ├── span invoke_agent {agent.name}           INTERNAL
    │   ├── span plan {agent.name}               INTERNAL
    │   ├── span chat {model}                    CLIENT
    │   ├── span execute_tool {tool}             INTERNAL
    │   │   └── span {http/db/sandbox call}      CLIENT
    │   └── span hitl.wait {approval}            INTERNAL
    ├── span policy.evaluate {ruleset}           INTERNAL  (custom)
    └── span retrieval {index}                   INTERNAL
```

| Layer | Attributes | Notes |
|---|---|---|
| Identity | `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model` | Required-level; needed for sampling at span creation |
| Agent | `gen_ai.agent.id`, `.name`, `.version` | Stable registry ID, not in-memory instance ID |
| Session | `gen_ai.conversation.id` | Only a real conversation ID; the spec forbids synthesising one |
| Usage | input/output tokens, cache-read counts, `gen_ai.response.finish_reasons` | Without cache-read tokens, cache savings are invisible |
| Content | input/output messages, system instructions | Opt-in; hash/redact by default |
| Platform | `app.tenant.id`, `app.license.plan`, `app.prompt.version`, `app.policy.decision`, `app.tool.idempotency_key`, `app.cost.usd`, `app.budget.remaining` | What billing, audit and incident review actually need |
| Linkage | span links approval↔resumed run | A suspended agent is two traces otherwise |

Two rules that save pain: **`app.tenant.id` on every span, enforced by a processor that quarantines non-conforming spans** (same discipline as tenant-scoped .NET middleware); and **cost per span**, so regressions attribute to a tool or prompt version rather than "the agent got expensive".

### 2.3 Content capture, PII, retention

The spec itself warns message attributes likely contain PII. Default to **no bodies**: hashes, lengths, redacted previews. Full capture only on tenant opt-in, with short TTL, field-level redaction, and access logging. Keep **audit** (who/what/approval/result) separate from **debug** (prompts/messages): different retention, access control and legal basis.

### 2.4 Tooling comparison (late 2026)

| Tool | Self-host | Strengths | Watch-outs |
|---|---|---|---|
| **LangSmith** — traces, dashboards, automations, online evals ([docs](https://docs.langchain.com/langsmith/observability), accessed 2026-10-18) | Commercial/enterprise options | Mature eval UX; deepest with LangChain | Verify residency/DPA and .NET client maturity |
| **Langfuse** — OSS, OTel-based; v4 released 2026-08 ([docs](https://langfuse.com/docs), accessed 2026-10-18) | **Yes** (Docker/K8s) | Best default for on-prem/regulated; prompts+evals+sessions+agent graphs | You own HA/upgrades; check license for embedding in a commercial product |
| **Braintrust** — instrument→evaluate→deploy, online scoring, audit logs, SCIM ([docs](https://www.braintrust.dev/docs), accessed 2026-10-18) | Enterprise options | Strong experiments and human review | SaaS-first; confirm self-host and audit-log export |
| **Arize Phoenix** — OSS tracing + evals, OpenInference, RBAC/secrets/retention ([docs](https://arize.com/docs/phoenix), accessed 2026-10-18) | **Yes** | Good OTel/OpenInference fit; judge + datasets built in | Smaller ecosystem than commercial suites |
| **W&B Weave / LangWatch** ([Weave](https://docs.wandb.ai/weave), [LangWatch](https://langwatch.ai)) | Varies | Evaluation-first UX | Content not independently re-verified for this note |

**Recommendation:** two layers — OTel-native instrumentation you own, exporting to a swappable backend. Self-hosted Langfuse or Phoenix for on-prem/licensed tiers; whichever passes procurement for SaaS. Never let the eval product become the system of record for audit.

### 2.5 Metrics and SLOs

Beyond latency/errors: **task success proxy**, **pass^k trend**, **cost per successful task**, **cache-hit rate**, **steps per task**, **tool error rate by tool**, **approval queue depth/age**, **guardrail-block rate**, **judge-score drift vs 7-day baseline**. Cost per successful task is the most useful business metric — it captures model choice *and* agent efficiency.

---

## 3. Security threat model

### 3.1 The premise

Prompt injection is unsolved. Willison's **lethal trifecta** — private data + untrusted content + external communication — lets an attacker controlling content the agent reads exfiltrate data; he argues vendors claiming "95% of attacks blocked" are failing by web-security standards ([lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/), accessed 2026-10-18). Make **removing one leg** a product decision, not a prompt tweak.

OWASP's 2026 list now folds in incident evidence (7,714 incidents, 6,639 classified): **Excessive Agency rose to #3**, Unbounded Consumption rose four places, Improper Output Handling fell 5th→10th, and System Prompt Leakage became **Hidden Context Exposure** ([OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/); [source](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final), accessed 2026-10-18). When the model becomes an **actor** — tools, memory, consequences — pair it with the **Agentic Top 10** ([OWASP Agentic 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), accessed 2026-10-18). **[unsettled] verify ASI numbering against the PDF before customer-facing use.**

### 3.2 Threat model

| Attack | Mechanism | Control (architectural, not prompt-based) |
|---|---|---|
| Direct injection / jailbreak | User text tells agent to ignore policy | Instruction hierarchy, allowlisted actions, output-schema validation, per-action authorisation; bound blast radius |
| **Indirect** injection | Poisoned doc/web/email/ticket/tool result carries instructions | Treat retrieved content as **data**; never auto-execute retrieved instructions; require explicit intent for consequential actions; provenance labels |
| Lethal-trifecta exfiltration | Agent reads private data and can send outward (HTTP/email/image URL/PR comment) | Break one leg: egress allowlist, outbound DLP, no unattended external send, human approval |
| Tool poisoning / malicious MCP server | Tool *descriptions* hide instructions; server changes after approval ("rug pull") | Allowlist + pin version/digest; review descriptions as code; no untrusted dynamic discovery; scope minimisation ([MCP security](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices), accessed 2026-10-18) |
| Confused deputy / token theft | Static client credentials in proxy; token passed upstream | Audience-bound tokens, **no token passthrough**, per-request consent, separate client registration (same source; [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)) |
| Excessive agency | Broad scopes, auto-approve, long-lived credentials | Least privilege per task, short-lived capability tokens, step-up auth, approval gates for irreversible actions |
| Sandbox escape / RCE | Model-generated code or shell | microVM/container isolation, no credentials inside sandbox, egress allowlist, ephemeral, resource-capped |
| Secret exposure | Secrets in prompt, tool output or trace bodies | Secret broker resolves inside the tool boundary; never in context; collector-side redaction |
| Memory/context poisoning | Attacker writes long-term memory or shared index | Tenant-scoped memory, provenance + TTL, validate writes, never promote untrusted content to system instructions |
| Supply chain | Compromised model artifact or MCP/agent package | Pin model versions, AI-BOM ([OWASP AIBOM](https://github.com/GenAI-Security-Project/aibom-generator), accessed 2026-10-18), eval gate before upgrade |
| Cross-tenant access | Tool call omits tenant filter; IDOR via arguments | Tenant ID bound by the platform, not the model; RLS; cross-tenant regression tests |
| Denial of wallet | Loops, huge context, tool recursion | Per-run token/$ caps, max steps, loop detection, per-tenant limits, backpressure |
| Trust exploitation | Agent asserts authority ("your manager approved") | Provenance in UI, confirmation with concrete action diff, immutable audit |

### 3.3 MCP hardening

MCP is now a Linux Foundation project under the **Agentic AI Foundation** (donated 2025-12-09; co-founded by Anthropic, Block, OpenAI, with Google, Microsoft, AWS, Cloudflare, Bloomberg), with >10,000 public servers and a community registry; the 2025-11-25 spec added async operations, statelessness, server identity and extensions ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), accessed 2026-10-18).

Practical controls: **registry + allowlist, not open marketplace**; OAuth 2.1 with audience-bound tokens and step-up scopes; **no token passthrough, no static client secrets**; tool descriptions reviewed like code (they are prompt content); **per-tenant credentials**, never a shared service identity.

### 3.4 Sandboxing, audit, red teaming

Anything executing model-authored code or driving a browser is a hostile-code boundary: ephemeral microVM/container per session, no host mounts, no ambient cloud credentials, egress allowlist, CPU/memory/disk/time caps, kill switch. E2B documents sandbox templates, network and secrets/identity ([E2B](https://docs.e2b.dev), accessed 2026-10-18); Daytona documents orgs, SSO, limits and multi-language SDKs incl. Java ([Daytona](https://www.daytona.io/docs/en/), accessed 2026-10-18); AWS now offers **Lambda MicroVMs** (8-hour max, 400 GB aggregate memory) for managed isolation inside your AWS account ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18).

**Audit is a separate product from observability.** Per consequential action record: timestamp, tenant, user, agent ID+version, prompt version, model+version, tool, redacted arguments, policy decision + rule ID, approver, result, idempotency key, trace ID. Append-only storage, retention aligned to contract/regulation, customer-readable export.

**Red teaming is continuous**, not a one-off pen test: injection corpora (direct/indirect), tool-poisoning payloads, exfiltration attempts, cross-tenant probes, budget-exhaustion loops, refreshed weekly in CI. **[unsettled]** No agent red-team benchmark maps credibly to enterprise risk yet; OWASP's incident corpus and AISVS mapping are the closest anchors.

---

## 4. Reliability engineering

### 4.1 Durable execution is the default for agent loops

An agent loop is a long-running, stateful workflow whose steps fail independently. Temporal documents exactly this mapping: the loop is a Workflow, each model and tool call an Activity, crashes resume rather than restart, and human-in-the-loop is a durable Signal + Timer with an Approval design pattern ([Temporal use cases](https://docs.temporal.io/evaluate/use-cases-design-patterns), accessed 2026-10-18). It also names the broker failure mode this avoids: a queue with a short visibility timeout can hand the same message to a second consumer while the first is still working (same source). Temporal has a **.NET SDK**.

Alternatives by operational weight: **Temporal/Inngest/Step Functions** (full replay, timers, human waits; Inngest markets durable execution, flow control, agent evals, sandboxes, SOC 2 Type II — [Inngest](https://www.inngest.com/platform/durable-execution), accessed 2026-10-18); **AWS Lambda durable functions** — 5M running executions/region (10M in us-east-1/us-west-2/eu-west-1), 30,000 durable operations per execution, 100 MB persisted per execution ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18); **roll-your-own queue + checkpoint table** — acceptable only for short loops with idempotent tools.

### 4.2 Idempotency, retries, timeouts

- **Idempotency key per tool invocation**, derived from `(run_id, step_no, tool, canonical_args_hash)`, persisted before the call and checked on retry — the only reliable defence against duplicate side effects.
- **Retry only idempotent or key-protected operations**; never blind-retry payments, emails or ticket creation.
- **Exponential backoff with jitter** for 429/5xx, capped attempts and total elapsed per step ([AWS backoff/jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), accessed 2026-10-18).
- **Distinguish retryable from terminal** (validation, policy denial, auth failure = terminal).
- **Circuit breakers per provider+model and per critical tool**, with closed/open/half-open states and manual override ([Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker), accessed 2026-10-18).
- **Timeouts from p99** per model+prompt size, plus a **per-run wall-clock deadline** communicated to the model as a remaining budget.

### 4.3 Human-in-the-loop: suspend, don't block

Never park an HTTP request or worker thread for a 10-minute approval. Model it: agent proposes → orchestrator writes an approval request (action, redacted diff, policy context, expiry) and transitions to `waiting_approval` → worker released, state and trace link persisted → approver acts in UI/Teams/Slack → a Signal/Update resumes. Timeout policy is auto-deny or escalate; **never auto-approve on timeout**. Record approver + timestamp in audit and link the two traces.

### 4.4 Multi-tenant isolation

| Dimension | Mechanism | Failure if missed |
|---|---|---|
| Data | Tenant ID enforced in data layer + RLS; never model-supplied filters | Cross-tenant read via tool args |
| Credentials | Per-tenant secrets/OAuth grants | One breach compromises all |
| Compute | Tenant-scoped queues/workers; durable engines expose task-queue priority and fairness (Temporal documents this for shared workers) | Batch tenant starves interactive |
| Prompt/memory | Tenant-partitioned memory and vector namespaces | Retrieval leaks |
| Caches | Per-customer cache-accounting keys; OpenAI documents `prompt_cache_key` to separate accounting and prevent cache-hit probing ([OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18) | Billing opacity; side-channel probing |
| Rate/cost | Per-tenant token and $ budgets at the gateway | Denial of wallet; unfair allocation |
| Audit | Tenant-scoped views + platform immutable copy | Can't answer "what did our agents do" |

**[established]** the dimensions; **[unsettled]** fair allocation of shared prompt-cache costs across tenants — pick a policy (attribute by cache key) and put it in the contract.

---

## 5. Cost and latency levers

Cost is dominated by **input tokens × context length × turns**, so token/turn levers beat millisecond levers.

| Lever | Mechanism | Expected impact | Cost / risk |
|---|---|---|---|
| **Prompt caching** | Reuse stable prefix (system prompt, tools, examples, history) | Cache reads **0.1×** input price (0.05× on Anthropic Opus/Sonnet 5.5-class, 0.025× on Fable/Mythos 5.1-class); OpenAI **0.1× read / 1.25× write** on current GPT-5.6+ models; a documented multi-turn agent pattern reported **>90% cache-hit** ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18) | Writes cost more; 5-min (Anthropic) / 30-min (OpenAI GPT-5.6+) TTL; any dynamic prefix kills reuse |
| **Stable-prefix hygiene** | Static content first, dynamic last, append never rewrite | Turns ~30% hit rate into ~80–90% on long sessions | Requires prompt architecture + versioning |
| **Compaction / tool-result clearing** | Summarize near window limit; drop stale raw output | ~40–70% context reduction on long runs (~) | Loses detail; tuned on real traces; resets cache on next call ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), accessed 2026-10-18) |
| **Model routing/cascade** | Small model for easy turns, escalate on confidence/failure | ~50–80% cost cut with equal quality when routed well (~) | Two models to eval/monitor; routing errors visible ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [RouteLLM](https://arxiv.org/abs/2406.18665), accessed 2026-10-18) |
| **Parallel tool calls** | Independent calls in one turn | Wall clock ≈ max instead of sum (~2–5× on fan-out) | Concurrency load; ordering must be explicit |
| **Deferred tool loading** | Load relevant tool definitions only | Large static schemas leave every request | Extra round trip; selection errors ([Anthropic/MCP](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)) |
| **Batch APIs** | Async bulk at provider discount | Historically ~50% cheaper, higher latency | Not interactive; **[unsettled] verify current %** ([Anthropic batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing), [OpenAI batch](https://developers.openai.com/api/docs/guides/batch)) |
| **Hard budget caps + output discipline** | Per-run/user/tenant ceilings; structured outputs, max tokens, stop sequences | Unbounded-cost incidents become bounded | Enforce at gateway, never via prompt ([budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/)) |

**Order of attack:** measure cache-hit rate and cost per successful task → stabilise prefix → cap budgets → compact long runs → route easy turns → batch non-interactive work. Most teams recover 50–80% of spend from the first three.

---

## 6. Deployment and infrastructure

**Serverless vs workers.** AWS Lambda caps a single invocation at **15 minutes** (90-minute async only for managed instances), and durable functions cap at 30,000 operations per execution ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18). Agent runs routinely exceed that or wait hours on humans. Therefore four tiers: stateless **API/edge** (streams, no loop), **orchestration** (durable engine owns state), **execution workers** (tools/sandboxes, scale on queue depth), and **sandbox** (ephemeral, network-restricted). This is your order-processing shape; the new part is that **step count is model-chosen**, so queue-depth scaling must be paired with step and budget caps.

**Sandbox providers:** E2B ([docs](https://docs.e2b.dev), accessed 2026-10-18); Daytona ([docs](https://www.daytona.io/docs/en/), accessed 2026-10-18); AWS Lambda MicroVMs ([quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)); self-hosted microVM if you already run a hardened container platform. Select on cold-start, egress granularity, snapshot/persistence, secret-injection model, per-tenant isolation guarantee, log export, and compliance boundary.

**Browser automation:** isolated browser session per tenant, credential brokering (never type customer passwords from model context), DOM-level action logging, domain allowlist, session recording for disputes. **[unsettled]** least standardised layer; expect Playwright + hosted sessions.

**Memory/vector stores:** namespace/index per tenant for regulated customers; shared index + mandatory filter only for low-sensitivity tiers, with tests proving tool arguments cannot bypass the filter. Memory needs TTL, provenance, user-visible edit/delete (GDPR), and a hard rule that retrieved content never becomes system instructions. Evaluate retrieval recall@k and answer groundedness separately — a bad index looks like a bad model.

---

## 7. Governance and compliance

### 7.1 EU AI Act — the 2026 timetable

The Commission page is now explicit: in force 2024-08-01, applicable **2026-08-02** with exceptions; the **AI Omnibus** was adopted 2025-11-19, politically agreed 2026-05-07, **in force 2026-07-27**, moving Annex III high-risk to **2027-12-02** and Annex I product-embedded high-risk to **2028-08-02** ([European Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai), accessed 2026-10-18; [Omnibus text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744); Parliament's final approval 2026-06-16 per [Morgan Lewis](https://www.morganlewis.com/zh-cn/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know), accessed 2026-10-18).

| Date | Obligation | Impact |
|---|---|---|
| 2025-02-02 | Prohibitions (1–8), AI literacy | No social scoring, manipulative practices, workplace emotion recognition |
| 2025-08-02 | GPAI obligations + governance | Upstream providers comply; you inherit artefacts/contracts |
| **2026-08-02** | **Main applicability; AI Office enforcement** | Document requests, model evaluation, corrective measures, fines ([Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)) |
| 2026-08 | Transparency (chatbot disclosure, content marking) | UI must disclose AI interaction; marking Code of Practice exists |
| 2026-12-02 | "Nudification" ban; watermarking transition ends | Content safety and provenance controls |
| **2027-12-02** | Annex III high-risk (employment, credit, education, critical infra…) | If your agent decides anything about people: logging, human oversight, risk management, technical documentation |
| 2028-08-02 | Annex I product-embedded high-risk | Only for regulated products |

**Opinionated read:** the delay is a scheduling reprieve, not a scope reduction. Build **logging, human oversight and risk-management artefacts now** — the §2/§3.5 trace and audit investments *are* the compliance evidence. Note also the July 2026 Cybersecurity and AI action plan and planned EU model-evaluation capacity by 2027 ([Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)): expect third-party model evaluation in procurement.

### 7.2 NIST AI RMF and ISO/IEC 42001

**NIST AI RMF 1.0** (2023-01-26) plus the **Generative AI Profile** (NIST-AI-600-1, 2024-07-26); NIST states RMF 1.0 **is being revised** under the White House AI Action Plan, and released a Critical Infrastructure profile concept note on 2026-04-07 ([NIST](https://www.nist.gov/itl/ai-risk-management-framework), accessed 2026-10-18; [AI 600-1](https://doi.org/10.6028/NIST.AI.600-1)). Use it as a **control taxonomy** (Govern/Map/Measure/Manage) mapped to SOC 2. **[unsettled]** the revision will change vocabulary; don't hard-code clause numbers into contracts.

**ISO/IEC 42001:2023** specifies an AI Management System with PDCA-style continual improvement (51 pages, JTC 1/SC 42); pair with **ISO/IEC 42005:2025** for AI impact assessment ([ISO](https://www.iso.org/standard/42001), accessed 2026-10-18). This is the certification enterprise procurement is most likely to demand in 2027.

### 7.3 SOC 2, licensing, agent registry

**SOC 2 Type II** stays the baseline; agent-specific additions are subprocessors covering model and sandbox vendors, retention/deletion for prompts and traces, change management for prompts and model versions, and access control on the eval/observability platform itself.

**Licensing:** meter per run or per seat with **auditable** counters enforced at the gateway (the model must not be able to talk past a license check); derive per-tenant cost from `app.cost.usd` span attributes.

**Agent registry:** emerging but already visible in standards — OTel recommends provider-assigned agent IDs such as AWS Bedrock agent ARNs or GCP Agent Registry identifiers in `gen_ai.agent.id` ([agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18). Build an internal registry now: owner, business purpose, model + tools + data scopes, eval status, last review, risk tier. It is the first artefact auditors request. **[unsettled]** no dominant registry standard; expect convergence over 2027.

---

## 8. Production-readiness checklist (38 items)

**Evaluation**
1. Private eval set of ≥30 cases from real requests, versioned in git.
2. pass^k (k≥3) reported for every release alongside pass@1.
3. Deterministic assertions preferred; judges only where ground truth is unavailable.
4. Every judge has a rubric, a 30–50 item human-labelled set, and a documented agreement score.
5. Trajectory checks (tools, args, policy, steps) exist for every multi-step agent.
6. Cost and latency asserted in CI, not only quality.
7. Every production incident becomes a regression case within one sprint.

**Observability**
8. OTel GenAI semconv adopted with a pinned version and one internal emission layer.
9. Every span carries tenant ID, agent ID/version, model, prompt version, cost.
10. Content capture is opt-in, redacted, short-TTL, access-logged.
11. Audit log is separate from debug traces and append-only.
12. Dashboards cover pass^k trend, cost per successful task, cache-hit rate, tool error rate, approval queue age.
13. Alerts fire on judge-score drift and refusal-rate spikes, not only 5xx.
14. OTLP/JSON export tested — no vendor lock on evidence.

**Security**
15. Lethal-trifecta audit done per agent; at least one leg removed or gated.
16. Tools use least-privilege, short-lived credentials; no ambient secrets.
17. MCP servers allowlisted, digest-pinned, reviewed like code.
18. MCP auth uses audience-bound tokens with no token passthrough.
19. Tool output treated as untrusted data; no auto-execution of retrieved instructions.
20. Irreversible actions require human approval with a concrete action diff.
21. Code execution and browsing run in ephemeral, egress-restricted sandboxes with no cloud credentials.
22. Cross-tenant probes are automated tests, not code-review conventions.
23. Red-team corpus runs in CI and is refreshed regularly.
24. AI-BOM covers models, MCP servers, and agent packages.

**Reliability**
25. Agent loop runs on a durable engine with replay, not an in-process loop.
26. Every tool call has an idempotency key persisted before invocation.
27. Timeouts are per-model/per-tool from measured p99; every run has a wall-clock deadline.
28. Circuit breakers exist per provider+model and per critical tool.
29. HITL is durable suspend/resume, never a blocked thread or held request.
30. Per-tenant rate limits and quotas protect interactive traffic from batch load.

**Cost, tenancy, governance**
31. Hard token/$ caps per run, user and tenant enforced at the gateway; cache-hit rate is a monitored SLO.
32. Per-tenant data, credential, memory/index and cache-accounting isolation documented and tested.
33. Agent registry entry exists (owner, purpose, model, tools, data scopes, risk tier, review date).
34. EU AI Act classification recorded per agent with logging/oversight evidence mapped to obligations.
35. NIST AI RMF / ISO 42001 control mappings exist for procurement questionnaires.
36. Release includes a model/prompt eval gate and a documented rollback.
37. Runbooks exist for provider outage, runaway loop, injection incident, cross-tenant suspicion, cost spike.
38. Cost attribution per tenant/feature reconciles monthly against invoices.

---

## 9. Top 10 anti-patterns

1. **Demo-driven development** — shipping what looked good in five cherry-picked chats; pass^k collapses on trials 6–8 ([τ-bench](https://arxiv.org/abs/2406.12045)).
2. **Leaderboard-as-quality-proof** — SWE-bench/GAIA numbers offered as evidence your product is safe or correct.
3. **Uncalibrated judge as sole oracle** — documented position/verbosity/self-enhancement biases drift your metric silently ([MT-Bench](https://arxiv.org/abs/2306.05685)).
4. **Blocking a thread for human approval** — ties up workers, breaks on deploy, loses state ([Temporal patterns](https://docs.temporal.io/evaluate/use-cases-design-patterns)).
5. **Blind retries on non-idempotent tools** — the duplicate-refund incident.
6. **One agent with private data, untrusted input and egress** — the lethal trifecta, shipped deliberately ([Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)).
7. **Secrets in the prompt or system instructions** — they surface in traces, logs and output; resolve secrets inside the tool boundary ([OWASP 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)).
8. **Unbounded loops with no step/budget cap** — denial of wallet; OWASP 2026 raised Unbounded Consumption four places ([preface](https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md)).
9. **Tenancy as a row filter only** — no per-tenant queues, keys, caches or memory namespaces.
10. **Vacuum observability** — capturing everything with no retention or access policy: a PII liability and an audit finding that still cannot explain failures because content is unlabelled.

---

## 10. Established vs unsettled, and what to verify

**Established:** OTel-style tracing as the model; prompt-caching mechanics and multipliers; durable-execution patterns for long loops; idempotency keys + backoff + circuit breakers; batch APIs; least privilege and sandbox isolation; eval datasets plus regression suites; the EU AI Act dates and the 2026 Omnibus delay; ISO/IEC 42001 as an AIMS.

**Unsettled / verify before committing:**
- **OTel GenAI semconv stability** — all agent spans are `Development`; names will change. Pin, wrap, expect migration ([spec](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)).
- **Prompt-injection defences** — capability separation, dual-LLM and "rule of two" are promising, not proven at enterprise scale. Never promise customers "injection-proof".
- **Agentic Top 10 IDs/scope** — use as taxonomy; verify ASI numbering against the published PDF.
- **Batch discounts and cache pricing** — percentages here are as documented on 2026-10-18; re-check pricing pages before financial modelling.
- **NIST AI RMF revision** — vocabulary may change; keep control mapping abstract.
- **WebArena/AgentBench leaderboards** — not re-verified for 2026; orientation only.
- **Cost-reduction "~" numbers** — practitioner estimates; measure on your own traces.
- **Agent identity/authorisation standards** — converging (MCP OAuth 2.1, AAIF governance) but not settled; design for swap-ability.

---

## Appendix: primary sources (all accessed 2026-10-18)

**Evals:** [τ-bench](https://arxiv.org/abs/2406.12045) · [SWE-bench](https://github.com/SWE-bench/SWE-bench) · [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) · [Terminal-Bench](https://www.tbench.ai/) · [GAIA](https://arxiv.org/abs/2311.12983) · [WebArena](https://arxiv.org/abs/2307.13854) · [AgentBench](https://arxiv.org/abs/2307.10928) · [LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) · [RouteLLM](https://arxiv.org/abs/2406.18665)

**Observability:** [OTel GenAI repo](https://github.com/open-telemetry/semantic-conventions-genai) · [OTel GenAI docs](https://opentelemetry.io/docs/specs/semconv/gen-ai/) · [LangSmith](https://docs.langchain.com/langsmith/observability) · [Langfuse](https://langfuse.com/docs) · [Braintrust](https://www.braintrust.dev/docs) · [Arize Phoenix](https://arize.com/docs/phoenix) · [W&B Weave](https://docs.wandb.ai/weave) · [LangWatch](https://langwatch.ai)

**Security:** [OWASP LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) · [OWASP source](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final) · [OWASP Agentic 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · [AIBOM](https://github.com/GenAI-Security-Project/aibom-generator) · [Lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) · [MCP security](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) · [MCP → AAIF](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)

**Reliability/infra:** [Temporal](https://docs.temporal.io/evaluate/use-cases-design-patterns) · [Inngest](https://www.inngest.com/platform/durable-execution) · [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) · [Circuit Breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) · [Backoff/jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) · [E2B](https://docs.e2b.dev) · [Daytona](https://www.daytona.io/docs/en/)

**Cost/latency:** [Anthropic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) · [OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching) · [Anthropic batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing) · [OpenAI batch](https://developers.openai.com/api/docs/guides/batch) · [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [Budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/)

**Governance:** [EU Commission AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) · [AI Act text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689) · [Omnibus text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744) · [Morgan Lewis](https://www.morganlewis.com/zh-cn/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know) · [GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) · [NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1) · [ISO/IEC 42001](https://www.iso.org/standard/42001)
