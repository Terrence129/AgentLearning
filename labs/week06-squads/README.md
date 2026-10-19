# Week 6 — Planning, orchestration and human approval

> **Lab id:** `week06-squads` · **Owned package:** `agentlab/orchestrator/`
> **Starter:** the files in `agentlab/orchestrator/` (they raise `NotImplementedError`)
> **Reference:** `solutions/week06/agentlab/orchestrator/`
> **Tests:** `tests/week06/`

> **The most important artifact in this course is `approval.py`.** The plan
> validator and the topology classifier are useful; the approval binding is the
> difference between a governed agent and a liability. Implement and test it
> first, and re-read `/review` your invariants before moving on.

## 1. Why this week exists

Two failures dominate production multi-agent systems: **too much shape** (a
swarm for a question one tool call answers, fan-out driven by ambiguity) and
**too little control** (a model-settable "approved" flag, duplicate side effects
on retry, approvals outliving the authority they were granted under). SendOS's
ADR-0001 replaced topology-by-vibes with a pure classifier — one capability node
→ direct call, one reasoning node → one specialist, ≥2 connected nodes → one
squad, ≥2 components → multiple squads — and refuses to guess a smaller shape
when the runtime cannot back the derived one
([`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.5).
Its `ApprovalCheckpoint` binds every write to the exact action, actor, tenant,
authority snapshot and expiry, and executes at most once (§4.1). This week you
rebuild both, small enough to hold in your head and test exhaustively.

Without this week, "AI recommends, a human approves, the backend executes" is a
sentence in a pitch deck rather than a property of the system.

## 2. Prerequisites & time budget

- **Time:** 10–12 h (plan/approval ≈ 5 h, orchestrator ≈ 3 h, reading/review ≈ 3 h).
- **Must be green:** foundation (`pytest -q`); week 2's loop is *not* required —
  this package has its own tiny driver inside `specialist.py`.
- **Reading:** `docs/research/01-agent-architecture-sota.md` §6 (§6.2 HITL,
  §6.4 pause/resume state machine); `docs/research/05-sendos-concept-map.md`
  §4.1 and §4.5; ADR-0001 in the SendOS repo.
- **Tools:** `MockProvider` for every model interaction; a fake clock for
  expiry; no sleeps, no network.

## 3. The spec

Implement every `NotImplementedError` in `agentlab/orchestrator/`.

| File | Public surface | Contract summary |
|---|---|---|
| `plan.py` | `NodeKind`, `Workstream`, `Plan`, `PlanError`, `validate_plan`, `topo_order`, `ready_workstreams`, `ReplanDecision`, `replan_after_failure` | Closed kinds `capability`/`reasoning`; capability nodes must name a capability, reasoning nodes must not; unique ids, known dependencies, acyclic graph, non-empty acceptance criteria, positive budgets. Topological order is deterministic (Kahn, declaration order). Replanning drops the failed node and its transitive dependents, refuses to exceed the retry budget, and refuses to empty the plan. |
| `specialist.py` | `ContextEnvelope`, `HandoffArtifact`, `SpecialistSpec`, `Specialist`, `SpecialistError` | Least-context input (objective/facts/constraints/references — **no transcript field**); only allowlisted tools are exposed, and calls to others become error observations without execution; the loop charges and enforces an optional budget; the final answer must be a JSON hand-off (`summary` required; `findings`/`artifacts` string arrays; `confidence` in `[0,1]`) or `SpecialistError`; trace emits `subagent_start`/`subagent_end` on a child scope carrying the summary/confidence/finding count, never the transcript. |
| `orchestrator.py` | `ExecutionShape`, `ShapeSelection`, `component_ids`, `classify_shape`, `select_shape`, `WorkstreamResult`, `OrchestrationResult`, `Orchestrator`, `CapabilityExecutor` | Pure classifier over plan topology. Unbacked derived shape → `shape=None`, `backed=False`, and a limitation that names the shape and refuses to guess smaller. Execution: validate → select shape → short-circuit with a limitation if unbacked → run in deterministic dependency order; capability nodes call plain functions, reasoning nodes run registered specialists with envelopes built from the objective, plan goal and upstream outputs; failed dependencies skip dependents (never guess); missing executors/specialists, specialist errors and budget overruns are reported per workstream; aggregate budget sums the per-workstream ledgers. |
| `approval.py` | `ApprovalState`, `Authority`, `ActionProposal`, `action_hash`, `ApprovalBinding`, `ApprovalRecord`, `ExecutionResult`, `ApprovedAction`, `ProposalStore`, `InMemoryProposalStore`, `ApprovalCheckpoint`, typed errors | See the invariants below — they are the spec. |

### The invariants (tested one by one in `tests/week06/test_approval.py`)

1. **Persisted before approval.** `propose` writes the proposal to the store and
   only then opens a PENDING approval; `approve` refuses a proposal that is not
   in the store; a store failure leaves no approval behind.
2. **Exact binding.** `ApprovalBinding(actor, tenant, action_hash,
   authority_snapshot, expires_at)` binds the human decision to the canonical
   action. A mismatched hash is rejected at approval; editing the persisted
   proposal after approval blocks execution.
3. **Proposer ≠ approver.** Self-approval is not a control.
4. **Tenant match.** Approvals cannot cross tenants.
5. **Expiry.** An expired binding can be neither approved nor executed; the
   record moves to `EXPIRED`.
6. **Authority.** The approver's snapshot must cover the action's required
   authority; at execution, *current* authority must still cover the snapshot —
   narrowing between approval and execution blocks the write.
7. **At-most-once.** Execution is reserved (state persisted as `EXECUTED`)
   *before* the executor runs; a replay raises `ApprovalReplayRejected` and the
   executor is called once. Every effect carries a deterministic
   `idempotency_key`. An executor failure marks `FAILED` and never retries.
8. **State machine.** `PENDING → APPROVED | REJECTED | CANCELLED`,
   `APPROVED → EXECUTED | REVOKED`, `PENDING | APPROVED → EXPIRED`; everything
   else raises `InvalidApprovalTransition`. Every step emits
   `approval_requested` / `approval_granted` / `approval_denied` /
   `tool_call` trace events (arguments are not logged; only the action and the
   idempotency key).

## 4. Acceptance criteria

```powershell
# Windows (PowerShell)
# 1. starter red
.\.venv\Scripts\python.exe -m pytest tests/week06 -m week -q

# 2. green after implementing
.\.venv\Scripts\python.exe -m pytest tests/week06 -m week -q

# 3. lint
.\.venv\Scripts\ruff.exe check agentlab/orchestrator tests/week06

# 4. foundation green
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
# 1. starter red
uv run pytest tests/week06 -m week -q

# 2. green after implementing
uv run pytest tests/week06 -m week -q

# 3. lint
uv run ruff check agentlab/orchestrator tests/week06

# 4. foundation green
uv run pytest -q
```

Manual acceptance (the learning-plan deliverable): a miniature "should we
discount this deal?" flow — meta-orchestrator → 1–2 specialists → typed decision
→ approval-gated write → audit row — built as a local script or notebook on top
of this package, plus a test (in your own notes/script, not in
`tests/week06/`) proving an edited, replayed or expired approval cannot execute.

## 5. Hints (progressive)

1. **Order of checks in `approve` matters for the tests:** not found → state →
   persistence → proposer → tenant → hash → authority → expiry. Each check has
   a distinct error type; do not collapse them into one.
2. `action_hash` must hash `{"action", "arguments", "tenant"}` with
   `sort_keys=True`; key order in a Python dict is not stable across callers.
3. Persist the **executed** state before calling the executor. If you call the
   executor first and then write the record, a crash in between gives you two
   side effects on retry — the exact bug at-most-once exists to prevent.
4. Compare authority in the right direction: at approval, `snapshot.covers(required)`;
   at execution, `current.covers(snapshot)`. "No amount limit" (`None`) covers
   any amount; a numeric cap only covers a smaller-or-equal required cap.
5. Shape selection is a *pure* function of topology. If any test outcome depends
   on budgets or objectives, you have put policy where classification belongs.
6. For the classifier, dependency edges are undirected when counting connected
   components. "≥ 2 connected nodes" means one component with ≥ 2 nodes.
7. In the specialist, validate the hand-off **before** it crosses the boundary.
   A malformed JSON response is a failed specialist, not a partial result.
8. `Orchestrator.run` must not raise for a failed workstream — failures are
   data (`WorkstreamResult.error`) so a human/replan layer can decide. Invalid
   *plans* still raise `PlanError`.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| `test_proposal_edited_after_approval_cannot_execute` passes but replay test fails | You check the hash at execution time but re-read the binding from the *caller*, or you re-reserve `EXECUTED` on every call. |
| `AuthorityNarrowed` raised for a clearly sufficient authority | You reversed the argument order: it is `current_authority.covers(binding.authority_snapshot)`. |
| Approval "works" but `pending()` is empty | `_transition` created a new record without replacing it in the checkpoint's map. |
| `classify_shape` returns SINGLE_SQUAD for two independent workstreams | You counted dependency *edges* instead of connected components; two nodes with no edges are two components. |
| Unbacked shape test still executes specialists | You returned a limitation but continued into the execution path; short-circuit immediately after `select_shape`. |
| `OrchestrationResult.ok` is True after a dependency failure | `ok` must require `result.ok or result.skipped` for **all** workstreams, and a skipped-but-blocked branch may still make the run not-ok via the failed dependency. |
| Specialist test finds "not in this specialist's tool set" in the *first* tool message | That message is correct — the forbidden tool must not run, but the model must see why. Check the handler-invocation list, not the prompt. |
| Expiry test flakes | You used `time.time`; inject the fake clock through `ApprovalCheckpoint(clock=...)` and build `expires_at` from it. |

## 7. SendOS bridge

Read (45 min, read-only), with paths from
[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)
§4.1 and §4.5:

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs`
  (typed decision family);
- `.../Application/Approval/ApprovalCheckpoint.cs` (lines ~237–468) and
  `.../Properties/ApprovalBindingAtMostOncePropertyTests.cs`;
- `.../Planning/TopologyClassifier.cs` (~28–102),
  `.../Planning/ExecutionPlanner.cs` (~143–230), and
  `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md`;
- `.../Domain/Authority/EffectiveAuthority.cs` and
  `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs`.

Answer in your lab notes:

1. Which invariants does `ApprovalCheckpoint.cs` enforce that this miniature does
   **not** (durability across process restart, revocation feeds, dual control,
   compensating actions), and what is the smallest test that would prove each?
2. Where does `TopologyClassifier` take inputs that are *not* pure topology
   (flags, importance scores, planner hints), and why does ADR-0001 explicitly
   keep classification orthogonal to review mode?
3. If you added durable suspend/resume to `ApprovalCheckpoint` (SQLite + resume
   on callback + CAS against double-resume), which of this week's invariants
   would still hold by construction, and which would now depend on the database
   transaction boundary?

## 8. Stretch (optional)

1. **Durable suspend/resume.** Persist pending approvals to SQLite, return a
   token to the caller, and resume execution from a callback process. Use a
   compare-and-swap on `(approval_id, state)` so two concurrent resumes produce
   exactly one execution. This is SendOS's unwired `CaseRuntime`; a working
   miniature is a credible contribution proposal.
2. **Property tests for the invariants.** Without adding `hypothesis`, loop over
   generated approval sequences (approve/reject/revoke/expire/execute in every
   order) and assert at-most-once, terminal states are terminal, and no sequence
   executes without an APPROVED state.

## 9. Reflection (weekly review)

1. **Conceptual:** why is an approval a *binding over a hash* rather than a
   message saying "approved"? Which of the seven invariants becomes impossible
   to enforce without the hash?
2. **Architectural:** the classifier refuses to downgrade an unbacked shape.
   Where else in the system should "refuse rather than guess" apply, and what is
   the cost of that refusal to a product team?
3. **Transfer:** when would you deliberately choose a *larger* shape than the
   topology requires (e.g. two specialists where one would do), and what would
   you measure to justify it afterwards?
