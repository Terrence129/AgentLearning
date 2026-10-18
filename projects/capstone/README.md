# Capstone — Mini-SendOS

The capstone is not a ninth lab with a new mechanism. It is the composition of weeks 1–8 into one governed system, plus the evidence that it behaves: a demo that runs offline, an audit trail you can read, an acceptance checklist you can sign, and a write-up you can show a hiring manager.

**Build spec:** [`labs/week09-capstone/README.md`](../../labs/week09-capstone/README.md) — read it first; it is the authoritative week-9 brief.
**Plan context:** [`docs/plan/LEARNING-PLAN.md`](../../docs/plan/LEARNING-PLAN.md) week 9.
**Time:** 12–16 h. **Prerequisites:** weeks 1–8 green.

## What you are building

```
goal (tenant + actor)
  -> typed decision            agentlab/capstone/decisions.py   (week 3 skills)
  -> capability check          agentlab/capstone/catalogue.py   (week 8 governance)
  -> persisted proposal        agentlab/capstone/platform.py    (week 6 approval)
  -> bound human approval      agentlab/capstone/platform.py
  -> at-most-once execution    agentlab/capstone/platform.py    (week 8 idempotency)
  -> append-only audit rows    agentlab/capstone/platform.py    (week 7 trace substrate)
  -> typed UI surface          agentlab/web/app.py              (optional extra)
```

## Starter layout

| Path | State | You do |
|---|---|---|
| `agentlab/capstone/decisions.py` | contracts + stubs | implement parse/serialise/budgets |
| `agentlab/capstone/catalogue.py` | contracts + stubs | implement merge/resolve/tenant rules |
| `agentlab/capstone/platform.py` | dataclasses + wiring + stubs | implement the five lifecycle methods + digest |
| `agentlab/web/app.py` | complete, guarded FastAPI | wire `create_app(platform)` into your platform |
| `tests/week09/` | 46 tests, red on purpose | make them green without editing them |
| `solutions/week09/` | reference implementation | open only after your tests pass |
| `scripts/demo_capstone.py` | complete | use as a prerequisite check; it exits 0 when done |
| `projects/capstone/ACCEPTANCE.md` | checklist | fill it with evidence |
| `projects/portfolio/WRITEUP.md` | template | write the design story |

## Build order (do not reorder)

1. `python scripts\demo_capstone.py` — read the "DEMO BLOCKED" list; it names the first gap.
2. `decisions.py` -> `pytest tests/week09 -m week -q` (decision tests go green).
3. `catalogue.py` -> catalogue tests go green.
4. `platform.py` -> the demo completes end-to-end.
5. `web/app.py` wiring -> optional demo UI.
6. Acceptance checklist -> portfolio write-up -> 5-minute demo (recorded).

## Deliverables

- [ ] `tests/week09` fully green, including at least three invariants you added yourself (replay, edit-after-approval, cross-tenant).
- [ ] `scripts/demo_capstone.py` exits `0` offline and prints the full audit sequence.
- [ ] `projects/capstone/ACCEPTANCE.md` filled in with command output and evidence.
- [ ] `projects/portfolio/WRITEUP.md` (800–1,500 words) + a 5-minute recorded demo per `DEMO-CHECKLIST.md`.
- [ ] One-page design proposal for a real SendOS improvement, grounded in the capstone (recommended: durable suspend/resume for approvals, or trace -> candidate evidence gating).

## Definition of done

You can draw the request path from ingress to audit row without notes; every arrow has a failure mode and a control; and a senior engineer can follow one request through the demo without asking a question.
