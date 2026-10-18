# StructuredDecisionBridge — typed decisions, validation, repair

**Week 3 bridge lab.** The Python week-3 lab builds `agentlab/schemas/`: structured output,
one repair retry, versioned prompts, and a typed `Decision` family with presentation budgets.
This app rebuilds it in C# — and adds the layer that makes a typed contract honest: a
**three-stage gate** (schema → binding → budget) that never returns a partial decision.

Timebox: **30 minutes**. Run `--selftest` first, then `--mock`, then read
`../Bridge.Shared/Decisions/` in this order: `DecisionInteraction.cs` → `DecisionSchema.cs` →
`DecisionValidator.cs` → `DecisionParser.cs`.

---

## Run

```powershell
# 1. offline mechanism checks (no key, no network) — THE GATE
dotnet run --project dotnet/StructuredDecisionBridge -- --selftest

# 2. offline repair demo: chart -> broken schema -> over budget -> valid
dotnet run --project dotnet/StructuredDecisionBridge -- --mock

# 3. live (needs BRIDGE_API_KEY; JSON mode requested, never trusted)
dotnet run --project dotnet/StructuredDecisionBridge -- --prompt "Why did revenue fall, and what should we do?"
```

| Flag | Effect |
|---|---|
| `--selftest` | Offline checks; exit 0 = all pass |
| `--mock` | The scripted four-stage failure sequence (no key, no network) |
| `--prompt <text>` | Business goal |
| `--max-repairs <n>` | Repairs after the first call, 0..5 (default 3) |

Exit codes: `0` accepted, `3` no validated decision, `1` self-test failure.

---

## The three-stage gate

```
raw model text
   │
   ├─ 1. JsonSchemaLite.Validate(json, DecisionSchema.Json)   → shape, required, oneOf, enum/const
   │       fails ⇒ ParseStage.Schema
   │
   ├─ 2. JsonSerializer.Deserialize<DecisionInteraction>      → discriminator → sealed subtype
   │       fails ⇒ ParseStage.Binding
   │
   └─ 3. DecisionValidator.Validate(boundDecision, budget)    → word/sentence counts, question count,
           fails ⇒ ParseStage.Budget                              options 1..3, confidence 0..1, required refs
```

**Why three stages and not one:** each catches a different failure class, and the repair message
differs per class. A model that emitted a chart needs to be told the response types; a model that
wrote a 15-word headline needs to be told the number 12. Collapsing them into "invalid JSON"
produces repair prompts that fix one problem and regress another.

**Why stop at the first failing stage:** the repair instruction then has one theme, and the
diagnostics stay readable. The self-test asserts this ordering explicitly (`ExcludedArtifact`
fails at schema, never reaching the budget check).

**Why the schema is shown to the model and still enforced in code:** provider JSON modes are a
request, not a guarantee. On hosts without constrained decoding, `jsonMode: true` is advice. The
lab's position: *trust nothing the model returns; validate everything you accept.*

---

## The scripted failure sequence (what `--mock` shows)

| Attempt | Scripted response | Stage rejected | What the repair teaches |
|---|---|---|---|
| 1 | `chartSpec` — an artifact the family cannot represent | Schema (`oneOf` matches 0 branches) | The response-type set is closed; charts are not decisions |
| 2 | `decisionState` missing `traceReference`/`evidenceSummary` | Schema | Required properties are part of the contract, not decoration |
| 3 | 15-word headline, 3-sentence meaning | Budget | Presentation budgets are numbers, and they are enforced |
| 4 | valid `decisionState` | — | Accepted; the loop returns the typed decision |

```
-- attempts
  #1: rejected at Schema (1 issue, 0 ms, raw 171 chars)
  #2: rejected at Schema (2 issues, 0 ms, raw 179 chars)
  #3: rejected at Budget (2 issues, 0 ms, raw 548 chars)
  #4: accepted (0 issues, 0 ms, raw 483 chars)
```

The console also prints **repair economics**: attempts used, characters re-sent, estimated cost.
Each repair re-sends the failing response plus the violation list, so the prompt grows — repair is
not free, which is why the loop is bounded at three.

---

## The typed family

Seven sealed subtypes sharing one envelope (`interactionId`, `headline`, `nextMoves`,
`traceReference`), discriminated on the wire by `responseType`:

`ClarificationPrompt | DirectAnswer | DecisionState | AnalysisConclusion |
DecisionRecommendation | ActionProposal | Limitation`

There is **no** subtype for a chart, dashboard, visualisation spec, report canvas or analytics
workspace. That absence is the structural guarantee: a chart request cannot be represented, so it
must be elevated into a decision — the same technique SendOS uses in
`DecisionInteraction.cs`. The self-test asserts the exclusion by reflecting over the assembly.

**Presentation budgets** (from `PresentationBudget`, mirroring SendOS):

| Field | Budget |
|---|---|
| `headline` | ≤ 12 words |
| `DecisionState.meaning` / `AnalysisConclusion.meaning` | ≤ 2 sentences |
| `consequence` | ≤ 1 sentence |
| `DecisionRecommendation.recommendation` | ≤ 1 sentence |
| `nextMoves` | ≤ 4 |
| `ClarificationPrompt.question` | exactly one question mark |
| `ClarificationPrompt.options` | 1–3 |
| `DecisionRecommendation.confidence` | 0..1 |

Sentence counting is deliberately simple (terminators `. ! ?`): a regex that "understands"
abbreviations is harder to explain than the rule it enforces.

---

## Self-test coverage (15 checks)

| Check | Mechanism |
|---|---|
| excluded artifact rejected at schema | closed response family + `oneOf` |
| missing required properties rejected | schema required |
| over-budget decision rejected at budget stage | stage ordering |
| valid decision state binds to subtype | System.Text.Json polymorphism |
| valid clarification + action proposal bind | options and action reference survive binding |
| serialise → parse round-trip | discriminator written and read back |
| headline boundary 12/13 | exact budget arithmetic |
| sentence counting boundaries | 0/1/2/3 sentences |
| clarification rules (2 questions, 0 or 4 options) | semantic rules schema cannot express |
| confidence range | numeric range validation |
| repair converges in 4 scripted attempts | stage sequence Schema→Schema→Budget→ok |
| never returns a partial decision | failure returns `Decision = null` |
| `maxRepairs = 0` = one attempt | bounded loop |
| repair instruction names every violation | repair prompt construction |
| family structurally excludes chart/dashboard | reflection over the assembly |

---

## SendOS bridge (30-minute session)

Read these with the week-3 questions in `docs/sendos/BRIDGE.md`:

1. `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/IStructuredCompletionHandler.cs`
   — the contract: schema in, validated output or `SchemaValid=false`.
2. `.../Structured/StructuredCompletionHandler.cs` and `JsonSchemaValidator.cs` — their validator
   supports `type`/`required`/`properties`/`items`; yours adds `oneOf`/`const`/`enum`. What does
   that difference cost in failure diagnosis?
3. `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs` —
   compare the envelope and the reserved-type exclusion. Note how much larger the real family is
   (richer evidence, execution results, readback verification).
4. `.../Application/Decision/{PresentationBudget,PresentationBudgetEnforcer}.cs` — the same
   numbers you implemented, enforced in production code.

**What maps cleanly:** schema-validated completion, validate-after rather than constrained
decoding, typed decision family, discriminated union on the wire, presentation budgets.
**What differs:** SendOS validates *inside* `Model.Adapter` and composes *inside* the runtime
(two services, two seams); the real family carries far more evidence and execution state; and
SendOS's `DecisionComposer` trims to budget rather than rejecting — a policy choice worth
comparing: **trim online vs reject and repair**.

---

## Exercises

1. **Measure the failure rate.** Run 20 live calls with `--max-repairs 0` and count schema vs
   budget failures. Which schema keyword catches most? Raise nesting depth in the schema and
   re-measure (the week-3 stretch).
2. **Add a subtype** (`EvidenceExplanation`) end-to-end: record type, `[JsonDerivedType]`, schema
   branch, validator rule, sample, self-test. Note how many places must change — this is the true
   cost of a closed family.
3. **Make the loop cheaper.** Instead of re-sending the whole failing response, send only the
   violations and the minimal prior context. Does repair still converge? What breaks?
4. **Compare trim vs reject.** Implement a `TrimToBudget` pass (cut headline to 12 words) and
   compare quality/cost against repair. When is trimming acceptable, and when does it silently
   change meaning?
5. **Persist the evidence.** Write every attempt (raw, stage, issues) to `attempts.jsonl` — the
   SendOS analogue is the append-only Outcome_Trace (week 7).
