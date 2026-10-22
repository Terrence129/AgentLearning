# Reading order — the shortest path to a productive contribution

**阅读顺序 —— 通往有效贡献的最短路径**

**Living document.** Ten steps, in order, with a time budget and what to look for. Total: **~1
working day** of reading, spread over the first two weeks. After step 10 you can find your way
around the platform, verify a claim against code, and pick up a real task.

**活文档。** 十个步骤，按顺序进行，每步都有时间预算和关注要点。总计约 **1 个工作日**的阅读量，分摊在最初两周内完成。完成第 10 步后，你就能在平台中找到方向、对照代码核实某个说法，并接手一个真实任务。

> **Code wins over docs.** Paths are relative to the SendOS repo root (`SendOs/`). Where a doc
> contradicts code, this page follows code and flags the drift. Evidence base:
> [`CONCEPT-MAP.md`](./CONCEPT-MAP.md). Week-by-week depth: [`BRIDGE.md`](./BRIDGE.md).
>
> **代码优先于文档。** 路径均相对于 SendOS 仓库根目录（`SendOs/`）。当文档与代码矛盾时，本页以代码为准并标注偏差。证据库：[`CONCEPT-MAP.md`](./CONCEPT-MAP.md)。逐周深入：[`BRIDGE.md`](./BRIDGE.md)。

---

## The ten steps

**十个步骤**

| # | Read<br>阅读 | Time<br>时间 | Look for<br>关注要点 | Output<br>产出 |
|---|---|---|---|---|
| 1 | `docs/business/01-what-is-sendos.md` | 5 min | The product story: a shared intelligence layer under five business products. Why the platform, not an app<br>产品故事：位于五个业务产品之下的共享智能层。为什么是平台，而不是一个应用 | One sentence: what SendOS sells<br>一句话：SendOS 卖的是什么 |
| 2 | `README.md` → "Implementation Status" + "Decision-First Runtime" sections<br>`README.md` → "Implementation Status" 和 "Decision-First Runtime" 两节 | 25 min | What is claimed built vs pending; the status vocabulary (Implemented / Partial / Scaffolded / Placeholder / Planned)<br>哪些声称已构建、哪些尚待完成；状态词汇（Implemented / Partial / Scaffolded / Placeholder / Planned） | A list of claims you will later verify in code<br>一份你之后要在代码中核实的说法清单 |
| 3 | `docs/architecture/system-architecture.md` §1 (10 principles), §4 (two request paths)<br>`docs/architecture/system-architecture.md` §1（10 条原则）、§4（两条请求路径） | 20 min | The non-negotiables: case-first, playbooks accelerate never required, discovery ≠ permission, source systems stay authoritative<br>不可妥协的原则：案例优先（case-first）；playbook 只用于加速，从不是必需的；发现 ≠ 许可；源系统始终是权威数据源 | The 10 principles, paraphrased<br>用自己的话复述这 10 条原则 |
| 4 | `docs/runtime-orchestration-flow.md` §1–4 **only** (read §9 but distrust it — shape selection is now topology; see Appendix B of the bridge)<br>`docs/runtime-orchestration-flow.md` **只读** §1–4（§9 可以读但别轻信 —— 形态选择现在已改为拓扑；见桥接文档的附录 B） | 30 min | The cast: Meta-Orchestrator, Planner, Squad leader, Specialist; definition vs instance; what crosses back to the client<br>角色阵容：Meta-Orchestrator、Planner、小队（squad）负责人、专员 Agent（specialist）；定义与实例的区别；哪些内容会回传给客户端 | A diagram you draw yourself<br>一张你自己画的图 |
| 5 | `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md` | 10 min | Why materiality stopped selecting shapes; how a decision of this size is recorded. This is the template for your own design write-ups<br>为什么重要性（materiality）不再用于选择形态；这种规模的决策是如何记录的。这就是你自己写设计总结文章的模板 | Three sentences on the trade<br>用三句话说明其中的取舍 |
| 6 | **Code**, in this order: `Domain/Decision/DecisionInteraction.cs` → `Application/IntentElevation/IntentElevator.cs` → `Application/Planning/ExecutionPlanner.cs` (`Plan`) → `Planning/TopologyClassifier.cs` → `Application/Approval/ApprovalCheckpoint.cs`<br>**代码**，按以下顺序：`Domain/Decision/DecisionInteraction.cs` → `Application/IntentElevation/IntentElevator.cs` → `Application/Planning/ExecutionPlanner.cs`（`Plan`）→ `Planning/TopologyClassifier.cs` → `Application/Approval/ApprovalCheckpoint.cs` | 2–3 h | The four mechanisms you will actually touch: typed decisions, deterministic policy over model output, topology selection, bound approval<br>你真正会接触到的四个机制：类型化决策、作用于模型输出之上的确定性策略、拓扑选择、绑定式审批 | Your own mini-diagrams, annotated with `path:line`<br>你自己画的小图，用 `path:line` 做标注 |
| 7 | `docs/architecture/governance-architecture.md` §2b, §5, §6b | 40 min | The two lifecycle state machines, the pre/post-LLM "sandwich", and the publish gate that a model cannot bypass<br>两个生命周期状态机、LLM 调用前后的"三明治"结构，以及模型无法绕过的发布关卡 | The governance sandwich, from memory<br>凭记忆写出治理三明治 |
| 8 | `docs/architecture/lower-layer-learning-loop.md` §1b, §3, §4 | 40 min | Trace → insight → candidate → human-gated publish; the two learning outputs and their different admission rules<br>trace → 洞察 → 候选 → 经人工把关的发布；两种学习产出及其不同的准入规则 | Where the loop stops and why<br>闭环在哪里中断，以及原因 |
| 9 | `docs/architecture/reconciliation-audit.md` §F (status matrix)<br>`docs/architecture/reconciliation-audit.md` §F（状态矩阵） | 30 min | The honest map of what is dark/unwired, with exact remaining work per subsystem. Read it **last** so you can check it<br>一份坦诚的地图，标明哪些是暗置/未接入的，并列出每个子系统确切的剩余工作。**最后**再读它，这样你才能检验它 | Three rows you disagree with, or confirm<br>三行你不同意的内容，或者确认它们 |
| 10 | `docs/tech-week/runbook.md`, `docs/tech-week/demo-workflows-v2.md`, `tools/techweek/acceptance/demo7_acceptance.py` | 45 min | The closest thing to a live acceptance spec — and a Python harness that black-box tests seven end-to-end scenarios against the real runtime<br>最接近实际验收规范的东西 —— 外加一个 Python harness（运行框架），针对真实运行时对七个端到端场景做黑盒测试 | How *you* would write the acceptance test<br>*你*会如何编写这个验收测试 |

**Skip until needed:** `docs/architecture/authority-graph-architecture.md` (1,200+ lines on OrgIntel),
`performance-architecture.md`, `connector-architecture.md`, `docs/licensing/**`, `infra/**`,
`docs/platform-completion-ledger.md` (150 KB tracker).

**需要时再读：** `docs/architecture/authority-graph-architecture.md`（关于 OrgIntel 的 1,200 多行）、`performance-architecture.md`、`connector-architecture.md`、`docs/licensing/**`、`infra/**`、`docs/platform-completion-ledger.md`（150 KB 的进度追踪表）。

**Do not read end-to-end:** `Application/Runtime/DecisionRuntime.cs` (5,379 lines) and
`MetaOrchestrator.cs` (2,685). Read their *method signatures* and the sections listed in the bridge;
read bodies only when chasing a specific behaviour.

**不要从头读到尾：** `Application/Runtime/DecisionRuntime.cs`（5,379 行）和 `MetaOrchestrator.cs`（2,685 行）。读它们的*方法签名*以及桥接文档中列出的章节；只有在追查某个具体行为时才去读方法体。

---

## How to read a SendOS file (the 10-minute method)

**如何阅读一个 SendOS 文件（10 分钟方法）**

1. **Header first.** These files carry unusually good doc comments stating *why* the type exists,
   what it prevents, and which requirement it satisfies. The comments are the design document.

   **先看文件头。** 这些文件带有质量格外高的文档注释，说明了该类型*为什么*存在、它防止了什么、满足了哪条需求。这些注释就是设计文档。

2. **The type declaration.** Fields/parameters are the contract; note which are capability/risk/
   authority metadata and which are payload.

   **类型声明。** 字段/参数就是契约；留意哪些是能力/风险/权限元数据，哪些是有效载荷。

3. **Validation and refusal branches.** Search for `throw`, `return false`, `Limitation`,
   `NoCapabilityResolved`, `Denied`. The refusals are the product.

   **校验与拒绝分支。** 搜索 `throw`、`return false`、`Limitation`、`NoCapabilityResolved`、`Denied`。拒绝本身就是产品。

4. **The tests.** `apps/Send.Agent.Runtime/tests/**/Properties/*.cs` encode invariants as property
   tests. A property test is a spec you can run.

   **测试。** `apps/Send.Agent.Runtime/tests/**/Properties/*.cs` 把不变量编码为属性测试。属性测试就是一份可以运行的规范。

5. **Then the body** — only for the one behaviour you are changing.

   **然后才是方法体** —— 只针对你正在修改的那一个行为。

---

## Three first-contribution candidates

**三个首次贡献候选任务**

Ranked by *time-to-merge* (all are small, well-scoped, and grounded in the repo's own audit). Pick
one after step 9.

按*合并所需时间*排序（三者都规模小、范围清晰，并且都以仓库自身的审计为依据）。完成第 9 步后挑一个。

### Candidate 1 — Fix documentation drift (best first PR)

**候选 1 —— 修复文档偏差（最佳的第一个 PR）**

**Why:** five verified doc-vs-code contradictions are listed in [`CONCEPT-MAP.md`](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins).
Stale docs actively mislead every new engineer, and the repo's own culture already treats claims as
defects (its audit cites `file:line`).

**为什么：** [`CONCEPT-MAP.md`](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins) 中列出了五处已核实的文档与代码矛盾。过时的文档会实实在在地误导每一位新工程师，而且这个仓库自身的文化已经把不实说法当作缺陷来对待（它的审计引用的是 `file:line`）。

**First files:** `README.md` §"Implementation Status"; `docs/README.md`;
`docs/business/09-status-and-roadmap.md`; `docs/runtime-orchestration-flow.md`;
`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417`;
`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Planning/ExecutionPlanningOptions.cs:75`.

**首先查看的文件：** `README.md` §"Implementation Status"；`docs/README.md`；`docs/business/09-status-and-roadmap.md`；`docs/runtime-orchestration-flow.md`；`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Api/Program.cs:417`；`apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Planning/ExecutionPlanningOptions.cs:75`。

**Done when:** each corrected claim cites the file/line that proves it; the flag language matches
`Program.cs:417`; the shape-selection section matches `ExecutionPlanner.cs:143-219`; a maintainer
can re-verify the page in under five minutes.

**完成标准：** 每个修正后的说法都引用了能证明它的文件/行号；关于开关的表述与 `Program.cs:417` 一致；形态选择一节与 `ExecutionPlanner.cs:143-219` 一致；维护者能在五分钟内重新核实这个页面。

**Ask first:** which docs are still maintained — `README.md`/`docs/` vs the external
`send-documentation/sendos-technical` set (the latter is not in this repo).

**先问清楚：** 哪些文档仍在维护 —— 是 `README.md`/`docs/`，还是外部的 `send-documentation/sendos-technical` 文档集（后者不在这个仓库里）。

### Candidate 2 — Per-connector write readback verification (audit #39)

**候选 2 —— 按连接器实现的写入回读验证（审计 #39）**

**Why:** the runtime records a write as successful on a transport acknowledgement plus an external
id, so an acknowledged-but-ineffective write looks identical to a real one. `ExecutionResult`
already carries `ReadbackVerification` (`Verified | Contradicted | Unconfirmed | NotPerformed`) and
`CapabilityDefinition` already has `VerificationStrategy` — the enum and the seam exist; the
per-connector strategies do not.

**为什么：** 运行时只要收到传输层确认外加一个外部 id，就把一次写入记录为成功，因此一次被确认但实际未生效的写入，看上去和真正的写入一模一样。`ExecutionResult` 已经携带 `ReadbackVerification`（`Verified | Contradicted | Unconfirmed | NotPerformed`），`CapabilityDefinition` 也已经有 `VerificationStrategy` —— 枚举和接缝（seam）都已存在；缺的是按连接器实现的具体策略。

**First files:** `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs`
(`ReadbackVerification`, lines ~447–536); `.../Domain/Capabilities/CapabilityDefinition.cs`
(`VerificationStrategy`); `libraries/Send.Connectors.Abstractions/IReadbackActionConnector.cs`;
one connector in `apps/Send.Integration.Service/src/.../Connectors/Write/` (e.g. Jira);
`.../Application/Evaluation/**` (the result verifier that consumes the verdict).

**首先查看的文件：** `apps/Send.Agent.Runtime/src/.../Domain/Decision/DecisionInteraction.cs`（`ReadbackVerification`，约第 447–536 行）；`.../Domain/Capabilities/CapabilityDefinition.cs`（`VerificationStrategy`）；`libraries/Send.Connectors.Abstractions/IReadbackActionConnector.cs`；`apps/Send.Integration.Service/src/.../Connectors/Write/` 中的某一个连接器（例如 Jira）；`.../Application/Evaluation/**`（消费该判定结果的结果验证器）。

**Done when:** an acknowledged write whose effect is absent from the source of record is returned
as `Contradicted` and success is withheld (fails closed); a connector that cannot observe its writes
still returns `NotPerformed`; a unit test covers all four verdicts without network.

**完成标准：** 一次已被确认、但其效果在记录源中并不存在的写入，会返回 `Contradicted` 并且不判定为成功（失败即关闭）；无法观测自身写入结果的连接器仍返回 `NotPerformed`；有一个不依赖网络的单元测试覆盖全部四种判定结果。

**Ask first:** which connector is safe to exercise in dev, and whether readback is expected to cost
an extra source call per write (it is — that is the trade).

**先问清楚：** 哪个连接器可以在开发环境中安全地实际调用，以及回读是否预期会让每次写入多付出一次对源系统的调用（会的 —— 这就是其中的取舍）。

### Candidate 3 — Structured action arguments never reach the connector (audit #24)

**候选 3 —— 结构化的动作参数始终没有到达连接器（审计 #24）**

**Why:** understanding extracts `Action`, `Entities` and `Parameters`, capability *selection* uses
them, but the executable action is built with empty `NormalizedArguments` — so even the one reachable
write (`jira.issue.transition`, which needs a `transitionId`) sends nothing. It is a small,
well-bounded data-flow fix with an obvious test: the bound arguments arrive at the connector.

**为什么：** 理解阶段提取出了 `Action`、`Entities` 和 `Parameters`，能力*选择*也用到了它们，但构建可执行动作时用的却是空的 `NormalizedArguments` —— 所以即便是唯一可达的那个写操作（`jira.issue.transition`，它需要一个 `transitionId`）也什么都没发出去。这是一个规模小、边界清晰的数据流修复，测试方法也显而易见：绑定好的参数确实到达了连接器。

**First files:** `apps/Send.Agent.Runtime/src/.../Application/Runtime/DecisionRuntime.cs`
(`BuildExecutableAction`, around line 1665 per the audit; `SemanticInputBinding`,
`UnboundRequiredInputs`); `.../Domain/Execution/ExecutableAction.cs`;
`.../Application/Execution/SemanticInputBinding.cs`;
`.../Application/Goals/DeterministicMissingInformationResolver.cs`;
`.../Domain/Goals/MissingInformation.cs`;
`.../Application/Execution/AuthoritativeActionExecutor.cs`.

**首先查看的文件：** `apps/Send.Agent.Runtime/src/.../Application/Runtime/DecisionRuntime.cs`（`BuildExecutableAction`，据审计约在第 1665 行；`SemanticInputBinding`、`UnboundRequiredInputs`）；`.../Domain/Execution/ExecutableAction.cs`；`.../Application/Execution/SemanticInputBinding.cs`；`.../Application/Goals/DeterministicMissingInformationResolver.cs`；`.../Domain/Goals/MissingInformation.cs`；`.../Application/Execution/AuthoritativeActionExecutor.cs`。

**Done when:** a turn that states an entity and the required value binds them onto the capability's
declared inputs; a turn that states neither asks one focused question instead of proposing an
unexecutable action; both behaviours are unit-tested and the proposal shows the arguments the
person is approving.

**完成标准：** 一轮对话中如果给出了实体和所需的值，就把它们绑定到该能力声明的输入上；如果两者都没给出，就提出一个聚焦的问题，而不是提议一个无法执行的动作；两种行为都有单元测试，并且提议中会展示用户正在审批的参数。

**Ask first:** which capability has a declared, non-secret input that is safe to exercise end-to-end
in dev.

**先问清楚：** 哪个能力具有已声明且非机密的输入，可以在开发环境中安全地端到端实际调用。

### Runner-ups (for later)

**备选（留待以后）**

- Wire `DistillationWorkProcessor → DistillationEngine` (audit #45) — the learning loop is real but
  uncalled; a seeded batch producing a gated insight is a credible demo.

  接通 `DistillationWorkProcessor → DistillationEngine`（审计 #45）—— 学习闭环是真实存在的，但从未被调用；用一批预置数据产出一条经过把关的洞察，就是一个可信的演示。

- Register the `DecisionTask` deadline worker (audit #35) — durable case machinery exists, no
  production caller.

  注册 `DecisionTask` 截止期限工作者（审计 #35）—— 持久化的案例机制已经存在，但没有生产环境的调用方。

---

## After the first contribution

**完成第一次贡献之后**

1. Ask for a second task in the same subsystem you touched — depth beats breadth for the internship.

   在你接触过的同一子系统里申请第二个任务 —— 对实习来说，深度胜过广度。

2. Update this file and [`BRIDGE.md`](./BRIDGE.md) with whatever you verified differently. The
   learning repo is only as good as its freshness.

   把你核实后发现不同的内容更新到本文件和 [`BRIDGE.md`](./BRIDGE.md) 中。学习仓库的价值取决于它有多新鲜。

3. Write the one-page improvement proposal recommended in week 9 (durable approval resume, or
   trace → candidate evidence gating) and send it to a senior engineer.

   写出第 9 周推荐的那份一页纸改进提案（持久化的审批恢复，或者 trace → 候选的证据把关），并把它发给一位资深工程师。
