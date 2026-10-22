# Week 7 — Evals and observability

**第 7 周 — 评测（eval）与可观测性**

Build the regression gate that turns *"it seems better"* into *"the numbers say it is better, and here is the proof"*.

构建一道回归关卡，把「*看起来更好了*」变成「*数据表明它确实更好，证据在此*」。

## 1. Why this week exists

**1. 为什么要有这一周**

An agent you cannot evaluate is an agent you cannot improve. Without a versioned dataset, deterministic-first scoring and a baseline gate, every prompt change is a coin flip: regressions ship because nobody measured them, and improvements are indistinguishable from luck. This week builds the feedback loop that every later week (and the capstone release gate) depends on.

无法评测的 Agent 就是无法改进的 Agent。没有带版本的数据集、确定性优先的评分和基线关卡，每一次提示词修改都像抛硬币：回归会被发布出去，因为没人度量过它们；而改进也与运气无从区分。本周构建的反馈回路是之后每一周（以及结业项目（capstone）的发布关卡）都要依赖的。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **8–10 hours** (build sessions of 2–3 h; the lab artifact needs a second sitting).

  **8–10 小时**（每次构建 2–3 小时；实验（lab）产物需要再安排一次时间完成）。

- Green: `pytest -m week` for weeks 1–6 as far as they are implemented (you only need the *types*, not the earlier agents, because this week is tested in isolation).

  通过（变绿）：第 1–6 周中已实现部分的 `pytest -m week`（你只需要那些*类型*，而不需要之前的 Agent，因为本周是隔离测试的）。

- Read first: [`docs/research/03-production-evals-ops.md`](../../docs/research/03-production-evals-ops.md) §1.1–1.6 (decision tree, pass@k vs pass^k, judge discipline, release gates) and §2 (trace/Observability — at least §2.1–2.2).

  先读：[`docs/research/03-production-evals-ops.md`](../../docs/research/03-production-evals-ops.md) §1.1–1.6（决策树、pass@k 与 pass^k 的对比、评审的使用规范、发布关卡）以及 §2（trace/可观测性——至少读 §2.1–2.2）。

- Re-read: [`agentlab/trace.py`](../../agentlab/trace.py) (what a trace event is) and [`agentlab/testing/mock.py`](../../agentlab/testing/mock.py) (scripted providers: the only model calls this lab makes).

  重读：[`agentlab/trace.py`](../../agentlab/trace.py)（trace 事件是什么）和 [`agentlab/testing/mock.py`](../../agentlab/testing/mock.py)（脚本化的模型提供商（provider）：本实验唯一会发起的模型调用）。

## 3. The spec

**3. 规格说明**

Implement everything under `agentlab/evals/`. The tests are the specification; the docstrings state the contract. Nothing here may call a network or a real model.

实现 `agentlab/evals/` 下的所有内容。测试就是规格说明；docstring 写明了契约。这里的任何代码都不得访问网络或调用真实模型。

### `agentlab/evals/dataset.py` — cases as versioned data

**`agentlab/evals/dataset.py` — 把用例当作带版本的数据**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `EvalCase`, `RubricCriterion`, `DeterministicCheck` | frozen value types; ids stable; checks are the closed set in `CHECK_KINDS`<br>冻结的值类型；id 稳定；检查项属于 `CHECK_KINDS` 中的封闭集合 |
| `EvalDataset.validate() -> list[str]` | collect **all** problems (duplicate ids, unknown check kind, missing required params, non-positive weights, no checks *and* no rubric, bad threshold); never raise<br>收集**所有**问题（重复 id、未知的检查类型、缺少必需参数、非正权重、既没有检查项*也*没有评分标准（rubric）、阈值不合法）；绝不抛出异常 |
| `EvalDataset.content_digest() -> str` | SHA-256 over canonical case records, header metadata excluded<br>对规范化的用例记录计算 SHA-256，不包含头部元数据 |
| `dataset_to_records` / `dataset_from_records` | JSONL-ready dicts, header first; raise `DatasetError` with `.errors`<br>可直接写成 JSONL 的字典，头部在最前；抛出带有 `.errors` 的 `DatasetError` |
| `load_dataset` / `save_dataset` | UTF-8 JSONL round-trip; save validates first (**fail closed**); malformed JSON names the line<br>UTF-8 JSONL 往返读写；保存前先校验（**失败即关闭**）；格式错误的 JSON 会指明所在行 |

### `agentlab/evals/judges.py` — a calibrated instrument

**`agentlab/evals/judges.py` — 一件经过校准的仪器**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `RubricJudge.judge(case, output) -> JudgeVerdict` | one provider call, `response_format={"type": "json_object"}`, rubric + output present in the messages; every criterion id exactly once; malformed/unknown/out-of-range output raises `SchemaValidationError` (never a partial verdict)<br>一次 provider 调用，`response_format={"type": "json_object"}`，消息中包含评分标准和输出；每个评分项 id 恰好出现一次；格式错误/未知/超出范围的输出会抛出 `SchemaValidationError`（绝不给出部分裁决） |
| `JudgeVerdict` | weighted normalized score `sum(score·weight) / (2·sum(weight))`; `passed = score >= case.pass_threshold`<br>加权归一化得分 `sum(score·weight) / (2·sum(weight))`；`passed = score >= case.pass_threshold` |
| `agreement_rate` / `cohen_kappa` | raw and chance-corrected agreement over label sequences; `ValueError` on empty/length mismatch<br>基于标签序列的原始一致率和经机会校正的一致率；序列为空或长度不匹配时抛出 `ValueError` |
| `measure_agreement(verdicts, labels)` | pair by **case id** (never by position); report `n`, agreement, kappa, sorted disagreements<br>按**用例 id** 配对（绝不按位置）；报告 `n`、一致率、kappa 以及排好序的分歧项 |

### `agentlab/evals/harness.py` — deterministic checks first

**`agentlab/evals/harness.py` — 确定性检查优先**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `AgentRun` | the only agent↔harness seam: output, tool calls, steps, usage, optional latency, error<br>Agent 与 harness（运行框架）之间唯一的接缝（seam）：输出、工具调用、步数、用量、可选的延迟、错误 |
| `EvalHarness.run(dataset) -> EvalRun` | validate dataset, run each case `repeats` times, capture a `Tracer` per trial; factory exceptions become failed trials; judge called **only after** deterministic checks pass; malformed judge output is a failed trial; each trace ends with a harness-emitted `eval_case` event<br>校验数据集，每个用例运行 `repeats` 次，每次试验捕获一个 `Tracer`；工厂函数的异常记为失败的试验；**只有在**确定性检查通过**之后**才调用评审；评审输出格式错误记为失败的试验；每条 trace 都以 harness 发出的 `eval_case` 事件结尾 |
| `CheckResult` / `CaseTrial` / `CaseResult` | per-check outcome, per-trial record, per-case roll-up (`pass_at_1`, `pass_all`)<br>每项检查的结果、每次试验的记录、每个用例的汇总（`pass_at_1`、`pass_all`） |
| `pass_at_1` / `pass_hat_k` | capability vs reliability: `pass_k` requires `k` trials; `k` outside `[1, repeats]` raises `ValueError`<br>能力与可靠性之别：`pass_k` 需要 `k` 次试验；`k` 超出 `[1, repeats]` 时抛出 `ValueError` |
| `EvalRun.metrics()` | `cases`, `trials`, `pass_at_1`, `pass_hat_k`, `total_cost_usd`, `avg_cost_usd`, `avg_latency_ms`, `p95_latency_ms` |
| `failure_taxonomy` | failed trials grouped by `failure_kind` (`agent_error`, `deterministic:<kind>`, `judge_rubric`, `judge_format_error`)<br>按 `failure_kind`（`agent_error`、`deterministic:<kind>`、`judge_rubric`、`judge_format_error`）分组的失败试验 |

### `agentlab/evals/report.py` — report and CI gate

**`agentlab/evals/report.py` — 报告与 CI 关卡**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `check_baseline(baseline, current, thresholds) -> GateResult` | compares the four `GATE_METRICS`; pass drops are absolute, cost/latency are relative; a missing metric is a failure (**fail closed**)<br>比较四项 `GATE_METRICS`；通过率的下降按绝对值计算，成本/延迟按相对值计算；缺失的指标视为失败（**失败即关闭**） |
| `render_markdown(run, ...)` | sections: identity, Summary, Baseline gate, Judge calibration, Failure taxonomy, Cases; timestamp omitted unless `generated_at` is passed (byte-stable diffs)<br>各节依次为：标识、Summary（摘要）、Baseline gate（基线关卡）、Judge calibration（评审校准）、Failure taxonomy（失败分类）、Cases（用例）；除非传入 `generated_at`，否则省略时间戳（使 diff 逐字节稳定） |
| `write_report(path, run, **options)` | render and write, creating parents<br>渲染并写入，必要时创建父目录 |

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week07 -m week -q   # must pass
.\.venv\Scripts\ruff.exe check agentlab/evals                   # must be clean
```

```bash
# macOS / Linux
uv run pytest tests/week07 -m week -q   # must pass
uv run ruff check agentlab/evals        # must be clean
```

The suite is offline and deterministic; it must finish in a handful of seconds. Then produce the **lab artifact** (not tested, but the point of the week):

测试套件是离线且确定性的；必须在几秒钟内跑完。然后产出**实验产物**（不受测试覆盖，但这才是本周的重点）：

1. An eval set of **≥ 25 cases** (`data/evals/…jsonl`) for the agents you built in weeks 2–6, with deterministic checks where ground truth exists and rubrics only where it does not.

   为你在第 2–6 周构建的 Agent 准备一个包含 **≥ 25 个用例**的评测集（`data/evals/…jsonl`），有标准答案的地方用确定性检查，只有在没有标准答案时才使用评分标准。

2. A baseline report written from a real run, committed next to the dataset.

   一份基于真实运行生成的基线报告，与数据集放在一起提交。

3. Change one prompt deliberately, find **three regressions** the gate catches, and keep one as a permanent case.

   刻意修改一个提示词，找出关卡捕获到的**三个回归**，并把其中一个保留为永久用例。

4. Calibrate the judge on **20–30 human-labelled** items and quote agreement/κ next to every judge-based metric (≥ 80% raw agreement is the bar; report κ too).

   用 **20–30 条人工标注**的样本校准评审，并在每个基于评审的指标旁注明一致率/κ（原始一致率 ≥ 80% 是及格线；同时也要报告 κ）。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. **Re-read** research 03 §1.2 before writing any metric. `pass@1` is capability, `pass^k` is reliability; production cares about the second, and one repeat cannot measure it.

   在编写任何指标之前，**重读**研究文档 03 的 §1.2。`pass@1` 衡量能力，`pass^k` 衡量可靠性；生产环境关心的是后者，而只运行一次是无法度量它的。

2. The dataset header exists so a report can answer *which expectations produced this number*: include `format` and `version`, keep case ids stable.

   数据集头部的存在，是为了让报告能够回答*这个数字是由哪些预期产生的*：要包含 `format` 和 `version`，并保持用例 id 稳定。

3. For validation, accumulate into a list and join at the end — fail-fast validation shows the learner one problem per run and hides the rest.

   做校验时，把问题累积到一个列表中，最后再拼接起来——快速失败式的校验每次运行只向学习者展示一个问题，把其余问题都藏了起来。

4. The harness's ordering rule ("deterministic checks first") is observable: the judge provider's call log must be empty for a case whose check failed. Write that assertion before the implementation.

   harness 的顺序规则（「确定性检查优先」）是可观测的：对于检查失败的用例，评审 provider 的调用日志必须为空。在实现之前先写好这条断言。

5. Canonical JSON means `sort_keys=True` + compact separators + `ensure_ascii=False`; otherwise the digest changes when the environment does.

   规范化 JSON 指的是 `sort_keys=True` + 紧凑分隔符 + `ensure_ascii=False`；否则环境一变，摘要就会跟着变。

6. The gate compares **four** metrics. Ask what "missing baseline" should mean before deciding it is a pass — fail-safe systems treat unverifiable as failure.

   关卡比较的是**四项**指标。在认定「缺失基线」算通过之前，先想清楚它应该意味着什么——故障安全的系统会把无法验证视为失败。

7. Watch the boundary: "drop > 2 points fails" means exactly 2 points passes. Floating-point subtraction needs a tolerance, or `0.5 - 0.48` will surprise you.

   注意边界：「下降 > 2 个点即失败」意味着恰好下降 2 个点是通过的。浮点减法需要容差，否则 `0.5 - 0.48` 会让你大吃一惊。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| Every case hits `agent_error`<br>每个用例都触发 `agent_error` | the factory signature is `(case, tracer) -> AgentRun`; a factory that raises inside the test shows up as a failed trial by design<br>工厂函数的签名是 `(case, tracer) -> AgentRun`；按设计，在测试内抛出异常的工厂函数会表现为一次失败的试验 |
| Judge called for failing cases<br>失败的用例也调用了评审 | deterministic checks were not run first, or `all(...)` over an empty check list was treated as failure<br>没有先运行确定性检查，或者把对空检查列表执行 `all(...)` 的结果当成了失败 |
| `pass^k` always 0 with `repeats=1`<br>`repeats=1` 时 `pass^k` 总是 0 | `k` must equal the number of recorded trials; pass^k of 3 needs `repeats >= 3`<br>`k` 必须等于已记录的试验次数；k 为 3 的 pass^k 需要 `repeats >= 3` |
| Round-trip loses `checks`<br>往返读写后丢失了 `checks` | defaults were omitted on write but not re-applied on read (or vice versa); missing key means the default, not an error<br>写入时省略了默认值，但读取时没有重新应用（或者反过来）；缺失的键表示默认值，而不是错误 |
| Report changes between identical runs<br>相同的运行之间报告却发生了变化 | a wall-clock timestamp leaked into `render_markdown`; use `generated_at` explicitly<br>挂钟时间戳泄漏进了 `render_markdown`；应显式使用 `generated_at` |
| Gate passes a regression<br>关卡放过了一个回归 | a metric was compared as relative instead of absolute (pass rates are absolute), or a missing metric was defaulted to zero<br>某个指标被按相对值而非绝对值比较（通过率应按绝对值），或者缺失的指标被默认为零 |

## 7. SendOS bridge

**7. 与 SendOS 的衔接**

Read-only reference (SendOS repo): the learning loop this week miniatures.

只读参考（SendOS 仓库）：本周以迷你形式复刻的学习回路。

- `apps/Send.Usage.Collector/src/**/Domain/{OutcomeTraceEvent,OutcomeTraceEventType,OutcomeTraceLifecycleEvent}.cs` — append-only trace contract, closed event enum.

  `apps/Send.Usage.Collector/src/**/Domain/{OutcomeTraceEvent,OutcomeTraceEventType,OutcomeTraceLifecycleEvent}.cs` —— 只追加的 trace 契约，封闭的事件枚举。

- `apps/Send.LowerLayer.Worker/src/.../Evaluation/Evaluator.cs` — the five-dimension evaluator.

  `apps/Send.LowerLayer.Worker/src/.../Evaluation/Evaluator.cs` —— 五维度评估器。

- `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs` — evidence thresholds before a candidate is even proposed.

  `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs` —— 在候选项被提出之前就要满足的证据阈值。

- `apps/Send.LowerLayer.Worker/src/.../ControlPlane/PublishingPipeline/PublishingService.cs` — submit-only promotion; AI never reaches `Published` without a human approval row.

  `apps/Send.LowerLayer.Worker/src/.../ControlPlane/PublishingPipeline/PublishingService.cs` —— 只能提交的晋级流程；没有人工审批记录，AI 永远无法到达 `Published`。

- `docs/architecture/governance-architecture.md` §6b — the learning-loop governance contract.

  `docs/architecture/governance-architecture.md` §6b —— 学习回路的治理契约。

Answer in your weekly notes:

在你的每周笔记中回答：

1. Which parts of SendOS's evidence gate are *deterministic* and which require a judge? How does it keep the judge from becoming the system of record?

   SendOS 的证据关卡中哪些部分是*确定性*的，哪些需要评审？它是如何防止评审变成记录系统（system of record）的？

2. Your `EvalRun.metrics()` is a snapshot. What would you need to store to reproduce a publish decision months later — dataset digest, model version, judge version, something else?

   你的 `EvalRun.metrics()` 只是一个快照。要在几个月后复现一次发布决策，你需要存储什么——数据集摘要、模型版本、评审版本，还是其他东西？

3. SendOS attributes distillation insights to asset versions and drops unattributable ones. Where would your harness have to record the asset/prompt version to make the same claim?

   SendOS 会把蒸馏得到的洞察归因到资产版本上，并丢弃无法归因的洞察。你的 harness 需要在哪里记录资产/提示词版本，才能做出同样的断言？

## 8. Stretch (optional)

**8. 拓展（可选）**

- **OTel exporter**: map your `TraceEvent`s to OTel GenAI `invoke_agent` / `chat` / `execute_tool` spans (pin the semconv version!) and view one run in a local collector. Note every attribute you had to guess because the spec is still `Development`.

  **OTel 导出器**：把你的 `TraceEvent` 映射为 OTel GenAI 的 `invoke_agent` / `chat` / `execute_tool` span（要固定 semconv 版本！），并在本地 collector 中查看一次运行。记下每一个你不得不去猜的属性，因为该规范仍处于 `Development` 阶段。

- **Golden traces**: replay a sanitized production trace through the cassette provider as an eval fixture, and prove it fails on the prompt change that caused the incident.

  **黄金 trace**：把一条脱敏后的生产 trace 作为评测夹具，通过 cassette（录制回放）provider 重放，并证明它会在导致事故的那次提示词修改上失败。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** why is `pass^k` a better release gate than `pass@1`, and why can a single high `pass@1` number be actively misleading in a demo?

   **概念层面：** 为什么 `pass^k` 是比 `pass@1` 更好的发布关卡？为什么一个很高的 `pass@1` 数字在演示中反而可能产生误导？

2. **Architectural:** where should the judge run in your architecture so that its failures are visible and its cost is bounded — inside the harness, behind a provider seam, or as an offline batch job? What did your design choose, and what breaks if you choose differently?

   **架构层面：** 在你的架构中，评审应该在哪里运行，才能让它的失败可见、成本有界——在 harness 内部、在 provider 接缝之后，还是作为离线批处理任务？你的设计选择了哪种？如果选择不同，会有什么东西出问题？

3. **Transfer:** pick a non-AI system you own. What is its versioned dataset, its deterministic checks, and its pass^k equivalent? What would it take to add the missing one?

   **迁移应用：** 选一个你负责的非 AI 系统。它的带版本数据集、确定性检查以及 pass^k 的等价物分别是什么？要补上缺失的那一项需要做些什么？
