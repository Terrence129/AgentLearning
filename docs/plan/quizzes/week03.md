# Week 3 Quiz — Structured Output and Prompts as Assets

**第 3 周测验 — 结构化输出与「提示词即资产」**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** What does JSON mode guarantee?

JSON 模式能保证什么？

- A) The output validates against your JSON Schema

  输出能通过你的 JSON Schema 校验

- B) The output is syntactically valid JSON

  输出是语法上合法的 JSON

- C) The output contains no hallucinated fields

  输出不包含任何幻觉出来的字段

- D) The output is deterministic

  输出是确定性的

**Q2.** Why use a discriminated union (e.g. a required `kind` field) for a decision family?

为什么要为一族决策类型使用可辨识联合（discriminated union，例如一个必填的 `kind` 字段）？

- A) It reduces token usage

  它能减少 token 用量

- B) It lets the model emit different payload shapes while keeping one validatable contract

  它让模型可以输出不同结构的 payload，同时仍保持一个可校验的统一契约

- C) It removes the need for a repair loop

  它免去了修复循环的必要

- D) It makes the schema unconstrained

  它让 schema 不受约束

**Q3.** A validation-repair loop should be:

校验—修复循环应当：

- A) Unbounded until valid output appears

  不设上限，直到出现合法输出为止

- B) Bounded to a small number of attempts, with the validation error fed back

  限制在少量尝试次数内，并把校验错误反馈回去

- C) Replaced by asking the user to fix the JSON

  改为让用户去修复 JSON

- D) Run only when `temperature > 0`

  只在 `temperature > 0` 时运行

**Q4.** Which metric turns "structured output works" into an engineering claim?

哪个指标能把「结构化输出能用」变成一个工程上的论断？

- A) The number of prompt tokens

  提示词的 token 数

- B) The schema failure rate before and after repair

  修复前后的 schema 失败率

- C) The model's release date

  模型的发布日期

- D) The number of fields in the schema

  schema 中的字段数量

**Q5.** Prompt templates are immutable assets carrying `id` and `version`. The main reason is:

提示词模板是带有 `id` 和 `version` 的不可变资产。主要原因是：

- A) To make the prompt longer

  为了让提示词更长

- B) To attribute behaviour changes and make prompt edits reviewable diffs

  为了能够归因行为变化，并让提示词的修改成为可审阅的 diff

- C) To improve caching automatically

  为了自动提升缓存效果

- D) To satisfy provider rate limits

  为了满足模型提供商（provider）的限流要求

**Q6.** A "presentation budget" (headline ≤ 12 words, ≤ 4 next moves) is best enforced:

「呈现预算」（标题 ≤ 12 个词，后续动作 ≤ 4 条）最好通过什么方式来强制执行：

- A) By politely asking the model in the prompt only

  只在提示词里礼貌地请求模型遵守

- B) Structurally, by schema constraints and/or a post-validation check

  从结构上，通过 schema 约束和 / 或校验后的检查

- C) By lowering `temperature`

  通过降低 `temperature`

- D) By using a smaller model

  通过使用更小的模型

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** Why must invalid output **never** be surfaced as if it were valid? Give the failure mode it creates for a downstream decision system.

为什么**绝不能**把不合法的输出当作合法输出呈现出来？给出它会给下游决策系统造成的失败模式。

**Q8.** What is a cassette, and which specific property does it give your test suite that a `MockProvider` does not?

什么是 cassette（录制回放）？它为你的测试套件提供了哪种 `MockProvider` 所不具备的特定属性？

**Q9.** Sketch (in words or pseudocode) the `StructuredExtractor.extract(messages, Decision)` contract: schema enforcement, bounded repair, and what it returns once the repair attempts are exhausted. What happens on a provider error?

（用文字或伪代码）勾勒出 `StructuredExtractor.extract(messages, Decision)` 的契约：schema 强制、有上限的修复，以及修复次数用尽后它返回什么。遇到提供商错误时会发生什么？

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This function is the whole "structured output" implementation. Identify **three** defects.

下面这个函数就是全部的「结构化输出」实现。找出**三个**缺陷。

```python
def analyze(text: str) -> Decision:
    raw = provider.complete(messages=[{"role": "user", "content": text}]).content
    return Decision.model_validate_json(raw)
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** JSON mode guarantees parseable JSON, not schema compliance: fields can be missing, extra or wrong-typed. Only provider-enforced structured outputs (or your validation) give schema-level guarantees.

JSON 模式保证的是可解析的 JSON，而不是符合 schema：字段可能缺失、多余或类型错误。只有由提供商强制执行的结构化输出（或你自己的校验）才能提供 schema 层面的保证。

**Q2 — B.** A tag field lets one schema describe several shapes and still be validated precisely; it also maps cleanly to pydantic discriminated unions. It does not remove validation failures.

标签字段让一个 schema 可以描述多种结构，同时仍能被精确校验；它还能干净地映射到 pydantic 的可辨识联合。但它并不能消除校验失败。

**Q3 — B.** Bounded repair (typically one retry) recovers most transient malformations without hiding the failure rate. Unbounded repair is a cost/latency bug.

有上限的修复（通常是一次重试）能挽回大多数偶发的格式错误，同时不会掩盖失败率。无上限的修复是一个成本 / 延迟 bug。

**Q4 — B.** Failure rate is the observable that tells you whether schema, model or prompt is the problem, and whether repair earns its cost.

失败率是一个可观测指标，它告诉你问题出在 schema、模型还是提示词上，以及修复是否值回它的成本。

**Q5 — B.** Prompts are code: the `id`/`version` pair makes every prompt change an explicit, reviewable revision (editing history is forbidden — you bump the version instead), so a behaviour regression can be attributed and rolled back. Caching benefits come from stable prefixes, not from the metadata.

提示词就是代码：`id` / `version` 这对字段让每一次提示词修改都成为显式、可审阅的修订（禁止改动历史版本——而是升版本号），因此行为回归可以被归因并回滚。缓存收益来自稳定的前缀，而不是来自这些元数据。

**Q6 — B.** Prompts alone are advisory and drift. Constraints in schema plus a deterministic post-check make the budget enforceable; a validator produces a measurable failure instead of a silently long answer.

仅靠提示词只是建议性的，而且会漂移。schema 中的约束加上确定性的事后检查，才能让预算可被强制执行；校验器会产生一个可度量的失败，而不是悄无声息地给出一个过长的回答。

**Q7 — model answer.** Downstream systems treat "valid according to the contract" as permission to act. If invalid output is coerced into a valid-looking object (defaults, string coercion, partial parse), the system acts on fabricated fields — e.g. an approval decision with a missing rationale and a guessed risk level. The failure is silent and appears downstream, where it is hardest to trace. Contract: invalid means an explicit `ExtractionResult(valid=False, value=None, errors=[...])` plus a recorded failure, never a repaired-looking object.

**参考答案。** 下游系统会把「符合契约的合法输出」视为可以采取行动的许可。如果不合法的输出被强行转换成一个看似合法的对象（填默认值、字符串强制转换、部分解析），系统就会基于编造出来的字段采取行动——例如一个缺失理由、风险等级靠猜的审批决策。这种失败是静默的，并且出现在下游，最难追查。契约：不合法就意味着一个显式的 `ExtractionResult(valid=False, value=None, errors=[...])` 外加一条记录在案的失败，绝不是一个看起来已被修好的对象。

**Q8 — model answer.** A cassette is a recorded real provider interaction replayed offline. Unlike a hand-written mock, it preserves the *actual* payload shape, odd field names, SSE chunking and provider quirks — freezing real protocol behaviour into a deterministic test.

**参考答案。** cassette 是一次被录制下来、可离线回放的真实提供商交互。与手写的 mock 不同，它保留了*真实*的 payload 结构、古怪的字段名、SSE 分块以及提供商的种种怪癖——把真实的协议行为冻结成一个确定性的测试。

**Q9 — model answer.** (1) Derive `response_format_for(model_cls)` from the pydantic model and send `[system instruction rendered with the schema name, JSON Schema, *messages]`. (2) Decode tolerantly (`extract_json` strips markdown fences), then `model_cls.model_validate`; a presentation-budget `SchemaValidationError` raised by a decision model is treated as an extraction error too. (3) On failure with repairs remaining, send `[assistant(<invalid raw>), *build_repair_messages(raw, errors)]` and retry, bounded by `max_repairs` (default 1). (4) Success → `ExtractionResult(valid=True, value=<model>, raw=..., errors=[], repairs=n)`. (5) Exhaustion → `ExtractionResult(valid=False, value=None, raw=<last raw>, errors=<last errors>, repairs=n)` — **returned as data, never raised** — and `stats.record(repairs=..., valid=...)` is called once so `failure_rate` and `repair_rate` are measurable. A `ProviderError` propagates: a flaky wire is not a schema failure.

**参考答案。** (1) 从 pydantic 模型推导出 `response_format_for(model_cls)`，并发送 `[用 schema 名称渲染的系统指令, JSON Schema, *messages]`。(2) 宽容地解码（`extract_json` 会去掉 markdown 代码围栏），然后执行 `model_cls.model_validate`；决策模型抛出的呈现预算 `SchemaValidationError` 也被视为提取错误。(3) 失败且仍有修复次数时，发送 `[assistant(<invalid raw>), *build_repair_messages(raw, errors)]` 并重试，次数上限为 `max_repairs`（默认为 1）。(4) 成功 → `ExtractionResult(valid=True, value=<model>, raw=..., errors=[], repairs=n)`。(5) 用尽 → `ExtractionResult(valid=False, value=None, raw=<last raw>, errors=<last errors>, repairs=n)`——**作为数据返回，绝不抛出**——并且 `stats.record(repairs=..., valid=...)` 只调用一次，使 `failure_rate` 和 `repair_rate` 可被度量。`ProviderError` 则直接向上传播：网络不稳定并不是 schema 失败。

**Q10 — model answer.** (1) No schema is supplied to the provider, so the model is guessing the shape — failure rate will be high. (2) `Decision.model_validate_json(raw)` lets pydantic `ValidationError` (and `ValueError` from empty/invalid JSON, and the models' `SchemaValidationError` presentation-budget violations) escape: malformed output crashes the caller instead of becoming `ExtractionResult(valid=False, value=None, errors=[...])`, and the raw text is not captured for diagnostics. (3) There is no repair path and no stats — `build_repair_messages`, `max_repairs` and `RepairStats` are unused, so a fixable violation never gets its one retry, and neither `failure_rate` nor `repair_rate` can be reported. Also: no prompt version is recorded, so a schema/prompt change cannot be attributed.

**参考答案。** (1) 没有把 schema 提供给提供商，所以模型只能猜测结构——失败率会很高。(2) `Decision.model_validate_json(raw)` 会让 pydantic 的 `ValidationError`（以及空 / 非法 JSON 导致的 `ValueError`，还有模型中违反呈现预算的 `SchemaValidationError`）逃逸出去：格式错误的输出会让调用方崩溃，而不是变成 `ExtractionResult(valid=False, value=None, errors=[...])`，原始文本也没有被保存下来用于诊断。(3) 没有修复路径，也没有统计——`build_repair_messages`、`max_repairs` 和 `RepairStats` 都没被用上，所以一个可修复的违规永远得不到那一次重试，`failure_rate` 和 `repair_rate` 也都无法上报。另外：没有记录提示词版本，所以 schema / 提示词的变更无法被归因。
