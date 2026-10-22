# The Learning Plan

**学习计划**

**Learner:** Terrence (Yaqi) Chen — full-stack engineer (Java/Spring, C#/.NET, React/TS, AWS), intern on SendOS.

**学习者：** Terrence (Yaqi) Chen——全栈工程师（Java/Spring、C#/.NET、React/TS、AWS），SendOS 实习生。

**Constraints:** 8–12 h/week alongside an internship and NUS coursework. Python primary, C# bridge.

**约束：** 在实习和 NUS 课程之外，每周 8–12 小时。以 Python 为主，C# 用于桥接。

**Horizon:** 9 working weeks + 1 buffer week (~90–110 hours). **Started:** 2026-10-18.

**周期：** 9 个工作周 + 1 个缓冲周（约 90–110 小时）。**开始日期：** 2026-10-18。

**Goal:** go from "I have called LLM APIs" to "I can design, build, evaluate, secure and operate an agent system — and I can read SendOS's agent runtime with expert eyes."

**目标：** 从「我调用过 LLM API」进阶到「我能设计、构建、评测、保护并运维一个 Agent 系统——而且能以专家的眼光读懂 SendOS 的 Agent 运行时」。

---

## 1. Outcome map

**1. 成果地图**

You named four goals. They are not equally served by every week, so the plan weights them explicitly:

你提出了四个目标。并不是每一周都同等地服务于这些目标，因此计划对它们做了明确的权重分配：

| Goal<br>目标 | How the plan serves it<br>计划如何服务于它 | Weeks<br>周次 |
|---|---|---|
| **A. Contribute meaningfully to SendOS faster**<br>**A. 更快地为 SendOS 做出有意义的贡献** | Every week has a SendOS bridge: the same mechanism rebuilt in miniature, then located in the real repo. Capstone is a Mini-SendOS.<br>每周都有一个 SendOS 桥接：先以微缩形式重建同一个机制，再在真实仓库中找到它的位置。结业项目（capstone）就是一个 Mini-SendOS。 | 1–9, strongest 3, 6, 7, 8<br>1–9，其中 3、6、7、8 周最强 |
| **B. Be hireable as an AI/agent engineer**<br>**B. 具备被聘为 AI/Agent 工程师的能力** | Public portfolio: 8 green test suites, a traced agent, an eval report, a capstone demo + architecture write-up.<br>公开的作品集：8 个通过（变绿）的测试套件、一个可追踪的 Agent、一份评测（eval）报告、一个结业项目演示 + 架构总结文章。 | 2–9 |
| **C. Build your own agent product**<br>**C. 打造你自己的 Agent 产品** | Weeks 2–8 cumulatively produce the platform; week 9 ships a web UI and a real end-to-end domain workflow.<br>第 2–8 周逐步累积出这个平台；第 9 周交付一个 Web UI 和一个真实的端到端领域工作流。 | 6–9 |
| **D. Deep technical mastery / research fluency**<br>**D. 深度技术掌握 / 研究素养** | From-scratch builds, weekly paper reading (1 must-read + 1 optional), and a "re-derive from memory" final.<br>从零构建、每周论文阅读（1 篇必读 + 1 篇选读），以及一次「凭记忆重新推导」的期末练习。 | 1–10 |

**Conflict rule:** when short on time, protect A and D (the compounding ones). B and C are outputs of doing A+D well, not separate tracks.

**冲突规则：** 时间不够时，优先保住 A 和 D（具有复利效应的那两个）。B 和 C 是把 A+D 做好之后的产出，而不是单独的路线。

---

## 2. Design principles

**2. 设计原则**

1. **From scratch first, frameworks second.** You implement the provider seam, loop, compaction, MCP discovery, and eval harness yourself. In weeks 6–9 you then read framework source (LangGraph, OpenAI Agents SDK, Microsoft Agent Framework) and recognise every abstraction.

   **先从零实现，再看框架。** 你会亲手实现 provider 接缝（seam）、循环、压缩（compaction）、MCP 发现机制和评测 harness（运行框架）。然后在第 6–9 周阅读框架源码（LangGraph、OpenAI Agents SDK、Microsoft Agent Framework），并认出其中的每一个抽象。

2. **Tests are the specification.** Each week has a test suite that fails before you build and passes when you are done. It removes the "did I learn it?" ambiguity that kills self-study.

   **测试就是规格说明。** 每周都有一个测试套件，在你动手构建之前是失败的，完成后则全部通过。它消除了「我学会了吗？」这种足以扼杀自学的模糊感。

3. **70 / 20 / 10.** 70% building, 20% reading, 10% reflecting and writing. Reading without a build is entertainment.

   **70 / 20 / 10。** 70% 构建，20% 阅读，10% 反思与写作。不伴随构建的阅读只是娱乐。

4. **Vertical slices.** Each week's code is reused by the next; the capstone is the composition of weeks 1–8, not a ninth unrelated project.

   **纵向切片。** 每周的代码都会被下一周复用；结业项目是第 1–8 周成果的组合，而不是第九个毫不相关的项目。

5. **Trace before you optimise.** From week 2 every run emits structured events. By week 7 you already own the data needed for evals.

   **先追踪，再优化。** 从第 2 周起，每次运行都会输出结构化事件。到第 7 周时，你已经拥有了评测所需的数据。

6. **The six runtime duties.** Research identifies the harness — not the model — as the real differentiator, and decomposes it into six duties: *observation, context, control, action, state, verification*. Every week maps to at least one; weeks 2, 6 and 8 exist specifically because action and verification are separate duties, not afterthoughts. See [`docs/research/01-agent-architecture-sota.md`](../research/01-agent-architecture-sota.md) §0–1.

   **运行时的六项职责。** 研究表明，真正的差异化因素是 harness 而不是模型，并把它分解为六项职责：*观察、上下文、控制、行动、状态、验证*。每一周至少对应其中一项；第 2、6、8 周之所以专门存在，正是因为行动和验证是独立的职责，而不是事后补充。参见 [`docs/research/01-agent-architecture-sota.md`](../research/01-agent-architecture-sota.md) §0–1。

7. **Least autonomy that passes the eval.** Prefer a workflow over an agent, one agent over many, a deterministic check over a model call. Weeks 6–8 make this measurable instead of ideological.

   **能通过评测的最小自主度。** 优先选择工作流而非 Agent，单个 Agent 而非多个，确定性检查而非模型调用。第 6–8 周会让这一点变得可度量，而不是停留在理念层面。

8. **Spaced repetition over cramming.** 5 flashcards + a 150-word teach-back every week. [`docs/glossary.md`](../glossary.md) is the canonical term list.

   **间隔重复，而不是临时突击。** 每周 5 张闪卡 + 一段 150 词的复述讲解（teach-back）。[`docs/glossary.md`](../glossary.md) 是权威的术语表。

---

## 3. Phase structure

**3. 阶段结构**

```
Phase 1  FOUNDATIONS (weeks 1–3)      Build the primitive: model, loop, tools, typed output.
Phase 2  CAPABILITY  (weeks 4–6)      Make it capable: context, memory, interoperability, planning.
Phase 3  PRODUCTION  (weeks 7–9)      Make it trustworthy: evals, security, governance, capstone.
Buffer   CONSOLIDATION (week 10)      Re-derive from memory, portfolio, interviews.
```

Each week is a contract:

每一周都是一份契约：

- **Inputs:** previous week's green tests, this week's brief and concept note.

  **输入：** 上一周已通过的测试、本周的任务说明和概念笔记。

- **Outputs:** green `tests/weekNN`, a lab artifact, a weekly review, 5 flashcards.

  **输出：** 通过的 `tests/weekNN`、一个实验（lab）产出物、一份每周复盘、5 张闪卡。

- **Gate:** you cannot start week N+1 until week N's gate passes (see [`CHECKPOINTS.md`](CHECKPOINTS.md)).

  **关卡：** 第 N 周的关卡通过之前，你不能开始第 N+1 周（参见 [`CHECKPOINTS.md`](CHECKPOINTS.md)）。

### Companion textbook (optional, time-boxed)

**配套教材（可选，限定时间）**

The curriculum adopts **[*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book)** (Bojie Li, v2.0, 2026, Apache-2.0) as its companion textbook — deep theory plus 109 runnable experiments. The local copy and full assessment live in [`docs/books/ai-agents-in-depth/`](../books/ai-agents-in-depth/README.md).

本课程采用 **[*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book)**（Bojie Li，v2.0，2026，Apache-2.0）作为配套教材——深入的理论加上 109 个可运行的实验。本地副本和完整评估位于 [`docs/books/ai-agents-in-depth/`](../books/ai-agents-in-depth/README.md)。

Use it in exactly three moments:

只在以下三个时机使用它：

1. **Before the week:** read the mapped 30–60 minute section to build vocabulary.

   **一周开始之前：** 阅读对应的 30–60 分钟章节，建立词汇基础。

2. **When a test fails for a conceptual reason:** re-read that section — it usually explains the *why* behind the failing contract.

   **当测试因为概念上的原因失败时：** 重读那一节——它通常能解释失败契约背后的*原因*。

3. **After the gate:** optionally run one of the chapter's experiments and compare its implementation with yours.

   **通过关卡之后：** 可选地运行该章的一个实验，并把它的实现与你的进行比较。

It never replaces a lab. If the week is short, read nothing and ship green tests. Week-by-week mapping, reading paths (6 h / 20 h / 60 h), selected experiments and the gap analysis — including why weeks 6 and 8 stay repo-primary — are in [`CHAPTER-MAP.md`](../books/ai-agents-in-depth/CHAPTER-MAP.md).

它永远不能替代实验。如果这一周时间紧张，就什么都不读，只交付通过的测试。逐周对应关系、阅读路径（6 小时 / 20 小时 / 60 小时）、精选实验以及差距分析——包括为什么第 6 周和第 8 周仍以本仓库为主——都在 [`CHAPTER-MAP.md`](../books/ai-agents-in-depth/CHAPTER-MAP.md) 中。

---

## 4. Week-by-week

**4. 逐周安排**

### Week 0 — Setup and baseline (3 h)

**第 0 周 — 环境搭建与基线（3 小时）**

**Objective:** a working environment and an honest baseline.

**目标：** 一个可用的环境和一个诚实的基线。

- Run `.\tasks.ps1 setup` (Windows) / `./tasks.sh setup` (macOS/Linux); fix `doctor` until clean.

  运行 `.\tasks.ps1 setup`（Windows）/ `./tasks.sh setup`（macOS/Linux）；修复问题直到 `doctor` 检查无问题。

- Run `pytest` (foundation green) and `pytest -m week` (all lab tests red — expected).

  运行 `pytest`（基础测试通过）和 `pytest -m week`（所有实验测试都是红的——这是预期的）。

- Make one live call with a throwaway script; record tokens and cost in `notes/week00-baseline.md`, and record latency from the CLI's wall-clock/elapsed time (the provider adapter returns `Usage` only — latency is measured by the caller's span and, from week 2, by the `model_call` trace event's `duration_ms`).

  用一个临时脚本发起一次真实调用；在 `notes/week00-baseline.md` 中记录 token 和成本，并根据 CLI 的挂钟/耗时记录延迟（模型提供商（provider）适配器只返回 `Usage`——延迟由调用方的 span 度量，从第 2 周起则由 `model_call` trace 事件的 `duration_ms` 度量）。

- Write your baseline answers: what is a token, why does streaming exist, what can go wrong in a retry.

  写下你的基线答案：什么是 token，为什么需要流式输出，重试时可能出什么问题。

**Gate:** `doctor` clean, foundation tests green, one recorded live call with cost.

**关卡：** `doctor` 检查无问题，基础测试通过，记录一次带成本的真实调用。

**Research:** read [`docs/research/04-learning-resources.md`](../research/04-learning-resources.md) §"2026 state of play".

**研究资料：** 阅读 [`docs/research/04-learning-resources.md`](../research/04-learning-resources.md) §"2026 state of play"（2026 年现状）。

---

### Week 1 — The model, demystified (8–10 h)

**第 1 周 — 揭开模型的神秘面纱（8–10 小时）**

**Objective:** stop treating the API as magic. Understand the wire format, streaming, retries and the provider seam.

**目标：** 不再把 API 当作魔法。理解线上传输格式、流式输出、重试和 provider 接缝。

**Build** (`agentlab/providers/openai_compat.py`):

**构建**（`agentlab/providers/openai_compat.py`）：

1. `_build_payload` — message/tool mapping, omit empty fields, `extra` override last.

   `_build_payload`——消息/工具映射，省略空字段，最后应用 `extra` 覆盖。

2. `_parse_response` — choices, tool calls, usage, raw payload retention.

   `_parse_response`——choices、工具调用、用量，保留原始载荷。

3. `complete` — POST, retry 429/5xx/transport with `Retry-After` + exponential backoff + jitter, error taxonomy.

   `complete`——POST 请求，对 429/5xx/传输层错误进行重试，配合 `Retry-After` + 指数退避 + 抖动（jitter），并建立错误分类体系。

4. `stream` — SSE parsing with fragmented frames, delta assembly, usage + `done` events.

   `stream`——处理分片帧的 SSE 解析、增量（delta）组装、用量 + `done` 事件。

**Lab deliverable:** `agentlab chat` streams responses and prints per-turn token/cost. `pytest tests/week01 -m week` green.

**实验交付物：** `agentlab chat` 以流式输出响应，并打印每轮的 token/成本。`pytest tests/week01 -m week` 通过。

**Concepts to be able to explain:** tokens vs characters, context window, system/user/assistant/tool roles, temperature/top-p, `finish_reason`, prompt caching, why retries belong in the adapter, why streaming is a protocol not a feature.

**需要能够讲解的概念：** token 与字符的区别、上下文窗口、system/user/assistant/tool 角色、temperature/top-p、`finish_reason`、提示词缓存、为什么重试应放在适配器中、为什么流式输出是一种协议而不是一个功能。

**Reading (2 h):** provider API reference (OpenAI *and* DeepSeek — compare), research 02 §3 (model-provider capabilities).

**阅读（2 小时）：** 提供商 API 参考文档（OpenAI *和* DeepSeek——对比着看），研究资料 02 §3（模型提供商能力）。

**SendOS bridge (30 min):** `apps/Send.Model.Adapter` structure; identify the three things your provider seam does that its adapters also do, and the two it does not (budget-aware routing, structured completion — you build those in weeks 3 and 8).

**SendOS 桥接（30 分钟）：** `apps/Send.Model.Adapter` 的结构；找出你的 provider 接缝所做的、它的适配器也在做的三件事，以及它在做而你的接缝没做的两件事（感知预算的路由、结构化补全——你会在第 3 周和第 8 周构建它们）。

**Stretch:** add an Anthropic adapter (different system-prompt placement, content blocks, tool schema) behind the same `Provider` protocol.

**拓展：** 在同一个 `Provider` 协议之后增加一个 Anthropic 适配器（系统提示词的放置位置、内容块、工具 schema 都不同）。

---

### Week 2 — Tools and the agent loop (10–12 h)

**第 2 周 — 工具与 Agent 循环（10–12 小时）**

**Objective:** build the loop yourself. This is the single most important week.

**目标：** 亲手构建循环。这是最重要的一周。

**Build** (`agentlab/loop/`, `agentlab/tools/builtin.py`):

**构建**（`agentlab/loop/`、`agentlab/tools/builtin.py`）：

- `ToolRegistry` usage: pydantic input models → JSON Schema → handler, errors-as-observations, output truncation (provided infra; you extend it).

  `ToolRegistry` 的用法：pydantic 输入模型 → JSON Schema → 处理器，把错误当作观察结果，输出截断（基础设施已提供；由你来扩展）。

- `react.py`: model → tool calls → execute → tool messages → repeat; `max_steps`, token/cost budget checks at the *top* of each iteration; stop conditions; step-level trace events.

  `react.py`：模型 → 工具调用 → 执行 → 工具消息 → 重复；`max_steps`，在每次迭代的*开头*做 token/成本预算检查；停止条件；步骤级 trace 事件。

- `runner.py`: run config, result type (final answer, steps, usage, trace ref, stop reason), `MaxStepsExceeded` partial results.

  `runner.py`：运行配置、结果类型（最终答案、步骤、用量、trace 引用、停止原因），`MaxStepsExceeded` 时返回部分结果。

- `builtin.py`: `calculator`, `read_file`, `list_dir` (sandboxed to a workspace), `write_file` (marked `is_write=True`), `search_text`.

  `builtin.py`：`calculator`、`read_file`、`list_dir`（沙箱限制在工作区内）、`write_file`（标记为 `is_write=True`）、`search_text`。

- A CLI agent (`agentlab chat --tools`) with `/trace` to show the last run's events.

  一个 CLI Agent（`agentlab chat --tools`），带有 `/trace` 命令，用于显示上一次运行的事件。

**Lab deliverable:** agent completes 5 golden tasks (arithmetic, file read, multi-step edit, graceful tool error, budget stop) with a complete trace. `pytest tests/week02 -m week` green.

**实验交付物：** Agent 完成 5 个黄金任务（算术、读文件、多步编辑、优雅处理工具错误、预算停止），并附带完整的 trace。`pytest tests/week02 -m week` 通过。

**Concepts:** native tool calling vs ReAct text parsing, parallel tool calls, observation formatting, loop termination, budget enforcement, error recovery, the difference between "agent" and "workflow".

**概念：** 原生工具调用与 ReAct 文本解析的对比、并行工具调用、观察结果格式化、循环终止、预算强制执行、错误恢复、「Agent」与「工作流」的区别。

**Reading (2 h):** research 01 §1–2; Anthropic *Building effective agents* (linked in research 04).

**阅读（2 小时）：** 研究资料 01 §1–2；Anthropic 的 *Building effective agents*（链接见研究资料 04）。

**SendOS bridge:** `CapabilityDefinition`, capability registry, `DirectCapabilityHandler`; compare their typed execution plan with your loop. Note what SendOS adds: risk level, approval requirement, read vs write.

**SendOS 桥接：** `CapabilityDefinition`、能力注册表、`DirectCapabilityHandler`；把它们的类型化执行计划与你的循环进行比较。留意 SendOS 额外增加了什么：风险等级、审批要求、读与写的区分。

**Stretch:** implement the loop twice — text-parsed ReAct and native tool calling — and write 150 words on when each is preferable.

**拓展：** 把循环实现两遍——基于文本解析的 ReAct 和原生工具调用——并写 150 词说明各自在什么情况下更合适。

---

### Week 3 — Structured output, prompts as assets, deterministic tests (8–10 h)

**第 3 周 — 结构化输出、提示词即资产、确定性测试（8–10 小时）**

**Objective:** make model output a typed contract instead of a paragraph.

**目标：** 让模型输出成为一份类型化的契约，而不是一段文字。

**Build** (`agentlab/schemas/`):

**构建**（`agentlab/schemas/`）：

- `structured.py`: pydantic → JSON Schema → constrained request; validate; **never** surface invalid output as valid.

  `structured.py`：pydantic → JSON Schema → 受约束的请求；校验；**永远不要**把无效输出当作有效输出呈现出来。

- `repair.py`: one repair retry that feeds validation errors back; bounded attempts; metrics on failure rate.

  `repair.py`：一次把校验错误反馈回去的修复重试；有上限的尝试次数；失败率指标。

- `prompts.py`: versioned prompt templates (`id`, `version`, `render`), so a prompt change is a reviewable diff. The version bump *is* the immutable edit — there is no separate content hash to drift out of sync.

  `prompts.py`：带版本的提示词模板（`id`、`version`、`render`），这样提示词的改动就是一个可审查的 diff。版本号的提升*本身*就是不可变的编辑——不存在一个可能与之不同步的独立内容哈希。

- A typed `Decision` family in the spirit of SendOS: `ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal` with presentation budgets (headline ≤ 12 words, ≤ 2 sentences of meaning, ≤ 4 next moves).

  一个秉承 SendOS 思路的类型化 `Decision` 族：`ClarificationPrompt | DirectAnswer | Decision | Recommendation | ActionProposal`，带有呈现预算（标题 ≤ 12 个词，含义 ≤ 2 句话，后续动作 ≤ 4 个）。

- Cassette-based tests: record one real interaction, replay in CI. **Scrub before committing:** recorded bodies can contain personal data, tenant identifiers, secrets and cost metadata — redact or synthesise them, and never record with a production key.

  基于 cassette（录制回放）的测试：录制一次真实交互，在 CI 中回放。**提交前要清洗：** 录制下来的内容可能包含个人数据、租户标识、密钥和成本元数据——要把它们脱敏或替换为合成数据，并且永远不要用生产环境的密钥来录制。

**Lab deliverable:** `StructuredExtractor(provider).extract(messages, DecisionUnion) -> ExtractionResult[Decision]` with schema enforcement, bounded repair, and a failure-rate report over 20 cases. `pytest tests/week03 -m week` green, offline.

**实验交付物：** `StructuredExtractor(provider).extract(messages, DecisionUnion) -> ExtractionResult[Decision]`，具备 schema 强制、有界修复，以及一份覆盖 20 个用例的失败率报告。`pytest tests/week03 -m week` 离线通过。

**Concepts:** JSON mode vs structured outputs vs grammar-constrained decoding, schema design for models, discriminated unions, retry economics, prompt versioning, replay testing.

**概念：** JSON 模式、结构化输出与语法约束解码的对比，面向模型的 schema 设计，可辨识联合（discriminated union），重试的经济性，提示词版本管理，回放测试。

**Reading (2 h):** research 01 §3 (context engineering) + research 02 §3; provider structured-output docs.

**阅读（2 小时）：** 研究资料 01 §3（上下文工程）+ 研究资料 02 §3；提供商的结构化输出文档。

**SendOS bridge:** `IStructuredCompletionHandler`, `JsonSchemaValidator` (hand-rolled subset), `DecisionInteraction` family, `PresentationBudgetEnforcer`. Note their choice: validate-after rather than impossible-to-emit — and when that is the right trade.

**SendOS 桥接：** `IStructuredCompletionHandler`、`JsonSchemaValidator`（手写的子集实现）、`DecisionInteraction` 族、`PresentationBudgetEnforcer`。留意他们的选择：事后校验，而不是让无效输出无法生成——以及在什么情况下这是正确的权衡。

**Stretch:** measure the schema failure rate for three levels of nesting depth; write up when hand-rolled validation beats provider-native schemas.

**拓展：** 度量三种嵌套深度下的 schema 失败率；写一篇说明手写校验在什么情况下优于提供商原生 schema 的总结。

---

### Week 4 — Context engineering and memory (10–12 h)

**第 4 周 — 上下文工程与记忆（10–12 小时）**

**Objective:** treat context as a budget. Make a long task survive without losing state.

**目标：** 把上下文当作预算来对待。让一个长任务在不丢失状态的情况下坚持到底。

**Build** (`agentlab/context/`):

**构建**（`agentlab/context/`）：

- `window.py`: token estimation, priority classes (pinned constraints > task state > recent turns > observations > history), budget policy.

  `window.py`：token 估算、优先级分类（固定约束 > 任务状态 > 最近几轮对话 > 观察结果 > 历史）、预算策略。

- `compaction.py`: summarise old turns into a bounded "carry-forward" note; prune stale tool outputs; verify task state survives (a post-compaction retention test).

  `compaction.py`：把旧的对话轮次总结成一份有长度上限的延续笔记（carry-forward note）；剪除过时的工具输出；验证任务状态得以保留（压缩后的保留测试）。

- `retrieval.py`: chunking, a from-scratch embedding interface (deterministic fake + one real provider), cosine search with numpy, then a sqlite-backed store; compare with pgvector in a note.

  `retrieval.py`：分块、一个从零实现的 embedding 接口（确定性的假实现 + 一个真实提供商）、用 numpy 做余弦检索，然后是基于 sqlite 的存储；在笔记中与 pgvector 进行比较。

- `memory.py`: episodic (run summaries), semantic (facts with provenance), working (scratchpad); consolidation rule; when NOT to add memory.

  `memory.py`：情景记忆（运行摘要）、语义记忆（带来源（provenance）的事实）、工作记忆（草稿区）；整合规则；什么时候*不*应该添加记忆。

**Lab deliverable:** the week-2 agent completes a 20-turn research task under a 12k-token budget with measurable retention, plus a cost comparison before/after. **Retention target:** ≥ 90% of pinned constraints and task state survive compaction. Treat that threshold as a *local invariant you define and test*, not a published benchmark — the point is that you chose a number, measured it, and can detect a regression.

**实验交付物：** 第 2 周的 Agent 在 12k token 预算内完成一个 20 轮的研究任务，保留率可度量，并附上前后成本对比。**保留目标：** ≥ 90% 的固定约束和任务状态在压缩后依然保留。把这个阈值当作*你自己定义并测试的本地不变量*，而不是一个公开的基准——关键在于你选定了一个数字、度量了它，并且能够发现回归。

**Concepts:** context rot, attention budget, progressive disclosure, filesystem-as-context, sub-agent context isolation, RAG vs long context, memory benchmarks, provenance.

**概念：** 上下文腐化（context rot）、注意力预算、渐进式披露、把文件系统当作上下文、子 Agent 上下文隔离、RAG 与长上下文的对比、记忆基准测试、来源。

**Reading (2 h):** research 01 §3–4 (read the context-rot section twice); Anthropic context-management write-up.

**阅读（2 小时）：** 研究资料 01 §3–4（上下文腐化那一节读两遍）；Anthropic 关于上下文管理的文章。

**SendOS bridge:** `Send.Context.Gateway`, the "least-context envelope" (`SpecialistContext`), semantic retriever + pgvector adapter. Their guarantee is *data minimisation*, not maximal recall — different objective from a chatbot.

**SendOS 桥接：** `Send.Context.Gateway`、「最小上下文信封」（`SpecialistContext`）、语义检索器 + pgvector 适配器。它们保证的是*数据最小化*，而不是最大召回——这与聊天机器人的目标不同。

**Stretch:** intentionally poison the context with a contradicting instruction and design a defence.

**拓展：** 故意用一条相互矛盾的指令污染上下文，并设计一种防御手段。

---

### Week 5 — MCP and interoperability (8–10 h)

**第 5 周 — MCP 与互操作性（8–10 小时）**

**Objective:** stop writing bespoke integrations. Build both sides of the protocol.

**目标：** 不再编写定制的集成。把协议的两端都构建出来。

> **Important:** the MCP spec was redesigned in 2026 and is now **stateless** — the `initialize` handshake and session ids were **removed**, `server/discover` is mandatory, and `_meta` carries version negotiation. Read the current changelog *before* coding; most tutorials in the wild still describe the removed 2025 flow. Deployed servers may lag the spec, so your lab brief must state which revision it implements. See research 01 §10 and research 02 §1.
>
> **重要：** MCP 规范在 2026 年经过了重新设计，现在是**无状态**的——`initialize` 握手和会话 id 已被**移除**，`server/discover` 是必需的，版本协商由 `_meta` 承载。*在写代码之前*先阅读当前的变更日志；网上的大多数教程描述的仍然是已被移除的 2025 年流程。已部署的服务器可能落后于规范，所以你的实验任务说明必须注明它实现的是哪个修订版本。参见研究资料 01 §10 和研究资料 02 §1。

**Build** (`agentlab/mcp/`):

**构建**（`agentlab/mcp/`）：

- `server.py`: expose 3 tools + 1 resource over stdio; JSON-RPC framing; capability declaration; error codes.

  `server.py`：通过 stdio 暴露 3 个工具 + 1 个资源；JSON-RPC 帧格式；能力声明；错误码。

- `client.py`: connect, discover capabilities, map remote tools into `ToolRegistry`, invoke, handle failures/timeouts.

  `client.py`：连接、发现能力、把远程工具映射到 `ToolRegistry` 中、调用、处理失败/超时。

- `security.py`: server trust list, tool-description digest pinning, allowlist, "never pass through user tokens".

  `security.py`：服务器信任列表、工具描述摘要固定（digest pinning）、允许列表、「永不透传用户 token」。

- Wire the client into the week-2 loop and use a remote tool inside a multi-step task.

  把客户端接入第 2 周的循环，并在一个多步任务中使用远程工具。

**Lab deliverable:** a working MCP server (`python -m agentlab.mcp.server`) + client that completes a task using a remote tool; a security checklist pass. `pytest tests/week05 -m week` green.

**实验交付物：** 一个可用的 MCP 服务器（`python -m agentlab.mcp.server`）+ 客户端，能使用远程工具完成一个任务；通过安全检查清单。`pytest tests/week05 -m week` 通过。

**Concepts:** hosts/clients/servers, tools vs resources vs prompts, transports (stdio vs streamable HTTP), auth (OAuth, audience binding), tool poisoning, confused deputy, MCP vs A2A vs plain function calling.

**概念：** 宿主/客户端/服务器，工具、资源与提示词的区别，传输方式（stdio 与可流式 HTTP 的对比），鉴权（OAuth、受众绑定），工具投毒，混淆代理，MCP、A2A 与普通函数调用的对比。

**Reading (2 h):** the current MCP spec + changelog; research 02 §1.

**阅读（2 小时）：** 当前的 MCP 规范 + 变更日志；研究资料 02 §1。

**SendOS bridge:** connector manifests → registry (`ICapabilityManifestProvider`) vs MCP discovery; execution origin stamping; where a standard protocol would reduce SendOS's bespoke connector surface, and where it would not (governed entitlements).

**SendOS 桥接：** 连接器清单 → 注册表（`ICapabilityManifestProvider`）与 MCP 发现机制的对比；执行来源标记；标准协议在哪些地方能缩减 SendOS 定制连接器的范围，又在哪些地方不能（受治理的授权）。

**Stretch:** expose your agent itself over A2A and explain what the agent card must and must not reveal.

**拓展：** 通过 A2A 暴露你的 Agent 本身，并解释 agent card 必须披露什么、不能披露什么。

---

### Week 6 — Planning, orchestration and human approval (10–12 h)

**第 6 周 — 规划、编排与人工审批（10–12 小时）**

**Objective:** learn when to use more than one agent — and how to keep a human in the loop safely.

**目标：** 学会什么时候该使用多个 Agent——以及如何安全地让人保持在回路中。

**Build** (`agentlab/orchestrator/`):

**构建**（`agentlab/orchestrator/`）：

- `plan.py`: typed plan (workstreams, dependencies, acceptance criteria), validate (acyclic, closed kinds), replan on failure.

  `plan.py`：类型化的计划（工作流线、依赖关系、验收标准），校验（无环、封闭的类型集合），失败时重新规划。

- `specialist.py`: sub-agents with isolated context, narrow tool sets, structured hand-off artifacts (never full transcripts).

  `specialist.py`：拥有隔离上下文、精简工具集和结构化交接产物（绝不是完整对话记录）的子 Agent。

- `orchestrator.py`: route by topology — one capability node → direct call; one reasoning node → single specialist; ≥2 connected nodes → one squad; ≥2 components → multi-squad. Unbacked shape → limitation, never a guessed smaller shape. (This is SendOS's `TopologyClassifier` rule, rebuilt.)

  `orchestrator.py`：按拓扑路由——一个能力节点 → 直接调用；一个推理节点 → 单个专员 Agent（specialist）；≥2 个相互连接的节点 → 一个小队（squad）；≥2 个组件 → 多小队。没有支撑的形态 → 报告局限，绝不猜测一个更小的形态。（这就是重建后的 SendOS `TopologyClassifier` 规则。）

- `approval.py`: proposal persisted **before** approval; `ApprovalBinding` (actor, tenant, action hash, authority snapshot, expiry); state machine; at-most-once execution; replay and post-approval-edit rejection.

  `approval.py`：提案在审批**之前**就被持久化；`ApprovalBinding`（执行者、租户、动作哈希、权限快照、过期时间）；状态机；至多一次执行；拒绝重放和审批后的篡改。

- Budget per workstream, aggregated at the orchestrator.

  每条工作流线各有预算，并在编排者处汇总。

**Lab deliverable:** mini-Squad for a business decision ("should we discount this deal?") with: meta-orchestrator → 1–2 specialists → typed decision → approval-gated write → audit row. A test proves an edited/replayed/expired approval cannot execute. `pytest tests/week06 -m week` green.

**实验交付物：** 一个用于商业决策（「这笔交易要不要打折？」）的迷你小队，包含：元编排者 → 1–2 个专员 → 类型化决策 → 经审批把关的写入 → 审计记录行。一个测试证明被篡改/重放/过期的审批无法执行。`pytest tests/week06 -m week` 通过。

**Concepts:** orchestrator-worker, handoff vs manager, context isolation, plan-and-execute vs ReAct, topology-driven shape selection, smallest sufficient shape, HITL as durable suspend/resume, approval binding.

**概念：** 编排者-工作者模式、交接（handoff）与管理者模式的对比、上下文隔离、计划-执行与 ReAct 的对比、拓扑驱动的形态选择、最小的足够形态、作为持久化挂起/恢复的人在回路（HITL）、审批绑定。

**Reading (2 h):** research 01 §6 + §2; Section 4.1/4.5 of [`docs/sendos/CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md).

**阅读（2 小时）：** 研究资料 01 §6 + §2；[`docs/sendos/CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) 的第 4.1/4.5 节。

**SendOS bridge:** decision-first runtime, `ExecutionPlan`, `ExecutionShape`, `ApprovalCheckpoint`, `EffectiveAuthority`, ADR-0001 (topology selection). This is the highest-value week for your day job — plan to demo the miniature to your team.

**SendOS 桥接：** 决策优先的运行时、`ExecutionPlan`、`ExecutionShape`、`ApprovalCheckpoint`、`EffectiveAuthority`、ADR-0001（拓扑选择）。这是对你日常工作价值最高的一周——计划好向团队演示你的微缩实现。

**Stretch:** implement durable suspend/resume (SQLite + resume on callback, CAS against double-resume). This is SendOS's unwired `CaseRuntime`; a working miniature is a credible contribution proposal.

**拓展：** 实现持久化的挂起/恢复（SQLite + 回调时恢复，用 CAS 防止重复恢复）。这就是 SendOS 中尚未接线的 `CaseRuntime`；一个可运行的微缩实现就是一份可信的贡献提案。

---

### Week 7 — Evals and observability (8–10 h)

**第 7 周 — 评测与可观测性（8–10 小时）**

**Objective:** turn "it seems better" into a regression gate.

**目标：** 把「看起来更好了」变成一道回归关卡。

**Build** (`agentlab/evals/`):

**构建**（`agentlab/evals/`）：

- `dataset.py`: eval cases as versioned data (JSONL) with inputs, rubric, weights, expected constraints.

  `dataset.py`：把评测用例作为带版本的数据（JSONL），包含输入、评分标准（rubric）、权重和预期约束。

- `harness.py`: run an agent factory over a dataset; capture traces + outputs; score with deterministic checks first; write a report.

  `harness.py`：在数据集上运行一个 Agent 工厂；捕获 trace + 输出；先用确定性检查打分；生成报告。

- `judges.py`: rubric-based LLM judge with forced JSON; measure agreement against 20–30 human labels; report pass@1 and **pass^k** (reliability across repeats).

  `judges.py`：基于评分标准、强制输出 JSON 的 LLM 评审（LLM-as-judge）；用 20–30 个人工标注度量一致率；报告 pass@1 和 **pass^k**（多次重复下的可靠性）。

- `report.py`: markdown/HTML report with regressions, cost, latency, failure taxonomy.

  `report.py`：包含回归、成本、延迟和失败分类的 markdown/HTML 报告。

- CI gate: fail when a metric drops below baseline.

  CI 关卡：当某个指标跌破基线时失败。

**Lab deliverable:** an eval suite of ≥ 25 cases for weeks 2–6 agents; a baseline report; three real regressions found by changing a prompt; judge agreement ≥ 80% with your labels. `pytest tests/week07 -m week` green.

**实验交付物：** 一套针对第 2–6 周 Agent 的评测套件，包含 ≥ 25 个用例；一份基线报告；通过修改提示词发现的三个真实回归；评审与你的标注一致率 ≥ 80%。`pytest tests/week07 -m week` 通过。

**Concepts:** outcome vs trajectory evals, pass^k, judge bias/calibration, eval leakage, deterministic-first scoring, what benchmarks (SWE-bench/TAU-bench/GAIA/Terminal-Bench) actually measure, trace schema design, OTel GenAI semconv status.

**概念：** 结果评测与轨迹评测的对比、pass^k、评审偏差/校准、评测泄漏、确定性优先的打分、各类基准（SWE-bench/TAU-bench/GAIA/Terminal-Bench）实际度量的是什么、trace schema 设计、OTel GenAI 语义约定（semconv）的现状。

**Reading (2 h):** research 03 §1–2; Hamel Husain on evals (research 04).

**阅读（2 小时）：** 研究资料 03 §1–2；Hamel Husain 关于评测的文章（见研究资料 04）。

**SendOS bridge:** `Outcome_Trace` append-only contract, 5-dimension `Evaluator`, `Distillation`/`Trainer` learning loop, publish gate. Note the gap research-05 flags: trace→candidate→publish is the most obviously unwired mechanism — your miniature is a design sketch for it.

**SendOS 桥接：** `Outcome_Trace` 只追加契约、5 维 `Evaluator`、`Distillation`/`Trainer` 学习闭环、发布关卡。留意研究资料 05 指出的差距：trace→候选→发布 是最明显尚未接线的机制——你的微缩实现就是它的一份设计草图。

**Stretch:** implement an OTel exporter for your trace events and view one run in a local collector.

**拓展：** 为你的 trace 事件实现一个 OTel 导出器，并在本地 collector 中查看一次运行。

---

### Week 8 — Security, governance, cost, reliability (8–10 h)

**第 8 周 — 安全、治理、成本、可靠性（8–10 小时）**

**Objective:** assume the model will be manipulated, and design so it does not matter.

**目标：** 假定模型一定会被操纵，并通过设计让这件事无关紧要。

**Build** (`agentlab/guard/`):

**构建**（`agentlab/guard/`）：

- `injection.py`: direct/indirect injection handling — untrusted-content delimiting, instruction hierarchy, output vetting; the "lethal trifecta" test.

  `injection.py`：直接/间接注入处理——为不可信内容加分隔符、指令层级、输出审查；「致命三要素」测试。

- `sandbox.py`: tool execution confined by path allowlist, size/time limits, and a subprocess or container boundary; write tools declare `is_write` and require approval.

  `sandbox.py`：工具执行受路径允许列表、大小/时间限制以及子进程或容器边界的约束；写入类工具声明 `is_write` 并需要审批。

- `authority.py`: deny-by-default intersection over independent sources; model output can never widen permission; per-tenant scoping.

  `authority.py`：对各独立来源取交集、默认拒绝；模型输出永远无法扩大权限；按租户划定范围。

- `audit.py`: append-only action log with before/after evidence and correlation ids.

  `audit.py`：只追加的动作日志，包含前后证据和关联 id。

- `ratelimit.py` + budget routing: per-tenant quotas, cost/latency-aware model routing with fail-safe budget checks, fallback on transient failures only.

  `ratelimit.py` + 预算路由：按租户的配额，感知成本/延迟的模型路由并配有故障安全的预算检查，仅在瞬时故障时回退。

- Red-team suite: ≥ 10 attacks (prompt injection via tool output, tool poisoning, path traversal, token passthrough, approval replay, budget exhaustion, data exfiltration).

  红队测试套件：≥ 10 种攻击（通过工具输出的提示词注入、工具投毒、路径穿越、token 透传、审批重放、预算耗尽、数据外泄）。

**Lab deliverable:** attack suite with before/after results; every write action gated and audited; a `SECURITY.md` threat model. `pytest tests/week08 -m week` green.

**实验交付物：** 带前后对比结果的攻击套件；每个写操作都经过把关和审计；一份 `SECURITY.md` 威胁模型。`pytest tests/week08 -m week` 通过。

**Concepts:** indirect injection, lethal trifecta, confused deputy, least privilege, sandboxing, approval binding, audit vs debug traces, prompt caching economics, durable execution, multi-tenant isolation, EU AI Act timeline (GPAI live since Aug 2026; high-risk Dec 2027).

**概念：** 间接注入、致命三要素、混淆代理、最小权限、沙箱、审批绑定、审计与调试 trace 的对比、提示词缓存的经济性、持久化执行、多租户隔离、欧盟《人工智能法案》时间线（GPAI 条款自 2026 年 8 月起生效；高风险条款 2027 年 12 月生效）。

**Reading (2 h):** research 03 §3–7 + checklist; OWASP GenAI Top 10 2026.

**阅读（2 小时）：** 研究资料 03 §3–7 + 检查清单；OWASP GenAI Top 10 2026。

**SendOS bridge:** the "governance sandwich", `EffectiveAuthority` nine-source intersection, licensing/quota at ingress, execution origin. SendOS is already ahead here — your job is to understand *why* each control exists, not to reproduce the code.

**SendOS 桥接：** 「治理三明治」、`EffectiveAuthority` 的九来源交集、入口处的许可/配额、执行来源。SendOS 在这方面已经领先——你的任务是理解每项控制*为什么*存在，而不是复刻代码。

**Stretch:** write a one-page threat model review of the SendOS approval path and send it to a senior engineer for critique.

**拓展：** 针对 SendOS 的审批路径写一页威胁模型评审，并发给一位资深工程师请其批评指正。

---

### Week 9 — Capstone: Mini-SendOS (12–16 h)

**第 9 周 — 结业项目：Mini-SendOS（12–16 小时）**

**Objective:** compose everything into one honest system, and demonstrate it.

**目标：** 把所有内容组合成一个诚实可信的系统，并进行演示。

**Build** (`projects/capstone/` + `agentlab/capstone/`, `agentlab/web/`):

**构建**（`projects/capstone/` + `agentlab/capstone/`、`agentlab/web/`）：

1. **Provider layer** — week 1 adapter + a mock provider for demos + budget routing (week 8).

   **提供商层**——第 1 周的适配器 + 一个用于演示的 mock 提供商 + 预算路由（第 8 周）。

2. **Capability catalogue** — tools with risk level, read/write, approval requirement; merged from two sources with published-wins.

   **能力目录**——带有风险等级、读/写属性、审批要求的工具；从两个来源合并，以已发布版本为准。

3. **Decision runtime** — typed decision family (week 3) + topology-driven shape selection (week 6) + specialists.

   **决策运行时**——类型化决策族（第 3 周）+ 拓扑驱动的形态选择（第 6 周）+ 专员。

4. **Governance** — fail-closed authority intersection, approval binding + at-most-once, audit log.

   **治理**——失败关闭的权限交集、审批绑定 + 至多一次执行、审计日志。

5. **Learning loop** — append-only traces (week 7) + eval harness + an evidence gate + a human-approved asset promotion (submit-only).

   **学习闭环**——只追加的 trace（第 7 周）+ 评测 harness + 一道证据关卡 + 一次经人工批准的资产晋升（仅提交）。

6. **Surface** — FastAPI + a minimal UI: submit a goal → see the typed decision, the plan, the approval request → approve → see the execution and the audit trail.

   **交互界面**——FastAPI + 一个极简 UI：提交一个目标 → 查看类型化决策、计划、审批请求 → 批准 → 查看执行过程和审计轨迹。

7. **Report** — architecture decisions, eval results, cost/latency, threats considered, what you would do next.

   **报告**——架构决策、评测结果、成本/延迟、考虑过的威胁，以及你接下来会做什么。

**Deliverable:** `scripts/demo_capstone.py` runs the whole flow offline with a mock provider; the web UI runs against a real provider. A 5-minute recorded demo. `projects/portfolio/WRITEUP.md` filled in.

**交付物：** `scripts/demo_capstone.py` 使用 mock 提供商离线运行整个流程；Web UI 对接真实提供商运行。一段 5 分钟的录屏演示。填写完成的 `projects/portfolio/WRITEUP.md`。

**Gate:** demo works end-to-end; eval suite green; a senior engineer (or me) can follow the trace of one request from ingress to audit row without asking questions.

**关卡：** 演示端到端可用；评测套件通过；一位资深工程师（或我）无需提问就能跟随一个请求从入口到审计记录行的 trace。

**SendOS bridge:** produce a 1-page design proposal for one real improvement (recommended: durable suspend/resume for approvals, or trace→candidate evidence gating). Ground it in your capstone.

**SendOS 桥接：** 为一项真实的改进写一页设计提案（推荐：审批的持久化挂起/恢复，或 trace→候选 的证据关卡）。以你的结业项目作为依据。

---

### Week 10 — Consolidation and leverage (4–6 h)

**第 10 周 — 巩固与发挥（4–6 小时）**

- **Re-derive from memory:** write the agent loop, MCP discovery flow, eval design and approval state machine from a blank file. Compare to your code.

  **凭记忆重新推导：** 从空白文件写出 Agent 循环、MCP 发现流程、评测设计和审批状态机。与你的代码进行比较。

- **Portfolio:** publish the capstone write-up and 2 deep-dive posts (e.g. "approval binding is a security mechanism", "why pass^k beats pass@1").

  **作品集：** 发布结业项目的总结文章和 2 篇深度剖析文章（例如「审批绑定是一种安全机制」、「为什么 pass^k 胜过 pass@1」）。

- **Interview prep:** 30 questions in [`docs/plan/INTERVIEW.md`](INTERVIEW.md) (built from research 01–03).

  **面试准备：** [`docs/plan/INTERVIEW.md`](INTERVIEW.md) 中的 30 道题（基于研究资料 01–03 编写）。

- **Next-step decision:** agentic RL / fine-tuning, framework specialisation (LangGraph or Microsoft Agent Framework), or productise the capstone.

  **下一步的决策：** Agent 强化学习 / 微调、框架专精（LangGraph 或 Microsoft Agent Framework），或者把结业项目产品化。

---

## 5. Time allocation per week (8–12 h)

**5. 每周时间分配（8–12 小时）**

| Block<br>时间块 | Time<br>时间 | What<br>内容 |
|---|---|---|
| Brief + concept note<br>任务说明 + 概念笔记 | 45 min<br>45 分钟 | Read lab brief and the week's concept note; write 3 goals<br>阅读实验任务说明和本周的概念笔记；写下 3 个目标 |
| Build session 1<br>构建会话 1 | 2–3 h<br>2–3 小时 | Core implementation against failing tests<br>针对失败的测试完成核心实现 |
| Build session 2<br>构建会话 2 | 2–3 h<br>2–3 小时 | Finish implementation; make the lab artifact work end-to-end<br>完成实现；让实验产出物端到端可用 |
| SendOS bridge<br>SendOS 桥接 | 45 min<br>45 分钟 | Read mapped C# code/docs; write 5 bullet comparison<br>阅读对应的 C# 代码/文档；写 5 条要点的对比 |
| Theory + paper<br>理论 + 论文 | 90 min<br>90 分钟 | One concept note + one must-read paper/essay<br>一篇概念笔记 + 一篇必读论文/文章 |
| Review + reflection<br>复盘 + 反思 | 60 min<br>60 分钟 | Green tests, weekly review, 5 flashcards, progress update<br>测试通过、每周复盘、5 张闪卡、更新进度 |
| Stretch (optional)<br>拓展（可选） | 1–2 h<br>1–2 小时 | Only if the gate is already passed<br>仅在关卡已经通过时进行 |

The efficiency method (timeboxing, retrieval practice, interleaving, spaced repetition) is in [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md).

效率方法（时间盒、提取练习、交错练习、间隔重复）见 [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)。

---

## 6. Assessment and gates

**6. 考核与关卡**

Each week has three gate conditions (details in [`CHECKPOINTS.md`](CHECKPOINTS.md)):

每周有三项关卡条件（详见 [`CHECKPOINTS.md`](CHECKPOINTS.md)）：

1. **Green:** `pytest tests/weekNN -m week` passes.

   **Green（通过）：** `pytest tests/weekNN -m week` 通过。

2. **Explain:** 150-word teach-back with no notes, plus answers to the week's quiz.

   **Explain（讲解）：** 不看笔记完成 150 词的复述讲解，并回答本周的测验。

3. **Transfer:** complete the SendOS bridge note (what matches, what differs, what you would change).

   **Transfer（迁移）：** 完成 SendOS 桥接笔记（哪些一致、哪些不同、你会改什么）。

You may not start week N+1 until all three pass. **One grace exception:** when work or coursework interferes, you may carry **one** non-green gate for **one** week, logged as debt in [`PROGRESS.md`](PROGRESS.md) with a repayment date. Two consecutive weeks of debt means you stop and clear it — a half-understood week compounds faster than any other failure mode in this plan. If a week overruns by > 50%, cut the stretch goal, not the gate.

三项全部通过之前，你不能开始第 N+1 周。**唯一的宽限例外：** 当工作或课程造成干扰时，你可以带着**一道**未通过的关卡度过**一周**，并在 [`PROGRESS.md`](PROGRESS.md) 中记为债务，注明偿还日期。连续两周欠债就意味着你必须停下来先清偿——一个半懂不懂的周，其恶果累积的速度比本计划中任何其他失败模式都快。如果某一周超时 > 50%，砍掉拓展目标，而不是关卡。

---

## 7. Risks and countermeasures

**7. 风险与应对措施**

| Risk<br>风险 | Countermeasure<br>应对措施 |
|---|---|
| Internship crunch eats the week<br>实习赶工吞掉了这一周 | Minimum viable week = 2 sessions + tests green; skip theory/stretch, never skip the gate<br>最低可行周 = 2 次会话 + 测试通过；跳过理论/拓展，但永远不跳过关卡 |
| API cost anxiety<br>担心 API 成本 | All tests are mock-based; live calls are capped at $0.50/run; DeepSeek for high-volume labs<br>所有测试都基于 mock；真实调用每次运行上限为 0.50 美元；大量调用的实验使用 DeepSeek |
| Tutorial rabbit hole<br>教程兔子洞 | The plan's reading list is capped; anything not linked from the week is "later"<br>计划的阅读清单有上限；凡是本周没有链接到的内容都归为「以后再看」 |
| Framework FOMO<br>框架错失恐惧（FOMO） | Frameworks arrive in week 6+ as comparison, not as prerequisites<br>框架从第 6 周起作为对比出现，而不是前置条件 |
| "It works but I can't explain it"<br>「能跑，但我讲不清楚」 | The teach-back gate; no exceptions<br>复述讲解关卡；没有例外 |
| SendOS docs vs code drift<br>SendOS 文档与代码不一致 | Research-05 §0 records five verified drifts — always trust code over docs<br>研究资料 05 §0 记录了五处经过核实的不一致——永远以代码为准，而不是文档 |
| Perfectionism on the capstone<br>对结业项目的完美主义 | Demo script + write-up beats polish; ship at 80%<br>演示脚本 + 总结文章胜过打磨；做到 80% 就交付 |

---

## 8. What "done" looks like at week 9

**8. 第 9 周时「完成」是什么样子**

You can, without notes:

你能够在不看笔记的情况下：

- Draw the request path of an agent run from ingress to audit row, naming every failure mode and its control.

  画出一次 Agent 运行从入口到审计记录行的请求路径，并点出每一种失败模式及其控制措施。

- Explain why approval must be bound to an action hash and an authority snapshot, and what breaks without it.

  解释为什么审批必须绑定到动作哈希和权限快照，以及没有它会坏掉什么。

- Design an eval suite that would catch a prompt regression before production, including pass^k reasoning.

  设计一套能在上线前捕捉到提示词回归的评测套件，包括基于 pass^k 的推理。

- Read a new agent framework's source and map its abstractions onto the primitives you built.

  阅读一个新的 Agent 框架的源码，并把它的抽象映射到你构建过的原语上。

- Read SendOS's `DecisionRuntime`/`ApprovalCheckpoint`/`Model.Adapter` and propose a concrete improvement.

  读懂 SendOS 的 `DecisionRuntime`/`ApprovalCheckpoint`/`Model.Adapter`，并提出一项具体的改进。

And you own: ~4–6k lines of tested Python, 9 lab reports, an eval report, a capstone demo, and a portfolio write-up.

而且你将拥有：约 4–6 千行经过测试的 Python 代码、9 份实验报告、一份评测报告、一个结业项目演示，以及一篇作品集总结文章。

---

## 9. After the course

**9. 课程结束之后**

Three credible directions, in increasing difficulty:

三个可行的方向，难度递增：

1. **Framework fluency** — reimplement week 6's squad in LangGraph and Microsoft Agent Framework; compare ergonomics (1 week).

   **框架熟练度**——用 LangGraph 和 Microsoft Agent Framework 重新实现第 6 周的小队；比较它们的易用性（1 周）。

2. **Learning loop** — extend the capstone's trace→eval→candidate→publish into a small "self-improving" pipeline with evidence gates (2–3 weeks).

   **学习闭环**——把结业项目中的 trace→评测→候选→发布 扩展成一个带证据关卡的小型「自我改进」流水线（2–3 周）。

3. **Agentic RL / post-training** — only if the eval and data plumbing above is solid; otherwise you will optimise noise.

   **Agent 强化学习 / 后训练**——只有在上述评测和数据管道足够扎实时才做；否则你只是在优化噪声。

Recommended reading order after the course: [`docs/research/04-learning-resources.md`](../research/04-learning-resources.md) §F, then the three must-read papers in §D that you have not yet read.

课程结束后推荐的阅读顺序：先读 [`docs/research/04-learning-resources.md`](../research/04-learning-resources.md) §F，然后读 §D 中你还没读过的三篇必读论文。

---

## Appendix — research mapping

**附录 — 研究资料对应关系**

| Plan section<br>计划章节 | Primary sources<br>主要来源 |
|---|---|
| Week 1–2<br>第 1–2 周 | research 01 §1–2, research 02 §3<br>研究资料 01 §1–2，研究资料 02 §3 |
| Week 3<br>第 3 周 | research 01 §3, research 02 §3<br>研究资料 01 §3，研究资料 02 §3 |
| Week 4<br>第 4 周 | research 01 §3–4<br>研究资料 01 §3–4 |
| Week 5<br>第 5 周 | research 02 §1, research 01 §10<br>研究资料 02 §1，研究资料 01 §10 |
| Week 6<br>第 6 周 | research 01 §2, §6; research 05 §4.1, §4.5<br>研究资料 01 §2、§6；研究资料 05 §4.1、§4.5 |
| Week 7<br>第 7 周 | research 03 §1–2; research 05 §4.3<br>研究资料 03 §1–2；研究资料 05 §4.3 |
| Week 8<br>第 8 周 | research 03 §3–7; research 05 §4.2<br>研究资料 03 §3–7；研究资料 05 §4.2 |
| Week 9<br>第 9 周 | research 05 §4<br>研究资料 05 §4 |
| Learning method<br>学习方法 | research 04 §A, §H<br>研究资料 04 §A、§H |
