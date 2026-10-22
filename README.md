# AgentLab

> A test-driven, from-scratch curriculum for learning modern **agent-system engineering** — built to run alongside a real enterprise agent platform, not a toy tutorial.
>
> 一套测试驱动、从零开始的课程，用于学习现代 **Agent 系统工程**——它是为配合一个真实的企业级 Agent 平台而设计的，而不是玩具式教程。

**Owner:** Terrence (Yaqi) Chen · **Started:** 2026-10-18 · **Plan:** 9 weeks × 8–12 h/week

**负责人：** Terrence (Yaqi) Chen · **开始日期：** 2026-10-18 · **计划：** 9 周 × 每周 8–12 小时

---

## What this is

**这是什么**

This repository is two things at once:

这个仓库同时是两样东西：

1. **A working Python codebase** (`agentlab/`) that you grow one capability at a time: provider adapter → agent loop → structured output → context & memory → MCP → orchestration → evals → guardrails → capstone.

   **一个可运行的 Python 代码库**（`agentlab/`），你一次增加一项能力：模型提供商（provider）适配器 → Agent 循环 → 结构化输出 → 上下文与记忆 → MCP → 编排 → 评测（eval）→ 护栏 → 结业项目（capstone）。

2. **A curriculum** (`docs/plan/`, `labs/`, `tests/`) that tells you exactly what to build, in what order, and how to know you are done.

   **一套课程**（`docs/plan/`、`labs/`、`tests/`），它明确告诉你要构建什么、按什么顺序构建，以及如何判断你已经完成。

Every week ships a runnable artifact and a test suite that **defines** the week's deliverable. If `pytest tests/week03 -m week -q` is green, you finished week 3 — no self-assessment required.

每周都会产出一个可运行的成果，以及一个**定义**该周交付物的测试套件。如果 `pytest tests/week03 -m week -q` 通过（变绿），你就完成了第 3 周——无需自我评估。

> The `-m week` marker is required: the default `pytest` run excludes lab tests (they start red on purpose), so `pytest tests/week03 -q` on its own would collect nothing.
>
> `-m week` 标记是必需的：默认的 `pytest` 运行会排除实验（lab）测试（它们故意以失败（红）状态开始），所以单独运行 `pytest tests/week03 -q` 不会收集到任何测试。

```
Week 1  model & provider seam ──►  Week 4  context & memory ──►  Week 7  evals & observability
Week 2  tool calls & agent loop ─►  Week 5  MCP interoperability ► Week 8  security & governance
Week 3  structured output ───────►  Week 6  planning & squads ──► Week 9  capstone: Mini-SendOS
```

---

## Why this shape

**为什么是这种结构**

Most agent tutorials teach framework APIs. That produces people who can wire a demo and cannot debug one. This curriculum is built on four choices:

大多数 Agent 教程教的是框架 API。这样培养出来的人能拼出一个演示，却无法调试它。本课程建立在四个选择之上：

| Choice<br>选择 | Why<br>原因 |
|---|---|
| **From scratch first, frameworks second**<br>**先从零实现，再用框架** | You cannot reason about LangGraph/Agents SDK failure modes until you have written the loop yourself. Frameworks appear in weeks 6–9 as *readable* abstractions, not magic.<br>在你亲手写出循环之前，你无法推理 LangGraph/Agents SDK 的失败模式。框架在第 6–9 周才出现，作为*可读懂*的抽象，而不是魔法。 |
| **Tests are the specification**<br>**测试就是规格说明** | Agent code is stochastic; its scaffolding need not be. Deterministic mocks (`MockProvider`) make every lab testable offline, with no API key and no flakiness.<br>Agent 代码是随机的，但它的脚手架不必如此。确定性的 mock（`MockProvider`）让每个实验都能离线测试，无需 API key，也不会出现不稳定的结果。 |
| **Evals from week 7, traces from week 2**<br>**评测从第 7 周开始，trace 从第 2 周开始** | Tracing is how you debug; evals are how you improve. Both are designed in early, not bolted on.<br>追踪是你调试的手段；评测是你改进的手段。两者都在早期就设计进去，而不是事后硬加上去。 |
| **A bridge to your day job**<br>**通往日常工作的桥梁** | Every week maps to a real mechanism in the SendOS codebase (`.NET 8/10`), with optional C# equivalents. See [`docs/sendos/`](docs/sendos/README.md).<br>每周的内容都对应 SendOS 代码库（`.NET 8/10`）中的一个真实机制，并提供可选的 C# 等价实现。参见 [`docs/sendos/`](docs/sendos/README.md)。 |

The full research basis — 5 deep-research reports, ~20k words with citations — lives in [`docs/research/`](docs/research/README.md).

完整的研究基础——5 份深度研究报告，约 2 万词并附有引用——位于 [`docs/research/`](docs/research/README.md)。

**Companion textbook:** [*AI Agents in Depth*](docs/books/ai-agents-in-depth/README.md) by Bojie Li (v2.0, 2026, free/Apache-2.0) — deep theory plus 109 experiments, mapped week-by-week in [CHAPTER-MAP.md](docs/books/ai-agents-in-depth/CHAPTER-MAP.md). It supplies the *why*; this repo supplies the tests, governance and SendOS transfer.

**配套教材：** 李博杰（Bojie Li）所著的 [*AI Agents in Depth*](docs/books/ai-agents-in-depth/README.md)（v2.0，2026，免费/Apache-2.0）——深入的理论加上 109 个实验，在 [CHAPTER-MAP.md](docs/books/ai-agents-in-depth/CHAPTER-MAP.md) 中逐周做了映射。它提供*为什么*；本仓库提供测试、治理以及向 SendOS 的迁移。

---

## Quickstart

**快速开始**

Both task runners expose the same subcommands: `tasks.ps1` on Windows (PowerShell), `tasks.sh` on macOS/Linux (bash or zsh).

两个任务运行器提供相同的子命令：Windows（PowerShell）上用 `tasks.ps1`，macOS/Linux（bash 或 zsh）上用 `tasks.sh`。

**Windows (PowerShell):**

```powershell
# Windows (PowerShell)
# from D:\DevRepo\MyProjects\AgentLearning
.\tasks.ps1 setup        # uv + Python 3.12 + deps + .env + doctor
```

**macOS / Linux:**

```bash
# macOS / Linux
# from the repo root
./tasks.sh setup         # uv + Python 3.12 + deps + .env + doctor
```

Then:

然后：

**Windows (PowerShell):**

```powershell
# Windows (PowerShell)
.\tasks.ps1 doctor       # check toolchain, keys, dirs
.\tasks.ps1 test         # full suite (foundation should be green; week labs start red on purpose)
.\tasks.ps1 week 1       # only week 1's tests
.\tasks.ps1 chat         # week 1 deliverable once implemented
```

**macOS / Linux:**

```bash
# macOS / Linux
./tasks.sh doctor
./tasks.sh test
./tasks.sh week 1
./tasks.sh chat
```

Read **[START-HERE.md](START-HERE.md)** first — it is a 90-minute on-ramp, not a manual.

请先阅读 **[START-HERE.md](START-HERE.md)**——它是一份 90 分钟的入门引导，而不是一本手册。

---

## Repository map

**仓库地图**

| Path<br>路径 | What lives there<br>里面有什么 |
|---|---|
| [`START-HERE.md`](START-HERE.md) | 90-minute onboarding: setup → first failing test → first fix<br>90 分钟入门：环境搭建 → 第一个失败的测试 → 第一次修复 |
| [`tasks.ps1`](tasks.ps1) / [`tasks.sh`](tasks.sh) | Cross-platform task runners: setup, doctor, tests, week N, chat, lint<br>跨平台任务运行器：setup、doctor、tests、week N、chat、lint |
| [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md) | The master 9-week plan: goals, hours, deliverables, exit gates<br>9 周总计划：目标、时长、交付物、结业关卡 |
| [`docs/plan/WEEKLY-RHYTHM.md`](docs/plan/WEEKLY-RHYTHM.md) | How to study efficiently (retrieval practice, timeboxing, spaced repetition)<br>如何高效学习（提取练习、时间盒、间隔重复） |
| [`docs/plan/CHECKPOINTS.md`](docs/plan/CHECKPOINTS.md) | Weekly gates, rubrics, and what "done" means<br>每周关卡、评分标准（rubric），以及“完成”的含义 |
| [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) | Your progress tracker — update it weekly<br>你的进度追踪表——每周更新 |
| [`docs/plan/LEARNER-PROFILE.md`](docs/plan/LEARNER-PROFILE.md) | Your starting point, constraints, goals, and API access<br>你的起点、约束、目标和 API 访问情况 |
| [`docs/concepts/`](docs/concepts/README.md) | Just-in-time concept notes (one per week), with the minimum theory and the failure modes<br>即时概念笔记（每周一篇），包含最少必要的理论和失败模式 |
| [`docs/research/`](docs/research/README.md) | The deep-research reports this curriculum was built from<br>本课程所依据的深度研究报告 |
| [`docs/books/`](docs/books/README.md) | Companion textbooks: assessment, chapter→week map, reading paths<br>配套教材：评估、章节→周映射、阅读路径 |
| [`docs/sendos/`](docs/sendos/README.md) | SendOS concept map, bridge labs, and reading order<br>SendOS 概念地图、桥接实验和阅读顺序 |
| [`docs/internals/IDE-SETUP.md`](docs/internals/IDE-SETUP.md) | Recommended editor + the preconfigured VS Code workspace (`.vscode/`)<br>推荐的编辑器 + 预配置的 VS Code 工作区（`.vscode/`） |
| [`docs/glossary.md`](docs/glossary.md) | Terms you should be able to define without notes<br>你应当能够不看笔记就给出定义的术语 |
| [`agentlab/`](agentlab/) | The package you build: providers, loop, tools, context, mcp, orchestrator, evals, guard, capstone<br>你要构建的包：providers、loop、tools、context、mcp、orchestrator、evals、guard、capstone |
| [`labs/`](labs/) | Weekly lab briefs: goal, specification, acceptance criteria, stretch<br>每周实验简介：目标、规格说明、验收标准、拓展 |
| [`tests/`](tests/) | The specification. `tests/weekNN/` = that week's exit gate<br>规格说明。`tests/weekNN/` = 该周的结业关卡 |
| [`solutions/`](solutions/) | Reference implementations — open only after your tests pass<br>参考实现——只有在你的测试通过后才打开 |
| [`projects/`](projects/) | Capstone and portfolio deliverables<br>结业项目和作品集交付物 |
| [`dotnet/`](dotnet/README.md) | C# bridge labs: provider/SSE/retry and typed-decision equivalents, mirroring weeks 1 and 3<br>C# 桥接实验：provider/SSE/重试以及类型化决策的等价实现，对应第 1 周和第 3 周 |
| [`scripts/`](scripts/) | Repo utilities: internal link checker, capstone demo<br>仓库工具：内部链接检查器、结业项目演示 |
| [`templates/`](templates/) | Weekly review, lab notes, ADR, portfolio write-up templates<br>每周回顾、实验笔记、ADR、作品集总结文章的模板 |

---

## The 9 weeks

**9 周安排**

| Week<br>周 | Theme<br>主题 | You build<br>你要构建 | Hours<br>小时 |
|---|---|---|---|
| 0 | Setup & baseline<br>环境搭建与基线 | Working env; first API call; token/cost accounting<br>可用的环境；第一次 API 调用；token/成本核算 | 3 |
| 1 | **The model, demystified**<br>**揭开模型的神秘面纱** | Raw HTTP + SSE + retries + provider seam (`agentlab/providers/`)<br>原始 HTTP + SSE + 重试 + provider 接缝（`agentlab/providers/`） | 8–10 |
| 2 | **Tools & the agent loop**<br>**工具与 Agent 循环** | Tool registry, ReAct loop, budgets, step traces, terminal agent<br>工具注册表、ReAct 循环、预算、步骤 trace、终端 Agent | 10–12 |
| 3 | **Structured output**<br>**结构化输出** | Schema-validated typed decisions, repair loop, prompt versioning, cassettes<br>经 schema 校验的类型化决策、修复循环、提示词版本管理、cassette（录制回放） | 8–10 |
| 4 | **Context & memory**<br>**上下文与记忆** | Token budgeting, compaction, from-scratch vector search, episodic memory<br>token 预算、压缩（compaction）、从零实现的向量检索、情景记忆 | 10–12 |
| 5 | **MCP** | MCP server + client over stdio; tool discovery into your loop; trust model<br>基于 stdio 的 MCP 服务器 + 客户端；把发现的工具接入你的循环；信任模型 | 8–10 |
| 6 | **Planning & squads**<br>**规划与小队** | Orchestrator + specialists, typed plans, isolated contexts, approval checkpoint<br>编排者 + 专员 Agent（specialist）、类型化计划、隔离的上下文、审批检查点 | 10–12 |
| 7 | **Evals & observability**<br>**评测与可观测性** | Trace store, eval harness, calibrated LLM judge, CI regression gate, dashboard<br>trace 存储、评测 harness（运行框架）、经过校准的 LLM 评审、CI 回归关卡、仪表盘 | 8–10 |
| 8 | **Security & governance**<br>**安全与治理** | Injection defenses, sandboxed tools, authority checks, audit log, model routing<br>注入防御、沙箱化工具、权限检查、审计日志、模型路由 | 8–10 |
| 9 | **Capstone: Mini-SendOS**<br>**结业项目：Mini-SendOS** | Full mini platform + web UI + eval report + architecture write-up<br>完整的迷你平台 + Web UI + 评测报告 + 架构总结文章 | 12–16 |
| 10 | Buffer / consolidation<br>缓冲 / 巩固 | Re-derive the loop from memory, portfolio, interviews<br>凭记忆重新推导循环、作品集、面试 | 4–6 |

Total: **~90–110 hours**. Details, objectives and exit criteria: [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md).

总计：**约 90–110 小时**。详细内容、目标和结业标准见：[`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md)。

---

## How the learning loop works

**学习循环如何运作**

Each week has four artifacts, in this order:

每周有四个产物，按以下顺序：

1. **Brief** — `labs/weekNN-*/README.md`: concept, specification, acceptance criteria, hints, stretch.

   **简介**——`labs/weekNN-*/README.md`：概念、规格说明、验收标准、提示、拓展。

2. **Failing tests** — `tests/weekNN/`: read them before coding. They are the contract.

   **失败的测试**——`tests/weekNN/`：在写代码之前先阅读它们。它们就是契约。

3. **Build** — write the code in `agentlab/` (or the week's lab directory).

   **构建**——在 `agentlab/`（或该周的实验目录）中编写代码。

4. **Review** — tests green → write the weekly review from [`templates/weekly-review.md`](templates/weekly-review.md) → add 5 flashcards → update [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md).

   **回顾**——测试通过（变绿）→ 根据 [`templates/weekly-review.md`](templates/weekly-review.md) 撰写每周回顾 → 添加 5 张闪卡 → 更新 [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md)。

Rules that keep this honest:

让这一切保持诚实的规则：

- **Do not read `solutions/` until your tests pass.** Then read it and diff your design against it.

  **在你的测试通过之前，不要阅读 `solutions/`。** 通过之后再阅读它，并把你的设计与之对比。

- **Never copy a tutorial without a test.** If you cannot test it, you do not understand it yet.

  **绝不在没有测试的情况下照抄教程。** 如果你无法测试它，说明你还没有理解它。

- **Every real model call goes through `agentlab.budget.Budget`.** No unbounded loops, ever.

  **每一次真实的模型调用都要经过 `agentlab.budget.Budget`。** 永远不要有无界循环。

- **One commit per lab step.** The git history is part of the portfolio.

  **每个实验步骤一次提交。** git 历史本身就是作品集的一部分。

- **Explain it before you ship it.** The weekly review has a "explain to a colleague in 150 words" section. If you cannot, re-read.

  **交付之前先讲清楚。** 每周回顾里有一个“用 150 个词向同事解释”的部分。如果你做不到，就重新读一遍。

---

## SendOS bridge (your day job)

**SendOS 桥接（你的日常工作）**

SendOS already contains a sophisticated agent platform: a decision-first reasoning runtime, capability registry, model adapter, governed assets, append-only outcome traces, and a trace→learning loop. This curriculum does not repeat it — it lets you **rebuild the interesting mechanisms in miniature** so the real implementation stops being opaque.

SendOS 已经包含一个成熟的 Agent 平台：决策优先的推理运行时、能力注册表、模型适配器、受治理的资产、仅追加的结果 trace，以及 trace→学习的闭环。本课程不会重复它——而是让你**以缩微形式重建其中有意思的机制**，从而让真实的实现不再是黑箱。

High-value pairings (details in [`docs/sendos/BRIDGE.md`](docs/sendos/BRIDGE.md)):

高价值的对应关系（详见 [`docs/sendos/BRIDGE.md`](docs/sendos/BRIDGE.md)）：

| You build (Python)<br>你构建的（Python） | SendOS equivalent (C#)<br>SendOS 中的对应物（C#） |
|---|---|
| Week 1 provider seam<br>第 1 周 provider 接缝 | `Send.Model.Adapter` provider adapters, budget-aware routed completion<br>`Send.Model.Adapter` 提供商适配器、感知预算的路由式补全 |
| Week 3 typed decision + repair<br>第 3 周类型化决策 + 修复 | `IStructuredCompletionHandler`, `DecisionInteraction`, presentation budgets<br>`IStructuredCompletionHandler`、`DecisionInteraction`、展示预算 |
| Week 6 orchestrator + approval gate<br>第 6 周编排者 + 审批关卡 | Decision-first runtime, `ApprovalCheckpoint`, authoritative execution<br>决策优先的运行时、`ApprovalCheckpoint`、权威执行 |
| Week 7 trace → eval<br>第 7 周 trace → 评测 | `Outcome_Trace`, 5-dimension `Evaluator`, trace→candidate learning loop<br>`Outcome_Trace`、5 维度 `Evaluator`、trace→候选的学习闭环 |
| Week 8 authority + audit<br>第 8 周权限 + 审计 | `EffectiveAuthority` nine-source intersection, governance sandwich<br>`EffectiveAuthority` 九源交集、治理“三明治” |

---

## Requirements

**环境要求**

- Windows 11 + PowerShell (Windows PowerShell 5.1 works; PowerShell 7 recommended), or macOS/Linux with bash or zsh. Both platforms use `uv` for Python; the task runners are `tasks.ps1` (Windows) and `tasks.sh` (macOS/Linux).

  Windows 11 + PowerShell（Windows PowerShell 5.1 可用；推荐 PowerShell 7），或带 bash 或 zsh 的 macOS/Linux。两个平台都使用 `uv` 管理 Python；任务运行器分别是 `tasks.ps1`（Windows）和 `tasks.sh`（macOS/Linux）。

- Python 3.12 (installed automatically by `uv`)

  Python 3.12（由 `uv` 自动安装）

- At least one provider key: **DeepSeek** or **OpenAI** (both configured in `.env.example`)

  至少一个提供商的 key：**DeepSeek** 或 **OpenAI**（两者都已在 `.env.example` 中配置）

- ~$2–5 of model spend for the whole curriculum (most labs run on mocks)

  整个课程约 2–5 美元的模型花费（大多数实验运行在 mock 上）

- Optional: .NET 10 SDK for the C# bridge labs in [`dotnet/`](dotnet/README.md)

  可选：.NET 10 SDK，用于 [`dotnet/`](dotnet/README.md) 中的 C# 桥接实验

---

## Status

**状态**

- [x] Foundation: package skeleton, config, tracing, budgets, mock provider, tool registry — 30 tests green

  基础：包骨架、配置、追踪、预算、mock 提供商、工具注册表——30 个测试通过

- [x] All 9 lab scaffolds: starter stubs, failing specifications, reference solutions, lab briefs — **563 lab tests**, each independently verified red → green → restored

  全部 9 个实验的脚手架：起始桩代码、失败的规格说明、参考解答、实验简介——**563 个实验测试**，每个都独立验证过 失败 → 通过 → 恢复

- [x] Research base (5 reports, ~20k words), companion textbook integrated with a week-by-week chapter map, learning plan, concept notes, glossary, quizzes, flashcards

  研究基础（5 份报告，约 2 万词）、已整合并附逐周章节映射的配套教材、学习计划、概念笔记、术语表、测验、闪卡

- [x] SendOS bridge docs + C# bridge labs (dotnet build: 0 warnings, 0 errors; both self-test suites pass)

  SendOS 桥接文档 + C# 桥接实验（dotnet build：0 个警告，0 个错误；两个自测套件都通过）

- [x] Repo integrity: 0 broken internal links, ruff clean, CI workflow in place

  仓库完整性：0 个失效的内部链接，ruff 检查干净，CI 工作流已就位

- [ ] Week 1 lab — **this is your next action**

  第 1 周实验——**这是你的下一步行动**

Each lab was verified independently: the starter fails for the intended reason, the reference solution passes, and the tree is restored to the learner state. No lab test touches the network.

每个实验都经过独立验证：起始代码按预期的原因失败，参考解答通过，并且代码树会恢复到学习者状态。没有任何实验测试会访问网络。

See [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) for the live tracker you fill in.

参见 [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md)，这是由你来填写的实时进度追踪表。

---

## License

**许可证**

MIT — this is a personal learning repository. Research reports cite their sources; third-party content remains under its own license.

MIT——这是一个个人学习仓库。研究报告均注明了出处；第三方内容仍遵循其各自的许可证。
