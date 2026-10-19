# Research reports

Five deep-research reports produced on **2026-10-18** as the evidence base for this curriculum. They are deliberately opinionated, citation-dense snapshots — not tutorials.

| # | Report | Words | What it answers |
|---|---|---|---|
| 01 | [Agent architecture: state of the art](01-agent-architecture-sota.md) | ~5,000 | How agent systems actually work in late 2026: harness duties, reasoning patterns, context engineering, memory, autonomy/HITL, durability, failure modes, and a build ladder. |
| 02 | [Frameworks, SDKs & protocols](02-frameworks-protocols.md) | ~4,500 | MCP 2026-07-28, A2A v1.0, AG-UI 1.0, 19-framework comparison, provider capabilities, and what a .NET engineer should learn first. |
| 03 | [Production, evals, security & ops](03-production-evals-ops.md) | ~4,400 | Eval strategy (pass^k, judges), observability/OTel, the security threat model, reliability, cost levers, governance, a 38-item checklist. |
| 04 | [Learning resources](04-learning-resources.md) | ~3,800 | Verified courses, essays, papers, codebases, books, communities, Chinese-language resources, a 50-hour essential subset. |
| 05 | [SendOS concept map](05-sendos-concept-map.md) | ~3,900 | What the SendOS platform actually implements (grounded in file:line), 20 ranked learning topics, six mechanisms worth rebuilding, and 11 departures from mainstream practice. |

---

## How to use these reports

- **Do not read them cover to cover.** Each week's concept note links the relevant section.
- **Treat them as snapshots.** Frameworks, spec versions and pricing change monthly. Every report records its access date; when you act on a claim &ge; 3 months old, re-verify the primary source.
- **Check the uncertainty registers.** Reports 01 §10, 02 §6, 03 §10 and 04 §J explicitly separate verified facts from estimates and vendor claims. Read those before quoting numbers in an interview.
- **Citations are the point.** Every non-obvious claim links its source. If a link is dead, the claim is a lead, not a fact.

## Refresh policy

When you finish a week and find a claim is stale:

1. Update the concept note (or this repo's lab) with the current fact.
2. Append a dated line to the report's uncertainty register — do not silently rewrite history.
3. If the change invalidates a lab, open an issue against that lab rather than patching the research.

Reports are valuable because they are **dated**, not because they are eternal.

## Provenance

Produced by parallel research agents with primary-source verification (spec sites, vendor docs, arXiv, official blogs, and the SendOS repository at `D:\DevRepo\SendProjects\SendOS\SendOs`; on macOS/Linux, substitute your local SendOS checkout path). SendOS analysis was read-only; the platform was not built or executed.
