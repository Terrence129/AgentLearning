# 07 — Evals and Observability

> **Week 7 · just-in-time concept note.** Read before the lab (~25 min). The lab asks you to build a dataset, harness, judge and CI gate — this note explains why reliability, not best-case quality, is the thing you are measuring. **Reads with:** [research 03 §1–2](../research/03-production-evals-ops.md) · **Lab:** `week07-evals`.

## The failure mode this prevents

You changed one sentence in the system prompt. The demo still looks great, so it ships. Two weeks later a customer shows the agent stopped calling the policy-check tool on refunds — the "tone-only" change had silently reordered tool selection. Nobody can reconstruct the failing turn: the trace recorded `step 4: failed` and a token count. Diagnosis cost: a week; exposure: unauthorised refunds.

Evals make that change **fail in CI instead of production**; observability makes the **next** failure take ten minutes to diagnose.

## If you remember five things

> 1. **pass@k is capability; pass^k is reliability.** Production needs the second one.
> 2. **Deterministic checks before judges.** A judge is an instrument you calibrate, not an oracle.
> 3. **A prompt is a versioned artifact.** If you can't reconstruct a failed run's prompt, model, tools and state, you have logs, not observability.
> 4. **OTel's GenAI conventions are the right schema but still `Development`** — and the spec moved to a new repository in 2026. Wrap them, pin them, expect renames.
> 5. **A metric without a failure taxonomy is a number, not a diagnosis.**

## The model in one page

### Outcome evals vs trajectory evals

An **outcome eval** scores the final artifact (JSON, decision, DB state) — cheap, deterministic, necessary. A **trajectory eval** scores the path: tools called, order, arguments, policy. It is the only way to catch an agent that got the right answer for the wrong reason.

Score outcome first (objective); add trajectory assertions where the path *is* the product:

| Dimension | Assertion | Catches |
|---|---|---|
| Tool selection | expected/forbidden tool sets | capability creep, skipped policy checks |
| Tool arguments | schema + business rules + tenant-ID equality | cross-tenant access, malformed actions |
| Policy compliance | rule engine over the trace | "approved" without an approval |
| Efficiency | steps, tokens, latency, retries | silent cost regressions |

### pass@k vs pass^k, operationally

`pass@k` asks "did at least one of k samples work?" — a best-case capability number, and the one demos accidentally report. `pass^k` asks "did **all** k trials work?" — the reliability users experience. τ-bench introduced pass^k and found strong function-calling agents below 50% success with **pass^8 under 25%** in retail ([τ-bench](https://arxiv.org/abs/2406.12045), accessed 2026-10-18).

Run it like this:

1. Run **k independent trials per case** (fresh process/context, not a resumed run).
2. `case_pass = all(trials)`; `pass^k = passing_cases / total_cases`, reported per category — a global average hides the category that regressed.
3. Treat `p^k` (from single-trial success `p`) as a **planning estimate only**: trials correlate through shared prompts, caches and tools, so measure, don't infer. With `p = 0.90`, `p^5 ≈ 0.59`; with `p = 0.95`, `p^5 ≈ 0.77` — that is what "90% accurate" means to a customer.
4. Budget `k × cases × tokens`: `k = 3` for PR gates, `k = 5–8` nightly; use batch APIs and caching.
5. Report a confidence interval (Wilson or bootstrap over cases); with 25 cases it is wide, so gate on clear deltas and trends.

Track **variance** too: which cases are flaky, which always fail. A flaky case is a bug report about non-determinism.

### Deterministic checks before judges

Score in this order, stopping at the first applicable layer:

1. **State/artifact assertions** — final JSON schema, DB row, exit code, tool side effects.
2. **Rules over the trajectory** — policy compiled to predicates over trace events.
3. **Reference comparisons** — exact/normalized match, numeric tolerance.
4. **LLM judge** — only for qualities with no ground truth (helpfulness, tone, prose groundedness).

### Judge calibration, concretely

The MT-Bench work documents **position, verbosity and self-enhancement bias plus limited reasoning**, while strong judges reach >80% agreement with humans — roughly human-human ([LLM-as-a-Judge](https://arxiv.org/abs/2306.05685), accessed 2026-10-18). Your week-7 gate is **agreement ≥ 80%** against your own labels. How:

1. **Atomic criteria** (0–2 each), forced JSON — not one holistic 1–10 score.
2. **Label 30 items**, then re-label 10 blind a day later to measure your own consistency; keep the set fixed and versioned.
3. Report **exact agreement and Cohen's κ**, plus a confusion matrix per criterion. Fix the criterion with the worst confusion — usually the vaguest one.
4. **Control the biases:** swap order in pairwise judging and report flip rate; randomize length; don't let the generating model family judge its own output; strip decorative formatting.
5. **Pin the judge model version** in every report; re-calibrate on any judge, rubric or agent change.
6. **Cache the rubric prefix** — fixed-rubric judges can exceed 70% cache-hit rates ([OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18), making nightly judging affordable.

Below the bar, narrow the criterion or improve examples before trying a bigger judge.

### The regression gate

Baseline in git, gate in CI:

- **Quality:** fail if pass^k drops >2 points, or any category >5.
- **Cost/latency:** fail if cost per successful task rises >15% or p95 latency >20%.
- **Judge health:** fail if judge-human agreement falls below 80% — the judge drifted.
- **Taxonomy:** label every failing case `schema | tool_selection | tool_args | policy | retrieval | reasoning | timeout | budget` and report counts. This turns a red build into a fix.

Golden traces are your highest-ROI fixtures: sanitize, freeze and replay on every prompt/model change.

### Trace data model

Model each run as a trace of spans. OTel GenAI defines the vocabulary — `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool` via `gen_ai.operation.name` ([semconv agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18):

| Span | Must record |
|---|---|
| `invoke_agent` | agent id/version, prompt id/version/hash, conversation id, tenant, stop reason |
| `chat` | provider, requested **and actual** model, temperature, input/output/cache tokens, finish reason, latency |
| `execute_tool` | tool, redacted args + hash, result size/status, `error.type`, idempotency key |
| `policy.evaluate` | decision, rule ids, authority snapshot version |
| `approval.wait` | proposal id, binding hash, approver, expiry |
| platform | `app.tenant.id`, `app.cost.usd`, `app.budget.remaining`, step index |

**Honest status of the spec.** The conventions are **not stable**: every agent span and attribute is marked `Development`, and in 2026 they **moved** to the dedicated `open-telemetry/semantic-conventions-genai` repository, extending core conventions via Weaver ([repo](https://github.com/open-telemetry/semantic-conventions-genai), accessed 2026-10-18). Names will change. The response is not "wait" but: adopt the semantics, **pin the version**, emit through **one internal telemetry module**, and never let dashboards or eval code bind raw attribute strings. Content attributes (`gen_ai.input.messages`, `gen_ai.output.messages`) are deliberately opt-in and PII-flagged — hash or redact by default.

**What makes a failed turn diagnosable.** Record: (1) exact prompt version hash, (2) actual model+provider served, (3) stop reason/`error.type`, (4) tokens including cache reads/writes, (5) tool args and truncated results with error status, (6) policy decisions with rule ids, (7) step index and remaining budget, (8) correlation ids across run, conversation, tenant and approval. Miss any and the trace says "what" but not "why".

## Common misconceptions

| Misconception | Reality |
|---|---|
| "pass@k 0.9 means a 90% reliable agent." | A 90% single-trial rate; multi-step reliability is multiplicative — that is pass^k. |
| "A judge score is objective." | A measurement with documented biases; without human-labelled calibration it is an opinion with a number. |
| "More traces = observability." | Traces without prompt/model versions, policy decisions and correlation ids are logs. |
| "We'll add evals once it stabilises." | Evals are how you learn it is stable; retrofitting hides which release broke what. |

## How this shows up in SendOS

- **`Outcome_Trace` is the contract to copy.** A 21-event closed lifecycle in an insert-only store; a DB trigger denies `UPDATE`/`DELETE`, and events carry a monotonic `Sequence` (`apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs`, `.../Infrastructure/Persistence/EfCoreOutcomeTraceStore.cs`).
- **The evaluator exists but is dark.** The 5-dimension evaluator — Correctness, PolicyCompliance, OutcomeAlignment, EvidenceGrounding, ExecutionQuality — is built and tested but **never called** (`apps/Send.LowerLayer.Worker/src/.../Evaluation/Evaluator.cs`; [research 05 §2.4](../research/05-sendos-concept-map.md)). Your harness miniatures the missing wiring.
- **The evidence gate gives you starting thresholds.** `EligibleForCandidate ∧ sample ≥ 30 ∧ confidence ≥ 0.7 ∧ quality ≥ 0.5` (`.../Distillation/EvidenceGate.cs:24-35`) — reuse the numbers, interrogate the confidence definition.
- **`TurnStage` is the diagnosis primitive.** 45 named stages, each `Ran`/`Skipped`/`Failed` with a reason (`.../Application/Runtime/TurnStage.cs:29-203`). SendOS has stage semantics but stubbed metrics/traces ([research 05 §5](../research/05-sendos-concept-map.md)) — exactly the gap an OTel exporter maps onto.

## Check yourself

1. Your agent succeeds 85% per trial on a 4-trial task. What does pass^4 tell you, and why is `0.85^4` only an estimate?
2. Which eval cases must be deterministic, and which genuinely need a judge?
3. Your judge agrees with you 72% of the time. Fix the judge model, the rubric, or your labels — in what order, and why?
4. A failed run's trace shows the final error but no prompt hash. Which two questions can you no longer answer?
5. Why doesn't `Development` status justify waiting, and what must you build instead?

## Reading

- [τ-bench](https://arxiv.org/abs/2406.12045) — pass^k origin and what reliability failure looks like.
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) — the bias catalogue you calibrate against.
- [OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) — span/attribute vocabulary and its `Development` status.
- [Research 03 §1–2](../research/03-production-evals-ops.md) — the full eval and observability map.
- **Companion book:** *AI Agents in Depth* v2.0, ch.7 §7.2, §7.5, §7.7–7.8 — pass@k vs pass^k, judge methods, failure attribution in trajectories, statistical significance, and observability. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).
