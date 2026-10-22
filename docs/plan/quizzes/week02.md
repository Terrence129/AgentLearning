# Week 2 Quiz — Tools and the Agent Loop

**第 2 周测验 — 工具与 Agent 循环**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** Which is the main advantage of native tool calling over text-parsed ReAct?

与基于文本解析的 ReAct 相比，原生工具调用的主要优势是什么？

- A) It uses fewer tokens in every case

  它在任何情况下都消耗更少的 token

- B) The provider returns structured `tool_calls` with ids and JSON arguments, removing brittle parsing

  模型提供商（provider）返回带有 id 和 JSON 参数的结构化 `tool_calls`，省去了脆弱的解析

- C) It removes the need for a maximum step count

  它不再需要最大步数限制

- D) It guarantees the model picks the correct tool

  它保证模型会选择正确的工具

**Q2.** The loop receives a `tool_call` with `id="call_7"`. What must the tool-result message contain?

循环收到一个 `id="call_7"` 的 `tool_call`。工具结果消息必须包含什么？

- A) Only the content; the model infers the association

  只需要内容；模型会自行推断对应关系

- B) `role="tool"`, the matching `tool_call_id`, and the result content

  `role="tool"`、相匹配的 `tool_call_id`，以及结果内容

- C) `role="assistant"` with the result appended

  `role="assistant"`，并在后面附上结果

- D) A new assistant turn summarising the result

  一个新的 assistant 轮次，对结果进行总结

**Q3.** Where should the token/cost budget check happen in the loop?

token / 成本预算检查应该放在循环的什么位置？

- A) After every tool execution

  每次工具执行之后

- B) At the top of each iteration, before the model call

  每次迭代的开头，在模型调用之前

- C) Only at the end of the run

  只在运行结束时

- D) Inside the provider adapter

  在提供商适配器内部

**Q4.** A tool raises `FileNotFoundError`. What should the loop do?

某个工具抛出了 `FileNotFoundError`。循环应该怎么做？

- A) Crash — programming errors must surface

  崩溃——编程错误必须暴露出来

- B) Return the error text to the model as a tool observation so it can adapt

  把错误文本作为工具观察结果返回给模型，让它能够调整

- C) Retry the tool three times with backoff

  带退避地把该工具重试三次

- D) Replace the tool with a fallback tool automatically

  自动用一个备用工具替换该工具

**Q5.** Why is tool-output truncation part of loop design, not an optional nicety?

为什么工具输出截断是循环设计的一部分，而不是可有可无的锦上添花？

- A) Truncation improves model creativity

  截断能提升模型的创造力

- B) A single verbose tool result can consume most of the context window and cost

  单个冗长的工具结果就可能耗掉大部分上下文窗口和成本

- C) Providers reject outputs over 1 KB

  提供商会拒绝超过 1 KB 的输出

- D) It is required for parallel tool calls

  并行工具调用必须依赖它

**Q6.** Which statement is the most defensible design principle?

哪种说法是最站得住脚的设计原则？

- A) Prefer an agent over a workflow because agents are more capable

  优先选择 Agent 而非工作流，因为 Agent 能力更强

- B) Prefer a workflow over an agent unless the task genuinely requires model-directed control flow

  优先选择工作流而非 Agent，除非任务确实需要由模型主导的控制流

- C) Prefer multiple agents for any multi-step task

  任何多步骤任务都优先使用多个 Agent

- D) Prefer the largest available model so the loop can stay simple

  优先使用可用的最大模型，这样循环可以保持简单

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** A loop's budget check is placed **after** the model call instead of before it. Explain the concrete failure this creates.

某个循环的预算检查被放在了模型调用**之后**而不是之前。解释这会造成什么具体的故障。

**Q8.** Give one task that should be a **workflow** and one that should be an **agent**, and state the property that separates them.

分别举出一个应该做成**工作流**的任务和一个应该做成 **Agent** 的任务，并说明区分二者的属性。

**Q9.** You are designing a `write_file` tool. Name three things in its definition/schema that matter for safety and say why.

你正在设计一个 `write_file` 工具。说出其定义 / schema 中对安全性重要的三点，并说明原因。

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This loop is supposed to be a minimal agent. Identify **three** defects that would make it hang, lose tool results, or overspend.

下面这个循环本应是一个最小化的 Agent。找出会导致它卡死、丢失工具结果或超支的**三个**缺陷。

```python
def run(goal):
    messages = [{"role": "user", "content": goal}]
    while True:
        resp = provider.complete(messages, tools=registry.schemas())
        for call in resp.tool_calls:
            result = registry.call(call.name, call.arguments)
            messages.append({"role": "tool", "content": result})
        if resp.content:
            return resp.content
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Native tool calling removes the parse-a-text-protocol problem and gives stable ids. It does not guarantee choice quality, reduce tokens universally (schemas cost tokens), or replace step limits. *Why it matters: it is the first real improvement over naive ReAct, but it does not remove loop control.*

原生工具调用消除了「解析文本协议」的问题，并提供稳定的 id。它并不保证选择的质量，也不会在所有情况下都减少 token（schema 本身也要消耗 token），更不能取代步数限制。*为什么重要：这是相对朴素 ReAct 的第一个真正改进，但它并没有免除对循环的控制。*

**Q2 — B.** The tool message must carry `tool_call_id` so the provider can pair request and result. Without it, providers reject the turn or the model misattributes results.

工具消息必须带上 `tool_call_id`，这样提供商才能把请求和结果配对。缺少它，提供商会拒绝该轮次，或者模型会把结果对应错。

**Q3 — B.** Checking before the call prevents starting a turn you cannot afford. Checking after means every overrun costs one full model call plus its tools. *Why it matters: budget enforcement is a loop invariant, not a post-hoc report.*

在调用之前检查，可以避免开启一个负担不起的轮次。在之后检查，则意味着每次超支都要多付出一次完整的模型调用外加它触发的工具。*为什么重要：预算控制是循环的不变量，而不是事后报告。*

**Q4 — B.** Errors are observations: the model can retry with a corrected path or choose another tool. Crashing converts a recoverable condition into an outage. *Why it matters: error-as-observation is what makes an agent robust.*

错误就是观察结果：模型可以用修正后的路径重试，或选择另一个工具。崩溃则会把一个可恢复的状况变成一次故障。*为什么重要：把错误当作观察结果，正是 Agent 健壮性的来源。*

**Q5 — B.** A directory listing or file dump can be tens of thousands of tokens; truncation (head/tail, byte caps, "N more lines" markers) preserves signal at bounded cost.

一次目录列表或文件转储就可能有数万 token；截断（保留头 / 尾、字节上限、「还有 N 行」标记）能以有限的成本保留有效信号。

**Q6 — B.** Use the least autonomy that passes the eval. Workflows are predictable, cheaper and easier to audit; agents are for cases where the path cannot be predefined.

使用能通过评测（eval）的最低自主程度。工作流可预测、更便宜、也更容易审计；Agent 适用于路径无法预先定义的场景。

**Q7 — model answer.** The loop can start a call that its remaining budget cannot pay for, so the run always overspends by at least one model call (plus any tool side effects it triggers). With parallel tool calls or expensive models the overrun can be large, and the recorded cost is then unreliable. Fix: reserve/estimate cost before the call and fail closed when the estimate exceeds the remaining budget.

**参考答案。** 循环可能会发起一个剩余预算支付不起的调用，因此运行总会至少超支一次模型调用（外加它触发的任何工具副作用）。在并行工具调用或昂贵模型的情况下，超支可能很大，记录下来的成本也就不可靠了。修复方法：在调用之前预留 / 估算成本，当估算超过剩余预算时以失败关闭（fail closed）。

**Q8 — model answer.** Workflow: "extract fields from these 200 invoices and write a CSV" — fixed steps, no model-directed branching. Agent: "find why CI is failing on this branch and fix it" — the number and nature of steps cannot be known in advance and depends on tool feedback. The separating property is whether the control flow can be encoded before runtime.

**参考答案。** 工作流：「从这 200 张发票中提取字段并写入 CSV」——步骤固定，没有由模型主导的分支。Agent：「找出这个分支上 CI 失败的原因并修好它」——步骤的数量和性质无法预先知道，取决于工具的反馈。区分二者的属性是：控制流能否在运行之前就被编码下来。

**Q9 — model answer.** (1) `is_write=True` metadata on the `Tool` (the registry carries it; read tools leave it `False`) so policy, approval and audit can gate it. (2) Workspace-relative path semantics: `WriteFileInput.path` is documented as relative to the workspace root and `FileSandbox.resolve` enforces containment — the JSON Schema cannot stop `../`, so the tool must. (3) An explicit write contract in the description (parents are created, existing files are overwritten) plus bounded content size, so the model does not have to guess. Bonus: failures return as observations via `ToolResult.failure`, never as exceptions escaping the loop.

**参考答案。** (1) `Tool` 上的 `is_write=True` 元数据（由工具注册表携带；读类工具保持为 `False`），以便策略、审批和审计能够对其把关。(2) 相对于工作区的路径语义：`WriteFileInput.path` 在文档中被说明为相对于工作区根目录，并由 `FileSandbox.resolve` 强制限定在其中——JSON Schema 拦不住 `../`，所以必须由工具来拦。(3) 在描述中写明写入契约（会创建父目录、会覆盖已有文件），并限制内容大小，让模型不必去猜。附加：失败通过 `ToolResult.failure` 作为观察结果返回，绝不以异常形式逃出循环。

**Q10 — model answer.** (1) No `max_steps`/budget guard and no increment — a model that keeps calling tools loops forever. (2) The assistant turn containing `tool_calls` is never appended, and tool results omit `tool_call_id` — the conversation is malformed; many providers will error or ignore the results. (3) Termination is `if resp.content` — an intermediate assistant message with prose ("Let me check the files…") ends the run prematurely; the correct condition is a final answer with no pending tool calls. Also: tool results are not truncated.

**参考答案。** (1) 没有 `max_steps` / 预算防护，也没有计数递增——一个不停调用工具的模型会让它永远循环下去。(2) 包含 `tool_calls` 的 assistant 轮次从未被追加，工具结果也缺少 `tool_call_id`——对话格式是错误的；很多提供商会报错或忽略这些结果。(3) 终止条件是 `if resp.content`——一条带有文字的中间 assistant 消息（「让我检查一下这些文件……」）会让运行过早结束；正确的条件是：给出最终答案且没有待处理的工具调用。另外：工具结果没有被截断。
