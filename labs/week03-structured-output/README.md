# Week 3 lab — Structured output, prompts as assets, typed decisions

**第 3 周实验（lab）— 结构化输出、作为资产的提示词、类型化决策**

## 1. Why this week exists

**1. 为什么要有这一周**

A paragraph of prose is not a contract: downstream code cannot branch on it, evals cannot score it, and a nearly-right answer looks identical to a catastrophically wrong one. Worse, JSON mode only guarantees *parseable* JSON — not your schema — so a naive `model_validate_json(raw)` turns a model mistake into an exception in production, or worse, coerces defaults into a decision that then gets acted on. This week you make model output a typed contract: schema-constrained requests, local validation, one bounded repair that feeds errors back, a failure-rate metric, versioned prompt assets, and a discriminated decision family whose presentation budgets are enforced by code rather than requested by prose. The invariant to protect above all: **invalid output is never surfaced as valid.**

一段散文不是契约：下游代码无法据此分支，评测（eval）无法为它打分，而一个几乎正确的回答和一个灾难性错误的回答看起来一模一样。更糟的是，JSON 模式只保证 JSON *可解析* —— 并不保证符合你的 schema —— 所以一个天真的 `model_validate_json(raw)` 会把模型的错误变成生产环境中的异常，甚至更糟：把默认值强行填充成一个决策，然后这个决策被付诸执行。本周你要让模型输出成为类型化的契约：受 schema 约束的请求、本地校验、一次有上限且会回传错误的修复、一个失败率指标、带版本的提示词资产，以及一个带判别字段的决策族，其展示预算由代码强制执行，而不是靠文字去请求。最需要守住的不变量是：**无效输出永远不会被当作有效输出呈现出来。**

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **8–10 hours** (extraction + repair ~4 h, prompts ~1.5 h, decisions ~2 h, review ~1 h).

  **8–10 小时**（提取 + 修复约 4 小时，提示词约 1.5 小时，决策约 2 小时，复盘约 1 小时）。

- Week 2 tests green is recommended (the lab artifact reuses the loop conceptually) but this week is self-contained for verification: `MockProvider` + `CassetteProvider` only.

  建议第 2 周的测试已通过（变绿）（实验产出物在概念上会复用该循环），但本周的验证是自包含的：只需要 `MockProvider` + `CassetteProvider`。

- Read first: [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §3, [`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) §3, [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.4, and provider structured-output docs (OpenAI `response_format`, DeepSeek JSON mode).

  先阅读：[`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) 的 §3、[`docs/research/02-frameworks-protocols.md`](../../docs/research/02-frameworks-protocols.md) 的 §3、[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) 的 §4.4，以及模型提供商（provider）的结构化输出文档（OpenAI `response_format`、DeepSeek JSON 模式）。

## 3. The spec

**3. 规格说明**

| File<br>文件 | Member<br>成员 | Contract<br>契约 |
|---|---|---|
| [`agentlab/schemas/structured.py`](../../agentlab/schemas/structured.py) | `extract_json`, `response_format_for`, `StructuredExtractor`, `ExtractionResult` | Decode JSON from model text (tolerate markdown fences); build `{"type": "json_schema", ...}` from a pydantic model; ask the provider with a versioned system prompt + schema; validate locally; on failure repair at most `max_repairs` times by appending the invalid output and field-level errors; return `valid=True, value=<model>` **or** `valid=False, value=None, raw=<last output>, errors=[...], repairs=<n>`; record stats; provider errors propagate.<br>从模型文本中解码 JSON（容忍 markdown 代码围栏）；从 pydantic 模型构建 `{"type": "json_schema", ...}`；用带版本的系统提示词 + schema 向提供商发起请求；在本地校验；失败时最多修复 `max_repairs` 次，做法是追加无效输出和字段级错误；返回 `valid=True, value=<model>` **或** `valid=False, value=None, raw=<last output>, errors=[...], repairs=<n>`；记录统计数据；提供商错误直接向上传播。 |
| [`agentlab/schemas/repair.py`](../../agentlab/schemas/repair.py) | `REPAIR_PROMPT`, `format_validation_errors`, `build_repair_messages`, `RepairStats` | Format `ValidationError.errors()` as `"field.path: message"`; build `[assistant(invalid raw), user(instruction with every error)]`; count clean / repaired / failed and expose `repair_rate` and `failure_rate` (0.0 when empty).<br>把 `ValidationError.errors()` 格式化为 `"field.path: message"`；构建 `[assistant(invalid raw), user(instruction with every error)]`；统计 clean / repaired / failed 的数量，并暴露 `repair_rate` 和 `failure_rate`（为空时为 0.0）。 |
| [`agentlab/schemas/prompts.py`](../../agentlab/schemas/prompts.py) | `PromptTemplate`, `PromptRegistry` | Immutable `id`/`version`/`template`; `render(**values)` fails on a missing placeholder (`PromptRenderError`), ignores extras; `hash` = sha256 of id + template (64 hex, version-independent); registry rejects duplicate id+version and non-numeric versions, resolves latest numerically, lists versions, renders, reports membership.<br>不可变的 `id`/`version`/`template`；`render(**values)` 在缺少占位符时失败（`PromptRenderError`），忽略多余的值；`hash` = id + template 的 sha256（64 位十六进制，与版本无关）；注册表拒绝重复的 id+version 和非数字版本，按数值解析出最新版本，列出版本，执行渲染，并报告是否包含某项。 |
| [`agentlab/schemas/structured.py`](../../agentlab/schemas/structured.py) | `PresentationBudget`, `DecisionUnion`, `parse_decision` | Budgets: headline ≤ 12 words, meaning ≤ 2 sentences, next moves ≤ 4, clarification options ≤ 3. `_BudgetedDecision` variants (`ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal`) enforce the budget on construction via `SchemaValidationError`; `ActionProposal.requires_approval` is always `True`; `parse_decision(payload)` returns the variant selected by `kind` and never a guessed one; `decision_schema()` is a discriminated JSON Schema.<br>预算：标题 ≤ 12 个词，含义 ≤ 2 句，后续动作 ≤ 4 个，澄清选项 ≤ 3 个。`_BudgetedDecision` 的各个变体（`ClarificationPrompt`、`DirectAnswer`、`Decision`、`Recommendation`、`ActionProposal`）在构造时通过 `SchemaValidationError` 强制执行预算；`ActionProposal.requires_approval` 始终为 `True`；`parse_decision(payload)` 返回由 `kind` 选定的变体，绝不猜测；`decision_schema()` 是一个带判别字段的 JSON Schema。 |

## 4. Acceptance criteria

**4. 验收标准**

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

实验产出物：用 `StructuredExtractor` + `DecisionUnion` 构建 `analyze(text) -> Decision`，在约 20 个用例上运行（使用预设脚本的提供商即可），并基于 `extractor.stats` 写一段失败率报告（clean / repaired / failed、`failure_rate`）。仅限离线 —— `tests/week03/test_structured.py` 中的 cassette（录制回放）测试展示了回放模式。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. Read `tests/week03/` in this order: prompts → repair → structured → decisions. Each file is one layer.

   按以下顺序阅读 `tests/week03/`：prompts → repair → structured → decisions。每个文件对应一层。

2. `extract_json` should return whatever JSON parses; the **extractor** is responsible for requiring an object before `model_cls.model_validate`. Keep those two failures distinct in the error text.

   `extract_json` 应该返回任何能解析出来的 JSON；由**提取器**负责在 `model_cls.model_validate` 之前要求它必须是一个对象。在错误文本中把这两种失败区分开。

3. The extractor's request starts as `[system, *messages]`; a repair attempt replaces the request messages with `[*previous, *build_repair_messages(raw, errors)]` — note `build_repair_messages` already contains the assistant turn, so do not append `response.message` again.

   提取器的请求一开始是 `[system, *messages]`；一次修复尝试会把请求消息替换为 `[*previous, *build_repair_messages(raw, errors)]` —— 注意 `build_repair_messages` 已经包含了 assistant 那一轮，所以不要再追加 `response.message`。

4. `SchemaValidationError` raised by a pydantic `model_validator` is **not** wrapped in `ValidationError` (only `ValueError`/`AssertionError` are). Catch both in `_decode`; otherwise a presentation-budget failure would crash the extraction instead of being repaired.

   由 pydantic `model_validator` 抛出的 `SchemaValidationError` **不会**被包装进 `ValidationError`（只有 `ValueError`/`AssertionError` 会）。在 `_decode` 中把两者都捕获；否则展示预算的失败会让提取直接崩溃，而不是进入修复。

5. Prompt hash: use `hashlib.sha256(f"{id}\x00{template}".encode()).hexdigest()`. Exclude the version — a no-op version bump should not look like a behaviour change.

   提示词哈希：使用 `hashlib.sha256(f"{id}\x00{template}".encode()).hexdigest()`。不要包含版本 —— 一次没有实质改动的版本号提升不应该看起来像行为变化。

6. For `DecisionUnion`, use `Annotated[..., Field(discriminator="kind")]`; then `TypeAdapter(DecisionUnion).json_schema()` gives the tagged schema and `validate_python` gives the right class. Each variant field order does not matter, but every variant must declare its own `kind` literal.

   对于 `DecisionUnion`，使用 `Annotated[..., Field(discriminator="kind")]`；这样 `TypeAdapter(DecisionUnion).json_schema()` 会给出带标签的 schema，`validate_python` 会给出正确的类。各变体的字段顺序无关紧要，但每个变体都必须声明自己的 `kind` 字面量。

7. Budget counting: split sentences with `re.split(r"[.!?]+", meaning)` and drop empty fragments — "Do it. Then stop!" is two sentences, not three.

   预算计数：用 `re.split(r"[.!?]+", meaning)` 切分句子，并丢弃空片段 ——「Do it. Then stop!」是两句，不是三句。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| Repair test sees 5 messages, roles mismatched<br>修复测试看到 5 条消息，角色不匹配 | You appended both `response.message` and `build_repair_messages(...)` (which already includes the invalid assistant turn).<br>你同时追加了 `response.message` 和 `build_repair_messages(...)`（后者已经包含了那个无效的 assistant 轮次）。 |
| Presentation-budget failures escape as a crash<br>展示预算失败逃逸成了崩溃 | Your validator raises a non-`ValueError`; pydantic propagates it. Catch `SchemaValidationError` explicitly in the extraction path.<br>你的校验器抛出的不是 `ValueError`；pydantic 会把它直接传播出去。在提取路径中显式捕获 `SchemaValidationError`。 |
| `PromptRenderError` not raised for a missing key<br>缺少 key 时没有抛出 `PromptRenderError` | You used `"{}".format(**values)` or `format_map` with a plain dict — both raise `KeyError`/`IndexError`. Use a mapping with `__missing__`, or pre-check placeholders.<br>你用了 `"{}".format(**values)` 或配合普通字典的 `format_map` —— 两者都会抛出 `KeyError`/`IndexError`。使用带 `__missing__` 的映射，或预先检查占位符。 |
| Registry picks `1.9` over `1.10`<br>注册表选了 `1.9` 而不是 `1.10` | You sorted version strings lexicographically; parse to integer tuples.<br>你按字典序对版本字符串排序了；应该解析成整数元组。 |
| `value` is not `None` on an invalid result<br>无效结果中 `value` 不是 `None` | Some path coerces defaults or returns a partially-validated model; every failure must return `ExtractionResult(valid=False, value=None, ...)`.<br>某条路径强行填充了默认值，或返回了部分校验过的模型；每一种失败都必须返回 `ExtractionResult(valid=False, value=None, ...)`。 |
| Cassette replay misses<br>Cassette 回放未命中 | The request hash includes the model name; a replaying cassette reports `"cassette"` unless you give it the recorded model. (See the `_ReplayProvider` helper in the tests.)<br>请求哈希包含模型名称；回放中的 cassette 会报告 `"cassette"`，除非你把录制时的模型名传给它。（参见测试中的 `_ReplayProvider` 辅助类。） |

## 7. SendOS bridge

**7. SendOS 对照**

Read `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`, `.../Decision/DecisionInteraction.cs` and `.../Decision/PresentationBudgetEnforcer.cs`; the summary is in [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §2.1 and §4.4.

阅读 `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`、`.../Decision/DecisionInteraction.cs` 和 `.../Decision/PresentationBudgetEnforcer.cs`；概要见 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) 的 §2.1 和 §4.4。

Answer in 5 bullets:

用 5 个要点回答：

1. `JsonSchemaValidator` is a hand-rolled subset of JSON Schema. What does it validate, what does it do with unsupported keywords, and why is "validate after" more honest than pretending the schema is impossible to violate?

   `JsonSchemaValidator` 是手工实现的 JSON Schema 子集。它校验什么？遇到不支持的关键字时怎么处理？为什么“事后校验”比假装 schema 不可能被违反更诚实？

2. `StructuredCompletionHandler` returns `valid=False, output=None` on mismatch. How does your `ExtractionResult` mirror that, and where does your repair loop sit relative to the handler (inside or outside)?

   `StructuredCompletionHandler` 在不匹配时返回 `valid=False, output=None`。你的 `ExtractionResult` 如何与之对应？你的修复循环相对于这个 handler 处在什么位置（内部还是外部）？

3. `PresentationBudgetEnforcer` is a structural check on the decision family. Which of your budgets map to which SendOS limit, and which limit is *not* a presentation concern (e.g. approval requirement) and therefore belongs elsewhere?

   `PresentationBudgetEnforcer` 是对决策族的结构性检查。你的哪些预算对应 SendOS 的哪个限制？哪个限制*不*属于展示层面的关注点（例如审批要求），因此应该放在别处？

## 8. Stretch

**8. 拓展**

1. **Failure-rate by schema depth.** Build three versions of the same extraction model with 1/2/3 levels of nesting, run 20 scripted (or live, capped) cases per version, and report failure rate before and after repair. When does hand-rolled validation beat provider-native schema enforcement?

   **按 schema 深度统计失败率。** 为同一个提取模型构建三个版本，分别有 1/2/3 层嵌套，每个版本运行 20 个预设脚本（或真实调用、设有上限）的用例，并报告修复前后的失败率。手工校验什么时候会胜过提供商原生的 schema 强制？

2. **Streaming cassettes.** `CassetteProvider.stream` is deliberately unimplemented. Design a frame format that replays fragmented SSE deterministically, implement it, and prove `assemble_stream(replay.stream(req))` equals the recorded `complete` response.

   **流式 cassette。** `CassetteProvider.stream` 被刻意留作未实现。设计一种能确定性地回放分片 SSE 的帧格式，实现它，并证明 `assemble_stream(replay.stream(req))` 等于录制下来的 `complete` 响应。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** What is the difference between JSON mode, structured outputs and grammar-constrained decoding — and which one is your `response_format_for` actually asking for?

   **概念层面：** JSON 模式、结构化输出和语法约束解码之间有什么区别？你的 `response_format_for` 实际请求的是哪一种？

2. **Architectural:** Validation failure can be data (`ExtractionResult(valid=False, ...)`) or an exception (`SchemaValidationError`). Which callers should get which, and what does the choice do to the repair loop and the metrics?

   **架构层面：** 校验失败可以是数据（`ExtractionResult(valid=False, ...)`），也可以是异常（`SchemaValidationError`）。哪些调用方应该得到哪一种？这个选择会对修复循环和指标产生什么影响？

3. **Transfer:** Prompts now have `id`/`version`/`hash`. If a prompt change causes a 10% quality regression in production, what exactly do these three fields let you do that a git blame does not?

   **迁移层面：** 提示词现在有了 `id`/`version`/`hash`。如果一次提示词改动在生产环境中造成了 10% 的质量回归，这三个字段具体能让你做到哪些 git blame 做不到的事？
