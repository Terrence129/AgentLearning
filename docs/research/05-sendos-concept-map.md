# SendOS Concept Map — what the platform actually implements, and what to rebuild in miniature

**SendOS 概念地图 —— 平台实际实现了什么，以及该做成微缩版重建什么**

> **Source:** read-only analysis of `D:\DevRepo\SendProjects\SendOS\SendOs` on 2026-10-18 (on macOS/Linux, substitute your local SendOS checkout path). Nothing was modified, built or executed. Paths below are repo-relative to that root.
> **Audience:** an intern contributing to SendOS who needs transferable agent-engineering skill, not familiarity with one codebase.
> **Method:** read `README.md`, `docs/architecture/*.md`, `docs/implementation-inventory.md`, `docs/runtime-orchestration-flow.md`, `docs/adrs/`, `docs/business/01`, then verified claims against code in `apps/Send.Agent.Runtime`, `apps/Send.Model.Adapter`, `apps/Send.Intel.Server`, `apps/Send.Usage.Collector`, `apps/Send.LowerLayer.Worker`, `libraries/Send.Context.Gateway`, `libraries/Send.Work.Capability`.
>
> **来源：** 2026-10-18 对 `D:\DevRepo\SendProjects\SendOS\SendOs` 所做的只读分析（在 macOS/Linux 上请替换为你本地 SendOS 代码检出的路径）。没有修改、构建或执行任何东西。下文路径均相对于该根目录。
>
> **读者：** 为 SendOS 做贡献的实习生，他需要的是可迁移的 Agent 工程技能，而不是对某一个代码库的熟悉程度。
>
> **方法：** 阅读了 `README.md`、`docs/architecture/*.md`、`docs/implementation-inventory.md`、`docs/runtime-orchestration-flow.md`、`docs/adrs/`、`docs/business/01`，然后对照 `apps/Send.Agent.Runtime`、`apps/Send.Model.Adapter`、`apps/Send.Intel.Server`、`apps/Send.Usage.Collector`、`apps/Send.LowerLayer.Worker`、`libraries/Send.Context.Gateway`、`libraries/Send.Work.Capability` 中的代码核实了各项说法。

---

## 0. Read this first: the docs are three vintages, and the code wins

**0. 先读这一节：文档分属三个年代，以代码为准**

The repo holds **current docs, target docs, and frozen audits**, and they contradict each other. Five verified examples:

这个仓库里同时存放着**现行文档、目标文档和已冻结的审计**，而且它们彼此矛盾。下面是五个已核实的例子：

| # | Doc says<br>文档说法 | Code says<br>代码事实 | Cite<br>出处 |
|---|---|---|---|
| 1 | Decision runtime is behind `DecisionFirst:Enabled`, 404 when off<br>决策运行时受 `DecisionFirst:Enabled` 控制，关闭时返回 404 | The flag **was removed**; the governed path is not opt-in<br>该开关**已被移除**；受治理的路径不是可选启用的 | `README.md:52`; `docs/README.md:10` vs `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417` |
| 2 | Shape chosen from `Materiality` + `PossibleIntentions` (`SelectShape`)<br>形态根据 `Materiality` + `PossibleIntentions` 选择（`SelectShape`） | Shape chosen **only** from plan topology via `TopologyClassifier` over a `BoundPlanGraph`<br>形态**只**根据计划拓扑选择，由 `TopologyClassifier` 作用于 `BoundPlanGraph` 得出 | `docs/runtime-orchestration-flow.md:243-301` vs `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Planning/ExecutionPlanner.cs:143-219` |
| 3 | `UseLogicalPlanner` "Defaults `false`"<br>`UseLogicalPlanner`"默认为 `false`" | Initialiser is `= true` (XML comment stale)<br>初始化器是 `= true`（XML 注释已过时） | `.../Planning/ExecutionPlanningOptions.cs:69-75` |
| 4 | `Send.Usage.Collector` and `Send.Intel.Admin` are placeholders<br>`Send.Usage.Collector` 和 `Send.Intel.Admin` 是占位符 | Usage Collector has 24 source files: append-only EF store, migrations, write queue, replay endpoints<br>Usage Collector 有 24 个源文件：只追加的 EF 存储、迁移、写入队列、回放端点 | `docs/implementation-inventory.md:31,153` vs `apps/Send.Usage.Collector/src/**` |
| 5 | `Send.Distillation.Engine` / `Send.Intel.Trainer` / `Send.Intel.Promoter` are apps<br>`Send.Distillation.Engine` / `Send.Intel.Trainer` / `Send.Intel.Promoter` 是应用 | They no longer exist as projects; the learning subsystem is `apps/Send.LowerLayer.Worker` (435 `.cs`)<br>它们已不再作为项目存在；学习子系统是 `apps/Send.LowerLayer.Worker`（435 个 `.cs`） | `README.md:59-67` vs `apps/Send.LowerLayer.Worker/**`; `docs/architecture/reconciliation-audit.md:19` records the removal<br>`README.md:59-67` 对比 `apps/Send.LowerLayer.Worker/**`；`docs/architecture/reconciliation-audit.md:19` 记录了这次移除 |

Even the honest audit is frozen: `docs/architecture/reconciliation-audit.md` (HEAD `3ee901e`) calls the logical planner off and `TopologyClassifier` dead code (lines 103-109, 216-223), which no longer matches the code.

就连那份坦诚的审计也已冻结：`docs/architecture/reconciliation-audit.md`（HEAD `3ee901e`）说逻辑规划器处于关闭状态、`TopologyClassifier` 是死代码（第 103-109、216-223 行），这已与代码不再相符。

**Working rule:** `docs/` is design intent and orientation; `file.cs` is fact. When they disagree, the disagreement is worth a small PR — the repo's best habit is that every claim is cited to `file:line` and stale claims are treated as defects.

**工作规则：** `docs/` 代表设计意图和方向指引；`file.cs` 才是事实。当两者不一致时，这种不一致值得提一个小 PR —— 这个仓库最好的习惯就是每个说法都引用到 `file:line`，并把过时的说法当作缺陷对待。

**Scale (grep counts; suite not run):** 10 apps, 25 `libraries/` projects, 979 `.cs` under Agent Runtime, 435 under `Send.LowerLayer.Worker`, 1,122 test files with ≈6,329 `[Fact]`/`[Theory]` and ≈486 FsCheck `[Property]` attributes.

**规模（grep 计数；未运行测试套件）：** 10 个应用，25 个 `libraries/` 项目，Agent Runtime 下有 979 个 `.cs`，`Send.LowerLayer.Worker` 下有 435 个，1,122 个测试文件，其中约 6,329 个 `[Fact]`/`[Theory]` 特性和约 486 个 FsCheck `[Property]` 特性。

---

## 1. The machine in one page

**1. 一页看懂这台机器**

| Stage<br>阶段 | Where<br>位置 | What it really does<br>实际做了什么 | State<br>状态 |
|---|---|---|---|
| Ingress<br>入口 | `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Filters/LicensingIngressFilter.cs`; `Controllers/ChatController.cs:61` (`POST api/chat/decision`) | Fail-closed licence/entitlement, tenant+actor claims, idempotency<br>失败即关闭的许可证/权益校验、租户 + 操作者声明、幂等性 | real<br>真实 |
| Understanding<br>理解 | `.../Application/Runtime/MetaOrchestrator.cs`; `.../Understanding/CanonicalTurnInterpreter.cs` | Observe → Resolve → Ground → Interpret → Validate → one `MessageUnderstanding`<br>观察 → 解析 → 落地（grounding）→ 解释 → 校验 → 产出一个 `MessageUnderstanding` | real (grounding thin)<br>真实（grounding 较薄弱） |
| Elevation<br>提升 | `.../Application/IntentElevation/IntentElevator.cs` | Deterministic projection to `InterpretedGoal`; ambiguity→clarify is a pure function<br>确定性地投影为 `InterpretedGoal`；歧义 → 澄清是一个纯函数 | real<br>真实 |
| Planning<br>规划 | `.../Application/Planning/ExecutionPlanner.cs` | Published assets, effective authority, `TopologyClassifier`, budgets, one accountable owner<br>已发布资产、有效权限、`TopologyClassifier`、预算、唯一的责任负责人 | real (topology ON)<br>真实（拓扑已开启） |
| Execution<br>执行 | `.../Execution/DirectCapabilityHandler.cs`, `Specialist/DirectSpecialistRunner.cs`, `Squad/SingleSquadHandler.cs`, `Squad/MultiSquadShapeHandler.cs` | Four shapes; Squads coordinate Specialists on a structured in-memory bus<br>四种形态；小队（squad）在结构化的内存总线上协调专员 Agent（specialist） | Direct real; Squad paths thin<br>Direct 路径真实；Squad 路径较薄弱 |
| Reasoning<br>推理 | `apps/Send.Model.Adapter/src/**` via `ISpecialistReasoner`<br>经由 `ISpecialistReasoner` 调用 `apps/Send.Model.Adapter/src/**` | Provider-independent completion, schema-validated output, budget-aware routing<br>与模型提供商（provider）无关的补全、经 schema 校验的输出、感知预算的路由 | real<br>真实 |
| Approval gate<br>审批关卡 | `.../Approval/ApprovalCheckpoint.cs`; `.../Execution/AuthoritativeActionExecutor` | Persist proposal → bound approval → revalidate authority → execute at-most-once<br>持久化提议 → 绑定式审批 → 重新校验权限 → 至多执行一次 | real<br>真实 |
| Response<br>响应 | `Domain/Decision/DecisionInteraction.cs`; `Api/Presentation/DecisionInteractionMapper.cs` | Closed family of 11 typed responses with presentation budgets<br>由 11 种类型化响应组成的封闭族，带有展示预算 | real<br>真实 |
| Trace | `.../Outcome/IOutcomeTraceEmitter.cs` → outbox → `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEvent.cs` | 21-event closed lifecycle, append-only, monotonic `Sequence`<br>21 种事件的封闭生命周期，只追加，`Sequence` 单调递增 | real (emission shallow)<br>真实（事件发出较浅） |
| Learning<br>学习 | `apps/Send.LowerLayer.Worker/src/**` | Distillation → evaluation → candidate synthesis → submit-only promotion<br>蒸馏 → 评测 → 候选合成 → 仅提交式晋升 | real code, **dry loop**<br>代码真实，**闭环干涸** |

Two facts explain most of the repo: **every step is a typed, testable seam**, and **several seams are not connected**. `DecisionRuntime.cs` is 5,379 lines and `MetaOrchestrator.cs` 2,685 — orchestration is a large procedural class, not a graph interpreter.

两个事实可以解释这个仓库的大部分情况：**每一步都是一个类型化、可测试的接缝（seam）**，以及**有好几个接缝并没有连起来**。`DecisionRuntime.cs` 有 5,379 行，`MetaOrchestrator.cs` 有 2,685 行 —— 编排是一个庞大的过程式类，而不是一个图解释器。

---

## 2. Concept map — industry term → SendOS implementation

**2. 概念地图 —— 业界术语 → SendOS 实现**

Status: **Implemented** (real and reachable) · **Partial** · **Dark** (built, tested, not on live path) · **Missing**.

状态：**Implemented**（已实现：真实且可达）· **Partial**（部分实现）· **Dark**（暗置：已构建、已测试，但不在实际运行路径上）· **Missing**（缺失）。

### 2.1 Understanding and intent

**2.1 理解与意图**

| Industry concept<br>业界概念 | How SendOS implements it<br>SendOS 如何实现 | Where<br>位置 | Status<br>状态 | Learn externally<br>外部学习资源 |
|---|---|---|---|---|
| Intent understanding<br>意图理解 | One authoritative model interpretation, then deterministic projection to `InterpretedGoal`; the model never sets `ClarificationRequired`<br>一次权威的模型解释，随后确定性地投影为 `InterpretedGoal`；模型从不设置 `ClarificationRequired` | `.../Understanding/CanonicalTurnInterpreter.cs`; `.../IntentElevation/IntentElevator.cs:96-215` | Implemented<br>已实现 | Structured extraction / function calling; dialogue state<br>结构化抽取 / 函数调用；对话状态 |
| Clarify-vs-act policy<br>澄清还是行动的策略 | Pure `RequiresClarification(ambiguity, threshold) => ambiguity >= threshold`; prior context lowers ambiguity<br>纯函数 `RequiresClarification(ambiguity, threshold) => ambiguity >= threshold`；先前的上下文会降低歧义度 | `IntentElevator.cs:80,111-124` | Implemented<br>已实现 | Value-of-information clarification<br>基于信息价值的澄清 |
| Grounding before inference<br>先落地再推断 | Observe→Resolve→Ground→Interpret→Validate; `StatedFactFidelity` reconciles interpretation against the literal words<br>观察→解析→落地→解释→校验；`StatedFactFidelity` 将解释结果与用户的原话进行核对 | `.../Understanding/**`; `IntentElevator.cs:137-150` | Partial (external resolve tiers + live fetch unregistered)<br>部分实现（外部解析层级 + 实时获取尚未注册） | Tool-augmented extraction<br>工具增强的抽取 |
| Reserved artifact types<br>保留的产物类型 | Response family **cannot represent** Chart/Dashboard/VisualisationSpec — type-system enforced<br>响应族**无法表示** Chart/Dashboard/VisualisationSpec —— 由类型系统强制保证 | `Domain/Decision/DecisionInteraction.cs:15-28` | Implemented<br>已实现 | Discriminated unions / API contracts<br>可辨识联合 / API 契约 |
| Presentation budgets<br>展示预算 | Headline ≤ 12 words, ≤ 4 next moves, 1 question ≤ 3 options<br>标题 ≤ 12 个词，后续动作 ≤ 4 个，1 个问题 ≤ 3 个选项 | `.../Decision/PresentationBudgetEnforcer.cs`; `.../Properties/PresentationBudgetPropertyTests.cs` | Implemented<br>已实现 | UI-shaped LLM output<br>面向 UI 形态的 LLM 输出 |

### 2.2 Planning and orchestration

**2.2 规划与编排**

| Industry concept<br>业界概念 | How SendOS implements it<br>SendOS 如何实现 | Where<br>位置 | Status<br>状态 | Learn externally<br>外部学习资源 |
|---|---|---|---|---|
| Plan-then-execute<br>先计划后执行 | `ILogicalPlanner` → `LogicalPlanValidator` (acyclic, closed kinds) → `CapabilityResolver` → `BoundPlanGraph`<br>`ILogicalPlanner` → `LogicalPlanValidator`（无环、封闭的类别）→ `CapabilityResolver` → `BoundPlanGraph` | `.../Application/Planning/*` | Implemented (ON)<br>已实现（已开启） | Plan-and-Solve; LLM Compiler; task DAGs<br>Plan-and-Solve；LLM Compiler；任务 DAG |
| Right-sizing topology<br>恰当规模的拓扑 | `TopologyClassifier`: ≥2 components → `MultiSquad`; 1 capability node → `DirectCapability`; 1 reasoning node → `DirectSpecialist`; ≥2 connected → `SingleSquad`; unbacked → **fail closed**<br>`TopologyClassifier`：≥2 个连通分量 → `MultiSquad`；1 个能力节点 → `DirectCapability`；1 个推理节点 → `DirectSpecialist`；≥2 个相连节点 → `SingleSquad`；无支撑 → **失败即关闭** | `.../Planning/TopologyClassifier.cs:28-102`; `ExecutionPlanner.cs:143-219` | Implemented<br>已实现 | Cost-aware orchestration; model cascades<br>成本感知的编排；模型级联 |
| Definition vs instance<br>定义与实例 | Specialist = published, version-pinned asset; instance = ephemeral `SpecialistContext`, never persisted<br>专员 Agent = 已发布、锁定版本的资产；实例 = 临时的 `SpecialistContext`，从不持久化 | `Domain/Execution/SpecialistContext.cs`; `.../Squad/SpecialistActivator.cs` | Implemented<br>已实现 | Agent registries; prompt versioning<br>Agent 注册表；提示词版本管理 |
| Multi-agent messaging<br>多 Agent 消息传递 | `ISquadMessageBus` carries structured `SquadMessage`; transcript stays internal, one `DecisionInteraction` leaves<br>`ISquadMessageBus` 承载结构化的 `SquadMessage`；对话记录留在内部，只有一个 `DecisionInteraction` 对外输出 | `.../Squad/InMemorySquadMessageBus.cs`, `SquadOrchestrator.cs` | Implemented (cross-squad depth thin)<br>已实现（跨小队的深度较薄弱） | FIPA-ACL; blackboard; A2A<br>FIPA-ACL；黑板模式；A2A |
| Review as orthogonal mode<br>作为正交模式的评审 | `ReviewMode` policy-selected, never a fifth shape, never model-chosen; `ReviewGatedApproval`<br>`ReviewMode` 由策略选择，从不是第五种形态，也从不由模型选择；`ReviewGatedApproval` | `.../Review/**`; `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs` | Implemented<br>已实现 | LLM-as-judge; constitutional review<br>LLM 评审（LLM-as-judge）；宪法式评审 |
| Bounded iteration<br>有界迭代 | `BoundedIterativeExecutionLoop`, `GoalCompletionLoop`, `IterationBudget`, `BudgetGuard` | `.../Runtime/Iteration/**`; `Domain/Execution/BudgetGuard.cs` | Implemented<br>已实现 | ReAct; Reflexion; budgeted agents<br>ReAct；Reflexion；受预算约束的 Agent |

### 2.3 Governance and tool use

**2.3 治理与工具使用**

| Industry concept<br>业界概念 | How SendOS implements it<br>SendOS 如何实现 | Where<br>位置 | Status<br>状态 | Learn externally<br>外部学习资源 |
|---|---|---|---|---|
| ABAC authorization<br>ABAC 授权 | `EffectiveAuthority` = intersection of **10 boundaries** (User, Tenant, Application, Entitlement, Playbook, Specialist, Tool, DataSource, ApprovalState, Squad); `Delegate()` only narrows<br>`EffectiveAuthority` = **10 个边界**的交集（User、Tenant、Application、Entitlement、Playbook、Specialist、Tool、DataSource、ApprovalState、Squad）；`Delegate()` 只会收窄 | `Domain/Authority/EffectiveAuthority.cs:8-36,114-225`; `Application/Authority/AuthoritySources.cs:49-91` | Implemented<br>已实现 | ABAC/XACML; Cedar; OpenFGA (contrast: ReBAC)<br>ABAC/XACML；Cedar；OpenFGA（对比：ReBAC） |
| Tool registry<br>工具注册表 | Three declaration sources — platform-owned, connector manifests, published assets — merged **published-wins**<br>三个声明来源 —— 平台自有、连接器清单、已发布资产 —— 按**已发布者优先**合并 | `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` | Implemented<br>已实现 | MCP tool discovery; manifest protocols<br>MCP 工具发现；清单协议 |
| Governance sandwich (pre/post-LLM)<br>治理三明治（LLM 调用前/后） | Pre: published+pinned assets, authority, entitlement, least context. Post: schema → re-authorize → approval by risk → backend revalidation<br>调用前：已发布且锁定版本的资产、权限、权益、最小上下文。调用后：schema → 重新授权 → 按风险审批 → 后端重新校验 | `docs/architecture/governance-architecture.md:223-273` | Partial<br>部分实现 | Guardrails frameworks<br>护栏框架 |
| HITL with binding + separation of duties<br>带绑定与职责分离的人在回路 | Proposal persisted before approval; approval bound to tenant/actor/action hash/authority version/expiry (15 min); proposer ≠ approver; 6 transitions; at-most-once; compensation<br>提议在审批前持久化；审批绑定到租户/操作者/动作哈希/权限版本/过期时间（15 分钟）；提议者 ≠ 审批者；6 种状态转换；至多一次；补偿 | `.../Approval/ApprovalCheckpoint.cs:237-468,470-571` | Implemented<br>已实现 | Maker-checker; 2PC; e-signature binding<br>制单-复核（maker-checker）；2PC；电子签名绑定 |
| Idempotent side effects<br>幂等的副作用 | Idempotency key + `ActionIdempotencyStore` + approval-consumed flag; replay rejected with stable codes<br>幂等键 + `ActionIdempotencyStore` + 审批已消费标记；重放会以稳定的错误码被拒绝 | `ApprovalCheckpoint.cs:341-412` | Implemented<br>已实现 | Idempotency keys; exactly-once<br>幂等键；恰好一次 |
| Verification / readback<br>验证 / 回读 | `IResultVerifier` + `ReadbackVerification` (Verified/Contradicted/Unconfirmed/NotPerformed) | `DecisionInteraction.cs:447-536`; `.../Evaluation/**` | Partial (per-connector readback missing)<br>部分实现（缺少按连接器的回读） | Post-condition verification<br>后置条件验证 |
| Semantic layer<br>语义层 | Published `BusinessSemanticDefinition`; user overlays additive only, never override the tenant-authoritative metric<br>已发布的 `BusinessSemanticDefinition`；用户叠加层只能做增补，永远不能覆盖租户权威的指标 | `Application/SemanticResolution/IBusinessSemanticResolver.cs:63-157` | Partial (revenue-first)<br>部分实现（以收入为先） | dbt Semantic Layer; MetricFlow<br>dbt Semantic Layer；MetricFlow |

### 2.4 Data, trace and learning

**2.4 数据、trace 与学习**

| Industry concept<br>业界概念 | How SendOS implements it<br>SendOS 如何实现 | Where<br>位置 | Status<br>状态 | Learn externally<br>外部学习资源 |
|---|---|---|---|---|
| Append-only trace<br>只追加的 trace | 21-event closed lifecycle; insert-only store; DB trigger denies UPDATE/DELETE; identity `Sequence`<br>21 种事件的封闭生命周期；只插入的存储；数据库触发器拒绝 UPDATE/DELETE；自增标识 `Sequence` | `apps/Send.Usage.Collector/src/.../Domain/OutcomeTraceEventType.cs`; `.../Infrastructure/Persistence/EfCoreOutcomeTraceStore.cs:1-80`; `UsageCollectorDbContext.cs` | Implemented<br>已实现 | Event logs vs event sourcing<br>事件日志与事件溯源的区别 |
| Transactional outbox<br>事务性发件箱 | Fire-and-forget `Emit` (never throws) → durable outbox → background worker<br>发出即不管的 `Emit`（从不抛异常）→ 持久化发件箱 → 后台工作者 | `.../Application/Outcome/IOutcomeTraceEmitter.cs:24-45` | Implemented<br>已实现 | Outbox pattern<br>发件箱模式 |
| Evaluation harness<br>评测框架 | 5 dimensions (Correctness, PolicyCompliance, OutcomeAlignment, EvidenceGrounding, ExecutionQuality) + aggregate<br>5 个维度（Correctness、PolicyCompliance、OutcomeAlignment、EvidenceGrounding、ExecutionQuality）+ 汇总 | `apps/Send.LowerLayer.Worker/src/.../Evaluation/{EvaluationDimensions,Evaluator}.cs` | Dark (uncalled)<br>暗置（未被调用） | Ragas/DeepEval; judge calibration<br>Ragas/DeepEval；评审校准 |
| Statistical-evidence gate<br>统计证据关卡 | `EligibleForCandidate ∧ sample ≥ 30 ∧ confidence ≥ 0.7 ∧ quality ≥ 0.5` | `.../Distillation/EvidenceGate.cs:24-35`; `DistillationEngine.cs:52-53` | Dark<br>暗置 | Sequential testing; power analysis<br>序贯检验；统计功效分析 |
| Data flywheel<br>数据飞轮 | Trace → distil (attribution + provenance) → train (diff vs BaseVersion) → submit-only promoter → human approve → write-once publish<br>trace → 蒸馏（归因 + 来源（provenance））→ 训练（相对 BaseVersion 的差异）→ 仅提交式晋升器 → 人工审批 → 一次写入式发布 | `apps/Send.LowerLayer.Worker/src/**`; `.../PublishingPipeline/PublishingService.cs` | Dark / dry<br>暗置 / 干涸 | Data flywheels; DSPy (vs RLHF)<br>数据飞轮；DSPy（对比 RLHF） |
| Versioned asset registry<br>带版本的资产注册表 | `Draft→Review→Approved→Published→Deprecated`; write-once; pins; rollback<br>`Draft→Review→Approved→Published→Deprecated`；一次写入；版本锁定；回滚 | `.../ControlPlane/Lifecycle/GovernedAssetLifecycleService.cs` | Implemented<br>已实现 | Prompt/asset registries<br>提示词/资产注册表 |
| Traceable stages<br>可追踪的阶段 | `TurnStage` enum: 45 named stages, each `Ran/Skipped/Failed` with a reason<br>`TurnStage` 枚举：45 个具名阶段，每个都带有原因地标记为 `Ran/Skipped/Failed` | `.../Application/Runtime/TurnStage.cs:29-203` | Implemented<br>已实现 | Structured logging; OTel GenAI conventions<br>结构化日志；OTel GenAI 约定 |

### 2.5 Platform

**2.5 平台**

| Industry concept<br>业界概念 | How SendOS implements it<br>SendOS 如何实现 | Where<br>位置 | Status<br>状态 | Learn externally<br>外部学习资源 |
|---|---|---|---|---|
| Ports & adapters<br>端口与适配器 | `IConnector` / `IConnectorSyncService` / `ICapabilityManifestProvider`; three paths (ingest, live query, governed action)<br>`IConnector` / `IConnectorSyncService` / `ICapabilityManifestProvider`；三条路径（数据摄取、实时查询、受治理的动作） | `libraries/Send.Connectors.Abstractions/**`; `apps/Send.Integration.Service/src/**` | Implemented<br>已实现 | Hexagonal architecture; iPaaS<br>六边形架构；iPaaS |
| Context read boundary<br>上下文读取边界 | Tenant-scoped, source-agnostic `IContextGateway`; empty result is not an error<br>按租户限定范围、与数据源无关的 `IContextGateway`；空结果不算错误 | `libraries/Send.Context.Gateway/IContextGateway.cs:1-32` | Implemented<br>已实现 | Hybrid retrieval; RAG eval<br>混合检索；RAG 评测 |
| Vector retrieval<br>向量检索 | Additive semantic path, pgvector adapter, deterministic hash embeddings by default<br>增补式的语义路径、pgvector 适配器，默认使用确定性的哈希嵌入 | `libraries/Send.Context.Gateway/Semantic/**` | Partial (model pluggable)<br>部分实现（模型可插拔） | Embeddings; pgvector tuning<br>嵌入；pgvector 调优 |
| Resilience stack<br>弹性技术栈 | Tiered cache, circuit breaker, per-connector rate limiter, single-flight, idempotency<br>分层缓存、熔断器、按连接器的限流器、single-flight（请求合并）、幂等性 | `apps/Send.Intelligence.Gateway/src/**` (`Caching/`, `CircuitBreaker/`, `RateLimiting/`) | Implemented<br>已实现 | Polly; Redis patterns<br>Polly；Redis 模式 |
| Durable long-running work<br>持久化的长时间运行工作 | `CaseRuntime` + `DecisionTask` with CAS reserve→suspend→resume + deadline worker<br>`CaseRuntime` + `DecisionTask`，带 CAS 的 预留→挂起→恢复，外加截止期限工作者 | `.../Domain/CaseRuntime/**`; `.../Infrastructure/CaseRuntime/**` | Dark (not wired)<br>暗置（未接入） | Temporal; DBOS; checkpointers<br>Temporal；DBOS；检查点器 |
| Property-based invariants<br>基于属性的不变量 | ≈486 FsCheck properties (authority narrows, approval ≤ once, budgets hold)<br>约 486 个 FsCheck 属性（权限只收窄、审批 ≤ 一次、预算守住） | `apps/Send.Agent.Runtime/tests/**/Properties/**` | Implemented<br>已实现 | FsCheck/Hypothesis |

---

## 3. Ranked learning topics (20)

**3. 排序后的学习主题（20 个）**

Ordered by SendOS relevance × teaching value × lab feasibility.

按 SendOS 相关性 × 教学价值 × 实验可行性排序。

| # | Topic<br>主题 | Why it matters at SendOS<br>为什么在 SendOS 中重要 | Miniature lab (Python first; .NET noted)<br>微缩实验（Python 优先；注明 .NET 做法） | Effort<br>工作量 |
|---|---|---|---|---|
| 1 | **Typed decision + approval gate**<br>**类型化决策 + 审批关卡** | The product promise: AI recommends, a human approves, the backend executes. Bugs are security bugs<br>产品承诺：AI 建议，人来审批，后端执行。这里的 bug 就是安全 bug | `pydantic` union of 11 response models + `/propose → /approve → /execute` that rejects replays and post-approval edits. .NET: polymorphic records<br>由 11 个响应模型组成的 `pydantic` 联合类型 + 拒绝重放和审批后修改的 `/propose → /approve → /execute`。.NET：多态 record | L |
| 2 | **Capability registry + fail-closed authority**<br>**能力注册表 + 失败即关闭的权限** | `CapabilityCatalogueAssembler` + `EffectiveAuthority` decide whether *anything* runs<br>`CapabilityCatalogueAssembler` + `EffectiveAuthority` 决定了*任何东西*是否能运行 | Merge three sources with published-wins; compute intersection; assert empty source ⇒ zero grants<br>按已发布者优先合并三个来源；计算交集；断言空来源 ⇒ 零授权 | M |
| 3 | **Trace → eval → candidate → human publish**<br>**trace → 评测 → 候选 → 人工发布** | The differentiator and the most obviously unwired part; highest-leverage contribution<br>差异化所在，也是最明显未接通的部分；杠杆最高的贡献点 | Append-only SQLite log (trigger denies UPDATE/DELETE) + rule learned from ≥30 traces + 5-dim evaluator + approval-gated publish<br>只追加的 SQLite 日志（触发器拒绝 UPDATE/DELETE）+ 从 ≥30 条 trace 中学到的规则 + 5 维评测器 + 经审批把关的发布 | L |
| 4 | **Schema-validated structured output**<br>**经 schema 校验的结构化输出** | Every model call is schema-gated; invalid output must never surface<br>每次模型调用都经过 schema 把关；无效输出绝不能暴露出去 | Ask for JSON, validate, return `{valid:false}` never partial; measure failure rate by schema complexity; add one repair-retry<br>要求输出 JSON，校验，返回 `{valid:false}` 而绝不返回部分结果；按 schema 复杂度测量失败率；加一次修复重试 | M |
| 5 | **Topology-driven shape selection**<br>**拓扑驱动的形态选择** | Newest live mechanism (ADR 0001); teaches "right-size the agent" better than tutorials<br>最新上线的机制（ADR 0001）；比教程更好地讲清"给 Agent 合适的规模" | `PlanGraph(nodes, edges)` → classify; unbacked ⇒ hard error not fallback; property-test it<br>`PlanGraph(nodes, edges)` → 分类；无支撑 ⇒ 硬错误而非回退；对它做属性测试 | M |
| 6 | **Intent elevation + ambiguity threshold**<br>**意图提升 + 歧义阈值** | Turns sloppy NL into an actionable goal; decides ask vs act; explainable to stakeholders<br>把随意的自然语言变成可执行的目标；决定是提问还是行动；可以向利益相关方解释 | Extract `{objective, ambiguity, candidate_intentions}`; `clarify = ambiguity >= threshold`; 1 question ≤3 options<br>抽取 `{objective, ambiguity, candidate_intentions}`；`clarify = ambiguity >= threshold`；1 个问题 ≤3 个选项 | S |
| 7 | **Model routing under budget**<br>**预算约束下的模型路由** | `HandleRoutedAsync` encodes cost/latency-aware routing with fail-safe budget checks<br>`HandleRoutedAsync` 实现了感知成本/延迟的路由，并带有失败即安全的预算检查 | Route across 3 fake providers; enforce cost/latency/attempts; fall back on transient only; "no candidate fits" ⇒ refuse<br>在 3 个模拟提供商之间路由；强制约束成本/延迟/尝试次数；只在瞬时错误时回退；"没有候选符合" ⇒ 拒绝 | M |
| 8 | **Least-context envelopes**<br>**最小上下文信封** | `SpecialistContext` is the data-minimisation guarantee; over-sharing is a governance bug<br>`SpecialistContext` 是数据最小化的保证；过度共享是治理 bug | Compare full transcript vs least-context on cost/quality; assert envelope fields<br>在成本/质量上比较完整对话记录与最小上下文；断言信封字段 | S |
| 9 | **Append-only audit + outbox**<br>**只追加的审计 + 发件箱** | `Outcome_Trace` is audit + learning substrate; emission must never fail the request<br>`Outcome_Trace` 既是审计也是学习的基础；发出事件绝不能导致请求失败 | Outbox row written in the request transaction; worker delivers; property: request succeeds while consumer is down<br>发件箱行在请求事务中写入；由工作者投递；属性：消费者宕机时请求仍然成功 | M |
| 10 | **Version pinning, immutable publish**<br>**版本锁定、不可变发布** | Runtime resolves Published, pinned assets; a mid-flight publish must not mutate a run<br>运行时解析的是已发布、已锁定版本的资产；运行过程中的发布不能改变正在进行的运行 | Asset store with write-once versions and pins; a run on v3 stays on v3 after v4 publishes<br>带一次写入版本和版本锁定的资产存储；v4 发布后，基于 v3 的运行仍停留在 v3 | M |
| 11 | **Independent review + verification**<br>**独立评审 + 验证** | Review is orthogonal to shape; verification is separate from success assertion<br>评审与形态正交；验证与成功断言相互分离 | Producer → critic (schema-constrained verdict) → gate + deterministic post-check that can withhold success<br>生产者 → 批评者（受 schema 约束的判定）→ 关卡 + 可以扣下"成功"判定的确定性后置检查 | M |
| 12 | **Idempotency, at-most-once execution**<br>**幂等性、至多一次执行** | Every write path depends on it<br>每条写入路径都依赖它 | Execute with key; replay same key; replay different key; assert one side effect<br>带键执行；用相同的键重放；用不同的键重放；断言只有一次副作用 | S |
| 13 | **Semantic layer before generation**<br>**生成之前先过语义层** | "A user cannot quietly redefine revenue" — the enterprise anti-hallucination move<br>"用户不能悄悄重新定义收入" —— 企业级的防幻觉手段 | Published metric + aliases-only overlays; assert overlay cannot change the formula; unconnected tenant gets honest "no data"<br>已发布指标 + 仅限别名的叠加层；断言叠加层无法改变公式；未接入的租户会得到坦诚的"无数据" | M |
| 14 | **Durable case / suspend-resume**<br>**持久化案例 / 挂起-恢复** | `CaseRuntime` is built and dark — fastest route to a real contribution<br>`CaseRuntime` 已构建但处于暗置状态 —— 是通往真实贡献的最快路线 | Park in SQLite, return 202, resume on callback, CAS against double-resume, expire on deadline<br>停放到 SQLite，返回 202，收到回调时恢复，用 CAS 防止重复恢复，到截止期限即过期 | L |
| 15 | **Property-based agent invariants**<br>**基于属性的 Agent 不变量** | Dominant quality technique (≈486 properties) — how probabilistic systems stay testable<br>最主要的质量手段（约 486 个属性）—— 概率性系统就是这样保持可测试的 | `hypothesis`: authority ⊆ narrowest; approval ≤ once; budgets respected; shape backed or error<br>`hypothesis`：权限 ⊆ 最窄边界；审批 ≤ 一次；预算得到遵守；形态有支撑否则报错 | M |
| 16 | **Evaluation harness with rubric**<br>**带评分标准（rubric）的评测框架** | Missing link between trace and learning<br>trace 与学习之间缺失的一环 | Golden set + 5-dim rubric; forced-JSON judge; measure agreement vs human labels<br>黄金数据集 + 5 维评分标准；强制 JSON 输出的评审；测量与人工标注的一致程度 | M |
| 17 | **Connector abstraction + execution origin**<br>**连接器抽象 + 执行来源** | Three connector paths; every result declares real/simulated origin<br>三条连接器路径；每个结果都声明其来源是真实还是模拟 | Two fake connectors behind one port; stamp origin; fail closed when omitted<br>一个端口背后的两个模拟连接器；标记来源；缺省时失败即关闭 | M |
| 18 | **Cache, breaker, single-flight**<br>**缓存、熔断器、single-flight** | Gateway resolution is cache-first with breaker fallback<br>网关解析以缓存优先，熔断器兜底 | TTL cache + breaker + single-flight; chaos-test origin down: stale within budget or honest failure<br>TTL 缓存 + 熔断器 + single-flight；混沌测试源站宕机：要么在预算内返回陈旧数据，要么坦诚失败 | M |
| 19 | **Multi-agent message protocol**<br>**多 Agent 消息协议** | Squad chatter structured and internal; one decision leaves<br>小队内部的交流是结构化且内部的；只有一个决策对外输出 | Three agents on a bus with typed messages; assert no transcript leaks to API; budget exhaustion ⇒ degraded honest answer<br>三个 Agent 在总线上用类型化消息通信；断言对话记录不会泄漏到 API；预算耗尽 ⇒ 降级但坦诚的回答 | M |
| 20 | **Eval-gated asset promotion**<br>**经评测把关的资产晋升** | Promotion is submit-only; a model can never bypass a human<br>晋升只能提交；模型永远无法绕过人 | Candidate must beat baseline on eval and pass evidence thresholds, then require an approval row before write<br>候选必须在评测上胜过基线并通过证据阈值，然后在写入前还需要一条审批记录 | S |

---

## 4. Where a from-scratch build teaches the most — six mechanisms

**4. 从零构建最能学到东西的地方 —— 六个机制**

### 4.1 Typed decision family + bound approval gate

**4.1 类型化决策族 + 绑定式审批关卡**

**Build:** a closed response union (`ClarificationPrompt | DirectAnswer | DecisionState | AnalysisConclusion | DecisionRecommendation | ActionProposal | ApprovalRequired | ExecutionResult | Limitation`), a proposal **persisted before approval**, an `ApprovalBinding` (tenant, actor, action hash, authority snapshot, expiry), a state machine (`Pending → Approved | Rejected | Modified | Cancelled | Expired | Revoked → Executed`), and an executor refusing modified/replayed/expired/narrowed approvals.

**构建：** 一个封闭的响应联合类型（`ClarificationPrompt | DirectAnswer | DecisionState | AnalysisConclusion | DecisionRecommendation | ActionProposal | ApprovalRequired | ExecutionResult | Limitation`）；一个**在审批之前就持久化**的提议；一个 `ApprovalBinding`（租户、操作者、动作哈希、权限快照、过期时间）；一个状态机（`Pending → Approved | Rejected | Modified | Cancelled | Expired | Revoked → Executed`）；以及一个会拒绝已修改/已重放/已过期/权限已收窄的审批的执行器。

**Invariants:** persisted-before-approve; wrong reference never satisfies; proposer ≠ approver; hash mismatch blocks; authority narrowing between approve and execute blocks; replay returns the original reference; failure compensates.

**不变量：** 审批前已持久化；错误的引用永远无法满足条件；提议者 ≠ 审批者；哈希不匹配会阻止执行；审批与执行之间权限收窄会阻止执行；重放返回原始引用；失败时进行补偿。

**Reference:** `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs`; `.../Application/Approval/ApprovalCheckpoint.cs:237-468`; `.../Properties/ApprovalBindingAtMostOncePropertyTests.cs`.

**参考：** `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs`；`.../Application/Approval/ApprovalCheckpoint.cs:237-468`；`.../Properties/ApprovalBindingAtMostOncePropertyTests.cs`。

**Without it:** a model-settable "approved" flag; duplicate side effects on retry; approvals outliving the authority they were granted under.

**没有它会怎样：** 出现一个模型就能设置的"已审批"标记；重试时产生重复的副作用；审批在授予它的那份权限失效之后依然有效。

### 4.2 Capability catalogue with fail-closed authority intersection

**4.2 带失败即关闭权限交集的能力目录**

**Build:** three declaration sources merged by id with published-wins; registry match filtered by tenant then declared shape (read vs action kind); authority as intersection over independent boundaries with `effective ⊆ narrowest`, and `delegate()` only narrowing.

**构建：** 三个声明来源按 id 合并，已发布者优先；注册表匹配先按租户过滤，再按声明的形态（读取类还是动作类）过滤；权限是多个独立边界的交集，满足 `effective ⊆ narrowest`，并且 `delegate()` 只会收窄。

**Invariants:** empty boundary ⇒ no grants; adding a boundary never widens; matched capability carries a governed-asset reference; undeclared capability is not invokable.

**不变量：** 空边界 ⇒ 无授权；增加一个边界永远不会放宽；匹配到的能力携带一个受治理资产的引用；未声明的能力不可调用。

**Reference:** `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120`; `Domain/Authority/EffectiveAuthority.cs`; `Application/Authority/AuthoritySources.cs`; `.../Properties/AuthorityIntersectionNarrowingPropertyTests.cs`.

**参考：** `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120`；`Domain/Authority/EffectiveAuthority.cs`；`Application/Authority/AuthoritySources.cs`；`.../Properties/AuthorityIntersectionNarrowingPropertyTests.cs`。

**Without it:** a tool described in a prompt but absent from the governed catalogue; providers quietly granting permissions; cross-tenant matches.

**没有它会怎样：** 某个工具在提示词里有描述，却不在受治理的目录中；提供商悄悄授予权限；出现跨租户的匹配。

### 4.3 Append-only trace → eval → evidence-gated candidate → human publish

**4.3 只追加的 trace → 评测 → 经证据把关的候选 → 人工发布**

**Build:** append-only store with store-assigned monotonic sequence and a DB rule denying UPDATE/DELETE; distillation that attributes insights to the asset versions that produced them and **drops unattributable** ones; an evidence gate; a five-dimension evaluator; candidates as **diffs against a base version**; a submit-only promoter creating `Draft` only; a publish step refusing without a human approval row.

**构建：** 一个只追加的存储，由存储分配单调递增的序号，并有一条拒绝 UPDATE/DELETE 的数据库规则；一个蒸馏过程，把洞察归因到产生它们的资产版本，并**丢弃无法归因**的洞察；一个证据关卡；一个五维评测器；以**相对于基础版本的差异**形式表示的候选；一个只能提交、只会创建 `Draft` 的晋升器；以及一个没有人工审批记录就拒绝执行的发布步骤。

**Invariants:** no update/delete; replay in append order; weak evidence never becomes a candidate; AI never reaches `Published` without approval; next request resolves the new pinned version.

**不变量：** 不允许更新/删除；按追加顺序重放；证据不足的永远不会成为候选；未经审批 AI 永远无法到达 `Published`；下一次请求会解析到新锁定的版本。

**Reference:** `apps/Send.Usage.Collector/src/**`; `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs`; `.../Evaluation/Evaluator.cs`; `.../ControlPlane/PublishingPipeline/PublishingService.cs`; `docs/architecture/governance-architecture.md:§6b`.

**参考：** `apps/Send.Usage.Collector/src/**`；`apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs`；`.../Evaluation/Evaluator.cs`；`.../ControlPlane/PublishingPipeline/PublishingService.cs`；`docs/architecture/governance-architecture.md:§6b`。

**Without it:** a "self-improving" loop that silently ships model-authored policy; traces that cannot be replayed.

**没有它会怎样：** 一个"自我改进"的闭环悄无声息地上线由模型撰写的策略；trace 无法重放。

### 4.4 Schema-gated structured output + budgeted routing

**4.4 schema 把关的结构化输出 + 受预算约束的路由**

**Build:** provider abstraction returning text, finish reason, usage; schema validator over a documented subset; handler returning `valid=False, output=None` on mismatch; router filtering candidates by task type/reliability/token/cost/latency, ordering by policy (including an explicit declared-order mode), retrying transient failures only, reporting per-call cost.

**构建：** 一个提供商抽象，返回文本、结束原因和用量；一个针对有文档说明的子集的 schema 校验器；一个在不匹配时返回 `valid=False, output=None` 的处理器；一个路由器，按任务类型/可靠性/token/成本/延迟过滤候选，按策略排序（包括一种显式的声明顺序模式），只对瞬时故障重试，并报告每次调用的成本。

**Invariants:** invalid never surfaces as valid; unverifiable budget ⇒ candidate excluded (fail-safe); cancellation never retries; time budget aborts in-flight calls; cost = profile × tokens.

**不变量：** 无效结果永远不会以有效结果的面目出现；预算无法核实 ⇒ 排除该候选（失败即安全）；取消永不重试；时间预算会中止进行中的调用；成本 = 价格档位 × token 数。

**Reference:** `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`; `.../Handlers/CompletionHandler.cs:60-210`.

**参考：** `apps/Send.Model.Adapter/src/Send.Model.Adapter.Application/Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs`；`.../Handlers/CompletionHandler.cs:60-210`。

**Without it:** JSON parse exceptions in production; silent budget overruns; a "cheapest" router ignoring a caller's deliberate model order (recorded as a real bug at `CompletionHandler.cs:78-85`).

**没有它会怎样：** 生产环境出现 JSON 解析异常；预算悄无声息地超支；一个"选最便宜"的路由器无视调用方刻意指定的模型顺序（这在 `CompletionHandler.cs:78-85` 被记录为一个真实 bug）。

### 4.5 Topology-driven shape selection

**4.5 拓扑驱动的形态选择**

**Build:** plan graph (workstreams, dependencies, bound capability or reasoning node), validator (acyclic, closed kinds, testable acceptance criteria), capability binder with per-workstream authorization, and a **pure classifier**: ≥2 components → multi-squad; 1 capability node → direct capability; 1 reasoning node → direct specialist; ≥2 connected → single squad. Unbacked derived shape → limitation, never a smaller guessed shape.

**构建：** 计划图（工作流、依赖、绑定的能力节点或推理节点）、校验器（无环、封闭的类别、可测试的验收标准）、按工作流逐一授权的能力绑定器，以及一个**纯分类器**：≥2 个连通分量 → 多小队；1 个能力节点 → 直接能力；1 个推理节点 → 直接专员 Agent；≥2 个相连节点 → 单小队。推导出的形态若无支撑 → 返回限制说明（limitation），绝不退而求其次去猜一个更小的形态。

**Invariants:** exactly one shape; smallest sufficient; classification independent of any importance score; unbacked ⇒ limitation; zero bound nodes is an error.

**不变量：** 恰好一种形态；最小且足够；分类不依赖任何重要性评分；无支撑 ⇒ 限制说明；绑定节点为零是一个错误。

**Reference:** `.../Planning/TopologyClassifier.cs:28-102`; `ExecutionPlanner.cs:143-230`; `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md`; `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs`.

**参考：** `.../Planning/TopologyClassifier.cs:28-102`；`ExecutionPlanner.cs:143-230`；`docs/adrs/0001-flag-gated-logical-planner-shape-selection.md`；`.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs`。

**Without it:** fan-out driven by ambiguity (the exact failure ADR 0001 removes); agent swarms for questions one tool call answers.

**没有它会怎样：** 由歧义驱动的扇出（恰恰是 ADR 0001 所消除的那种失败）；一次工具调用就能回答的问题却动用了一大群 Agent。

### 4.6 Append-only trace as the runtime↔learning contract

**4.6 作为运行时↔学习之间契约的只追加 trace**

**Build:** closed event enum (~21), typed lifecycle-event family projecting to one flat row with `PayloadJson`, correlation keys (`interactionId`, `businessStateId`, `executionId`, `traceReference`), stage telemetry.

**构建：** 封闭的事件枚举（约 21 个）、投影为一条带 `PayloadJson` 的扁平行的类型化生命周期事件族、关联键（`interactionId`、`businessStateId`、`executionId`、`traceReference`）、阶段遥测。

**Invariants:** enum closed and exhaustive; lossless projection; correlation keys always present; replay deterministic.

**不变量：** 枚举封闭且穷尽；投影无损；关联键始终存在；重放是确定性的。

**Reference:** `apps/Send.Usage.Collector/src/.../Domain/{OutcomeTraceEvent,OutcomeTraceEventType,OutcomeTraceLifecycleEvent}.cs`; `.../Application/Outcome/IOutcomeTraceEmitter.cs`; `.../Runtime/TurnStage.cs`.

**参考：** `apps/Send.Usage.Collector/src/.../Domain/{OutcomeTraceEvent,OutcomeTraceEventType,OutcomeTraceLifecycleEvent}.cs`；`.../Application/Outcome/IOutcomeTraceEmitter.cs`；`.../Runtime/TurnStage.cs`。

**Runner-up (worth a chapter, not a build):** the pre/post-LLM "governance sandwich" (`docs/architecture/governance-architecture.md:223-273`) — mostly the composition of 4.1, 4.2 and 4.4, and the clearest one-diagram explanation of the architecture.

**次选（值得写一章，但不值得构建）：** LLM 调用前/后的"治理三明治"（`docs/architecture/governance-architecture.md:223-273`）—— 它基本上是 4.1、4.2 和 4.4 的组合，也是用一张图解释这套架构最清晰的方式。

### 4.7 Mapping onto the learning repo's `agentlab/` package

**4.7 映射到学习仓库的 `agentlab/` 包**

The course package already exists and is well aimed: `agentlab/orchestrator/__init__.py` states the theme as *"smallest sufficient shape"* — the exact rule `TopologyClassifier` implements. Suggested homes:

课程包已经存在，而且目标很准：`agentlab/orchestrator/__init__.py` 把主题表述为“*最小且足够的形态*” —— 这正是 `TopologyClassifier` 所实现的规则。建议的落脚点如下：

| SendOS mechanism<br>SendOS 机制 | `agentlab/` target<br>`agentlab/` 中的目标位置 |
|---|---|
| 4.1 typed decision + approval gate<br>4.1 类型化决策 + 审批关卡 | `agentlab/types.py` (discriminated outputs) + `orchestrator/approval.py` (planned: suspend/resume)<br>`agentlab/types.py`（可辨识的输出类型）+ `orchestrator/approval.py`（计划中：挂起/恢复） |
| 4.2 capability catalogue + authority<br>4.2 能力目录 + 权限 | `tools/registry.py` (one object owns schema + handler) + a small new `authority.py`<br>`tools/registry.py`（由一个对象同时持有 schema + 处理器）+ 一个新的小型 `authority.py` |
| 4.3 trace → eval → publish<br>4.3 trace → 评测 → 发布 | `trace.py` (append-only, monotonic, already the right shape) + `evals/harness.py` + a new `evals/promote.py`<br>`trace.py`（只追加、单调递增，形态已经正确）+ `evals/harness.py` + 一个新的 `evals/promote.py` |
| 4.4 structured output + budget routing<br>4.4 结构化输出 + 预算路由 | `providers/*` + `budget.py`/`pricing.py`; add the schema-reject-and-retry layer<br>`providers/*` + `budget.py`/`pricing.py`；加上 schema 拒绝并重试这一层 |
| 4.5 topology-driven shape selection<br>4.5 拓扑驱动的形态选择 | `orchestrator/plan.py` + `orchestrator/orchestrator.py` |
| 4.6 trace contract<br>4.6 trace 契约 | `trace.py` event kinds (`approval_requested/granted/denied`, `tool_call`, `eval_case`) map 1:1 onto SendOS lifecycle events<br>`trace.py` 的事件类型（`approval_requested/granted/denied`、`tool_call`、`eval_case`）与 SendOS 生命周期事件一一对应 |

---

## 5. Where SendOS departs from mainstream practice

**5. SendOS 偏离主流做法的地方**

| Area<br>领域 | SendOS choice<br>SendOS 的选择 | Mainstream alternative<br>主流替代方案 | Transferable skill<br>可迁移的技能 |
|---|---|---|---|
| Orchestration runtime<br>编排运行时 | One procedural class (`DecisionRuntime.cs`, 5,379 lines) with typed seams; no graph interpreter<br>一个带类型化接缝的过程式类（`DecisionRuntime.cs`，5,379 行）；没有图解释器 | LangGraph/AutoGen/CrewAI; Temporal; DBOS<br>LangGraph/AutoGen/CrewAI；Temporal；DBOS | When a state machine beats a framework, and how property tests compensate for a large procedural core<br>状态机何时胜过框架，以及属性测试如何弥补庞大的过程式核心 |
| Structured output<br>结构化输出 | Hand-rolled JSON Schema subset; generate → parse → reject; no constrained decoding<br>手写的 JSON Schema 子集；生成 → 解析 → 拒绝；没有约束解码 | Provider structured outputs; GBNF/Outlines; PydanticAI typed tools<br>提供商原生的结构化输出；GBNF/Outlines；PydanticAI 类型化工具 | Validated-after vs impossible-to-emit<br>事后校验与根本无法输出的区别 |
| Learning<br>学习 | Asset/policy refinement + human publish gate; **no weight training, no RLHF**<br>资产/策略精炼 + 人工发布关卡；**没有权重训练，没有 RLHF** | DPO/RLHF/SFT; DSPy prompt optimisation<br>DPO/RLHF/SFT；DSPy 提示词优化 | Cheapest intervention that changes behaviour<br>能改变行为的最廉价干预 |
| Authorization<br>授权 | In-house ABAC intersection; authority **discovery** (OrgIntel graph) separate from **permission**<br>自研的 ABAC 交集；权限**发现**（OrgIntel 图）与**许可**相分离 | Cedar/OPA; OpenFGA/Zanzibar<br>Cedar/OPA；OpenFGA/Zanzibar | "Who should decide" vs "who may act"; deny-by-default arithmetic<br>"谁应该决定"与"谁可以行动"的区别；默认拒绝的运算 |
| Policy assets<br>策略资产 | Versioned JSON assets validated by app code<br>由应用代码校验的带版本 JSON 资产 | OPA/Rego; Cedar; Starlark<br>OPA/Rego；Cedar；Starlark | Versioned config vs executable policy<br>带版本的配置与可执行策略的区别 |
| Event log<br>事件日志 | Append-only audit/learning stream — **not** event sourcing<br>只追加的审计/学习流 —— **不是**事件溯源 | Event sourcing + CQRS projections<br>事件溯源 + CQRS 投影 | Know which one you are building<br>清楚自己在构建的是哪一种 |
| Durable execution<br>持久化执行 | `CaseRuntime` built, unwired; Business_State is the de-facto durability spine<br>`CaseRuntime` 已构建但未接入；Business_State 实际上是持久化的主干 | Temporal/DBOS; checkpointers<br>Temporal/DBOS；检查点器 | Suspend/resume, CAS on resume, deadline sweeps<br>挂起/恢复、恢复时的 CAS、截止期限扫描 |
| Multi-tenancy<br>多租户 | Tenant scope threaded through every call and query<br>租户范围贯穿每一次调用和查询 | Postgres RLS; schema-per-tenant<br>Postgres RLS；每租户一个 schema | Defence in depth for isolation<br>隔离的纵深防御 |
| Tool discovery<br>工具发现 | Connector manifest endpoint assembled into a registry<br>连接器清单端点汇编成一个注册表 | MCP servers/clients<br>MCP 服务器/客户端 | Manifest catalogues vs runtime introspection<br>清单目录与运行时自省的区别 |
| Agent tracing<br>Agent 追踪 | Custom `TurnStage` enum + JSON payloads; metrics/traces stubs<br>自定义的 `TurnStage` 枚举 + JSON 载荷；指标/trace 只是桩代码 | OpenTelemetry GenAI conventions<br>OpenTelemetry GenAI 约定 | What to record so a failed turn is diagnosable<br>该记录什么，才能让失败的一轮可以被诊断 |
| Self-improvement<br>自我改进 | Human-gated promotion; a model can only `Draft`<br>经人工把关的晋升；模型只能创建 `Draft` | Auto-publish loops; online RL<br>自动发布闭环；在线强化学习 | Governance as a product feature<br>把治理当作产品特性 |

Net: SendOS is **ahead of mainstream tutorials** on governance (approval binding, authority intersection, append-only trace, publish gates) and **behind** on orchestration ergonomics (no graph runtime, durable engine unwired, thin observability). Reproduce the first; learn the second from frameworks.

总结：SendOS 在治理方面（审批绑定、权限交集、只追加的 trace、发布关卡）**领先于主流教程**，在编排的易用性方面（没有图运行时、持久化引擎未接入、可观测性薄弱）则**落后**。前者要亲手复现；后者向各种框架学习。

---

## 6. Reading order — shortest path to a productive contribution

**6. 阅读顺序 —— 通往有效贡献的最短路径**

| Step<br>步骤 | Read<br>阅读 | Time<br>时间 | Why<br>原因 |
|---|---|---|---|
| 1 | `docs/business/01-what-is-sendos.md` | 5 min | Product story<br>产品故事 |
| 2 | `README.md` → "Implementation Status", "Decision-First Runtime"<br>`README.md` → "Implementation Status"（实现状态）、"Decision-First Runtime"（决策优先运行时）两节 | 25 min | What is claimed built (note stale flag language)<br>哪些声称已构建（留意过时的开关表述） |
| 3 | `docs/architecture/system-architecture.md` §1, §4 | 20 min | 10 principles; immediate vs durable path<br>10 条原则；即时路径与持久化路径 |
| 4 | `docs/runtime-orchestration-flow.md` §1-4 (distrust §9: shape selection is now topology)<br>`docs/runtime-orchestration-flow.md` §1-4（别轻信 §9：形态选择现在已改为拓扑） | 30 min | The cast: Meta-Orchestrator, Planner, Squad leader, Specialist<br>角色阵容：Meta-Orchestrator、Planner、小队负责人、专员 Agent |
| 5 | `docs/adrs/0001-...md` | 10 min | Why topology replaced materiality — a model ADR<br>为什么拓扑取代了重要性 —— 一份堪称范本的 ADR |
| 6 | Code: `DecisionInteraction.cs` → `IntentElevator.cs` → `ExecutionPlanner.Plan` → `TopologyClassifier.cs` → `ApprovalCheckpoint.cs`<br>代码：`DecisionInteraction.cs` → `IntentElevator.cs` → `ExecutionPlanner.Plan` → `TopologyClassifier.cs` → `ApprovalCheckpoint.cs` | 2–3 h | The four mechanisms you will actually touch<br>你真正会接触到的四个机制 |
| 7 | `docs/architecture/governance-architecture.md` §2b, §5, §6b | 40 min | Two lifecycle state machines and the publish gate<br>两个生命周期状态机以及发布关卡 |
| 8 | `docs/architecture/lower-layer-learning-loop.md` §1b, §3, §4 | 40 min | Trace → insight → candidate → publish, and what is missing<br>trace → 洞察 → 候选 → 发布，以及缺了什么 |
| 9 | `docs/architecture/reconciliation-audit.md` §F | 30 min | Honest map of what is dark; read last so you can check it<br>一份坦诚标明哪些处于暗置状态的地图；最后再读，这样你才能检验它 |
| 10 | `docs/tech-week/runbook.md`, `demo-workflows-v2.md`, `tools/techweek/acceptance/demo7_acceptance.py` | 45 min | Closest thing to a live acceptance spec — and Python, a model for our labs<br>最接近实际验收规范的东西 —— 而且是 Python 写的，可作为我们实验的范本 |

**Skip until needed:** `docs/architecture/authority-graph-architecture.md`, `performance-architecture.md`, `connector-architecture.md`, `docs/licensing/**`, `infra/**`.

**需要时再读：** `docs/architecture/authority-graph-architecture.md`、`performance-architecture.md`、`connector-architecture.md`、`docs/licensing/**`、`infra/**`。

**First-contribution candidates (audit §F, confirmed against code):** structured action arguments never reaching the connector (#24), per-connector write readback verification (#39), wiring `DistillationWorkProcessor → DistillationEngine` (#45), registering the `DecisionTask` deadline worker (#35), and docs-drift fixes (cheapest, most visible).

**首次贡献候选任务（审计 §F，已对照代码确认）：** 结构化的动作参数始终没有到达连接器（#24）、按连接器实现的写入回读验证（#39）、接通 `DistillationWorkProcessor → DistillationEngine`（#45）、注册 `DecisionTask` 截止期限工作者（#35），以及修复文档偏差（成本最低、最显眼）。

---

## 7. What I could not assess

**7. 我无法评估的内容**

- **Anything runtime.** I did not build, test, or execute the stack (forbidden). No verification of DI wiring, no measured Postgres/Redis/Apache AGE/pgvector behaviour, no confirmation the 6,300+ tests pass, no live provider calls, no licensing-service runtime behaviour, no front-end/pack behaviour.

  **任何运行时相关的内容。** 我没有构建、测试或执行这套技术栈（这是被禁止的）。没有核实依赖注入的接线，没有实测 Postgres/Redis/Apache AGE/pgvector 的行为，没有确认那 6,300 多个测试能通过，没有真实调用提供商，没有观察许可证服务的运行时行为，也没有观察前端/打包的行为。

- **The target-design set.** `README.md` and `docs/README.md` point at `send-documentation/sendos-technical`; **that directory does not exist in this repo**, so target claims (Squads, Intelligence Candidates) could only be read through their implementation and repo docs.

  **目标设计文档集。** `README.md` 和 `docs/README.md` 都指向 `send-documentation/sendos-technical`；**这个目录在本仓库中并不存在**，所以目标层面的说法（Squads、Intelligence Candidates）只能通过它们的实现和仓库内文档来解读。

- **Depth-limited areas:** `Send.License.Service` (336 files), `Send.Integration.Service` (835 files), `Send.Intel.Server` control-plane detail beyond publish/lifecycle, `Send.Intel.Admin`, `Send.Intelligence.Gateway`, `sdk/`, `infra/`, `tools/techweek`, and the 150 KB `docs/platform-completion-ledger.md`.

  **深度有限的部分：** `Send.License.Service`（336 个文件）、`Send.Integration.Service`（835 个文件）、`Send.Intel.Server` 中发布/生命周期之外的控制平面细节、`Send.Intel.Admin`、`Send.Intelligence.Gateway`、`sdk/`、`infra/`、`tools/techweek`，以及 150 KB 的 `docs/platform-completion-ledger.md`。

- **Which contradictory doc is intended.** Three vintages disagree (§0). I used the rule stated at `docs/README.md:12` — code is authoritative — but could not tell which docs are actively maintained.

  **相互矛盾的文档中哪一份才是本意。** 三个年代的文档说法不一（§0）。我采用了 `docs/README.md:12` 中声明的规则 —— 以代码为权威 —— 但无法判断哪些文档仍在积极维护。

- **The legacy path.** `POST /api/agent/execute` (`Controllers/AgentController.cs`) is the legacy 9-stage pipeline; the audit calls it an ungoverned second runtime. I did not trace it end-to-end.

  **遗留路径。** `POST /api/agent/execute`（`Controllers/AgentController.cs`）是遗留的 9 阶段流水线；审计称它为一个不受治理的第二运行时。我没有端到端地追踪它。

---

*Every mechanism in §4 is small enough to rebuild in a weekend, and faithful enough that reading the SendOS original afterwards will feel like reading your own notes.*

*§4 中的每个机制都小到可以在一个周末内重建，又忠实到让你事后再读 SendOS 原版时，感觉就像在读自己的笔记。*
