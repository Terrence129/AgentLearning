# Week 2 lab — Tools and the agent loop

**第 2 周实验（lab）— 工具与 Agent 循环**

## 1. Why this week exists

**1. 为什么要有这一周**

An agent is a model using tools in a loop — and almost every "the agent went crazy" incident is a loop bug, not a model bug: no step ceiling, no budget check, a tool error that crashes the run, a tool result with no `tool_call_id` so the provider ignores it, or an agent that repeats one call until the invoice arrives. This week you build the loop yourself (the single most important week of the course) plus the tools it acts through: a structurally safe calculator and a filesystem confined to one workspace root. From here on, every later week is a modifier around this loop.

Agent 就是一个在循环中使用工具的模型 —— 而几乎每一起“Agent 失控了”的事故都是循环的 bug，而不是模型的 bug：没有步数上限、没有预算检查、工具出错导致整个运行崩溃、工具结果缺少 `tool_call_id` 导致模型提供商（provider）忽略它，或者 Agent 一直重复同一个调用直到账单到来。本周你要亲手构建这个循环（整门课程中最重要的一周），以及它所借助的工具：一个在结构上安全的计算器，和一个被限制在单一工作区根目录内的文件系统。从这里开始，之后的每一周都是围绕这个循环的修饰与扩展。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **10–12 hours** (core loop ~5 h, built-in tools ~3 h, trace/tests ~3 h, review ~1 h).

  **10–12 小时**（核心循环约 5 小时，内置工具约 3 小时，trace/测试约 3 小时，复盘约 1 小时）。

- Week 1 tests green (or at least `OpenAICompatibleProvider` implemented); you can also run this week against `MockProvider` alone.

  第 1 周的测试已通过（变绿）（或者至少已实现 `OpenAICompatibleProvider`）；你也可以只用 `MockProvider` 来完成本周内容。

- Read first: [`docs/concepts/01-agent-loop.md`](../../docs/concepts/01-agent-loop.md), [`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) §1.1–1.6, and the Anthropic *Building effective agents* essay (linked in [`docs/research/04-learning-resources.md`](../../docs/research/04-learning-resources.md)).

  先阅读：[`docs/concepts/01-agent-loop.md`](../../docs/concepts/01-agent-loop.md)、[`docs/research/01-agent-architecture-sota.md`](../../docs/research/01-agent-architecture-sota.md) 的 §1.1–1.6，以及 Anthropic 的 *Building effective agents* 一文（链接见 [`docs/research/04-learning-resources.md`](../../docs/research/04-learning-resources.md)）。

## 3. The spec

**3. 规格说明**

| File<br>文件 | Member<br>成员 | Contract<br>契约 |
|---|---|---|
| [`agentlab/loop/react.py`](../../agentlab/loop/react.py) | `run_loop(...)` | Budget check at the **top** of each iteration; model call; stop conditions; natural answer when no tool calls; execute tools, append assistant message then tool observations (both ok and failed); charge budget per call, count steps; terminate as data with `LoopOutcome.stop_reason` ∈ `answer / budget / max_steps / error / <condition reason>`; `MaxStepsExceeded` carries `steps` + `last_message`; emit `step`/`model_call`/`tool_call`/`tool_result` trace events.<br>在每次迭代的**开头**检查预算；调用模型；检查停止条件；没有工具调用时即为自然回答；执行工具，先追加 assistant 消息，再追加工具观察结果（成功和失败的都要）；每次调用都计入预算，并统计步数；以数据形式终止，`LoopOutcome.stop_reason` ∈ `answer / budget / max_steps / error / <condition reason>`；`MaxStepsExceeded` 携带 `steps` + `last_message`；发出 `step`/`model_call`/`tool_call`/`tool_result` trace 事件。 |
| [`agentlab/loop/runner.py`](../../agentlab/loop/runner.py) | `AgentRunner`, `AgentResult` | Open the conversation (`system_prompt` then goal); wrap the loop in `run_start`/`run_end` events; map `LoopOutcome` → `AgentResult(answer, steps, usage, stop_reason, trace_events, error)`; partial results survive budget/step stops.<br>开启对话（先 `system_prompt`，再目标）；用 `run_start`/`run_end` 事件包裹循环；把 `LoopOutcome` 映射为 `AgentResult(answer, steps, usage, stop_reason, trace_events, error)`；因预算/步数停止时，部分结果仍然保留。 |
| [`agentlab/loop/stop.py`](../../agentlab/loop/stop.py) | `StepState`, `StopDecision`, `PredicateStop`, `FinishReasonStop`, `RepeatedToolCallStop`, `AnyOf` | One cheap decision per condition; first halt wins; a truncated/filtered response ends the run instead of being treated as an answer; repeated identical tool calls are recognised as "stuck".<br>每个条件做一次廉价的判断；第一个要求停止的条件生效；被截断/被过滤的响应会结束运行，而不是被当作回答；重复的相同工具调用会被识别为“卡住”。 |
| [`agentlab/tools/builtin.py`](../../agentlab/tools/builtin.py) | `safe_eval`, `FileSandbox`, `build_builtin_tools` | Calculator accepts arithmetic only (whitelisted AST: literals, parentheses, unary, `+ - * / // % **`), rejects names/calls/attributes and abusive exponents; filesystem tools resolve every path under one root (absolute paths and traversal rejected); `write_file` is marked `is_write=True`; `search_text` is literal, skips binaries and ignored directories, caps results.<br>计算器只接受算术运算（白名单 AST：字面量、括号、一元运算、`+ - * / // % **`），拒绝名称/调用/属性以及滥用的指数；文件系统工具把每个路径都解析到同一个根目录之下（拒绝绝对路径和目录穿越）；`write_file` 被标记为 `is_write=True`；`search_text` 按字面匹配，跳过二进制文件和被忽略的目录，并限制结果数量。 |

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week02 -m week -q   # all green
.\.venv\Scripts\ruff.exe check agentlab/loop agentlab/tools/builtin.py
```

```bash
# macOS / Linux
uv run pytest tests/week02 -m week -q   # all green
uv run ruff check agentlab/loop agentlab/tools/builtin.py
```

The five golden tasks are in `tests/week02/test_runner.py`: arithmetic, file read, multi-step edit, graceful tool error, budget stop. Manual artifact: run the loop once against a real provider with `build_builtin_tools(tmp_dir)` and a `Tracer` whose `JsonlSink` writes `traces/week02-run.jsonl`; read it back with `agentlab.trace.load_trace` and check that every `tool_call` has a matching `tool_result` with the same `tool_call_id`.

五个黄金任务位于 `tests/week02/test_runner.py`：算术、读文件、多步编辑、优雅处理工具错误、预算停止。手动产出物：用 `build_builtin_tools(tmp_dir)` 和一个 `Tracer`（其 `JsonlSink` 写入 `traces/week02-run.jsonl`），对真实的提供商运行一次循环；用 `agentlab.trace.load_trace` 读回，并检查每个 `tool_call` 都有一个具有相同 `tool_call_id` 的对应 `tool_result`。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. Start from the test file for `react.run_loop`; every assert maps to one line of the docstring's ordered contract.

   从 `react.run_loop` 的测试文件入手；每条 assert 都对应 docstring 中有序契约的一行。

2. The budget check must be the **first** statement inside the loop body. A check after the model call always overspends by one call — write the test in your head: one scripted model call must remain unused when `Budget(max_steps=1)` trips.

   预算检查必须是循环体内的**第一条**语句。放在模型调用之后的检查总会多花一次调用 —— 在脑子里写一下这个测试：当 `Budget(max_steps=1)` 触发时，必须还剩一个预设的模型调用没有被使用。

3. Message order matters: append the assistant message (which holds the `tool_calls`) **before** appending tool results, and give each result `Message.tool_result(call.id, result.output, name=call.name)`.

   消息顺序很重要：**先**追加 assistant 消息（其中包含 `tool_calls`），**再**追加工具结果，并且每个结果都使用 `Message.tool_result(call.id, result.output, name=call.name)`。

4. `registry.invoke` never raises for a bad tool or bad arguments — it returns `ToolResult(ok=False, ...)`. Append `result.output` even when `not result.ok`; that is how the model recovers.

   `registry.invoke` 遇到错误的工具或错误的参数时从不抛异常 —— 它返回 `ToolResult(ok=False, ...)`。即使 `not result.ok`，也要追加 `result.output`；模型正是靠这个来恢复的。

5. Trace events: `tracer.emit(...)` **returns** the event. Collect those returns; do not add a private sink.

   Trace 事件：`tracer.emit(...)` 会**返回**该事件。收集这些返回值即可；不要额外添加私有的 sink。

6. `RepeatedToolCallStop` needs state: keep the last fingerprint and a counter; reset on any change or on a text-only response. Fingerprints must canonicalise dict order (`json.dumps(..., sort_keys=True)`).

   `RepeatedToolCallStop` 需要状态：保存上一次的指纹和一个计数器；任何变化或纯文本响应都会重置它。指纹必须对字典顺序做规范化（`json.dumps(..., sort_keys=True)`）。

7. For the sandbox, `resolve()` once and check `Path.is_relative_to` **after** `resolve()` so symlinks and `..` are both caught. Absolute paths are simply rejected.

   对于沙箱，调用一次 `resolve()`，并在 `resolve()` **之后**检查 `Path.is_relative_to`，这样符号链接和 `..` 都能被拦住。绝对路径直接拒绝。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| `ProviderError: MockProvider script exhausted` | Your loop made one model call too many — usually it treats a text-only response as needing another turn, or the budget check is at the bottom.<br>你的循环多调用了一次模型 —— 通常是把纯文本响应当成了还需要再来一轮，或者预算检查放在了底部。 |
| Provider/mocks see malformed conversations<br>提供商/mock 看到格式错误的对话 | You appended tool messages without `tool_call_id`, or forgot to append the assistant message that requested the tools.<br>你追加的工具消息没有 `tool_call_id`，或者忘了追加请求这些工具的 assistant 消息。 |
| `test_loop_checks_budget_at_top...` fails with 2 calls<br>`test_loop_checks_budget_at_top...` 因 2 次调用而失败 | Budget check placed after the model call, or `budget.add_step()` too early/late.<br>预算检查放在了模型调用之后，或者 `budget.add_step()` 调用得太早/太晚。 |
| `len(outcome.steps)` is one short on stop-condition runs<br>因停止条件结束的运行中 `len(outcome.steps)` 少了一个 | You evaluate conditions (or the natural-answer branch) before recording the `StepRecord`.<br>你在记录 `StepRecord` 之前就评估了停止条件（或进入了自然回答分支）。 |
| `search_text` leaks `.git` matches or crashes on a binary<br>`search_text` 泄露了 `.git` 中的匹配，或在二进制文件上崩溃 | You walk `rglob("*")` without skipping `SKIP_DIRS` or without catching `UnicodeDecodeError`.<br>你用 `rglob("*")` 遍历时没有跳过 `SKIP_DIRS`，或没有捕获 `UnicodeDecodeError`。 |
| `list_dir` output order differs<br>`list_dir` 的输出顺序不一致 | Sort the rendered entries (`"sub/"` sorts after files with the slash suffix), not the raw `Path` objects as the model sees them.<br>对渲染后（即模型看到的形式）的条目排序（带斜杠后缀的 `"sub/"` 会排在文件之后），而不是对原始 `Path` 对象排序。 |

## 7. SendOS bridge

**7. SendOS 对照**

Read `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/**`, `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120`, and `.../Execution/DirectCapabilityHandler.cs`; the summary lives in [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §2.2–2.3 and §4.2.

阅读 `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/**`、`.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` 和 `.../Execution/DirectCapabilityHandler.cs`；概要见 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) 的 §2.2–2.3 和 §4.2。

Answer in 5 bullets:

用 5 个要点回答：

1. What does `CapabilityDefinition` declare that your `Tool` does not (risk level, read/write kind, approval requirement, governed-asset reference) — and which of those would need to exist before your loop could run a real write safely?

   `CapabilityDefinition` 声明了哪些你的 `Tool` 没有声明的内容（风险等级、读/写类型、审批要求、受治理资产引用）—— 在你的循环能够安全地执行真实写操作之前，其中哪些必须先存在？

2. Trace the path from a bound plan node to `DirectCapabilityHandler` execution. Where does your `run_loop` correspond, and what does SendOS add around it (authority, approvals, idempotency, readback)?

   追踪从一个已绑定的计划节点到 `DirectCapabilityHandler` 执行的路径。你的 `run_loop` 对应其中哪一部分？SendOS 又在它周围加了什么（权限、审批、幂等、回读校验）？

3. Your loop treats a repeated tool call as "stuck". What does SendOS do instead of a generic detector, and why might a governance system prefer policy over heuristics?

   你的循环把重复的工具调用视为“卡住”。SendOS 用什么代替了通用的检测器？为什么一个治理系统可能更偏好策略而不是启发式？

## 8. Stretch

**8. 拓展**

1. **Two loops, one task.** Implement text-parsed ReAct (`Thought:`/`Action:`/`Observation:` in plain text) next to native tool calling; run both on 3 of the golden tasks and write 150 words on when each is preferable.

   **两种循环，同一个任务。** 在原生工具调用之外，再实现一个基于文本解析的 ReAct（纯文本形式的 `Thought:`/`Action:`/`Observation:`）；在其中 3 个黄金任务上分别运行两者，并写 150 词说明各自在什么情况下更合适。

2. **No-progress detector with a state hash.** Extend `RepeatedToolCallStop` with a post-action workspace hash so a loop that alternates two different calls but never changes state also terminates as `stuck`. Add the test first.

   **基于状态哈希的无进展检测器。** 为 `RepeatedToolCallStop` 增加一个动作执行后的工作区哈希，使得在两个不同调用之间来回交替、却从不改变状态的循环也会以 `stuck` 终止。先写测试。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** Why are tool errors observations rather than exceptions? What breaks in the loop's reliability story if a tool failure aborts the run?

   **概念层面：** 为什么工具错误是观察结果而不是异常？如果一次工具失败就中止整个运行，循环的可靠性会在哪里崩塌？

2. **Architectural:** Which parts of `run_loop` are *mechanism* and which are *policy* (stop rules, budgets, message formatting)? What would you extract first if a second agent shape were added in week 6?

   **架构层面：** `run_loop` 的哪些部分是*机制*，哪些是*策略*（停止规则、预算、消息格式化）？如果在第 6 周加入第二种 Agent 形态，你会首先抽取出什么？

3. **Transfer:** A "golden task" is an eval case before you have an eval harness. What makes the five tasks here a useful eval set, and what would you add before trusting them for a real product?

   **迁移层面：** “黄金任务”是在你拥有评测（eval）harness（运行框架）之前的评测用例。是什么让这里的五个任务成为一个有用的评测集？在真实产品中信任它们之前，你还会补充什么？
