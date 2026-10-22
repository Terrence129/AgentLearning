# BRIDGE — the week-by-week SendOS reading bridge

**BRIDGE —— 逐周的 SendOS 阅读桥接**

**Living document.** One page per learning-plan week, each sized for a **30-minute** bridge session.
Read real SendOS code, answer three questions, write five bullets. No setup, no build, no network.

**活文档。** 学习计划的每一周对应一页，每页的分量都按一次 **30 分钟**的桥接课时来设计。阅读真实的 SendOS 代码，回答三个问题，写下五条要点。无需环境搭建，无需构建，无需联网。

> **Code wins over docs.** Every path here was verified to exist on **2026-10-18** against the
> source checkout. Where a repo doc contradicts the code, this page follows the code and says so.
> Paths are **relative to the SendOS repo root** (`SendOs/`), not to this learning repo.
> Evidence base and status labels: [`CONCEPT-MAP.md`](./CONCEPT-MAP.md) (research §0–§7).
> Reading sequence: [`READING-ORDER.md`](./READING-ORDER.md). C# labs: [`../../dotnet/`](../../dotnet/).
>
> **代码优先于文档。** 这里的每条路径都于 **2026-10-18** 对照源码检出核实过确实存在。当仓库文档与代码矛盾时，本页以代码为准并明确指出。路径均**相对于 SendOS 仓库根目录**（`SendOs/`），而不是这个学习仓库。证据库与状态标签：[`CONCEPT-MAP.md`](./CONCEPT-MAP.md)（研究报告 §0–§7）。阅读顺序：[`READING-ORDER.md`](./READING-ORDER.md)。C# 实验（lab）：[`../../dotnet/`](../../dotnet/)。

---

## How to use this bridge (the 30-minute protocol)

**如何使用本桥接文档（30 分钟流程）**

| Minutes | Do | Why |
|---|---|---|
| 0–15 | Open the listed files. Read **headers, type declarations and validation branches** — not every method body<br>打开列出的文件。阅读**文件头、类型声明和校验分支** —— 不必读每个方法体 | The API shape is the design; bodies are implementation detail you can return to<br>API 的形状就是设计；方法体是实现细节，可以以后再回来看 |
| 15–25 | Answer the week's 3 questions **in writing, without looking anything up**<br>**以书面形式、不查阅任何资料**回答本周的 3 个问题 | Retrieval practice; you discover what you only *recognised*<br>提取练习；你会发现哪些东西你其实只是*看着眼熟* |
| 25–28 | Check your answers against [Appendix A](#appendix-a--answers), correct in a different colour<br>对照[附录 A](#appendix-a--answers) 检查答案，用另一种颜色修正 | Calibration<br>校准 |
| 28–30 | Write 5 bullets in your weekly note: **maps cleanly / differs / would change**<br>在周笔记中写 5 条要点：**干净对应 / 存在差异 / 我会怎么改** | Becomes the "Transfer" gate for the week<br>成为本周的"迁移（Transfer）"关卡 |

**Rule:** if the 30 minutes is all you have that week, this *is* the SendOS work. Do not skip it for
more tutorials — the plan weights this as goal A ("contribute faster"), and it compounds.

**规则：** 如果这周你只有这 30 分钟，那么这*就是*你的 SendOS 工作。不要为了多看几篇教程而跳过它 —— 计划把它作为目标 A（"更快地做出贡献"）来加权，而且它会产生复利。

**Rule:** never paste production code into the learning repo. Cite `path:line`, quote at most a few
lines, and keep the learning repo's code your own.

**规则：** 永远不要把生产代码粘贴到学习仓库里。引用 `path:line`，最多摘录几行，让学习仓库里的代码始终是你自己写的。

---

## The framing: SendOS is ahead on governance, behind on orchestration ergonomics

**核心框架：SendOS 在治理上领先，在编排易用性上落后**

This one sentence explains almost every difference you will find, and it is the most transferable
judgement in the bridge.

这一句话几乎能解释你将发现的所有差异，也是本桥接文档中最具可迁移性的判断。

| SendOS is **ahead** of mainstream tutorials on…<br>SendOS 在以下方面**领先**于主流教程…… | …because production demanded it<br>……因为生产环境要求如此 | Your lab already proves a miniature<br>你的实验已经验证了一个微缩版 |
|---|---|---|
| Typed decisions instead of free text<br>用类型化决策取代自由文本 | A paragraph cannot be approved, audited or budgeted<br>一段文字无法被审批、审计或纳入预算 | `dotnet/StructuredDecisionBridge`; week-3 `agentlab/schemas/`<br>`dotnet/StructuredDecisionBridge`；第 3 周的 `agentlab/schemas/` |
| Approval binding (action hash, authority snapshot, expiry, at-most-once)<br>审批绑定（动作哈希、权限快照、过期时间、至多一次） | Double-execution and post-approval edits are real incidents<br>重复执行和审批后修改都是真实发生过的事故 | week 6 `agentlab/orchestrator/approval.py`<br>第 6 周的 `agentlab/orchestrator/approval.py` |
| Authority as an intersection of independent boundaries<br>权限是多个独立边界的交集 | "The AI said I could" is not an authorisation<br>"AI 说我可以"不是授权 | week 8 `agentlab/guard/authority.py`<br>第 8 周的 `agentlab/guard/authority.py` |
| Append-only outcome trace<br>只追加的结果 trace | Learning and audit both need history that cannot be rewritten<br>学习和审计都需要无法被改写的历史 | week 7 `agentlab/trace.py`<br>第 7 周的 `agentlab/trace.py` |
| Human-gated publish of learned assets<br>经人工把关的学习所得资产发布 | A model must never change its own policy<br>模型绝不能修改自己的策略 | week 7/9 evidence gate + publish<br>第 7/9 周的证据关卡 + 发布 |
| Version pinning of governed assets<br>受治理资产的版本锁定 | A mid-flight publish must not mutate a running decision<br>运行过程中的发布不能改变正在进行的决策 | week 6 asset resolution<br>第 6 周的资产解析 |

| SendOS is **behind** on…<br>SendOS 在以下方面**落后**…… | Consequence in the repo<br>在仓库中的后果 | What to learn instead<br>应该改学什么 |
|---|---|---|
| Graph/state-machine orchestration runtime<br>图/状态机式的编排运行时 | Shape selection and dispatch live in a large procedural `DecisionRuntime` (5,379 lines)<br>形态选择和分发都放在一个庞大的过程式 `DecisionRuntime`（5,379 行）里 | LangGraph / Temporal / Microsoft Agent Framework, in week 9 comparison<br>LangGraph / Temporal / Microsoft Agent Framework，在第 9 周做比较 |
| Wired durable execution<br>已接通的持久化执行 | `CaseRuntime` + `DecisionTask` are built and unit-tested but have no production caller<br>`CaseRuntime` + `DecisionTask` 已构建并有单元测试，但没有生产环境的调用方 | Temporal, DBOS, checkpoint-and-resume patterns<br>Temporal、DBOS、检查点与恢复模式 |
| Observability stack<br>可观测性技术栈 | `TurnStage` enum is excellent; metrics/traces are stubs<br>`TurnStage` 枚举非常出色；指标/trace 只是桩代码 | OpenTelemetry GenAI conventions (week 7 stretch)<br>OpenTelemetry GenAI 约定（第 7 周拓展） |
| Learning loop connectivity<br>学习闭环的连通性 | Distillation/Trainer/Evaluator are real code with a dry loop<br>Distillation/Trainer/Evaluator 都是真实代码，但闭环是干涸的 | Your capstone's trace → eval → candidate → publish is a design sketch for it<br>你的结业项目（capstone）中的 trace → 评测（eval）→ 候选 → 发布就是它的设计草图 |
| Provider-native constrained decoding<br>模型提供商（provider）原生的约束解码 | Hand-rolled JSON Schema subset instead<br>改用手写的 JSON Schema 子集 | Structured outputs / grammars; measure the trade in week 3<br>结构化输出 / 语法约束；在第 3 周量化其中的取舍 |

**How to use the framing:** when a week's mechanisms feel over-engineered, ask *which incident paid
for this control*. When they feel incomplete, ask *which framework has already solved this*. Both
questions are interview answers.

**如何运用这个框架：** 当某周的机制显得过度设计时，问一问*是哪次事故换来了这个控制*。当它们显得不完整时，问一问*哪个框架已经解决了这个问题*。这两个问题都是面试时的好答案。

---

## The six mechanisms worth rebuilding (and where each lives)

**值得重建的六个机制（以及它们各自所在的位置）**

From [`CONCEPT-MAP.md` §4](./CONCEPT-MAP.md#4-where-a-from-scratch-build-teaches-the-most--six-mechanisms).
These are the highest-value transfers; every week's bridge touches at least one.

出自 [`CONCEPT-MAP.md` §4](./CONCEPT-MAP.md#4-where-a-from-scratch-build-teaches-the-most--six-mechanisms)。这些是价值最高的迁移点；每周的桥接都至少涉及其中一个。

| # | Mechanism<br>机制 | Weeks<br>周次 | Built in this repo<br>本仓库中的实现 | SendOS reference<br>SendOS 参考 |
|---|---|---|---|---|
| 1 | Typed decision family + bound approval gate<br>类型化决策族 + 绑定式审批关卡 | 3, 6 | `dotnet/StructuredDecisionBridge`; `agentlab/schemas/`, `agentlab/orchestrator/approval.py` | `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs`; `.../Application/Approval/ApprovalCheckpoint.cs` |
| 2 | Capability catalogue + fail-closed authority<br>能力目录 + 失败即关闭的权限 | 2, 8 | `agentlab/tools/registry.py`, `agentlab/guard/authority.py` | `.../Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs`; `.../Domain/Authority/EffectiveAuthority.cs`; `.../Application/Authority/AuthoritySources.cs` |
| 3 | Trace → eval → evidence-gated candidate → human publish<br>trace → 评测 → 经证据把关的候选 → 人工发布 | 7, 9 | `agentlab/trace.py`, `agentlab/evals/` | `apps/Send.Usage.Collector/src/.../Domain/*`; `apps/Send.LowerLayer.Worker/src/.../Distillation/*`, `.../Evaluation/*`; `.../PublishingPipeline/PublishingService.cs` |
| 4 | Schema-gated structured output + budget routing<br>schema 把关的结构化输出 + 预算路由 | 3, 8 | `dotnet/StructuredDecisionBridge`; `agentlab/providers/`, week-8 routing<br>`dotnet/StructuredDecisionBridge`；`agentlab/providers/`、第 8 周的路由 | `apps/Send.Model.Adapter/src/.../Structured/*`; `.../Handlers/CompletionHandler.cs` |
| 5 | Topology-driven shape selection<br>拓扑驱动的形态选择 | 6 | `agentlab/orchestrator/plan.py` | `.../Application/Planning/TopologyClassifier.cs`; `ExecutionPlanner.cs`; `docs/adrs/0001-*.md` |
| 6 | Append-only trace as the runtime↔learning contract<br>作为运行时↔学习之间契约的只追加 trace | 7, 9 | `agentlab/trace.py` | `apps/Send.Usage.Collector/src/.../Domain/OutcomeTrace*`; `.../Application/Outcome/IOutcomeTraceEmitter.cs` |

---

## Week 1 — The model, demystified → `Send.Model.Adapter`

**第 1 周 —— 揭开模型的面纱 → `Send.Model.Adapter`**

**You build:** the provider seam (`agentlab/providers/openai_compat.py`), payload/parse/stream/retry.
**C# lab:** [`dotnet/ProviderBridge`](../../dotnet/ProviderBridge/README.md) — same seam in .NET,
with an 11-check offline self-test.

**你要构建：** provider 接缝（seam）（`agentlab/providers/openai_compat.py`），包括请求载荷/解析/流式输出/重试。
**C# 实验：** [`dotnet/ProviderBridge`](../../dotnet/ProviderBridge/README.md) —— 用 .NET 实现同样的接缝，附带一个包含 11 项检查的离线自测。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Interfaces/IProviderAdapter.cs` | The seam: what a provider adapter must do, and what it must not<br>接缝：提供商适配器必须做什么，以及绝不能做什么 |
| `.../Infrastructure/ExternalServices/OpenAiProviderAdapter.cs` | Payload build, response parse, JSON-output mode, usage capture<br>构建请求载荷、解析响应、JSON 输出模式、用量采集 |
| `.../Infrastructure/ExternalServices/StructuredOutputDirective.cs` | How the SDK nudges JSON output without native schemas<br>在没有原生 schema 支持的情况下，SDK 如何引导模型输出 JSON |
| `.../Application/Handlers/CompletionHandler.cs` | Retry/fallback/time-budget loop; `IsTransient` (only 502/504!), the `Declared` selection-order bug recorded at lines 78–85<br>重试/回退/时间预算循环；`IsTransient`（只认 502/504！）；第 78–85 行记录的 `Declared` 选择顺序 bug |
| `.../Contracts/Routing/ModelBudget.cs` | The budget fields your lab does not enforce yet (week 8)<br>你的实验尚未强制执行的预算字段（第 8 周） |

### Questions

**问题**

1. SendOS puts retry in `CompletionHandler`, not in the adapter. What does that placement make possible that an adapter-level retry cannot?

   SendOS 把重试放在 `CompletionHandler` 里，而不是放在适配器里。这种放置方式能做到哪些适配器层面的重试做不到的事？

2. `CompletionHandler.IsTransient` returns true only for 502/504. Is that too narrow? What would you include, and what breaks if you are wrong in each direction?

   `CompletionHandler.IsTransient` 只对 502/504 返回 true。这是否太窄了？你会把哪些状态码也包括进来？如果你在两个方向上判断失误，分别会坏掉什么？

3. Which of `ChatCompletionsClient`'s responsibilities map to `IProviderAdapter`, and which map to `CompletionHandler`?

   `ChatCompletionsClient` 的哪些职责对应 `IProviderAdapter`，哪些对应 `CompletionHandler`？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** provider seam, payload/response translation, usage capture, provider-independent model id, wire-level retry.

  **干净对应：** provider 接缝、请求载荷/响应的转换、用量采集、与提供商无关的模型 id、线路层面的重试。

- **Differs:** SendOS routes across *candidate models* with cost/latency/reliability policy, retries at the handler so a fallback can pick a different model, and requests provider JSON-output modes. Its `ModelCostProfile`/`ModelBudget` combination is week-8 material.

  **存在差异：** SendOS 依据成本/延迟/可靠性策略在*多个候选模型*之间路由，在处理器层面重试，以便回退时能选择另一个模型，并且会请求提供商的 JSON 输出模式。它的 `ModelCostProfile`/`ModelBudget` 组合属于第 8 周的内容。

**Micro-action:** list every field `ModelBudget` carries and mark which your week-1 client ignores. That list is your week-8 to-do.

**微行动：** 列出 `ModelBudget` 携带的每个字段，并标出你第 1 周的客户端忽略了哪些。这份清单就是你第 8 周的待办事项。

---

## Week 2 — Tools and the agent loop → `CapabilityDefinition` + registry

**第 2 周 —— 工具与 Agent 循环 → `CapabilityDefinition` + 注册表**

**You build:** the loop and tool registry (`agentlab/loop/`, `agentlab/tools/`).

**你要构建：** 循环和工具注册表（`agentlab/loop/`、`agentlab/tools/`）。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `apps/Send.Agent.Runtime/src/.../Domain/Capabilities/CapabilityDefinition.cs` | The fields a governed tool carries: risk, read/write, approval, side effects, idempotency, compensation, evidence kinds, action kind, result resource type, tenant availability, version, governed-asset reference<br>一个受治理的工具所携带的字段：风险、读/写、审批、副作用、幂等性、补偿、证据类型、动作类型、结果资源类型、租户可用性、版本、受治理资产引用 |
| `.../Application/CapabilityRegistry/ICapabilityRegistry.cs` | `Match` vs `MatchByRequirements` vs `MatchByUnderstanding` — structural selection, not keyword overlap<br>`Match`、`MatchByRequirements` 与 `MatchByUnderstanding` 的区别 —— 基于结构的选择，而不是关键词重合 |
| `.../Application/CapabilityRegistry/CapabilityRegistry.cs` | Tenant scoping and the hard boundaries applied before anything is offered<br>租户范围限定，以及在提供任何能力之前就施加的硬边界 |
| `.../Application/Execution/DirectCapabilityHandler.cs` | The one fully-live execution shape: authorize → invoke → reason → compose<br>唯一一个完全上线的执行形态：授权 → 调用 → 推理 → 组装 |
| `.../Application/Execution/SemanticInputBinding.cs` | How a turn's values get bound onto declared inputs (and what "unbound" means)<br>一轮对话中的值如何被绑定到声明的输入上（以及"未绑定"意味着什么） |

### Questions

**问题**

1. Which `CapabilityDefinition` fields have no analogue in a plain tool schema, and what failure does each field prevent?

   `CapabilityDefinition` 中哪些字段在普通的工具 schema 里没有对应物？每个字段分别防止了什么失败？

2. Why does the registry prefer structured matching (`ProvidedEvidence`, `ActionKind`, `ResultResourceType`) over objective-keyword overlap?

   为什么注册表更倾向于结构化匹配（`ProvidedEvidence`、`ActionKind`、`ResultResourceType`），而不是目标关键词的重合？

3. SendOS has no generic "ReAct loop". Where is its loop, and why might an enterprise platform avoid one generic loop?

   SendOS 没有通用的"ReAct 循环"。它的循环在哪里？为什么企业级平台可能会刻意避免使用一个通用循环？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** tool registry with schema + handler together, errors-as-observations (your registry does this; SendOS returns structured read outcomes), tenant scoping.

  **干净对应：** schema 与处理器放在一起的工具注册表、把错误当作观察结果（你的注册表就是这么做的；SendOS 返回结构化的读取结果）、租户范围限定。

- **Differs:** SendOS capabilities are **governed assets** with risk/approval/version — a tool cannot be "just registered". The loop is a bounded goal loop inside `DecisionRuntime`, specialised per shape, not a general-purpose reason-act loop.

  **存在差异：** SendOS 的能力是带有风险/审批/版本的**受治理资产** —— 一个工具不能"注册一下就完事"。它的循环是 `DecisionRuntime` 内部的一个有界目标循环，按形态分别特化，而不是一个通用的推理-行动循环。

**Micro-action:** open your `ToolRegistry` and add one metadata field SendOS has (`is_write` is the cheapest). Note what code had to change to enforce it.

**微行动：** 打开你的 `ToolRegistry`，加上一个 SendOS 拥有的元数据字段（`is_write` 成本最低）。记下为了强制执行它需要改动哪些代码。

---

## Week 3 — Structured output, prompts as assets → `IStructuredCompletionHandler`

**第 3 周 —— 结构化输出、提示词即资产 → `IStructuredCompletionHandler`**

**You build:** `agentlab/schemas/` — structured output, repair, versioned prompts, typed `Decision`.
**C# lab:** [`dotnet/StructuredDecisionBridge`](../../dotnet/StructuredDecisionBridge/README.md) —
three-stage gate (schema → binding → budget) with a 15-check offline self-test.

**你要构建：** `agentlab/schemas/` —— 结构化输出、修复、带版本的提示词、类型化的 `Decision`。
**C# 实验：** [`dotnet/StructuredDecisionBridge`](../../dotnet/StructuredDecisionBridge/README.md) —— 三阶段关卡（schema → 绑定 → 预算），附带一个包含 15 项检查的离线自测。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `apps/Send.Model.Adapter/src/.../Structured/IStructuredCompletionHandler.cs` | The contract: schema in; validated output or `SchemaValid=false`<br>契约：输入 schema；输出经过校验的结果，或者 `SchemaValid=false` |
| `.../Structured/StructuredCompletionHandler.cs` | Never surfaces invalid output; status handling; no retry here<br>从不暴露无效输出；状态处理；这里不做重试 |
| `.../Structured/JsonSchemaValidator.cs` | The supported subset: `type`, `required`, `properties`, `items` only<br>支持的子集：只有 `type`、`required`、`properties`、`items` |
| `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs` | Closed response family; envelope; the reserved-artifact exclusion<br>封闭的响应族；信封；对保留产物类型的排除 |
| `.../Application/Decision/PresentationBudget.cs` + `PresentationBudgetEnforcer.cs` | The numbers you implemented, enforced in production<br>你实现过的那些数字，在生产环境中被强制执行 |
| `.../Application/IntentElevation/IntentElevator.cs` lines 96–215<br>`.../Application/IntentElevation/IntentElevator.cs` 第 96–215 行 | The deterministic projection that keeps `ClarificationRequired` a pure function — models interpret, code decides policy<br>让 `ClarificationRequired` 保持为纯函数的确定性投影 —— 模型负责解释，代码负责决定策略 |

### Questions

**问题**

1. SendOS validates *after* generation instead of using provider-native constrained decoding. What does that cost, and when is it the right trade?

   SendOS 在生成*之后*才做校验，而不是使用提供商原生的约束解码。这样做的代价是什么？什么时候这是正确的取舍？

2. `StructuredCompletionHandler` returns `SchemaValid=false` and `StructuredOutput=null` rather than a partial object. How does that choice change the caller's error handling?

   `StructuredCompletionHandler` 返回 `SchemaValid=false` 和 `StructuredOutput=null`，而不是一个部分有效的对象。这个选择如何改变调用方的错误处理？

3. SendOS's composer **trims** to budget while your lab **rejects and repairs**. What can trimming silently change, and when is repair worth the extra calls?

   SendOS 的组装器按预算进行**裁剪**，而你的实验则是**拒绝并修复**。裁剪可能会悄悄改变什么？什么时候修复值得多付出那几次调用？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** schema-gated completion, validate-after, discriminated decision family, presentation budgets as numbers.

  **干净对应：** schema 把关的补全、事后校验、可辨识的决策族、以数字表示的展示预算。

- **Differs:** SendOS validates in `Model.Adapter` and composes in the runtime (two services, two seams); its family is much larger (evidence, execution results, readback verdicts); prompts are governed assets (`PromptGuidance`, `SpecialistDefinition`), not files.

  **存在差异：** SendOS 在 `Model.Adapter` 中校验，在运行时中组装（两个服务、两个接缝）；它的响应族要大得多（证据、执行结果、回读判定）；提示词是受治理的资产（`PromptGuidance`、`SpecialistDefinition`），而不是文件。

**Micro-action:** count how many of your week-3 tests would still pass if the schema allowed `additionalProperties`. Then add the test that catches it.

**微行动：** 数一数如果 schema 允许 `additionalProperties`，你第 3 周的测试中还有多少会通过。然后补上能捕获这个问题的测试。

---

## Week 4 — Context engineering and memory → `Send.Context.Gateway`

**第 4 周 —— 上下文工程与记忆 → `Send.Context.Gateway`**

**You build:** `agentlab/context/` — window, compaction, retrieval, memory.

**你要构建：** `agentlab/context/` —— 上下文窗口、压缩（compaction）、检索、记忆。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `libraries/Send.Context.Gateway/IContextGateway.cs` | The boundary's promises: tenant-scoped, source-agnostic, no reasoning, no SDK<br>这个边界的承诺：按租户限定范围、与数据源无关、不做推理、不依赖 SDK |
| `libraries/Send.Context.Gateway/ContextGateway.cs` | Tenant-mismatch error vs empty result; freshness policy<br>租户不匹配错误与空结果的区别；新鲜度策略 |
| `libraries/Send.Context.Gateway/Semantic/SemanticContextRetriever.cs` | Additive semantic path layered over structured retrieval<br>叠加在结构化检索之上的增补式语义路径 |
| `libraries/Send.Context.Gateway/Semantic/DeterministicEmbeddingGenerator.cs` | Why a hash embedding is plumbing, not intelligence<br>为什么哈希嵌入只是管道，而不是智能 |
| `apps/Send.Agent.Runtime/src/.../Domain/Execution/SpecialistContext.cs` | The least-context envelope: exactly what a specialist may see<br>最小上下文信封：精确规定专员 Agent（specialist）能看到什么 |
| `apps/Send.Agent.Runtime/src/.../Infrastructure/ContextGateway/HttpContextRecordReader.cs` | How the runtime reads governed context over HTTP<br>运行时如何通过 HTTP 读取受治理的上下文 |

### Questions

**问题**

1. Why is "empty result is not an error" a deliberate contract rather than a convenience?

   为什么"空结果不是错误"是一个刻意设计的契约，而不只是图方便？

2. What is excluded from `SpecialistContext`, and what does each exclusion protect against?

   `SpecialistContext` 中排除了哪些内容？每一项排除分别防范了什么？

3. Why is a deterministic hash embedding shipped by default, and what is the honest remaining upgrade?

   为什么默认附带的是确定性的哈希嵌入？坦白说，剩下要做的升级是什么？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** context is a budget, least-context envelopes, retrieval behind a boundary, empty-vs-error distinction.

  **干净对应：** 上下文是一种预算、最小上下文信封、位于边界之后的检索、空结果与错误的区分。

- **Differs:** SendOS's objective is **data minimisation for governance**, not maximal recall for quality; its retrieval is mostly structured records, with vectors additive; memory is split across Business_State (durable) and Decision Memory (OrgIntel), not one `memory.py`.

  **存在差异：** SendOS 的目标是**为治理而做数据最小化**，而不是为质量而追求最大召回；它的检索主要面向结构化记录，向量只是增补；记忆被拆分到 Business_State（持久化）和 Decision Memory（OrgIntel）中，而不是一个 `memory.py`。

**Micro-action:** measure tokens saved by passing a least-context envelope instead of the full transcript in your week-2 agent. Write the number down.

**微行动：** 在你第 2 周的 Agent 中，用最小上下文信封代替完整对话记录，测量节省了多少 token。把这个数字记下来。

---

## Week 5 — MCP and interoperability → connector manifests

**第 5 周 —— MCP 与互操作性 → 连接器清单**

**You build:** `agentlab/mcp/` — server, client, security checks.

**你要构建：** `agentlab/mcp/` —— 服务器、客户端、安全检查。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `libraries/Send.Connectors.Abstractions/IConnector.cs` | The source-agnostic port; vendor types never leak<br>与数据源无关的端口；厂商类型从不外泄 |
| `libraries/Send.Connectors.Abstractions/ExecutionOrigin.cs` | The enum every result carries: external-demo / simulated / controlled-live<br>每个结果都携带的枚举：外部演示 / 模拟 / 受控实时 |
| `libraries/Send.Shared.Contracts/Capabilities/ConnectorCapabilityManifest.cs` | The manifest a connector publishes<br>连接器发布的清单 |
| `apps/Send.Integration.Service/src/.../Application/Connectors/ICapabilityManifestProvider.cs` | The declaration seam: connectors declare, they do not route<br>声明接缝：连接器只负责声明，不负责路由 |
| `apps/Send.Agent.Runtime/src/.../Infrastructure/CapabilityRegistry/HttpConnectorCapabilityManifestSource.cs` | How the runtime pulls manifests at startup/refresh<br>运行时如何在启动/刷新时拉取清单 |
| `apps/Send.Agent.Runtime/src/.../Application/Execution/ExecutionOrigins.cs` | Where origin is stamped and enforced<br>来源在哪里被标记并强制执行 |
| `libraries/Send.Connectors.Abstractions/IDeclaresExecutionOrigin.cs` | The interface that makes "say what you touched" non-optional<br>让"说明你动了什么"成为强制要求的接口 |

### Questions

**问题**

1. In SendOS, does a connector decide which capabilities exist, or does governance? Trace the path from `.cs` declaration to runtime registry.

   在 SendOS 中，是连接器决定存在哪些能力，还是治理层决定？追踪从 `.cs` 中的声明到运行时注册表的路径。

2. MCP discovers tools at runtime from a server; SendOS assembles a catalogue from manifests and published assets. What does each approach make easy, and what does each make hard to govern?

   MCP 在运行时从服务器发现工具；SendOS 则从清单和已发布资产中汇编出一个目录。两种方式各自让什么变得容易，又各自让什么变得难以治理？

3. Why does `ExecutionOrigin` exist as a first-class result field, and what should happen when a connector fails to declare one?

   为什么 `ExecutionOrigin` 要作为一等的结果字段存在？当某个连接器没有声明它时，应该发生什么？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** capabilities are declared by their provider, not hard-coded in the agent; tool descriptions are data; transport is separate from declaration.

  **干净对应：** 能力由其提供方声明，而不是硬编码在 Agent 里；工具描述是数据；传输与声明相分离。

- **Differs:** SendOS has no MCP. It has a bespoke manifest + governed-asset pipeline with tenant entitlements and published-wins precedence — stronger on governance, weaker on ecosystem interop. **This is the clearest place a standard protocol could reduce bespoke surface** (see `docs/architecture/capability-ownership.md`).

  **存在差异：** SendOS 没有 MCP。它有一条定制的"清单 + 受治理资产"流水线，带有租户权益和已发布者优先的优先级规则 —— 治理上更强，生态互操作上更弱。**这正是采用标准协议最能减少定制化表面的地方**（见 `docs/architecture/capability-ownership.md`）。

**Micro-action:** write the three-line manifest your MCP server's tools would need if SendOS adopted MCP. Which field has no MCP equivalent? (Hint: entitlement.)

**微行动：** 假设 SendOS 采用了 MCP，写出你的 MCP 服务器的工具所需的三行清单。哪个字段在 MCP 中没有对应物？（提示：权益。）

---

## Week 6 — Planning, orchestration, human approval → the decision-first runtime

**第 6 周 —— 规划、编排、人工审批 → 决策优先的运行时**

**You build:** `agentlab/orchestrator/` — plan, specialists, orchestrator, approval.
This is the highest-value bridge week for the day job.

**你要构建：** `agentlab/orchestrator/` —— 计划、专员 Agent、编排者、审批。
对日常工作而言，这是价值最高的一周桥接。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `apps/Send.Agent.Runtime/src/.../Application/Planning/ExecutionPlanner.cs` | Shape selection from topology, authority enforcement, budgets, one accountable owner<br>基于拓扑的形态选择、权限强制执行、预算、唯一的责任负责人 |
| `.../Application/Planning/TopologyClassifier.cs` | 100 lines that decide direct / specialist / squad / multi-squad, with materiality deliberately absent<br>决定 direct / specialist / squad / multi-squad 的 100 行代码，其中刻意不考虑重要性（materiality） |
| `.../Application/Planning/LogicalPlanValidator.cs` | Acyclic, closed kinds, testable acceptance criteria<br>无环、封闭的类别、可测试的验收标准 |
| `.../Domain/Execution/ExecutionPlan.cs`, `ExecutionShape.cs`, `ReviewMode.cs` | The plan, the closed shape set, and review as an orthogonal mode<br>计划、封闭的形态集合，以及作为正交模式的评审 |
| `.../Application/Approval/ApprovalCheckpoint.cs` | Persist-before-approve, `ApprovalBinding`, 6 transitions, execute-time rechecks, separation of duties, 15-min TTL<br>审批前先持久化、`ApprovalBinding`、6 种状态转换、执行时重新检查、职责分离、15 分钟 TTL |
| `.../Domain/Execution/ApprovalBinding.cs` | What is actually bound (tenant, actor, action version, content hash, authority snapshot, expiry)<br>实际绑定了什么（租户、操作者、动作版本、内容哈希、权限快照、过期时间） |
| `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` | Why materiality stopped selecting shapes — an ADR worth copying the structure of<br>为什么重要性不再用于选择形态 —— 一份结构值得照搬的 ADR |

### Questions

**问题**

1. Why is approval an `ExecutionMode` checkpoint rather than a fifth `ExecutionShape`?

   为什么审批是一个 `ExecutionMode` 检查点，而不是第五种 `ExecutionShape`？

2. `TopologyClassifier` takes no materiality parameter. What does it classify on, and what failure does removing materiality fix?

   `TopologyClassifier` 不接收重要性参数。它依据什么来分类？去掉重要性修复了什么失败？

3. What exactly does an approval bind, and which of those bindings are re-checked at execution time?

   一次审批具体绑定了哪些东西？其中哪些绑定会在执行时被重新检查？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** typed plan, smallest-sufficient shape, topology over intent-flags, approval as checkpoint, at-most-once execution.

  **干净对应：** 类型化的计划、最小且足够的形态、拓扑优先于意图标记、审批作为检查点、至多一次执行。

- **Differs:** SendOS's planner consumes published, version-pinned assets (Squad/Specialist definitions) that your mini-squad does not have; its approval path is a persisted, resumable state machine with authority-version drift detection; and its `DecisionRuntime` is a 5,379-line procedural class — a framework would replace much of it.

  **存在差异：** SendOS 的规划器使用的是已发布、锁定版本的资产（Squad/Specialist 定义），而你的迷你小队（squad）没有这些；它的审批路径是一个持久化、可恢复的状态机，带有权限版本漂移检测；它的 `DecisionRuntime` 是一个 5,379 行的过程式类 —— 一个框架就能取代其中的大部分。

**Micro-action:** add an `authority_snapshot` to your week-6 approval binding and the test that a narrowed authority after approval blocks execution. That test is the week-8 security bridge.

**微行动：** 在你第 6 周的审批绑定中加入一个 `authority_snapshot`，并补上一个测试：审批之后权限被收窄会阻止执行。这个测试就是通往第 8 周安全主题的桥梁。

---

## Week 7 — Evals and observability → `Outcome_Trace` + evaluator

**第 7 周 —— 评测与可观测性 → `Outcome_Trace` + 评测器**

**You build:** `agentlab/evals/` — dataset, harness, judges, report, CI gate.

**你要构建：** `agentlab/evals/` —— 数据集、harness（运行框架）、评审、报告、CI 关卡。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs` | The closed 21-event lifecycle, and the Phase-1 nine-event subset in the comment<br>封闭的 21 种事件生命周期，以及注释中提到的第一阶段九种事件子集 |
| `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEvent.cs` | Store-assigned monotonic `Sequence`; append-only contract<br>由存储分配的单调递增 `Sequence`；只追加的契约 |
| `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceLifecycleEvent.cs` | Typed event family projecting to one flat row with `PayloadJson`<br>投影为一条带 `PayloadJson` 的扁平行的类型化事件族 |
| `apps/Send.Agent.Runtime/src/.../Application/Outcome/IOutcomeTraceEmitter.cs` | Fire-and-forget: `Emit` must never throw, never block the request<br>发出即不管：`Emit` 绝不能抛异常，也绝不能阻塞请求 |
| `apps/Send.Agent.Runtime/src/.../Application/Runtime/TurnStage.cs` | 45 named stages with `Ran/Skipped/Failed` — the observability lesson<br>45 个带 `Ran/Skipped/Failed` 的具名阶段 —— 可观测性的一课 |
| `apps/Send.LowerLayer.Worker/src/.../Evaluation/EvaluationDimensions.cs` | The five assessable dimensions<br>五个可评估的维度 |
| `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs` | Attribution, provenance pinning, unattributable-drop, 30/0.7/0.5 evidence gate<br>归因、来源（provenance）锁定、丢弃无法归因的洞察、30/0.7/0.5 证据关卡 |
| `apps/Send.Intel.Server/src/.../ControlPlane/PublishingPipeline/PublishingService.cs` | Publish refuses without approval and without `Promoted`<br>没有审批、也没有 `Promoted` 状态时，发布会被拒绝 |

### Questions

**问题**

1. Why a store-assigned monotonic sequence rather than `OccurredAtUtc` ordering?

   为什么用由存储分配的单调序号，而不是按 `OccurredAtUtc` 排序？

2. What are the five evaluation dimensions, and what does the aggregate score deliberately *not* claim?

   五个评测维度分别是什么？汇总分数刻意*不*声称什么？

3. Where does SendOS's learning loop stop before publishing, and who must act for it to continue?

   SendOS 的学习闭环在发布之前停在哪里？必须由谁采取行动它才能继续？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** append-only trace, stage-level events with skip reasons, deterministic checks before judges, evidence gates, human-approved promotion.

  **干净对应：** 只追加的 trace、带跳过原因的阶段级事件、在评审之前先做确定性检查、证据关卡、经人工审批的晋升。

- **Differs:** SendOS's loop is currently **dry** — the Distillation Engine is real and uncalled, the stores have no production writer (see `CONCEPT-MAP.md` §0 and the repo's own `docs/architecture/reconciliation-audit.md` §F). Its evaluator scores *decisions*, not just outputs. Your week-7 suite is a working specimen of what the platform has designed but not yet wired.

  **存在差异：** SendOS 的闭环目前是**干涸的** —— Distillation Engine 真实存在但从未被调用，各个存储都没有生产环境的写入方（见 `CONCEPT-MAP.md` §0 以及仓库自己的 `docs/architecture/reconciliation-audit.md` §F）。它的评测器给*决策*打分，而不仅仅是给输出打分。你第 7 周的测试套件，就是平台已经设计好但尚未接通的那部分的一个可运行样本。

**Micro-action:** emit one event per stage of your week-2 run, including the stages that were skipped and why. That is `TurnStage`, and it is the cheapest observability win you will ever ship.

**微行动：** 在你第 2 周的运行中，为每个阶段发出一个事件，包括被跳过的阶段及其原因。这就是 `TurnStage`，也是你所能交付的最廉价的可观测性收益。

---

## Week 8 — Security, governance, cost, reliability → the governance sandwich

**第 8 周 —— 安全、治理、成本、可靠性 → 治理三明治**

**You build:** `agentlab/guard/` — injection, sandbox, authority, audit, rate limits, red team.

**你要构建：** `agentlab/guard/` —— 注入防护、沙箱、权限、审计、限流、红队测试。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `docs/architecture/governance-architecture.md` lines 223–273<br>`docs/architecture/governance-architecture.md` 第 223–273 行 | The pre-LLM gate, the post-LLM gate, and why the model can only recommend<br>LLM 调用前的关卡、LLM 调用后的关卡，以及为什么模型只能提出建议 |
| `apps/Send.Agent.Runtime/src/.../Domain/Authority/EffectiveAuthority.cs` | Intersection of nine sources; `Delegate` can only narrow<br>九个来源的交集；`Delegate` 只能收窄 |
| `.../Application/Authority/AuthoritySources.cs` | The ten boundaries including the optional Squad boundary; DataSource sourced independently<br>十个边界，包括可选的 Squad 边界；DataSource 独立获取 |
| `.../Application/Approval/ApprovalCheckpoint.cs` | Separation of duties, action hash, authority version, replay rejection, compensation<br>职责分离、动作哈希、权限版本、拒绝重放、补偿 |
| `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Filters/LicensingIngressFilter.cs` | Fail-closed licence/entitlement at ingress<br>在入口处失败即关闭的许可证/权益校验 |
| `.../Application/Ingress/IIngressAuthorizer.cs` | The ingress authorisation seam<br>入口授权接缝 |
| `.../Domain/Execution/ExecutionOrigin.cs` | What a fact says it touched<br>一个事实声明它触及了什么 |
| `docs/adrs/0002-edge-licence-check-restored.md` | A real incident: a catch-all product code denied every request; the fix and the guard test<br>一次真实事故：一个兜底的产品代码拒绝了所有请求；以及对应的修复和防护测试 |

### Questions

**问题**

1. Name the authority boundaries SendOS intersects. Can anything the model produces widen them?

   说出 SendOS 取交集的那些权限边界。模型产出的任何东西能放宽它们吗？

2. What fails closed at ingress, and what happens when the licence service is unreachable?

   入口处有哪些东西是失败即关闭的？当许可证服务不可达时会发生什么？

3. Why is the approval binding a *security* control rather than a confirmation dialog?

   为什么审批绑定是一种*安全*控制，而不是一个确认对话框？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** deny-by-default, intersection arithmetic, model output never grants authority, approval binding, append-only audit.

  **干净对应：** 默认拒绝、交集运算、模型输出从不授予权限、审批绑定、只追加的审计。

- **Differs:** SendOS is **ahead** here — do not reproduce the code, learn why each control exists. It uses in-house ABAC rather than Cedar/OPA, and app-level tenancy rather than Postgres RLS. Note one sharp detail from ADR 0002: a route→product catch-all silently denied a whole surface; the fix added "no catch-all" and a test asserting every emittable code exists in the catalogue.

  **存在差异：** SendOS 在这里是**领先**的 —— 不要照搬代码，而要学习每个控制为什么存在。它使用自研的 ABAC 而不是 Cedar/OPA，使用应用层面的多租户而不是 Postgres RLS。留意 ADR 0002 中的一个尖锐细节：一个路由→产品的兜底映射悄无声息地拒绝了整个功能面；修复方案加入了"不允许兜底"的规则，以及一个断言每个可能发出的代码都存在于目录中的测试。

**Micro-action:** write a one-page threat model of the SendOS approval path (5 threats, 5 controls, 2 gaps). Send it to a senior engineer for critique — this is the plan's recommended stretch.

**微行动：** 为 SendOS 的审批路径写一页纸的威胁模型（5 个威胁、5 个控制、2 个缺口）。把它发给一位资深工程师请他点评 —— 这是计划推荐的拓展任务。

---

## Week 9 — Capstone: Mini-SendOS → composing the runtime

**第 9 周 —— 结业项目：Mini-SendOS → 组装运行时**

**You build:** the capstone; a design proposal for one real improvement.

**你要构建：** 结业项目；以及一份针对某个真实改进的设计提案。

### Read (SendOS)

**阅读（SendOS）**

| File<br>文件 | Look for<br>关注要点 |
|---|---|
| `apps/Send.Agent.Runtime/src/.../Application/Runtime/MetaOrchestrator.cs` | Turn lifecycle: interpretation → business state → planning → dispatch<br>一轮对话的生命周期：解释 → 业务状态 → 规划 → 分发 |
| `.../Application/Runtime/DecisionRuntime.cs` | The dispatch surface: 30+ private methods; where a framework would help<br>分发的表面：30 多个私有方法；框架能在哪里帮上忙 |
| `.../Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs` | Three sources, published-wins — your capstone's catalogue merge<br>三个来源，已发布者优先 —— 对应你结业项目中的目录合并 |
| `.../Domain/Decision/DecisionInteraction.cs` | The response family your capstone's surface renders<br>你的结业项目界面所渲染的响应族 |
| `.../Domain/CaseRuntime/Case.cs`, `DecisionTask.cs` | Durable suspend/resume — built, tested, **unwired**<br>持久化的挂起/恢复 —— 已构建、已测试、**未接入** |
| `apps/Send.LowerLayer.Worker/src/.../Distillation/DistillationEngine.cs` | The learning loop's real engine<br>学习闭环的真正引擎 |
| `docs/architecture/reconciliation-audit.md` §F | The honest status matrix; a map of what is dark and why<br>坦诚的状态矩阵；一张标明哪些处于暗置状态及其原因的地图 |

### Questions

**问题**

1. Map each capstone component to the SendOS service it mirrors. Which mirror is weakest, and why?

   把结业项目的每个组件对应到它所映射的 SendOS 服务。哪一个映射最弱？为什么？

2. Which two improvements does the plan recommend proposing, and what evidence from your capstone supports each?

   计划推荐提出哪两项改进？你的结业项目中有哪些证据分别支持它们？

3. After nine weeks, which SendOS files can you now read and critique without a guide?

   九周之后，哪些 SendOS 文件你已经可以在没有指引的情况下阅读并评判？

### Maps cleanly · differs

**干净对应 · 存在差异**

- **Clean:** the whole loop — provider → capability catalogue → typed decision → topology → approval → audit → eval → learning.

  **干净对应：** 整个闭环 —— 提供商 → 能力目录 → 类型化决策 → 拓扑 → 审批 → 审计 → 评测 → 学习。

- **Differs:** SendOS runs as 10 services with licensing, tenancy, governed assets and multiple datastores; your capstone is one process. The difference is not the concepts, it is the **failure isolation and governance surface** between them.

  **存在差异：** SendOS 以 10 个服务的形式运行，带有许可证、多租户、受治理资产和多个数据存储；你的结业项目只是一个进程。区别不在于概念，而在于它们之间的**故障隔离和治理表面**。

**Micro-action:** write the one-page proposal. Recommended topics: (a) durable suspend/resume for approvals (`CaseRuntime` wiring), (b) trace → candidate evidence gating (wiring `DistillationWorkProcessor → DistillationEngine`). Both are grounded in gaps the repo documents itself.

**微行动：** 写出那份一页纸的提案。推荐主题：(a) 审批的持久化挂起/恢复（接通 `CaseRuntime`），(b) trace → 候选的证据把关（接通 `DistillationWorkProcessor → DistillationEngine`）。两者都基于仓库自己记录在案的缺口。

---

## Appendix A — answers

**附录 A —— 答案**

Check your written answers against these. They are deliberately short: if your answer is longer and
still correct, that is fine; the point is whether the *mechanism* was named.

用这些答案来检查你写下的回答。它们刻意写得很简短：如果你的答案更长但同样正确，那也没问题；关键在于你是否说出了那个*机制*。

<details>
<summary><strong>Week 1 — Model.Adapter</strong><br>第 1 周 — Model.Adapter</summary>

1. **Retry placement.** The handler owns the *candidate set*, so a retry can degrade to a different model (cost/latency/fallback) and enforce a whole-invocation time budget. An adapter-level retry can only retry the same model and cannot see the budget or the alternative.

   **重试的放置位置。** 处理器掌握着*候选集合*，所以一次重试可以降级到另一个模型（基于成本/延迟/回退），并对整次调用强制执行时间预算。适配器层面的重试只能重试同一个模型，既看不到预算，也看不到替代选项。

2. **`IsTransient` narrowness.** It returns true only for 502/504 (see `CompletionHandler.cs:484-485`). 429 is arguably the most retryable status in practice (`Retry-After`), and 500/503 are common; being too narrow wastes recoverable requests, being too wide burns money on permanent failures. The transferable point: the classification must be explicit, tested, and matched to where rate limiting actually lives (SendOS leans on ingress limits).

   **`IsTransient` 的狭窄性。** 它只对 502/504 返回 true（见 `CompletionHandler.cs:484-485`）。在实践中，429 可以说是最值得重试的状态码（`Retry-After`），而 500/503 也很常见；分类太窄会浪费本可恢复的请求，太宽则会在永久性失败上白白烧钱。可迁移的要点是：这种分类必须是显式的、经过测试的，并且要与限流实际所在的位置相匹配（SendOS 依赖的是入口处的限流）。

3. **Split of duties.** `ChatCompletionsClient` ≈ `IProviderAdapter` (payload build, response parse, usage); routing, retry, fallback, budgets and cancellation belong to `CompletionHandler` (and, in SendOS, `ModelCostProfile`/`ModelBudget`).

   **职责划分。** `ChatCompletionsClient` ≈ `IProviderAdapter`（构建请求载荷、解析响应、用量）；路由、重试、回退、预算和取消属于 `CompletionHandler`（在 SendOS 中还有 `ModelCostProfile`/`ModelBudget`）。

</details>

<details>
<summary><strong>Week 2 — capability registry and loop</strong><br>第 2 周 — 能力注册表与循环</summary>

1. **Fields with no plain-tool analogue.** `ReadOrWrite`, `RiskLevel`, `ApprovalRequirement`, `SideEffects`, `IdempotencyRequirement`, `CompensationSupport`, `AuditRequirement`, `TenantAvailability`, `RequiredPermissions`, `ProvidedEvidence`, `ResultResourceType`, `ActionKind`, `GovernedAssetReference`, `Version`, `EffectiveDate`. Each prevents a governance failure: unapproved writes, cross-tenant exposure, ambiguous result types, unversioned assets, unverifiable side effects.

   **普通工具中没有对应物的字段。** `ReadOrWrite`、`RiskLevel`、`ApprovalRequirement`、`SideEffects`、`IdempotencyRequirement`、`CompensationSupport`、`AuditRequirement`、`TenantAvailability`、`RequiredPermissions`、`ProvidedEvidence`、`ResultResourceType`、`ActionKind`、`GovernedAssetReference`、`Version`、`EffectiveDate`。每个字段都防止了一种治理失败：未经审批的写入、跨租户暴露、含糊的结果类型、无版本的资产、无法核实的副作用。

2. **Structural matching.** Objective keywords are free text and produce false negatives/positives; declared metadata (`ProvidedEvidence`, `ActionKind`, `ResultResourceType`) is a contract. A mis-declared capability then fails visibly rather than silently hiding a correct one — the code comments (e.g. on `ProvidedEvidence`) record exactly that false-negative incident.

   **结构化匹配。** 目标关键词是自由文本，会产生漏报/误报；而声明的元数据（`ProvidedEvidence`、`ActionKind`、`ResultResourceType`）是一份契约。这样一来，声明错误的能力会显式地失败，而不是悄无声息地把正确的能力藏起来 —— 代码注释（例如 `ProvidedEvidence` 上的注释）恰好记录了那次漏报事故。

3. **Where the loop is.** Inside `DecisionRuntime`/shape handlers as a bounded goal loop (`Runtime/Iteration/BoundedIterativeExecutionLoop`, `Goals/GoalCompletionLoop`), specialised per shape. A generic ReAct loop makes every tool reachable from every step, which is hard to govern; SendOS instead constrains *which* capability can serve *which* classified turn.

   **循环在哪里。** 它作为一个有界目标循环位于 `DecisionRuntime`/各形态处理器内部（`Runtime/Iteration/BoundedIterativeExecutionLoop`、`Goals/GoalCompletionLoop`），并按形态分别特化。通用的 ReAct 循环会让每个工具在每一步都可达，这很难治理；SendOS 则约束了*哪个*能力可以服务于*哪种*已分类的对话轮次。

</details>

<details>
<summary><strong>Week 3 — structured output and typed decisions</strong><br>第 3 周 — 结构化输出与类型化决策</summary>

1. **Validate-after vs constrained decoding.** Cost: retries, extra latency/cost, and a failure rate that scales with schema complexity. It is the right trade when not every provider supports grammars, when the schema needs product-level rules (budgets, semantics) that grammars cannot express, and when the validation diagnostics are themselves the product (repair messages, audit).

   **事后校验与约束解码。** 代价：重试、额外的延迟/成本，以及随 schema 复杂度上升的失败率。当并非每个提供商都支持语法约束、当 schema 需要语法约束无法表达的产品级规则（预算、语义）、以及当校验诊断信息本身就是产品的一部分（修复消息、审计）时，这是正确的取舍。

2. **Never surfacing invalid output.** The caller has one branch: valid or not-valid. It prevents partially-valid decisions rendering, and makes failure an explicit `Limitation` rather than a downstream wrong action.

   **从不暴露无效输出。** 调用方只有一个分支：有效或无效。这能防止部分有效的决策被渲染出来，并让失败成为一个显式的 `Limitation`，而不是在下游变成一个错误的动作。

3. **Trim vs reject.** Trimming can silently change meaning (cutting a headline can invert it); rejecting costs calls but preserves the model's full statement for a human. SendOS trims presentation *after* the decision is semantically fixed, and rejects at the schema gate — the two serve different failure classes.

   **裁剪与拒绝。** 裁剪可能会悄悄改变含义（截断一个标题可能让它的意思反转）；拒绝要多花调用次数，但能为人保留模型的完整陈述。SendOS 在决策的语义*确定之后*才裁剪展示内容，而在 schema 关卡处做拒绝 —— 两者针对的是不同类别的失败。

</details>

<details>
<summary><strong>Week 4 — context and memory</strong><br>第 4 周 — 上下文与记忆</summary>

1. **Empty is not an error.** "No matching governed records" is information the reasoner must be able to state honestly; conflating it with failure forces retries and encourages fabrication. It is also a security separation: the boundary reports absence, it does not reason about it.

   **空不是错误。** "没有匹配的受治理记录"是推理者必须能够如实陈述的信息；把它与失败混为一谈会迫使系统重试，并助长捏造。它也是一种安全上的分离：边界只报告"不存在"，而不对此进行推理。

2. **Exclusions in `SpecialistContext`.** No full Business_State, no transcript, no unrelated evidence, no other tenants' data. Each exclusion limits blast radius, prompt-injection surface and data-minimisation exposure — governance, not just token savings.

   **`SpecialistContext` 中的排除项。** 没有完整的 Business_State，没有对话记录，没有无关的证据，没有其他租户的数据。每一项排除都限制了爆炸半径、提示词注入的攻击面以及数据最小化方面的暴露 —— 这是治理问题，而不仅仅是节省 token。

3. **Hash embeddings.** They prove the retrieval plumbing (index, query, citations) end-to-end without a vendor dependency or a per-token cost, and they are deterministic so tests are stable. The honest upgrade is swapping `IEmbeddingGenerator` for a real model — the plumbing already exists.

   **哈希嵌入。** 它们在没有厂商依赖、也没有按 token 计费成本的情况下，端到端地验证了检索管道（索引、查询、引用），而且是确定性的，因此测试很稳定。坦白说，剩下的升级就是把 `IEmbeddingGenerator` 换成一个真实的模型 —— 管道已经就绪。

</details>

<details>
<summary><strong>Week 5 — connectors, manifests, MCP</strong><br>第 5 周 — 连接器、清单、MCP</summary>

1. **Who decides.** The connector *declares* (`ICapabilityManifestProvider`), SendOS governance *publishes*, and the runtime *assembles* the registry (`CapabilityCatalogueAssembler`: platform-owned → connector manifests → published assets, with **published wins**). So a connector cannot unilaterally introduce a capability into the governed surface.

   **谁来决定。** 连接器负责*声明*（`ICapabilityManifestProvider`），SendOS 治理层负责*发布*，运行时负责*汇编*注册表（`CapabilityCatalogueAssembler`：平台自有 → 连接器清单 → 已发布资产，且**已发布者优先**）。因此连接器无法单方面把某个能力引入受治理的表面。

2. **MCP vs manifests.** MCP makes ecosystem interop and dynamic discovery easy; manifests + published assets make entitlement, versioning and governance easy. MCP's server-declared tools are exactly the thing a governance layer must re-check — the two are complementary, not competing.

   **MCP 与清单。** MCP 让生态互操作和动态发现变得容易；清单 + 已发布资产则让权益、版本管理和治理变得容易。MCP 中由服务器声明的工具，恰恰是治理层必须重新检查的东西 —— 两者是互补的，而不是竞争的。

3. **Execution origin.** It lets audit, trace and UI say what was real (`ControlledLiveExecution`), simulated, or demo data without inferring it from a provider name. An undeclared origin must be refused fail-closed at the boundary — otherwise every downstream claim about "what actually happened" is unverifiable.

   **执行来源。** 它让审计、trace 和 UI 能够说明哪些是真实的（`ControlledLiveExecution`）、哪些是模拟的、哪些是演示数据，而无需从提供商名称去推断。未声明的来源必须在边界处以失败即关闭的方式被拒绝 —— 否则下游所有关于"实际发生了什么"的说法都无法核实。

</details>

<details>
<summary><strong>Week 6 — planning, topology, approval</strong><br>第 6 周 — 规划、拓扑、审批</summary>

1. **Approval is not a shape.** Shapes describe *how work is executed*; approval is a *governance checkpoint* that can interrupt any shape. Making it a shape would mean choosing between "squad with approval" and "squad without", and the two could drift; as an orthogonal `ExecutionMode`, every shape inherits the same gate. `ReviewMode` is orthogonal for the same reason.

   **审批不是一种形态。** 形态描述的是*工作如何被执行*；审批则是一个可以打断任何形态的*治理检查点*。如果把它做成一种形态，就意味着要在"带审批的小队"和"不带审批的小队"之间做选择，而这两者可能会逐渐分化；作为一个正交的 `ExecutionMode`，每种形态都继承同一个关卡。`ReviewMode` 之所以是正交的，也是出于同样的原因。

2. **Topology, not materiality.** It classifies on bound-plan structure: ≥2 disconnected components → multi-squad; single capability node → direct capability; single reasoning node → direct specialist; ≥2 connected node → single squad. Materiality used to select shapes, which conflated "important" with "needs many agents" and let model-authored labels pick a shape nothing could back; the classifier now ignores both, and an unbacked shape fails closed.

   **依据拓扑，而不是重要性。** 它依据已绑定计划的结构来分类：≥2 个互不相连的分量 → 多小队；单个能力节点 → 直接能力；单个推理节点 → 直接专员 Agent；≥2 个相连节点 → 单小队。过去由重要性来选择形态，这把"重要"与"需要很多 Agent"混为一谈，还让模型撰写的标签选出了一个没有任何东西能支撑的形态；如今分类器对两者都不予理会，而无支撑的形态会失败即关闭。

3. **What approval binds.** Tenant, actor, action version, action content hash, effective-authority grant snapshot, granted-at, expiry (default 15 minutes), approver role, authority version. At execution: proposal still approved with a live binding, action version/hash still match, authority still covers, approval not expired, approval not consumed by another key, proposer ≠ approver, approver holds the role/permission. Any failure refuses.

   **审批绑定了什么。** 租户、操作者、动作版本、动作内容哈希、有效权限授予快照、授予时间、过期时间（默认 15 分钟）、审批者角色、权限版本。执行时检查：提议仍处于已审批状态且绑定仍然有效、动作版本/哈希仍然匹配、权限仍然覆盖、审批未过期、审批未被另一个键消费、提议者 ≠ 审批者、审批者持有相应角色/权限。任何一项不满足都会拒绝执行。

</details>

<details>
<summary><strong>Week 7 — trace, eval, publish</strong><br>第 7 周 — trace、评测、发布</summary>

1. **Why a store sequence.** Timestamps can collide, go backwards across instances, or be rewritten by clock correction; a store-assigned sequence gives a total, gap-tolerant order that replay depends on (`OutcomeTraceEvent.Sequence`, unique-indexed).

   **为什么用存储序号。** 时间戳可能冲突，可能在不同实例之间倒退，也可能因时钟校正而被改写；由存储分配的序号提供了一个全序的、容忍空缺的顺序，而重放正依赖于此（`OutcomeTraceEvent.Sequence`，带唯一索引）。

2. **Five dimensions.** Correctness, PolicyCompliance, OutcomeAlignment, EvidenceGrounding, ExecutionQuality. The aggregate is a summary of *assessed* dimensions only — it is not a truth claim, and an unassessed dimension must not be silently averaged in as zero.

   **五个维度。** Correctness、PolicyCompliance、OutcomeAlignment、EvidenceGrounding、ExecutionQuality。汇总分数只是对*已评估*维度的概括 —— 它不是一个关于真相的断言，未评估的维度绝不能被悄悄当作零计入平均值。

3. **Where the loop stops.** At a Draft candidate: distillation produces evidence-gated insights, the trainer synthesises a candidate diff, the promoter is submit-only, and `PublishingService` refuses without a recorded human approval and a `Promoted` status. The model can recommend; a person must publish.

   **闭环停在哪里。** 停在一个 Draft 状态的候选上：蒸馏产出经证据把关的洞察，训练器合成一个候选差异，晋升器只能提交，而 `PublishingService` 在没有已记录的人工审批和 `Promoted` 状态时会拒绝发布。模型可以提出建议；必须由人来发布。

</details>

<details>
<summary><strong>Week 8 — security and governance</strong><br>第 8 周 — 安全与治理</summary>

1. **Boundaries.** User, Tenant, Application, Entitlement, Playbook, Specialist, Tool, DataSource, ApprovalState, and (application layer) Squad; `EffectiveAuthority` intersects them and `Delegate` can only narrow. No — model output is deliberately not a source, so it cannot widen authority; it can only *propose* something that must pass the same arithmetic.

   **边界。** User、Tenant、Application、Entitlement、Playbook、Specialist、Tool、DataSource、ApprovalState，以及（应用层的）Squad；`EffectiveAuthority` 对它们取交集，而 `Delegate` 只能收窄。不能 —— 模型输出被刻意排除在来源之外，所以它无法放宽权限；它只能*提议*某件事，而这件事必须通过同样的运算。

2. **Ingress fail-closed.** Licence/entitlement, tenant and actor resolution, quotas, idempotency. On a licensing outage or timeout the request is denied (`Unavailable`/deny), never allowed; cached grants cannot authorise reads during an outage.

   **入口处失败即关闭。** 许可证/权益、租户与操作者解析、配额、幂等性。当许可证服务宕机或超时时，请求会被拒绝（`Unavailable`/拒绝），而绝不会被放行；宕机期间，缓存的授权也不能为读取操作授权。

3. **Approval binding as security.** It converts "the model said yes" into "a specific person, with a specific authority snapshot, approved a specific immutable action before a deadline". Replay, post-approval edit, authority drift, expiry and self-approval are all rejected — none of that is a UX concern.

   **作为安全控制的审批绑定。** 它把"模型说可以"转变为"某个特定的人，带着特定的权限快照，在截止时间之前审批了某个特定且不可变的动作"。重放、审批后修改、权限漂移、过期以及自我审批都会被拒绝 —— 这些都不是用户体验层面的问题。

</details>

<details>
<summary><strong>Week 9 — capstone and proposal</strong><br>第 9 周 — 结业项目与提案</summary>

1. **Mapping.** Provider layer → `Send.Model.Adapter`; capability catalogue → `Send.Agent.Runtime` registry + `Send.Intel.Server` published assets; decision runtime → `MetaOrchestrator` + `DecisionRuntime`; governance → `EffectiveAuthority` + `ApprovalCheckpoint` + ingress; learning loop → `Send.Usage.Collector` + `Send.LowerLayer.Worker` + Intel publish; surface → Conversation Layer/website. Weakest mirror: the learning loop, because SendOS's is dry and yours is wired — which is why it is a good proposal topic.

   **映射关系。** 提供商层 → `Send.Model.Adapter`；能力目录 → `Send.Agent.Runtime` 注册表 + `Send.Intel.Server` 已发布资产；决策运行时 → `MetaOrchestrator` + `DecisionRuntime`；治理 → `EffectiveAuthority` + `ApprovalCheckpoint` + 入口；学习闭环 → `Send.Usage.Collector` + `Send.LowerLayer.Worker` + Intel 发布；界面 → Conversation Layer/网站。最弱的映射：学习闭环，因为 SendOS 的是干涸的，而你的是接通的 —— 这正是它适合作为提案主题的原因。

2. **Two recommended proposals.** Durable suspend/resume for approvals (`CaseRuntime` is built and unwired; your SQLite resume + CAS is a working sketch), or trace → candidate evidence gating (wire the Distillation Engine into the worker and prove an evidence-gated candidate can reach a human-approved publish).

   **两个推荐的提案。** 审批的持久化挂起/恢复（`CaseRuntime` 已构建但未接入；你基于 SQLite 的恢复 + CAS 就是一个可运行的草图），或者 trace → 候选的证据把关（把 Distillation Engine 接入工作者，并证明一个经证据把关的候选能够走到经人工审批的发布）。

3. **What you can read now.** `DecisionInteraction`, `EffectiveAuthority`, `ApprovalCheckpoint`, `TopologyClassifier`, `OutcomeTrace*`, `StructuredCompletionHandler` — and you can say which of them you would change and why.

   **你现在能读懂什么。** `DecisionInteraction`、`EffectiveAuthority`、`ApprovalCheckpoint`、`TopologyClassifier`、`OutcomeTrace*`、`StructuredCompletionHandler` —— 而且你能说出其中哪些你会修改，以及为什么。

</details>

---

## Appendix B — path index and doc-drift warnings

**附录 B —— 路径索引与文档偏差警告**

**Docs that are stale (checked 2026-10-18) — use the code paths, not these claims:**

**已过时的文档（2026-10-18 检查）—— 请使用代码路径，而不是这些说法：**

| Doc says<br>文档说法 | Code says<br>代码事实 |
|---|---|
| Decision runtime behind `DecisionFirst:Enabled`, 404 when off (`README.md:52`, `docs/README.md:10`, `docs/business/09-status-and-roadmap.md:26`)<br>决策运行时受 `DecisionFirst:Enabled` 控制，关闭时返回 404（`README.md:52`、`docs/README.md:10`、`docs/business/09-status-and-roadmap.md:26`） | Flag removed: `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417`<br>开关已移除：`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417` |
| Shape chosen from materiality via `SelectShape` (`docs/runtime-orchestration-flow.md:243-301`)<br>通过 `SelectShape` 根据重要性选择形态（`docs/runtime-orchestration-flow.md:243-301`） | Topology only: `.../Application/Planning/ExecutionPlanner.cs:143-219` + `TopologyClassifier.cs`<br>只依据拓扑：`.../Application/Planning/ExecutionPlanner.cs:143-219` + `TopologyClassifier.cs` |
| `UseLogicalPlanner` "defaults false" (`ExecutionPlanningOptions.cs:69-74` comment)<br>`UseLogicalPlanner`"默认为 false"（`ExecutionPlanningOptions.cs:69-74` 中的注释） | Initialiser is `= true` (`:75`)<br>初始化器是 `= true`（`:75`） |
| `Send.Distillation.Engine` / `Send.Intel.Trainer` / `Send.Intel.Promoter` are apps (`README.md:59-67`)<br>`Send.Distillation.Engine` / `Send.Intel.Trainer` / `Send.Intel.Promoter` 是应用（`README.md:59-67`） | Removed as projects; learning subsystem is `apps/Send.LowerLayer.Worker`<br>已作为项目被移除；学习子系统是 `apps/Send.LowerLayer.Worker` |
| `Send.Usage.Collector` is a placeholder (`docs/implementation-inventory.md:31,153`)<br>`Send.Usage.Collector` 是占位符（`docs/implementation-inventory.md:31,153`） | 24 source files incl. append-only EF store, migrations, replay endpoints<br>24 个源文件，包括只追加的 EF 存储、迁移、回放端点 |

**Files worth bookmarking:** `docs/architecture/governance-architecture.md` §5–6b ·
`docs/architecture/reconciliation-audit.md` §F ·
`docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` ·
`docs/adrs/0002-edge-licence-check-restored.md`.

**值得加入书签的文件：** `docs/architecture/governance-architecture.md` §5–6b · `docs/architecture/reconciliation-audit.md` §F · `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` · `docs/adrs/0002-edge-licence-check-restored.md`。

---

## Appendix C — weekly bridge log template

**附录 C —— 每周桥接日志模板**

Copy into `notes/weekNN-bridge.md` (3 minutes at the end of each session):

复制到 `notes/weekNN-bridge.md` 中（每次课时结束时花 3 分钟）：

```markdown
# Week NN bridge — <mechanism>

## Questions
Q1:
Q2:
Q3:

## Maps cleanly (SendOS → my lab)
-
-

## Differs / would change
-
-

## One-sentence transfer
"When I see <SendOS concept>, I will check <my lab's mechanism> for <failure mode>."
```
