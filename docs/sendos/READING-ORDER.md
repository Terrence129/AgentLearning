# Reading order — the shortest path to a productive contribution

**Living document.** Ten steps, in order, with a time budget and what to look for. Total: **~1
working day** of reading, spread over the first two weeks. After step 10 you can find your way
around the platform, verify a claim against code, and pick up a real task.

> **Code wins over docs.** Paths are relative to the SendOS repo root (`SendOs/`). Where a doc
> contradicts code, this page follows code and flags the drift. Evidence base:
> [`CONCEPT-MAP.md`](./CONCEPT-MAP.md). Week-by-week depth: [`BRIDGE.md`](./BRIDGE.md).

---

## The ten steps

| # | Read | Time | Look for | Output |
|---|---|---|---|---|
| 1 | `docs/business/01-what-is-sendos.md` | 5 min | The product story: a shared intelligence layer under five business products. Why the platform, not an app | One sentence: what SendOS sells |
| 2 | `README.md` → "Implementation Status" + "Decision-First Runtime" sections | 25 min | What is claimed built vs pending; the status vocabulary (Implemented / Partial / Scaffolded / Placeholder / Planned) | A list of claims you will later verify in code |
| 3 | `docs/architecture/system-architecture.md` §1 (10 principles), §4 (two request paths) | 20 min | The non-negotiables: case-first, playbooks accelerate never required, discovery ≠ permission, source systems stay authoritative | The 10 principles, paraphrased |
| 4 | `docs/runtime-orchestration-flow.md` §1–4 **only** (read §9 but distrust it — shape selection is now topology; see Appendix B of the bridge) | 30 min | The cast: Meta-Orchestrator, Planner, Squad leader, Specialist; definition vs instance; what crosses back to the client | A diagram you draw yourself |
| 5 | `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` | 10 min | Why materiality stopped selecting shapes; how a decision of this size is recorded. This is the template for your own design write-ups | Three sentences on the trade |
| 6 | **Code**, in this order: `Domain/Decision/DecisionInteraction.cs` → `Application/IntentElevation/IntentElevator.cs` → `Application/Planning/ExecutionPlanner.cs` (`Plan`) → `Planning/TopologyClassifier.cs` → `Application/Approval/ApprovalCheckpoint.cs` | 2–3 h | The four mechanisms you will actually touch: typed decisions, deterministic policy over model output, topology selection, bound approval | Your own mini-diagrams, annotated with `path:line` |
| 7 | `docs/architecture/governance-architecture.md` §2b, §5, §6b | 40 min | The two lifecycle state machines, the pre/post-LLM "sandwich", and the publish gate that a model cannot bypass | The governance sandwich, from memory |
| 8 | `docs/architecture/lower-layer-learning-loop.md` §1b, §3, §4 | 40 min | Trace → insight → candidate → human-gated publish; the two learning outputs and their different admission rules | Where the loop stops and why |
| 9 | `docs/architecture/reconciliation-audit.md` §F (status matrix) | 30 min | The honest map of what is dark/unwired, with exact remaining work per subsystem. Read it **last** so you can check it | Three rows you disagree with, or confirm |
| 10 | `docs/tech-week/runbook.md`, `docs/tech-week/demo-workflows-v2.md`, `tools/techweek/acceptance/demo7_acceptance.py` | 45 min | The closest thing to a live acceptance spec — and a Python harness that black-box tests seven end-to-end scenarios against the real runtime | How *you* would write the acceptance test |

**Skip until needed:** `docs/architecture/authority-graph-architecture.md` (1,200+ lines on OrgIntel),
`performance-architecture.md`, `connector-architecture.md`, `docs/licensing/**`, `infra/**`,
`docs/platform-completion-ledger.md` (150 KB tracker).

**Do not read end-to-end:** `Application/Runtime/DecisionRuntime.cs` (5,379 lines) and
`MetaOrchestrator.cs` (2,685). Read their *method signatures* and the sections listed in the bridge;
read bodies only when chasing a specific behaviour.

---

## How to read a SendOS file (the 10-minute method)

1. **Header first.** These files carry unusually good doc comments stating *why* the type exists,
   what it prevents, and which requirement it satisfies. The comments are the design document.
2. **The type declaration.** Fields/parameters are the contract; note which are capability/risk/
   authority metadata and which are payload.
3. **Validation and refusal branches.** Search for `throw`, `return false`, `Limitation`,
   `NoCapabilityResolved`, `Denied`. The refusals are the product.
4. **The tests.** `apps/Send.Agent.Runtime/tests/**/Properties/*.cs` encode invariants as property
   tests. A property test is a spec you can run.
5. **Then the body** — only for the one behaviour you are changing.

---

## Three first-contribution candidates

Ranked by *time-to-merge* (all are small, well-scoped, and grounded in the repo's own audit). Pick
one after step 9.

### Candidate 1 — Fix documentation drift (best first PR)

**Why:** five verified doc-vs-code contradictions are listed in [`CONCEPT-MAP.md`](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins).
Stale docs actively mislead every new engineer, and the repo's own culture already treats claims as
defects (its audit cites `file:line`).

**First files:** `README.md` §"Implementation Status"; `docs/README.md`;
`docs/business/09-status-and-roadmap.md`; `docs/runtime-orchestration-flow.md`;
`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417`;
`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Planning/ExecutionPlanningOptions.cs:75`.

**Done when:** each corrected claim cites the file/line that proves it; the flag language matches
`Program.cs:417`; the shape-selection section matches `ExecutionPlanner.cs:143-219`; a maintainer
can re-verify the page in under five minutes.

**Ask first:** which docs are still maintained — `README.md`/`docs/` vs the external
`send-documentation/sendos-technical` set (the latter is not in this repo).

### Candidate 2 — Per-connector write readback verification (audit #39)

**Why:** the runtime records a write as successful on a transport acknowledgement plus an external
id, so an acknowledged-but-ineffective write looks identical to a real one. `ExecutionResult`
already carries `ReadbackVerification` (`Verified | Contradicted | Unconfirmed | NotPerformed`) and
`CapabilityDefinition` already has `VerificationStrategy` — the enum and the seam exist; the
per-connector strategies do not.

**First files:** `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs`
(`ReadbackVerification`, lines ~447–536); `.../Domain/Capabilities/CapabilityDefinition.cs`
(`VerificationStrategy`); `libraries/Send.Connectors.Abstractions/IReadbackActionConnector.cs`;
one connector in `apps/Send.Integration.Service/src/.../Connectors/Write/` (e.g. Jira);
`.../Application/Evaluation/**` (the result verifier that consumes the verdict).

**Done when:** an acknowledged write whose effect is absent from the source of record is returned
as `Contradicted` and success is withheld (fails closed); a connector that cannot observe its writes
still returns `NotPerformed`; a unit test covers all four verdicts without network.

**Ask first:** which connector is safe to exercise in dev, and whether readback is expected to cost
an extra source call per write (it is — that is the trade).

### Candidate 3 — Structured action arguments never reach the connector (audit #24)

**Why:** understanding extracts `Action`, `Entities` and `Parameters`, capability *selection* uses
them, but the executable action is built with empty `NormalizedArguments` — so even the one reachable
write (`jira.issue.transition`, which needs a `transitionId`) sends nothing. It is a small,
well-bounded data-flow fix with an obvious test: the bound arguments arrive at the connector.

**First files:** `apps/Send.Agent.Runtime/src/.../Application/Runtime/DecisionRuntime.cs`
(`BuildExecutableAction`, around line 1665 per the audit; `SemanticInputBinding`,
`UnboundRequiredInputs`); `.../Domain/Execution/ExecutableAction.cs`;
`.../Application/Execution/SemanticInputBinding.cs`;
`.../Application/Goals/DeterministicMissingInformationResolver.cs`;
`.../Domain/Goals/MissingInformation.cs`;
`.../Application/Execution/AuthoritativeActionExecutor.cs`.

**Done when:** a turn that states an entity and the required value binds them onto the capability's
declared inputs; a turn that states neither asks one focused question instead of proposing an
unexecutable action; both behaviours are unit-tested and the proposal shows the arguments the
person is approving.

**Ask first:** which capability has a declared, non-secret input that is safe to exercise end-to-end
in dev.

### Runner-ups (for later)

- Wire `DistillationWorkProcessor → DistillationEngine` (audit #45) — the learning loop is real but
  uncalled; a seeded batch producing a gated insight is a credible demo.
- Register the `DecisionTask` deadline worker (audit #35) — durable case machinery exists, no
  production caller.

---

## After the first contribution

1. Ask for a second task in the same subsystem you touched — depth beats breadth for the internship.
2. Update this file and [`BRIDGE.md`](./BRIDGE.md) with whatever you verified differently. The
   learning repo is only as good as its freshness.
3. Write the one-page improvement proposal recommended in week 9 (durable approval resume, or
   trace → candidate evidence gating) and send it to a senior engineer.
