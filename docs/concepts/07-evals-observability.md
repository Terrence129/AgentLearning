# 07 — Evals and Observability

**07 — 评测与可观测性**

> **Week 7 · just-in-time concept note.** Read before the lab (~25 min). The lab asks you to build a dataset, harness, judge and CI gate — this note explains why reliability, not best-case quality, is the thing you are measuring. **Reads with:** [research 03 §1–2](../research/03-production-evals-ops.md) · **Lab:** `week07-evals`.
>
> **第 7 周 · 即时概念笔记。** 请在做实验（lab）之前阅读（约 25 分钟）。实验要求你构建一个数据集、一个评测 harness（运行框架）、一个评审和一道 CI 关卡——这篇笔记解释为什么你要衡量的是可靠性，而不是最佳情况下的质量。**配合阅读：** [研究 03 §1–2](../research/03-production-evals-ops.md) · **实验：** `week07-evals`。

## The failure mode this prevents

**这篇笔记要防止的失败模式**

You changed one sentence in the system prompt. The demo still looks great, so it ships. Two weeks later a customer shows the agent stopped calling the policy-check tool on refunds — the "tone-only" change had silently reordered tool selection. Nobody can reconstruct the failing turn: the trace recorded `step 4: failed` and a token count. Diagnosis cost: a week; exposure: unauthorised refunds.

你改了系统提示词里的一句话。演示看起来依然很棒，于是就上线了。两周后，一位客户指出 Agent 在处理退款时不再调用策略检查工具了——那个「只改语气」的改动悄无声息地改变了工具选择的顺序。没有人能还原出失败的那一轮：trace 里只记录了 `step 4: failed` 和一个 token 数。诊断成本：一周；风险敞口：未经授权的退款。

Evals make that change **fail in CI instead of production**; observability makes the **next** failure take ten minutes to diagnose.

评测（eval）让这种改动**在 CI 中失败，而不是在生产环境中失败**；可观测性则让**下一次**失败只需十分钟就能诊断出来。

## If you remember five things

**如果只记住五件事**

> 1. **pass@k is capability; pass^k is reliability.** Production needs the second one.
>
>    **pass@k 衡量的是能力；pass^k 衡量的是可靠性。** 生产环境需要的是后者。
>
> 2. **Deterministic checks before judges.** A judge is an instrument you calibrate, not an oracle.
>
>    **先做确定性检查，再用评审。** 评审是一件需要你去校准的仪器，而不是神谕。
>
> 3. **A prompt is a versioned artifact.** If you can't reconstruct a failed run's prompt, model, tools and state, you have logs, not observability.
>
>    **提示词是一个有版本的产物。** 如果你无法还原一次失败运行所用的提示词、模型、工具和状态，那你拥有的只是日志，而不是可观测性。
>
> 4. **OTel's GenAI conventions are the right schema but still `Development`** — and the spec moved to a new repository in 2026. Wrap them, pin them, expect renames.
>
>    **OTel 的 GenAI 语义约定是正确的 schema，但仍处于 `Development` 状态**——而且该规范在 2026 年迁移到了一个新的仓库。把它们封装起来，固定版本，并做好改名的准备。
>
> 5. **A metric without a failure taxonomy is a number, not a diagnosis.**
>
>    **没有失败分类体系的指标只是一个数字，而不是诊断。**

## The model in one page

**一页看懂模型**

### Outcome evals vs trajectory evals

**结果评测 vs 轨迹评测**

An **outcome eval** scores the final artifact (JSON, decision, DB state) — cheap, deterministic, necessary. A **trajectory eval** scores the path: tools called, order, arguments, policy. It is the only way to catch an agent that got the right answer for the wrong reason.

**结果评测**为最终产物打分（JSON、决策、数据库状态）——便宜、确定、必不可少。**轨迹评测**为路径打分：调用了哪些工具、顺序、参数、策略。只有它才能抓出那种「因为错误的理由得到了正确答案」的 Agent。

Score outcome first (objective); add trajectory assertions where the path *is* the product:

先给结果打分（客观）；在路径*本身就是*产品的地方，再加上轨迹断言：

| Dimension<br>维度 | Assertion<br>断言 | Catches<br>能捕获 |
|---|---|---|
| Tool selection<br>工具选择 | expected/forbidden tool sets<br>预期/禁止的工具集合 | capability creep, skipped policy checks<br>能力蔓延、跳过的策略检查 |
| Tool arguments<br>工具参数 | schema + business rules + tenant-ID equality<br>schema + 业务规则 + 租户 ID 一致性 | cross-tenant access, malformed actions<br>跨租户访问、格式错误的动作 |
| Policy compliance<br>策略合规 | rule engine over the trace<br>基于 trace 的规则引擎 | "approved" without an approval<br>没有审批却显示「已批准」 |
| Efficiency<br>效率 | steps, tokens, latency, retries<br>步数、token、延迟、重试 | silent cost regressions<br>悄无声息的成本回归 |

### pass@k vs pass^k, operationally

**pass@k 与 pass^k 的实际操作**

`pass@k` asks "did at least one of k samples work?" — a best-case capability number, and the one demos accidentally report. `pass^k` asks "did **all** k trials work?" — the reliability users experience. τ-bench introduced pass^k and found strong function-calling agents below 50% success with **pass^8 under 25%** in retail ([τ-bench](https://arxiv.org/abs/2406.12045), accessed 2026-10-18).

`pass@k` 问的是「k 次采样中是否至少有一次成功？」——这是一个最佳情况下的能力数字，也是演示时常常不经意报告出来的那个。`pass^k` 问的是「k 次试验是否**全部**成功？」——这才是用户实际体验到的可靠性。τ-bench 提出了 pass^k，并发现强大的函数调用 Agent 成功率低于 50%，在零售场景中 **pass^8 低于 25%**（[τ-bench](https://arxiv.org/abs/2406.12045)，访问于 2026-10-18）。

Run it like this:

具体这样做：

1. Run **k independent trials per case** (fresh process/context, not a resumed run).

   **每个用例运行 k 次独立试验**（全新的进程/上下文，而不是恢复之前的运行）。

2. `case_pass = all(trials)`; `pass^k = passing_cases / total_cases`, reported per category — a global average hides the category that regressed.

   `case_pass = all(trials)`；`pass^k = passing_cases / total_cases`，按类别分别报告——全局平均值会掩盖发生回归的那个类别。

3. Treat `p^k` (from single-trial success `p`) as a **planning estimate only**: trials correlate through shared prompts, caches and tools, so measure, don't infer. With `p = 0.90`, `p^5 ≈ 0.59`; with `p = 0.95`, `p^5 ≈ 0.77` — that is what "90% accurate" means to a customer.

   把 `p^k`（由单次试验成功率 `p` 推算）**仅当作规划用的估计值**：各次试验会通过共享的提示词、缓存和工具产生相关性，所以要实测，而不是推算。当 `p = 0.90` 时，`p^5 ≈ 0.59`；当 `p = 0.95` 时，`p^5 ≈ 0.77`——这就是「90% 准确」对客户而言的真实含义。

4. Budget `k × cases × tokens`: `k = 3` for PR gates, `k = 5–8` nightly; use batch APIs and caching.

   按 `k × cases × tokens` 做预算：PR 关卡用 `k = 3`，夜间运行用 `k = 5–8`；使用批处理 API 和缓存。

5. Report a confidence interval (Wilson or bootstrap over cases); with 25 cases it is wide, so gate on clear deltas and trends.

   报告置信区间（Wilson 区间，或对用例做 bootstrap）；只有 25 个用例时区间很宽，所以要基于明显的差值和趋势来设关卡。

Track **variance** too: which cases are flaky, which always fail. A flaky case is a bug report about non-determinism.

同时也要跟踪**方差**：哪些用例时好时坏（flaky），哪些总是失败。一个 flaky 用例就是一份关于不确定性的 bug 报告。

### Deterministic checks before judges

**先做确定性检查，再用评审**

Score in this order, stopping at the first applicable layer:

按以下顺序打分，在第一个适用的层级停下：

1. **State/artifact assertions** — final JSON schema, DB row, exit code, tool side effects.

   **状态/产物断言**——最终的 JSON schema、数据库行、退出码、工具的副作用。

2. **Rules over the trajectory** — policy compiled to predicates over trace events.

   **基于轨迹的规则**——把策略编译成针对 trace 事件的谓词。

3. **Reference comparisons** — exact/normalized match, numeric tolerance.

   **参考答案比对**——精确/归一化匹配、数值容差。

4. **LLM judge** — only for qualities with no ground truth (helpfulness, tone, prose groundedness).

   **LLM 评审**——仅用于没有标准答案的质量维度（有用性、语气、文字内容是否有据可依）。

### Judge calibration, concretely

**评审校准的具体做法**

The MT-Bench work documents **position, verbosity and self-enhancement bias plus limited reasoning**, while strong judges reach >80% agreement with humans — roughly human-human ([LLM-as-a-Judge](https://arxiv.org/abs/2306.05685), accessed 2026-10-18). Your week-7 gate is **agreement ≥ 80%** against your own labels. How:

MT-Bench 的研究记录了**位置偏差、冗长偏差、自我增强偏差以及有限的推理能力**，同时强评审与人类的一致率可达 80% 以上——大致相当于人与人之间的一致率（[LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)，访问于 2026-10-18）。你第 7 周的关卡是与你自己的标注**一致率 ≥ 80%**。做法如下：

1. **Atomic criteria** (0–2 each), forced JSON — not one holistic 1–10 score.

   **原子化的评判标准**（每项 0–2 分），强制输出 JSON——而不是一个笼统的 1–10 分总评。

2. **Label 30 items**, then re-label 10 blind a day later to measure your own consistency; keep the set fixed and versioned.

   **标注 30 条样本**，一天后在不看之前结果的情况下重新标注其中 10 条，以衡量你自己的一致性；保持这个集合固定并做版本管理。

3. Report **exact agreement and Cohen's κ**, plus a confusion matrix per criterion. Fix the criterion with the worst confusion — usually the vaguest one.

   报告**精确一致率和 Cohen's κ**，以及每项标准的混淆矩阵。先修正混淆最严重的那项标准——通常是最含糊的那一项。

4. **Control the biases:** swap order in pairwise judging and report flip rate; randomize length; don't let the generating model family judge its own output; strip decorative formatting.

   **控制偏差：** 在成对评审中交换顺序并报告翻转率；随机化长度；不要让生成内容的模型家族评审自己的输出；去掉装饰性的格式。

5. **Pin the judge model version** in every report; re-calibrate on any judge, rubric or agent change.

   在每份报告中**固定评审模型的版本**；评审、评分标准（rubric）或 Agent 有任何变动时都要重新校准。

6. **Cache the rubric prefix** — fixed-rubric judges can exceed 70% cache-hit rates ([OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18), making nightly judging affordable.

   **缓存评分标准前缀**——评分标准固定的评审，缓存命中率可以超过 70%（[OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)，访问于 2026-10-18），这让夜间评审的成本变得可以承受。

Below the bar, narrow the criterion or improve examples before trying a bigger judge.

如果达不到门槛，先收窄评判标准或改进示例，再考虑换一个更大的评审模型。

### The regression gate

**回归关卡**

Baseline in git, gate in CI:

基线放在 git 里，关卡放在 CI 里：

- **Quality:** fail if pass^k drops >2 points, or any category >5.

  **质量：** 如果 pass^k 下降超过 2 个百分点，或任一类别下降超过 5 个百分点，则失败。

- **Cost/latency:** fail if cost per successful task rises >15% or p95 latency >20%.

  **成本/延迟：** 如果每个成功任务的成本上升超过 15%，或 p95 延迟上升超过 20%，则失败。

- **Judge health:** fail if judge-human agreement falls below 80% — the judge drifted.

  **评审健康度：** 如果评审与人类的一致率跌破 80%，则失败——说明评审发生了漂移。

- **Taxonomy:** label every failing case `schema | tool_selection | tool_args | policy | retrieval | reasoning | timeout | budget` and report counts. This turns a red build into a fix.

  **分类体系：** 给每个失败用例打上 `schema | tool_selection | tool_args | policy | retrieval | reasoning | timeout | budget` 之一的标签，并报告各自的数量。这能把一次失败（红）的构建变成一次修复。

Golden traces are your highest-ROI fixtures: sanitize, freeze and replay on every prompt/model change.

黄金 trace 是投资回报率最高的测试夹具：脱敏、冻结，并在每次提示词/模型变更时回放。

### Trace data model

**Trace 数据模型**

Model each run as a trace of spans. OTel GenAI defines the vocabulary — `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool` via `gen_ai.operation.name` ([semconv agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18):

把每次运行建模为由多个 span 组成的一条 trace。OTel GenAI 通过 `gen_ai.operation.name` 定义了相关词汇——`invoke_agent`、`invoke_workflow`、`plan`、`execute_tool`（[semconv agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)，访问于 2026-10-18）：

| Span | Must record<br>必须记录 |
|---|---|
| `invoke_agent` | agent id/version, prompt id/version/hash, conversation id, tenant, stop reason<br>Agent ID/版本、提示词 ID/版本/哈希、会话 ID、租户、停止原因 |
| `chat` | provider, requested **and actual** model, temperature, input/output/cache tokens, finish reason, latency<br>模型提供商（provider）、请求的**以及实际使用的**模型、温度、输入/输出/缓存 token、结束原因、延迟 |
| `execute_tool` | tool, redacted args + hash, result size/status, `error.type`, idempotency key<br>工具、脱敏后的参数 + 哈希、结果大小/状态、`error.type`、幂等键 |
| `policy.evaluate` | decision, rule ids, authority snapshot version<br>决策、规则 ID、授权快照版本 |
| `approval.wait` | proposal id, binding hash, approver, expiry<br>提案 ID、绑定哈希、审批者、过期时间 |
| platform<br>平台 | `app.tenant.id`, `app.cost.usd`, `app.budget.remaining`, step index<br>`app.tenant.id`、`app.cost.usd`、`app.budget.remaining`、步骤序号 |

**Honest status of the spec.** The conventions are **not stable**: every agent span and attribute is marked `Development`, and in 2026 they **moved** to the dedicated `open-telemetry/semantic-conventions-genai` repository, extending core conventions via Weaver ([repo](https://github.com/open-telemetry/semantic-conventions-genai), accessed 2026-10-18). Names will change. The response is not "wait" but: adopt the semantics, **pin the version**, emit through **one internal telemetry module**, and never let dashboards or eval code bind raw attribute strings. Content attributes (`gen_ai.input.messages`, `gen_ai.output.messages`) are deliberately opt-in and PII-flagged — hash or redact by default.

**规范的真实状态。** 这些约定**并不稳定**：每一个 Agent span 和属性都被标记为 `Development`，并且在 2026 年它们**迁移**到了专门的 `open-telemetry/semantic-conventions-genai` 仓库，通过 Weaver 扩展核心约定（[仓库](https://github.com/open-telemetry/semantic-conventions-genai)，访问于 2026-10-18）。名称将来会变。正确的应对不是「等等再说」，而是：采纳其语义，**固定版本**，通过**一个内部遥测模块**统一输出，并且绝不让仪表盘或评测代码直接绑定原始属性字符串。内容类属性（`gen_ai.input.messages`、`gen_ai.output.messages`）被有意设计为需要主动开启，并标记为含 PII——默认应做哈希或脱敏处理。

**What makes a failed turn diagnosable.** Record: (1) exact prompt version hash, (2) actual model+provider served, (3) stop reason/`error.type`, (4) tokens including cache reads/writes, (5) tool args and truncated results with error status, (6) policy decisions with rule ids, (7) step index and remaining budget, (8) correlation ids across run, conversation, tenant and approval. Miss any and the trace says "what" but not "why".

**怎样让一次失败的轮次可诊断。** 记录：(1) 精确的提示词版本哈希，(2) 实际提供服务的模型 + 提供商，(3) 停止原因/`error.type`，(4) 包括缓存读写在内的 token，(5) 工具参数和截断后的结果及其错误状态，(6) 带规则 ID 的策略决策，(7) 步骤序号和剩余预算，(8) 贯穿运行、会话、租户和审批的关联 ID。缺了任何一项，trace 就只能告诉你「发生了什么」，而说不清「为什么」。

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>实际情况 |
|---|---|
| "pass@k 0.9 means a 90% reliable agent."<br>「pass@k 为 0.9 就意味着 Agent 有 90% 的可靠性。」 | A 90% single-trial rate; multi-step reliability is multiplicative — that is pass^k.<br>那只是 90% 的单次试验成功率；多步骤的可靠性是相乘的——那才是 pass^k。 |
| "A judge score is objective."<br>「评审分数是客观的。」 | A measurement with documented biases; without human-labelled calibration it is an opinion with a number.<br>它是一种存在已知偏差的测量；没有基于人工标注的校准，它只是一个带数字的观点。 |
| "More traces = observability."<br>「trace 越多 = 可观测性越好。」 | Traces without prompt/model versions, policy decisions and correlation ids are logs.<br>没有提示词/模型版本、策略决策和关联 ID 的 trace 只是日志。 |
| "We'll add evals once it stabilises."<br>「等它稳定下来我们再加评测。」 | Evals are how you learn it is stable; retrofitting hides which release broke what.<br>评测正是你得知它是否稳定的手段；事后补加会掩盖究竟是哪个版本弄坏了什么。 |

## How this shows up in SendOS

**这在 SendOS 中如何体现**

- **`Outcome_Trace` is the contract to copy.** A 21-event closed lifecycle in an insert-only store; a DB trigger denies `UPDATE`/`DELETE`, and events carry a monotonic `Sequence` (`apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs`, `.../Infrastructure/Persistence/EfCoreOutcomeTraceStore.cs`).

  **`Outcome_Trace` 是值得照搬的契约。** 它是一个由 21 种事件构成的封闭生命周期，存放在只允许插入的存储中；一个数据库触发器会拒绝 `UPDATE`/`DELETE`，并且事件带有单调递增的 `Sequence`（`apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs`、`.../Infrastructure/Persistence/EfCoreOutcomeTraceStore.cs`）。

- **The evaluator exists but is dark.** The 5-dimension evaluator — Correctness, PolicyCompliance, OutcomeAlignment, EvidenceGrounding, ExecutionQuality — is built and tested but **never called** (`apps/Send.LowerLayer.Worker/src/.../Evaluation/Evaluator.cs`; [research 05 §2.4](../research/05-sendos-concept-map.md)). Your harness miniatures the missing wiring.

  **评估器已经存在，但处于未启用状态。** 这个 5 维度评估器——Correctness、PolicyCompliance、OutcomeAlignment、EvidenceGrounding、ExecutionQuality——已经构建并经过测试，但**从未被调用**（`apps/Send.LowerLayer.Worker/src/.../Evaluation/Evaluator.cs`；[研究 05 §2.4](../research/05-sendos-concept-map.md)）。你的 harness 就是这段缺失接线的缩小版。

- **The evidence gate gives you starting thresholds.** `EligibleForCandidate ∧ sample ≥ 30 ∧ confidence ≥ 0.7 ∧ quality ≥ 0.5` (`.../Distillation/EvidenceGate.cs:24-35`) — reuse the numbers, interrogate the confidence definition.

  **证据关卡给了你起步用的阈值。** `EligibleForCandidate ∧ sample ≥ 30 ∧ confidence ≥ 0.7 ∧ quality ≥ 0.5`（`.../Distillation/EvidenceGate.cs:24-35`）——可以复用这些数字，但要追问置信度是如何定义的。

- **`TurnStage` is the diagnosis primitive.** 45 named stages, each `Ran`/`Skipped`/`Failed` with a reason (`.../Application/Runtime/TurnStage.cs:29-203`). SendOS has stage semantics but stubbed metrics/traces ([research 05 §5](../research/05-sendos-concept-map.md)) — exactly the gap an OTel exporter maps onto.

  **`TurnStage` 是诊断的基本单元。** 共有 45 个具名阶段，每个阶段的状态为 `Ran`/`Skipped`/`Failed` 之一并附带原因（`.../Application/Runtime/TurnStage.cs:29-203`）。SendOS 有阶段语义，但指标/trace 还只是桩实现（[研究 05 §5](../research/05-sendos-concept-map.md)）——这正是 OTel 导出器要填补的空白。

## Check yourself

**自我检查**

1. Your agent succeeds 85% per trial on a 4-trial task. What does pass^4 tell you, and why is `0.85^4` only an estimate?

   你的 Agent 在一个 4 次试验的任务上单次成功率为 85%。pass^4 告诉了你什么？为什么 `0.85^4` 只是一个估计值？

2. Which eval cases must be deterministic, and which genuinely need a judge?

   哪些评测用例必须是确定性的？哪些真正需要评审？

3. Your judge agrees with you 72% of the time. Fix the judge model, the rubric, or your labels — in what order, and why?

   你的评审与你的一致率为 72%。修正评审模型、评分标准还是你的标注——按什么顺序？为什么？

4. A failed run's trace shows the final error but no prompt hash. Which two questions can you no longer answer?

   一次失败运行的 trace 显示了最终错误，但没有提示词哈希。哪两个问题你将再也无法回答？

5. Why doesn't `Development` status justify waiting, and what must you build instead?

   为什么 `Development` 状态不能成为等待的理由？你必须转而构建什么？

## Reading

**阅读材料**

- [τ-bench](https://arxiv.org/abs/2406.12045) — pass^k origin and what reliability failure looks like.

  [τ-bench](https://arxiv.org/abs/2406.12045)——pass^k 的出处，以及可靠性失败是什么样子。

- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) — the bias catalogue you calibrate against.

  [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)——你在校准时要对照的偏差目录。

- [OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) — span/attribute vocabulary and its `Development` status.

  [OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)——span/属性词汇表及其 `Development` 状态。

- [Research 03 §1–2](../research/03-production-evals-ops.md) — the full eval and observability map.

  [研究 03 §1–2](../research/03-production-evals-ops.md)——完整的评测与可观测性全景图。

- **Companion book:** *AI Agents in Depth* v2.0, ch.7 §7.2, §7.5, §7.7–7.8 — pass@k vs pass^k, judge methods, failure attribution in trajectories, statistical significance, and observability. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 7 章 §7.2、§7.5、§7.7–7.8——pass@k 与 pass^k、评审方法、轨迹中的失败归因、统计显著性，以及可观测性。[章节地图](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
