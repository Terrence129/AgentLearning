# Portfolio Post — <title>

> For `projects/portfolio/` or a public blog. Target 800–1,400 words. Write it in week 9–10, after the capstone, from the weekly reviews and ADRs — not from memory.
> The post must be readable by a senior engineer who does not know this repo, and must contain **evidence**, not adjectives.

## Working title options

1. ______
2. ______

**Chosen title:** ______ · **Date:** YYYY-MM-DD · **Links:** repo / demo video / live UI

## 1. The hook (2–3 sentences)

What broke, or what did you build that was hard, and why should a senior engineer care?

> ______

## 2. The problem, precisely

- The system/context: ______
- The failure mode this addresses (with numbers if you have them): ______
- Why the obvious/idiot solution does not work: ______

## 3. Approach (the architecture, in one diagram + 5 bullets)

```
<ASCII or linked diagram: ingress → decision → plan → approval → execution → audit>
```

1. ______
2. ______
3. ______
4. ______
5. ______

## 4. The three decisions that mattered

For each: the choice, the alternative, and the consequence. Link the ADRs.

| Decision | Alternative | Consequence | ADR |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

## 5. Evidence

> No numbers, no post. Use your eval report, trace data, and cost ledger.

| Claim | Evidence | Measurement method |
|---|---|---|
| e.g. "approval replay cannot execute twice" | test + trace | CAS test, 100 concurrent resumes |
| e.g. "pass^k improved from … to …" | eval report | 5 repeats × 25 cases |
| e.g. "cost per run is $0.0x" | trace/cost ledger | usage tokens × pricing |

Paste one small, real artifact: a trace excerpt, a rendered report table, or a test output.

## 6. What failed (this is the credibility section)

- Failure 1: ______
- What the trace showed: ______
- What I changed: ______
- What I would now do by default: ______

## 7. What I would do differently

Three bullets, honest, specific. Avoid "write more tests".

## 8. Limits of the claim

What this does **not** show: mock vs real providers, sample size, domain specificity, what was not evaluated.

## 9. Call to action

What should the reader do? (run the demo, try the pattern, review the ADR)

## 10. Appendix

- Repo link, demo command, test command
- Reading that informed it (2–3 links max)
- Related posts
