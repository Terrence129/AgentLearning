# Week 6 — Planning, orchestration and human approval

**第 6 周 — 规划、编排与人工审批**

> **Lab id:** `week06-squads` · **Owned package:** `agentlab/orchestrator/`
> **Starter:** the files in `agentlab/orchestrator/` (they raise `NotImplementedError`)
> **Reference:** `solutions/week06/agentlab/orchestrator/`
> **Tests:** `tests/week06/`
>
> **实验（lab）编号：** `week06-squads` · **负责的包：** `agentlab/orchestrator/`
> **起始代码：** `agentlab/orchestrator/` 中的文件（它们会抛出 `NotImplementedError`）
> **参考实现：** `solutions/week06/agentlab/orchestrator/`
> **测试：** `tests/week06/`

> **The most important artifact in this course is `approval.py`.** The plan
> validator and the topology classifier are useful; the approval binding is the
> difference between a governed agent and a liability. Implement and test it
> first, and re-read `/review` your invariants before moving on.
>
> **本课程中最重要的产物是 `approval.py`。** 计划校验器和拓扑分类器固然有用；但审批绑定决定了一个 Agent 是受治理的，还是一个隐患。请先实现并测试它，在继续之前重新阅读并 `/review` 你的不变量。

## 1. Why this week exists

**1. 为什么要有这一周**

Two failures dominate production multi-agent systems: **too much shape** (a
swarm for a question one tool call answers, fan-out driven by ambiguity) and
**too little control** (a model-settable "approved" flag, duplicate side effects
on retry, approvals outliving the authority they were granted under). SendOS's
ADR-0001 replaced topology-by-vibes with a pure classifier — one capability node
→ direct call, one reasoning node → one specialist, ≥2 connected nodes → one
squad, ≥2 components → multiple squads — and refuses to guess a smaller shape
when the runtime cannot back the derived one
([`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.5).
Its `ApprovalCheckpoint` binds every write to the exact action, actor, tenant,
authority snapshot and expiry, and executes at most once (§4.1). This week you
rebuild both, small enough to hold in your head and test exhaustively.

生产环境中的多 Agent 系统主要有两类失败：**结构过多**（一次工具调用就能回答的问题却动用一群 Agent，由含糊不清驱动的扇出）和**控制过少**（模型可以自行设置的「已批准」标志、重试时重复产生的副作用、审批在授予它的权限失效后依然有效）。SendOS 的 ADR-0001 用一个纯分类器取代了凭感觉决定拓扑的做法——一个能力节点 → 直接调用，一个推理节点 → 一个专员 Agent（specialist），≥2 个相连节点 → 一个小队（squad），≥2 个连通分量 → 多个小队——并且当运行时无法支撑推导出的结构时，拒绝去猜一个更小的结构（[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.5）。它的 `ApprovalCheckpoint` 把每次写操作绑定到确切的动作、执行者、租户、权限快照和过期时间，并且最多执行一次（§4.1）。本周你将重建这两者，规模小到可以装在脑子里并进行穷尽测试。

Without this week, "AI recommends, a human approves, the backend executes" is a
sentence in a pitch deck rather than a property of the system.

没有这一周，「AI 建议、人类审批、后端执行」就只是融资演示文稿里的一句话，而不是系统本身的属性。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **Time:** 10–12 h (plan/approval ≈ 5 h, orchestrator ≈ 3 h, reading/review ≈ 3 h).

  **时间：** 10–12 小时（计划/审批 ≈ 5 小时，编排者 ≈ 3 小时，阅读/复习 ≈ 3 小时）。

- **Must be green:** foundation (`pytest -q`); week 2's loop is *not* required —
  this package has its own tiny driver inside `specialist.py`.

  **必须通过（变绿）：** 基础部分（`pytest -q`）；*不*需要第 2 周的循环——这个包在 `specialist.py` 里有自己的小型驱动器。

- **Reading:** `docs/research/01-agent-architecture-sota.md` §6 (§6.2 HITL,
  §6.4 pause/resume state machine); `docs/research/05-sendos-concept-map.md`
  §4.1 and §4.5; ADR-0001 in the SendOS repo.

  **阅读：** `docs/research/01-agent-architecture-sota.md` §6（§6.2 人在回路（HITL），§6.4 暂停/恢复状态机）；`docs/research/05-sendos-concept-map.md` §4.1 和 §4.5；SendOS 仓库中的 ADR-0001。

- **Tools:** `MockProvider` for every model interaction; a fake clock for
  expiry; no sleeps, no network.

  **工具：** 所有模型交互都使用 `MockProvider`；过期逻辑使用假时钟；不使用 sleep，不访问网络。

## 3. The spec

**3. 规格说明**

Implement every `NotImplementedError` in `agentlab/orchestrator/`.

实现 `agentlab/orchestrator/` 中所有的 `NotImplementedError`。

| File<br>文件 | Public surface<br>公开接口 | Contract summary<br>契约摘要 |
|---|---|---|
| `plan.py` | `NodeKind`, `Workstream`, `Plan`, `PlanError`, `validate_plan`, `topo_order`, `ready_workstreams`, `ReplanDecision`, `replan_after_failure` | Closed kinds `capability`/`reasoning`; capability nodes must name a capability, reasoning nodes must not; unique ids, known dependencies, acyclic graph, non-empty acceptance criteria, positive budgets. Topological order is deterministic (Kahn, declaration order). Replanning drops the failed node and its transitive dependents, refuses to exceed the retry budget, and refuses to empty the plan.<br>封闭的节点类型 `capability`/`reasoning`；能力节点必须指明一个能力，推理节点则不得指明；id 唯一、依赖已知、图无环、验收标准非空、预算为正。拓扑顺序是确定的（Kahn 算法，按声明顺序）。重新规划会丢弃失败节点及其所有传递依赖者，拒绝超出重试预算，也拒绝把计划清空。 |
| `specialist.py` | `ContextEnvelope`, `HandoffArtifact`, `SpecialistSpec`, `Specialist`, `SpecialistError` | Least-context input (objective/facts/constraints/references — **no transcript field**); only allowlisted tools are exposed, and calls to others become error observations without execution; the loop charges and enforces an optional budget; the final answer must be a JSON hand-off (`summary` required; `findings`/`artifacts` string arrays; `confidence` in `[0,1]`) or `SpecialistError`; trace emits `subagent_start`/`subagent_end` on a child scope carrying the summary/confidence/finding count, never the transcript.<br>最小上下文输入（目标/事实/约束/引用——**没有对话记录字段**）；只暴露白名单中的工具，对其他工具的调用会变成错误观察结果而不会被执行；循环会计费并强制执行可选的预算；最终答案必须是一个 JSON 交接物（`summary` 必填；`findings`/`artifacts` 为字符串数组；`confidence` 在 `[0,1]` 范围内），否则为 `SpecialistError`；trace 在子作用域上发出 `subagent_start`/`subagent_end`，携带摘要/置信度/发现数量，绝不包含对话记录。 |
| `orchestrator.py` | `ExecutionShape`, `ShapeSelection`, `component_ids`, `classify_shape`, `select_shape`, `WorkstreamResult`, `OrchestrationResult`, `Orchestrator`, `CapabilityExecutor` | Pure classifier over plan topology. Unbacked derived shape → `shape=None`, `backed=False`, and a limitation that names the shape and refuses to guess smaller. Execution: validate → select shape → short-circuit with a limitation if unbacked → run in deterministic dependency order; capability nodes call plain functions, reasoning nodes run registered specialists with envelopes built from the objective, plan goal and upstream outputs; failed dependencies skip dependents (never guess); missing executors/specialists, specialist errors and budget overruns are reported per workstream; aggregate budget sums the per-workstream ledgers.<br>基于计划拓扑的纯分类器。推导出的结构若无支撑 → `shape=None`、`backed=False`，并给出一条指明该结构、拒绝猜测更小结构的限制说明。执行流程：校验 → 选择结构 → 若无支撑则带着限制说明短路返回 → 按确定的依赖顺序运行；能力节点调用普通函数，推理节点运行已注册的专员 Agent，其信封由目标、计划目标和上游输出构建；依赖失败则跳过其依赖者（绝不猜测）；缺失的执行器/专员 Agent、专员 Agent 错误和预算超支都按工作流逐一报告；总预算是各工作流账目之和。 |
| `approval.py` | `ApprovalState`, `Authority`, `ActionProposal`, `action_hash`, `ApprovalBinding`, `ApprovalRecord`, `ExecutionResult`, `ApprovedAction`, `ProposalStore`, `InMemoryProposalStore`, `ApprovalCheckpoint`, typed errors | See the invariants below — they are the spec.<br>见下方的不变量——它们就是规格说明。 |

### The invariants (tested one by one in `tests/week06/test_approval.py`)

**不变量（在 `tests/week06/test_approval.py` 中逐条测试）**

1. **Persisted before approval.** `propose` writes the proposal to the store and
   only then opens a PENDING approval; `approve` refuses a proposal that is not
   in the store; a store failure leaves no approval behind.

   **先持久化，再审批。** `propose` 先把提案写入存储，然后才开启一个 PENDING 状态的审批；`approve` 拒绝不在存储中的提案；存储失败不会留下任何审批。

2. **Exact binding.** `ApprovalBinding(actor, tenant, action_hash,
   authority_snapshot, expires_at)` binds the human decision to the canonical
   action. A mismatched hash is rejected at approval; editing the persisted
   proposal after approval blocks execution.

   **精确绑定。** `ApprovalBinding(actor, tenant, action_hash, authority_snapshot, expires_at)` 把人的决定绑定到规范化的动作上。哈希不匹配会在审批时被拒绝；审批后再编辑已持久化的提案会阻止执行。

3. **Proposer ≠ approver.** Self-approval is not a control.

   **提议者 ≠ 审批者。** 自我审批不算管控。

4. **Tenant match.** Approvals cannot cross tenants.

   **租户匹配。** 审批不能跨租户。

5. **Expiry.** An expired binding can be neither approved nor executed; the
   record moves to `EXPIRED`.

   **过期。** 已过期的绑定既不能被批准，也不能被执行；记录转入 `EXPIRED`。

6. **Authority.** The approver's snapshot must cover the action's required
   authority; at execution, *current* authority must still cover the snapshot —
   narrowing between approval and execution blocks the write.

   **权限。** 审批者的快照必须覆盖该动作所需的权限；执行时，*当前*权限必须仍然覆盖该快照——在审批与执行之间权限若被收窄，写操作会被阻止。

7. **At-most-once.** Execution is reserved (state persisted as `EXECUTED`)
   *before* the executor runs; a replay raises `ApprovalReplayRejected` and the
   executor is called once. Every effect carries a deterministic
   `idempotency_key`. An executor failure marks `FAILED` and never retries.

   **最多一次。** 在执行器运行*之前*就预留执行（状态持久化为 `EXECUTED`）；重放会抛出 `ApprovalReplayRejected`，执行器只被调用一次。每个效果都带有一个确定性的 `idempotency_key`。执行器失败会标记为 `FAILED`，并且绝不重试。

8. **State machine.** `PENDING → APPROVED | REJECTED | CANCELLED`,
   `APPROVED → EXECUTED | REVOKED`, `PENDING | APPROVED → EXPIRED`; everything
   else raises `InvalidApprovalTransition`. Every step emits
   `approval_requested` / `approval_granted` / `approval_denied` /
   `tool_call` trace events (arguments are not logged; only the action and the
   idempotency key).

   **状态机。** `PENDING → APPROVED | REJECTED | CANCELLED`，`APPROVED → EXECUTED | REVOKED`，`PENDING | APPROVED → EXPIRED`；其他任何转换都会抛出 `InvalidApprovalTransition`。每一步都会发出 `approval_requested` / `approval_granted` / `approval_denied` / `tool_call` trace 事件（不记录参数；只记录动作和幂等键）。

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
# 1. starter red
.\.venv\Scripts\python.exe -m pytest tests/week06 -m week -q

# 2. green after implementing
.\.venv\Scripts\python.exe -m pytest tests/week06 -m week -q

# 3. lint
.\.venv\Scripts\ruff.exe check agentlab/orchestrator tests/week06

# 4. foundation green
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
# 1. starter red
uv run pytest tests/week06 -m week -q

# 2. green after implementing
uv run pytest tests/week06 -m week -q

# 3. lint
uv run ruff check agentlab/orchestrator tests/week06

# 4. foundation green
uv run pytest -q
```

Manual acceptance (the learning-plan deliverable): a miniature "should we
discount this deal?" flow — meta-orchestrator → 1–2 specialists → typed decision
→ approval-gated write → audit row — built as a local script or notebook on top
of this package, plus a test (in your own notes/script, not in
`tests/week06/`) proving an edited, replayed or expired approval cannot execute.

人工验收（学习计划的交付物）：在这个包之上，以本地脚本或 notebook 的形式构建一个迷你的「这笔交易要不要打折？」流程——元编排者 → 1–2 个专员 Agent → 类型化决策 → 受审批把关的写操作 → 审计记录行——再加上一个测试（写在你自己的笔记/脚本里，而不是 `tests/week06/` 中），证明被编辑过、被重放或已过期的审批无法执行。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. **Order of checks in `approve` matters for the tests:** not found → state →
   persistence → proposer → tenant → hash → authority → expiry. Each check has
   a distinct error type; do not collapse them into one.

   **`approve` 中检查的顺序对测试很重要：** 未找到 → 状态 → 持久化 → 提议者 → 租户 → 哈希 → 权限 → 过期。每项检查都有各自不同的错误类型；不要把它们合并成一个。

2. `action_hash` must hash `{"action", "arguments", "tenant"}` with
   `sort_keys=True`; key order in a Python dict is not stable across callers.

   `action_hash` 必须以 `sort_keys=True` 对 `{"action", "arguments", "tenant"}` 进行哈希；Python 字典中的键顺序在不同调用者之间并不稳定。

3. Persist the **executed** state before calling the executor. If you call the
   executor first and then write the record, a crash in between gives you two
   side effects on retry — the exact bug at-most-once exists to prevent.

   在调用执行器之前先持久化**已执行**状态。如果你先调用执行器再写记录，两者之间发生崩溃会导致重试时产生两次副作用——这正是「最多一次」要防止的 bug。

4. Compare authority in the right direction: at approval, `snapshot.covers(required)`;
   at execution, `current.covers(snapshot)`. "No amount limit" (`None`) covers
   any amount; a numeric cap only covers a smaller-or-equal required cap.

   按正确的方向比较权限：审批时用 `snapshot.covers(required)`；执行时用 `current.covers(snapshot)`。「无金额上限」（`None`）覆盖任何金额；数值上限只覆盖小于或等于它的所需上限。

5. Shape selection is a *pure* function of topology. If any test outcome depends
   on budgets or objectives, you have put policy where classification belongs.

   结构选择是拓扑的*纯*函数。如果任何测试结果依赖于预算或目标，说明你把策略放在了本该属于分类的地方。

6. For the classifier, dependency edges are undirected when counting connected
   components. "≥ 2 connected nodes" means one component with ≥ 2 nodes.

   对分类器来说，计算连通分量时依赖边是无向的。「≥ 2 个相连节点」指的是一个包含 ≥ 2 个节点的连通分量。

7. In the specialist, validate the hand-off **before** it crosses the boundary.
   A malformed JSON response is a failed specialist, not a partial result.

   在专员 Agent 中，要在交接物越过边界**之前**对其进行校验。格式错误的 JSON 响应意味着专员 Agent 失败，而不是部分结果。

8. `Orchestrator.run` must not raise for a failed workstream — failures are
   data (`WorkstreamResult.error`) so a human/replan layer can decide. Invalid
   *plans* still raise `PlanError`.

   `Orchestrator.run` 不能因为某个工作流失败而抛出异常——失败是数据（`WorkstreamResult.error`），以便由人或重新规划层来决定。无效的*计划*仍然会抛出 `PlanError`。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| `test_proposal_edited_after_approval_cannot_execute` passes but replay test fails<br>`test_proposal_edited_after_approval_cannot_execute` 通过但重放测试失败 | You check the hash at execution time but re-read the binding from the *caller*, or you re-reserve `EXECUTED` on every call.<br>你在执行时检查了哈希，但却从*调用者*那里重新读取绑定，或者每次调用都重新预留 `EXECUTED`。 |
| `AuthorityNarrowed` raised for a clearly sufficient authority<br>权限明显足够却抛出 `AuthorityNarrowed` | You reversed the argument order: it is `current_authority.covers(binding.authority_snapshot)`.<br>你把参数顺序弄反了：应该是 `current_authority.covers(binding.authority_snapshot)`。 |
| Approval "works" but `pending()` is empty<br>审批「能用」但 `pending()` 为空 | `_transition` created a new record without replacing it in the checkpoint's map.<br>`_transition` 创建了新记录，却没有在检查点的映射中替换它。 |
| `classify_shape` returns SINGLE_SQUAD for two independent workstreams<br>对两个独立工作流，`classify_shape` 返回了 SINGLE_SQUAD | You counted dependency *edges* instead of connected components; two nodes with no edges are two components.<br>你数的是依赖*边*而不是连通分量；两个没有边的节点是两个连通分量。 |
| Unbacked shape test still executes specialists<br>无支撑结构的测试仍然执行了专员 Agent | You returned a limitation but continued into the execution path; short-circuit immediately after `select_shape`.<br>你返回了限制说明，但仍继续进入执行路径；应在 `select_shape` 之后立即短路返回。 |
| `OrchestrationResult.ok` is True after a dependency failure<br>依赖失败后 `OrchestrationResult.ok` 仍为 True | `ok` must require `result.ok or result.skipped` for **all** workstreams, and a skipped-but-blocked branch may still make the run not-ok via the failed dependency.<br>`ok` 必须要求**所有**工作流都满足 `result.ok or result.skipped`，而一个被跳过但被阻塞的分支仍可能因失败的依赖使整次运行变为不 ok。 |
| Specialist test finds "not in this specialist's tool set" in the *first* tool message<br>专员 Agent 测试在*第一条*工具消息中发现「not in this specialist's tool set」 | That message is correct — the forbidden tool must not run, but the model must see why. Check the handler-invocation list, not the prompt.<br>这条消息是正确的——被禁止的工具不能运行，但模型必须看到原因。应检查处理器调用列表，而不是提示词。 |
| Expiry test flakes<br>过期测试时过时不过 | You used `time.time`; inject the fake clock through `ApprovalCheckpoint(clock=...)` and build `expires_at` from it.<br>你用了 `time.time`；应通过 `ApprovalCheckpoint(clock=...)` 注入假时钟，并用它来构造 `expires_at`。 |

## 7. SendOS bridge

**7. 与 SendOS 的衔接**

Read (45 min, read-only), with paths from
[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)
§4.1 and §4.5:

阅读（45 分钟，只读），路径取自 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.1 和 §4.5：

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs`
  (typed decision family);

  `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs`（类型化决策族）；

- `.../Application/Approval/ApprovalCheckpoint.cs` (lines ~237–468) and
  `.../Properties/ApprovalBindingAtMostOncePropertyTests.cs`;

  `.../Application/Approval/ApprovalCheckpoint.cs`（约第 237–468 行）以及 `.../Properties/ApprovalBindingAtMostOncePropertyTests.cs`；

- `.../Planning/TopologyClassifier.cs` (~28–102),
  `.../Planning/ExecutionPlanner.cs` (~143–230), and
  `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md`;

  `.../Planning/TopologyClassifier.cs`（约 28–102 行）、`.../Planning/ExecutionPlanner.cs`（约 143–230 行），以及 `docs/adrs/0001-flag-gated-logical-planner-shape-selection.md`；

- `.../Domain/Authority/EffectiveAuthority.cs` and
  `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs`.

  `.../Domain/Authority/EffectiveAuthority.cs` 以及 `.../Properties/SingleMinimalShapeReviewModeOrthogonalPropertyTests.cs`。

Answer in your lab notes:

在你的实验笔记中回答：

1. Which invariants does `ApprovalCheckpoint.cs` enforce that this miniature does
   **not** (durability across process restart, revocation feeds, dual control,
   compensating actions), and what is the smallest test that would prove each?

   `ApprovalCheckpoint.cs` 强制执行了哪些这个迷你版本**没有**实现的不变量（跨进程重启的持久性、撤销通知流、双人控制、补偿动作）？能证明每一项的最小测试是什么？

2. Where does `TopologyClassifier` take inputs that are *not* pure topology
   (flags, importance scores, planner hints), and why does ADR-0001 explicitly
   keep classification orthogonal to review mode?

   `TopologyClassifier` 在哪些地方接收了*非*纯拓扑的输入（标志、重要性评分、规划器提示）？为什么 ADR-0001 明确让分类与评审模式保持正交？

3. If you added durable suspend/resume to `ApprovalCheckpoint` (SQLite + resume
   on callback + CAS against double-resume), which of this week's invariants
   would still hold by construction, and which would now depend on the database
   transaction boundary?

   如果你为 `ApprovalCheckpoint` 添加持久化的挂起/恢复（SQLite + 回调时恢复 + 用 CAS 防止重复恢复），本周的哪些不变量在构造上仍然成立，哪些会转而依赖数据库事务边界？

## 8. Stretch (optional)

**8. 拓展（可选）**

1. **Durable suspend/resume.** Persist pending approvals to SQLite, return a
   token to the caller, and resume execution from a callback process. Use a
   compare-and-swap on `(approval_id, state)` so two concurrent resumes produce
   exactly one execution. This is SendOS's unwired `CaseRuntime`; a working
   miniature is a credible contribution proposal.

   **持久化的挂起/恢复。** 把待处理的审批持久化到 SQLite，向调用者返回一个令牌，并从回调进程中恢复执行。在 `(approval_id, state)` 上使用比较并交换（compare-and-swap），使两个并发的恢复只产生恰好一次执行。这就是 SendOS 中尚未接线的 `CaseRuntime`；一个可运行的迷你版本就是一份可信的贡献提案。

2. **Property tests for the invariants.** Without adding `hypothesis`, loop over
   generated approval sequences (approve/reject/revoke/expire/execute in every
   order) and assert at-most-once, terminal states are terminal, and no sequence
   executes without an APPROVED state.

   **为不变量编写属性测试。** 不引入 `hypothesis`，遍历生成的审批序列（批准/拒绝/撤销/过期/执行的所有顺序组合），并断言：最多执行一次、终止状态确实是终止的、没有任何序列能在缺少 APPROVED 状态的情况下执行。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** why is an approval a *binding over a hash* rather than a
   message saying "approved"? Which of the seven invariants becomes impossible
   to enforce without the hash?

   **概念层面：** 为什么审批是*对哈希的绑定*，而不是一条写着「已批准」的消息？没有哈希的话，七条不变量中的哪一条将无法强制执行？

2. **Architectural:** the classifier refuses to downgrade an unbacked shape.
   Where else in the system should "refuse rather than guess" apply, and what is
   the cost of that refusal to a product team?

   **架构层面：** 分类器拒绝降级一个无支撑的结构。系统中还有哪些地方应当适用「宁可拒绝也不猜测」？这种拒绝对产品团队的代价是什么？

3. **Transfer:** when would you deliberately choose a *larger* shape than the
   topology requires (e.g. two specialists where one would do), and what would
   you measure to justify it afterwards?

   **迁移应用：** 什么时候你会刻意选择比拓扑所需*更大*的结构（例如一个专员 Agent 就够用时却用两个）？事后你会度量什么来证明这样做是合理的？
