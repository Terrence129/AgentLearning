# Week 9 Quiz — Capstone: Mini-SendOS

**Time:** 20 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** The capstone is described as a *composition* because:

- A) It is a ninth, unrelated project
- B) It reuses weeks 1–8 modules as vertical slices into one system
- C) It copies SendOS's C# code
- D) It is only a UI

**Q2.** The capability catalogue merges two sources with the rule:

- A) Last source wins
- B) Published definitions win over derived/discovered ones, with provenance recorded
- C) The model decides at runtime
- D) Merge is random to avoid bias

**Q3.** In the capstone, governance must be:

- A) Optional in demo mode
- B) The same fail-closed path in demo and live runs
- C) Enforced only for write tools
- D) Delegated to the model

**Q4.** The learning loop in the capstone ends with:

- A) Automatic prompt rewriting
- B) A human-approved asset promotion gated on evidence (submit-only)
- C) Fine-tuning the model
- D) Deleting failing traces

**Q5.** The offline demo script uses:

- A) A live provider with a $50 budget
- B) A mock provider, so the flow is deterministic and free
- C) A recorded video only
- D) No data

**Q6.** The acceptance gate says a senior engineer must be able to:

- A) Read the README
- B) Follow one request's trace from ingress to audit row without asking questions
- C) Run the tests
- D) Approve the design

## Part B — Short answer (3 questions)

**Q7.** List the six layers the capstone must compose and, for each, name the earlier week it comes from.

**Q8.** How do you demonstrate governance in a demo without live spend and without faking the control path?

**Q9.** Your final deliverable includes a one-page improvement proposal for real SendOS. What makes such a proposal credible rather than a wish list?

## Part C — Spot the bug (1 question)

**Q10.** This is the capstone request handler. Identify **three** defects that would make the governance claims false.

```python
def handle(request: Request):
    if os.getenv("DEMO_MODE") == "1":
        return execute_unchecked(request.action)
    decision = runtime.decide(request)
    return execute_governed(request, decision)
```

---

## Answers and explanations

**Q1 — B.** Each week's module is a layer; the capstone is the first system where all layers must agree on ids, state and evidence.

**Q2 — B.** Precedence plus provenance: the platform team's published capability definition outranks an inferred one, but the merge records where each definition came from. This is SendOS's published-wins rule in miniature.

**Q3 — B.** A demo-only bypass is how untested paths reach production, and an env-flag bypass is a backdoor. Mock the provider, not the policy.

**Q4 — B.** Trace → candidate → evidence gate → human publish. Automation proposes; a human promotes; the gate is evidence, not vibes.

**Q5 — B.** Deterministic, free, and reproducible in CI. Live calls are for the optional web UI demo only.

**Q6 — B.** The trace is the proof that the system is what you claim: model call, plan, approval, execution, audit row, all correlated.

**Q7 — model answer.** (1) Provider layer (week 1) + mock + budget routing (week 8). (2) Capability catalogue (week 2 registry + week 6 risk/appoval metadata). (3) Decision runtime (week 3 typed decisions + week 6 topology/shape selection). (4) Specialists/plan (week 6). (5) Governance: authority, approval binding, audit (weeks 6 and 8). (6) Learning loop: traces + eval harness + evidence gate + human publish (week 7). Surface (FastAPI + UI) is week 9 scaffolding.

**Q8 — model answer.** Point the provider seam at a scripted `MockProvider` that replays deterministic responses (including a malicious one), and run the *same* handler path used in live mode. Show: a write proposal blocked pending approval; an edited action rejected by the hash check; a replayed approval rejected by at-most-once; and the resulting audit rows. Because only the provider is mocked, the governance code exercised in the demo is the governance code that ships.

**Q9 — model answer.** It is grounded in a mechanism you rebuilt and measured: a specific gap (e.g. `CaseRuntime` suspend/resume unwired), the failure it causes today, your miniature's design, evidence from your eval run, the smallest change to SendOS that would close it, its risks and a test plan. Credibility comes from the evidence and the small diff, not from the ambition of the proposal.

**Q10 — model answer.** (1) The demo branch bypasses governance entirely (`execute_unchecked`) — the path you demo is not the path that is governed, and an env flag left set in production is a direct privilege bypass. (2) No authority/approval check is shown at all in the demo path, so the "every write is gated" claim is false under that flag. (3) No audit row is written on the demo path, so the demo cannot prove the control it claims. Fix: mock the provider only; single governed handler for both modes; flags may change data, never policy.
