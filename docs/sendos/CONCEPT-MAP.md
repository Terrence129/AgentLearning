# SendOS Concept Map — living document

> **Living document — code wins over docs.**
> This is the team's shared reference for *what SendOS actually implements*, verified against the
> source checkout on **2026-10-18**. The platform changes faster than its documentation: when this
> page and the code disagree, **the code is right** — and the disagreement is itself a finding
> worth reporting (see §0 for five verified examples).
>
> - **Audience:** an engineer learning agent engineering who wants to read SendOS with expert eyes.
> - **Use it with:** [`BRIDGE.md`](./BRIDGE.md) (week-by-week bridge), [`READING-ORDER.md`](./READING-ORDER.md) (10-step path), [`../../dotnet/`](../../dotnet/) (C# bridge labs).
> - **Freshness rule:** every claim carries a repo-relative path; a claim without a path is an
>   impression, not a finding. Claim paths are relative to the SendOS repo root
>   (`SendOs/`), not to this learning repo.
> - **Update rule:** when you verify something different in code, change the claim *and* record
>   the file/line that changed it. Do not "fix" this page from documentation alone.

**Contents**

- [0. Read this first: the docs are three vintages, and the code wins](#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins)
- [1. The machine in one page](#1-the-machine-in-one-page)
- [2. Concept map — industry term → SendOS implementation](#2-concept-map--industry-term--sendos-implementation)
  - [2.1 Understanding and intent](#21-understanding-and-intent)
  - [2.2 Planning and orchestration](#22-planning-and-orchestration)
  - [2.3 Governance and tool use](#23-governance-and-tool-use)
  - [2.4 Data, trace and learning](#24-data-trace-and-learning)
  - [2.5 Platform](#25-platform)
- [3. Ranked learning topics (20)](#3-ranked-learning-topics-20)
- [4. Where a from-scratch build teaches the most — six mechanisms](#4-where-a-from-scratch-build-teaches-the-most--six-mechanisms)
  - [4.1 Typed decision family + bound approval gate](#41-typed-decision-family--bound-approval-gate)
  - [4.2 Capability catalogue with fail-closed authority intersection](#42-capability-catalogue-with-fail-closed-authority-intersection)
  - [4.3 Append-only trace → eval → evidence-gated candidate → human publish](#43-append-only-trace--eval--evidence-gated-candidate--human-publish)
  - [4.4 Schema-gated structured output + budgeted routing](#44-schema-gated-structured-output--budgeted-routing)
  - [4.5 Topology-driven shape selection](#45-topology-driven-shape-selection)
  - [4.6 Append-only trace as the runtime↔learning contract](#46-append-only-trace-as-the-runtimelearning-contract)
  - [4.7 Mapping onto the learning repo's agentlab package](#47-mapping-onto-the-learning-repos-agentlab-package)
- [5. Where SendOS departs from mainstream practice](#5-where-sendos-departs-from-mainstream-practice)
- [6. Reading order — shortest path to a productive contribution](#6-reading-order--shortest-path-to-a-productive-contribution)
- [7. What I could not assess](#7-what-i-could-not-assess)

---

> **The report below is preserved verbatim** from the original analysis (`docs/research/05-sendos-concept-map.md`,
> 2026-10-18). It is the evidence base for the bridge material; the bridge docs cite it by section.
# SendOS Concept Map — what the platform actually implements, and what to rebuild in miniature

> **Source:** read-only analysis of `D:\DevRepo\SendProjects\SendOS\SendOs` on 2026-10-18 (on macOS/Linux, substitute your local SendOS checkout path). Nothing was modified, built or executed. Paths below are repo-relative to that root.
> **Audience:** an intern contributing to SendOS who needs transferable agent-engineering skill, not familiarity with one codebase.
> **Method:** read `README.md`, `docs/architecture/*.md`, `docs/implementation-inventory.md`, `docs/runtime-orchestration-flow.md`, `docs/adrs/`, `docs/business/01`, then verified claims against code in `apps/Send.Agent.Runtime`, `apps/Send.Model.Adapter`, `apps/Send.Intel.Server`, `apps/Send.Usage.Collector`, `apps/Send.LowerLayer.Worker`, `libraries/Send.Context.Gateway`, `libraries/Send.Work.Capability`.

---

## 0. Read this first: the docs are three vintages, and the code wins

The repo holds **current docs, target docs, and frozen audits**, and they contradict each other. Five verified examples:

| # | Doc says | Code says | Cite |
|---|---|---|---|
| 1 | Decision runtime is behind `DecisionFirst:Enabled`, 404 when off | The flag **was removed**; the governed path is not opt-in | `README.md:52`; `docs/README.md:10` vs `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417` |
| 2 | Shape chosen from `Materiality` + `PossibleIntentions` (`SelectShape`) | Shape chosen **only** from plan topology via `TopologyClassifier` over a `BoundPlanGraph` | `docs/runtime-orchestration-flow.md:243-301` vs `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Planning/ExecutionPlanner.cs:143-219` |
| 3 | `UseLogicalPlanner` "Defaults `false`" | Initialiser is `= true` (XML comment stale) | `.../Planning/ExecutionPlanningOptions.cs:69-75` |
| 4 | `Send.Usage.Collector` and `Send.Intel.Admin` are placeholders | Usage Collector has 24 source files: append-only EF store, migrations, write queue, replay endpoints | `docs/implementation-inventory.md:31,153` vs `apps/Send.Usage.Collector/src/**` |
| 5 | `Send.Distillation.Engine` / `Send.Intel.Trainer` / `Send.Intel.Promoter` are apps | They no longer exist as projects; the learning subsystem is `apps/Send.LowerLayer.Worker` (435 `.cs`) | `README.md:59-67` vs `apps/Send.LowerLayer.Worker/**`; `docs/architecture/reconciliation-audit.md:19` records the removal |

Even the honest audit is frozen: `docs/architecture/reconciliation-audit.md` (HEAD `3ee901e`) calls the logical planner off and `TopologyClassifier` dead code (lines 103-109, 216-223), which no longer matches the code.

**Working rule:** `docs/` is design intent and orientation; `file.cs` is fact. When they disagree, the disagreement is worth a small PR — the repo's best habit is that every claim is cited to `file:line` and stale claims are treated as defects.

**Scale (grep counts; suite not run):** 10 apps, 25 `libraries/` projects, 979 `.cs` under Agent Runtime, 435 under `Send.LowerLayer.Worker`, 1,122 test files with ≈6,329 `[Fact]`/`[Theory]` and ≈486 FsCheck `[Property]` attributes.

---

## 1. The machine in one page

| Stage | Where | What it really does | State |
|---|---|---|---|
| Ingress | `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Filters/LicensingIngressFilter.cs`; `Controllers/ChatController.cs:61` (`POST api/chat/decision`) | Fail-closed licence/entitlement, tenant+actor claims, idempotency | real |
| Understanding | `.../Application/Runtime/MetaOrchestrator.cs`; `.../Understanding/CanonicalTurnInterpreter.cs` | Observe → Resolve → Ground → Interpret → Validate → one `MessageUnderstanding` | real (grounding thin) |
| Elevation | `.../Application/IntentElevation/IntentElevator.cs` | Deterministic projection to `InterpretedGoal`; ambiguity→clarify is a pure function | real |
| Planning | `.../Application/Planning/ExecutionPlanner.cs` | Published assets, effective authority, `TopologyClassifier`, budgets, one accountable owner | real (topology ON) |
| Execution | `.../Execution/DirectCapabilityHandler.cs`, `Specialist/DirectSpecialistRunner.cs`, `Squad/SingleSquadHandler.cs`, `Squad/MultiSquadShapeHandler.cs` | Four shapes; Squads coordinate Specialists on a structured in-memory bus | Direct real; Squad paths thin |
| Reasoning | `apps/Send.Model.Adapter/src/**` via `ISpecialistReasoner` | Provider-independent completion, schema-validated output, budget-aware routing | real |
| Approval gate | `.../Approval/ApprovalCheckpoint.cs`; `.../Execution/AuthoritativeActionExecutor` | Persist proposal → bound approval → revalidate authority → execute at-most-once | real |
| Response | `Domain/Decision/DecisionInteraction.cs`; `Api/Presentation/DecisionInteractionMapper.cs` | Closed family of 11 typed responses with presentation budgets | real |
| Trace | `.../Outcome/IOutcomeTraceEmitter.cs` → outbox → `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEvent.cs` | 21-event closed lifecycle, append-only, monotonic `Sequence` | real (emission shallow) |
| Learning | `apps/Send.LowerLayer.Worker/src/**` | Distillation → evaluation → candidate synthesis → submit-only promotion | real code, **dry loop** |

Two facts explain most of the repo: **every step is a typed, testable seam**, and **several seams are not connected**. `DecisionRuntime.cs` is 5,379 lines and `MetaOrchestrator.cs` 2,685 — orchestration is a large procedural class, not a graph interpreter.

---

## 2. Concept map — industry term → SendOS implementation

Status: **Implemented** (real and reachable) · **Partial** · **Dark** (built, tested, not on live path) · **Missing**.

### 2.1 Understanding and intent

| Industry concept | How SendOS implements it | Where | Status | Learn externally |
|---|---|---|---|---|
| Intent understanding | One authoritative model interpretation, then deterministic projection to `InterpretedGoal`; the model never sets `ClarificationRequired` | `.../Understanding/CanonicalTurnInterpreter.cs`; `.../IntentElevation/IntentElevator.cs:96-215` | Implemented | Structured extraction / function calling; dialogue state |
| Clarify-vs-act policy | Pure `RequiresClarification(ambiguity, threshold) => ambiguity >= threshold`; prior context lowers ambiguity | `IntentElevator.cs:80,111-124` | Implemented | Value-of-information clarification |
| Grounding before inference | Observe→Resolve→Ground→Interpret→Validate; `StatedFactFidelity` reconciles interpretation against the literal words | `.../Understanding/**`; `IntentElevator.cs:137-150` | Partial (external resolve tiers + live fetch unregistered) | Tool-augmented extraction |
| Reserved artifact types | Response family **cannot represent** Chart/Dashboard/VisualisationSpec — type-system enforced | `Domain/Decision/DecisionInteraction.cs:15-28` | Implemented | Discriminated unions / API contracts |
| Presentation budgets | Headline ≤ 12 words, ≤ 4 next moves, 1 question ≤ 3 options | `.../Decision/PresentationBudgetEnforcer.cs`; `.../Properties/PresentationBudgetPropertyTests.cs` | Implemented | UI-shaped LLM output |

### 2.2 Planning and orchestration

| Industry concept | How SendOS implements it | Where | Status | Learn externally |
|---|---|---|---|---|
| Plan-then-execute | `ILogicalPlanner` → `LogicalPlanValidator` (acyclic, closed kinds) → `CapabilityResolver` → `BoundPlanGraph` | `.../Application/Planning/*` | Implemented (ON) | Plan-and-Solve; LLM Compiler; task DAGs |
| Right-sizing topology | `TopologyClassifier`: ≥2 components → `MultiSquad`; 1 capability node → `DirectCapability`; 1 reasoning node → `DirectSpecialist`; ≥2 connected → `SingleSquad`; unbacked → **fail closed** | `.../Planning/TopologyClassifier.cs:28-102`; `ExecutionPlanner.cs:143-219` | Implemented | Cost-aware orchestration; model cascades |
| Definition vs instance | Specialist = published, version-pinned asset; instance = ephemeral `SpecialistContext`, never persisted | `Domain/Execution/SpecialistContext.cs`; `.../Squad/SpecialistActivator.cs` | Implemented | Agent registries; prompt versioning |
| Multi-agent messaging | `ISquadMessageBus` carries structured `SquadMessage`; transcript stays internal, one `DecisionInteraction` leaves | `.../Squad/InMemorySquadMessageBus.cs`, `SquadOrchestrator.cs` | Implemented (cross-squad depth thin) | FIPA-ACL; blackboard; A2A |
| Review as orthogonal mode | `ReviewMode` policy-selected, never a fifth shape, never model-chosen; `ReviewGatedApproval` | `.../Review/**`; `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs` | Implemented | LLM-as-judge; constitutional review |
| Bounded iteration | `BoundedIterativeExecutionLoop`, `GoalCompletionLoop`, `IterationBudget`, `BudgetGuard` | `.../Runtime/Iteration/**`; `Domain/Execution/BudgetGuard.cs` | Implemented | ReAct; Reflexion; budgeted agents |

### 2.3 Governance and tool use

| Industry concept | How SendOS implements it | Where | Status | Learn externally |
|---|---|---|---|---|
| ABAC authorization | `EffectiveAuthority` = intersection of **10 boundaries** (User, Tenant, Application, Entitlement, Playbook, Specialist, Tool, DataSource, ApprovalState, Squad); `Delegate()` only narrows | `Domain/Authority/EffectiveAuthority.cs:8-36,114-225`; `Application/Authority/AuthoritySources.cs:49-91` | Implemented | ABAC/XACML; Cedar; OpenFGA (contrast: ReBAC) |
| Tool registry | Three declaration sources — platform-owned, connector manifests, published assets — merged **published-wins** | `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` | Implemented | MCP tool discovery; manifest protocols |
| Governance sandwich (pre/post-LLM) | Pre: published+pinned assets, authority, entitlement, least context. Post: schema → re-authorize → approval by risk → backend revalidation | `docs/architecture/governance-architecture.md:223-273` | Partial | Guardrails frameworks |
| HITL with binding + separation of duties | Proposal persisted before approval; approval bound to tenant/actor/action hash/authority version/expiry (15 min); proposer ≠ approver; 6 transitions; at-most-once; compensation | `.../Approval/ApprovalCheckpoint.cs:237-468,470-571` | Implemented | Maker-checker; 2PC; e-signature binding |
| Idempotent side effects | Idempotency key + `ActionIdempotencyStore` + approval-consumed flag; replay rejected with stable codes | `ApprovalCheckpoint.cs:341-412` | Implemented | Idempotency keys; exactly-once |
| Verification / readback | `IResultVerifier` + `ReadbackVerification` (Verified/Contradicted/Unconfirmed/NotPerformed) | `DecisionInteraction.cs:447-536`; `.../Evaluation/**` | Partial (per-connector readback missing) | Post-condition verification |
| Semantic layer | Published `BusinessSemanticDefinition`; user overlays additive only, never override the tenant-authoritative metric | `Application/SemanticResolution/IBusinessSemanticResolver.cs:63-157` | Partial (revenue-first) | dbt Semantic Layer; MetricFlow |

### 2.4 Data, trace and learning

| Industry concept | How SendOS implements it | Where | Status | Learn externally |
|---|---|---|---|---|
| Append-only trace | 21-event closed lifecycle; insert-only store; DB trigger denies UPDATE/DELETE; identity `Sequence` | `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs`; `.../Infrastructure/Persistence/EfCoreOutcomeTraceStore.cs:1-80`; `UsageCollectorDbContext.cs` | Implemented | Event logs vs event sourcing |
| Transactional outbox | Fire-and-forget `Emit` (never throws) → durable outbox → background worker | `.../Application/Outcome/IOutcomeTraceEmitter.cs:24-45` | Implemented | Outbox pattern |
| Evaluation harness | 5 dimensions (Correctness, PolicyCompliance, OutcomeAlignment, EvidenceGrounding, ExecutionQuality) + aggregate | `apps/Send.LowerLayer.Worker/src/.../Evaluation/{EvaluationDimensions,Evaluator}.cs` | Dark (uncalled) | Ragas/DeepEval; judge calibration |
| Statistical-evidence gate | `EligibleForCandidate ∧ sample ≥ 30 ∧ confidence ≥ 0.7 ∧ quality ≥ 0.5` | `.../Distillation/EvidenceGate.cs:24-35`; `DistillationEngine.cs:52-53` | Dark | Sequential testing; power analysis |
| Data flywheel | Trace → distil (attribution + provenance) → train (diff vs BaseVersion) → submit-only promoter → human approve → write-once publish | `apps/Send.LowerLayer.Worker/src/**`; `.../PublishingPipeline/PublishingService.cs` | Dark / dry | Data flywheels; DSPy (vs RLHF) |
| Versioned asset registry | `Draft→Review→Approved→Published→Deprecated`; write-once; pins; rollback | `.../ControlPlane/Lifecycle/GovernedAssetLifecycleService.cs` | Implemented | Prompt/asset registries |
| Traceable stages | `TurnStage` enum: 45 named stages, each `Ran/Skipped/Failed` with a reason | `.../Application/Runtime/TurnStage.cs:29-203` | Implemented | Structured logging; OTel GenAI conventions |

### 2.5 Platform

| Industry concept | How SendOS implements it | Where | Status | Learn externally |
|---|---|---|---|---|
| Ports & adapters | `IConnector` / `IConnectorSyncService` / `ICapabilityManifestProvider`; three paths (ingest, live query, governed action) | `libraries/Send.Connectors.Abstractions/**`; `apps/Send.Integration.Service/src/**` | Implemented | Hexagonal architecture; iPaaS |
| Context read boundary | Tenant-scoped, source-agnostic `IContextGateway`; empty result is not an error | `libraries/Send.Context.Gateway/IContextGateway.cs:1-32` | Implemented | Hybrid retrieval; RAG eval |
| Vector retrieval | Additive semantic path, pgvector adapter, deterministic hash embeddings by default | `libraries/Send.Context.Gateway/Semantic/**` | Partial (model pluggable) | Embeddings; pgvector tuning |
| Resilience stack | Tiered cache, circuit breaker, per-connector rate limiter, single-flight, idempotency | `apps/Send.Intelligence.Gateway/src/**` (`Caching/`, `CircuitBreaker/`, `RateLimiting/`) | Implemented | Polly; Redis patterns |
| Durable long-running work | `CaseRuntime` + `DecisionTask` with CAS reserve→suspend→resume + deadline worker | `.../Domain/CaseRuntime/**`; `.../Infrastructure/CaseRuntime/**` | Dark (not wired) | Temporal; DBOS; checkpointers |
| Property-based invariants | ≈486 FsCheck properties (authority narrows, approval ≤ once, budgets hold) | `apps/Send.Agent.Runtime/tests/**/Properties/**` | Implemented | FsCheck/Hypothesis |

---

## 3. Ranked learning topics (20)

Ordered by SendOS relevance × teaching value × lab feasibility.

| # | Topic | Why it matters at SendOS | Miniature lab (Python first; .NET noted) | Effort |
|---|---|---|---|---|
| 1 | **Typed decision + approval gate** | The product promise: AI recommends, a human approves, the backend executes. Bugs are security bugs | `pydantic` union of 11 response models + `/propose → /approve → /execute` that rejects replays and post-approval edits. .NET: polymorphic records | L |
| 2 | **Capability registry + fail-closed authority** | `CapabilityCatalogueAssembler` + `EffectiveAuthority` decide whether *anything* runs | Merge three sources with published-wins; compute intersection; assert empty source ⇒ zero grants | M |
| 3 | **Trace → eval → candidate → human publish** | The differentiator and the most obviously unwired part; highest-leverage contribution | Append-only SQLite log (trigger denies UPDATE/DELETE) + rule learned from ≥30 traces + 5-dim evaluator + approval-gated publish | L |
| 4 | **Schema-validated structured output** | Every model call is schema-gated; invalid output must never surface | Ask for JSON, validate, return `{valid:false}` never partial; measure failure rate by schema complexity; add one repair-retry | M |
| 5 | **Topology-driven shape selection** | Newest live mechanism (ADR 0001); teaches "right-size the agent" better than tutorials | `PlanGraph(nodes, edges)` → classify; unbacked ⇒ hard error not fallback; property-test it | M |
| 6 | **Intent elevation + ambiguity threshold** | Turns sloppy NL into an actionable goal; decides ask vs act; explainable to stakeholders | Extract `{objective, ambiguity, candidate_intentions}`; `clarify = ambiguity >= threshold`; 1 question ≤3 options | S |
| 7 | **Model routing under budget** | `HandleRoutedAsync` encodes cost/latency-aware routing with fail-safe budget checks | Route across 3 fake providers; enforce cost/latency/attempts; fall back on transient only; "no candidate fits" ⇒ refuse | M |
| 8 | **Least-context envelopes** | `SpecialistContext` is the data-minimisation guarantee; over-sharing is a governance bug | Compare full transcript vs least-context on cost/quality; assert envelope fields | S |
| 9 | **Append-only audit + outbox** | `Outcome_Trace` is audit + learning substrate; emission must never fail the request | Outbox row written in the request transaction; worker delivers; property: request succeeds while consumer is down | M |
| 10 | **Version pinning, immutable publish** | Runtime resolves Published, pinned assets; a mid-flight publish must not mutate a run | Asset store with write-once versions and pins; a run on v3 stays on v3 after v4 publishes | M |
| 11 | **Independent review + verification** | Review is orthogonal to shape; verification is separate from success assertion | Producer → critic (schema-constrained verdict) → gate + deterministic post-check that can withhold success | M |
| 12 | **Idempotency, at-most-once execution** | Every write path depends on it | Execute with key; replay same key; replay different key; assert one side effect | S |
| 13 | **Semantic layer before generation** | "A user cannot quietly redefine revenue" — the enterprise anti-hallucination move | Published metric + aliases-only overlays; assert overlay cannot change the formula; unconnected tenant gets honest "no data" | M |
| 14 | **Durable case / suspend-resume** | `CaseRuntime` is built and dark — fastest route to a real contribution | Park in SQLite, return 202, resume on callback, CAS against double-resume, expire on deadline | L |
| 15 | **Property-based agent invariants** | Dominant quality technique (≈486 properties) — how probabilistic systems stay testable | `hypothesis`: authority ⊆ narrowest; approval ≤ once; budgets respected; shape backed or error | M |
| 16 | **Evaluation harness with rubric** | Missing link between trace and learning | Golden set + 5-dim rubric; forced-JSON judge; measure agreement vs human labels | M |
| 17 | **Connector abstraction + execution origin** | Three connector paths; every result declares real/simulated origin | Two fake connectors behind one port; stamp origin; fail closed when omitted | M |
| 18 | **Cache, breaker, single-flight** | Gateway resolution is cache-first with breaker fallback | TTL cache + breaker + single-flight; chaos-test origin down: stale within budget or honest failure | M |
| 19 | **Multi-agent message protocol** | Squad chatter structured and internal; one decision leaves | Three agents on a bus with typed messages; assert no transcript leaks to API; budget exhaustion ⇒ degraded honest answer | M |
| 20 | **Eval-gated asset promotion** | Promotion is submit-only; a model can never bypass a human | Candidate must beat baseline on eval and pass evidence thresholds, then require an approval row before write | S |

---

## 4. Where a from-scratch build teaches the most — six mechanisms

### 4.1 Typed decision family + bound approval gate

**Build:** a closed response union (`ClarificationPrompt | DirectAnswer | DecisionState | AnalysisConclusion | DecisionRecommendation | ActionProposal | ApprovalRequired | ExecutionResult | Limitation`), a proposal **persisted before approval**, an `ApprovalBinding` (tenant, actor, action hash, authority snapshot, expiry), a state machine (`Pending → Approved | Rejected | Modified | Cancelled | Expired | Revoked → Executed`), and an executor refusing modified/replayed/expired/narrowed approvals.

**Invariants:** persisted-before-approve; wrong reference never satisfies; proposer ≠ approver; hash mismatch blocks; authority narrowing between approve and execute blocks; replay returns the original reference; failure compensates.

**Reference:** `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs`; `.../Application/Approval/ApprovalCheckpoint.cs:237-468`; `.../Properties/ApprovalBindingAtMostOncePropertyTests.cs`.

**Without it:** a model-settable "approved" flag; duplicate side effects on retry; approvals outliving the authority they were granted under.

### 4.2 Capability catalogue with fail-closed authority intersection

**Build:** three declaration sources merged by id with published-wins; registry match filtered by tenant then declared shape (read vs action kind); authority as intersection over independent boundaries with `effective ⊆ narrowest`, and `delegate()` only narrowing.

**Invariants:** empty boundary ⇒ no grants; adding a boundary never widens; matched capability carries a governed-asset reference; undeclared capability is not invokable.

**Reference:** `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120`; `Domain/Authority/EffectiveAuthority.cs`; `Application/Authority/AuthoritySources.cs`; `.../Properties/AuthorityIntersectionNarrowingPropertyTests.cs`.

**Without it:** a tool described in a prompt but absent from the governed catalogue; providers quietly granting permissions; cross-tenant matches.

### 4.3 Append-only trace → eval → evidence-gated candidate → human publish

**Build:** append-only store with store-assigned monotonic sequence and a DB rule denying UPDATE/DELETE; distillation that attributes insights to the asset versions that produced them and **drops unattributable** ones; an evidence gate; a five-dimension evaluator; candidates as **diffs against a base version**; a submit-only promoter creating `Draft` only; a publish step refusing without a human approval row.

**Invariants:** no update/delete; replay in append order; weak evidence never becomes a candidate; AI never reaches `Published` without approval; next request resolves the new pinned version.

**Reference:** `apps/Send.Usage.Collector/src/**`; `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs`; `.../Evaluation/Evaluator.cs`; `.../ControlPlane/PublishingPipeline/PublishingService.cs`; `docs/architecture/governance-architecture.md:§6b`.

**Without it:** a "self-improving" loop that silently ships model-authored policy; traces that cannot be replayed.

### 4.4 Schema-gated structured output + budgeted routing

**Build:** provider abstraction returning text, finish reason, usage; schema validator over a documented subset; handler returning `valid=False, output=None` on mismatch; router filtering candidates by task type/reliability/token/cost/latency, ordering by policy (including an explicit declared-order mode), retrying transient failures only, reporting per-call cost.

**Invariants:** invalid never surfaces as valid; unverifiable budget ⇒ candidate excluded (fail-safe); cancellation never retries; time budget aborts in-flight calls; cost = profile × tokens.

**Reference:** `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`; `.../Handlers/CompletionHandler.cs:60-210`.

**Without it:** JSON parse exceptions in production; silent budget overruns; a "cheapest" router ignoring a caller's deliberate model order (recorded as a real bug at `CompletionHandler.cs:78-85`).

### 4.5 Topology-driven shape selection

**Build:** plan graph (workstreams, dependencies, bound capability or reasoning node), validator (acyclic, closed kinds, testable acceptance criteria), capability binder with per-workstream authorization, and a **pure classifier**: ≥2 components → multi-squad; 1 capability node → direct capability; 1 reasoning node → direct specialist; ≥2 connected → single squad. Unbacked derived shape → limitation, never a smaller guessed shape.

**Invariants:** exactly one shape; smallest sufficient; classification independent of any importance score; unbacked ⇒ limitation; zero bound nodes is an error.

**Reference:** `.../Planning/TopologyClassifier.cs:28-102`; `ExecutionPlanner.cs:143-230`; `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md`; `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs`.

**Without it:** fan-out driven by ambiguity (the exact failure ADR 0001 removes); agent swarms for questions one tool call answers.

### 4.6 Append-only trace as the runtime↔learning contract

**Build:** closed event enum (~21), typed lifecycle-event family projecting to one flat row with `PayloadJson`, correlation keys (`interactionId`, `businessStateId`, `executionId`, `traceReference`), stage telemetry.

**Invariants:** enum closed and exhaustive; lossless projection; correlation keys always present; replay deterministic.

**Reference:** `apps/Send.Usage.Collector/src/.../Domain/{OutcomeTraceEvent,OutcomeTraceEventType,OutcomeTraceLifecycleEvent}.cs`; `.../Application/Outcome/IOutcomeTraceEmitter.cs`; `.../Runtime/TurnStage.cs`.

**Runner-up (worth a chapter, not a build):** the pre/post-LLM "governance sandwich" (`docs/architecture/governance-architecture.md:223-273`) — mostly the composition of 4.1, 4.2 and 4.4, and the clearest one-diagram explanation of the architecture.

### 4.7 Mapping onto the learning repo's `agentlab/` package

The course package already exists and is well aimed: `agentlab/orchestrator/__init__.py` states the theme as *"smallest sufficient shape"* — the exact rule `TopologyClassifier` implements. Suggested homes:

| SendOS mechanism | `agentlab/` target |
|---|---|
| 4.1 typed decision + approval gate | `agentlab/types.py` (discriminated outputs) + `orchestrator/approval.py` (planned: suspend/resume) |
| 4.2 capability catalogue + authority | `tools/registry.py` (one object owns schema + handler) + a small new `authority.py` |
| 4.3 trace → eval → publish | `trace.py` (append-only, monotonic, already the right shape) + `evals/harness.py` + a new `evals/promote.py` |
| 4.4 structured output + budget routing | `providers/*` + `budget.py`/`pricing.py`; add the schema-reject-and-retry layer |
| 4.5 topology-driven shape selection | `orchestrator/plan.py` + `orchestrator/orchestrator.py` |
| 4.6 trace contract | `trace.py` event kinds (`approval_requested/granted/denied`, `tool_call`, `eval_case`) map 1:1 onto SendOS lifecycle events |

---

## 5. Where SendOS departs from mainstream practice

| Area | SendOS choice | Mainstream alternative | Transferable skill |
|---|---|---|---|
| Orchestration runtime | One procedural class (`DecisionRuntime.cs`, 5,379 lines) with typed seams; no graph interpreter | LangGraph/AutoGen/CrewAI; Temporal; DBOS | When a state machine beats a framework, and how property tests compensate for a large procedural core |
| Structured output | Hand-rolled JSON Schema subset; generate → parse → reject; no constrained decoding | Provider structured outputs; GBNF/Outlines; PydanticAI typed tools | Validated-after vs impossible-to-emit |
| Learning | Asset/policy refinement + human publish gate; **no weight training, no RLHF** | DPO/RLHF/SFT; DSPy prompt optimisation | Cheapest intervention that changes behaviour |
| Authorization | In-house ABAC intersection; authority **discovery** (OrgIntel graph) separate from **permission** | Cedar/OPA; OpenFGA/Zanzibar | "Who should decide" vs "who may act"; deny-by-default arithmetic |
| Policy assets | Versioned JSON assets validated by app code | OPA/Rego; Cedar; Starlark | Versioned config vs executable policy |
| Event log | Append-only audit/learning stream — **not** event sourcing | Event sourcing + CQRS projections | Know which one you are building |
| Durable execution | `CaseRuntime` built, unwired; Business_State is the de-facto durability spine | Temporal/DBOS; checkpointers | Suspend/resume, CAS on resume, deadline sweeps |
| Multi-tenancy | Tenant scope threaded through every call and query | Postgres RLS; schema-per-tenant | Defence in depth for isolation |
| Tool discovery | Connector manifest endpoint assembled into a registry | MCP servers/clients | Manifest catalogues vs runtime introspection |
| Agent tracing | Custom `TurnStage` enum + JSON payloads; metrics/traces stubs | OpenTelemetry GenAI conventions | What to record so a failed turn is diagnosable |
| Self-improvement | Human-gated promotion; a model can only `Draft` | Auto-publish loops; online RL | Governance as a product feature |

Net: SendOS is **ahead of mainstream tutorials** on governance (approval binding, authority intersection, append-only trace, publish gates) and **behind** on orchestration ergonomics (no graph runtime, durable engine unwired, thin observability). Reproduce the first; learn the second from frameworks.

---

## 6. Reading order — shortest path to a productive contribution

| Step | Read | Time | Why |
|---|---|---|---|
| 1 | `docs/business/01-what-is-sendos.md` | 5 min | Product story |
| 2 | `README.md` → "Implementation Status", "Decision-First Runtime" | 25 min | What is claimed built (note stale flag language) |
| 3 | `docs/architecture/system-architecture.md` §1, §4 | 20 min | 10 principles; immediate vs durable path |
| 4 | `docs/runtime-orchestration-flow.md` §1-4 (distrust §9: shape selection is now topology) | 30 min | The cast: Meta-Orchestrator, Planner, Squad leader, Specialist |
| 5 | `docs/adrs/0001-...md` | 10 min | Why topology replaced materiality — a model ADR |
| 6 | Code: `DecisionInteraction.cs` → `IntentElevator.cs` → `ExecutionPlanner.Plan` → `TopologyClassifier.cs` → `ApprovalCheckpoint.cs` | 2–3 h | The four mechanisms you will actually touch |
| 7 | `docs/architecture/governance-architecture.md` §2b, §5, §6b | 40 min | Two lifecycle state machines and the publish gate |
| 8 | `docs/architecture/lower-layer-learning-loop.md` §1b, §3, §4 | 40 min | Trace → insight → candidate → publish, and what is missing |
| 9 | `docs/architecture/reconciliation-audit.md` §F | 30 min | Honest map of what is dark; read last so you can check it |
| 10 | `docs/tech-week/runbook.md`, `demo-workflows-v2.md`, `tools/techweek/acceptance/demo7_acceptance.py` | 45 min | Closest thing to a live acceptance spec — and Python, a model for our labs |

**Skip until needed:** `docs/architecture/authority-graph-architecture.md`, `performance-architecture.md`, `connector-architecture.md`, `docs/licensing/**`, `infra/**`.

**First-contribution candidates (audit §F, confirmed against code):** structured action arguments never reaching the connector (#24), per-connector write readback verification (#39), wiring `DistillationWorkProcessor → DistillationEngine` (#45), registering the `DecisionTask` deadline worker (#35), and docs-drift fixes (cheapest, most visible).

---

## 7. What I could not assess

- **Anything runtime.** I did not build, test, or execute the stack (forbidden). No verification of DI wiring, no measured Postgres/Redis/Apache AGE/pgvector behaviour, no confirmation the 6,300+ tests pass, no live provider calls, no licensing-service runtime behaviour, no front-end/pack behaviour.
- **The target-design set.** `README.md` and `docs/README.md` point at `send-documentation/sendos-technical`; **that directory does not exist in this repo**, so target claims (Squads, Intelligence Candidates) could only be read through their implementation and repo docs.
- **Depth-limited areas:** `Send.License.Service` (336 files), `Send.Integration.Service` (835 files), `Send.Intel.Server` control-plane detail beyond publish/lifecycle, `Send.Intel.Admin`, `Send.Intelligence.Gateway`, `sdk/`, `infra/`, `tools/techweek`, and the 150 KB `docs/platform-completion-ledger.md`.
- **Which contradictory doc is intended.** Three vintages disagree (§0). I used the rule stated at `docs/README.md:12` — code is authoritative — but could not tell which docs are actively maintained.
- **The legacy path.** `POST /api/agent/execute` (`Controllers/AgentController.cs`) is the legacy 9-stage pipeline; the audit calls it an ungoverned second runtime. I did not trace it end-to-end.

---

*Every mechanism in §4 is small enough to rebuild in a weekend, and faithful enough that reading the SendOS original afterwards will feel like reading your own notes.*
