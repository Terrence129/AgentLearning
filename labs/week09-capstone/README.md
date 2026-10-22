# Week 9 — Capstone: Mini-SendOS

**第 9 周 — 结业项目（capstone）：迷你 SendOS**

**Time:** 12–16 h · **Prerequisites:** weeks 1–8 green (`tests/week01`–`tests/week08`), `scripts/demo_capstone.py` runnable · **Module:** `agentlab/capstone/`, `agentlab/web/` · **Tests:** `tests/week09`

**时间：** 12–16 小时 · **前置条件：** 第 1–8 周全部通过（变绿）（`tests/week01`–`tests/week08`），`scripts/demo_capstone.py` 可以运行 · **模块：** `agentlab/capstone/`、`agentlab/web/` · **测试：** `tests/week09`

## 1. Why this week exists

**1. 为什么要有这一周**

Every previous week built one mechanism in isolation. This week composes them into one honest, governed system: a goal becomes a typed decision, a state change becomes a persisted proposal, a human approves it with binding checks, execution happens at most once, and every step lands in an append-only audit trail. The failure this prevents is the demo that looks intelligent and cannot be trusted — model-authored "approved" booleans, duplicate side effects on retry, and no evidence of who approved what or under which authority. Nothing new is invented this week; the work is integration, and integration is where the course's claims get tested.

之前的每一周都是孤立地构建某一种机制。本周把它们组合成一个诚实、受治理的系统：一个目标变成一个类型化决策，一次状态变更变成一个已持久化的提案，由人在绑定检查下进行审批，执行最多发生一次，并且每一步都落入只追加的审计轨迹中。它要防止的失败，是那种看起来很智能却无法被信任的演示——由模型生成的「已批准」布尔值、重试时重复的副作用，以及没有任何证据表明是谁、在什么权限下批准了什么。本周不发明任何新东西；工作就是集成，而集成正是检验本课程各项主张的地方。

## 2. Prerequisites and time budget

**2. 前置条件与时间预算**

| Area<br>领域 | Must be true before you start<br>开始前必须满足的条件 |
|---|---|
| Weeks 1–2<br>第 1–2 周 | provider seam + loop green — the capstone reuses `Provider`, `ToolRegistry`, `Budget`, `Tracer`<br>模型提供商（provider）接缝（seam）+ 循环已通过——结业项目会复用 `Provider`、`ToolRegistry`、`Budget`、`Tracer` |
| Week 3<br>第 3 周 | structured output + prompt versions green — decisions are the same discipline<br>结构化输出 + 提示词版本已通过——决策遵循的是同一套规范 |
| Week 4<br>第 4 周 | context/memory green — the decision pipeline must fit a context budget<br>上下文/记忆已通过——决策流水线必须符合上下文预算 |
| Weeks 6–8<br>第 6–8 周 | approval, authority, audit, evals green — the capstone composes them<br>审批、权限、审计、评测（eval）已通过——结业项目会把它们组合起来 |
| Tooling<br>工具 | `.\.venv\Scripts\python.exe` (Windows) / `uv run python` (macOS/Linux) works; run everything from the repo root<br>`.\.venv\Scripts\python.exe`（Windows）/ `uv run python`（macOS/Linux）可用；所有命令都从仓库根目录运行 |

Suggested split: 2 h read the brief + starter contracts; 6–8 h implement `decisions.py`, `catalogue.py`, `platform.py`; 2 h wire `web/`; 1 h demo + acceptance; 1–2 h write-up and reflection.

建议的时间分配：2 小时阅读任务说明和起始代码的契约；6–8 小时实现 `decisions.py`、`catalogue.py`、`platform.py`；2 小时接通 `web/`；1 小时演示 + 验收；1–2 小时撰写总结文章和反思。

## 3. The spec

**3. 规格说明**

Run the prerequisite check first — it tells you what is missing, in order:

先运行前置条件检查——它会按顺序告诉你缺了什么：

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe scripts\demo_capstone.py
```

```bash
# macOS / Linux
uv run python scripts/demo_capstone.py
```

You are done when that script exits `0` and prints `DEMO COMPLETE`.

当这个脚本以 `0` 退出并打印出 `DEMO COMPLETE` 时，你就完成了。

### Step 1 — Provider layer (reuse, don't rebuild)

**第 1 步 — 提供商层（复用，不要重建）**

`agentlab/capstone/platform.py` receives a `provider` (`agentlab.providers.base.Provider`), a `tools` registry, and a `catalogue`. The demo passes `agentlab.testing.MockProvider`. Do not add network calls to the capstone flow; a live-provider run is the *stretch*, behind `@pytest.mark.network`.

`agentlab/capstone/platform.py` 接收一个 `provider`（`agentlab.providers.base.Provider`）、一个 `tools` 注册表和一个 `catalogue`。演示中传入的是 `agentlab.testing.MockProvider`。不要在结业项目流程中添加网络调用；使用真实提供商运行属于*拓展*内容，放在 `@pytest.mark.network` 之后。

### Step 2 — Capability catalogue: `agentlab/capstone/catalogue.py`

**第 2 步 — 能力目录：`agentlab/capstone/catalogue.py`**

| Symbol<br>符号 | Contract<br>契约 |
|---|---|
| `CapabilityDefinition` | frozen dataclass: `id`, `description`, `input_schema`, `risk_level`, `is_write`, `approval_required`, `tenant_ids`, `version`, `source`<br>冻结的 dataclass：`id`、`description`、`input_schema`、`risk_level`、`is_write`、`approval_required`、`tenant_ids`、`version`、`source` |
| `CapabilityCatalogue.merge(connectors, published)` | validate both sources; duplicates *within* a source raise `CatalogueError`; published wins on id conflicts (whole definition, never field-merged); result order-independent<br>校验两个来源；同一来源*内部*的重复项会抛出 `CatalogueError`；id 冲突时以已发布版本为准（整个定义替换，绝不按字段合并）；结果与顺序无关 |
| `CapabilityCatalogue.resolve(id, tenant)` | return the definition when known and permitted, else `CapabilityNotAvailable`; unknown and "not for this tenant" must be indistinguishable (no cross-tenant oracle); empty tenant fails closed<br>已知且被允许时返回定义，否则抛出 `CapabilityNotAvailable`；「未知」与「不属于该租户」必须无法区分（不能成为跨租户的探测神谕）；租户为空时失败即关闭 |
| `CapabilityCatalogue.list_for_tenant(tenant)` | sorted tuple, universal + tenant-scoped<br>排好序的元组，包含通用能力 + 该租户范围内的能力 |
| `CapabilityCatalogue.ids()` / `__len__` | sorted ids / count<br>排好序的 id / 数量 |

Fail-closed rules (tests enforce them): snake_case ids, `input_schema` is `type: object`, valid risk level, **every write declares `approval_required=True`**, and an empty `tenant_ids` set is invalid.

失败即关闭的规则（由测试强制执行）：id 为 snake_case，`input_schema` 为 `type: object`，风险等级合法，**每个写操作都声明 `approval_required=True`**，并且空的 `tenant_ids` 集合是无效的。

### Step 3 — Typed decisions: `agentlab/capstone/decisions.py`

**第 3 步 — 类型化决策：`agentlab/capstone/decisions.py`**

Implement the closed union documented at the top of the file: `parse_decision`, `decision_to_wire`, `enforce_presentation_budgets`. The wire contract table is the specification; the tests are the proof. Three things to get right:

实现文件顶部所描述的封闭联合类型：`parse_decision`、`decision_to_wire`、`enforce_presentation_budgets`。传输契约表就是规格说明；测试就是证明。有三件事必须做对：

1. **Validate fully before raising.** `SchemaValidationError.errors` lists *every* problem, not the first.

   **在抛出之前完整校验。** `SchemaValidationError.errors` 列出*每一个*问题，而不只是第一个。

2. **Closed union.** Unknown kinds and unknown fields are rejected; the model cannot smuggle new keys into the contract.

   **封闭联合。** 未知的类型和未知的字段都会被拒绝；模型无法把新的键偷偷塞进契约。

3. **Presentation budgets.** Headline ≤ 12 words, `next_moves` ≤ 4, clarification `options` ≤ 3, and the single primary text field ≤ 2 sentences. Collect all violations into one `PresentationBudgetError`.

   **展示预算。** 标题 ≤ 12 个词，`next_moves` ≤ 4 项，澄清用的 `options` ≤ 3 项，唯一的主文本字段 ≤ 2 句话。把所有违规项收集到一个 `PresentationBudgetError` 中。

### Step 4 — The governed lifecycle: `agentlab/capstone/platform.py`

**第 4 步 — 受治理的生命周期：`agentlab/capstone/platform.py`**

| Method<br>方法 | Invariant<br>不变量 |
|---|---|
| `action_digest(capability_id, arguments)` | deterministic hash; key order must not matter<br>确定性的哈希；键的顺序不能影响结果 |
| `submit_goal(request)` | authenticated goal → one budget-safe `Decision`; no catalogue bypass<br>经过认证的目标 → 一个符合预算的 `Decision`；不得绕过能力目录 |
| `propose_action(...)` | capability resolved for the tenant; writes only; **proposal persisted before approval**, with `action_hash` and `expires_at`<br>按租户解析能力；仅限写操作；**提案在审批前持久化**，并带有 `action_hash` 和 `expires_at` |
| `approve(proposal_id, approver_id, approved)` | unknown/expired → `ApprovalError`; proposer ≠ approver; decision persisted and audited<br>未知/已过期 → `ApprovalError`；提议者 ≠ 审批者；决定会被持久化并记入审计 |
| `execute(proposal_id, approval_id)` | missing/rejected/expired/mismatched approval → `ExecutionError`; **at most once**; executes via `tools`; audits start + finish<br>审批缺失/被拒绝/已过期/不匹配 → `ExecutionError`；**最多一次**；通过 `tools` 执行；审计记录开始 + 结束 |
| `audit_trail()` | append-only, strictly increasing `seq` from 1, never mutated or removed<br>只追加，`seq` 从 1 开始严格递增，永不修改或删除 |

### Step 5 — The surface: `agentlab/web/`

**第 5 步 — 界面层：`agentlab/web/`**

`agentlab/web/app.py` is written but stubbed: `create_app(platform)` wires routes `POST /api/goal`, `POST /api/proposals`, `POST /api/proposals/{id}/approve`, `POST /api/proposals/{id}/execute`, `GET /api/audit` and the HTML page. FastAPI is an optional extra — importing `agentlab.web` must work without it. Run the UI with:

`agentlab/web/app.py` 已经写好，但仍是桩实现：`create_app(platform)` 接通了路由 `POST /api/goal`、`POST /api/proposals`、`POST /api/proposals/{id}/approve`、`POST /api/proposals/{id}/execute`、`GET /api/audit` 以及 HTML 页面。FastAPI 是可选依赖——没有它时导入 `agentlab.web` 也必须能正常工作。用以下命令运行 UI：

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pip install -e ".[web]"
.\.venv\Scripts\python.exe -c "from agentlab.web.app import create_app, main; main()"
```

```bash
# macOS / Linux
uv sync --extra web
uv run python -c "from agentlab.web.app import create_app, main; main()"
```

No route may invent text: the UI renders the typed decision and forwards approval/execution to the platform.

任何路由都不得自行编造文本：UI 只渲染类型化决策，并把审批/执行转发给平台。

### Step 6 — Learning loop, demo and write-up

**第 6 步 — 学习回路、演示与总结文章**

- The audit trail is your eval substrate: after the demo, read `audit_trail()` and confirm the exact sequence `proposal_created → approval_granted → execution_started → execution_finished` (at minimum).

  审计轨迹就是你的评测基础：演示结束后，读取 `audit_trail()`，并确认确切的顺序为 `proposal_created → approval_granted → execution_started → execution_finished`（至少要有这些）。

- `scripts/demo_capstone.py` is the end-to-end acceptance: offline, mock provider, exits `0`.

  `scripts/demo_capstone.py` 是端到端的验收：离线运行，使用模拟提供商，以 `0` 退出。

- Fill `projects/capstone/ACCEPTANCE.md`, then write up the design in `projects/portfolio/WRITEUP.md`.

  填写 `projects/capstone/ACCEPTANCE.md`，然后在 `projects/portfolio/WRITEUP.md` 中写下设计总结。

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
# 1. starter is replaced by your implementation; lab tests green
.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q

# 2. the demo runs the whole lifecycle offline and exits 0
.\.venv\Scripts\python.exe scripts\demo_capstone.py

# 3. foundation still green (default pytest excludes week markers)
.\.venv\Scripts\python.exe -m pytest -q

# 4. lint your files
.\.venv\Scripts\ruff.exe check agentlab\capstone agentlab\web tests\week09

# 5. web imports without FastAPI installed
.\.venv\Scripts\python.exe -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"
```

```bash
# macOS / Linux
# 1. starter is replaced by your implementation; lab tests green
uv run pytest tests/week09 -m week -q

# 2. the demo runs the whole lifecycle offline and exits 0
uv run python scripts/demo_capstone.py

# 3. foundation still green (default pytest excludes week markers)
uv run pytest -q

# 4. lint your files
uv run ruff check agentlab/capstone agentlab/web tests/week09

# 5. web imports without FastAPI installed
uv run python -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"
```

Strong submission also shows: two tenants cannot see each other's capabilities; a replayed approval cannot execute twice; and editing the proposal arguments after approval blocks execution (hash mismatch). Add those as tests in `tests/week09/test_capstone_extra.py` (mark them `pytest.mark.week`).

优秀的提交还会展示：两个租户看不到彼此的能力；被重放的审批无法执行两次；审批后再编辑提案参数会阻止执行（哈希不匹配）。把这些作为测试添加到 `tests/week09/test_capstone_extra.py` 中（标记为 `pytest.mark.week`）。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. Read the module docstring of `decisions.py` first; the wire table is the test spec in prose.

   先读 `decisions.py` 的模块 docstring；其中的传输表就是用文字写成的测试规格。

2. Implement `parse_decision` before `decision_to_wire`; then round-trip in a REPL until it is boring.

   先实现 `parse_decision`，再实现 `decision_to_wire`；然后在 REPL 里反复做往返转换，直到觉得乏味为止。

3. In `catalogue.merge`, process connectors first and published second — "published wins" then falls out of dict assignment order.

   在 `catalogue.merge` 中，先处理连接器，再处理已发布的定义——这样「以已发布版本为准」就自然由字典的赋值顺序得出。

4. For `resolve`, build the availability predicate once; the "same error" rule is easier when both branches share it.

   对于 `resolve`，只构建一次可用性判断谓词；当两个分支共用它时，「相同错误」这条规则会更容易实现。

5. In `platform.propose_action`, compute the digest from canonical JSON (`sort_keys=True`) *before* persisting; the approval binds to that string, not to a re-derived copy.

   在 `platform.propose_action` 中，要在持久化*之前*基于规范化 JSON（`sort_keys=True`）计算摘要；审批绑定的是这个字符串，而不是重新推导出来的副本。

6. Store the approval's `proposal_id` **and** compare it to the proposal's `action_hash` at execute time; matching ids alone is not binding.

   存储审批的 `proposal_id`，**并且**在执行时将其与提案的 `action_hash` 进行比较；仅仅 id 匹配并不构成绑定。

7. Keep the audit append in a single helper (`_audit.append(...)`) so `seq` cannot skip.

   把审计追加操作集中在一个辅助函数（`_audit.append(...)`）中，这样 `seq` 就不会跳号。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Meaning / fix<br>含义 / 修复方法 |
|---|---|
| `NotImplementedError: Week 9 capstone: implement ...` | Expected on the starter. Build in the order the demo prints.<br>在起始代码上这是预期行为。按演示打印的顺序逐步构建。 |
| `SchemaValidationError: unknown field(s) for ...` | Your wire payload has a key the contract does not allow; check the docstring table.<br>你的传输载荷中有契约不允许的键；请检查 docstring 中的表格。 |
| `CatalogueError: write capability ... must set approval_required=True` | Fail-closed rule; a write may not be auto-approved by omission.<br>失败即关闭规则；写操作不能因为漏写而被自动批准。 |
| `ApprovalError` on a fresh approval | Maker-checker: the demo's approver must differ from the proposer (analyst vs manager).<br>制单-复核（maker-checker）原则：演示中的审批者必须不同于提议者（分析师与经理）。 |
| `SystemExit: demo expected an action_proposal` | `submit_goal` consumed the scripted mock turn somewhere else; make it parse the text turn and return the decision.<br>`submit_goal` 在别处消耗掉了脚本化的模拟轮次；让它解析文本轮次并返回决策。 |
| `ModuleNotFoundError: agentlab` when running the demo | Run from the repo root: `.\.venv\Scripts\python.exe scripts\demo_capstone.py` (Windows) / `uv run python scripts/demo_capstone.py` (macOS/Linux).<br>从仓库根目录运行：`.\.venv\Scripts\python.exe scripts\demo_capstone.py`（Windows）/ `uv run python scripts/demo_capstone.py`（macOS/Linux）。 |
| `ConfigError: FastAPI is not installed` | Optional extra missing: `pip install -e ".[web]"` (Windows) / `uv sync --extra web` (macOS/Linux). Import of the module must still work.<br>缺少可选依赖：`pip install -e ".[web]"`（Windows）/ `uv sync --extra web`（macOS/Linux）。模块的导入仍然必须能正常工作。 |

## 7. SendOS bridge

**7. 与 SendOS 的衔接**

Read these before answering the questions (paths relative to the SendOS repo root; see [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) for the verified map):

在回答问题之前先阅读以下内容（路径相对于 SendOS 仓库根目录；经过核实的映射见 [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md)）：

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs` + `Application/Decision/PresentationBudgetEnforcer.cs` — the closed response family and its UI budgets.

  `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Decision/DecisionInteraction.cs` + `Application/Decision/PresentationBudgetEnforcer.cs` —— 封闭的响应类型族及其 UI 预算。

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Approval/ApprovalCheckpoint.cs:237-468` — proposal persisted before approval; binding to tenant/actor/action hash/authority version/expiry; proposer ≠ approver; at-most-once.

  `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/Approval/ApprovalCheckpoint.cs:237-468` —— 提案在审批前持久化；绑定到租户/执行者/动作哈希/权限版本/过期时间；提议者 ≠ 审批者；最多一次。

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` — three declaration sources, published-wins, tenant filtering.

  `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Application/CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` —— 三个声明来源、以已发布版本为准、按租户过滤。

- `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Authority/EffectiveAuthority.cs` + `Application/Authority/AuthoritySources.cs` — the intersection that a capstone approval should be bound to.

  `apps/Send.Agent.Runtime/src/Send.Agent.Runtime.Domain/Authority/EffectiveAuthority.cs` + `Application/Authority/AuthoritySources.cs` —— 结业项目中的审批应当绑定到的那个权限交集。

Answer in `notes/week09-sendos-bridge.md`:

在 `notes/week09-sendos-bridge.md` 中回答：

1. `ApprovalCheckpoint` binds an approval to more than a proposal id. List the fields it checks and mark which ones your `ActionProposal`/approval flow is missing. What attack does each missing field allow?

   `ApprovalCheckpoint` 绑定审批时用到的不只是提案 id。列出它检查的字段，并标出你的 `ActionProposal`/审批流程缺少哪些。每个缺失的字段会让哪种攻击成为可能？

2. `CapabilityCatalogueAssembler` merges **three** sources with published-wins. Your capstone merges two. What would break if you added the third (platform-owned declarations) in the wrong order, and how do the tests in the SendOS repo guard it?

   `CapabilityCatalogueAssembler` 以「已发布版本为准」的方式合并**三个**来源。你的结业项目只合并两个。如果你以错误的顺序加入第三个来源（平台自有的声明），会有什么东西出问题？SendOS 仓库中的测试是如何防范这一点的？

3. `DecisionInteraction` is a closed type family enforced by the type system. Your capstone enforces a closed union at parse time. Name one defect class each approach catches and one each misses.

   `DecisionInteraction` 是由类型系统强制执行的封闭类型族。你的结业项目则在解析时强制执行封闭联合。分别说出每种方法能捕获的一类缺陷和会漏掉的一类缺陷。

## 8. Stretch

**8. 拓展**

1. **Durable suspend/resume (the credible SendOS contribution):** persist proposals and approvals in SQLite; `execute` becomes a two-phase operation; a callback resumes an approval that arrived after a restart; CAS against double-resume. SendOS's `CaseRuntime` is built but unwired — a miniature is a design sketch for a real proposal.

   **持久化的挂起/恢复（一项可信的 SendOS 贡献）：** 把提案和审批持久化到 SQLite；`execute` 变成两阶段操作；由回调恢复在重启之后才到达的审批；用 CAS 防止重复恢复。SendOS 的 `CaseRuntime` 已经构建但尚未接线——一个迷你版本就是一份真实提案的设计草图。

2. **Eval-gated asset promotion:** add `agentlab/capstone/promote.py` where a candidate prompt/asset can only become `published` after an eval threshold and a human approval row. Keep the model's output restricted to `draft`.

   **受评测把关的资产晋级：** 添加 `agentlab/capstone/promote.py`，其中候选的提示词/资产只有在达到评测阈值并有一条人工审批记录之后才能变为 `published`。模型的输出始终限制为 `draft`。

## 9. Reflection

**9. 反思**

1. **Conceptual:** why must the proposal be persisted *before* approval? Describe the failure that appears if it is persisted after.

   **概念层面：** 为什么提案必须在审批*之前*持久化？描述一下如果在审批之后才持久化，会出现什么样的失败。

2. **Architectural:** `platform.py` is one class on purpose. Which responsibilities would you split out first if this were a real service, and which invariants would you test at each new boundary?

   **架构层面：** `platform.py` 被刻意写成一个类。如果这是一个真实的服务，你会首先拆分出哪些职责？在每个新的边界上你会测试哪些不变量？

3. **Transfer:** pick one SendOS mechanism from §7. What does your miniature get right, and what does SendOS do that you deliberately left out — and is that difference about scale, governance, or both?

   **迁移应用：** 从 §7 中选一个 SendOS 机制。你的迷你版本做对了什么？SendOS 做了哪些你刻意省略的事情——这种差异是关于规模、治理，还是两者兼有？
