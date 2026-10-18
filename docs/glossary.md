# Glossary

**Purpose:** the canonical term list for this curriculum. A strong agent engineer should be able to define every term below *without notes*. This file is the source for the weekly flashcards (`docs/plan/flashcards/`) and for the teach-back gate in [`CHECKPOINTS.md`](plan/CHECKPOINTS.md).

**How to use it (not as a reading list):**

1. Do **not** read it top-to-bottom. Read only the group for the week you are on.
2. Cover the "Definition" column and try to produce it from the term, then check yourself. That is retrieval practice, not re-reading.
3. If you cannot explain a term in one sentence to a colleague, mark it and ask the AI tutor to quiz you on it.
4. A term is "learned" when you can also give one failure mode it prevents. The "Why it matters" column is the seed for that sentence.

**Legend:** Week links point to that week's quiz (`docs/plan/quizzes/`). Terms marked **SendOS** are specific to the C# platform you work on; the rest are industry vocabulary.

---

## 1. Model & API surface (Week 1)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **Token** | A subword unit produced by the model's tokenizer; the unit of billing and context accounting. | Every cost, limit and latency estimate is in tokens, never characters or words. | [W1](plan/quizzes/week01.md) |
| **Context window** | Maximum tokens the model can attend to in one request (input + generated output). | Exceeding it fails requests or forces truncation; it is the resource context engineering manages. | [W1](plan/quizzes/week01.md) |
| **Temperature** | Sampling randomness: lower = more deterministic, higher = more diverse. | Affects reproducibility of tests and evals more than it affects "creativity". | [W1](plan/quizzes/week01.md) |
| **`finish_reason`** | Why generation stopped: `stop`, `length`, `tool_calls`, `content_filter`. | It is how the loop decides whether to continue, fail or parse output. | [W1](plan/quizzes/week01.md) |
| **Streaming (SSE)** | Server-Sent Events: incremental delivery of deltas over one HTTP response. | Needed for latency feel and for cancelling runaway generations; it is a protocol, not a feature. | [W1](plan/quizzes/week01.md) |
| **Delta assembly** | Accumulating streamed chunks into a complete message, including partial tool-call arguments. | The most common streaming bug: tool arguments arrive fragmented across chunks. | [W1](plan/quizzes/week01.md) |
| **Exponential backoff + jitter** | Retry delay growing exponentially with randomisation to avoid synchronised retry storms. | Correct retries make an adapter reliable; naive retries multiply outages and cost. | [W1](plan/quizzes/week01.md) |
| **`Retry-After`** | Server hint, in seconds, for when to retry a 429/503. | Ignoring it turns rate limiting into a self-inflicted denial of service. | [W1](plan/quizzes/week01.md) |
| **Error taxonomy** | Classification of failures into retryable (429, 5xx, transport) vs terminal (400, auth, content policy). | Retrying a terminal error burns budget and hides the real bug. | [W1](plan/quizzes/week01.md) |
| **Provider seam** | An interface behind which each model provider is an adapter. | The seam is what lets you swap models, mock them in tests, and add budget-aware routing later. | [W1](plan/quizzes/week01.md) |
| **Usage accounting** | Recording input/output/cached tokens per call and converting to cost. | You cannot evaluate or budget an agent you cannot price. | [W1](plan/quizzes/week01.md) |

## 2. Structured output & prompts (Week 3)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **JSON Schema** | A declarative contract describing the shape of a JSON value. | It is the shared language between your pydantic models and the model provider. | [W3](plan/quizzes/week03.md) |
| **JSON mode** | Provider setting that guarantees *syntactically valid* JSON — not schema compliance. | "Valid JSON" still fails your schema; you must validate. | [W3](plan/quizzes/week03.md) |
| **Structured outputs** | Provider-enforced schema adherence (e.g. `json_schema`, strict mode). | Stronger than JSON mode, but limits schema features and provider support. | [W3](plan/quizzes/week03.md) |
| **Constrained decoding** | Decoding restricted by a grammar so invalid tokens cannot be emitted. | The strongest guarantee; explains why "impossible-to-emit" beats "validate-after". | [W3](plan/quizzes/week03.md) |
| **Discriminated union** | A union of schemas distinguished by a required tag field (e.g. `kind`). | The clean way to model a decision family with different payloads. | [W3](plan/quizzes/week03.md) |
| **Validation-repair loop** | On schema failure, feed the validation error back once and retry with a bounded attempt count. | Recovers most malformed outputs without hiding failure rates. | [W3](plan/quizzes/week03.md) |
| **Schema failure rate** | Fraction of calls whose output fails validation (before and after repair). | A first-class metric; it turns a "working" feature into an observable one. | [W3](plan/quizzes/week03.md) |
| **Prompt versioning** | Prompts are immutable assets carrying `id` and `version` — editing history is forbidden, you bump the version instead. | Prompt edits are code changes; unversioned prompts make regressions unattributable. | [W3](plan/quizzes/week03.md) |
| **Presentation budget** | Hard caps on how much text a decision may show (e.g. headline ≤ 12 words, ≤ 4 next moves). | Prevents the model from ignoring product constraints on brevity. | [W3](plan/quizzes/week03.md) |
| **Cassette (record/replay)** | A recorded real interaction replayed in tests for deterministic offline runs. | Gives you one real-payload test without network flakiness. | [W3](plan/quizzes/week03.md) |

## 3. Loop & tools (Week 2)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **`tool_call`** | The model's request to run a named tool with JSON arguments, carrying an `id`. | The `id` is how you match the tool result back to the request. | [W2](plan/quizzes/week02.md) |
| **Native tool calling** | Provider-supported structured tool requests rather than parsing text. | More reliable than text parsing; the first architectural improvement over naive ReAct. | [W2](plan/quizzes/week02.md) |
| **ReAct** | Reasoning + acting loop: model emits a thought/action, environment returns an observation, repeat. | The fundamental agent loop; every framework is a variant of it. | [W2](plan/quizzes/week02.md) |
| **Tool registry** | A runtime mapping from tool name to schema + handler + metadata (read/write, risk). | One place for discovery, validation, recording and policy — instead of ad-hoc `if` branches. | [W2](plan/quizzes/week02.md) |
| **Error as observation** | Tool failures are returned to the model as observations rather than raised to the caller. | Lets the agent recover; a crashed loop cannot. | [W2](plan/quizzes/week02.md) |
| **Parallel tool calls** | Multiple tool requests in one assistant turn. | Fewer round-trips and lower latency — but only if handlers are independent and idempotent. | [W2](plan/quizzes/week02.md) |
| **`max_steps` / iteration budget** | Hard cap on loop iterations. | The primary runaway-cost control; every production loop has one. | [W2](plan/quizzes/week02.md) |
| **Stop condition** | The predicate that ends the loop: final answer, budget exhausted, max steps, no progress. | Loops that only end on "final answer" hang forever when the model stalls. | [W2](plan/quizzes/week02.md) |
| **Budget check at the top** | Verifying token/cost budget *before* each model call, not after. | Checking after the fact means you always overspend by one full turn. | [W2](plan/quizzes/week02.md) |
| **Step trace** | Structured events emitted per loop step (model call, tool call, result, stop). | Tracing is how you debug stochastic systems; it must be designed in, not logged ad hoc. | [W2](plan/quizzes/week02.md) |
| **Agent vs workflow** | Workflow = LLM steps on predefined code paths; agent = model directs its own process and tools. | The central architectural choice; most "agent" use cases should be workflows. | [W2](plan/quizzes/week02.md) |
| **ACI (agent-computer interface)** | The designed surface of tools, feedback and errors the model interacts with. | SWE-agent showed ACI design changes benchmark scores more than model swaps. | [W2](plan/quizzes/week02.md) |
| **Write tool / `is_write`** | A tool with side effects, marked explicitly so policy can gate it. | Side effects are where trust and audit requirements begin. | [W2](plan/quizzes/week02.md) |

## 4. Context engineering & memory (Week 4)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **Context engineering** | Curating the smallest high-signal token set for the next model call. | It is the craft that replaced prompt engineering for multi-turn agents. | [W4](plan/quizzes/week04.md) |
| **Context rot** | Degradation of recall/accuracy as context length grows. | Explains why dumping everything into 1M tokens still fails. | [W4](plan/quizzes/week04.md) |
| **Compaction** | Summarising old turns into a bounded carry-forward note and restarting with it. | The first lever for long-horizon coherence. | [W4](plan/quizzes/week04.md) |
| **Carry-forward note** | The durable summary a compactor writes: decisions, open bugs, constraints. | What survives compaction defines what the agent can still do. | [W4](plan/quizzes/week04.md) |
| **Structured note-taking** | Agent writes progress to an external file (e.g. `NOTES.md`) and rereads it later. | Turns context from a scratchpad into a recoverable log. | [W4](plan/quizzes/week04.md) |
| **Priority classes** | Ranking context by value: pinned constraints > task state > recent turns > observations > history. | Makes eviction decisions principled rather than "drop the oldest". | [W4](plan/quizzes/week04.md) |
| **Progressive disclosure** | Loading detail on demand rather than all at once (files, links, search results). | Keeps context small while preserving access to depth. | [W4](plan/quizzes/week04.md) |
| **Filesystem as context** | Using paths, names and directory structure as navigational metadata for retrieval. | Cheaper and fresher than a vector index for file-shaped knowledge. | [W4](plan/quizzes/week04.md) |
| **Sub-agent context isolation** | Workers explore with their own context and return a distilled summary. | The main way to do deep work without polluting the lead agent's window. | [W4](plan/quizzes/week04.md) |
| **Episodic memory** | Per-run summaries stored for later recall ("what happened last time"). | Enables cross-session continuity without replaying transcripts. | [W4](plan/quizzes/week04.md) |
| **Semantic memory** | Durable facts with provenance ("customer X is on plan Y"). | Facts outlive sessions; provenance makes them auditable. | [W4](plan/quizzes/week04.md) |
| **Provenance** | Where a remembered fact came from and when. | Memory without provenance cannot be trusted or revoked. | [W4](plan/quizzes/week04.md) |
| **RAG (retrieval-augmented generation)** | Retrieving relevant documents and placing them in context before generating. | One retrieval strategy among several; agents often prefer search tools. | [W4](plan/quizzes/week04.md) |
| **Embedding & cosine similarity** | Vector representation and the similarity metric used to rank chunks. | The core of semantic retrieval; know the failure mode (semantic near-miss). | [W4](plan/quizzes/week04.md) |
| **Retention test** | An explicit test that pinned constraints survive compaction at ≥ a target rate. | Turns "it seems to remember" into a measurable gate. | [W4](plan/quizzes/week04.md) |

## 5. MCP & protocols (Week 5)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **MCP (Model Context Protocol)** | An open standard for exposing tools, resources and prompts to AI applications. | The interoperability layer; it replaces bespoke per-integration glue. | [W5](plan/quizzes/week05.md) |
| **Host / client / server** | Host runs the app and model; client is the per-server connector; server exposes capabilities. | Getting the roles right is the difference between a clean integration and a security hole. | [W5](plan/quizzes/week05.md) |
| **Tools vs resources vs prompts** | MCP's three primitives: callable actions, readable data, reusable prompt templates. | Choosing the wrong primitive exposes action capability where only data was needed. | [W5](plan/quizzes/week05.md) |
| **stdio transport** | Local MCP transport over a child process's standard I/O. | The simplest, fastest path to a working server; not a network boundary. | [W5](plan/quizzes/week05.md) |
| **Streamable HTTP transport** | Remote MCP transport over HTTP with streaming responses. | Required for multi-client/cloud deployments; changes auth and trust requirements. | [W5](plan/quizzes/week05.md) |
| **MCP stateless revision (2026-07-28)** | MCP removed the `initialize` handshake and protocol session; every request carries version/identity in `params._meta` and servers answer `server/discover`. | Tutorials that still show `initialize` describe the pre-2026 dialect; the 2026 server/client in `agentlab/mcp/` is stateless. | [W5](plan/quizzes/week05.md) |
| **Tool poisoning** | A malicious tool description that injects instructions into the model's context. | Descriptions are untrusted input; digest-pinning and review are mitigations. | [W5](plan/quizzes/week05.md) |
| **Description digest pinning** | Recording a hash of a tool's description/schema and refusing silent changes. | Detects rug-pull attacks where a server mutates tool semantics after approval. | [W5](plan/quizzes/week05.md) |
| **OAuth audience binding** | Tokens are scoped to the intended recipient service. | Prevents a token minted for one server being replayed against another. | [W5](plan/quizzes/week05.md) |
| **Confused deputy** | A privileged component tricked into acting on an attacker's behalf. | The core risk of granting an agent broad tool authority. | [W5](plan/quizzes/week05.md) |

## 6. Orchestration, planning & approval (Week 6)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **Orchestrator-worker** | A lead agent decomposes work and delegates to workers, then synthesises. | The one multi-agent pattern with strong production evidence — when the task is genuinely parallelisable. | [W6](plan/quizzes/week06.md) |
| **Specialist** | A sub-agent with a narrow toolset and isolated context. | Isolation is what makes delegation safer and cheaper than one giant context. | [W6](plan/quizzes/week06.md) |
| **Squad** | A bounded group of specialists coordinated for one objective. | SendOS's unit of multi-agent work; the miniature you rebuild in week 6. | [W6](plan/quizzes/week06.md) |
| **Typed plan** | A structured plan: workstreams, dependencies, acceptance criteria. | Makes plans validatable and replannable instead of prose. | [W6](plan/quizzes/week06.md) |
| **DAG validation** | Checking the plan's dependencies are acyclic and closed over known kinds. | Cycles and dangling dependencies are the plan equivalent of infinite loops. | [W6](plan/quizzes/week06.md) |
| **Replan** | Producing a new plan after a failed step, bounded in retries. | Plans fail; the ability to replan is what separates orchestration from scripting. | [W6](plan/quizzes/week06.md) |
| **Topology classifier** | Rules that map problem shape to execution shape (direct → single specialist → squad → multi-squad). | Prevents both over-engineering (squad for one call) and under-powering. | [W6](plan/quizzes/week06.md) |
| **Execution shape** | The chosen structure for a run: direct capability, single specialist, single squad, multi-squad. | The architecture decision that determines cost, latency and control surface. | [W6](plan/quizzes/week06.md) |
| **Smallest sufficient shape** | The least complex topology that can satisfy the task; unbacked shapes are reported as limitations. | The plan's core rule: never guess a smaller shape, never build a bigger one. | [W6](plan/quizzes/week06.md) |
| **HITL (human-in-the-loop)** | A human approves or edits before a consequential action executes. | The control that makes write-capable agents acceptable in enterprises. | [W6](plan/quizzes/week06.md) |
| **Durable suspend/resume** | Persisting a paused run and resuming it on an external callback. | This is the difference between a demo approval and a real one. | [W6](plan/quizzes/week06.md) |
| **Approval binding** | A proposal bound to actor, tenant, action hash, authority snapshot and expiry. | Without binding, an approved proposal can be swapped, replayed or executed by the wrong principal. | [W6](plan/quizzes/week06.md) |
| **Action hash** | A digest of exactly what will be executed, checked at approval and execution time. | Detects post-approval edits. | [W6](plan/quizzes/week06.md) |
| **Authority snapshot** | The permission state captured when approval was granted. | Authority can change between approval and execution; the snapshot is the contract. | [W6](plan/quizzes/week06.md) |
| **At-most-once execution** | A guarantee that an approved action runs no more than once, even on retries. | Duplicate side effects are worse than a failed request. | [W6](plan/quizzes/week06.md) |
| **CAS (compare-and-swap)** | Conditional write used to prevent double-resume/double-execute. | The standard primitive for at-most-once under concurrency. | [W6](plan/quizzes/week06.md) |

## 7. Evals & observability (Week 7)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **Eval dataset** | Versioned cases (inputs, rubric, expected constraints) used to score an agent. | Evals are code and data, not a vibe check; version them. | [W7](plan/quizzes/week07.md) |
| **Outcome eval** | Scores only the final result. | Cheap and objective, but blind to how the agent got there. | [W7](plan/quizzes/week07.md) |
| **Trajectory eval** | Scores the path: tool choices, steps, constraints respected. | Needed when process compliance matters (security, approvals). | [W7](plan/quizzes/week07.md) |
| **Deterministic-first scoring** | Exhaust exact checks (schema, substring, exit code) before calling a judge. | Cheaper, faster and more reliable than model judgement. | [W7](plan/quizzes/week07.md) |
| **Rubric** | Explicit criteria and levels used to score an output. | Makes qualitative judgement reproducible and debuggable. | [W7](plan/quizzes/week07.md) |
| **LLM-as-judge** | A model scores outputs against a rubric, usually with forced JSON. | Scales qualitative grading; must be calibrated, never trusted blindly. | [W7](plan/quizzes/week07.md) |
| **Judge agreement** | How often the judge matches human labels on a sample. | The only credibility a judge has; below ~80% it is noise. | [W7](plan/quizzes/week07.md) |
| **pass@1** | Probability the agent succeeds on one attempt. | The standard headline metric for agent tasks. | [W7](plan/quizzes/week07.md) |
| **pass^k** | Probability of succeeding on *all* of k independent attempts. | Exposes reliability: a 70% pass@1 agent may be far worse at pass^5. | [W7](plan/quizzes/week07.md) |
| **Eval leakage** | Tuning on the eval cases until they no longer predict real performance. | The most common way eval suites become theatre. | [W7](plan/quizzes/week07.md) |
| **Regression gate** | A CI check that fails when a metric drops below baseline. | Converts evals from a report into a control. | [W7](plan/quizzes/week07.md) |
| **Trace / span** | Structured record of a run and its timed sub-operations. | Traces are the primary debugging and eval substrate. | [W7](plan/quizzes/week07.md) |

## 8. Security & governance (Week 8)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **Direct prompt injection** | The user's message overrides the developer's instructions. | The oldest attack; instruction hierarchy and output vetting are the mitigations. | [W8](plan/quizzes/week08.md) |
| **Indirect prompt injection** | Malicious instructions arrive via content the agent reads (web page, file, tool result, email). | The dominant real-world attack on tool-using agents. | [W8](plan/quizzes/week08.md) |
| **Lethal trifecta** | Private data + untrusted content + external communication in one agent. | Any two are manageable; all three is exfiltration by design. | [W8](plan/quizzes/week08.md) |
| **Instruction hierarchy** | Explicit precedence between system, developer, user and untrusted content. | Makes injection a policy violation rather than a coin flip. | [W8](plan/quizzes/week08.md) |
| **Sandbox** | A confined execution environment (paths, time, size, process/container boundary). | Tool execution is code execution; confinement is the only reliable control. | [W8](plan/quizzes/week08.md) |
| **Path allowlist** | Explicitly permitted filesystem roots for read/write tools. | Blocks traversal attacks without needing perfect prompt hygiene. | [W8](plan/quizzes/week08.md) |
| **Deny-by-default** | Start from no permission and require explicit grants. | The only safe default for autonomous systems. | [W8](plan/quizzes/week08.md) |
| **Authority intersection** | Effective permission = intersection over independent grants, never union. | Prevents one source (or the model) from widening access. | [W8](plan/quizzes/week08.md) |
| **Effective authority** | The computed permission set actually enforced for this action. | The object every check should consult; one implementation, one truth. | [W8](plan/quizzes/week08.md) |
| **Per-tenant scoping** | Every object, cache entry and budget is scoped to one tenant. | Multi-tenant leakage is the fastest way to lose enterprise trust. | [W8](plan/quizzes/week08.md) |
| **Audit log** | Append-only record of actions with before/after evidence and correlation ids. | Audit is evidence, not debugging output; it must be tamper-evident. | [W8](plan/quizzes/week08.md) |
| **Correlation id** | An id propagated across services to join logs, traces and audit rows. | Without it, incident reconstruction is guesswork. | [W8](plan/quizzes/week08.md) |
| **Credential isolation** | Secrets never reachable from the sandbox where generated code runs. | On injection, the agent cannot exfiltrate what it cannot read. | [W8](plan/quizzes/week08.md) |
| **Red-team suite** | A repeatable set of attacks run against the system, with before/after results. | Security claims need tests; a suite is how you know a control works. | [W8](plan/quizzes/week08.md) |
| **EU AI Act (GPAI / high-risk)** | Regulation with obligations phased in: general-purpose AI live from Aug 2026, high-risk from Dec 2027. | Enterprise agent platforms will be asked for evidence; know the timeline. | [W8](plan/quizzes/week08.md) |

## 9. SendOS-specific (your day job)

| Term | Definition | Why it matters | Week |
|---|---|---|---|
| **SendOS** | The enterprise .NET agent platform you intern on: decision-first runtime, capability registry, governed assets, traces and a learning loop. | The curriculum exists to make this codebase legible rather than magic. | [W6](plan/quizzes/week06.md) |
| **`Send.Model.Adapter`** | SendOS's provider layer: adapters per model plus routed completion. | Your week-1 provider seam is the same idea; compare what it adds (budget-aware routing, structured completion). | [W1](plan/quizzes/week01.md) |
| **`DecisionRuntime`** | SendOS's decision-first execution runtime that produces typed decisions rather than chat replies. | The architectural centre of gravity of the platform; week 6 rebuilds a miniature. | [W6](plan/quizzes/week06.md) |
| **`DecisionInteraction` family** | The typed decision set: clarification, direct answer, decision, recommendation, action proposal. | Structured outputs are how a platform makes model behaviour governable. | [W3](plan/quizzes/week03.md) |
| **`PresentationBudgetEnforcer`** | SendOS component that enforces output shape limits (headline length, number of next moves). | Shows that product constraints can be enforced structurally, not politely asked for. | [W3](plan/quizzes/week03.md) |
| **`IStructuredCompletionHandler`** | SendOS's interface for schema-gated completions. | Week 3's `analyze(text) -> Decision` is its miniature. | [W3](plan/quizzes/week03.md) |
| **Capability / `CapabilityDefinition`** | A declared action with schema, risk level, read/write flag and approval requirement. | Capabilities are the unit of tool governance; week 2's registry grows into this. | [W2](plan/quizzes/week02.md) |
| **`ICapabilityManifestProvider`** | SendOS's connector-manifest source that feeds the capability registry. | Contrast with MCP discovery: manifest-based governance vs protocol-based discovery. | [W5](plan/quizzes/week05.md) |
| **`TopologyClassifier`** | SendOS component that selects execution shape from problem topology. | Week 6 rebuilds the rule; it is the best example of architecture-as-decision. | [W6](plan/quizzes/week06.md) |
| **`ExecutionPlan` / `ExecutionShape`** | The typed plan and the chosen structural shape for a run. | Explains how SendOS avoids both over- and under-orchestration. | [W6](plan/quizzes/week06.md) |
| **`ApprovalCheckpoint`** | SendOS's human approval gate: proposal persisted before approval, then executed at most once. | Week 6's approval state machine is its miniature; the security properties are the lesson. | [W6](plan/quizzes/week06.md) |
| **`ApprovalBinding`** | The binding of approval to actor, tenant, action hash, authority snapshot and expiry. | The mechanism that stops approval replay and post-approval edits. | [W6](plan/quizzes/week06.md) |
| **Governance sandwich** | SendOS's layering of ingress controls, runtime authority checks and egress/audit controls. | Explains why every control exists, and what removing one would break. | [W8](plan/quizzes/week08.md) |
| **`Send.Context.Gateway` / `SpecialistContext`** | SendOS's context gateway and the "least-context envelope" passed to specialists. | Data minimisation, not maximal recall — a different objective from a chatbot. | [W4](plan/quizzes/week04.md) |
| **`Outcome_Trace`** | Append-only trace contract emitted per run/step. | The runtime↔learning contract; week 7's trace store is its miniature. | [W7](plan/quizzes/week07.md) |
| **Trace → candidate → publish loop** | SendOS's learning loop: traces become eval cases, candidates are evidence-gated, humans publish. | Research flags this as the most obviously unwired mechanism — a credible contribution area. | [W7](plan/quizzes/week07.md) |
| **`CaseRuntime`** | SendOS's case-level runtime, including durable suspend/resume that is not fully wired. | The recommended capstone-inspired contribution: a working miniature plus a design proposal. | [W6](plan/quizzes/week06.md) |
| **`ActionIdempotencyStore`** | SendOS's store for deduplicating actions. | Enables at-most-once execution across retries; week 6 implements the CAS version. | [W6](plan/quizzes/week06.md) |

---

**Maintenance:** add a term only when a week introduces it; never let this list exceed the weeks it serves. If a term has no "why it matters" sentence, it is trivia — delete it.
