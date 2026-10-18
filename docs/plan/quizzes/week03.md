# Week 3 Quiz — Structured Output and Prompts as Assets

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

## Part A — Multiple choice (6 questions)

**Q1.** What does JSON mode guarantee?

- A) The output validates against your JSON Schema
- B) The output is syntactically valid JSON
- C) The output contains no hallucinated fields
- D) The output is deterministic

**Q2.** Why use a discriminated union (e.g. a required `kind` field) for a decision family?

- A) It reduces token usage
- B) It lets the model emit different payload shapes while keeping one validatable contract
- C) It removes the need for a repair loop
- D) It makes the schema unconstrained

**Q3.** A validation-repair loop should be:

- A) Unbounded until valid output appears
- B) Bounded to a small number of attempts, with the validation error fed back
- C) Replaced by asking the user to fix the JSON
- D) Run only when `temperature > 0`

**Q4.** Which metric turns "structured output works" into an engineering claim?

- A) The number of prompt tokens
- B) The schema failure rate before and after repair
- C) The model's release date
- D) The number of fields in the schema

**Q5.** Prompt templates are immutable assets carrying `id` and `version`. The main reason is:

- A) To make the prompt longer
- B) To attribute behaviour changes and make prompt edits reviewable diffs
- C) To improve caching automatically
- D) To satisfy provider rate limits

**Q6.** A "presentation budget" (headline ≤ 12 words, ≤ 4 next moves) is best enforced:

- A) By politely asking the model in the prompt only
- B) Structurally, by schema constraints and/or a post-validation check
- C) By lowering `temperature`
- D) By using a smaller model

## Part B — Short answer (3 questions)

**Q7.** Why must invalid output **never** be surfaced as if it were valid? Give the failure mode it creates for a downstream decision system.

**Q8.** What is a cassette, and which specific property does it give your test suite that a `MockProvider` does not?

**Q9.** Sketch (in words or pseudocode) the `StructuredExtractor.extract(messages, Decision)` contract: schema enforcement, bounded repair, and what it returns once the repair attempts are exhausted. What happens on a provider error?

## Part C — Spot the bug (1 question)

**Q10.** This function is the whole "structured output" implementation. Identify **three** defects.

```python
def analyze(text: str) -> Decision:
    raw = provider.complete(messages=[{"role": "user", "content": text}]).content
    return Decision.model_validate_json(raw)
```

---

## Answers and explanations

**Q1 — B.** JSON mode guarantees parseable JSON, not schema compliance: fields can be missing, extra or wrong-typed. Only provider-enforced structured outputs (or your validation) give schema-level guarantees.

**Q2 — B.** A tag field lets one schema describe several shapes and still be validated precisely; it also maps cleanly to pydantic discriminated unions. It does not remove validation failures.

**Q3 — B.** Bounded repair (typically one retry) recovers most transient malformations without hiding the failure rate. Unbounded repair is a cost/latency bug.

**Q4 — B.** Failure rate is the observable that tells you whether schema, model or prompt is the problem, and whether repair earns its cost.

**Q5 — B.** Prompts are code: the `id`/`version` pair makes every prompt change an explicit, reviewable revision (editing history is forbidden — you bump the version instead), so a behaviour regression can be attributed and rolled back. Caching benefits come from stable prefixes, not from the metadata.

**Q6 — B.** Prompts alone are advisory and drift. Constraints in schema plus a deterministic post-check make the budget enforceable; a validator produces a measurable failure instead of a silently long answer.

**Q7 — model answer.** Downstream systems treat "valid according to the contract" as permission to act. If invalid output is coerced into a valid-looking object (defaults, string coercion, partial parse), the system acts on fabricated fields — e.g. an approval decision with a missing rationale and a guessed risk level. The failure is silent and appears downstream, where it is hardest to trace. Contract: invalid means an explicit `ExtractionResult(valid=False, value=None, errors=[...])` plus a recorded failure, never a repaired-looking object.

**Q8 — model answer.** A cassette is a recorded real provider interaction replayed offline. Unlike a hand-written mock, it preserves the *actual* payload shape, odd field names, SSE chunking and provider quirks — freezing real protocol behaviour into a deterministic test.

**Q9 — model answer.** (1) Derive `response_format_for(model_cls)` from the pydantic model and send `[system instruction rendered with the schema name, JSON Schema, *messages]`. (2) Decode tolerantly (`extract_json` strips markdown fences), then `model_cls.model_validate`; a presentation-budget `SchemaValidationError` raised by a decision model is treated as an extraction error too. (3) On failure with repairs remaining, send `[assistant(<invalid raw>), *build_repair_messages(raw, errors)]` and retry, bounded by `max_repairs` (default 1). (4) Success → `ExtractionResult(valid=True, value=<model>, raw=..., errors=[], repairs=n)`. (5) Exhaustion → `ExtractionResult(valid=False, value=None, raw=<last raw>, errors=<last errors>, repairs=n)` — **returned as data, never raised** — and `stats.record(repairs=..., valid=...)` is called once so `failure_rate` and `repair_rate` are measurable. A `ProviderError` propagates: a flaky wire is not a schema failure.

**Q10 — model answer.** (1) No schema is supplied to the provider, so the model is guessing the shape — failure rate will be high. (2) `Decision.model_validate_json(raw)` lets pydantic `ValidationError` (and `ValueError` from empty/invalid JSON, and the models' `SchemaValidationError` presentation-budget violations) escape: malformed output crashes the caller instead of becoming `ExtractionResult(valid=False, value=None, errors=[...])`, and the raw text is not captured for diagnostics. (3) There is no repair path and no stats — `build_repair_messages`, `max_repairs` and `RepairStats` are unused, so a fixable violation never gets its one retry, and neither `failure_rate` nor `repair_rate` can be reported. Also: no prompt version is recorded, so a schema/prompt change cannot be attributed.
