# ADR NNN — <short decision title>

> Architecture Decision Record. Use this when a choice is expensive to reverse, spans more than one week's module, or encodes a safety/evals trade-off. One page maximum. Copy to `notes/adr-NNN-<slug>.md`.
> Examples worth an ADR: "where the budget check lives", "approval binding fields", "compaction policy", "judge calibration threshold", "MCP transport choice", "why the loop owns tool execution".

## Status

`proposed` | `accepted` | `superseded by ADR-NNN` | `rejected`

- **Date:** YYYY-MM-DD
- **Week:** NN
- **Deciders:** (you, plus anyone whose review matters)
- **Related:** lab brief, tests, research section

## Context

What forces are at play? Include only facts a reviewer needs:

- The problem or failure mode this decision addresses: ______
- Constraints: time budget, provider limits, SendOS parity, security policy: ______
- What happens if we do nothing (the status quo cost): ______

## Decision

> We will **<do X>**, because **<reason>**.

- Concrete mechanics (where it lives in the code, what the interface is): ______
- What is explicitly **out of scope**: ______

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| A. <chosen> | | | — |
| B. | | | |
| C. | | | |

## Consequences

**Positive:** ______

**Negative / accepted costs:** ______

**Risks and mitigations:**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| | | | |

**How we will know it was wrong:** (a metric, a test, or a review trigger) ______

## Evidence

- Tests that encode this decision: `tests/weekNN/test_...`
- Measurements (cost, latency, pass rate, calibration): ______
- Source that informed it (link + section): ______

## SendOS mapping (if relevant)

| This decision | SendOS equivalent | Same / different | Why |
|---|---|---|---|
| | | | |

## Revisit trigger

Revisit when: ______ (e.g. provider adds native support; eval shows pass^k < 0.7; SendOS ships a different binding).
