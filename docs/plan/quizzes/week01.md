# Week 1 Quiz — The Model, Demystified

**第 1 周测验 — 揭开模型的神秘面纱**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10. This quiz feeds the "Explain" gate in [`CHECKPOINTS.md`](../CHECKPOINTS.md).

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。本测验计入 [`CHECKPOINTS.md`](../CHECKPOINTS.md) 中的「Explain（讲解）」关卡。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** Your agent sends a 12,000-token prompt and the model replies with `finish_reason: "length"`. What happened?

你的 Agent 发送了一个 12,000 token 的提示词，模型返回了 `finish_reason: "length"`。发生了什么？

- A) The model refused for safety reasons

  模型出于安全原因拒绝了

- B) Generation hit the `max_tokens` cap before finishing

  生成在完成之前触到了 `max_tokens` 上限

- C) The request exceeded the context window

  请求超出了上下文窗口

- D) The provider rate-limited the request

  模型提供商（provider）对该请求进行了限流

**Q2.** Which failure should **not** be retried automatically inside the provider adapter?

哪种失败**不应**在提供商适配器内部自动重试？

- A) HTTP 429 with `Retry-After: 2`

  带有 `Retry-After: 2` 的 HTTP 429

- B) HTTP 503 from the model gateway

  来自模型网关的 HTTP 503

- C) HTTP 400 "invalid tool schema"

  HTTP 400「invalid tool schema」（工具 schema 无效）

- D) `httpx.ConnectError` (transient connection reset)

  `httpx.ConnectError`（瞬时的连接重置）

**Q3.** Why must the adapter apply exponential backoff **with jitter** rather than a fixed `time.sleep(1)`?

为什么适配器必须使用**带抖动（jitter）的**指数退避，而不是固定的 `time.sleep(1)`？

- A) Jitter makes the request cheaper

  抖动让请求更便宜

- B) Fixed delays are illegal under provider terms

  按提供商条款，固定延迟是不允许的

- C) Without randomness, many clients retry in lockstep and amplify the outage

  没有随机性的话，大量客户端会步调一致地重试，从而放大故障

- D) Backoff is required for SSE parsing to work

  SSE 解析必须依赖退避才能工作

**Q4.** A streaming response delivers tool-call arguments as many small deltas. What is the correct handling?

一个流式响应把工具调用参数拆成许多小的增量（delta）下发。正确的处理方式是什么？

- A) Send each delta to the tool immediately

  立即把每个增量发送给工具

- B) Accumulate deltas per `tool_call.id`, then parse the complete JSON before executing

  按 `tool_call.id` 累积增量，在执行之前解析完整的 JSON

- C) Disable streaming when tools are present

  存在工具时禁用流式输出

- D) Parse each delta as JSON and merge dictionaries

  把每个增量都当作 JSON 解析，然后合并字典

**Q5.** Which statement best describes the purpose of a **provider seam**?

哪种说法最能描述 **provider 接缝（seam）** 的作用？

- A) It caches prompts to reduce cost

  它缓存提示词以降低成本

- B) It is the single interface behind which provider-specific wire formats, retries and parsing live

  它是唯一的接口，提供商特有的传输格式、重试和解析逻辑都隐藏在它背后

- C) It validates structured output against JSON Schema

  它根据 JSON Schema 校验结构化输出

- D) It enforces the per-run budget

  它强制执行每次运行的预算

**Q6.** You want maximum reproducibility for a regression test against a live model. Which settings fit best?

你希望针对真实模型的回归测试具备最大的可复现性。哪组设置最合适？

- A) `temperature=1.0, top_p=1.0`
- B) `temperature=0.0` (and leave `top_p` at its default), plus a recorded cassette

  `temperature=0.0`（`top_p` 保持默认值），再加上一个录制好的 cassette（录制回放）

- C) `temperature=0.0, top_p=0.0`
- D) `max_tokens=1`

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** In two sentences: why do retries belong **inside** the provider adapter rather than in the calling agent loop?

用两句话回答：为什么重试应该放在提供商适配器**内部**，而不是放在调用它的 Agent 循环里？

**Q8.** What per-call measurement does the provider adapter return, and where does latency get recorded instead? Why the split?

提供商适配器在每次调用时返回什么度量数据？延迟又是在哪里记录的？为什么要这样拆分？

**Q9.** Prompt caching rewards a specific prompt layout. State the rule and give one practical consequence for an agent whose system prompt contains the current date and time.

提示词缓存偏好一种特定的提示词布局。说明这条规则，并针对一个系统提示词中包含当前日期和时间的 Agent，给出一个实际后果。

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This retry helper is used for every model call. It "works" in demos. List **three** defects and give the minimal corrected behaviour.

下面这个重试辅助函数被用于每一次模型调用。它在演示中「能用」。列出**三个**缺陷，并给出最小限度的修正后行为。

```python
def complete_with_retry(payload, attempts=3):
    for _ in range(attempts):
        try:
            return http.post(API_URL, json=payload)
        except Exception:
            time.sleep(1)
    raise RuntimeError("model call failed")
```

---

## Answers and explanations (do not read until you have attempted all 10)

**答案与解析（请先完成全部 10 道题再看）**

**Q1 — B.** `finish_reason: "length"` means the output hit `max_tokens` (or the provider's output cap); the prompt itself fitted. A context-window overflow is usually rejected before generation (400) or truncates the input. Safety refusals surface as `content_filter` or a refusal message. *Why it matters: the loop must branch on `finish_reason`, not assume "any response means done".*

`finish_reason: "length"` 表示输出触到了 `max_tokens`（或提供商的输出上限）；提示词本身是放得下的。上下文窗口溢出通常会在生成之前就被拒绝（400），或者导致输入被截断。安全拒绝则表现为 `content_filter` 或一条拒绝消息。*为什么重要：循环必须根据 `finish_reason` 分支处理，而不能假设「有响应就代表完成」。*

**Q2 — C.** 400-level errors caused by malformed requests are terminal; retrying repeats the same invalid request and burns budget. 429/503/transport errors are retryable. *Why it matters: an error taxonomy is the adapter's contract.*

由请求格式错误引起的 400 级错误是终结性的；重试只会重复同一个无效请求并白白消耗预算。429/503/传输层错误则是可重试的。*为什么重要：错误分类体系就是适配器的契约。*

**Q3 — C.** Jitter spreads retries; synchronised retries create a thundering herd and prolong the outage. Backoff also gives the provider time to recover. *Why it matters: retry storms are self-inflicted incidents.*

抖动把重试分散开；同步的重试会造成惊群效应（thundering herd），延长故障时间。退避还能给提供商留出恢复的时间。*为什么重要：重试风暴是自己制造的事故。*

**Q4 — B.** Tool arguments can be split mid-string across chunks, so per-delta JSON parsing fails. Accumulate by `tool_call.id`, then validate complete arguments. *Why it matters: this is the most common streaming bug in hand-written adapters.*

工具参数可能在字符串中间被切分到不同的数据块里，所以逐个增量解析 JSON 会失败。应按 `tool_call.id` 累积，然后校验完整的参数。*为什么重要：这是手写适配器中最常见的流式输出 bug。*

**Q5 — B.** The seam hides provider differences (payload shape, error codes, SSE framing, auth) behind one protocol, which also enables mocks and later budget-aware routing. It does not itself cache, validate schemas or enforce budgets. *Why it matters: the seam is the basis of testability and provider flexibility.*

接缝把提供商之间的差异（payload 结构、错误码、SSE 分帧、鉴权）隐藏在一个统一协议之后，这也使得 mock 以及后续按预算感知的路由成为可能。它本身并不负责缓存、校验 schema 或强制执行预算。*为什么重要：接缝是可测试性和提供商灵活性的基础。*

**Q6 — B.** `temperature=0` is the closest thing to determinism a hosted model offers; `top_p=0` is invalid/undefined behaviour territory and should be left alone. Even at `temperature=0`, providers are not bit-reproducible, so a cassette is what makes the test stable. *Why it matters: tests must be deterministic even when models are not.*

`temperature=0` 是托管模型所能提供的最接近确定性的设置；`top_p=0` 属于无效或未定义行为的范畴，不应去动它。即使在 `temperature=0` 下，提供商也无法做到逐比特可复现，所以真正让测试稳定的是 cassette。*为什么重要：即使模型不是确定性的，测试也必须是确定性的。*

**Q7 — model answer.** Retry policy depends on provider-specific signals (`Retry-After`, 429 vs 400, SSE mid-stream failures) that only the adapter understands; putting it in the loop makes every caller reimplement it and lets it interact wrongly with loop-level budgets and step accounting. One seam also means one place to count retries and cost.

**参考答案。** 重试策略依赖于只有适配器才理解的提供商特有信号（`Retry-After`、429 与 400 的区别、SSE 流中途失败）；把它放进循环会让每个调用方都得重新实现一遍，还会让它与循环层面的预算和步数统计产生错误的相互影响。只有一个接缝，也意味着只有一个地方来统计重试次数和成本。

**Q8 — model answer.** The adapter returns a `CompletionResponse` carrying `Usage` (input/output/cached tokens) plus `finish_reason`, `model` and the raw payload; `Usage` is what cost accounting and budget enforcement consume. `CompletionResponse` has no latency field — wall-clock time is measured by the *caller's* span, and in this repo the week-2 loop emits a `model_call` trace event whose `duration_ms` comes from `Tracer.span(...)`. The split keeps the adapter stateless with respect to timing (a timer inside a retrying adapter would double-count retry and stream waits) while latency stays a property of the observed call in a run.

**参考答案。** 适配器返回一个 `CompletionResponse`，其中包含 `Usage`（输入 / 输出 / 缓存 token），以及 `finish_reason`、`model` 和原始 payload；成本核算和预算控制使用的就是 `Usage`。`CompletionResponse` 没有延迟字段——墙钟时间由*调用方*的 span 来测量，在本仓库中，第 2 周的循环会发出一个 `model_call` trace 事件，其 `duration_ms` 来自 `Tracer.span(...)`。这样拆分可以让适配器在计时方面保持无状态（在会重试的适配器内部计时，会把重试和流式等待重复计算），同时让延迟作为一次运行中被观测调用的属性。

**Q9 — model answer.** Put stable content first and volatile content last: an identical prefix is what gets cached. If the system prompt embeds the current timestamp, the prefix changes every call and the cache never hits; move the timestamp into the last user/tool message (or round it to a longer bucket).

**参考答案。** 稳定的内容放在前面，易变的内容放在最后：被缓存的是完全相同的前缀。如果系统提示词中嵌入了当前时间戳，前缀每次调用都会变化，缓存永远不会命中；应把时间戳移到最后一条 user / tool 消息里（或者把它取整到更粗的时间粒度）。

**Q10 — model answer.** Three defects: (1) it retries **all** exceptions, including terminal 400/auth errors; (2) it uses a fixed 1-second delay with no exponential growth and no jitter; (3) it ignores `Retry-After` and never logs/limits attempts. Bonus: it returns the raw response object without status/error-taxonomy mapping. Minimal fix: classify the exception, retry only retryable classes, sleep `max(Retry-After, base * 2**attempt + random jitter)` with a cap, and raise a typed error after the final attempt.

**参考答案。** 三个缺陷：(1) 它会重试**所有**异常，包括终结性的 400 / 鉴权错误；(2) 它使用固定的 1 秒延迟，既没有指数增长也没有抖动；(3) 它忽略了 `Retry-After`，并且从不记录日志或限制尝试。附加：它直接返回原始响应对象，没有做状态码 / 错误分类映射。最小修复：对异常进行分类，只重试可重试的类别，按 `max(Retry-After, base * 2**attempt + random jitter)` 休眠并设置上限，在最后一次尝试之后抛出带类型的错误。
