# Week 6 Quiz — Planning, Orchestration and Approval

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** When does an orchestrator-worker topology earn its cost?

- A) Whenever a task has more than one step
- B) When subtasks are genuinely parallelisable or need isolated contexts, and synthesis is the hard part
- C) When you want to use more agents than your competitor
- D) Always — more agents means better results

**Q2.** The topology rule in the plan says:

- A) Always start with a multi-squad and simplify later
- B) Pick the smallest sufficient shape; if no shape is backed by the task's topology, report a limitation rather than guessing smaller
- C) Let the model choose freely between shapes
- D) Use whichever shape the previous run used

**Q3.** An `ApprovalBinding` must include:

- A) Only the approval id and timestamp
- B) Actor, tenant, action hash, authority snapshot and expiry
- C) The model name and temperature
- D) The full conversation transcript

**Q4.** The action hash exists to prevent:

- A) Slow approvals
- B) Post-approval edits — the executed action must be exactly the approved one
- C) Duplicate tool names
- D) Token overflow

**Q5.** "At-most-once execution" of an approved action is typically guaranteed with:

- A) A retry loop
- B) A compare-and-swap state transition plus an idempotency record
- C) A larger model
- D) Asking the human twice

**Q6.** A handoff between agents should pass:

- A) The full transcript, for completeness
- B) A `HandoffArtifact`: specialist, summary, findings, confidence, and artifact references — not the sender's transcript
- C) Only a one-line summary
- D) The raw tool outputs

## Part B — Short answer (3 questions)

**Q7.** Why must the proposal be persisted **before** approval, not after? Name the two failure classes this prevents.

**Q8.** Authority can change between approval and execution. Explain the scenario that makes an authority snapshot necessary and what goes wrong without it.

**Q9.** Define "smallest sufficient shape" and apply it to: "summarise this one document". Justify the shape you pick.

## Part C — Spot the bug (1 question)

**Q10.** This approval executor is the entire governance of the action path. Identify **three** security defects.

```python
def execute(approval_id: str, action: dict):
    approval = store.get(approval_id)
    if approval.status == "approved":
        return tools.call(action["tool"], action["args"])
    raise NotApproved()
```

---

## Answers and explanations

**Q1 — B.** Multi-agent pays when work is parallel or context isolation is essential and synthesis dominates. Otherwise it multiplies cost, latency and failure surface.

**Q2 — B.** Topology-driven selection with an explicit "no backed shape" limitation. Guessing a smaller shape silently under-powers the task; guessing bigger over-spends and adds control risk.

**Q3 — B.** Binding is what makes an approval specific and non-replayable. Approval id alone is an opaque handle anyone can reuse.

**Q4 — B.** The hash is recomputed at execution and compared to the approved hash; any edit between approval and execution fails the check.

**Q5 — B.** CAS on state (proposed → approved → executing → executed) plus an idempotency key prevents double execution under retries/concurrency.

**Q6 — B.** `HandoffArtifact(specialist, summary, findings, confidence, artifacts)` (rendered by `as_text()`) is the contract: bounded, attributable, and enough for the orchestrator to synthesise without seeing the sender's context. Full transcripts leak context and cost; one-liners lose the findings.

**Q7 — model answer.** Persist first so the approved object is durable and auditable: (1) crash/restart between approval and execution would otherwise lose the approval (or force a re-approval), and (2) an attacker or bug could alter the proposal after approval if the canonical record is created later. The persisted proposal is the thing the hash binds.

**Q8 — model answer.** A manager approves a refund; before execution the approver's role is revoked or the tenant's entitlement changes. Without a snapshot, execution re-reads current authority and may (a) execute with no valid approver, or (b) silently widen/deny based on unrelated later changes. With a snapshot, the execution decision is made against exactly the authority that justified the approval, and discrepancy is surfaced rather than silently resolved.

**Q9 — model answer.** The least complex execution shape whose topology the task actually supports. "Summarise this one document" is a single capability/reasoning node → direct call or one specialist; no squad, no multi-squad, no planner. Adding a squad adds cost, latency and failure modes without adding capability.

**Q10 — model answer.** (1) It never checks the action against the approved proposal: `action` is caller-supplied, so an approved "read" can be swapped for a "refund" — no action hash comparison. (2) No expiry check and no authority check at execution; approvals can be used forever and by anyone. (3) No at-most-once/idempotency: replaying the call executes the side effect again. Also no audit append and no tenant scoping.
