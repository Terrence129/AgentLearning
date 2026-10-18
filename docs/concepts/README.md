# Concept Notes

Nine just-in-time notes, one per mechanism you build. They are **not reference material to read later** — each one is 25 minutes before its lab, and it exists to explain *why* the failing tests are shaped the way they are. Every note answers the same question first: **what failure does this mechanism prevent?**

Read the note, answer its five questions in your own words, then open the lab. After the lab's tests are green, re-answer the five questions — if you still miss one, you have found the gap the lab did not close.

## The contract for every note

| Section | What it gives you |
|---|---|
| **The failure mode this prevents** | A concrete incident story — the bug this week's mechanism is designed to make impossible |
| **If you remember five things** | The minimum viable mental model; read this first if you are short on time |
| **The model in one page** | Mechanism, numbers with sources, and the one code sketch worth internalising |
| **Common misconceptions** | Belief → reality → consequence; the fastest way to find what you have wrong |
| **How this shows up in SendOS** | 2–4 real mechanisms from the platform you work on, so the transfer is explicit |
| **Check yourself** | Five questions, no answers. If you cannot answer one, re-read that section before the lab |
| **Reading** | 2–4 primary sources, ranked; the full map is in [research 04](../research/04-learning-resources.md) |

## Index

| # | Note | Weeks | Read before | Lab | Grounded in |
|---|---|---|---|---|---|
| 01 | [The agent loop](01-agent-loop.md) | 1–2 | Week 1, day 1 | [`week01-provider`](../../labs/week01-provider/README.md), [`week02-agent-loop`](../../labs/week02-agent-loop/README.md) | [research 01 §1–2](../research/01-agent-architecture-sota.md) |
| 02 | [Tool design](02-tool-design.md) | 2 | Week 2, before the loop build | [`week02-agent-loop`](../../labs/week02-agent-loop/README.md) | [research 01 §1.4](../research/01-agent-architecture-sota.md), [research 02 §2](../research/02-frameworks-protocols.md) |
| 03 | [Context engineering](03-context-engineering.md) | 3–4 | Week 3 (prompts as assets), re-read week 4 | [`week03-structured-output`](../../labs/week03-structured-output/README.md), [`week04-context-memory`](../../labs/week04-context-memory/README.md) | [research 01 §3](../research/01-agent-architecture-sota.md) |
| 04 | [Memory](04-memory.md) | 4 | Week 4, after note 03 | [`week04-context-memory`](../../labs/week04-context-memory/README.md) | [research 01 §4](../research/01-agent-architecture-sota.md) |
| 05 | [MCP and interoperability](05-mcp-interop.md) | 5 | Week 5, with the current spec open | [`week05-mcp`](../../labs/week05-mcp/README.md) | [research 02 §1](../research/02-frameworks-protocols.md), [research 01 §10](../research/01-agent-architecture-sota.md) |
| 06 | [Orchestration and approval](06-orchestration.md) | 6 | Week 6 | [`week06-squads`](../../labs/week06-squads/README.md) | [research 01 §2, §6](../research/01-agent-architecture-sota.md), [research 05 §4.5](../research/05-sendos-concept-map.md) |
| 07 | [Evals and observability](07-evals-observability.md) | 7 | Week 7 | [`week07-evals`](../../labs/week07-evals/README.md) | [research 03 §1–2](../research/03-production-evals-ops.md) |
| 08 | [Security and governance](08-security-governance.md) | 8 | Week 8 | [`week08-security`](../../labs/week08-security/README.md) | [research 03 §3–7](../research/03-production-evals-ops.md) |
| 09 | [Production: durability, cost, checks](09-production.md) | 9+ | Week 9 | [`week09-capstone`](../../labs/week09-capstone/README.md) | [research 03 §4–8](../research/03-production-evals-ops.md) |

## Dependencies between notes

> Lab links above point at each week's brief; those files land with the lab scaffolds, so a link may 404 for a few days while a week is being built. The note and the weekly brief in [`docs/plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md) stay authoritative in the meantime.

The notes are numbered in build order, but three dependencies are worth respecting:

- **01 before 02.** Tool design only makes sense once you know that the loop appends observations and checks budgets; a tool is the action surface of a loop you have already built.
- **03 before 04.** Context engineering keeps one run coherent; memory is what survives between runs. Building memory first produces a vector database with no write policy and no eval.
- **02 before 05.** MCP is a transport and discovery layer on top of the tool contract you designed in week 2; if tool descriptions and schemas are vague locally, they are vague over the wire too.

Notes 06–09 assume the earlier mechanisms exist. They are still readable standalone, but the SendOS references land harder after the labs.

## How to use them with the rest of the repo

- **Before the week:** read the week's note (25 min), write three goals for the week, and skim the week's lab brief.
- **During the week:** keep the note open next to the failing tests. The "Common misconceptions" table is the fastest debugging heuristic when a test fails for a conceptual reason.
- **Saturday:** answer the five questions from memory, then write the weekly teach-back. The [glossary](../glossary.md) and weekly flashcards are the spaced-repetition layer; this folder is the just-in-time layer.
- **When you are stuck:** the relevant section of a note plus the lab's hints should unblock you; if not, ask the tutor with the test name and what you tried.

The full nine-week schedule lives in [`docs/plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md); the lab index is [`labs/README.md`](../../labs/README.md); the research reports these notes compress are in [`docs/research/`](../research/01-agent-architecture-sota.md).

## Scope and honesty

These notes deliberately compress. Where a claim is contested, unverified, or based on 2025-era models, the research report says so in its §10 — and you should treat it as a live question rather than settled fact. The most important habit to build from this folder: **every number has a source, and every mechanism has a failure mode it exists to prevent.**
