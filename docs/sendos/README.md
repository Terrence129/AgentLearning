# `docs/sendos/` — the SendOS bridge

Everything needed to turn nine weeks of agent-engineering labs into **readable, contributable
SendOS expertise**. This folder is the bridge between the Python course in `agentlab/` and the
.NET platform the learner interns on (`D:\DevRepo\SendProjects\SendOS\SendOs`; on macOS/Linux, substitute your local SendOS checkout path).

> **Living documents — code wins over docs.** These pages were verified against the source on
> **2026-10-18**. The platform moves faster than its own documentation; when a claim here and the
> code disagree, **the code is right**, and fixing the page is a contribution, not housekeeping.

---

## Contents

| File | What it is | When you use it |
|---|---|---|
| [`CONCEPT-MAP.md`](./CONCEPT-MAP.md) | The evidence base: what SendOS actually implements, mapped to industry terms, with status labels, ranked learning topics and the six mechanisms worth rebuilding in miniature | **Reference.** Read §0 once, then §4 for each mechanism. This is the page you cite when someone asks "does SendOS really do X?" |
| [`BRIDGE.md`](./BRIDGE.md) | The week-by-week bridge: for each learning-plan week 1–9, which SendOS files to read, three questions, what maps cleanly vs differs, and a 30-minute timebox. Answers in a collapsed appendix | **Every week**, once, for 30 minutes. The "Transfer" gate of the plan |
| [`READING-ORDER.md`](./READING-ORDER.md) | A 10-step reading order (~1 day total) plus three first-contribution candidates with acceptance criteria | **Once**, in week 1–2; then again when you pick your first task |
| [`../../dotnet/`](../../dotnet/) | The C# bridge labs: `ProviderBridge` (week 1) and `StructuredDecisionBridge` (week 3), each with an offline self-test | **Week 1 and week 3**, as the language bridge to the C# codebase |

Primary inputs: [`../research/05-sendos-concept-map.md`](../research/05-sendos-concept-map.md) (the
source report) and [`../plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md) (weekly objectives).

---

## How to use it weekly

The plan gives you ~45 minutes for the SendOS bridge in a normal week; the pages below assume a
**30-minute** session (the remaining 15 minutes are your weekly note).

| Week | Plan topic | Bridge section | C# lab | Mechanism (CONCEPT-MAP §4) |
|---|---|---|---|---|
| 1 | The model, demystified | [Week 1](./BRIDGE.md#week-1--the-model-demystified--sendmodeladapter) | `dotnet/ProviderBridge` | §4.4 (schema-gated completion — the routing half is week 8) |
| 2 | Tools and the agent loop | [Week 2](./BRIDGE.md#week-2--tools-and-the-agent-loop--capabilitydefinition--registry) | — | §4.2 (capability catalogue) |
| 3 | Structured output, typed decisions | [Week 3](./BRIDGE.md#week-3--structured-output-prompts-as-assets--istructuredcompletionhandler) | `dotnet/StructuredDecisionBridge` | §4.1 (typed decision), §4.4 |
| 4 | Context engineering and memory | [Week 4](./BRIDGE.md#week-4--context-engineering-and-memory--sendcontextgateway) | — | — (least-context envelope) |
| 5 | MCP and interoperability | [Week 5](./BRIDGE.md#week-5--mcp-and-interoperability--connector-manifests) | — | §4.2 (declaration sources) |
| 6 | Planning, orchestration, approval | [Week 6](./BRIDGE.md#week-6--planning-orchestration-human-approval--the-decision-first-runtime) | — | §4.1, §4.5 |
| 7 | Evals and observability | [Week 7](./BRIDGE.md#week-7--evals-and-observability--outcome_trace--evaluator) | — | §4.3, §4.6 |
| 8 | Security, governance, cost | [Week 8](./BRIDGE.md#week-8--security-governance-cost-reliability--the-governance-sandwich) | — | §4.2 (authority), §4.4 (budgets) |
| 9 | Capstone: Mini-SendOS | [Week 9](./BRIDGE.md#week-9--capstone-mini-sendos--composing-the-runtime) | — | all six |

### The weekly loop (30 minutes)

1. **Before the session:** open `BRIDGE.md` at your week. Do not pre-read anything else.
2. **During:** 15 min read the listed files → 10 min write answers to the three questions → 5 min
   write the five bullets using the template in [Appendix C](./BRIDGE.md#appendix-c--weekly-bridge-log-template).
3. **After:** check the answers in [Appendix A](./BRIDGE.md#appendix-a--answers) and correct them.
   The corrections are the learning; a clean match means you already knew it.
4. **If the week is short:** do the 30 minutes and skip the stretch. Never skip the bridge — it is
   the compounding part of the plan (goal A).

---

## Using the concept map well

`CONCEPT-MAP.md` is long on purpose; do not read it cover to cover.

| You want | Read |
|---|---|
| To understand why these docs distrust SendOS's docs | [§0](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins) — five verified drifts |
| The one-page path a request takes | [§1](./CONCEPT-MAP.md#1-the-machine-in-one-page) |
| To look up "how does SendOS do X?" | [§2](./CONCEPT-MAP.md#2-concept-map--industry-term--sendos-implementation) — 30-row concept table |
| A ranked list of what to learn, with labs | [§3](./CONCEPT-MAP.md#3-ranked-learning-topics-20) |
| What to rebuild in miniature (and how) | [§4](./CONCEPT-MAP.md#4-where-a-from-scratch-build-teaches-the-most--six-mechanisms) |
| Where SendOS departs from mainstream practice | [§5](./CONCEPT-MAP.md#5-where-sendos-departs-from-mainstream-practice) |
| What the analysis could not verify | [§7](./CONCEPT-MAP.md#7-what-i-could-not-assess) — read this before quoting anything |

**Status vocabulary used throughout:** *Implemented* (real and reachable) · *Partial* · *Dark*
(built and tested, not on the live path) · *Missing*. The distinction between "exists" and
"reachable" is the single most useful thing to carry into conversations with the team.

---

## The one framing to remember

> **SendOS is ahead of mainstream tutorials on governance, behind on orchestration ergonomics.**

Ahead: approval binding, authority intersection, append-only trace, publish gates, version pinning.
Behind: no graph runtime (a 5,379-line procedural `DecisionRuntime`), durable execution built but
unwired, thin observability, a dry learning loop.

Use it in both directions: when a control feels over-engineered, ask *which incident paid for it*;
when the platform feels incomplete, ask *which framework already solved this*. Both are interview
answers, and both are how you choose a contribution.

---

## Maintenance rules

1. **Code wins.** Never update a claim from documentation alone — open the file and cite it.
2. **Every claim carries a path** (`file.cs:line`). A claim without a path is an impression.
3. **Verified date** goes in the header of any page you change materially.
4. **When you find drift:** fix the claim, record the file/line that changed it, and add it to the
   drift table in [`CONCEPT-MAP.md` §0](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins)
   or [`BRIDGE.md` Appendix B](./BRIDGE.md#appendix-b--path-index-and-doc-drift-warnings).
5. **Do not copy SendOS source into this repo.** Cite paths and quote at most a few lines; the
   learner's own code stays their own.

---

## Verified status (2026-10-18)

| Artifact | Verified how | Result |
|---|---|---|
| SendOS paths cited in `BRIDGE.md` / `READING-ORDER.md` | Every full path checked with `Test-Path` (macOS/Linux: `test -e`) against the source checkout; every `.../` shorthand resolved to an existing file/dir under its app or library subtree; every internal markdown link and anchor checked | ✅ 0 unresolved |
| `CONCEPT-MAP.md` body | Copied verbatim from `docs/research/05-sendos-concept-map.md` | ✅ byte-for-byte preserved after the wrapper header |
| `dotnet/AgentBridgeLabs.sln` | `dotnet build` on SDK 10.0.303 | ✅ 0 warnings, 0 errors |
| Both C# self-tests | `--selftest` run offline | ✅ 11/11 and 15/15 checks pass |
| Five doc drifts | Re-read the cited code | ✅ confirmed (see CONCEPT-MAP §0) |
