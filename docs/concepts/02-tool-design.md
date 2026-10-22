# 02 — Tool Design

**02 — 工具设计**

> **Week 2 · just-in-time concept note.** Read before the [agent loop lab](../../labs/week02-agent-loop/README.md) (~20 min). The loop is the machinery; tools are the product surface. Most "the agent is dumb" complaints are tool-design bugs.
>
> **第 2 周 · 即时概念笔记。** 在做 [Agent 循环实验](../../labs/week02-agent-loop/README.md)之前阅读（约 20 分钟）。循环是机器本身；工具是产品的界面。大多数“这个 Agent 太笨了”的抱怨，其实都是工具设计上的 bug。

## The failure mode this prevents

**本机制防止的失败模式**

The tool museum. Somebody wraps every endpoint in the service — `list_customers`, `get_customer`, `get_customer_by_email`, `search_customers`, `update_customer`, `send_email`, and forty more — and the model now has to choose among overlapping tools using names that differ by one word. It picks `list_customers` and receives 400 KB of JSON; the transcript grows by 60k tokens in one step; the next model call is slower, more expensive, and worse at the actual task. Then, on a retry after a 500, `send_email` runs twice, because the loop retried the step and nothing about the tool was idempotent. And when a tool finally raises a `KeyError`, the agent dies at step 9 with a Python traceback instead of reading the error and trying a different parameter — because tool errors were raised, not observed.

工具博物馆。有人把服务里的每个端点都包装了一遍——`list_customers`、`get_customer`、`get_customer_by_email`、`search_customers`、`update_customer`、`send_email`，外加四十多个——于是模型现在必须在一堆功能重叠、名字只差一个词的工具中做选择。它选了 `list_customers`，收到了 400 KB 的 JSON；对话记录在一步之内增长了 60k token；下一次模型调用更慢、更贵，在真正的任务上表现也更差。接着，在一次 500 之后的重试中，`send_email` 执行了两次，因为循环重试了整个步骤，而这个工具没有任何幂等设计。最后，当某个工具终于抛出 `KeyError` 时，Agent 在第 9 步带着一段 Python traceback 崩溃了，而不是读取错误信息、换一个参数再试——因为工具错误是被抛出的，而不是被观察到的。

This note is how you avoid all four: one schema/handler contract, agent-shaped schemas and descriptions, token-bounded outputs, errors as observations, and a hard read/write distinction.

这篇笔记讲的就是如何避免这四种问题：统一的 schema/处理函数契约、为 Agent 量身设计的 schema 和描述、有 token 上限的输出、把错误当作观察结果，以及严格的读/写区分。

## If you remember five things

**如果只记住五件事**

> 1. **A tool is a two-sided contract**: the JSON Schema the model sees and the handler you run. Keep them in one object ([`agentlab/tools/registry.py`](../../agentlab/tools/registry.py)) so they cannot drift.
>
>    **工具是一份双向契约**：一边是模型看到的 JSON Schema，另一边是你运行的处理函数。把它们放在同一个对象里（[`agentlab/tools/registry.py`](../../agentlab/tools/registry.py)），这样两者就不会逐渐脱节。
>
> 2. **The schema is validation and the description is a prompt.** Both are loaded into context on every step, so both are design surfaces with a token cost.
>
>    **schema 是校验，描述是提示词。** 两者在每一步都会被加载进上下文，所以它们都是有 token 成本的设计界面。
>
> 3. **Errors are observations.** `invoke()` never raises for a tool-level problem; it returns `ok=False` with actionable text the model can act on.
>
>    **错误是观察结果。** `invoke()` 绝不会因为工具层面的问题而抛出异常；它返回 `ok=False`，并附带模型可以据此行动的可操作文本。
>
> 4. **Output is context.** Truncate, filter, paginate and instruct — an unbounded tool result is a context-window incident waiting to happen.
>
>    **输出就是上下文。** 截断、过滤、分页并给出指引——一个没有上限的工具结果就是一场随时会发生的上下文窗口事故。
>
> 5. **Read vs write is the safety axis.** `is_write=True` implies approval, an idempotency key, a receipt and (in SendOS) post-condition verification. Read tools can be parallel and unrestricted; write tools cannot.
>
>    **读与写是安全的主轴。** `is_write=True` 意味着需要审批、幂等键、回执，以及（在 SendOS 中）后置条件验证。读工具可以并行执行且不受限制；写工具则不行。

## The model in one page

**一页看懂模型**

### Two halves, one object

**两个半边，一个对象**

```python
@dataclass
class Tool:
    name: str  # stable, verb-shaped; namespaced when shared
    description: str  # prompt text: what it does, when to use, when not to
    parameters: JSONSchema  # what the model may send
    handler: Callable  # what actually runs
    input_model: type[BaseModel]  # pydantic; produces the schema and validates
    is_write: bool = False  # drives approval/idempotency policy
    max_output_chars: int = 8_000
```

The registry turns `input_model` into JSON Schema with `additionalProperties: false`, validates arguments *before* execution, and converts exceptions into `ToolResult.failure(...)` ([`registry.py`](../../agentlab/tools/registry.py)). The docstring rule is the whole design: validate at the boundary, never halfway through a side effect.

工具注册表会把 `input_model` 转换成带 `additionalProperties: false` 的 JSON Schema，在执行*之前*校验参数，并把异常转换为 `ToolResult.failure(...)`（[`registry.py`](../../agentlab/tools/registry.py)）。文档字符串里的那条规则就是整个设计：在边界处校验，绝不在副作用执行到一半时才校验。

### Schema design for models

**面向模型的 schema 设计**

| Rule<br>规则 | Why<br>原因 | Bad → good<br>差 → 好 |
|---|---|---|
| Object root, `additionalProperties: false`, `strict: true` where supported<br>根节点为 object，`additionalProperties: false`，在支持的地方使用 `strict: true` | removes a class of malformed calls; still validate locally<br>消除一类格式错误的调用；仍需在本地校验 | `{}` → `{"type":"object","properties":{...},"required":[...],"additionalProperties":false}` |
| Semantic parameter names<br>有语义的参数名 | models reason over names; `user` is ambiguous<br>模型会根据名称进行推理；`user` 有歧义 | `user` → `user_id`; `date` → `start_date_iso8601` |
| Enums, formats, units in the description<br>在描述中写明枚举、格式和单位 | turns guessing into selecting<br>把猜测变成选择 | `"format": "date-time"`, `"unit": "USD cents"` |
| Required-first; avoid all-optional schemas<br>必填优先；避免全部可选的 schema | optional-everything invites omissions<br>全部可选会招致遗漏 | mark five fields required before adding optionals<br>先把五个字段标为必填，再添加可选字段 |
| Discriminated union for variants<br>用可辨识联合表示变体 | one tool with `kind` beats five near-identical tools<br>一个带 `kind` 的工具胜过五个几乎相同的工具 | `{kind: "refund" \| "void", ...}` |
| Depth ≤ 2, arrays of scalars preferred<br>深度 ≤ 2，优先使用标量数组 | deep nesting multiplies schema and error surface<br>深层嵌套会成倍放大 schema 和出错面 | flatten or split<br>扁平化或拆分 |
| No free-form `dict`/`Any`<br>不要使用自由格式的 `dict`/`Any` | unvalidatable input becomes runtime bugs<br>无法校验的输入会变成运行时 bug | `dict[str, str]` with documented keys<br>带有文档化键的 `dict[str, str]` |

Week 3's structured-output lab builds the pydantic → JSON Schema path you use here; the same discipline applies to tool arguments, which are just structured output the model emits as a side effect.

第 3 周的结构化输出实验会构建你在这里使用的 pydantic → JSON Schema 路径；同样的规范也适用于工具参数，因为工具参数不过是模型作为副作用产出的结构化输出。

### Descriptions are prompts

**描述就是提示词**

The tool name and description decide whether the model selects the tool at all. Write them for a competent new hire: what it does, when to use it, when **not** to, what the return looks like, one example argument. Anthropic's tool-writing guidance found that even small description refinements produced large accuracy changes — and that namespace schemes (service first vs resource first) have model-dependent effects worth evaluating rather than guessing ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)). The corollary: descriptions are versioned, reviewed assets, not comments. SendOS makes this literal — a capability is a published, version-pinned asset, and an undeclared capability is not invokable ([research 05 §2.3](../research/05-sendos-concept-map.md)).

工具名称和描述决定了模型到底会不会选中这个工具。把它们写给一位能干的新员工看：它做什么、什么时候用、什么时候**不该**用、返回值是什么样子、一个示例参数。Anthropic 的工具编写指南发现，即使是对描述的细微改进也能带来准确率的大幅变化——而且命名空间方案（服务优先 vs 资源优先）的效果取决于模型，值得评测而不是靠猜（[Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)）。由此推论：描述是有版本、经过评审的资产，而不是注释。SendOS 把这一点落到了实处——一项能力（capability）是一个已发布、锁定版本的资产，而未声明的能力不可调用（[research 05 §2.3](../research/05-sendos-concept-map.md)）。

### Outputs: filter, truncate, instruct

**输出：过滤、截断、指引**

Tools should return **high-signal fields**, not the raw provider response. Resolve opaque IDs to names where the agent has to reason about them, keep raw IDs only when they are needed for the next call, and expose a `response_format: concise | detailed` enum when both use cases exist — Claude Code caps tool responses at 25,000 tokens by default for exactly this reason ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).

工具应当返回**高信号字段**，而不是模型提供商（provider）的原始响应。在 Agent 需要基于其进行推理的地方，把不透明的 ID 解析为名称；只有在下一次调用需要时才保留原始 ID；当两种使用场景都存在时，暴露一个 `response_format: concise | detailed` 枚举——Claude Code 默认把工具响应限制在 25,000 个 token 以内，正是出于这个原因（[Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)）。

`agentlab`'s default is 8,000 characters, and `ToolResult.truncated` is part of the contract. Truncation must **instruct**: `"...[truncated; refine with query= or page=]"` teaches the model to narrow instead of retrying blindly. Pagination, range selection and filters belong in the schema, with sane defaults.

`agentlab` 的默认值是 8,000 个字符，而 `ToolResult.truncated` 是契约的一部分。截断必须**给出指引**：`"...[truncated; refine with query= or page=]"` 能教会模型缩小范围，而不是盲目重试。分页、范围选择和过滤条件都应该放在 schema 中，并配上合理的默认值。

### Errors as observations

**把错误当作观察结果**

```python
return ToolResult.failure(
    f"arguments for tool 'schedule_event' do not match its schema: "
    f"start_at must be ISO-8601 (got 'tomorrow 3pm')"
)
```

Three properties matter: the model can see *which* argument is wrong, it gets a fixable instruction, and the loop continues. Unknown tool names should list what *is* available (`available tools: read_file, list_dir, search_text`) — that message is the model's only map. Keep a distinction between retryable (timeout, transient 5xx) and terminal (schema violation, authorization denied) errors; for terminal errors the right move is often to change strategy, not retry.

有三个性质很重要：模型能看到*哪个*参数错了，它得到一条可以照着修正的指引，并且循环会继续。对于未知的工具名，应当列出*有哪些*工具可用（`available tools: read_file, list_dir, search_text`）——这条消息是模型唯一的地图。要区分可重试的错误（超时、暂时性 5xx）和终止性的错误（违反 schema、授权被拒）；对于终止性错误，正确的做法往往是改变策略，而不是重试。

Week 8 pushes this further: tool output is untrusted input, so observations must be delimited and never treated as instructions (note 08).

第 8 周会更进一步：工具输出是不可信的输入，因此观察结果必须加上分隔标记，且绝不能被当作指令（见笔记 08）。

### Parallel tool calls

**并行工具调用**

A single assistant message can request several tools. Execute them concurrently, then append **one tool message per call, in the original order** — order is part of the wire contract and makes traces readable. Decide the partial-failure policy up front: all-or-nothing for transactional workflows, best-effort with per-call errors for research. The lab's `MockProvider.tool_turn(extra_calls=...)` scripts exactly this case.

一条 assistant 消息可以请求多个工具。并发执行它们，然后**按原始顺序为每个调用追加一条工具消息**——顺序是传输契约的一部分，也让 trace 更易读。要提前确定部分失败时的策略：事务性工作流采用全有或全无，研究类任务则尽力而为并逐个报告调用错误。实验中的 `MockProvider.tool_turn(extra_calls=...)` 正是用脚本模拟了这种情况。

Parallel *reads* are cheap and safe; parallel *writes* need independent idempotency keys and, in a governed system, separate approvals. Parallelism also multiplies rate-limit pressure — the provider seam should own concurrency limits, not each tool.

并行*读*既便宜又安全；并行*写*则需要各自独立的幂等键，并且在受治理的系统中需要分别审批。并行还会成倍放大限流压力——并发上限应由 provider 接缝（seam）统一掌管，而不是由每个工具各自负责。

### Read vs write

**读与写**

Make `is_write` explicit and treat it as a risk declaration, not a label. Write tools need: an idempotency key (the retry story), an approval gate when the effect is irreversible or external (week 6/8), an audit receipt (who/what/args hash/result), and ideally a readback verification — SendOS models this with `IResultVerifier` and `ReadbackVerification` states (`Verified/Contradicted/Unconfirmed/NotPerformed`) precisely because "the API returned 200" is not evidence the business outcome happened ([research 05 §2.3](../research/05-sendos-concept-map.md)). Read tools need none of that, which is why the distinction buys you both safety and latency.

把 `is_write` 显式标出，并把它当作一项风险声明，而不是一个标签。写工具需要：幂等键（应对重试）、当效果不可逆或涉及外部时的审批关卡（第 6/8 周）、审计回执（谁/做了什么/参数哈希/结果），最好还要有回读验证——SendOS 用 `IResultVerifier` 和 `ReadbackVerification` 的几种状态（`Verified/Contradicted/Unconfirmed/NotPerformed`）来建模这一点，正是因为“API 返回了 200”并不能证明业务结果真的发生了（[research 05 §2.3](../research/05-sendos-concept-map.md)）。读工具完全不需要这些，这就是为什么这一区分能同时为你换来安全性和低延迟。

### When not to use a tool

**什么时候不该使用工具**

- **Deterministic work belongs in code.** If a step is a fixed transformation, a tool call is a slow, expensive, probabilistic function call.

  **确定性的工作应该写在代码里。** 如果某一步是固定的转换，那么工具调用就只是一次缓慢、昂贵且带有概率性的函数调用。

- **Merge tools the model cannot choose between.** If two tools overlap, you created a decision problem; fix the design.

  **合并模型无法区分的工具。** 如果两个工具功能重叠，你就制造了一个决策难题；去修正设计。

- **Filter inside the tool, not after.** `search_logs` beats `read_logs` — return the rows the decision needs, not everything plus a request to narrow ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).

  **在工具内部过滤，而不是事后过滤。** `search_logs` 胜过 `read_logs`——返回决策所需的那些行，而不是返回全部内容再附上一句“请缩小范围”（[Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)）。

- **Code-mode for large catalogues.** Presenting MCP servers as importable code lets the agent load only what it needs and keep intermediate results out of context: one Anthropic task dropped from ~150k to ~2k tokens (98.7%) ([Anthropic, 2025-11](https://www.anthropic.com/engineering/code-execution-with-mcp)). The cost is a sandbox you must operate.

  **大型工具目录采用代码模式（code-mode）。** 把 MCP 服务器呈现为可导入的代码，可以让 Agent 只加载它需要的部分，并把中间结果留在上下文之外：Anthropic 的一个任务因此从约 150k token 降到了约 2k token（减少 98.7%）（[Anthropic, 2025-11](https://www.anthropic.com/engineering/code-execution-with-mcp)）。代价是你必须运维一个沙箱。

- **Sometimes the answer is "no tool".** Answering from context is cheaper and lower-risk when the model already has the facts.

  **有时答案就是“不用工具”。** 当模型已经掌握事实时，直接根据上下文作答更便宜、风险也更低。

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>现实 |
|---|---|
| "More tools make the agent more capable."<br>“工具越多，Agent 能力越强。” | Beyond a dozen, selection accuracy and per-step cost both degrade. Curate; consolidate; namespace.<br>超过十来个之后，选择准确率和每步成本都会变差。精选、合并、加命名空间。 |
| "Strict mode means I don't need local validation."<br>“有了严格模式，我就不需要本地校验了。” | Only some providers/models support it, and it validates schema, not semantics. Validate at your boundary regardless.<br>只有部分提供商/模型支持它，而且它校验的是 schema，而不是语义。无论如何都要在你的边界处校验。 |
| "Tool errors should raise so bugs are visible."<br>“工具错误应该抛出，这样 bug 才看得见。” | Tool-level failures are observations. Raise only for harness bugs; log both.<br>工具层面的失败是观察结果。只在 harness（运行框架）自身有 bug 时才抛出；两者都要记录日志。 |
| "Return the full API response, the model can filter."<br>“返回完整的 API 响应，模型自己会过滤。” | Every token is context rent. Return the fields the decision needs.<br>每个 token 都是在为上下文付租金。只返回决策所需的字段。 |
| "Read/write is a UI label."<br>“读/写只是一个 UI 标签。” | It determines approvals, idempotency, sandboxing, receipts and verification.<br>它决定了审批、幂等、沙箱、回执和验证。 |
| "Tool descriptions are documentation."<br>“工具描述就是文档。” | They are prompt text loaded every step, and they decide selection. Version and test them.<br>它们是每一步都会加载的提示词文本，并决定了工具的选择。要对它们做版本管理和测试。 |

## How this shows up in SendOS

**在 SendOS 中如何体现**

- **A governed registry, not a pile of wrappers.** `CapabilityCatalogueAssembler.cs:34-120` merges three declaration sources with **published-wins**, and matching filters by tenant and declared shape (read vs action kind). That is your `ToolRegistry` plus the governance layer you will build in weeks 6–8 ([research 05 §2.3](../research/05-sendos-concept-map.md)).

  **一个受治理的注册表，而不是一堆包装器。** `CapabilityCatalogueAssembler.cs:34-120` 按照**已发布者优先**的规则合并三个声明来源，并按租户和声明的形态（读类 vs 动作类）进行匹配过滤。这就是你的 `ToolRegistry`，再加上你将在第 6–8 周构建的治理层（[research 05 §2.3](../research/05-sendos-concept-map.md)）。

- **Risk is part of the contract.** SendOS capabilities carry risk level, approval requirement and read/write metadata; the execution path differs by declared shape (`DirectCapabilityHandler`). Your `is_write` flag is the miniature of that idea — keep it, and let it drive policy rather than documentation.

  **风险是契约的一部分。** SendOS 的能力带有风险等级、审批要求和读/写元数据；执行路径会因声明的形态而不同（`DirectCapabilityHandler`）。你的 `is_write` 标志就是这一思想的缩影——保留它，并让它驱动策略，而不只是充当文档。

- **Writes are verified, not assumed.** `IResultVerifier` + `ReadbackVerification` exist because a 200 response is not an outcome. When you build `write_file` in week 2, notice that "wrote the file" is a claim you can verify cheaply — a good habit to carry into week 8.

  **写操作要验证，而不是假定成功。** `IResultVerifier` + `ReadbackVerification` 之所以存在，是因为一个 200 响应并不等于结果。当你在第 2 周构建 `write_file` 时，请注意“已写入文件”是一个可以低成本验证的断言——这是一个值得带到第 8 周的好习惯。

## Check yourself

**自测**

1. Your schema has `additionalProperties: false` and the provider supports strict mode. Name two classes of bad input that still reach your handler.

   你的 schema 设置了 `additionalProperties: false`，提供商也支持严格模式。说出仍然会到达你的处理函数的两类错误输入。

2. You have both `list_contacts` and `search_contacts`. What observable agent behaviour tells you this is a design bug, and what are your two options?

   你同时有 `list_contacts` 和 `search_contacts`。哪种可观察到的 Agent 行为会告诉你这是一个设计 bug？你有哪两种选择？

3. Rewrite this observation so a model can recover: `ERROR: 400 Bad Request`. What must it include, and what must it avoid?

   改写这条观察结果，使模型能够从中恢复：`ERROR: 400 Bad Request`。它必须包含什么，又必须避免什么？

4. Which of your tools need an idempotency key, and why does parallel tool calling make the answer sharper rather than optional?

   你的哪些工具需要幂等键？为什么并行工具调用会让这个问题的答案更加明确，而不是变得可有可无？

5. You must expose 30 tools. Describe three ways to cut per-step context cost, and one downside of each.

   你必须暴露 30 个工具。描述三种降低每步上下文成本的方法，以及每种方法的一个缺点。

## Reading

**延伸阅读**

- [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09) — naming, token-efficient returns, error surfaces, and the evaluate-your-tools loop.

  [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)（2025-09）——命名、节省 token 的返回值、错误呈现方式，以及“评测你的工具”这一循环。

- [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) (2025-11) — progressive tool disclosure and the 150k → 2k token result; read it before designing a large tool catalogue.

  [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)（2025-11）——渐进式工具披露，以及 150k → 2k token 的结果；在设计大型工具目录之前先读它。

- [SWE-agent](https://arxiv.org/abs/2405.15793) (2024) — the agent–computer interface paper: command design as the main lever.

  [SWE-agent](https://arxiv.org/abs/2405.15793)（2024）——关于 Agent–计算机接口的论文：命令设计是最主要的杠杆。

- [smolagents](https://github.com/huggingface/smolagents) — read the whole ~1k-line core to see tools, executor and memory in one small system.

  [smolagents](https://github.com/huggingface/smolagents)——通读其约 1k 行的核心代码，在一个小系统中同时看到工具、执行器和记忆。

- **Companion book:** *AI Agents in Depth* v2.0, ch.4 §4.1–4.2 and §4.4 + ch.2 §2.4.6 — capability-expression forms, the art of tool descriptions, parameter fidelity, and what to do when the catalogue outgrows the context. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 4 章 §4.1–4.2 和 §4.4 + 第 2 章 §2.4.6——能力的表达形式、编写工具描述的艺术、参数保真度，以及当工具目录超出上下文容量时该怎么办。[章节对照表](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
