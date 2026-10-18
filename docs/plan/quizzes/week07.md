# Week 7 Quiz — Evals and Observability

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** The difference between an outcome eval and a trajectory eval is:

- A) Outcome evals are always better
- B) Outcome scores only the final result; trajectory scores the path (tool choices, constraints respected)
- C) Trajectory evals require no dataset
- D) Outcome evals use judges, trajectory evals use exact match

**Q2.** `pass^k` measures:

- A) Success on the first attempt only
- B) The probability of succeeding on all k independent attempts — a reliability measure
- C) Average tokens per attempt
- D) Judge agreement across k samples

**Q3.** An LLM judge is credible only when:

- A) It uses the newest model
- B) It is calibrated against human labels, and both raw agreement and Cohen's kappa are reported
- C) It gives yes/no answers
- D) It runs at temperature 1.0

**Q4.** "Deterministic-first scoring" means:

- A) Use exact checks before any judge call
- B) Only use deterministic agents
- C) Fix the random seed and call the judge
- D) Remove all non-deterministic tests

**Q5.** Eval leakage is:

- A) Eval cases leaking to users
- B) Tuning on the eval set until it stops predicting real performance
- C) Traces containing PII
- D) A judge scoring too strictly

**Q6.** A regression gate in CI should fail when:

- A) Any single eval case fails
- B) A metric drops below the recorded baseline (or a pass^k floor)
- C) The model changes
- D) Cost increases by any amount

## Part B — Short answer (3 questions)

**Q7.** You have 25 agent traces and two hours. Describe how you build a 20-case golden set that will actually catch regressions, including what makes a case good.

**Q8.** Why is a trace schema a prerequisite for evals, not just for debugging?

**Q9.** A teammate says "the new prompt is better, it feels more helpful." Give the three-step answer you would require before accepting the change.

## Part C — Spot the bug (1 question)

**Q10.** This scoring function is supposed to be the eval harness. Identify **three** methodological defects.

```python
def score(outputs):
    good = 0
    for output in outputs:
        verdict = provider.complete(f"Is this answer good? {output.text}").content
        if "yes" in verdict.lower():
            good += 1
    return good / len(outputs)
```

---

## Answers and explanations

**Q1 — B.** Trajectory evals matter when process compliance is the requirement (approvals, no write without gate). They are more expensive to build and score.

**Q2 — B.** pass@1 flatters unreliable agents: an agent that succeeds 70% of the time has a pass^5 far below 70%. Reliability is what production needs.

**Q3 — B.** An uncalibrated judge measures its own bias. Agreement against 20–30 human labels is the evidence — and report Cohen's kappa alongside it, because 90% raw agreement on a 90/10 label set can be κ≈0. Without calibration a judge is a random number generator with good prose.

**Q4 — A.** Exact checks (schema valid, substring present, exit code, constraint count) are cheaper, faster and more reliable; judges are reserved for what cannot be checked mechanically.

**Q5 — B.** Repeated tuning against the same cases overfits: metrics rise while real quality stalls. Countermeasure: hold out cases, refresh periodically, and weight rare failures.

**Q6 — B.** Baselines (and floors such as pass^k) define acceptable regression. Failing on any single case is too brittle; failing on a metric drop is the control.

**Q7 — model answer.** Sample 25 traces, cluster failures by taxonomy, and pick cases to cover: happy paths (5), each failure category (8–10), safety/policy constraints (3–4), and edge/adversarial inputs (2–3). Each case needs a stable input, a deterministic check where possible, a rubric with 2–4 graded criteria, and a known baseline result. Good cases are *discriminating* (a bad agent fails them), *stable* (no flaky tool/network), and *explainable* (you can say why it failed).

**Q8 — model answer.** Evals consume traces: to score a trajectory you need structured events (steps, tool calls, results, stop reason) with stable ids and timings. If tracing is ad hoc logs, you cannot join a score to the steps that caused it, cannot compute pass^k reliably, and cannot reproduce the failure. The trace schema is also the contract SendOS uses between runtime and learning.

**Q9 — model answer.** (1) Show a baseline: run the existing eval suite on old and new prompt; no number, no change. (2) Check the shape: which cases moved, by how much, and is the change within judge noise (repeat runs / pass^k)? (3) Check for leakage and cost — did cases get tuned on, and did tokens/latency change? Only then accept, with the report attached.

**Q10 — model answer.** (1) No rubric and no forced structured output: a substring "yes" match on free text is not a judgement. (2) The judge is the same model as the generator (self-preference bias) and is never calibrated against human labels. (3) Single run per case, no baseline, no deterministic checks first, no failure taxonomy — the number produced is not comparable across time. Also: no cost estimate and no held-out set.
