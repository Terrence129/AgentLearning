# 01 — The Agent Loop

**01 — Agent 循环**

> **Weeks 1–2 · just-in-time concept note.** Read before the labs (~25 min): [provider seam](../../labs/week01-provider/README.md), then [agent loop](../../labs/week02-agent-loop/README.md). You do not need framework knowledge. You need to know exactly what goes over the wire, where state lives, and how the loop stops.
>
> **第 1–2 周 · 即时概念笔记。** 在做实验前阅读（约 25 分钟）：先做 [provider 接缝](../../labs/week01-provider/README.md)，再做 [Agent 循环](../../labs/week02-agent-loop/README.md)。你不需要了解任何框架。你需要确切知道哪些内容会通过网络传输、状态存放在哪里，以及循环如何停止。

## The failure mode this prevents

**本机制防止的失败模式**

An agent that never ends, and a bill that does. A task starts looping: the model keeps calling the same search tool, each result is appended to the transcript, every iteration grows the context and costs money. Nothing checks steps, tokens, dollars or repeated calls, so after forty iterations you have a 180k-token transcript, a `$6` charge on a `$0.50`-budget task, and no answer — and because you logged only the final response, you cannot say which step went wrong. The second version of the same bug is quieter: the model asks for a tool (`finish_reason="tool_calls"`), your code reads `response.text` (empty), treats it as the final answer, and the agent replies nothing. The third is a retry storm: a 429 is caught inside the loop and the *whole step* — model call plus tool side effect — is retried, so the write happens twice.

一个永远不会结束的 Agent，以及一张终究会寄到的账单。某个任务开始陷入循环：模型不停地调用同一个搜索工具，每个结果都被追加到对话记录（transcript）中，每次迭代都让上下文变大、花掉更多钱。没有任何东西检查步数、token、美元花费或重复调用，于是四十次迭代之后，你得到一份 180k token 的对话记录、一个预算 `$0.50` 的任务被收了 `$6`，而且没有答案——又因为你只记录了最终响应，你根本说不出是哪一步出了问题。同一个 bug 的第二种形态更隐蔽：模型请求调用工具（`finish_reason="tool_calls"`），你的代码读取 `response.text`（为空），把它当成最终答案，结果 Agent 什么也没回复。第三种是重试风暴：一个 429 在循环内部被捕获，于是*整个步骤*——模型调用加上工具副作用——都被重试，写操作就执行了两次。

Weeks 1–2 make these structurally impossible: a typed provider seam that owns retries, a loop that checks budgets at the top of every iteration, tool errors fed back as observations, and a trace that records every step.

第 1–2 周会让这些问题在结构上不可能发生：一个负责重试的强类型 provider 接缝（seam），一个在每次迭代开头检查预算的循环，作为观察结果回传的工具错误，以及一份记录每一步的 trace。

## If you remember five things

**如果只记住五件事**

> 1. **The model is stateless.** One call is `(messages, tools) → one assistant message`. The conversation lives in *your* loop, not in the provider.
>
>    **模型是无状态的。** 一次调用就是 `(messages, tools) → one assistant message`。对话存在于*你的*循环中，而不在模型提供商（provider）那里。
>
> 2. **`finish_reason` is a control signal, not metadata.** `stop` ends; `tool_calls` dispatches; `length` means truncated; `content_filter` is a policy stop; `error` is retryable or not depending on the error class.
>
>    **`finish_reason` 是控制信号，而不是元数据。** `stop` 表示结束；`tool_calls` 表示分派工具；`length` 表示被截断；`content_filter` 是策略性停止；`error` 是否可重试取决于错误类别。
>
> 3. **Budgets belong at the top of the iteration** (`steps`, tokens in/out, USD, wall clock), and a no-progress detector is worth more than a bigger `max_steps`.
>
>    **预算检查应放在迭代的开头**（`steps`、输入/输出 token、美元、挂钟时间），而一个“无进展”检测器比更大的 `max_steps` 更有价值。
>
> 4. **Tool failures are observations, not exceptions.** The model sees `ERROR: ...` text as a tool message and can recover; a raised exception usually cannot.
>
>    **工具失败是观察结果，而不是异常。** 模型会把 `ERROR: ...` 文本当作一条工具消息看到，并且能够恢复；而抛出的异常通常无法恢复。
>
> 5. **Streaming is a transport protocol and it is not resumable.** Tool-call arguments arrive as fragments; a broken stream is retried as a new request, not replayed.
>
>    **流式输出是一种传输协议，而且不可续传。** 工具调用的参数以片段形式到达；中断的流会作为一个新请求重试，而不是重放。

## The model in one page

**一页看懂模型**

### What actually goes over the wire

**网络上实际传输的是什么**

Every provider you will meet — OpenAI, DeepSeek, Anthropic behind a thin adapter — reduces to four roles and two link fields ([`agentlab/types.py`](../../agentlab/types.py)):

你会遇到的每一个提供商——OpenAI、DeepSeek，以及包在一层薄适配器后面的 Anthropic——都可以归结为四种角色和两个关联字段（[`agentlab/types.py`](../../agentlab/types.py)）：

| Role<br>角色          | Contains<br>包含内容                                             | Required link<br>必需的关联                                         |
| ------------- | ---------------------------------------------------- | ----------------------------------------------------- |
| `system`    | instructions, policy, tool guidance<br>指令、策略、工具使用指引                  | —                                                    |
| `user`      | the task or follow-up<br>任务或后续追问                                | —                                                    |
| `assistant` | text and/or `tool_calls` (content may be `null`)<br>文本和/或 `tool_calls`（content 可能为 `null`） | —                                                    |
| `tool`      | one result per requested call<br>每个被请求的调用对应一个结果                        | `tool_call_id` matching the assistant's call `id`<br>`tool_call_id` 与 assistant 调用的 `id` 相匹配 |

The linkage matters more than it looks. An assistant turn that only calls tools has no text; the next request must contain a `tool` message for **every** `tool_call_id`, or the provider rejects the turn (and some providers accept it while silently losing the result). Tool arguments arrive as a JSON **string** that you parse and validate at the provider/tool boundary — `agentlab.providers.base.parse_tool_arguments` is the seam.

这种关联比看上去更重要。一个只调用工具的 assistant 轮次没有文本；下一个请求必须为**每一个** `tool_call_id` 都包含一条 `tool` 消息，否则提供商会拒绝该轮次（有些提供商会接受，但会悄无声息地丢掉结果）。工具参数以 JSON **字符串**的形式到达，你需要在 provider/工具边界上对其进行解析和校验——`agentlab.providers.base.parse_tool_arguments` 就是这个接缝。

### The loop is a state machine, not a `while True`

**循环是一个状态机，而不是一个 `while True`**

```python
while True:
    budget.assert_ok(what="run")  # steps/tokens/$ checked BEFORE spending
    tracer.emit("step", "iteration", {"n": budget.steps})
    resp = provider.complete(request)  # seam owns retries, usage, finish_reason
    budget.charge(resp.model, resp.usage)
    transcript.append(resp.message)  # assistant turn (possibly tool calls)
    if not resp.wants_tools:  # stop | length | content_filter
        return AgentResult(answer=resp.text, stop_reason=resp.finish_reason)
    for call in resp.tool_calls:  # parallel calls: one message each
        result = registry.invoke(call.name, call.arguments)  # never raises
        transcript.append(Message.tool_result(call.id, result.as_observation()))
        tracer.emit("tool_result", call.name, {"ok": result.ok, "truncated": result.truncated})
```

That is the whole of week 2's `agentlab/loop/react.py` plus `runner.py`. The interesting engineering is in what surrounds it:

这就是第 2 周 `agentlab/loop/react.py` 加上 `runner.py` 的全部内容。真正有意思的工程在于它周围的东西：

- **Stop conditions** are composable (`agentlab/loop/stop.py`): final answer, `max_steps`, any budget ceiling, and no-progress. Fingerprint `(tool_name, canonical_json(args))` plus a hash of the observable state; if the fingerprint repeats with no state delta, terminate with `stop_reason="stuck"` and the partial result.

  **停止条件**是可组合的（`agentlab/loop/stop.py`）：最终答案、`max_steps`、任意预算上限，以及无进展。对 `(tool_name, canonical_json(args))` 加上可观察状态的哈希值计算指纹；如果指纹重复出现且状态没有变化，就以 `stop_reason="stuck"` 终止，并返回部分结果。

- **Partial results on failure.** `MaxStepsExceeded` and `BudgetExceeded` are normal outcomes in a platform: return the work done, the steps taken and the stop reason. A production agent that fails with "step limit" is debuggable; one that raises `RuntimeError` is not.

  **失败时返回部分结果。** 在平台中，`MaxStepsExceeded` 和 `BudgetExceeded` 都是正常的结果：返回已完成的工作、已执行的步骤和停止原因。一个以“达到步数上限”失败的生产 Agent 是可调试的；一个抛出 `RuntimeError` 的则不是。

- **Trace before you optimise.** From week 2, every run emits `run_start`, `step`, `model_call`, `tool_call`, `tool_result`, `run_end` through [`agentlab/trace.py`](../../agentlab/trace.py). These are the same events your week 7 eval harness and a future OTel exporter consume.

  **先追踪，再优化。** 从第 2 周开始，每次运行都会通过 [`agentlab/trace.py`](../../agentlab/trace.py) 发出 `run_start`、`step`、`model_call`、`tool_call`、`tool_result`、`run_end` 事件。你第 7 周的评测 harness（运行框架）以及未来的 OTel 导出器消费的正是这些事件。

### `finish_reason`: five values, five behaviours

**`finish_reason`：五个取值，五种行为**

| Value<br>取值              | Meaning<br>含义                       | Loop behaviour<br>循环行为                                                                                        |
| ------------------ | ----------------------------- | ----------------------------------------------------------------------------------------------------- |
| `stop`           | model finished the turn<br>模型结束了本轮       | return answer<br>返回答案                                                                                         |
| `tool_calls`     | model wants tools<br>模型需要调用工具             | dispatch, append results, continue<br>分派、追加结果、继续                                                                    |
| `length`         | hit `max_tokens` mid-output<br>输出途中触及 `max_tokens` | repair: continue with "resume" instruction, or fail loudly — never accept truncated JSON as complete<br>修复：用“继续”指令接着生成，或者明确地失败——绝不把被截断的 JSON 当作完整结果接受 |
| `content_filter` | provider refused<br>提供商拒绝了              | terminal policy outcome; surface it, do not retry the same prompt<br>终止性的策略结果；把它暴露出来，不要用同一个提示词重试                                     |
| `error`          | transport/parse issue<br>传输/解析问题         | adapter-level retry or raise `ProviderError`<br>在适配器层重试，或抛出 `ProviderError`                                                        |

### Why the harness dominates the model

**为什么 harness 比模型更重要**

Same model, different loop, different reliability. SWE-agent's central result was that the **agent–computer interface** — command set, feedback format, guardrails — materially changed benchmark outcomes independent of the model ([arXiv:2405.15793](https://arxiv.org/abs/2405.15793)); Anthropic's tool-writing work reports the same for tool descriptions ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)). The 2026 survey formalises it: an agent is "a foundation model coupled with an execution harness", and quality emerges from observation, context, control, action, state and verification together ([arXiv:2606.20683](https://arxiv.org/abs/2606.20683)). Your week-2 loop is small, but all six duties are present — which is why you build it instead of importing one.

同样的模型，不同的循环，就有不同的可靠性。SWE-agent 的核心结论是：**Agent–计算机接口**——命令集、反馈格式、护栏——在与模型无关的情况下实质性地改变了基准测试结果（[arXiv:2405.15793](https://arxiv.org/abs/2405.15793)）；Anthropic 关于编写工具的研究在工具描述上也报告了同样的现象（[Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)）。2026 年的综述将其形式化：Agent 是“一个基础模型与一个执行 harness 的结合”，而质量来自观察、上下文、控制、行动、状态和验证的共同作用（[arXiv:2606.20683](https://arxiv.org/abs/2606.20683)）。你第 2 周的循环很小，但这六项职责一应俱全——这正是你要亲手构建它、而不是导入现成实现的原因。

### Streaming, caching, retries

**流式输出、缓存、重试**

- **Streaming** is SSE frames of text deltas plus tool-call fragments keyed by index, with usage often arriving only in the final chunk. You implement a parser that tolerates fragmented frames and prove the property `assemble_stream(stream(req)) == complete(req)` — the same invariant [`agentlab/providers/base.py`](../../agentlab/providers/base.py) documents. Streaming is not a UI nicety: it is how you get time-to-first-token down and how the model API models long outputs.

  **流式输出**由承载文本增量（delta）的 SSE 帧和按索引组织的工具调用片段组成，而用量（usage）信息往往只在最后一个分块中到达。你要实现一个能容忍碎片化帧的解析器，并证明 `assemble_stream(stream(req)) == complete(req)` 这一性质——也就是 [`agentlab/providers/base.py`](../../agentlab/providers/base.py) 中记录的同一个不变式。流式输出不是 UI 上的锦上添花：它是降低首 token 时间的手段，也是模型 API 表达长输出的方式。

- **Streams are not resumable.** The MCP 2026-07-28 revision removed stream resumability for the same reason ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)); assume any long-lived response can die and design re-issue, not replay.

  **流不可续传。** MCP 2026-07-28 修订版出于同样的原因移除了流的可续传性（[changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)）；要假定任何长时间存活的响应都可能中断，并设计重新发起请求，而不是重放。

- **Prompt caching** rewards a stable prefix: system prompt → tool definitions → few-shot → history. Put volatile content (timestamps, run IDs, retrieved chunks) at the end; track `Usage.cached_input_tokens` so you can see whether caching is actually working. Token accounting is a first-class feature, not a nice-to-have.

  **提示词缓存**奖励稳定的前缀：系统提示词 → 工具定义 → 少样本示例 → 历史记录。把易变内容（时间戳、运行 ID、检索到的片段）放在最后；跟踪 `Usage.cached_input_tokens`，这样你才能看到缓存是否真的生效。token 计量是一等功能，而不是可有可无的附加项。

- **Retries belong in the adapter**: 429 with `Retry-After`, 5xx, transport errors, exponential backoff with jitter; never retry a 400/401/403. The loop never sees a vendor error code. Model calls are safe to retry (they are reads); **tool calls are not** — that is why tools need idempotency keys and write tools need approvals (note 02 and week 8).

  **重试应放在适配器中**：带 `Retry-After` 的 429、5xx、传输错误，使用带抖动（jitter）的指数退避；绝不重试 400/401/403。循环永远不会看到厂商的错误码。模型调用可以安全地重试（它们是读操作）；**工具调用则不行**——这就是为什么工具需要幂等键，而写工具需要审批（见笔记 02 和第 8 周）。

### Surviving many context windows

**跨越多个上下文窗口而存续**

Compaction keeps a single run alive, but it is not memory: each new session still starts blank. Anthropic's long-running harness adds the missing half — an *initializer* session that writes `init.sh`, a progress file, a JSON feature list and a first git commit, then *coding* sessions that read progress + git log, pick one feature, and finish by committing and updating progress ([Anthropic, 2025-11-26](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). Note 03 makes this concrete; for now, notice that "state" is a file and git history, not a clever prompt.

压缩（compaction）能让单次运行维持下去，但它不是记忆：每个新会话仍然从空白开始。Anthropic 的长时运行 harness 补上了缺失的另一半——先由一个*初始化*会话编写 `init.sh`、一个进度文件、一份 JSON 功能列表并完成第一次 git 提交，随后的*编码*会话读取进度和 git log，挑选一个功能，最后提交代码并更新进度（[Anthropic, 2025-11-26](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)）。笔记 03 会把这一点具体化；眼下只需注意：“状态”是一个文件加上 git 历史，而不是一段巧妙的提示词。

## Common misconceptions

**常见误解**

| Misconception<br>误解                           | Reality<br>现实                                                                                                                            |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| "The model remembers the conversation."<br>“模型会记住对话。” | It does not. You resend the whole transcript every call; that is why context size is a budget.<br>它不会。每次调用你都要重新发送整份对话记录；这就是上下文大小是一种预算的原因。                                     |
| "A tool exception should propagate."<br>“工具异常应该向上传播。”    | Tool-level failures are observations. Raise only for bugs you cannot represent (e.g. `KeyboardInterrupt`).<br>工具层面的失败是观察结果。只在出现无法表示的 bug 时才抛出异常（例如 `KeyboardInterrupt`）。                       |
| "Streaming is a UI feature."<br>“流式输出是一个 UI 功能。”            | It is the wire format for deltas, including fragmented tool-call arguments. Reassembly and equivalence are testable contracts.<br>它是增量的传输格式，包括碎片化的工具调用参数。重组与等价性都是可测试的契约。     |
| "More steps means a thorough agent."<br>“步数越多，Agent 越周全。”    | More steps means more cost, more context and more ways to loop. Effort should scale with task complexity, not with hope.<br>步数越多意味着成本越高、上下文越多、陷入循环的方式也越多。投入应随任务复杂度增长，而不是随期望增长。           |
| "Retries are generic middleware."<br>“重试是通用的中间件。”       | While-loop retries duplicate side effects. Retries belong in the adapter for model calls; tool writes need idempotency + approval.<br>在 while 循环中重试会重复产生副作用。模型调用的重试应放在适配器中；工具写操作需要幂等 + 审批。 |
| "The harness is boilerplate."<br>“harness 只是样板代码。”           | It is the product. Two teams on the same model can differ several-fold on task success because of loop, tool and context design.<br>它就是产品本身。使用同一模型的两个团队，可能因为循环、工具和上下文设计的不同，在任务成功率上相差数倍。   |

## How this shows up in SendOS

**在 SendOS 中如何体现**

- **The provider seam already exists.** `apps/Send.Model.Adapter` (reached through `ISpecialistReasoner`) is `agentlab/providers/base.py` at enterprise scale: provider-independent completion, schema-validated output, budget-aware routing, retries and cost accounting behind one interface ([research 05 §2.2](../research/05-sendos-concept-map.md)). Yours is deliberately synchronous and simpler; the seam is the lesson.

  **provider 接缝已经存在。** `apps/Send.Model.Adapter`（通过 `ISpecialistReasoner` 访问）就是企业规模版的 `agentlab/providers/base.py`：与提供商无关的补全、经 schema 校验的输出、感知预算的路由、重试和成本核算，全部位于同一个接口之后（[research 05 §2.2](../research/05-sendos-concept-map.md)）。你的版本有意做成同步且更简单的；要学的正是这个接缝。

- **The loop is the same machine, governed.** `BoundedIterativeExecutionLoop`, `GoalCompletionLoop`, `IterationBudget` and `BudgetGuard` (`apps/Send.Agent.Runtime/.../Domain/Execution/BudgetGuard.cs`) enforce the same three ceilings you build in week 2 — but aggregated per workstream and checked before every model call. When you read them, compare *where* the budget is checked, not just that it is checked.

  **循环是同一台机器，只是受到治理。** `BoundedIterativeExecutionLoop`、`GoalCompletionLoop`、`IterationBudget` 和 `BudgetGuard`（`apps/Send.Agent.Runtime/.../Domain/Execution/BudgetGuard.cs`）强制执行的正是你在第 2 周构建的三个上限——只不过按工作流汇总，并在每次模型调用之前检查。阅读这些代码时，要比较预算是在*哪里*被检查的，而不仅仅是它有没有被检查。

- **Your tracer becomes `TurnStage`.** SendOS records 45 named stages, each `Ran/Skipped/Failed` with a reason, plus an append-only `IOutcomeTraceEmitter` (`apps/Send.Agent.Runtime/.../Application/Runtime/TurnStage.cs:29-203`). Week 2's `step`/`model_call`/`tool_call`/`tool_result` events are the same design at a smaller scale — which is exactly what makes week 7's eval harness possible.

  **你的 tracer 会变成 `TurnStage`。** SendOS 记录 45 个具名阶段，每个阶段都带有 `Ran/Skipped/Failed` 状态及原因，外加一个只追加的 `IOutcomeTraceEmitter`（`apps/Send.Agent.Runtime/.../Application/Runtime/TurnStage.cs:29-203`）。第 2 周的 `step`/`model_call`/`tool_call`/`tool_result` 事件是同一设计的小规模版本——这恰恰是第 7 周评测 harness 得以实现的基础。

## Check yourself

**自测**

1. An assistant message has `content=null` and two `tool_calls`. What must the next request contain before the model can see tool results at all, and which field links each result to its call?

   一条 assistant 消息的 `content=null`，并带有两个 `tool_calls`。在模型能够看到任何工具结果之前，下一个请求必须包含什么？哪个字段把每个结果与其调用关联起来？

2. `finish_reason="length"` arrives mid-plan. Name three legitimate responses and the trade-off each one makes.

   在执行计划的途中收到了 `finish_reason="length"`。说出三种合理的应对方式，以及每种方式所做的权衡。

3. Why does a budget check at the **top** of the iteration prevent a class of bug that a check after the model call cannot?

   为什么在迭代**开头**进行预算检查，能防止一类在模型调用之后检查所无法防止的 bug？

4. Tool-call arguments stream as fragments across several SSE deltas. What bug appears if you parse each delta independently, and what is the correct accumulation key?

   工具调用参数以片段形式分散在多个 SSE 增量中流式传输。如果你独立解析每个增量，会出现什么 bug？正确的累积键是什么？

5. Your adapter retries a 500 twice. Why is that safe for the model call but unsafe if you copy the same policy to tool execution?

   你的适配器对一个 500 重试了两次。为什么这对模型调用是安全的，但如果把同样的策略照搬到工具执行上就不安全？

## Reading

**延伸阅读**

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (2024, 2026 update note) — the vocabulary of workflows vs agents, and the tool-design appendix.

  [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（2024，附 2026 年更新说明）——工作流与 Agent 的术语区分，以及工具设计附录。

- [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629) (2022) — the loop's research ancestor; read for the thought/action/observation structure.

  [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629)（2022）——该循环在研究上的鼻祖；重点读其中的思考/行动/观察结构。

- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) (2025) — "own your prompt, context, control flow and state" as a production checklist.

  [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)（2025）——把“掌控你的提示词、上下文、控制流和状态”作为一份生产检查清单。

- [SWE-agent: agent–computer interfaces](https://arxiv.org/abs/2405.15793) (2024) — the evidence that the harness, not just the model, moves benchmark results.

  [SWE-agent: agent–computer interfaces](https://arxiv.org/abs/2405.15793)（2024）——证明了推动基准测试结果的是 harness，而不仅仅是模型。

- **Companion book:** *AI Agents in Depth* v2.0, ch.1 + ch.2 §2.2 — the harness framing, the five harness elements, and the same loop at API level with a code walkthrough. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 1 章 + 第 2 章 §2.2——harness 的框架、harness 的五个要素，以及同一个循环在 API 层面的实现与代码讲解。[章节对照表](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
