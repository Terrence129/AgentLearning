# Checkpoints — the weekly gate

**Purpose:** remove the "did I actually learn it?" ambiguity. Each week has three gates; you may not start week N+1 until all three pass. The gates are cheap to run (about 15 minutes) and they are the difference between a portfolio and a pile of notebooks.

**Run the gate every Saturday**, and paste the evidence into [`PROGRESS.md`](PROGRESS.md) and `notes/weekNN-review.md`.

---

## 1. The three gates (every week)

| Gate | Command / evidence | Pass criterion | Where it maps |
|---|---|---|---|
| **G. Green** | `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux), equivalently `pytest tests/weekNN -m week -q` | All week tests pass, no skips, no xfail; suite runs offline (< 10 s) | Lab deliverable |
| **E. Explain** | `docs/plan/quizzes/weekNN.md` closed book + 150-word teach-back, no notes | Quiz ≥ 8/10 **and** teach-back mentions the mechanism + one failure mode it prevents | Concepts list in Learning Plan |
| **T. Transfer** | SendOS bridge note in the weekly review (what matches / what differs / what you would change) | Three specific answers naming real C# types/files, with one open question you cannot answer yet | Day-job goal (A) |

A week is **done** only when G + E + T all pass. Stretch goals, extra reading and a prettier demo do not substitute for a missing gate.

> **Week 0** has a single gate: `doctor` clean, foundation tests green, one live call recorded with tokens/latency/cost.
> **Week 10** has G = re-derivation exercises complete, E = all 10 quizzes ≥ 8/10, T = final improvement proposal drafted.

---

## 2. Per-week gate table

| Wk | Green (tests) | Explain (quiz + teach-back) | Transfer (SendOS) | Artifact | Hours |
|---|---|---|---|---|---|
| 0 | `.\tasks.ps1 test` (Windows) / `./tasks.sh test` (macOS/Linux), foundation only | Baseline: what is a token / streaming / a retry failure | — | `notes/week00-baseline.md` with one priced call | 3 |
| 1 | `tests/week01` | Quiz 1 ≥ 8; explain retries + SSE + provider seam | `Send.Model.Adapter` — 3 shared duties, 2 missing | `agentlab chat` streams + prints tokens/cost | 8–10 |
| 2 | `tests/week02` | Quiz 2 ≥ 8; explain loop termination + budget placement | `CapabilityDefinition`, registry, `DirectCapabilityHandler` | 5 golden tasks + full trace | 10–12 |
| 3 | `tests/week03` | Quiz 3 ≥ 8; explain schema failure + repair economics | `IStructuredCompletionHandler`, `JsonSchemaValidator`, decision family | `analyze() -> Decision` + failure-rate report | 8–10 |
| 4 | `tests/week04` | Quiz 4 ≥ 8; explain compaction + retention evidence | `Send.Context.Gateway`, `SpecialistContext` | 20-turn task under 12k budget, retention ≥ 90% | 10–12 |
| 5 | `tests/week05` | Quiz 5 ≥ 8; explain MCP roles + trust model | Connector manifests vs MCP discovery | server + client + security checklist pass | 8–10 |
| 6 | `tests/week06` | Quiz 6 ≥ 8; explain approval binding + topology rule | `TopologyClassifier`, `ApprovalCheckpoint`, `ExecutionPlan` | mini-Squad + approval test proving edit/replay/expiry rejection | 10–12 |
| 7 | `tests/week07` | Quiz 7 ≥ 8; explain pass^k + judge calibration | `Outcome_Trace`, 5-dim `Evaluator`, publish gate | ≥ 25-case eval suite + baseline + 3 regressions + agreement ≥ 80% | 8–10 |
| 8 | `tests/week08` | Quiz 8 ≥ 8; explain lethal trifecta + authority intersection | governance sandwich, `EffectiveAuthority` | attack suite (≥ 10) + threat model `SECURITY.md` | 8–10 |
| 9 | `tests/week09` (optional) | Quiz 9 ≥ 8; trace one request end-to-end aloud | one-page improvement proposal grounded in the build | Mini-SendOS demo + eval report + write-up | 12–16 |
| 10 | Re-derivation: loop, MCP handshake, eval design, approval state machine from a blank file | Quizzes 1–10 revisited, all ≥ 8; teach-back without notes | Proposal reviewed by a senior engineer (feedback recorded) | Portfolio post + 2 deep dives + interview rehearsal | 4–6 |

---

## 3. Rubric — what "pass" means at each level

### G. Green

| Level | Descriptor |
|---|---|
| **Fail** | Any week test fails, errors, or is skipped/xfail to make the suite green. |
| **Pass** | `pytest tests/weekNN -m week -q` is green, runs offline in < 10 s, and you can point to the test that would fail if you deleted your implementation. |
| **Strong** | Pass, plus: one extra test of your own for a failure mode the brief did not cover, and no changes outside the owned module. |

### E. Explain

| Level | Descriptor |
|---|---|
| **Fail** | Quiz < 8/10, or the teach-back is a list of terms without a mechanism, or you needed notes. |
| **Pass** | Quiz ≥ 8/10; 150-word teach-back states the mechanism, one failure mode it prevents, and where it lives in the codebase. |
| **Strong** | Pass, plus: you can answer "what would break if we removed it?" and compare it to the alternative you rejected (from the week's concepts). |

### T. Transfer

| Level | Descriptor |
|---|---|
| **Fail** | Generic comparison ("SendOS has a similar layer"), no file/type names, or the section is empty. |
| **Pass** | Names the matching C# types/files, states two concrete differences (what SendOS adds or omits), and one thing you would change. |
| **Strong** | Pass, plus: one open question you could ask a SendOS engineer, and a hypothesis about why SendOS made its choice (regulation, multi-tenancy, scale). |

### Artifact quality (informs the portfolio, not a separate gate)

| Level | Descriptor |
|---|---|
| **Fail** | Only works with a live key, no trace, numbers not recorded. |
| **Pass** | Runs offline against mocks where the brief asks; emits trace events; records cost/latency; one command reproduces it. |
| **Strong** | Pass, plus: a small table of measurements (tokens, cost, latency, pass rate) committed in the repo. |

---

## 4. What to do when a gate fails

Diagnose **which** gate failed — the remedies are different. Do not "study more" as a reflex.

| Symptom | Likely cause | Action (in order) |
|---|---|---|
| Tests red at the end of the week | Misread the tests; implementation fought the contract | Re-read the failing test names and docstrings; write down the contract in one sentence; ask the tutor for a hint with the exact error. Cut stretch. |
| Tests green but quiz < 8/10 | Retrieval gap, not comprehension gap | Re-read only the missed concepts; make one flashcard per miss; retake the quiz the next day (not immediately). |
| Quiz fine but teach-back rambles | You recognize the terms but do not own the mechanism | Blank-page recall: draw the mechanism, then diff against the code. Re-do the teach-back tomorrow. |
| Transfer section thin | You have not read the C# side | 45-minute SendOS bridge session: open the mapped types, answer the three questions with file names. Ask a senior engineer one question. |
| Artifact works only live | Missing mock seam or trace | Add mock-based test path; emit events; record cost. This is usually a 90-minute fix, not a redesign. |
| Overrun by > 50% | Scope creep (usually stretch or perfectionism) | Cut stretch and polish; ship the gate at 80%. Record the debt in the review. |
| Two weeks in a row fail E | Method problem | Stop advancing; run one consolidation week (re-do quizzes, re-derive week N−1) before resuming. |

### Escalation rules

1. **One week grace:** you may start the next week with **one** gate outstanding if you log it in PROGRESS.md as debt and clear it within 7 days. Never two gates, never two weeks.
2. **Hard stop:** if the same gate fails twice (e.g. week 4 tests red on two consecutive Saturdays), do not start week 5. Spend the Saturday on the minimal failing test and the concept note, then ask the tutor for a review of your design.
3. **Ask for review, not answers:** "Here is my design for X; review it against these three failure modes." This keeps the productive struggle and gets you unstuck.

---

## 5. Gate evidence block (copy into PROGRESS.md)

```
Week NN — <theme>
[G] command: ______________________ result: ______ passed, ______ failed, time ____ s
[E] quiz: __/10   teach-back written: yes/no   words: ____
[T] SendOS files read: ______________________   differences stated: ____
[A] artifact command: ______________________   cost/latency recorded: $____ / ____ ms
Hours: ____   Sessions: ______________________   Debt carried: ______________________
```

---

## 6. The honest-failure clause

If you cannot pass a gate by the end of the week, the correct output is **a documented failure**, not a fake pass: what you tried, where it broke, what you now believe the cause is, and the next experiment. A documented failure is evidence of engineering maturity and is explicitly acceptable in the weekly review. A skipped gate recorded as "done" is the one thing that breaks the curriculum — because week N+1 silently assumes week N.
