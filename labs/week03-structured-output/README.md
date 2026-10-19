# Week 3 lab — Structured output, prompts as assets, typed decisions

## 1. Why this week exists

A paragraph of prose is not a contract: downstream code cannot branch on it, evals cannot score it, and a nearly-right answer looks identical to a catastrophically wrong one. Worse, JSON mode only guarantees *parseable* JSON — not your schema — so a naive `model_validate_json(raw)` turns a model mistake into an exception in production, or worse, coerces defaults into a decision that then gets acted on. This week you make model output a typed contract: schema-constrained requests, local validation, one bounded repair that feeds errors back, a failure-rate metric, versioned prompt assets, and a discriminated decision family whose presentation budgets are enforced by code rather than requested by prose. The invariant to protect above all: **invalid output is never surfaced as valid.**

## 2. Prerequisites & time budget

- **8–10 hours** (extraction + repair ~4 h, prompts ~1.5 h, decisions ~2 h, review ~1 h).
- Week 2 tests green is recommended (the lab artifact reuses the loop conceptually) but this week is self-contained for verification: `MockProvider` + `CassetteProvider` only.
- Read first: [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §3, [`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) §3, [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.4, and provider structured-output docs (OpenAI `response_format`, DeepSeek JSON mode).

## 3. The spec

| File | Member | Contract |
|---|---|---|
| [`agentlab/schemas/structured.py`](../../agentlab/schemas/structured.py) | `extract_json`, `response_format_for`, `StructuredExtractor`, `ExtractionResult` | Decode JSON from model text (tolerate markdown fences); build `{"type": "json_schema", ...}` from a pydantic model; ask the provider with a versioned system prompt + schema; validate locally; on failure repair at most `max_repairs` times by appending the invalid output and field-level errors; return `valid=True, value=<model>` **or** `valid=False, value=None, raw=<last output>, errors=[...], repairs=<n>`; record stats; provider errors propagate. |
| [`agentlab/schemas/repair.py`](../../agentlab/schemas/repair.py) | `REPAIR_PROMPT`, `format_validation_errors`, `build_repair_messages`, `RepairStats` | Format `ValidationError.errors()` as `"field.path: message"`; build `[assistant(invalid raw), user(instruction with every error)]`; count clean / repaired / failed and expose `repair_rate` and `failure_rate` (0.0 when empty). |
| [`agentlab/schemas/prompts.py`](../../agentlab/schemas/prompts.py) | `PromptTemplate`, `PromptRegistry` | Immutable `id`/`version`/`template`; `render(**values)` fails on a missing placeholder (`PromptRenderError`), ignores extras; `hash` = sha256 of id + template (64 hex, version-independent); registry rejects duplicate id+version and non-numeric versions, resolves latest numerically, lists versions, renders, reports membership. |
| [`agentlab/schemas/structured.py`](../../agentlab/schemas/structured.py) | `PresentationBudget`, `DecisionUnion`, `parse_decision` | Budgets: headline ≤ 12 words, meaning ≤ 2 sentences, next moves ≤ 4, clarification options ≤ 3. `_BudgetedDecision` variants (`ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal`) enforce the budget on construction via `SchemaValidationError`; `ActionProposal.requires_approval` is always `True`; `parse_decision(payload)` returns the variant selected by `kind` and never a guessed one; `decision_schema()` is a discriminated JSON Schema. |

## 4. Acceptance criteria

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week03 -m week -q   # all green
.\.venv\Scripts\ruff.exe check agentlab/schemas
```

```bash
# macOS / Linux
uv run pytest tests/week03 -m week -q   # all green
uv run ruff check agentlab/schemas
```

Lab artifact: `analyze(text) -> Decision` built from `StructuredExtractor` + `DecisionUnion` over ~20 cases (scripted provider is fine), plus a one-paragraph failure-rate report from `extractor.stats` (clean / repaired / failed, `failure_rate`). Offline only — the cassette test in `tests/week03/test_structured.py` shows the replay pattern.

## 5. Hints (progressive)

1. Read `tests/week03/` in this order: prompts → repair → structured → decisions. Each file is one layer.
2. `extract_json` should return whatever JSON parses; the **extractor** is responsible for requiring an object before `model_cls.model_validate`. Keep those two failures distinct in the error text.
3. The extractor's request starts as `[system, *messages]`; a repair attempt replaces the request messages with `[*previous, *build_repair_messages(raw, errors)]` — note `build_repair_messages` already contains the assistant turn, so do not append `response.message` again.
4. `SchemaValidationError` raised by a pydantic `model_validator` is **not** wrapped in `ValidationError` (only `ValueError`/`AssertionError` are). Catch both in `_decode`; otherwise a presentation-budget failure would crash the extraction instead of being repaired.
5. Prompt hash: use `hashlib.sha256(f"{id}\x00{template}".encode()).hexdigest()`. Exclude the version — a no-op version bump should not look like a behaviour change.
6. For `DecisionUnion`, use `Annotated[..., Field(discriminator="kind")]`; then `TypeAdapter(DecisionUnion).json_schema()` gives the tagged schema and `validate_python` gives the right class. Each variant field order does not matter, but every variant must declare its own `kind` literal.
7. Budget counting: split sentences with `re.split(r"[.!?]+", meaning)` and drop empty fragments — "Do it. Then stop!" is two sentences, not three.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| Repair test sees 5 messages, roles mismatched | You appended both `response.message` and `build_repair_messages(...)` (which already includes the invalid assistant turn). |
| Presentation-budget failures escape as a crash | Your validator raises a non-`ValueError`; pydantic propagates it. Catch `SchemaValidationError` explicitly in the extraction path. |
| `PromptRenderError` not raised for a missing key | You used `"{}".format(**values)` or `format_map` with a plain dict — both raise `KeyError`/`IndexError`. Use a mapping with `__missing__`, or pre-check placeholders. |
| Registry picks `1.9` over `1.10` | You sorted version strings lexicographically; parse to integer tuples. |
| `value` is not `None` on an invalid result | Some path coerces defaults or returns a partially-validated model; every failure must return `ExtractionResult(valid=False, value=None, ...)`. |
| Cassette replay misses | The request hash includes the model name; a replaying cassette reports `"cassette"` unless you give it the recorded model. (See the `_ReplayProvider` helper in the tests.) |

## 7. SendOS bridge

Read `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`, `.../Decision/DecisionInteraction.cs` and `.../Decision/PresentationBudgetEnforcer.cs`; the summary is in [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §2.1 and §4.4.

Answer in 5 bullets:

1. `JsonSchemaValidator` is a hand-rolled subset of JSON Schema. What does it validate, what does it do with unsupported keywords, and why is "validate after" more honest than pretending the schema is impossible to violate?
2. `StructuredCompletionHandler` returns `valid=False, output=None` on mismatch. How does your `ExtractionResult` mirror that, and where does your repair loop sit relative to the handler (inside or outside)?
3. `PresentationBudgetEnforcer` is a structural check on the decision family. Which of your budgets map to which SendOS limit, and which limit is *not* a presentation concern (e.g. approval requirement) and therefore belongs elsewhere?

## 8. Stretch

1. **Failure-rate by schema depth.** Build three versions of the same extraction model with 1/2/3 levels of nesting, run 20 scripted (or live, capped) cases per version, and report failure rate before and after repair. When does hand-rolled validation beat provider-native schema enforcement?
2. **Streaming cassettes.** `CassetteProvider.stream` is deliberately unimplemented. Design a frame format that replays fragmented SSE deterministically, implement it, and prove `assemble_stream(replay.stream(req))` equals the recorded `complete` response.

## 9. Reflection (weekly review)

1. **Conceptual:** What is the difference between JSON mode, structured outputs and grammar-constrained decoding — and which one is your `response_format_for` actually asking for?
2. **Architectural:** Validation failure can be data (`ExtractionResult(valid=False, ...)`) or an exception (`SchemaValidationError`). Which callers should get which, and what does the choice do to the repair loop and the metrics?
3. **Transfer:** Prompts now have `id`/`version`/`hash`. If a prompt change causes a 10% quality regression in production, what exactly do these three fields let you do that a git blame does not?
