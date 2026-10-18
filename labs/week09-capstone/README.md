# Week 9 — Capstone: Mini-SendOS

**Time:** 12–16 h · **Prerequisites:** weeks 1–8 green (`tests/week01`–`tests/week08`), `scripts/demo_capstone.py` runnable · **Module:** `agentlab/capstone/`, `agentlab/web/` · **Tests:** `tests/week09`

## 1. Why this week exists

Every previous week built one mechanism in isolation. This week composes them into one honest, governed system: a goal becomes a typed decision, a state change becomes a persisted proposal, a human approves it with binding checks, execution happens at most once, and every step lands in an append-only audit trail. The failure this prevents is the demo that looks intelligent and cannot be trusted — model-authored "approved" booleans, duplicate side effects on retry, and no evidence of who approved what or under which authority. Nothing new is invented this week; the work is integration, and integration is where the course's claims get tested.

## 2. Prerequisites and time budget

| Area | Must be true before you start |
|---|---|
| Weeks 1–2 | provider seam + loop green — the capstone reuses `Provider`, `ToolRegistry`, `Budget`, `Tracer` |
| Week 3 | structured output + prompt versions green — decisions are the same discipline |
| Week 4 | context/memory green — the decision pipeline must fit a context budget |
| Weeks 6–8 | approval, authority, audit, evals green — the capstone composes them |
| Tooling | `.\.venv\Scripts\python.exe` works; run everything from the repo root |

Suggested split: 2 h read the brief + starter contracts; 6–8 h implement `decisions.py`, `catalogue.py`, `platform.py`; 2 h wire `web/`; 1 h demo + acceptance; 1–2 h write-up and reflection.

## 3. The spec

Run the prerequisite check first — it tells you what is missing, in order:

```powershell
.\.venv\Scripts\python.exe scripts\demo_capstone.py
```

You are done when that script exits `0` and prints `DEMO COMPLETE`.

### Step 1 — Provider layer (reuse, don't rebuild)

`agentlab/capstone/platform.py` receives a `provider` (`agentlab.providers.base.Provider`), a `tools` registry, and a `catalogue`. The demo passes `agentlab.testing.MockProvider`. Do not add network calls to the capstone flow; a live-provider run is the *stretch*, behind `@pytest.mark.network`.

### Step 2 — Capability catalogue: `agentlab/capstone/catalogue.py`

| Symbol | Contract |
|---|---|
| `CapabilityDefinition` | frozen dataclass: `id`, `description`, `input_schema`, `risk_level`, `is_write`, `approval_required`, `tenant_ids`, `version`, `source` |
| `CapabilityCatalogue.merge(connectors, published)` | validate both sources; duplicates *within* a source raise `CatalogueError`; published wins on id conflicts (whole definition, never field-merged); result order-independent |
| `CapabilityCatalogue.resolve(id, tenant)` | return the definition when known and permitted, else `CapabilityNotAvailable`; unknown and "not for this tenant" must be indistinguishable (no cross-tenant oracle); empty tenant fails closed |
| `CapabilityCatalogue.list_for_tenant(tenant)` | sorted tuple, universal + tenant-scoped |
| `CapabilityCatalogue.ids()` / `__len__` | sorted ids / count |

Fail-closed rules (tests enforce them): snake_case ids, `input_schema` is `type: object`, valid risk level, **every write declares `approval_required=True`**, and an empty `tenant_ids` set is invalid.

### Step 3 — Typed decisions: `agentlab/capstone/decisions.py`

Implement the closed union documented at the top of the file: `parse_decision`, `decision_to_wire`, `enforce_presentation_budgets`. The wire contract table is the specification; the tests are the proof. Three things to get right:

1. **Validate fully before raising.** `SchemaValidationError.errors` lists *every* problem, not the first.
2. **Closed union.** Unknown kinds and unknown fields are rejected; the model cannot smuggle new keys into the contract.
3. **Presentation budgets.** Headline ≤ 12 words, `next_moves` ≤ 4, clarification `options` ≤ 3, and the single primary text field ≤ 2 sentences. Collect all violations into one `PresentationBudgetError`.

### Step 4 — The governed lifecycle: `agentlab/capstone/platform.py`

| Method | Invariant |
|---|---|
| `action_digest(capability_id, arguments)` | deterministic hash; key order must not matter |
| `submit_goal(request)` | authenticated goal → one budget-safe `Decision`; no catalogue bypass |
| `propose_action(...)` | capability resolved for the tenant; writes only; **proposal persisted before approval**, with `action_hash` and `expires_at` |
| `approve(proposal_id, approver_id, approved)` | unknown/expired → `ApprovalError`; proposer ≠ approver; decision persisted and audited |
| `execute(proposal_id, approval_id)` | missing/rejected/expired/mismatched approval → `ExecutionError`; **at most once**; executes via `tools`; audits start + finish |
| `audit_trail()` | append-only, strictly increasing `seq` from 1, never mutated or removed |

### Step 5 — The surface: `agentlab/web/`

`agentlab/web/app.py` is written but stubbed: `create_app(platform)` wires routes `POST /api/goal`, `POST /api/proposals`, `POST /api/proposals/{id}/approve`, `POST /api/proposals/{id}/execute`, `GET /api/audit` and the HTML page. FastAPI is an optional extra — importing `agentlab.web` must work without it. Run the UI with:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[web]"
.\.venv\Scripts\python.exe -c "from agentlab.web.app import create_app, main; main()"
```

No route may invent text: the UI renders the typed decision and forwards approval/execution to the platform.

### Step 6 — Learning loop, demo and write-up

- The audit trail is your eval substrate: after the demo, read `audit_trail()` and confirm the exact sequence `proposal_created → approval_granted → execution_started → execution_finished` (at minimum).
- `scripts/demo_capstone.py` is the end-to-end acceptance: offline, mock provider, exits `0`.
- Fill `projects/capstone/ACCEPTANCE.md`, then write up the design in `projects/portfolio/WRITEUP.md`.

## 4. Acceptance criteria

```powershell
# 1. starter is replaced by your implementation; lab tests green
.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q

# 2. the demo runs the whole lifecycle offline and exits 0
.\.venv\Scripts\python.exe scripts\demo_capstone.py

# 3. foundation still green (default pytest excludes week markers)
.\.venv\Scripts\python.exe -m pytest -q

# 4. lint your files
.\.venv\Scripts\ruff.exe check agentlab\capstone agentlab\web tests\week09

# 5. web imports without FastAPI installed
.\.venv\Scripts\python.exe -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"
```

Strong submission also shows: two tenants cannot see each other's capabilities; a replayed approval cannot execute twice; and editing the proposal arguments after approval blocks execution (hash mismatch). Add those as tests in `tests/week09/test_capstone_extra.py` (mark them `pytest.mark.week`).

## 5. Hints (progressive)

1. Read the module docstring of `decisions.py` first; the wire table is the test spec in prose.
2. Implement `parse_decision` before `decision_to_wire`; then round-trip in a REPL until it is boring.
3. In `catalogue.merge`, process connectors first and published second — "published wins" then falls out of dict assignment order.
4. For `resolve`, build the availability predicate once; the "same error" rule is easier when both branches share it.
5. In `platform.propose_action`, compute the digest from canonical JSON (`sort_keys=True`) *before* persisting; the approval binds to that string, not to a re-derived copy.
6. Store the approval's `proposal_id` **and** compare it to the proposal's `action_hash` at execute time; matching ids alone is not binding.
7. Keep the audit append in a single helper (`_audit.append(...)`) so `seq` cannot skip.

## 6. Debugging guide

| Symptom | Meaning / fix |
|---|---|
| `NotImplementedError: Week 9 capstone: implement ...` | Expected on the starter. Build in the order the demo prints. |
| `SchemaValidationError: unknown field(s) for ...` | Your wire payload has a key the contract does not allow; check the docstring table. |
| `CatalogueError: write capability ... must set approval_required=True` | Fail-closed rule; a write may not be auto-approved by omission. |
| `ApprovalError` on a fresh approval | Maker-checker: the demo's approver must differ from the proposer (analyst vs manager). |
| `SystemExit: demo expected an action_proposal` | `submit_goal` consumed the scripted mock turn somewhere else; make it parse the text turn and return the decision. |
| `ModuleNotFoundError: agentlab` when running the demo | Run from the repo root (`.\.venv\Scripts\python.exe scripts\demo_capstone.py`). |
| `ConfigError: FastAPI is not installed` | Optional extra missing: `pip install -e ".[web]"`. Import of the module must still work. |

## 7. SendOS bridge

Read these before answering the questions (paths relative to the SendOS repo root; see [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) for the verified map):

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs` + `Application/Decision/PresentationBudgetEnforcer.cs` — the closed response family and its UI budgets.
- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Approval/ApprovalCheckpoint.cs:237-468` — proposal persisted before approval; binding to tenant/actor/action hash/authority version/expiry; proposer ≠ approver; at-most-once.
- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` — three declaration sources, published-wins, tenant filtering.
- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Authority/EffectiveAuthority.cs` + `Application/Authority/AuthoritySources.cs` — the intersection that a capstone approval should be bound to.

Answer in `notes/week09-sendos-bridge.md`:

1. `ApprovalCheckpoint` binds an approval to more than a proposal id. List the fields it checks and mark which ones your `ActionProposal`/approval flow is missing. What attack does each missing field allow?
2. `CapabilityCatalogueAssembler` merges **three** sources with published-wins. Your capstone merges two. What would break if you added the third (platform-owned declarations) in the wrong order, and how do the tests in the SendOS repo guard it?
3. `DecisionInteraction` is a closed type family enforced by the type system. Your capstone enforces a closed union at parse time. Name one defect class each approach catches and one each misses.

## 8. Stretch

1. **Durable suspend/resume (the credible SendOS contribution):** persist proposals and approvals in SQLite; `execute` becomes a two-phase operation; a callback resumes an approval that arrived after a restart; CAS against double-resume. SendOS's `CaseRuntime` is built but unwired — a miniature is a design sketch for a real proposal.
2. **Eval-gated asset promotion:** add `agentlab/capstone/promote.py` where a candidate prompt/asset can only become `published` after an eval threshold and a human approval row. Keep the model's output restricted to `draft`.

## 9. Reflection

1. **Conceptual:** why must the proposal be persisted *before* approval? Describe the failure that appears if it is persisted after.
2. **Architectural:** `platform.py` is one class on purpose. Which responsibilities would you split out first if this were a real service, and which invariants would you test at each new boundary?
3. **Transfer:** pick one SendOS mechanism from §7. What does your miniature get right, and what does SendOS do that you deliberately left out — and is that difference about scale, governance, or both?
