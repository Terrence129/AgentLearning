# Projects

The labs teach individual mechanisms. The projects force you to compose them and defend the composition.

## 1. Capstone — Mini-SendOS (week 9)

Build a small but complete agent platform that mirrors the governance-first architecture of SendOS:

```
goal → typed decision → topology-selected execution → approval gate → authoritative execution → audit trail
                                                                        ↘ trace → evidence gate → human-approved asset promotion
```

Deliverables:

- Working demo: `scripts/demo_capstone.py` (offline, mock provider) and a web UI (real provider).
- Eval report: baseline, regressions, pass^k, cost and latency.
- Architecture write-up: decisions, trade-offs, threats, what you would do next.
- 5-minute recorded demo.

Acceptance criteria: [`capstone/ACCEPTANCE.md`](capstone/ACCEPTANCE.md). Write-up template: [`portfolio/WRITEUP.md`](portfolio/WRITEUP.md).

## 2. Portfolio artifacts (ongoing)

You are hiring-manager-visible from week 2 onward, not week 9. Each week produces one public artifact:

| Artifact | When | Why it matters |
|---|---|---|
| Lab report (`notes/weekNN-review.md`) | every week | Shows reasoning, not just code |
| "Approval binding is a security mechanism" deep-dive | week 6 | Demonstrates governance maturity |
| "Why pass^k beats pass@1" eval write-up | week 7 | Shows measurement discipline |
| Capstone architecture + demo | week 9 | The interview centrepiece |

Templates are in [`../templates/`](../templates/).

## 3. Stretch ideas

- [ ] Port the week-2 loop to **.NET** using `Microsoft.Extensions.AI` (`IChatClient`) and compare ergonomics.
- [ ] Reimplement the week-6 squad in **LangGraph** and **Microsoft Agent Framework**; write a 1-page comparison.
- [ ] Turn the week-9 catalogue into a real **MCP server** and connect it to Claude Desktop or another host.
- [ ] Add an **OTel exporter** to the trace module and view a run in a local collector.
- [ ] Implement **durable suspend/resume** for approvals with SQLite + CAS (SendOS's unwired `CaseRuntime`).
- [ ] Build an **eval-gated promotion** pipeline: candidate improves a prompt only if it beats baseline on the suite.

## Rules of thumb

- A project you cannot demo in 5 minutes is not finished.
- Every number you report (cost, accuracy, latency) needs its measurement method in the report.
- Write the "what I would do differently" section first; it is the most valuable part.
