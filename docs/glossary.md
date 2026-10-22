# Glossary

**术语表**

**Purpose:** the canonical term list for this curriculum. A strong agent engineer should be able to define every term below *without notes*. This file is the source for the weekly flashcards (`docs/plan/flashcards/`) and for the teach-back gate in [`CHECKPOINTS.md`](plan/CHECKPOINTS.md).

**用途：** 本课程的标准术语清单。一名优秀的 Agent 工程师应当能够*不看笔记*就给出下面每个术语的定义。本文件是每周闪卡（`docs/plan/flashcards/`）以及 [`CHECKPOINTS.md`](plan/CHECKPOINTS.md) 中复述讲解（teach-back）关卡的素材来源。

**How to use it (not as a reading list):**

**使用方法（不要把它当作阅读清单）：**

1. Do **not** read it top-to-bottom. Read only the group for the week you are on.

   **不要**从头读到尾。只读你当前所在那一周对应的分组。

2. Cover the "Definition" column and try to produce it from the term, then check yourself. That is retrieval practice, not re-reading.

   遮住「Definition」（定义）一列，试着根据术语自己说出定义，然后再核对。这是提取练习，而不是重读。

3. If you cannot explain a term in one sentence to a colleague, mark it and ask the AI tutor to quiz you on it.

   如果你无法用一句话向同事解释清楚某个术语，就把它标记出来，并让 AI 导师就它对你进行测验。

4. A term is "learned" when you can also give one failure mode it prevents. The "Why it matters" column is the seed for that sentence.

   只有当你还能说出它所防止的一种失败模式时，这个术语才算「学会了」。「Why it matters」（为什么重要）一列就是这句话的种子。

**Legend:** Week links point to that week's quiz (`docs/plan/quizzes/`). Terms marked **SendOS** are specific to the C# platform you work on; the rest are industry vocabulary.

**图例：** 周次链接指向该周的测验（`docs/plan/quizzes/`）。标记为 **SendOS** 的术语专属于你所工作的 C# 平台；其余的都是行业通用词汇。

---

## 1. Model & API surface (Week 1)

**1. 模型与 API 接口（第 1 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **Token**<br>**token（词元）** | A subword unit produced by the model's tokenizer; the unit of billing and context accounting.<br>由模型的分词器产生的子词单元；是计费和上下文核算的单位。 | Every cost, limit and latency estimate is in tokens, never characters or words.<br>所有成本、限制和延迟的估算都以 token 为单位，而不是字符或单词。 | [W1](plan/quizzes/week01.md) |
| **Context window**<br>**上下文窗口** | Maximum tokens the model can attend to in one request (input + generated output).<br>模型在一次请求中能够关注的最大 token 数（输入 + 生成的输出）。 | Exceeding it fails requests or forces truncation; it is the resource context engineering manages.<br>超出它会导致请求失败或被迫截断；它正是上下文工程所管理的资源。 | [W1](plan/quizzes/week01.md) |
| **Temperature**<br>**温度（temperature）** | Sampling randomness: lower = more deterministic, higher = more diverse.<br>采样的随机程度：越低越确定，越高越多样。 | Affects reproducibility of tests and evals more than it affects "creativity".<br>它对测试和评测（eval）可复现性的影响，比对「创造力」的影响更大。 | [W1](plan/quizzes/week01.md) |
| **`finish_reason`** | Why generation stopped: `stop`, `length`, `tool_calls`, `content_filter`.<br>生成停止的原因：`stop`、`length`、`tool_calls`、`content_filter`。 | It is how the loop decides whether to continue, fail or parse output.<br>循环正是依据它来决定是继续、失败还是解析输出。 | [W1](plan/quizzes/week01.md) |
| **Streaming (SSE)**<br>**流式输出（SSE）** | Server-Sent Events: incremental delivery of deltas over one HTTP response.<br>Server-Sent Events（服务器发送事件）：在一个 HTTP 响应中逐步传送增量（delta）。 | Needed for latency feel and for cancelling runaway generations; it is a protocol, not a feature.<br>它对改善延迟体感和取消失控的生成都是必需的；它是一种协议，而不是一项功能。 | [W1](plan/quizzes/week01.md) |
| **Delta assembly**<br>**增量拼装** | Accumulating streamed chunks into a complete message, including partial tool-call arguments.<br>把流式传来的分块累积成一条完整的消息，包括不完整的工具调用参数。 | The most common streaming bug: tool arguments arrive fragmented across chunks.<br>最常见的流式输出 bug：工具参数被拆散在多个分块中到达。 | [W1](plan/quizzes/week01.md) |
| **Exponential backoff + jitter**<br>**指数退避 + 抖动（jitter）** | Retry delay growing exponentially with randomisation to avoid synchronised retry storms.<br>重试延迟按指数增长并加入随机化，以避免同步发生的重试风暴。 | Correct retries make an adapter reliable; naive retries multiply outages and cost.<br>正确的重试让适配器变得可靠；幼稚的重试会成倍放大故障和成本。 | [W1](plan/quizzes/week01.md) |
| **`Retry-After`** | Server hint, in seconds, for when to retry a 429/503.<br>服务器给出的提示（以秒为单位），告诉你何时可以重试 429/503。 | Ignoring it turns rate limiting into a self-inflicted denial of service.<br>忽略它，会把限流变成一场自己造成的拒绝服务。 | [W1](plan/quizzes/week01.md) |
| **Error taxonomy**<br>**错误分类体系** | Classification of failures into retryable (429, 5xx, transport) vs terminal (400, auth, content policy).<br>把失败分为可重试的（429、5xx、传输层）和终止性的（400、认证、内容策略）。 | Retrying a terminal error burns budget and hides the real bug.<br>重试终止性错误会白白烧掉预算，并掩盖真正的 bug。 | [W1](plan/quizzes/week01.md) |
| **Provider seam**<br>**provider 接缝** | An interface behind which each model provider is an adapter.<br>一个接口，其背后的每个模型提供商（provider）都是一个适配器。 | The seam is what lets you swap models, mock them in tests, and add budget-aware routing later.<br>正是这个接缝（seam）让你可以切换模型、在测试中 mock 它们，并在之后加入感知预算的路由。 | [W1](plan/quizzes/week01.md) |
| **Usage accounting**<br>**用量核算** | Recording input/output/cached tokens per call and converting to cost.<br>记录每次调用的输入/输出/缓存 token，并换算成成本。 | You cannot evaluate or budget an agent you cannot price.<br>你无法评测一个你算不出价格的 Agent，也无法为它做预算。 | [W1](plan/quizzes/week01.md) |

## 2. Structured output & prompts (Week 3)

**2. 结构化输出与提示词（第 3 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **JSON Schema** | A declarative contract describing the shape of a JSON value.<br>一种声明式契约，描述 JSON 值的结构。 | It is the shared language between your pydantic models and the model provider.<br>它是你的 pydantic 模型与模型提供商之间的共同语言。 | [W3](plan/quizzes/week03.md) |
| **JSON mode**<br>**JSON 模式** | Provider setting that guarantees *syntactically valid* JSON — not schema compliance.<br>提供商的一项设置，保证输出*语法上合法*的 JSON——但不保证符合 schema。 | "Valid JSON" still fails your schema; you must validate.<br>「合法的 JSON」仍然可能不符合你的 schema；你必须做校验。 | [W3](plan/quizzes/week03.md) |
| **Structured outputs**<br>**结构化输出** | Provider-enforced schema adherence (e.g. `json_schema`, strict mode).<br>由提供商强制保证符合 schema（例如 `json_schema`、严格模式）。 | Stronger than JSON mode, but limits schema features and provider support.<br>比 JSON 模式更强，但会限制可用的 schema 特性和支持的提供商。 | [W3](plan/quizzes/week03.md) |
| **Constrained decoding**<br>**约束解码** | Decoding restricted by a grammar so invalid tokens cannot be emitted.<br>用语法约束解码过程，使非法 token 根本无法被输出。 | The strongest guarantee; explains why "impossible-to-emit" beats "validate-after".<br>最强的保证；它说明了为什么「根本无法输出」胜过「事后校验」。 | [W3](plan/quizzes/week03.md) |
| **Discriminated union**<br>**可辨识联合（discriminated union）** | A union of schemas distinguished by a required tag field (e.g. `kind`).<br>由一个必填的标签字段（例如 `kind`）来区分的多个 schema 的联合。 | The clean way to model a decision family with different payloads.<br>对载荷各不相同的一族决策进行建模的简洁方式。 | [W3](plan/quizzes/week03.md) |
| **Validation-repair loop**<br>**校验-修复循环** | On schema failure, feed the validation error back once and retry with a bounded attempt count.<br>当 schema 校验失败时，把校验错误回传给模型一次，并在有限的尝试次数内重试。 | Recovers most malformed outputs without hiding failure rates.<br>能挽救大多数格式错误的输出，同时不掩盖失败率。 | [W3](plan/quizzes/week03.md) |
| **Schema failure rate**<br>**schema 失败率** | Fraction of calls whose output fails validation (before and after repair).<br>输出未通过校验的调用所占比例（分别统计修复前和修复后）。 | A first-class metric; it turns a "working" feature into an observable one.<br>一项一等指标；它把一个「能用」的功能变成一个可观测的功能。 | [W3](plan/quizzes/week03.md) |
| **Prompt versioning**<br>**提示词版本管理** | Prompts are immutable assets carrying `id` and `version` — editing history is forbidden, you bump the version instead.<br>提示词是带有 `id` 和 `version` 的不可变资产——禁止修改历史版本，而是提升版本号。 | Prompt edits are code changes; unversioned prompts make regressions unattributable.<br>修改提示词就是修改代码；没有版本的提示词会让回归无法归因。 | [W3](plan/quizzes/week03.md) |
| **Presentation budget**<br>**展示预算** | Hard caps on how much text a decision may show (e.g. headline ≤ 12 words, ≤ 4 next moves).<br>对一个决策可展示文本量的硬上限（例如标题 ≤ 12 个词，后续行动 ≤ 4 条）。 | Prevents the model from ignoring product constraints on brevity.<br>防止模型无视产品对简洁性的约束。 | [W3](plan/quizzes/week03.md) |
| **Cassette (record/replay)**<br>**cassette（录制回放）** | A recorded real interaction replayed in tests for deterministic offline runs.<br>一段录制下来的真实交互，在测试中回放，以实现确定性的离线运行。 | Gives you one real-payload test without network flakiness.<br>让你拥有一个使用真实载荷、又不受网络波动影响的测试。 | [W3](plan/quizzes/week03.md) |

## 3. Loop & tools (Week 2)

**3. 循环与工具（第 2 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **`tool_call`** | The model's request to run a named tool with JSON arguments, carrying an `id`.<br>模型发出的、请求以 JSON 参数运行某个具名工具的请求，带有一个 `id`。 | The `id` is how you match the tool result back to the request.<br>你正是靠这个 `id` 把工具结果与对应的请求匹配起来。 | [W2](plan/quizzes/week02.md) |
| **Native tool calling**<br>**原生工具调用** | Provider-supported structured tool requests rather than parsing text.<br>由提供商原生支持的结构化工具请求，而不是靠解析文本。 | More reliable than text parsing; the first architectural improvement over naive ReAct.<br>比解析文本更可靠；是相对于朴素 ReAct 的第一项架构改进。 | [W2](plan/quizzes/week02.md) |
| **ReAct** | Reasoning + acting loop: model emits a thought/action, environment returns an observation, repeat.<br>推理 + 行动循环：模型输出一个思考/动作，环境返回一个观察结果，如此反复。 | The fundamental agent loop; every framework is a variant of it.<br>最基础的 Agent 循环；所有框架都是它的变体。 | [W2](plan/quizzes/week02.md) |
| **Tool registry**<br>**工具注册表** | A runtime mapping from tool name to schema + handler + metadata (read/write, risk).<br>一个运行时映射，从工具名映射到 schema + 处理函数 + 元数据（读/写、风险等级）。 | One place for discovery, validation, recording and policy — instead of ad-hoc `if` branches.<br>把发现、校验、记录和策略集中到一处——而不是零散的 `if` 分支。 | [W2](plan/quizzes/week02.md) |
| **Error as observation**<br>**错误即观察结果** | Tool failures are returned to the model as observations rather than raised to the caller.<br>工具失败作为观察结果返回给模型，而不是作为异常抛给调用方。 | Lets the agent recover; a crashed loop cannot.<br>让 Agent 有机会恢复；一个崩溃的循环做不到。 | [W2](plan/quizzes/week02.md) |
| **Parallel tool calls**<br>**并行工具调用** | Multiple tool requests in one assistant turn.<br>在一个助手轮次中发出多个工具请求。 | Fewer round-trips and lower latency — but only if handlers are independent and idempotent.<br>更少的往返和更低的延迟——但前提是各处理函数相互独立且幂等。 | [W2](plan/quizzes/week02.md) |
| **`max_steps` / iteration budget**<br>**`max_steps` / 迭代预算** | Hard cap on loop iterations.<br>循环迭代次数的硬上限。 | The primary runaway-cost control; every production loop has one.<br>防止成本失控的首要手段；每个生产环境中的循环都有它。 | [W2](plan/quizzes/week02.md) |
| **Stop condition**<br>**停止条件** | The predicate that ends the loop: final answer, budget exhausted, max steps, no progress.<br>结束循环的判定条件：得到最终答案、预算耗尽、达到最大步数、没有进展。 | Loops that only end on "final answer" hang forever when the model stalls.<br>只在「得到最终答案」时才结束的循环，一旦模型卡住就会永远挂起。 | [W2](plan/quizzes/week02.md) |
| **Budget check at the top**<br>**在循环顶部检查预算** | Verifying token/cost budget *before* each model call, not after.<br>在每次模型调用*之前*而不是之后检查 token/成本预算。 | Checking after the fact means you always overspend by one full turn.<br>事后检查意味着你总会多花掉一整轮的开销。 | [W2](plan/quizzes/week02.md) |
| **Step trace**<br>**步骤 trace** | Structured events emitted per loop step (model call, tool call, result, stop).<br>每个循环步骤输出的结构化事件（模型调用、工具调用、结果、停止）。 | Tracing is how you debug stochastic systems; it must be designed in, not logged ad hoc.<br>追踪是调试随机性系统的手段；它必须在设计时就纳入，而不是临时随手打日志。 | [W2](plan/quizzes/week02.md) |
| **Agent vs workflow**<br>**Agent 与工作流** | Workflow = LLM steps on predefined code paths; agent = model directs its own process and tools.<br>工作流 = 在预先定义的代码路径上执行的 LLM 步骤；Agent = 由模型自己主导执行过程和工具使用。 | The central architectural choice; most "agent" use cases should be workflows.<br>核心的架构选择；大多数所谓「Agent」的用例其实应该是工作流。 | [W2](plan/quizzes/week02.md) |
| **ACI (agent-computer interface)**<br>**ACI（Agent-计算机接口）** | The designed surface of tools, feedback and errors the model interacts with.<br>经过设计的、供模型与之交互的工具、反馈和错误信息的界面。 | SWE-agent showed ACI design changes benchmark scores more than model swaps.<br>SWE-agent 表明，ACI 的设计对基准分数的影响比更换模型还大。 | [W2](plan/quizzes/week02.md) |
| **Write tool / `is_write`**<br>**写工具 / `is_write`** | A tool with side effects, marked explicitly so policy can gate it.<br>带有副作用的工具，会被显式标记出来，以便策略对其设卡。 | Side effects are where trust and audit requirements begin.<br>副作用正是信任和审计要求的起点。 | [W2](plan/quizzes/week02.md) |

## 4. Context engineering & memory (Week 4)

**4. 上下文工程与记忆（第 4 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **Context engineering**<br>**上下文工程** | Curating the smallest high-signal token set for the next model call.<br>为下一次模型调用精心挑选出最小的高信号 token 集合。 | It is the craft that replaced prompt engineering for multi-turn agents.<br>对于多轮 Agent 而言，它是取代了提示词工程的那门手艺。 | [W4](plan/quizzes/week04.md) |
| **Context rot**<br>**上下文腐化（context rot）** | Degradation of recall/accuracy as context length grows.<br>随着上下文长度增长，召回率/准确率随之下降。 | Explains why dumping everything into 1M tokens still fails.<br>解释了为什么把所有东西都塞进 1M token 仍然会失败。 | [W4](plan/quizzes/week04.md) |
| **Compaction**<br>**压缩（compaction）** | Summarising old turns into a bounded carry-forward note and restarting with it.<br>把旧的轮次总结成一份有长度上限的延续笔记，然后带着它重新开始。 | The first lever for long-horizon coherence.<br>保持长周期连贯性的第一根杠杆。 | [W4](plan/quizzes/week04.md) |
| **Carry-forward note**<br>**延续笔记（carry-forward note）** | The durable summary a compactor writes: decisions, open bugs, constraints.<br>由压缩器写下的持久化摘要：决策、未解决的 bug、约束。 | What survives compaction defines what the agent can still do.<br>压缩后留存下来的内容，决定了 Agent 还能做什么。 | [W4](plan/quizzes/week04.md) |
| **Structured note-taking**<br>**结构化笔记** | Agent writes progress to an external file (e.g. `NOTES.md`) and rereads it later.<br>Agent 把进度写到一个外部文件（例如 `NOTES.md`）中，之后再重新读取。 | Turns context from a scratchpad into a recoverable log.<br>把上下文从一张草稿纸变成一份可恢复的日志。 | [W4](plan/quizzes/week04.md) |
| **Priority classes**<br>**优先级类别** | Ranking context by value: pinned constraints > task state > recent turns > observations > history.<br>按价值给上下文排序：固定约束 > 任务状态 > 最近的轮次 > 观察结果 > 历史记录。 | Makes eviction decisions principled rather than "drop the oldest".<br>让淘汰决策有章可循，而不是简单地「丢掉最旧的」。 | [W4](plan/quizzes/week04.md) |
| **Progressive disclosure**<br>**渐进式披露** | Loading detail on demand rather than all at once (files, links, search results).<br>按需加载细节，而不是一次性全部加载（文件、链接、搜索结果）。 | Keeps context small while preserving access to depth.<br>在保持上下文精简的同时，仍能触达深层信息。 | [W4](plan/quizzes/week04.md) |
| **Filesystem as context**<br>**文件系统即上下文** | Using paths, names and directory structure as navigational metadata for retrieval.<br>把路径、文件名和目录结构作为检索时的导航元数据。 | Cheaper and fresher than a vector index for file-shaped knowledge.<br>对于以文件形式存在的知识，比向量索引更便宜、也更新鲜。 | [W4](plan/quizzes/week04.md) |
| **Sub-agent context isolation**<br>**子 Agent 上下文隔离** | Workers explore with their own context and return a distilled summary.<br>工作者在各自的上下文中探索，然后返回一份提炼后的摘要。 | The main way to do deep work without polluting the lead agent's window.<br>在不污染主 Agent 上下文窗口的前提下完成深入工作的主要方式。 | [W4](plan/quizzes/week04.md) |
| **Episodic memory**<br>**情景记忆** | Per-run summaries stored for later recall ("what happened last time").<br>为每次运行保存的摘要，供日后回忆（「上次发生了什么」）。 | Enables cross-session continuity without replaying transcripts.<br>无需回放完整对话记录就能实现跨会话的连续性。 | [W4](plan/quizzes/week04.md) |
| **Semantic memory**<br>**语义记忆** | Durable facts with provenance ("customer X is on plan Y").<br>带有来源（provenance）的持久化事实（「客户 X 使用的是 Y 套餐」）。 | Facts outlive sessions; provenance makes them auditable.<br>事实比会话活得更久；来源让它们可以被审计。 | [W4](plan/quizzes/week04.md) |
| **Provenance**<br>**来源** | Where a remembered fact came from and when.<br>一条被记住的事实来自哪里、何时得到。 | Memory without provenance cannot be trusted or revoked.<br>没有来源的记忆既无法信任，也无法撤销。 | [W4](plan/quizzes/week04.md) |
| **RAG (retrieval-augmented generation)**<br>**RAG（检索增强生成）** | Retrieving relevant documents and placing them in context before generating.<br>在生成之前检索相关文档并把它们放入上下文。 | One retrieval strategy among several; agents often prefer search tools.<br>只是几种检索策略之一；Agent 往往更喜欢使用搜索工具。 | [W4](plan/quizzes/week04.md) |
| **Embedding & cosine similarity**<br>**嵌入与余弦相似度** | Vector representation and the similarity metric used to rank chunks.<br>向量表示，以及用来给文本块排序的相似度度量。 | The core of semantic retrieval; know the failure mode (semantic near-miss).<br>语义检索的核心；要了解它的失败模式（语义上的近似误中）。 | [W4](plan/quizzes/week04.md) |
| **Retention test**<br>**保留率测试** | An explicit test that pinned constraints survive compaction at ≥ a target rate.<br>一个显式测试，验证固定约束在压缩后的留存率 ≥ 目标值。 | Turns "it seems to remember" into a measurable gate.<br>把「它好像记得」变成一道可度量的关卡。 | [W4](plan/quizzes/week04.md) |

## 5. MCP & protocols (Week 5)

**5. MCP 与协议（第 5 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **MCP (Model Context Protocol)**<br>**MCP（模型上下文协议）** | An open standard for exposing tools, resources and prompts to AI applications.<br>一项向 AI 应用暴露工具、资源和提示词的开放标准。 | The interoperability layer; it replaces bespoke per-integration glue.<br>互操作层；它取代了为每个集成单独定制的胶水代码。 | [W5](plan/quizzes/week05.md) |
| **Host / client / server**<br>**宿主 / 客户端 / 服务器** | Host runs the app and model; client is the per-server connector; server exposes capabilities.<br>宿主运行应用和模型；客户端是对应每个服务器的连接器；服务器负责暴露能力。 | Getting the roles right is the difference between a clean integration and a security hole.<br>角色划分是否正确，决定了你得到的是一个干净的集成还是一个安全漏洞。 | [W5](plan/quizzes/week05.md) |
| **Tools vs resources vs prompts**<br>**工具 vs 资源 vs 提示词** | MCP's three primitives: callable actions, readable data, reusable prompt templates.<br>MCP 的三种原语：可调用的动作、可读取的数据、可复用的提示词模板。 | Choosing the wrong primitive exposes action capability where only data was needed.<br>选错原语，会在只需要数据的地方暴露出执行动作的能力。 | [W5](plan/quizzes/week05.md) |
| **stdio transport**<br>**stdio 传输** | Local MCP transport over a child process's standard I/O.<br>通过子进程标准输入输出进行的本地 MCP 传输。 | The simplest, fastest path to a working server; not a network boundary.<br>搭出一个可用服务器的最简单、最快捷的途径；但它不是网络边界。 | [W5](plan/quizzes/week05.md) |
| **Streamable HTTP transport**<br>**Streamable HTTP 传输** | Remote MCP transport over HTTP with streaming responses.<br>基于 HTTP、支持流式响应的远程 MCP 传输。 | Required for multi-client/cloud deployments; changes auth and trust requirements.<br>多客户端/云端部署所必需；它会改变认证和信任方面的要求。 | [W5](plan/quizzes/week05.md) |
| **MCP stateless revision (2026-07-28)**<br>**MCP 无状态修订版（2026-07-28）** | MCP removed the `initialize` handshake and protocol session; every request carries version/identity in `params._meta` and servers answer `server/discover`.<br>MCP 移除了 `initialize` 握手和协议会话；每个请求都在 `params._meta` 中携带版本/身份信息，服务器则响应 `server/discover`。 | Tutorials that still show `initialize` describe the pre-2026 dialect; the 2026 server/client in `agentlab/mcp/` is stateless.<br>仍在展示 `initialize` 的教程描述的是 2026 年之前的方言；`agentlab/mcp/` 中的 2026 版服务器/客户端是无状态的。 | [W5](plan/quizzes/week05.md) |
| **Tool poisoning**<br>**工具投毒** | A malicious tool description that injects instructions into the model's context.<br>恶意的工具描述，会把指令注入到模型的上下文中。 | Descriptions are untrusted input; digest-pinning and review are mitigations.<br>工具描述是不可信输入；摘要固定和人工审查是缓解手段。 | [W5](plan/quizzes/week05.md) |
| **Description digest pinning**<br>**描述摘要固定** | Recording a hash of a tool's description/schema and refusing silent changes.<br>记录工具描述/schema 的哈希值，并拒绝任何悄无声息的变更。 | Detects rug-pull attacks where a server mutates tool semantics after approval.<br>能发现「抽地毯」式攻击，即服务器在获得批准后篡改工具语义。 | [W5](plan/quizzes/week05.md) |
| **OAuth audience binding**<br>**OAuth 受众绑定** | Tokens are scoped to the intended recipient service.<br>令牌的作用范围被限定在预期的接收服务上。 | Prevents a token minted for one server being replayed against another.<br>防止为某个服务器签发的令牌被拿去对另一个服务器重放。 | [W5](plan/quizzes/week05.md) |
| **Confused deputy**<br>**混淆代理（confused deputy）** | A privileged component tricked into acting on an attacker's behalf.<br>一个拥有特权的组件被诱骗去替攻击者办事。 | The core risk of granting an agent broad tool authority.<br>授予 Agent 宽泛工具权限的核心风险。 | [W5](plan/quizzes/week05.md) |

## 6. Orchestration, planning & approval (Week 6)

**6. 编排、规划与审批（第 6 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **Orchestrator-worker**<br>**编排者-工作者** | A lead agent decomposes work and delegates to workers, then synthesises.<br>一个主 Agent 分解工作并委派给工作者，然后汇总结果。 | The one multi-agent pattern with strong production evidence — when the task is genuinely parallelisable.<br>唯一一个有充分生产证据支持的多 Agent 模式——前提是任务真的可以并行。 | [W6](plan/quizzes/week06.md) |
| **Specialist**<br>**专员 Agent（specialist）** | A sub-agent with a narrow toolset and isolated context.<br>一个拥有狭窄工具集和隔离上下文的子 Agent。 | Isolation is what makes delegation safer and cheaper than one giant context.<br>正是隔离让委派比使用一个巨大的上下文更安全、更便宜。 | [W6](plan/quizzes/week06.md) |
| **Squad**<br>**小队（squad）** | A bounded group of specialists coordinated for one objective.<br>为同一个目标而协同工作、有边界的一组专员 Agent。 | SendOS's unit of multi-agent work; the miniature you rebuild in week 6.<br>SendOS 中多 Agent 工作的单位；也是你在第 6 周重建的那个缩小版。 | [W6](plan/quizzes/week06.md) |
| **Typed plan**<br>**带类型的计划** | A structured plan: workstreams, dependencies, acceptance criteria.<br>一份结构化的计划：工作流（workstream）、依赖关系、验收标准。 | Makes plans validatable and replannable instead of prose.<br>让计划可以被校验、可以重新规划，而不是一段散文。 | [W6](plan/quizzes/week06.md) |
| **DAG validation**<br>**DAG 校验** | Checking the plan's dependencies are acyclic and closed over known kinds.<br>检查计划的依赖关系无环，并且只涉及已知的类型。 | Cycles and dangling dependencies are the plan equivalent of infinite loops.<br>环和悬空依赖，相当于计划层面的死循环。 | [W6](plan/quizzes/week06.md) |
| **Replan**<br>**重新规划** | Producing a new plan after a failed step, bounded in retries.<br>在某一步失败后生成一份新计划，且重试次数有上限。 | Plans fail; the ability to replan is what separates orchestration from scripting.<br>计划总会失败；能否重新规划，正是编排与脚本的分水岭。 | [W6](plan/quizzes/week06.md) |
| **Topology classifier**<br>**拓扑分类器** | Rules that map problem shape to execution shape (direct → single specialist → squad → multi-squad).<br>把问题形态映射为执行形态的规则（直接调用 → 单个专员 Agent → 小队 → 多小队）。 | Prevents both over-engineering (squad for one call) and under-powering.<br>既防止过度设计（为一次调用动用一个小队），也防止能力不足。 | [W6](plan/quizzes/week06.md) |
| **Execution shape**<br>**执行形态** | The chosen structure for a run: direct capability, single specialist, single squad, multi-squad.<br>为一次运行选定的结构：直接能力调用、单个专员 Agent、单个小队、多小队。 | The architecture decision that determines cost, latency and control surface.<br>决定成本、延迟和控制面的架构决策。 | [W6](plan/quizzes/week06.md) |
| **Smallest sufficient shape**<br>**足够用的最小形态** | The least complex topology that can satisfy the task; unbacked shapes are reported as limitations.<br>能满足任务需求的最简单拓扑；没有实现支撑的形态会作为限制说明上报。 | The plan's core rule: never guess a smaller shape, never build a bigger one.<br>计划的核心规则：绝不猜测一个更小的形态，也绝不构建一个更大的形态。 | [W6](plan/quizzes/week06.md) |
| **HITL (human-in-the-loop)**<br>**人在回路（HITL）** | A human approves or edits before a consequential action executes.<br>在有重大后果的动作执行之前，由人类批准或修改。 | The control that makes write-capable agents acceptable in enterprises.<br>正是这项控制，让具备写能力的 Agent 能够被企业接受。 | [W6](plan/quizzes/week06.md) |
| **Durable suspend/resume**<br>**持久化挂起/恢复** | Persisting a paused run and resuming it on an external callback.<br>持久化一次暂停的运行，并在外部回调到来时恢复它。 | This is the difference between a demo approval and a real one.<br>这就是演示用审批与真正审批之间的区别。 | [W6](plan/quizzes/week06.md) |
| **Approval binding**<br>**审批绑定** | A proposal bound to actor, tenant, action hash, authority snapshot and expiry.<br>把提案绑定到操作者、租户、动作哈希、授权快照和过期时间。 | Without binding, an approved proposal can be swapped, replayed or executed by the wrong principal.<br>没有绑定，已批准的提案就可能被调包、被重放，或被错误的主体执行。 | [W6](plan/quizzes/week06.md) |
| **Action hash**<br>**动作哈希** | A digest of exactly what will be executed, checked at approval and execution time.<br>对将要执行的确切内容计算出的摘要，在审批时和执行时都会检查。 | Detects post-approval edits.<br>能发现批准之后的篡改。 | [W6](plan/quizzes/week06.md) |
| **Authority snapshot**<br>**授权快照** | The permission state captured when approval was granted.<br>在批准时捕获的权限状态。 | Authority can change between approval and execution; the snapshot is the contract.<br>授权在批准与执行之间可能发生变化；快照就是契约。 | [W6](plan/quizzes/week06.md) |
| **At-most-once execution**<br>**最多一次执行** | A guarantee that an approved action runs no more than once, even on retries.<br>保证一个已批准的动作最多只运行一次，即使发生重试也是如此。 | Duplicate side effects are worse than a failed request.<br>重复的副作用比一次失败的请求更糟糕。 | [W6](plan/quizzes/week06.md) |
| **CAS (compare-and-swap)**<br>**CAS（比较并交换）** | Conditional write used to prevent double-resume/double-execute.<br>一种条件写入，用来防止重复恢复/重复执行。 | The standard primitive for at-most-once under concurrency.<br>在并发下实现最多一次语义的标准原语。 | [W6](plan/quizzes/week06.md) |

## 7. Evals & observability (Week 7)

**7. 评测与可观测性（第 7 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **Eval dataset**<br>**评测数据集** | Versioned cases (inputs, rubric, expected constraints) used to score an agent.<br>用于给 Agent 打分的、有版本的用例集合（输入、评分标准（rubric）、预期约束）。 | Evals are code and data, not a vibe check; version them.<br>评测是代码和数据，而不是凭感觉打分；要给它们做版本管理。 | [W7](plan/quizzes/week07.md) |
| **Outcome eval**<br>**结果评测** | Scores only the final result.<br>只为最终结果打分。 | Cheap and objective, but blind to how the agent got there.<br>便宜且客观，但看不到 Agent 是怎样得出结果的。 | [W7](plan/quizzes/week07.md) |
| **Trajectory eval**<br>**轨迹评测** | Scores the path: tool choices, steps, constraints respected.<br>为路径打分：工具选择、步骤、是否遵守约束。 | Needed when process compliance matters (security, approvals).<br>当过程合规很重要时（安全、审批）就需要它。 | [W7](plan/quizzes/week07.md) |
| **Deterministic-first scoring**<br>**确定性优先打分** | Exhaust exact checks (schema, substring, exit code) before calling a judge.<br>在调用评审之前，先用尽各种精确检查（schema、子串、退出码）。 | Cheaper, faster and more reliable than model judgement.<br>比模型评判更便宜、更快、也更可靠。 | [W7](plan/quizzes/week07.md) |
| **Rubric**<br>**评分标准** | Explicit criteria and levels used to score an output.<br>用于给输出打分的明确标准和等级。 | Makes qualitative judgement reproducible and debuggable.<br>让定性评判变得可复现、可调试。 | [W7](plan/quizzes/week07.md) |
| **LLM-as-judge**<br>**LLM 评审（LLM-as-judge）** | A model scores outputs against a rubric, usually with forced JSON.<br>由一个模型依据评分标准给输出打分，通常强制输出 JSON。 | Scales qualitative grading; must be calibrated, never trusted blindly.<br>让定性评分可以规模化；但必须经过校准，绝不能盲目信任。 | [W7](plan/quizzes/week07.md) |
| **Judge agreement**<br>**评审一致率** | How often the judge matches human labels on a sample.<br>在一个样本上，评审结果与人工标注一致的频率。 | The only credibility a judge has; below ~80% it is noise.<br>这是评审唯一的可信度来源；低于约 80% 就只是噪声。 | [W7](plan/quizzes/week07.md) |
| **pass@1** | Probability the agent succeeds on one attempt.<br>Agent 在一次尝试中成功的概率。 | The standard headline metric for agent tasks.<br>Agent 任务的标准头条指标。 | [W7](plan/quizzes/week07.md) |
| **pass^k** | Probability of succeeding on *all* of k independent attempts.<br>在 k 次独立尝试中*全部*成功的概率。 | Exposes reliability: a 70% pass@1 agent may be far worse at pass^5.<br>暴露出可靠性问题：一个 pass@1 为 70% 的 Agent，在 pass^5 上可能差得多。 | [W7](plan/quizzes/week07.md) |
| **Eval leakage**<br>**评测泄漏** | Tuning on the eval cases until they no longer predict real performance.<br>针对评测用例反复调优，直到它们不再能预测真实表现。 | The most common way eval suites become theatre.<br>评测套件沦为表演的最常见方式。 | [W7](plan/quizzes/week07.md) |
| **Regression gate**<br>**回归关卡** | A CI check that fails when a metric drops below baseline.<br>当某项指标跌破基线时就会失败的 CI 检查。 | Converts evals from a report into a control.<br>把评测从一份报告变成一项控制手段。 | [W7](plan/quizzes/week07.md) |
| **Trace / span**<br>**trace / span（追踪 / 跨度）** | Structured record of a run and its timed sub-operations.<br>对一次运行及其带计时的子操作的结构化记录。 | Traces are the primary debugging and eval substrate.<br>trace 是调试和评测的主要基础。 | [W7](plan/quizzes/week07.md) |

## 8. Security & governance (Week 8)

**8. 安全与治理（第 8 周）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **Direct prompt injection**<br>**直接提示词注入** | The user's message overrides the developer's instructions.<br>用户的消息覆盖了开发者的指令。 | The oldest attack; instruction hierarchy and output vetting are the mitigations.<br>最古老的攻击；指令层级和输出审查是缓解手段。 | [W8](plan/quizzes/week08.md) |
| **Indirect prompt injection**<br>**间接提示词注入** | Malicious instructions arrive via content the agent reads (web page, file, tool result, email).<br>恶意指令通过 Agent 读取的内容到达（网页、文件、工具结果、邮件）。 | The dominant real-world attack on tool-using agents.<br>现实中针对使用工具的 Agent 的主要攻击方式。 | [W8](plan/quizzes/week08.md) |
| **Lethal trifecta**<br>**致命三要素** | Private data + untrusted content + external communication in one agent.<br>私有数据 + 不可信内容 + 对外通信，集于一个 Agent。 | Any two are manageable; all three is exfiltration by design.<br>任意两者都还可控；三者俱全就等于在设计上允许数据外泄。 | [W8](plan/quizzes/week08.md) |
| **Instruction hierarchy**<br>**指令层级** | Explicit precedence between system, developer, user and untrusted content.<br>在系统、开发者、用户和不可信内容之间明确规定的优先级。 | Makes injection a policy violation rather than a coin flip.<br>让注入成为一种策略违规，而不是一次抛硬币。 | [W8](plan/quizzes/week08.md) |
| **Sandbox**<br>**沙箱** | A confined execution environment (paths, time, size, process/container boundary).<br>一个受限的执行环境（路径、时间、大小、进程/容器边界）。 | Tool execution is code execution; confinement is the only reliable control.<br>执行工具就是执行代码；限制是唯一可靠的控制手段。 | [W8](plan/quizzes/week08.md) |
| **Path allowlist**<br>**路径白名单** | Explicitly permitted filesystem roots for read/write tools.<br>为读/写工具明确允许的文件系统根目录。 | Blocks traversal attacks without needing perfect prompt hygiene.<br>无需完美的提示词卫生也能阻止路径穿越攻击。 | [W8](plan/quizzes/week08.md) |
| **Deny-by-default**<br>**默认拒绝** | Start from no permission and require explicit grants.<br>从没有任何权限开始，要求显式授予。 | The only safe default for autonomous systems.<br>对自主系统而言唯一安全的默认值。 | [W8](plan/quizzes/week08.md) |
| **Authority intersection**<br>**授权交集** | Effective permission = intersection over independent grants, never union.<br>有效权限 = 各个独立授权的交集，绝不是并集。 | Prevents one source (or the model) from widening access.<br>防止某一个来源（或模型）扩大访问范围。 | [W8](plan/quizzes/week08.md) |
| **Effective authority**<br>**有效授权** | The computed permission set actually enforced for this action.<br>针对当前动作计算出并实际强制执行的权限集合。 | The object every check should consult; one implementation, one truth.<br>每一项检查都应当查询的对象；一个实现，一个真相。 | [W8](plan/quizzes/week08.md) |
| **Per-tenant scoping**<br>**按租户限定范围** | Every object, cache entry and budget is scoped to one tenant.<br>每个对象、缓存条目和预算都限定在单个租户范围内。 | Multi-tenant leakage is the fastest way to lose enterprise trust.<br>多租户数据泄漏是失去企业信任的最快方式。 | [W8](plan/quizzes/week08.md) |
| **Audit log**<br>**审计日志** | Append-only record of actions with before/after evidence and correlation ids.<br>只追加的动作记录，附带变更前后的证据和关联 ID。 | Audit is evidence, not debugging output; it must be tamper-evident.<br>审计是证据，而不是调试输出；它必须能让篡改留下痕迹。 | [W8](plan/quizzes/week08.md) |
| **Correlation id**<br>**关联 ID** | An id propagated across services to join logs, traces and audit rows.<br>在各服务之间传递的一个 ID，用来把日志、trace 和审计记录关联起来。 | Without it, incident reconstruction is guesswork.<br>没有它，事故复盘就只能靠猜。 | [W8](plan/quizzes/week08.md) |
| **Credential isolation**<br>**凭据隔离** | Secrets never reachable from the sandbox where generated code runs.<br>在运行生成代码的沙箱中，永远无法访问到密钥。 | On injection, the agent cannot exfiltrate what it cannot read.<br>一旦遭到注入，Agent 也无法外泄它读不到的东西。 | [W8](plan/quizzes/week08.md) |
| **Red-team suite**<br>**红队测试套件** | A repeatable set of attacks run against the system, with before/after results.<br>一组可重复执行、针对系统发起的攻击，并记录修复前后的结果。 | Security claims need tests; a suite is how you know a control works.<br>安全声明需要测试；测试套件让你知道某项控制是否真的有效。 | [W8](plan/quizzes/week08.md) |
| **EU AI Act (GPAI / high-risk)**<br>**欧盟《人工智能法案》（GPAI / 高风险）** | Regulation with obligations phased in: general-purpose AI live from Aug 2026, high-risk from Dec 2027.<br>一项分阶段施加义务的法规：通用人工智能相关条款自 2026 年 8 月起生效，高风险条款自 2027 年 12 月起生效。 | Enterprise agent platforms will be asked for evidence; know the timeline.<br>企业级 Agent 平台将会被要求提供证据；要清楚这条时间线。 | [W8](plan/quizzes/week08.md) |

## 9. SendOS-specific (your day job)

**9. SendOS 专属术语（你的日常工作）**

| Term<br>术语 | Definition<br>定义 | Why it matters<br>为什么重要 | Week<br>周次 |
|---|---|---|---|
| **SendOS** | The enterprise .NET agent platform you intern on: decision-first runtime, capability registry, governed assets, traces and a learning loop.<br>你实习所在的企业级 .NET Agent 平台：决策优先的运行时、能力注册表、受治理的资产、trace 以及一个学习循环。 | The curriculum exists to make this codebase legible rather than magic.<br>这门课程存在的意义，就是让这个代码库变得易于理解，而不是像魔法一样神秘。 | [W6](plan/quizzes/week06.md) |
| **`Send.Model.Adapter`** | SendOS's provider layer: adapters per model plus routed completion.<br>SendOS 的提供商层：每个模型一个适配器，外加路由式补全。 | Your week-1 provider seam is the same idea; compare what it adds (budget-aware routing, structured completion).<br>你第 1 周做的 provider 接缝就是同样的思路；对比一下它额外增加了什么（感知预算的路由、结构化补全）。 | [W1](plan/quizzes/week01.md) |
| **`DecisionRuntime`** | SendOS's decision-first execution runtime that produces typed decisions rather than chat replies.<br>SendOS 决策优先的执行运行时，产出带类型的决策，而不是聊天回复。 | The architectural centre of gravity of the platform; week 6 rebuilds a miniature.<br>整个平台的架构重心；第 6 周会重建一个缩小版。 | [W6](plan/quizzes/week06.md) |
| **`DecisionInteraction` family**<br>**`DecisionInteraction` 家族** | The typed decision set: clarification, direct answer, decision, recommendation, action proposal.<br>带类型的决策集合：澄清、直接回答、决策、建议、动作提案。 | Structured outputs are how a platform makes model behaviour governable.<br>结构化输出是平台让模型行为变得可治理的方式。 | [W3](plan/quizzes/week03.md) |
| **`PresentationBudgetEnforcer`** | SendOS component that enforces output shape limits (headline length, number of next moves).<br>SendOS 中强制执行输出形态限制（标题长度、后续行动数量）的组件。 | Shows that product constraints can be enforced structurally, not politely asked for.<br>说明产品约束可以从结构上强制执行，而不是客气地请求模型遵守。 | [W3](plan/quizzes/week03.md) |
| **`IStructuredCompletionHandler`** | SendOS's interface for schema-gated completions.<br>SendOS 中用于经过 schema 把关的补全的接口。 | Week 3's `analyze(text) -> Decision` is its miniature.<br>第 3 周的 `analyze(text) -> Decision` 就是它的缩小版。 | [W3](plan/quizzes/week03.md) |
| **Capability / `CapabilityDefinition`**<br>**能力 / `CapabilityDefinition`** | A declared action with schema, risk level, read/write flag and approval requirement.<br>一个声明式的动作，带有 schema、风险等级、读/写标志和审批要求。 | Capabilities are the unit of tool governance; week 2's registry grows into this.<br>能力是工具治理的单位；第 2 周的注册表最终会成长为它。 | [W2](plan/quizzes/week02.md) |
| **`ICapabilityManifestProvider`** | SendOS's connector-manifest source that feeds the capability registry.<br>SendOS 中为能力注册表提供数据的连接器清单来源。 | Contrast with MCP discovery: manifest-based governance vs protocol-based discovery.<br>与 MCP 的发现机制对比：基于清单的治理 vs 基于协议的发现。 | [W5](plan/quizzes/week05.md) |
| **`TopologyClassifier`** | SendOS component that selects execution shape from problem topology.<br>SendOS 中根据问题拓扑选择执行形态的组件。 | Week 6 rebuilds the rule; it is the best example of architecture-as-decision.<br>第 6 周会重建这条规则；它是「架构即决策」的最佳范例。 | [W6](plan/quizzes/week06.md) |
| **`ExecutionPlan` / `ExecutionShape`** | The typed plan and the chosen structural shape for a run.<br>一次运行的带类型计划，以及选定的结构形态。 | Explains how SendOS avoids both over- and under-orchestration.<br>解释了 SendOS 如何同时避免过度编排和编排不足。 | [W6](plan/quizzes/week06.md) |
| **`ApprovalCheckpoint`** | SendOS's human approval gate: proposal persisted before approval, then executed at most once.<br>SendOS 的人工审批关卡：提案在审批前持久化，然后最多执行一次。 | Week 6's approval state machine is its miniature; the security properties are the lesson.<br>第 6 周的审批状态机就是它的缩小版；其中的安全性质才是要学的重点。 | [W6](plan/quizzes/week06.md) |
| **`ApprovalBinding`** | The binding of approval to actor, tenant, action hash, authority snapshot and expiry.<br>把审批绑定到操作者、租户、动作哈希、授权快照和过期时间。 | The mechanism that stops approval replay and post-approval edits.<br>阻止审批重放和批准后篡改的机制。 | [W6](plan/quizzes/week06.md) |
| **Governance sandwich**<br>**治理三明治** | SendOS's layering of ingress controls, runtime authority checks and egress/audit controls.<br>SendOS 的分层设计：入口控制、运行时授权检查，以及出口/审计控制。 | Explains why every control exists, and what removing one would break.<br>解释了每一项控制为何存在，以及去掉其中一项会破坏什么。 | [W8](plan/quizzes/week08.md) |
| **`Send.Context.Gateway` / `SpecialistContext`** | SendOS's context gateway and the "least-context envelope" passed to specialists.<br>SendOS 的上下文网关，以及传递给专员 Agent 的「最小上下文信封」。 | Data minimisation, not maximal recall — a different objective from a chatbot.<br>追求数据最小化，而不是最大化召回——与聊天机器人的目标不同。 | [W4](plan/quizzes/week04.md) |
| **`Outcome_Trace`** | Append-only trace contract emitted per run/step.<br>按每次运行/每个步骤输出的、只追加的 trace 契约。 | The runtime↔learning contract; week 7's trace store is its miniature.<br>运行时 ↔ 学习之间的契约；第 7 周的 trace 存储就是它的缩小版。 | [W7](plan/quizzes/week07.md) |
| **Trace → candidate → publish loop**<br>**trace → 候选 → 发布循环** | SendOS's learning loop: traces become eval cases, candidates are evidence-gated, humans publish.<br>SendOS 的学习循环：trace 变成评测用例，候选项经过证据关卡筛选，最后由人类发布。 | Research flags this as the most obviously unwired mechanism — a credible contribution area.<br>研究指出这是最明显尚未接线的机制——一个可以做出有说服力贡献的方向。 | [W7](plan/quizzes/week07.md) |
| **`CaseRuntime`** | SendOS's case-level runtime, including durable suspend/resume that is not fully wired.<br>SendOS 的案例级运行时，其中包括尚未完全接线的持久化挂起/恢复。 | The recommended capstone-inspired contribution: a working miniature plus a design proposal.<br>推荐的、受结业项目（capstone）启发的贡献方向：一个可运行的缩小版加一份设计提案。 | [W6](plan/quizzes/week06.md) |
| **`ActionIdempotencyStore`** | SendOS's store for deduplicating actions.<br>SendOS 中用于对动作去重的存储。 | Enables at-most-once execution across retries; week 6 implements the CAS version.<br>使重试情况下的最多一次执行成为可能；第 6 周会实现基于 CAS 的版本。 | [W6](plan/quizzes/week06.md) |

---

**Maintenance:** add a term only when a week introduces it; never let this list exceed the weeks it serves. If a term has no "why it matters" sentence, it is trivia — delete it.

**维护说明：** 只有当某一周引入了某个术语时才把它加进来；绝不要让这份清单超出它所服务的周次范围。如果某个术语写不出「为什么重要」的那句话，它就只是冷知识——删掉它。
