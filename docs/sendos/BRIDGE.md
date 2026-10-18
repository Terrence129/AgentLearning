# BRIDGE — the week-by-week SendOS reading bridge

**Living document.** One page per learning-plan week, each sized for a **30-minute** bridge session.
Read real SendOS code, answer three questions, write five bullets. No setup, no build, no network.

> **Code wins over docs.** Every path here was verified to exist on **2026-10-18** against the
> source checkout. Where a repo doc contradicts the code, this page follows the code and says so.
> Paths are **relative to the SendOS repo root** (`SendOs/`), not to this learning repo.
> Evidence base and status labels: [`CONCEPT-MAP.md`](./CONCEPT-MAP.md) (research §0–§7).
> Reading sequence: [`READING-ORDER.md`](./READING-ORDER.md). C# labs: [`../../dotnet/`](../../dotnet/).

---

## How to use this bridge (the 30-minute protocol)

| Minutes | Do | Why |
|---|---|---|
| 0–15 | Open the listed files. Read **headers, type declarations and validation branches** — not every method body | The API shape is the design; bodies are implementation detail you can return to |
| 15–25 | Answer the week's 3 questions **in writing, without looking anything up** | Retrieval practice; you discover what you only *recognised* |
| 25–28 | Check your answers against [Appendix A](#appendix-a--answers), correct in a different colour | Calibration |
| 28–30 | Write 5 bullets in your weekly note: **maps cleanly / differs / would change** | Becomes the "Transfer" gate for the week |

**Rule:** if the 30 minutes is all you have that week, this *is* the SendOS work. Do not skip it for
more tutorials — the plan weights this as goal A ("contribute faster"), and it compounds.

**Rule:** never paste production code into the learning repo. Cite `path:line`, quote at most a few
lines, and keep the learning repo's code your own.

---

## The framing: SendOS is ahead on governance, behind on orchestration ergonomics

This one sentence explains almost every difference you will find, and it is the most transferable
judgement in the bridge.

| SendOS is **ahead** of mainstream tutorials on… | …because production demanded it | Your lab already proves a miniature |
|---|---|---|
| Typed decisions instead of free text | A paragraph cannot be approved, audited or budgeted | `dotnet/StructuredDecisionBridge`; week-3 `agentlab/schemas/` |
| Approval binding (action hash, authority snapshot, expiry, at-most-once) | Double-execution and post-approval edits are real incidents | week 6 `agentlab/orchestrator/approval.py` |
| Authority as an intersection of independent boundaries | "The AI said I could" is not an authorisation | week 8 `agentlab/guard/authority.py` |
| Append-only outcome trace | Learning and audit both need history that cannot be rewritten | week 7 `agentlab/trace.py` |
| Human-gated publish of learned assets | A model must never change its own policy | week 7/9 evidence gate + publish |
| Version pinning of governed assets | A mid-flight publish must not mutate a running decision | week 6 asset resolution |

| SendOS is **behind** on… | Consequence in the repo | What to learn instead |
|---|---|---|
| Graph/state-machine orchestration runtime | Shape selection and dispatch live in a large procedural `DecisionRuntime` (5,379 lines) | LangGraph / Temporal / Microsoft Agent Framework, in week 9 comparison |
| Wired durable execution | `CaseRuntime` + `DecisionTask` are built and unit-tested but have no production caller | Temporal, DBOS, checkpoint-and-resume patterns |
| Observability stack | `TurnStage` enum is excellent; metrics/traces are stubs | OpenTelemetry GenAI conventions (week 7 stretch) |
| Learning loop connectivity | Distillation/Trainer/Evaluator are real code with a dry loop | Your capstone's trace → eval → candidate → publish is a design sketch for it |
| Provider-native constrained decoding | Hand-rolled JSON Schema subset instead | Structured outputs / grammars; measure the trade in week 3 |

**How to use the framing:** when a week's mechanisms feel over-engineered, ask *which incident paid
for this control*. When they feel incomplete, ask *which framework has already solved this*. Both
questions are interview answers.

---

## The six mechanisms worth rebuilding (and where each lives)

From [`CONCEPT-MAP.md` §4](./CONCEPT-MAP.md#4-where-a-from-scratch-build-teaches-the-most--six-mechanisms).
These are the highest-value transfers; every week's bridge touches at least one.

| # | Mechanism | Weeks | Built in this repo | SendOS reference |
|---|---|---|---|---|
| 1 | Typed decision family + bound approval gate | 3, 6 | `dotnet/StructuredDecisionBridge`; `agentlab/schemas/`, `agentlab/orchestrator/approval.py` | `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs`; `.../Application/Approval/ApprovalCheckpoint.cs` |
| 2 | Capability catalogue + fail-closed authority | 2, 8 | `agentlab/tools/registry.py`, `agentlab/guard/authority.py` | `.../Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs`; `.../Domain/Authority/EffectiveAuthority.cs`; `.../Application/Authority/AuthoritySources.cs` |
| 3 | Trace → eval → evidence-gated candidate → human publish | 7, 9 | `agentlab/trace.py`, `agentlab/evals/` | `apps/Send.Usage.Collector/src/.../Domain/*`; `apps/Send.LowerLayer.Worker/src/.../Distillation/*`, `.../Evaluation/*`; `.../PublishingPipeline/PublishingService.cs` |
| 4 | Schema-gated structured output + budget routing | 3, 8 | `dotnet/StructuredDecisionBridge`; `agentlab/providers/`, week-8 routing | `apps/Send.Model.Adapter/src/.../Structured/*`; `.../Handlers/CompletionHandler.cs` |
| 5 | Topology-driven shape selection | 6 | `agentlab/orchestrator/plan.py` | `.../Application/Planning/TopologyClassifier.cs`; `ExecutionPlanner.cs`; `docs/adrs/0001-*.md` |
| 6 | Append-only trace as the runtime↔learning contract | 7, 9 | `agentlab/trace.py` | `apps/Send.Usage.Collector/src/.../Domain/OutcomeTrace*`; `.../Application/Outcome/IOutcomeTraceEmitter.cs` |

---

## Week 1 — The model, demystified → `Send.Model.Adapter`

**You build:** the provider seam (`agentlab/providers/openai_compat.py`), payload/parse/stream/retry.
**C# lab:** [`dotnet/ProviderBridge`](../../dotnet/ProviderBridge/README.md) — same seam in .NET,
with an 11-check offline self-test.

### Read (SendOS)

| File | Look for |
|---|---|
| `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Interfaces/IProviderAdapter.cs` | The seam: what a provider adapter must do, and what it must not |
| `.../Infrastructure/ExternalServices/OpenAiProviderAdapter.cs` | Payload build, response parse, JSON-output mode, usage capture |
| `.../Infrastructure/ExternalServices/StructuredOutputDirective.cs` | How the SDK nudges JSON output without native schemas |
| `.../Application/Handlers/CompletionHandler.cs` | Retry/fallback/time-budget loop; `IsTransient` (only 502/504!), the `Declared` selection-order bug recorded at lines 78–85 |
| `.../Contracts/Routing/ModelBudget.cs` | The budget fields your lab does not enforce yet (week 8) |

### Questions

1. SendOS puts retry in `CompletionHandler`, not in the adapter. What does that placement make possible that an adapter-level retry cannot?
2. `CompletionHandler.IsTransient` returns true only for 502/504. Is that too narrow? What would you include, and what breaks if you are wrong in each direction?
3. Which of `ChatCompletionsClient`'s responsibilities map to `IProviderAdapter`, and which map to `CompletionHandler`?

### Maps cleanly · differs

- **Clean:** provider seam, payload/response translation, usage capture, provider-independent model id, wire-level retry.
- **Differs:** SendOS routes across *candidate models* with cost/latency/reliability policy, retries at the handler so a fallback can pick a different model, and requests provider JSON-output modes. Its `ModelCostProfile`/`ModelBudget` combination is week-8 material.

**Micro-action:** list every field `ModelBudget` carries and mark which your week-1 client ignores. That list is your week-8 to-do.

---

## Week 2 — Tools and the agent loop → `CapabilityDefinition` + registry

**You build:** the loop and tool registry (`agentlab/loop/`, `agentlab/tools/`).

### Read (SendOS)

| File | Look for |
|---|---|
| `apps/Send.Agent.Runtime/src/.../Domain/Capabilities/CapabilityDefinition.cs` | The fields a governed tool carries: risk, read/write, approval, side effects, idempotency, compensation, evidence kinds, action kind, result resource type, tenant availability, version, governed-asset reference |
| `.../Application/CapabilityRegistry/ICapabilityRegistry.cs` | `Match` vs `MatchByRequirements` vs `MatchByUnderstanding` — structural selection, not keyword overlap |
| `.../Application/CapabilityRegistry/CapabilityRegistry.cs` | Tenant scoping and the hard boundaries applied before anything is offered |
| `.../Application/Execution/DirectCapabilityHandler.cs` | The one fully-live execution shape: authorize → invoke → reason → compose |
| `.../Application/Execution/SemanticInputBinding.cs` | How a turn's values get bound onto declared inputs (and what "unbound" means) |

### Questions

1. Which `CapabilityDefinition` fields have no analogue in a plain tool schema, and what failure does each field prevent?
2. Why does the registry prefer structured matching (`ProvidedEvidence`, `ActionKind`, `ResultResourceType`) over objective-keyword overlap?
3. SendOS has no generic "ReAct loop". Where is its loop, and why might an enterprise platform avoid one generic loop?

### Maps cleanly · differs

- **Clean:** tool registry with schema + handler together, errors-as-observations (your registry does this; SendOS returns structured read outcomes), tenant scoping.
- **Differs:** SendOS capabilities are **governed assets** with risk/approval/version — a tool cannot be "just registered". The loop is a bounded goal loop inside `DecisionRuntime`, specialised per shape, not a general-purpose reason-act loop.

**Micro-action:** open your `ToolRegistry` and add one metadata field SendOS has (`is_write` is the cheapest). Note what code had to change to enforce it.

---

## Week 3 — Structured output, prompts as assets → `IStructuredCompletionHandler`

**You build:** `agentlab/schemas/` — structured output, repair, versioned prompts, typed `Decision`.
**C# lab:** [`dotnet/StructuredDecisionBridge`](../../dotnet/StructuredDecisionBridge/README.md) —
three-stage gate (schema → binding → budget) with a 15-check offline self-test.

### Read (SendOS)

| File | Look for |
|---|---|
| `apps/Send.Model.Adapter/src/.../Structured/IStructuredCompletionHandler.cs` | The contract: schema in; validated output or `SchemaValid=false` |
| `.../Structured/StructuredCompletionHandler.cs` | Never surfaces invalid output; status handling; no retry here |
| `.../Structured/JsonSchemaValidator.cs` | The supported subset: `type`, `required`, `properties`, `items` only |
| `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs` | Closed response family; envelope; the reserved-artifact exclusion |
| `.../Application/Decision/PresentationBudget.cs` + `PresentationBudgetEnforcer.cs` | The numbers you implemented, enforced in production |
| `.../Application/IntentElevation/IntentElevator.cs` lines 96–215 | The deterministic projection that keeps `ClarificationRequired` a pure function — models interpret, code decides policy |

### Questions

1. SendOS validates *after* generation instead of using provider-native constrained decoding. What does that cost, and when is it the right trade?
2. `StructuredCompletionHandler` returns `SchemaValid=false` and `StructuredOutput=null` rather than a partial object. How does that choice change the caller's error handling?
3. SendOS's composer **trims** to budget while your lab **rejects and repairs**. What can trimming silently change, and when is repair worth the extra calls?

### Maps cleanly · differs

- **Clean:** schema-gated completion, validate-after, discriminated decision family, presentation budgets as numbers.
- **Differs:** SendOS validates in `Model.Adapter` and composes in the runtime (two services, two seams); its family is much larger (evidence, execution results, readback verdicts); prompts are governed assets (`PromptGuidance`, `SpecialistDefinition`), not files.

**Micro-action:** count how many of your week-3 tests would still pass if the schema allowed `additionalProperties`. Then add the test that catches it.

---

## Week 4 — Context engineering and memory → `Send.Context.Gateway`

**You build:** `agentlab/context/` — window, compaction, retrieval, memory.

### Read (SendOS)

| File | Look for |
|---|---|
| `libraries/Send.Context.Gateway/IContextGateway.cs` | The boundary's promises: tenant-scoped, source-agnostic, no reasoning, no SDK |
| `libraries/Send.Context.Gateway/ContextGateway.cs` | Tenant-mismatch error vs empty result; freshness policy |
| `libraries/Send.Context.Gateway/Semantic/SemanticContextRetriever.cs` | Additive semantic path layered over structured retrieval |
| `libraries/Send.Context.Gateway/Semantic/DeterministicEmbeddingGenerator.cs` | Why a hash embedding is plumbing, not intelligence |
| `apps/Send.Agent.Runtime/src/.../Domain/Execution/SpecialistContext.cs` | The least-context envelope: exactly what a specialist may see |
| `apps/Send.Agent.Runtime/src/.../Infrastructure/ContextGateway/HttpContextRecordReader.cs` | How the runtime reads governed context over HTTP |

### Questions

1. Why is "empty result is not an error" a deliberate contract rather than a convenience?
2. What is excluded from `SpecialistContext`, and what does each exclusion protect against?
3. Why is a deterministic hash embedding shipped by default, and what is the honest remaining upgrade?

### Maps cleanly · differs

- **Clean:** context is a budget, least-context envelopes, retrieval behind a boundary, empty-vs-error distinction.
- **Differs:** SendOS's objective is **data minimisation for governance**, not maximal recall for quality; its retrieval is mostly structured records, with vectors additive; memory is split across Business_State (durable) and Decision Memory (OrgIntel), not one `memory.py`.

**Micro-action:** measure tokens saved by passing a least-context envelope instead of the full transcript in your week-2 agent. Write the number down.

---

## Week 5 — MCP and interoperability → connector manifests

**You build:** `agentlab/mcp/` — server, client, security checks.

### Read (SendOS)

| File | Look for |
|---|---|
| `libraries/Send.Connectors.Abstractions/IConnector.cs` | The source-agnostic port; vendor types never leak |
| `libraries/Send.Connectors.Abstractions/ExecutionOrigin.cs` | The enum every result carries: external-demo / simulated / controlled-live |
| `libraries/Send.Shared.Contracts/Capabilities/ConnectorCapabilityManifest.cs` | The manifest a connector publishes |
| `apps/Send.Integration.Service/src/.../Application/Connectors/ICapabilityManifestProvider.cs` | The declaration seam: connectors declare, they do not route |
| `apps/Send.Agent.Runtime/src/.../Infrastructure/CapabilityRegistry/HttpConnectorCapabilityManifestSource.cs` | How the runtime pulls manifests at startup/refresh |
| `apps/Send.Agent.Runtime/src/.../Application/Execution/ExecutionOrigins.cs` | Where origin is stamped and enforced |
| `libraries/Send.Connectors.Abstractions/IDeclaresExecutionOrigin.cs` | The interface that makes "say what you touched" non-optional |

### Questions

1. In SendOS, does a connector decide which capabilities exist, or does governance? Trace the path from `.cs` declaration to runtime registry.
2. MCP discovers tools at runtime from a server; SendOS assembles a catalogue from manifests and published assets. What does each approach make easy, and what does each make hard to govern?
3. Why does `ExecutionOrigin` exist as a first-class result field, and what should happen when a connector fails to declare one?

### Maps cleanly · differs

- **Clean:** capabilities are declared by their provider, not hard-coded in the agent; tool descriptions are data; transport is separate from declaration.
- **Differs:** SendOS has no MCP. It has a bespoke manifest + governed-asset pipeline with tenant entitlements and published-wins precedence — stronger on governance, weaker on ecosystem interop. **This is the clearest place a standard protocol could reduce bespoke surface** (see `docs/architecture/capability-ownership.md`).

**Micro-action:** write the three-line manifest your MCP server's tools would need if SendOS adopted MCP. Which field has no MCP equivalent? (Hint: entitlement.)

---

## Week 6 — Planning, orchestration, human approval → the decision-first runtime

**You build:** `agentlab/orchestrator/` — plan, specialists, orchestrator, approval.
This is the highest-value bridge week for the day job.

### Read (SendOS)

| File | Look for |
|---|---|
| `apps/Send.Agent.Runtime/src/.../Application/Planning/ExecutionPlanner.cs` | Shape selection from topology, authority enforcement, budgets, one accountable owner |
| `.../Application/Planning/TopologyClassifier.cs` | 100 lines that decide direct / specialist / squad / multi-squad, with materiality deliberately absent |
| `.../Application/Planning/LogicalPlanValidator.cs` | Acyclic, closed kinds, testable acceptance criteria |
| `.../Domain/Execution/ExecutionPlan.cs`, `ExecutionShape.cs`, `ReviewMode.cs` | The plan, the closed shape set, and review as an orthogonal mode |
| `.../Application/Approval/ApprovalCheckpoint.cs` | Persist-before-approve, `ApprovalBinding`, 6 transitions, execute-time rechecks, separation of duties, 15-min TTL |
| `.../Domain/Execution/ApprovalBinding.cs` | What is actually bound (tenant, actor, action version, content hash, authority snapshot, expiry) |
| `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` | Why materiality stopped selecting shapes — an ADR worth copying the structure of |

### Questions

1. Why is approval an `ExecutionMode` checkpoint rather than a fifth `ExecutionShape`?
2. `TopologyClassifier` takes no materiality parameter. What does it classify on, and what failure does removing materiality fix?
3. What exactly does an approval bind, and which of those bindings are re-checked at execution time?

### Maps cleanly · differs

- **Clean:** typed plan, smallest-sufficient shape, topology over intent-flags, approval as checkpoint, at-most-once execution.
- **Differs:** SendOS's planner consumes published, version-pinned assets (Squad/Specialist definitions) that your mini-squad does not have; its approval path is a persisted, resumable state machine with authority-version drift detection; and its `DecisionRuntime` is a 5,379-line procedural class — a framework would replace much of it.

**Micro-action:** add an `authority_snapshot` to your week-6 approval binding and the test that a narrowed authority after approval blocks execution. That test is the week-8 security bridge.

---

## Week 7 — Evals and observability → `Outcome_Trace` + evaluator

**You build:** `agentlab/evals/` — dataset, harness, judges, report, CI gate.

### Read (SendOS)

| File | Look for |
|---|---|
| `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs` | The closed 21-event lifecycle, and the Phase-1 nine-event subset in the comment |
| `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEvent.cs` | Store-assigned monotonic `Sequence`; append-only contract |
| `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceLifecycleEvent.cs` | Typed event family projecting to one flat row with `PayloadJson` |
| `apps/Send.Agent.Runtime/src/.../Application/Outcome/IOutcomeTraceEmitter.cs` | Fire-and-forget: `Emit` must never throw, never block the request |
| `apps/Send.Agent.Runtime/src/.../Application/Runtime/TurnStage.cs` | 45 named stages with `Ran/Skipped/Failed` — the observability lesson |
| `apps/Send.LowerLayer.Worker/src/.../Evaluation/EvaluationDimensions.cs` | The five assessable dimensions |
| `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs` | Attribution, provenance pinning, unattributable-drop, 30/0.7/0.5 evidence gate |
| `apps/Send.Intel.Server/src/.../ControlPlane/PublishingPipeline/PublishingService.cs` | Publish refuses without approval and without `Promoted` |

### Questions

1. Why a store-assigned monotonic sequence rather than `OccurredAtUtc` ordering?
2. What are the five evaluation dimensions, and what does the aggregate score deliberately *not* claim?
3. Where does SendOS's learning loop stop before publishing, and who must act for it to continue?

### Maps cleanly · differs

- **Clean:** append-only trace, stage-level events with skip reasons, deterministic checks before judges, evidence gates, human-approved promotion.
- **Differs:** SendOS's loop is currently **dry** — the Distillation Engine is real and uncalled, the stores have no production writer (see `CONCEPT-MAP.md` §0 and the repo's own `docs/architecture/reconciliation-audit.md` §F). Its evaluator scores *decisions*, not just outputs. Your week-7 suite is a working specimen of what the platform has designed but not yet wired.

**Micro-action:** emit one event per stage of your week-2 run, including the stages that were skipped and why. That is `TurnStage`, and it is the cheapest observability win you will ever ship.

---

## Week 8 — Security, governance, cost, reliability → the governance sandwich

**You build:** `agentlab/guard/` — injection, sandbox, authority, audit, rate limits, red team.

### Read (SendOS)

| File | Look for |
|---|---|
| `docs/architecture/governance-architecture.md` lines 223–273 | The pre-LLM gate, the post-LLM gate, and why the model can only recommend |
| `apps/Send.Agent.Runtime/src/.../Domain/Authority/EffectiveAuthority.cs` | Intersection of nine sources; `Delegate` can only narrow |
| `.../Application/Authority/AuthoritySources.cs` | The ten boundaries including the optional Squad boundary; DataSource sourced independently |
| `.../Application/Approval/ApprovalCheckpoint.cs` | Separation of duties, action hash, authority version, replay rejection, compensation |
| `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Filters/LicensingIngressFilter.cs` | Fail-closed licence/entitlement at ingress |
| `.../Application/Ingress/IIngressAuthorizer.cs` | The ingress authorisation seam |
| `.../Domain/Execution/ExecutionOrigin.cs` | What a fact says it touched |
| `docs/adrs/0002-edge-licence-check-restored.md` | A real incident: a catch-all product code denied every request; the fix and the guard test |

### Questions

1. Name the authority boundaries SendOS intersects. Can anything the model produces widen them?
2. What fails closed at ingress, and what happens when the licence service is unreachable?
3. Why is the approval binding a *security* control rather than a confirmation dialog?

### Maps cleanly · differs

- **Clean:** deny-by-default, intersection arithmetic, model output never grants authority, approval binding, append-only audit.
- **Differs:** SendOS is **ahead** here — do not reproduce the code, learn why each control exists. It uses in-house ABAC rather than Cedar/OPA, and app-level tenancy rather than Postgres RLS. Note one sharp detail from ADR 0002: a route→product catch-all silently denied a whole surface; the fix added "no catch-all" and a test asserting every emittable code exists in the catalogue.

**Micro-action:** write a one-page threat model of the SendOS approval path (5 threats, 5 controls, 2 gaps). Send it to a senior engineer for critique — this is the plan's recommended stretch.

---

## Week 9 — Capstone: Mini-SendOS → composing the runtime

**You build:** the capstone; a design proposal for one real improvement.

### Read (SendOS)

| File | Look for |
|---|---|
| `apps/Send.Agent.Runtime/src/.../Application/Runtime/MetaOrchestrator.cs` | Turn lifecycle: interpretation → business state → planning → dispatch |
| `.../Application/Runtime/DecisionRuntime.cs` | The dispatch surface: 30+ private methods; where a framework would help |
| `.../Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs` | Three sources, published-wins — your capstone's catalogue merge |
| `.../Domain/Decision/DecisionInteraction.cs` | The response family your capstone's surface renders |
| `.../Domain/CaseRuntime/Case.cs`, `DecisionTask.cs` | Durable suspend/resume — built, tested, **unwired** |
| `apps/Send.LowerLayer.Worker/src/.../Distillation/DistillationEngine.cs` | The learning loop's real engine |
| `docs/architecture/reconciliation-audit.md` §F | The honest status matrix; a map of what is dark and why |

### Questions

1. Map each capstone component to the SendOS service it mirrors. Which mirror is weakest, and why?
2. Which two improvements does the plan recommend proposing, and what evidence from your capstone supports each?
3. After nine weeks, which SendOS files can you now read and critique without a guide?

### Maps cleanly · differs

- **Clean:** the whole loop — provider → capability catalogue → typed decision → topology → approval → audit → eval → learning.
- **Differs:** SendOS runs as 10 services with licensing, tenancy, governed assets and multiple datastores; your capstone is one process. The difference is not the concepts, it is the **failure isolation and governance surface** between them.

**Micro-action:** write the one-page proposal. Recommended topics: (a) durable suspend/resume for approvals (`CaseRuntime` wiring), (b) trace → candidate evidence gating (wiring `DistillationWorkProcessor → DistillationEngine`). Both are grounded in gaps the repo documents itself.

---

## Appendix A — answers

Check your written answers against these. They are deliberately short: if your answer is longer and
still correct, that is fine; the point is whether the *mechanism* was named.

<details>
<summary><strong>Week 1 — Model.Adapter</strong></summary>

1. **Retry placement.** The handler owns the *candidate set*, so a retry can degrade to a different model (cost/latency/fallback) and enforce a whole-invocation time budget. An adapter-level retry can only retry the same model and cannot see the budget or the alternative.
2. **`IsTransient` narrowness.** It returns true only for 502/504 (see `CompletionHandler.cs:484-485`). 429 is arguably the most retryable status in practice (`Retry-After`), and 500/503 are common; being too narrow wastes recoverable requests, being too wide burns money on permanent failures. The transferable point: the classification must be explicit, tested, and matched to where rate limiting actually lives (SendOS leans on ingress limits).
3. **Split of duties.** `ChatCompletionsClient` ≈ `IProviderAdapter` (payload build, response parse, usage); routing, retry, fallback, budgets and cancellation belong to `CompletionHandler` (and, in SendOS, `ModelCostProfile`/`ModelBudget`).

</details>

<details>
<summary><strong>Week 2 — capability registry and loop</strong></summary>

1. **Fields with no plain-tool analogue.** `ReadOrWrite`, `RiskLevel`, `ApprovalRequirement`, `SideEffects`, `IdempotencyRequirement`, `CompensationSupport`, `AuditRequirement`, `TenantAvailability`, `RequiredPermissions`, `ProvidedEvidence`, `ResultResourceType`, `ActionKind`, `GovernedAssetReference`, `Version`, `EffectiveDate`. Each prevents a governance failure: unapproved writes, cross-tenant exposure, ambiguous result types, unversioned assets, unverifiable side effects.
2. **Structural matching.** Objective keywords are free text and produce false negatives/positives; declared metadata (`ProvidedEvidence`, `ActionKind`, `ResultResourceType`) is a contract. A mis-declared capability then fails visibly rather than silently hiding a correct one — the code comments (e.g. on `ProvidedEvidence`) record exactly that false-negative incident.
3. **Where the loop is.** Inside `DecisionRuntime`/shape handlers as a bounded goal loop (`Runtime/Iteration/BoundedIterativeExecutionLoop`, `Goals/GoalCompletionLoop`), specialised per shape. A generic ReAct loop makes every tool reachable from every step, which is hard to govern; SendOS instead constrains *which* capability can serve *which* classified turn.

</details>

<details>
<summary><strong>Week 3 — structured output and typed decisions</strong></summary>

1. **Validate-after vs constrained decoding.** Cost: retries, extra latency/cost, and a failure rate that scales with schema complexity. It is the right trade when not every provider supports grammars, when the schema needs product-level rules (budgets, semantics) that grammars cannot express, and when the validation diagnostics are themselves the product (repair messages, audit).
2. **Never surfacing invalid output.** The caller has one branch: valid or not-valid. It prevents partially-valid decisions rendering, and makes failure an explicit `Limitation` rather than a downstream wrong action.
3. **Trim vs reject.** Trimming can silently change meaning (cutting a headline can invert it); rejecting costs calls but preserves the model's full statement for a human. SendOS trims presentation *after* the decision is semantically fixed, and rejects at the schema gate — the two serve different failure classes.

</details>

<details>
<summary><strong>Week 4 — context and memory</strong></summary>

1. **Empty is not an error.** "No matching governed records" is information the reasoner must be able to state honestly; conflating it with failure forces retries and encourages fabrication. It is also a security separation: the boundary reports absence, it does not reason about it.
2. **Exclusions in `SpecialistContext`.** No full Business_State, no transcript, no unrelated evidence, no other tenants' data. Each exclusion limits blast radius, prompt-injection surface and data-minimisation exposure — governance, not just token savings.
3. **Hash embeddings.** They prove the retrieval plumbing (index, query, citations) end-to-end without a vendor dependency or a per-token cost, and they are deterministic so tests are stable. The honest upgrade is swapping `IEmbeddingGenerator` for a real model — the plumbing already exists.

</details>

<details>
<summary><strong>Week 5 — connectors, manifests, MCP</strong></summary>

1. **Who decides.** The connector *declares* (`ICapabilityManifestProvider`), SendOS governance *publishes*, and the runtime *assembles* the registry (`CapabilityCatalogueAssembler`: platform-owned → connector manifests → published assets, with **published wins**). So a connector cannot unilaterally introduce a capability into the governed surface.
2. **MCP vs manifests.** MCP makes ecosystem interop and dynamic discovery easy; manifests + published assets make entitlement, versioning and governance easy. MCP's server-declared tools are exactly the thing a governance layer must re-check — the two are complementary, not competing.
3. **Execution origin.** It lets audit, trace and UI say what was real (`ControlledLiveExecution`), simulated, or demo data without inferring it from a provider name. An undeclared origin must be refused fail-closed at the boundary — otherwise every downstream claim about "what actually happened" is unverifiable.

</details>

<details>
<summary><strong>Week 6 — planning, topology, approval</strong></summary>

1. **Approval is not a shape.** Shapes describe *how work is executed*; approval is a *governance checkpoint* that can interrupt any shape. Making it a shape would mean choosing between "squad with approval" and "squad without", and the two could drift; as an orthogonal `ExecutionMode`, every shape inherits the same gate. `ReviewMode` is orthogonal for the same reason.
2. **Topology, not materiality.** It classifies on bound-plan structure: ≥2 disconnected components → multi-squad; single capability node → direct capability; single reasoning node → direct specialist; ≥2 connected node → single squad. Materiality used to select shapes, which conflated "important" with "needs many agents" and let model-authored labels pick a shape nothing could back; the classifier now ignores both, and an unbacked shape fails closed.
3. **What approval binds.** Tenant, actor, action version, action content hash, effective-authority grant snapshot, granted-at, expiry (default 15 minutes), approver role, authority version. At execution: proposal still approved with a live binding, action version/hash still match, authority still covers, approval not expired, approval not consumed by another key, proposer ≠ approver, approver holds the role/permission. Any failure refuses.

</details>

<details>
<summary><strong>Week 7 — trace, eval, publish</strong></summary>

1. **Why a store sequence.** Timestamps can collide, go backwards across instances, or be rewritten by clock correction; a store-assigned sequence gives a total, gap-tolerant order that replay depends on (`OutcomeTraceEvent.Sequence`, unique-indexed).
2. **Five dimensions.** Correctness, PolicyCompliance, OutcomeAlignment, EvidenceGrounding, ExecutionQuality. The aggregate is a summary of *assessed* dimensions only — it is not a truth claim, and an unassessed dimension must not be silently averaged in as zero.
3. **Where the loop stops.** At a Draft candidate: distillation produces evidence-gated insights, the trainer synthesises a candidate diff, the promoter is submit-only, and `PublishingService` refuses without a recorded human approval and a `Promoted` status. The model can recommend; a person must publish.

</details>

<details>
<summary><strong>Week 8 — security and governance</strong></summary>

1. **Boundaries.** User, Tenant, Application, Entitlement, Playbook, Specialist, Tool, DataSource, ApprovalState, and (application layer) Squad; `EffectiveAuthority` intersects them and `Delegate` can only narrow. No — model output is deliberately not a source, so it cannot widen authority; it can only *propose* something that must pass the same arithmetic.
2. **Ingress fail-closed.** Licence/entitlement, tenant and actor resolution, quotas, idempotency. On a licensing outage or timeout the request is denied (`Unavailable`/deny), never allowed; cached grants cannot authorise reads during an outage.
3. **Approval binding as security.** It converts "the model said yes" into "a specific person, with a specific authority snapshot, approved a specific immutable action before a deadline". Replay, post-approval edit, authority drift, expiry and self-approval are all rejected — none of that is a UX concern.

</details>

<details>
<summary><strong>Week 9 — capstone and proposal</strong></summary>

1. **Mapping.** Provider layer → `Send.Model.Adapter`; capability catalogue → `Send.Agent.Runtime` registry + `Send.Intel.Server` published assets; decision runtime → `MetaOrchestrator` + `DecisionRuntime`; governance → `EffectiveAuthority` + `ApprovalCheckpoint` + ingress; learning loop → `Send.Usage.Collector` + `Send.LowerLayer.Worker` + Intel publish; surface → Conversation Layer/website. Weakest mirror: the learning loop, because SendOS's is dry and yours is wired — which is why it is a good proposal topic.
2. **Two recommended proposals.** Durable suspend/resume for approvals (`CaseRuntime` is built and unwired; your SQLite resume + CAS is a working sketch), or trace → candidate evidence gating (wire the Distillation Engine into the worker and prove an evidence-gated candidate can reach a human-approved publish).
3. **What you can read now.** `DecisionInteraction`, `EffectiveAuthority`, `ApprovalCheckpoint`, `TopologyClassifier`, `OutcomeTrace*`, `StructuredCompletionHandler` — and you can say which of them you would change and why.

</details>

---

## Appendix B — path index and doc-drift warnings

**Docs that are stale (checked 2026-10-18) — use the code paths, not these claims:**

| Doc says | Code says |
|---|---|
| Decision runtime behind `DecisionFirst:Enabled`, 404 when off (`README.md:52`, `docs/README.md:10`, `docs/business/09-status-and-roadmap.md:26`) | Flag removed: `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417` |
| Shape chosen from materiality via `SelectShape` (`docs/runtime-orchestration-flow.md:243-301`) | Topology only: `.../Application/Planning/ExecutionPlanner.cs:143-219` + `TopologyClassifier.cs` |
| `UseLogicalPlanner` "defaults false" (`ExecutionPlanningOptions.cs:69-74` comment) | Initialiser is `= true` (`:75`) |
| `Send.Distillation.Engine` / `Send.Intel.Trainer` / `Send.Intel.Promoter` are apps (`README.md:59-67`) | Removed as projects; learning subsystem is `apps/Send.LowerLayer.Worker` |
| `Send.Usage.Collector` is a placeholder (`docs/implementation-inventory.md:31,153`) | 24 source files incl. append-only EF store, migrations, replay endpoints |

**Files worth bookmarking:** `docs/architecture/governance-architecture.md` §5–6b ·
`docs/architecture/reconciliation-audit.md` §F ·
`docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` ·
`docs/adrs/0002-edge-licence-check-restored.md`.

---

## Appendix C — weekly bridge log template

Copy into `notes/weekNN-bridge.md` (3 minutes at the end of each session):

```markdown
# Week NN bridge — <mechanism>

## Questions
Q1:
Q2:
Q3:

## Maps cleanly (SendOS → my lab)
-
-

## Differs / would change
-
-

## One-sentence transfer
"When I see <SendOS concept>, I will check <my lab's mechanism> for <failure mode>."
```
