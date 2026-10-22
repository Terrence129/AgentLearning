# Learning TODO — AgentLab, from scaffold to mastery

**学习待办 — AgentLab，从脚手架到精通**

**Created:** 2026-10-19 (Monday) · **Plan:** [`LEARNING-PLAN.md`](LEARNING-PLAN.md) · **Gates:** [`CHECKPOINTS.md`](CHECKPOINTS.md) · **Rhythm:** [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)

**创建日期：** 2026-10-19（周一）· **计划：** [`LEARNING-PLAN.md`](LEARNING-PLAN.md) · **关卡：** [`CHECKPOINTS.md`](CHECKPOINTS.md) · **节奏：** [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)

**Verified starting state when this file was created**

**创建本文件时核实的起始状态**

| Check<br>检查项 | Result<br>结果 |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Foundation suite (`pytest -q`)<br>基础测试套件（`pytest -q`） | **30 passed**<br>**30 个通过** |
| Lab suite (`pytest -m week --collect-only`)<br>实验测试套件（`pytest -m week --collect-only`） | **563 collected — all red on purpose**<br>**收集到 563 个——全部刻意处于失败（红）状态** |
| `agentlab doctor`                           | `python ok` · `.env warn` · `provider fail` (expected until week 0 is done)<br>`python ok` · `.env warn` · `provider fail`（在完成第 0 周之前属于预期情况） |
| Git                                           | clean tree on `main` at `aacfdc4`<br>`main` 分支位于 `aacfdc4`，工作区干净 |
| Machine<br>机器 | macOS; repo at `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`; `uv` 0.13.1 + `.venv` ready (phase 0 done)<br>macOS；仓库位于 `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`；`uv` 0.13.1 + `.venv` 已就绪（阶段 0 已完成） |

This file is the **ordered execution list**. It does not replace the curriculum: the lab brief is the build spec, the tests are the definition of done, and [`PROGRESS.md`](PROGRESS.md) is the status tracker. Tick a box only when the evidence exists (a green command, a review note, a commit). Work one week at a time; do not start week N+1 before week N passes all three gates.

本文件是**按顺序执行的清单**。它不取代课程大纲：实验简介是构建规格，测试是"完成"的定义，而 [`PROGRESS.md`](PROGRESS.md) 是状态追踪表。只有在证据存在时（一条通过的命令、一份复盘笔记、一次提交）才打勾。一次只做一周；在第 N 周通过全部三个关卡之前，不要开始第 N+1 周。

**Source of truth**

**权威来源**

| Question<br>问题 | File<br>文件 |
| ----------------------------- | ---------------------------------------------------------------------- |
| What am I building this week?<br>这周我要构建什么？ | [`labs/weekNN-*/README.md`](../../labs/)                              |
| What does "done" mean?<br>"完成"意味着什么？ | [`tests/weekNN/`](../../tests/) + [`CHECKPOINTS.md`](CHECKPOINTS.md) |
| What theory do I need first?<br>我需要先掌握哪些理论？ | [`docs/concepts/`](../concepts/README.md) — one note per week<br>[`docs/concepts/`](../concepts/README.md) — 每周一篇笔记 |
| How do I spend the hours?<br>这些时间怎么分配？ | [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)                                |
| Where do I record evidence?<br>证据记录在哪里？ | [`PROGRESS.md`](PROGRESS.md) + `notes/weekNN-review.md`             |
| Where is the sequence?<br>顺序在哪里？ | this file<br>本文件 |

> **Today is 2026-10-19, the Monday that starts learning-plan week 1.** Week 0 (setup) was scheduled for 2026-10-18; do it today first — it is only 3–4 hours. If you start later, keep the 7-day cadence() and shift the dates, not the order.
>
> **今天是 2026-10-19，即学习计划第 1 周开始的周一。** 第 0 周（环境搭建）原定在 2026-10-18；今天先把它做完——只需要 3–4 小时。如果你开始得更晚，就保持 7 天的节奏，顺延日期，而不是调换顺序。

---

## 0. Non-negotiable rules (all ten weeks)

**0. 不可妥协的规则（全部十周）**

- [X] **Tests are the contract.** Run the suite, read the failing test names and docstrings, then ask for help. Never read `solutions/` until your own tests are green.

  **测试就是契约。** 先运行测试套件，阅读失败测试的名称和文档字符串，然后再求助。在你自己的测试通过之前，绝不要阅读 `solutions/`。

- [X] **One week at a time.** A week is done only when **G + E + T** pass (§4). One grace debt maximum, cleared within 7 days; two weeks of debt means stop and clear.

  **一次只做一周。** 只有当 **G + E + T** 都通过时（§4），这一周才算完成。最多允许一项宽限欠账，并须在 7 天内清掉；欠账累计两周就意味着要停下来先清账。

- [X] **Own only this week's module.** The edit map is in [`SCAFFOLD-CONTRACT.md`](../internals/SCAFFOLD-CONTRACT.md). Do not edit `agentlab/{types,config,trace,budget,pricing,errors,cli}.py`, `agentlab/testing/*`, `agentlab/tools/registry.py`, `tests/test_core.py`, `tests/conftest.py`, `pyproject.toml`, `README.md`, `START-HERE.md`, or the plan docs.

  **只改本周负责的模块。** 修改范围图见 [`SCAFFOLD-CONTRACT.md`](../internals/SCAFFOLD-CONTRACT.md)。不要编辑 `agentlab/{types,config,trace,budget,pricing,errors,cli}.py`、`agentlab/testing/*`、`agentlab/tools/registry.py`、`tests/test_core.py`、`tests/conftest.py`、`pyproject.toml`、`README.md`、`START-HERE.md` 或计划文档。

- [X] **No live model calls in tests.** Use `MockProvider` and cassettes. Any live run must go through `agentlab.budget.Budget`; keep `AGENTLAB_RUN_BUDGET_USD=0.50`.

  **测试中不进行真实模型调用。** 使用 `MockProvider` 和 cassette（录制回放）。任何真实运行都必须经过 `agentlab.budget.Budget`；保持 `AGENTLAB_RUN_BUDGET_USD=0.50`。

- [X] **One commit per step.** `week NN: <what moved>` then `week NN: gate green + review`. The git history is portfolio evidence.

  **每一步一次提交。** 先 `week NN: <what moved>`，然后 `week NN: gate green + review`。Git 历史就是作品集的证据。

- [X] **20-minute unstuck rule.** Write what you expected / what happened / what you tried; shrink it to the smallest failing test; ask for a hint, never the answer.

  **20 分钟脱困规则。** 写下你的预期 / 实际发生了什么 / 你尝试过什么；把问题缩小到最小的失败测试；求提示，而不是求答案。

- [X] **70 / 20 / 10.** 70% building, 20% reading, 10% reflection. If reading exceeds 30% of a week, cut it.

  **70 / 20 / 10。** 70% 动手构建，20% 阅读，10% 反思。如果某周阅读超过 30%，就砍掉一些。

- [X] **Stop at the timer**, leaving a written next step.

  **计时器一响就停**，并留下一条书面的下一步。

- [X] **Never paste SendOS source, internal URLs, tenant data, or secrets** into an external model or into this repo. The bridge is abstraction, not copy-paste.

  **绝不要把 SendOS 源码、内部 URL、租户数据或密钥粘贴**到外部模型或本仓库中。对照（bridge）靠的是抽象，而不是复制粘贴。

- [X] **One tracker only:** [`PROGRESS.md`](PROGRESS.md). Do not maintain a second status system.

  **只用一个追踪表：** [`PROGRESS.md`](PROGRESS.md)。不要维护第二套状态系统。

---

## 1. Roadmap at a glance

**1. 路线图一览**

| Phase<br>阶段 | Wk<br>周 | Dates<br>日期 | Theme<br>主题 | You build<br>你要构建的 | Lab tests<br>实验测试数 | Hours<br>小时 |
| ------------------ | --- | --------------------------- | ------------------------------------ | ------------------------------------------------- | --------- | ------ |
| 0                  | 0   | 2026-10-18 (catch up 10-19)<br>2026-10-18（10-19 补做） | Setup & baseline<br>环境搭建与基线 | Working env; one priced live call<br>可用的环境；一次计价的真实调用 | 0         | 3–4   |
| 1 — Foundations<br>1 — 基础 | 1   | 10-19 → 10-25              | Model & provider seam<br>模型与 provider 接缝 | `agentlab/providers/openai_compat.py`           | 43        | 8–10  |
| 1 — Foundations<br>1 — 基础 | 2   | 10-26 → 11-01              | Tools & the agent loop<br>工具与 Agent 循环 | `agentlab/loop/`, `agentlab/tools/builtin.py` | 67        | 10–12 |
| 1 — Foundations<br>1 — 基础 | 3   | 11-02 → 11-08              | Structured output<br>结构化输出 | `agentlab/schemas/`                             | 61        | 8–10  |
| 2 — Capability<br>2 — 能力 | 4   | 11-09 → 11-15              | Context & memory<br>上下文与记忆 | `agentlab/context/`                             | 55        | 10–12 |
| 2 — Capability<br>2 — 能力 | 5   | 11-16 → 11-22              | MCP interoperability<br>MCP 互操作 | `agentlab/mcp/`                                 | 68        | 8–10  |
| 2 — Capability<br>2 — 能力 | 6   | 11-23 → 11-29              | Planning & squads<br>规划与小队（squad） | `agentlab/orchestrator/`                        | 82        | 10–12 |
| 3 — Production<br>3 — 生产 | 7   | 11-30 → 12-06              | Evals & observability<br>评测与可观测性 | `agentlab/evals/`                               | 48        | 8–10  |
| 3 — Production<br>3 — 生产 | 8   | 12-07 → 12-13              | Security & governance<br>安全与治理 | `agentlab/guard/`                               | 93        | 8–10  |
| 3 — Production<br>3 — 生产 | 9   | 12-14 → 12-20              | Capstone: Mini-SendOS<br>结业项目（capstone）：Mini-SendOS | `agentlab/capstone/`, `agentlab/web/`         | 46        | 12–16 |
| 4 — Consolidation<br>4 — 巩固 | 10  | 12-21 → 12-27              | Portfolio, interviews, re-derivation<br>作品集、面试、重新推导 | Evidence, not new code<br>证据，而非新代码 | —        | 4–6   |
| Buffer<br>缓冲 | buf | 12-28 → 2027-01-03         | Overflow / holiday<br>溢出 / 假期 | —                                                | —        | —     |

**The five failure modes this curriculum exists to prevent** (keep them in view all ten weeks): treating the API as magic · an agent loop with no budget or stop condition · unvalidated model output · context that silently rots · a system you cannot evaluate, secure, or audit.

**本课程要防止的五种失败模式**（全部十周都要牢记）：把 API 当成魔法 · 没有预算或停止条件的 Agent 循环 · 未经校验的模型输出 · 悄无声息地腐化的上下文 · 一个你无法评测、保护或审计的系统。

---

## 2. Phase 0 — Environment and baseline (Week 0, ~3–4 h)

**2. 阶段 0 — 环境与基线（第 0 周，约 3–4 小时）**

Do this today. Target state: `doctor` has **no blocking problem**, the foundation is green, the lab suites are red by design, and one live call is priced.

今天就做。目标状态：`doctor` **没有阻塞性问题**，基础测试通过，实验测试套件按设计处于失败（红）状态，并且有一次计价的真实调用。

### 2.1 Install the toolchain

**2.1 安装工具链**

- [X] Install `uv` (macOS / Linux):

  安装 `uv`（macOS / Linux）：

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  exec "$SHELL" -l        # or open a new terminal
  uv --version
  ```

  Windows equivalent: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`.

  Windows 下的等价命令：`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`。

- [X] `uv python install 3.12`
- [X] `uv sync --extra dev` — creates `.venv/` and installs the pinned dev dependencies.

  `uv sync --extra dev` — 创建 `.venv/` 并安装锁定版本的开发依赖。

- [X] Or, one command: `./tasks.sh setup` (Windows: `.\tasks.ps1 setup`) — installs Python, syncs deps, creates `.env`, and runs `doctor`.

  或者一条命令搞定：`./tasks.sh setup`（Windows：`.\tasks.ps1 setup`）——安装 Python、同步依赖、创建 `.env` 并运行 `doctor`。

- [X] Point your editor at `.venv/bin/python` (VS Code: **Python: Select Interpreter**).

  让编辑器指向 `.venv/bin/python`（VS Code：**Python: Select Interpreter**）。

### 2.2 Configure a provider

**2.2 配置模型提供商（provider）**

- [X] `cp .env.example .env`
- [X] Edit `.env`: set `DEFAULT_PROVIDER=deepseek` and a real `DEEPSEEK_API_KEY=sk-...` (or `OPENAI_API_KEY`). No quotes, no spaces. **Never commit `.env`.**

  编辑 `.env`：设置 `DEFAULT_PROVIDER=deepseek` 和一个真实的 `DEEPSEEK_API_KEY=sk-...`（或 `OPENAI_API_KEY`）。不要加引号，不要有空格。**绝不要提交 `.env`。**

- [X] `uv run python -m agentlab.cli doctor` → every row `ok`/`info`, `provider ok`.

  `uv run python -m agentlab.cli doctor` → 每一行都是 `ok`/`info`，并且 `provider ok`。

- [X] `uv run agentlab --help` works.

  `uv run agentlab --help` 可以正常运行。

### 2.3 See the starting line

**2.3 看清起跑线**

- [X] `uv run pytest -q` → **30 passed** (the provided foundation; not your work).

  `uv run pytest -q` → **30 个通过**（提供的基础部分；不是你的工作）。

- [X] `uv run pytest -m week -q` → **563 failed** — the whole curriculum red on purpose.

  `uv run pytest -m week -q` → **563 个失败**——整个课程刻意处于失败（红）状态。

- [X] `uv run pytest tests/week01 -m week -q` → **43 failed**; that is your first lab.

  `uv run pytest tests/week01 -m week -q` → **43 个失败**；这就是你的第一个实验（lab）。

- [X] `uv run agentlab chat` → prints the "Week 1 lab not implemented yet" panel (exit code 3). Correct.

  `uv run agentlab chat` → 打印 "Week 1 lab not implemented yet" 面板（退出码 3）。这是正确的。

### 2.4 Baseline note and ritual

**2.4 基线笔记与仪式**

- [ ] Read [`START-HERE.md`](../../START-HERE.md) §3–5, [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md), [`CHECKPOINTS.md`](CHECKPOINTS.md), and weeks 0–1 of [`LEARNING-PLAN.md`](LEARNING-PLAN.md).

  阅读 [`START-HERE.md`](../../START-HERE.md) §3–5、[`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)、[`CHECKPOINTS.md`](CHECKPOINTS.md)，以及 [`LEARNING-PLAN.md`](LEARNING-PLAN.md) 的第 0–1 周。

- [ ] Skim the repository map in [`README.md`](../../README.md) once, so you know where everything lives.

  把 [`README.md`](../../README.md) 中的仓库地图浏览一遍，知道各部分放在哪里。

- [ ] Make **one live call** with a throwaway script or `curl`. Record model, input/output tokens, wall-clock latency, and cost (use `agentlab.pricing.estimate_cost`) in `notes/week00-baseline.md`.

  用一个临时脚本或 `curl` 做**一次真实调用**。在 `notes/week00-baseline.md` 中记录模型、输入/输出 token、实际耗时（延迟）和成本（使用 `agentlab.pricing.estimate_cost`）。

- [ ] Write your baseline answers, then correct them: *What is a token? Why does streaming exist? What can go wrong in a retry?*

  写下你的基线答案，然后再纠正它们：*什么是 token？为什么需要流式输出？重试时可能出什么问题？*

- [ ] Fill the week 0 row of [`PROGRESS.md`](PROGRESS.md); put three sessions in your calendar (Tue 20:00, Thu 20:00, Sat 09:00–13:00).

  填写 [`PROGRESS.md`](PROGRESS.md) 中第 0 周那一行；在日历中安排三次学习时段（周二 20:00、周四 20:00、周六 09:00–13:00）。

- [ ] `cp templates/weekly-review.md notes/week01-review.md` and leave it open all week.

  执行 `cp templates/weekly-review.md notes/week01-review.md`，并让它整周保持打开。

- [ ] Commit: `git add -A && git commit -m "week 0: environment + baseline"`.

  提交：`git add -A && git commit -m "week 0: environment + baseline"`。

**Week 0 gate:** `doctor` clean · foundation 30 green · one priced live call recorded.

**第 0 周关卡：** `doctor` 无问题 · 基础测试 30 个通过 · 记录了一次计价的真实调用。

> **macOS vs Windows:** there are two equivalent task runners at the repo root — [`tasks.ps1`](../../tasks.ps1) for Windows PowerShell and [`tasks.sh`](../../tasks.sh) for macOS/Linux bash or zsh. They expose the same subcommands. On this machine use `./tasks.sh <task>` or the `uv` commands in §3; they are exactly what the task runners wrap. If you install PowerShell 7 (`pwsh`), `./tasks.ps1 week 1` also works, but it is not required.
>
> **macOS 与 Windows：** 仓库根目录下有两个等价的任务运行器——用于 Windows PowerShell 的 [`tasks.ps1`](../../tasks.ps1) 和用于 macOS/Linux bash 或 zsh 的 [`tasks.sh`](../../tasks.sh)。它们提供相同的子命令。在这台机器上使用 `./tasks.sh <task>` 或 §3 中的 `uv` 命令；任务运行器封装的正是这些命令。如果你安装了 PowerShell 7（`pwsh`），`./tasks.ps1 week 1` 也能用，但并非必需。

---

## 3. Command reference

**3. 命令参考**

Default pytest behaviour excludes lab tests (`addopts = -m "not week"`); the `-m week` flag is required for any week test.

pytest 默认会排除实验测试（`addopts = -m "not week"`）；运行任何周测试都必须加 `-m week` 标志。

| Purpose<br>用途 | macOS (this checkout)<br>macOS（当前检出） | Windows (`tasks.ps1`)<br>Windows（`tasks.ps1`） |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Setup<br>环境搭建 | `./tasks.sh setup` or `uv sync --extra dev`<br>`./tasks.sh setup` 或 `uv sync --extra dev` | `.\tasks.ps1 setup`      |
| Any task runner command<br>任意任务运行器命令 | `./tasks.sh <task>` (same subcommands)<br>`./tasks.sh <task>`（子命令相同） | `.\tasks.ps1 <task>`     |
| Doctor<br>环境诊断 | `uv run python -m agentlab.cli doctor`                                                                      | `.\tasks.ps1 doctor`     |
| Foundation tests<br>基础测试 | `uv run pytest -q`                                                                                          | `.\tasks.ps1 test`       |
| One week's tests<br>单周测试 | `uv run pytest tests/week01 -m week -q`                                                                     | `.\tasks.ps1 week 1`     |
| All lab tests<br>全部实验测试 | `uv run pytest -m week -q`                                                                                  | `.\tasks.ps1 labs`       |
| One test / one file<br>单个测试 / 单个文件 | `uv run pytest tests/week01/test_retry.py -m week -vv`                                                      | —                         |
| Interactive chat<br>交互式聊天 | `uv run agentlab chat`                                                                                      | `.\tasks.ps1 chat`       |
| Lint<br>代码检查 | `uv run ruff check .`                                                                                       | `.\tasks.ps1 lint`       |
| Format<br>格式化 | `uv run ruff format .`                                                                                      | `.\tasks.ps1 fmt`        |
| What CI runs<br>CI 运行的内容 | `uv run ruff check . && uv run ruff format --check . && uv run pytest -q`                                   | `.\tasks.ps1 check`      |
| Internal link check<br>内部链接检查 | `uv run python scripts/check_links.py`                                                                      | same<br>同上 |
| Capstone demo<br>结业项目演示 | `uv run python scripts/demo_capstone.py`                                                                    | `.\tasks.ps1`-equivalent<br>`.\tasks.ps1` 的等价命令 |
| C# bridge<br>C# 对照 | `dotnet build dotnet/AgentBridgeLabs.sln` then `dotnet run --project dotnet/ProviderBridge -- --selftest`<br>`dotnet build dotnet/AgentBridgeLabs.sln`，然后 `dotnet run --project dotnet/ProviderBridge -- --selftest` | same<br>同上 |
| Solution (last resort)<br>参考答案（最后手段） | `cp -R solutions/week01/. .` then `git restore .` to undo<br>`cp -R solutions/week01/. .`，然后用 `git restore .` 撤销 | `.\tasks.ps1 solution 1` |

**Environment variables worth knowing**

**值得了解的环境变量**

| Variable<br>变量 | Default<br>默认值 | Meaning<br>含义 |
| ---------------------------------------------- | ------------------------- | ----------------------------------------------------- |
| `DEFAULT_PROVIDER`                           | `deepseek`              | `deepseek` \| `openai` \| a `COMPAT_*` provider<br>`deepseek` \| `openai` \| 某个 `COMPAT_*` 提供商 |
| `DEEPSEEK_API_KEY` / `OPENAI_API_KEY`      | —                        | provider keys; placeholders are rejected<br>提供商密钥；占位符会被拒绝 |
| `AGENTLAB_RUN_BUDGET_USD`                    | `0.50`                  | hard ceiling per lab run — leave it on<br>每次实验运行的硬性上限——保持开启 |
| `AGENTLAB_ALLOW_NETWORK`                     | `0`                     | `1` enables `-m network` tests<br>`1` 启用 `-m network` 测试 |
| `AGENTLAB_DATA_DIR` / `AGENTLAB_TRACE_DIR` | `./data` / `./traces` | runtime artifacts<br>运行时产物 |

---

## 4. The weekly loop and the gate

**4. 每周循环与关卡**

Copy this block into `notes/weekNN-review.md`, or keep it open on Saturday.

把这个清单块复制到 `notes/weekNN-review.md` 中，或者在周六让它保持打开。

### Session A — Build A (Tue, 90–120 min)

**时段 A — 构建 A（周二，90–120 分钟）**

- [ ] Five flashcards from an older week, closed book.

  闭卷复习五张旧周的闪卡。

- [ ] Read the week's concept note (25 min): `docs/concepts/NN-*.md`.

  阅读本周的概念笔记（25 分钟）：`docs/concepts/NN-*.md`。

- [ ] Skim the lab brief: `labs/weekNN-*/README.md`.

  浏览实验简介：`labs/weekNN-*/README.md`。

- [ ] Run the week's tests; read the first failing test's name and docstring.

  运行本周的测试；阅读第一个失败测试的名称和文档字符串。

- [ ] Write this block's target in one sentence.

  用一句话写下本时段的目标。

- [ ] Implement the smallest failing test; stop at the timer with a written next step.

  实现最小的失败测试；计时器一响就停，并写下下一步。

### Session B — Build B (Thu, 90–120 min)

**时段 B — 构建 B（周四，90–120 分钟）**

- [ ] Five flashcards.

  五张闪卡。

- [ ] Continue from the written next step.

  从写下的下一步继续。

- [ ] Make the lab **artifact** run end-to-end — tests green is not the same as the deliverable working.

  让本实验的**产出物**端到端跑起来——测试通过不等于交付物可用。

- [ ] Close-out log: what moved, what is next, what confused me.

  收尾日志：推进了什么、下一步是什么、什么让我困惑。

### Session C — Deep session (Sat, 3–4 h)

**时段 C — 深度时段（周六，3–4 小时）**

- [ ] Integration and remaining tests.

  集成与剩余测试。

- [ ] Theory: 90 min — one must-read from the week, not a reading list.

  理论：90 分钟——本周的一篇必读材料，而不是一张阅读清单。

- [ ] SendOS bridge: 30–45 min — three questions, three bullets, one open question.

  SendOS 对照：30–45 分钟——三个问题、三条要点、一个开放问题。

- [ ] Run the gate (below).

  运行关卡（见下文）。

- [ ] Weekly review + five flashcards + [`PROGRESS.md`](PROGRESS.md) + commit.

  每周复盘 + 五张闪卡 + [`PROGRESS.md`](PROGRESS.md) + 提交。

- [ ] Put next week's three sessions in the calendar.

  在日历中安排下周的三次学习时段。

### The gate (all three, every week)

**关卡（每周三项全过）**

- [ ] **G — Green:** `uv run pytest tests/weekNN -m week -q` passes, no skips/xfails, offline, under ~10 s. Foundation (`uv run pytest -q`) still green; `uv run ruff check <owned path>` clean.

  **G — 通过（Green）：** `uv run pytest tests/weekNN -m week -q` 通过，没有 skip/xfail，离线运行，耗时约 10 秒以内。基础测试（`uv run pytest -q`）依然通过；`uv run ruff check <owned path>` 无问题。

- [ ] **E — Explain:** quiz `docs/plan/quizzes/weekNN.md` closed book **≥ 8/10**, plus a **150-word teach-back without notes** that names the mechanism, one failure mode it prevents, and where it lives in the code.

  **E — 讲解（Explain）：** 闭卷完成测验 `docs/plan/quizzes/weekNN.md`，**≥ 8/10**，外加一份**不看笔记写出的 150 词复述讲解（teach-back）**，要说出机制本身、它防止的一种失败模式，以及它在代码中的位置。

- [ ] **T — Transfer:** SendOS bridge note naming real C# types/files, two concrete differences, one thing you would change, and one open question you cannot answer yet.

  **T — 迁移（Transfer）：** SendOS 对照笔记，要点名真实的 C# 类型/文件、两处具体差异、一处你会改动的地方，以及一个你暂时还答不上来的开放问题。

- [ ] **Artifact:** the week's deliverable runs offline where the brief allows, emits trace events, and records cost/latency.

  **产出物：** 在简介允许的情况下，本周交付物可离线运行、发出 trace 事件，并记录成本/延迟。

- [ ] **Commit:** `git commit -m "week NN: gate green + review"`.

  **提交：** `git commit -m "week NN: gate green + review"`。

**Minimum viable week (4–5 h, when internship/coursework explodes):** Session 1 = brief + first failing test; Session 2 = finish until green; Gate = quiz ×10 + teach-back + five cards. Skip theory, bridge, and stretch — but record them as debt. A partial week with a record beats a skipped week with none.

**最小可行周（4–5 小时，实习/课业爆炸时）：** 时段 1 = 简介 + 第一个失败测试；时段 2 = 一直做到通过；关卡 = 测验 ×10 + 复述讲解 + 五张卡片。跳过理论、对照和拓展——但要把它们记为欠账。有记录的不完整一周，胜过没有任何记录的跳过一周。

**If a gate fails:** diagnose *which* gate failed using [`CHECKPOINTS.md`](CHECKPOINTS.md) §4. Do not "study more" as a reflex. One grace debt maximum, cleared within 7 days; two consecutive debt weeks means stop and clear.

**如果某个关卡未通过：** 用 [`CHECKPOINTS.md`](CHECKPOINTS.md) §4 诊断究竟是*哪个*关卡没过。不要条件反射式地"多学一点"。最多允许一项宽限欠账，并须在 7 天内清掉；连续两周欠账就意味着要停下来先清账。

---

## 5. The nine labs

**5. 九个实验**

Each week below lists: the only files you own, what to read first, the tests that define done, the build checklist, the **artifact** (which tests do not prove), the three gates, the stretch, and the traps.

下面每一周都列出：你唯一负责的文件、要先读什么、定义完成的测试、构建清单、**产出物**（测试无法证明的部分）、三个关卡、拓展任务，以及陷阱。

### Week 1 — The model, demystified (provider seam)

**第 1 周 — 揭开模型的神秘面纱（provider 接缝）**

**2026-10-19 → 10-25 · 8–10 h · Owned:** `agentlab/providers/openai_compat.py` only.

**2026-10-19 → 10-25 · 8–10 小时 · 负责：** 仅 `agentlab/providers/openai_compat.py`。

**Read first:** [concept note 01](../concepts/01-agent-loop.md) · [lab brief](../../labs/week01-provider/README.md) · the OpenAI and DeepSeek chat-completions docs side by side.

**先读：** [概念笔记 01](../concepts/01-agent-loop.md) · [实验简介](../../labs/week01-provider/README.md) · 把 OpenAI 和 DeepSeek 的 chat-completions 文档并排对照着读。

**Tests (43):** [`test_request_mapping.py`](../../tests/week01/test_request_mapping.py) · [`test_response_parsing.py`](../../tests/week01/test_response_parsing.py) · [`test_retry.py`](../../tests/week01/test_retry.py) · [`test_streaming.py`](../../tests/week01/test_streaming.py)

**Build**

**构建**

- [ ] `_build_payload` — model fallback; message mapping; omit unset optionals; omit empty tools; `stream_options={"include_usage": True}` when streaming; `extra` merged **last**; never mutate the request.

  `_build_payload` — 模型回退；消息映射；省略未设置的可选字段；省略空的工具列表；流式输出时设置 `stream_options={"include_usage": True}`；`extra` **最后**合并；绝不修改原请求。

- [ ] `_parse_response` — first choice → assistant `Message` (text and/or tool calls); JSON arguments parsed; `Usage` including cached tokens; `finish_reason`; raw payload retained; malformed arguments or missing `choices` → `ProviderError`.

  `_parse_response` — 第一个 choice → 助手 `Message`（文本和/或工具调用）；解析 JSON 参数；`Usage` 包括缓存的 token；`finish_reason`；保留原始 payload；参数格式错误或缺少 `choices` → `ProviderError`。

- [ ] `complete` — POST `{base_url}/chat/completions`; at most `max_retries + 1` attempts; retry 429/5xx/transport; exact numeric `Retry-After`, else exponential backoff with jitter; no retry on other 4xx; every failure becomes `ProviderError`; never leak `httpx` types.

  `complete` — POST `{base_url}/chat/completions`；最多尝试 `max_retries + 1` 次；对 429/5xx/传输错误重试；严格遵循数值型的 `Retry-After`，否则使用带抖动（jitter）的指数退避；其他 4xx 不重试；每个失败都转为 `ProviderError`；绝不泄露 `httpx` 类型。

- [ ] `stream` — SSE `data:` lines only; ignore comments/`event:`; `[DONE]` terminates; tolerate frames fragmented across chunks; forward tool-call argument fragments verbatim; emit `text` / `tool_call_delta` / `usage` and exactly one `done`; mid-stream error frames raise; no retries mid-stream.

  `stream` — 只处理 SSE 的 `data:` 行；忽略注释/`event:`；`[DONE]` 表示结束；容忍跨 chunk 被拆碎的帧；原样转发工具调用参数片段；发出 `text` / `tool_call_delta` / `usage` 以及恰好一个 `done`；流中途的错误帧要抛出异常；流中途不重试。

- [ ] Prove the equivalence contract: `assemble_stream(provider.stream(req))` equals `provider.complete(req)` for the same logical response.

  证明等价契约：对同一个逻辑响应，`assemble_stream(provider.stream(req))` 等于 `provider.complete(req)`。

- [ ] **Artifact:** `uv run agentlab chat` streams one turn and prints per-turn tokens/cost; `/cost`, `/reset`, `/quit` work; compare `--stream` vs `--no-stream` on the same prompt.

  **产出物：** `uv run agentlab chat` 流式输出一轮对话，并打印每轮的 token/成本；`/cost`、`/reset`、`/quit` 可用；用同一个提示词比较 `--stream` 与 `--no-stream`。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week01 -m week -q` green · `uv run pytest -q` (30) green · `uv run ruff check agentlab/providers/openai_compat.py`.

  **G：** `uv run pytest tests/week01 -m week -q` 通过 · `uv run pytest -q`（30 个）通过 · `uv run ruff check agentlab/providers/openai_compat.py`。

- [ ] **E:** quiz 1 ≥ 8/10; teach-back: *why retries, SSE delta assembly and usage accounting live in the provider adapter*.

  **E：** 测验 1 ≥ 8/10；复述讲解：*为什么重试、SSE 增量（delta）拼装和用量统计都放在 provider 适配器里*。

- [ ] **T:** `Send.Model.Adapter` — three duties your seam shares, two it lacks (budget-aware routing, structured completion), one open question.

  **T：** `Send.Model.Adapter` — 你的接缝与它共有的三项职责、你的接缝所缺少的两项（感知预算的路由、结构化补全），以及一个开放问题。

- [ ] Commit `week 1: provider seam green` and `week 1: review + flashcards`.

  提交 `week 1: provider seam green` 和 `week 1: review + flashcards`。

**Stretch (only after the gate):** an Anthropic adapter behind the same `Provider` protocol — different system-prompt placement, content blocks, tool schema.

**拓展（仅在通过关卡之后）：** 在同一个 `Provider` 协议后面实现一个 Anthropic 适配器——系统提示词的位置、内容块和工具 schema 都不同。

**Watch-outs:** `extra` wins last · no mutation · never retry terminal 4xx · fragmented SSE frames · don't treat a `finish_reason: "length"` response as a complete answer.

**注意事项：** `extra` 最后生效 · 不修改请求 · 绝不重试终止性的 4xx · 被拆碎的 SSE 帧 · 不要把 `finish_reason: "length"` 的响应当成完整答案。

---

### Week 2 — Tools and the agent loop (the most important week)

**第 2 周 — 工具与 Agent 循环（最重要的一周）**

**2026-10-26 → 11-01 · 10–12 h · Owned:** `agentlab/loop/` and `agentlab/tools/builtin.py`.

**2026-10-26 → 11-01 · 10–12 小时 · 负责：** `agentlab/loop/` 和 `agentlab/tools/builtin.py`。

**Read first:** [concept note 02](../concepts/02-tool-design.md) · [lab brief](../../labs/week02-agent-loop/README.md) · research 01 §1–2 · Anthropic *Building effective agents*.

**先读：** [概念笔记 02](../concepts/02-tool-design.md) · [实验简介](../../labs/week02-agent-loop/README.md) · 研究报告 01 §1–2 · Anthropic 的 *Building effective agents*。

**Tests (67):** [`test_builtin_tools.py`](../../tests/week02/test_builtin_tools.py) · [`test_loop.py`](../../tests/week02/test_loop.py) · [`test_runner.py`](../../tests/week02/test_runner.py) · [`test_stop.py`](../../tests/week02/test_stop.py)

**Build**

**构建**

- [ ] `safe_eval` — whitelisted AST only: literals, parentheses, unary, `+ - * / // % **`; reject names/calls/attributes and abusive exponents; division by zero becomes a clear error.

  `safe_eval` — 只允许白名单内的 AST：字面量、括号、一元运算、`+ - * / // % **`；拒绝名称/调用/属性访问以及滥用的指数运算；除以零要变成清晰的错误。

- [ ] `FileSandbox` — `resolve`/`read_text`/`list_dir`/`write_text`/`search_text`; every path resolves under one root; absolute paths and traversal rejected; writes marked `is_write=True`; missing files are observations.

  `FileSandbox` — `resolve`/`read_text`/`list_dir`/`write_text`/`search_text`；每个路径都解析到同一个根目录之下；拒绝绝对路径和目录穿越；写操作标记 `is_write=True`；文件不存在作为观察结果返回。

- [ ] `build_builtin_tools` — `calculator`, `read_file`, `list_dir`, `write_file`, `search_text`; pydantic schemas → JSON Schema; output truncation; `search_text` literal, skips binaries/ignored dirs, caps results.

  `build_builtin_tools` — `calculator`、`read_file`、`list_dir`、`write_file`、`search_text`；pydantic schema → JSON Schema；输出截断；`search_text` 按字面匹配，跳过二进制文件/被忽略的目录，并限制结果数量。

- [ ] `run_loop` — budget check at the **top** of every iteration; model call; stop conditions; natural answer when no tool calls; execute tools; append assistant message then tool observations (success *and* failure); parallel tool calls in request order; charge budget per call; `LoopOutcome.stop_reason` ∈ `answer / budget / max_steps / error / <condition>`; emit `step`, `model_call`, `tool_call`, `tool_result` trace events.

  `run_loop` — 在每次迭代的**开头**检查预算；调用模型；检查停止条件；没有工具调用时即为自然答案；执行工具；先追加助手消息，再追加工具观察结果（成功*和*失败都要）；并行的工具调用按请求顺序处理；每次调用都计入预算；`LoopOutcome.stop_reason` ∈ `answer / budget / max_steps / error / <condition>`；发出 `step`、`model_call`、`tool_call`、`tool_result` trace 事件。

- [ ] `AgentRunner.run` — system prompt then goal; `run_start`/`run_end`; map `LoopOutcome` → `AgentResult`; partial results survive budget/step stops.

  `AgentRunner.run` — 先系统提示词，再目标；`run_start`/`run_end`；把 `LoopOutcome` 映射为 `AgentResult`；因预算/步数而停止时保留部分结果。

- [ ] `stop.py` — `PredicateStop`, `FinishReasonStop`, `RepeatedToolCallStop`, `AnyOf`; first halt wins; truncation/filter ends the run rather than counting as an answer.

  `stop.py` — `PredicateStop`、`FinishReasonStop`、`RepeatedToolCallStop`、`AnyOf`；最先触发的停止条件生效；截断/过滤会结束运行，而不是被算作一个答案。

- [ ] **Artifact:** the five golden tasks in `test_runner.py` pass, and a live run writes `traces/week02-run.jsonl`; read it back with `agentlab.trace.load_trace` and confirm every `tool_call` has a matching `tool_result` with the same `tool_call_id`.

  **产出物：** `test_runner.py` 中的五个黄金任务通过，并且一次真实运行写出 `traces/week02-run.jsonl`；用 `agentlab.trace.load_trace` 读回它，确认每个 `tool_call` 都有一个 `tool_call_id` 相同的 `tool_result` 与之对应。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week02 -m week -q` green · foundation green · `uv run ruff check agentlab/loop agentlab/tools/builtin.py`.

  **G：** `uv run pytest tests/week02 -m week -q` 通过 · 基础测试通过 · `uv run ruff check agentlab/loop agentlab/tools/builtin.py`。

- [ ] **E:** quiz 2 ≥ 8/10; teach-back: *how the loop terminates, where the budget check goes, and why tool errors are observations*.

  **E：** 测验 2 ≥ 8/10；复述讲解：*循环如何终止、预算检查放在哪里，以及为什么工具错误是观察结果*。

- [ ] **T:** `CapabilityDefinition`, capability registry, `DirectCapabilityHandler` — compare their typed plan with your loop; note risk level, approval requirement, read vs write.

  **T：** `CapabilityDefinition`、能力注册表、`DirectCapabilityHandler` — 把它们的类型化计划与你的循环做比较；记录风险等级、审批要求、读与写。

- [ ] Commit.

  提交。

**Stretch:** implement the loop twice — text-parsed ReAct and native tool calling — and write 150 words on when each is preferable.

**拓展：** 把循环实现两遍——基于文本解析的 ReAct 和原生工具调用——并写 150 词说明各自在什么情况下更合适。

**Watch-outs:** budget at the top, not bottom · assistant message before tool observations · unknown tool must not crash the loop · tool errors are data · `max_steps` returns partial work · no unbounded loops.

**注意事项：** 预算检查放在开头而非结尾 · 助手消息先于工具观察结果 · 未知工具不能让循环崩溃 · 工具错误是数据 · `max_steps` 返回部分工作 · 不允许无界循环。

---

### Week 3 — Structured output, prompts as assets, deterministic tests

**第 3 周 — 结构化输出、提示词即资产、确定性测试**

**2026-11-02 → 11-08 · 8–10 h · Owned:** `agentlab/schemas/`.

**2026-11-02 → 11-08 · 8–10 小时 · 负责：** `agentlab/schemas/`。

**Read first:** [concept note 03](../concepts/03-context-engineering.md) · [lab brief](../../labs/week03-structured-output/README.md) · provider structured-output docs.

**先读：** [概念笔记 03](../concepts/03-context-engineering.md) · [实验简介](../../labs/week03-structured-output/README.md) · 提供商的结构化输出文档。

**Tests (61):** [`test_structured.py`](../../tests/week03/test_structured.py) · [`test_repair.py`](../../tests/week03/test_repair.py) · [`test_prompts.py`](../../tests/week03/test_prompts.py) · [`test_decisions.py`](../../tests/week03/test_decisions.py)

**Build**

**构建**

- [ ] `extract_json` — tolerate markdown fences; reject empty/invalid output.

  `extract_json` — 容忍 markdown 代码围栏；拒绝空的/无效的输出。

- [ ] `response_format_for` — pydantic model → `{"type": "json_schema", ...}` strict request.

  `response_format_for` — pydantic 模型 → `{"type": "json_schema", ...}` 严格模式请求。

- [ ] `StructuredExtractor.extract` — versioned system prompt + schema; validate locally; on failure repair at most `max_repairs` times by feeding back the invalid output and field-level errors; return `valid=True, value=<model>` **or** `valid=False, value=None, raw=<last>, errors=[...], repairs=<n>`; record stats; provider errors propagate.

  `StructuredExtractor.extract` — 带版本的系统提示词 + schema；在本地校验；失败时最多修复 `max_repairs` 次，做法是把无效输出和字段级错误回传给模型；返回 `valid=True, value=<model>` **或** `valid=False, value=None, raw=<last>, errors=[...], repairs=<n>`；记录统计数据；提供商错误直接向上传播。

- [ ] `format_validation_errors` / `build_repair_messages` / `RepairStats` — `"field.path: message"`; statistics for clean/repaired/failed; `repair_rate` and `failure_rate` are 0.0 when empty.

  `format_validation_errors` / `build_repair_messages` / `RepairStats` — `"field.path: message"`；分别统计一次成功/修复后成功/失败；为空时 `repair_rate` 和 `failure_rate` 为 0.0。

- [ ] `PromptTemplate` / `PromptRegistry` — immutable `id`/`version`/`template`; missing placeholder raises; hash = sha256(id + template), version-independent; reject duplicate id+version and non-numeric versions; resolve latest numerically.

  `PromptTemplate` / `PromptRegistry` — 不可变的 `id`/`version`/`template`；缺少占位符时抛出异常；hash = sha256(id + template)，与版本无关；拒绝重复的 id+version 以及非数字版本；按数值解析最新版本。

- [ ] `PresentationBudget` + decision family — headline ≤ 12 words, meaning ≤ 2 sentences, next moves ≤ 4, clarification options ≤ 3; `ActionProposal.requires_approval` is always `True`; `parse_decision` selects by `kind`, never guesses; `decision_schema()` is a discriminated union.

  `PresentationBudget` + 决策类型族 — 标题 ≤ 12 个词，含义 ≤ 2 句，后续动作 ≤ 4 个，澄清选项 ≤ 3 个；`ActionProposal.requires_approval` 永远为 `True`；`parse_decision` 按 `kind` 选择，绝不猜测；`decision_schema()` 是一个可辨识联合（discriminated union）。

- [ ] **Artifact:** `analyze(text) -> Decision` over ~20 cases (scripted provider is fine) plus a one-paragraph failure-rate report from `extractor.stats` (clean / repaired / failed). Offline only; scrub cassettes before committing.

  **产出物：** 在约 20 个用例上运行 `analyze(text) -> Decision`（使用脚本化的提供商即可），外加一段根据 `extractor.stats` 写出的失败率报告（一次成功 / 修复后成功 / 失败）。只做离线运行；提交前清理 cassette 中的敏感内容。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week03 -m week -q` green · foundation green · `uv run ruff check agentlab/schemas`.

  **G：** `uv run pytest tests/week03 -m week -q` 通过 · 基础测试通过 · `uv run ruff check agentlab/schemas`。

- [ ] **E:** quiz 3 ≥ 8/10; teach-back: *why JSON mode is not structured output, and how bounded repair + failure metrics work*.

  **E：** 测验 3 ≥ 8/10；复述讲解：*为什么 JSON 模式不等于结构化输出，以及有界修复 + 失败指标如何运作*。

- [ ] **T:** `IStructuredCompletionHandler`, `JsonSchemaValidator`, the `DecisionInteraction` family, `PresentationBudgetEnforcer` — and the validate-after vs impossible-to-emit trade-off.

  **T：** `IStructuredCompletionHandler`、`JsonSchemaValidator`、`DecisionInteraction` 类型族、`PresentationBudgetEnforcer`——以及"事后校验"与"根本无法输出无效内容"之间的取舍。

- [ ] Commit.

  提交。

**Stretch:** measure schema failure rate at three nesting depths; write when hand-rolled validation beats provider-native schemas.

**拓展：** 在三种嵌套深度下测量 schema 失败率；写下手写校验在什么情况下优于提供商原生的 schema。

**Watch-outs:** invalid output must **never** surface as valid · bounded repairs · provider error ≠ schema failure · prompt version bump is the immutable edit · `ActionProposal` cannot self-approve · never commit unscrubbed recorded bodies.

**注意事项：** 无效输出**绝不能**以有效的形式出现 · 修复次数有上限 · 提供商错误 ≠ schema 失败 · 提示词升版本才是不可变的修改方式 · `ActionProposal` 不能自我审批 · 绝不提交未清理的录制内容。

---

### Week 4 — Context engineering and memory

**第 4 周 — 上下文工程与记忆**

**2026-11-09 → 11-15 · 10–12 h · Owned:** `agentlab/context/`.

**2026-11-09 → 11-15 · 10–12 小时 · 负责：** `agentlab/context/`。

**Read first:** [concept note 03](../concepts/03-context-engineering.md) and [note 04](../concepts/04-memory.md) · [lab brief](../../labs/week04-context-memory/README.md) · research 01 §3–4 (read the context-rot section twice).

**先读：** [概念笔记 03](../concepts/03-context-engineering.md) 和 [笔记 04](../concepts/04-memory.md) · [实验简介](../../labs/week04-context-memory/README.md) · 研究报告 01 §3–4（上下文腐化（context rot）一节读两遍）。

**Tests (55):** [`test_window.py`](../../tests/week04/test_window.py) · [`test_compaction.py`](../../tests/week04/test_compaction.py) · [`test_retrieval.py`](../../tests/week04/test_retrieval.py) · [`test_memory.py`](../../tests/week04/test_memory.py)

**Build**

**构建**

- [ ] `window.py` — deterministic ~4-chars/token estimate with per-message overhead; priority classes PINNED > TASK_STATE > RECENT_TURNS > OBSERVATIONS > HISTORY; `input_budget = max_tokens - reserve_output_tokens`; newer wins within a class; insertion order preserved; duplicate ids rejected; pinned-over-budget is reported (`over_budget`), never silently dropped.

  `window.py` — 确定性的约 4 字符/token 估算，外加每条消息的固定开销；优先级分类 PINNED > TASK_STATE > RECENT_TURNS > OBSERVATIONS > HISTORY；`input_budget = max_tokens - reserve_output_tokens`；同一类别中较新的胜出；保留插入顺序；拒绝重复 id；固定项超出预算时要报告（`over_budget`），绝不悄悄丢弃。

- [ ] `compaction.py` — `should_compact`; pinned items always survive; last `keep_recent_items` verbatim; stale tool observations replaced by a placeholder *before* summarising; summariser called at most once; carry-forward note prefixed with the objective and hard-truncated; invalid policy raises.

  `compaction.py` — `should_compact`；固定项永远保留；最后 `keep_recent_items` 项原样保留；在总结*之前*把过时的工具观察结果替换为占位符；总结器最多调用一次；延续笔记（carry-forward note）以目标开头并做硬截断；无效策略抛出异常。

- [ ] `retrieval.py` — `[a-z0-9]+` tokenizer; deterministic blake2b signed-hashing embedder (unit-norm, zero vector for no tokens); cosine similarity with defined zero-vector/dimension behavior; word-preserving overlapping chunks ≤ `max_chars`; SQLite store records dimension (reopen mismatch raises), rejects duplicate ids/wrong lengths, exact top-k by score then id; `VectorIndex` re-index replaces a document.

  `retrieval.py` — `[a-z0-9]+` 分词器；确定性的 blake2b 带符号哈希嵌入器（单位范数，无 token 时为零向量）；余弦相似度对零向量/维度不一致有明确定义的行为；保留完整单词的重叠分块，长度 ≤ `max_chars`；SQLite 存储记录维度（重新打开时维度不匹配会抛出异常），拒绝重复 id/错误长度，按分数再按 id 精确返回 top-k；`VectorIndex` 重新索引时会替换文档。

- [ ] `memory.py` — bounded run-scoped working memory; append-only episodic memory with audited forget; semantic memory requiring provenance, idempotent, contradiction supersedes but keeps history, consolidation across keys, audited erase (the memory kill-switch); policy rejects short content, missing provenance, emails/API-key-shaped secrets/SSNs, unlisted kinds.

  `memory.py` — 有界的、以单次运行为范围的工作记忆；只追加的情景记忆，带可审计的遗忘；语义记忆要求有来源（provenance）、幂等、出现矛盾时新条目取代旧条目但保留历史、跨键整合、可审计的擦除（记忆的紧急开关）；策略拒绝过短内容、缺少来源、电子邮件/形似 API 密钥的秘密/SSN，以及未列出的类型。

- [ ] **Artifact:** a 20-turn research task under a 12k input-token budget, with before/after cost and a retention check showing **≥ 90% of pinned constraints and task state survive every compaction**. Keep the driver local; do not edit `tests/week04/`.

  **产出物：** 一个在 12k 输入 token 预算下进行的 20 轮研究任务，附有前后成本对比，以及一项保持性检查，证明**每次压缩（compaction）后都有 ≥ 90% 的固定约束和任务状态得以保留**。驱动脚本放在本地；不要编辑 `tests/week04/`。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week04 -m week -q` green · foundation green · `uv run ruff check agentlab/context tests/week04`.

  **G：** `uv run pytest tests/week04 -m week -q` 通过 · 基础测试通过 · `uv run ruff check agentlab/context tests/week04`。

- [ ] **E:** quiz 4 ≥ 8/10; teach-back: *how compaction, priority classes and a retention test keep a long task coherent*.

  **E：** 测验 4 ≥ 8/10；复述讲解：*压缩、优先级分类和保持性测试如何让长任务保持连贯*。

- [ ] **T:** `Send.Context.Gateway`, the "least-context envelope" (`SpecialistContext`), the semantic retriever + pgvector adapter — data minimisation, not maximal recall.

  **T：** `Send.Context.Gateway`、"最小上下文信封"（`SpecialistContext`）、语义检索器 + pgvector 适配器——目标是数据最小化，而不是最大化召回。

- [ ] Commit.

  提交。

**Stretch:** poison the context with a contradicting instruction and design a defence.

**拓展：** 用一条相互矛盾的指令污染上下文，并设计一种防御。

**Watch-outs:** pinned constraints are invariant · pruning before summarising · hard token bounds · deterministic embeddings in tests · PII/secret rejection · audited erase · retention threshold is a local invariant you define and measure, not a published benchmark.

**注意事项：** 固定约束是不变量 · 先裁剪再总结 · 硬性的 token 上限 · 测试中使用确定性嵌入 · 拒绝 PII/秘密 · 可审计的擦除 · 保持率阈值是你自己定义并测量的本地不变量，而不是公开的基准。

---

### Week 5 — MCP and interoperability

**第 5 周 — MCP 与互操作**

**2026-11-16 → 11-22 · 8–10 h · Owned:** `agentlab/mcp/`.

**2026-11-16 → 11-22 · 8–10 小时 · 负责：** `agentlab/mcp/`。

> **Read the current MCP changelog before coding.** The 2026 spec is **stateless**: `initialize` and session ids are gone, `server/discover` is mandatory, and `_meta` carries version negotiation. Most tutorials still describe the removed 2025 flow. The lab tests target the current revision.
>
> **写代码之前先读最新的 MCP 变更日志。** 2026 版规范是**无状态的**：`initialize` 和会话 id 都已移除，`server/discover` 是必需的，`_meta` 承载版本协商。大多数教程描述的仍是已被移除的 2025 流程。实验测试针对的是当前修订版。

**Read first:** [concept note 05](../concepts/05-mcp-interop.md) · [lab brief](../../labs/week05-mcp/README.md) · current MCP spec + changelog · research 02 §1.

**先读：** [概念笔记 05](../concepts/05-mcp-interop.md) · [实验简介](../../labs/week05-mcp/README.md) · 当前的 MCP 规范 + 变更日志 · 研究报告 02 §1。

**Tests (68):** [`test_jsonrpc.py`](../../tests/week05/test_jsonrpc.py) · [`test_transport.py`](../../tests/week05/test_transport.py) · [`test_server.py`](../../tests/week05/test_server.py) · [`test_client.py`](../../tests/week05/test_client.py) · [`test_security.py`](../../tests/week05/test_security.py)

**Build**

**构建**

- [ ] `jsonrpc.py` — request/notification/result/error shapes; `_meta` merged into `params`, never top level; ids string/int/absent but never float/bool; `resultType` `"complete"` / `"input_required"`; reserved codes incl. `-32022`.

  `jsonrpc.py` — request/notification/result/error 的结构；`_meta` 合并进 `params`，绝不放在顶层；id 可以是字符串/整数/缺省，但绝不能是浮点数/布尔值；`resultType` 为 `"complete"` / `"input_required"`；保留错误码，包括 `-32022`。

- [ ] `transport.py` — in-memory transport records every message; stdio framing one JSON per line; blank lines skipped; EOF raises `TransportClosed`; `serve_stdio` survives malformed lines and converts handler errors.

  `transport.py` — 内存传输记录每一条消息；stdio 分帧为每行一个 JSON；跳过空行；EOF 抛出 `TransportClosed`；`serve_stdio` 能扛住格式错误的行，并转换处理器错误。

- [ ] `server.py` — stateless dispatch: every request must carry `params._meta[protocolVersion]`; missing → `-32602`, unsupported → `-32022` with supported/requested; `server/discover` advertises versions/identity/capabilities/ttl; deterministic sorted `tools/list`; protocol errors vs tool-level `isError`; notifications never answered; 3 demo tools + 1 resource; `python -m agentlab.mcp.server` works over stdio.

  `server.py` — 无状态分发：每个请求都必须携带 `params._meta[protocolVersion]`；缺失 → `-32602`，不支持 → `-32022` 并附带支持的/请求的版本；`server/discover` 公布版本/身份/能力/ttl；确定性排序的 `tools/list`；区分协议错误与工具级的 `isError`；永远不回应通知；3 个演示工具 + 1 个资源；`python -m agentlab.mcp.server` 可通过 stdio 运行。

- [ ] `client.py` — every request carries `_meta`; `discover`, `list_tools` (digests), `call_tool` (failures become observations), `read_resource`; `as_tool_registry()` makes a remote tool indistinguishable from a local one; reject `input_required` as unsupported.

  `client.py` — 每个请求都携带 `_meta`；`discover`、`list_tools`（摘要）、`call_tool`（失败变成观察结果）、`read_resource`；`as_tool_registry()` 让远程工具与本地工具无法区分；将 `input_required` 作为不支持的情况拒绝。

- [ ] `security.py` — canonical sha-256 over `{name, description, inputSchema}`; server trust list; pin-on-first-contact then verify (mutated declaration or unpinned new tool → `ToolPoisoningError`); credential-like argument keys never cross the boundary; optional tool allowlist; checks run **before** anything is sent.

  `security.py` — 对 `{name, description, inputSchema}` 计算规范化的 sha-256；服务器信任列表；首次接触时固定（pin），之后校验（声明被篡改或出现未固定的新工具 → `ToolPoisoningError`）；形似凭据的参数键绝不跨越边界；可选的工具白名单；检查在发送任何内容**之前**执行。

- [ ] **Artifact:** a multi-step task calling a remote tool through `MCPClient.as_tool_registry()` (local mini-loop in a script; do not import `agentlab.loop` from week-5 tests), plus a security checklist pass: trust list populated, pins persisted, no credentials in arguments, origin/tenant recorded.

  **产出物：** 一个通过 `MCPClient.as_tool_registry()` 调用远程工具的多步任务（在脚本里写一个本地迷你循环；不要在第 5 周测试中导入 `agentlab.loop`），外加一次安全检查清单核对：信任列表已填充、固定信息已持久化、参数中没有凭据、已记录来源/租户。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week05 -m week -q` green · foundation green · `uv run ruff check agentlab/mcp tests/week05`.

  **G：** `uv run pytest tests/week05 -m week -q` 通过 · 基础测试通过 · `uv run ruff check agentlab/mcp tests/week05`。

- [ ] **E:** quiz 5 ≥ 8/10; teach-back: *what MCP standardises, and the trust model that makes it safe*.

  **E：** 测验 5 ≥ 8/10；复述讲解：*MCP 标准化了什么，以及让它安全的信任模型*。

- [ ] **T:** connector manifests → registry (`ICapabilityManifestProvider`) vs MCP discovery; execution-origin stamping; where a standard protocol reduces bespoke connector surface, and where it does not.

  **T：** 连接器清单 → 注册表（`ICapabilityManifestProvider`）与 MCP 发现机制的对比；执行来源标记；标准协议在哪些地方减少了定制连接器的范围，又在哪些地方没有。

- [ ] Commit.

  提交。

**Stretch:** expose your agent over A2A and explain what the agent card must and must not reveal.

**拓展：** 通过 A2A 暴露你的 Agent，并解释 agent card 必须披露什么、绝不能披露什么。

**Watch-outs:** stateless spec · `_meta` per request · notifications never answered · deterministic cacheable tool lists · pin before use · token passthrough blocked · tool errors are `isError`, not protocol crashes.

**注意事项：** 无状态规范 · 每个请求都带 `_meta` · 永远不回应通知 · 确定性、可缓存的工具列表 · 使用前先固定 · 阻止 token 透传 · 工具错误是 `isError`，不是协议崩溃。

---

### Week 6 — Planning, orchestration and human approval (highest value for the day job)

**第 6 周 — 规划、编排与人工审批（对日常工作价值最高）**

**2026-11-23 → 11-29 · 10–12 h · Owned:** `agentlab/orchestrator/`.

**2026-11-23 → 11-29 · 10–12 小时 · 负责：** `agentlab/orchestrator/`。

**Read first:** [concept note 06](../concepts/06-orchestration.md) · [lab brief](../../labs/week06-squads/README.md) · research 01 §2/§6 · [`CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) §4.1/§4.5.

**先读：** [概念笔记 06](../concepts/06-orchestration.md) · [实验简介](../../labs/week06-squads/README.md) · 研究报告 01 §2/§6 · [`CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) §4.1/§4.5。

**Tests (82):** [`test_plan.py`](../../tests/week06/test_plan.py) · [`test_specialist.py`](../../tests/week06/test_specialist.py) · [`test_orchestrator.py`](../../tests/week06/test_orchestrator.py) · [`test_shape.py`](../../tests/week06/test_shape.py) · [`test_approval.py`](../../tests/week06/test_approval.py)

**Build**

**构建**

- [ ] `plan.py` — closed kinds `capability`/`reasoning`; unique ids, known acyclic dependencies, non-empty acceptance criteria, positive budgets; deterministic Kahn topo order; replanning drops failure + transitive dependents, respects retry budget, refuses to empty the plan.

  `plan.py` — 封闭的类型 `capability`/`reasoning`；id 唯一、依赖已知且无环、验收标准非空、预算为正；确定性的 Kahn 拓扑排序；重新规划时丢弃失败步骤及其所有传递依赖者，遵守重试预算，并拒绝把计划清空。

- [ ] `specialist.py` — `ContextEnvelope` (objective/facts/constraints/references, **no transcript field**); only allowlisted tools exposed; other calls become error observations without execution; budget charged; final answer must validate as a JSON hand-off (`summary` required, `confidence` in `[0,1]`); traces record `subagent_start`/`subagent_end` on a child scope, never the transcript.

  `specialist.py` — `ContextEnvelope`（objective/facts/constraints/references，**没有 transcript 字段**）；只暴露白名单中的工具；其他调用变成错误观察结果而不执行；计入预算；最终答案必须能校验为 JSON 交接（`summary` 必填，`confidence` 在 `[0,1]` 内）；trace 在子作用域上记录 `subagent_start`/`subagent_end`，绝不记录对话记录（transcript）。

- [ ] `orchestrator.py` — pure topology classifier: one capability → direct call; one reasoning → one specialist; ≥2 connected → squad; ≥2 components → multi-squad; unbacked derived shape → `shape=None`, `backed=False`, limitation names the shape and refuses to guess smaller. Execution: validate → select → short-circuit if unbacked → deterministic dependency order; failed dependency skips dependents; missing executor/specialist is reported per workstream; aggregate budget sums ledgers.

  `orchestrator.py` — 纯粹的拓扑分类器：一个 capability → 直接调用；一个 reasoning → 一个专员 Agent（specialist）；≥2 个相连 → 小队（squad）；≥2 个连通分量 → 多小队；推导出的形态没有对应支持 → `shape=None`、`backed=False`，limitation 中写明该形态，并拒绝猜测一个更小的形态。执行：校验 → 选择 → 若无支持则短路 → 按确定性的依赖顺序执行；依赖失败时跳过其依赖者；缺少执行器/专员时按工作流（workstream）逐一报告；汇总预算是各账本之和。

- [ ] `approval.py` — the eight invariants, tested one by one: **persisted before approval** · **exact binding** (`actor, tenant, action_hash, authority_snapshot, expires_at`) · **proposer ≠ approver** · **tenant match** · **expiry** · **authority snapshot must be covered, and current authority must still cover it at execution** · **at-most-once** (reserve `EXECUTED` before the executor; replay rejected; deterministic idempotency key; failure marks `FAILED`, never retries) · **state machine** (every illegal transition raises; every step emits a trace event).

  `approval.py` — 八条不变量，逐条测试：**审批前先持久化** · **精确绑定**（`actor, tenant, action_hash, authority_snapshot, expires_at`）· **提议者 ≠ 审批者** · **租户匹配** · **过期** · **权限快照必须被覆盖，且执行时当前权限仍必须覆盖它** · **至多一次**（在调用执行器之前预留 `EXECUTED`；拒绝重放；确定性的幂等键；失败标记为 `FAILED`，绝不重试）· **状态机**（每个非法转换都抛出异常；每一步都发出 trace 事件）。

- [ ] **Artifact:** a miniature "should we discount this deal?" flow — meta-orchestrator → 1–2 specialists → typed decision → approval-gated write → audit row — plus your own test (outside `tests/week06/`) proving an edited, replayed, or expired approval cannot execute.

  **产出物：** 一个迷你的"这笔交易要不要打折？"流程——元编排者 → 1–2 个专员 → 类型化决策 → 受审批把关的写操作 → 审计记录——外加你自己写的测试（放在 `tests/week06/` 之外），证明被编辑过、被重放或已过期的审批无法执行。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week06 -m week -q` green · foundation green · `uv run ruff check agentlab/orchestrator tests/week06`.

  **G：** `uv run pytest tests/week06 -m week -q` 通过 · 基础测试通过 · `uv run ruff check agentlab/orchestrator tests/week06`。

- [ ] **E:** quiz 6 ≥ 8/10; teach-back: *why approval must bind to an action hash and an authority snapshot, and what at-most-once requires*.

  **E：** 测验 6 ≥ 8/10；复述讲解：*为什么审批必须绑定到动作哈希和权限快照，以及"至多一次"需要什么条件*。

- [ ] **T:** decision-first runtime, `ExecutionPlan`, `ExecutionShape`, `ApprovalCheckpoint`, `EffectiveAuthority`, ADR-0001 — this is the week to demo to your team.

  **T：** 决策优先的运行时、`ExecutionPlan`、`ExecutionShape`、`ApprovalCheckpoint`、`EffectiveAuthority`、ADR-0001——这一周最适合向团队做演示。

- [ ] Commit.

  提交。

**Stretch:** durable suspend/resume (SQLite + resume on callback, CAS against double-resume). This is the credible contribution proposal.

**拓展：** 持久化的挂起/恢复（SQLite + 回调时恢复，用 CAS 防止重复恢复）。这是一个可信的贡献提案。

**Watch-outs:** persistence before approval · no self-approval · authority can only narrow · replay rejected · edit-after-approval blocked by hash · never downgrade an unbacked shape · specialists never receive full transcripts.

**注意事项：** 审批前先持久化 · 不允许自我审批 · 权限只能收窄 · 拒绝重放 · 审批后的编辑会被哈希拦截 · 绝不降级一个没有支持的形态 · 专员 Agent 永远拿不到完整的对话记录。

---

### Week 7 — Evals and observability (highest-risk week — no prior eval culture)

**第 7 周 — 评测与可观测性（风险最高的一周——之前没有评测文化）**

**2026-11-30 → 12-06 · 8–10 h · Owned:** `agentlab/evals/`.

**2026-11-30 → 12-06 · 8–10 小时 · 负责：** `agentlab/evals/`。

**Read first:** [concept note 07](../concepts/07-evals-observability.md) · [lab brief](../../labs/week07-evals/README.md) · research 03 §1–2 · Hamel Husain on evals.

**先读：** [概念笔记 07](../concepts/07-evals-observability.md) · [实验简介](../../labs/week07-evals/README.md) · 研究报告 03 §1–2 · Hamel Husain 关于评测（eval）的文章。

**Tests (48):** [`test_dataset.py`](../../tests/week07/test_dataset.py) · [`test_harness.py`](../../tests/week07/test_harness.py) · [`test_judges.py`](../../tests/week07/test_judges.py) · [`test_report.py`](../../tests/week07/test_report.py)

**Build**

**构建**

- [ ] `dataset.py` — frozen case/rubric/check types; `validate()` collects **all** problems and never raises; `content_digest()` excludes header metadata; JSONL header-first round-trip; `save` validates first (fail closed); malformed JSON names the line.

  `dataset.py` — 冻结的 case/rubric/check 类型；`validate()` 收集**所有**问题且从不抛出异常；`content_digest()` 排除头部元数据；JSONL 以头部开头、可往返读写；`save` 先校验（失败即关闭）；格式错误的 JSON 会指出所在行。

- [ ] `judges.py` — `RubricJudge.judge` forces `response_format={"type": "json_object"}`, sends rubric + output, requires every criterion exactly once, and treats malformed/unknown/out-of-range output as `SchemaValidationError` (never a partial verdict); weighted normalized score; `agreement_rate` / `cohen_kappa`; `measure_agreement` pairs by **case id**, never position.

  `judges.py` — `RubricJudge.judge` 强制使用 `response_format={"type": "json_object"}`，发送评分标准（rubric）+ 输出，要求每条标准恰好出现一次，并把格式错误/未知/超出范围的输出视为 `SchemaValidationError`（绝不给出部分裁决）；加权归一化分数；`agreement_rate` / `cohen_kappa`；`measure_agreement` 按**用例 id** 配对，绝不按位置。

- [ ] `harness.py` — `AgentRun` seam; run each case `repeats` times with a per-trial `Tracer`; factory exceptions become failed trials; deterministic checks first, judge **only after** checks pass; malformed judge output = failed trial; each trace ends with an `eval_case` event; `pass@1` vs `pass^k` (`k` outside `[1, repeats]` raises); metrics incl. cost and p95 latency; failure taxonomy.

  `harness.py` — `AgentRun` 接缝（seam）；每个用例运行 `repeats` 次，每次试验使用独立的 `Tracer`；工厂异常变为失败的试验；先做确定性检查，**只有在**检查通过之后才调用评审；评审输出格式错误 = 试验失败；每条 trace 以一个 `eval_case` 事件结尾；`pass@1` 与 `pass^k`（`k` 超出 `[1, repeats]` 时抛出异常）；指标包括成本和 p95 延迟；失败分类。

- [ ] `report.py` — markdown/HTML report with identity, summary, failure taxonomy, judge calibration, and a baseline gate that **fails closed on a missing metric**.

  `report.py` — markdown/HTML 报告，包含标识信息、摘要、失败分类、评审校准，以及一个**在缺少指标时失败即关闭**的基线关卡。

- [ ] **Artifact:** an eval set of **≥ 25 cases** in `data/evals/*.jsonl` for the agents from weeks 2–6; a committed baseline report from a real run; one deliberate prompt change that finds **three regressions**, keeping one as a permanent case; judge calibrated on **20–30 human-labelled** items with **≥ 80% raw agreement** and κ quoted.

  **产出物：** 在 `data/evals/*.jsonl` 中为第 2–6 周的 Agent 建立一个 **≥ 25 个用例**的评测集；一份来自真实运行、已提交的基线报告；一次刻意的提示词修改，找出**三个回归**，并将其中一个保留为永久用例；评审在 **20–30 个人工标注**的条目上完成校准，**原始一致率 ≥ 80%**，并给出 κ 值。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week07 -m week -q` green · `uv run ruff check agentlab/evals`.

  **G：** `uv run pytest tests/week07 -m week -q` 通过 · `uv run ruff check agentlab/evals`。

- [ ] **E:** quiz 7 ≥ 8/10; teach-back: *how to build an eval suite that catches a regression before production (pass@1 vs pass^k)*.

  **E：** 测验 7 ≥ 8/10；复述讲解：*如何构建能在上线前捕获回归的评测套件（pass@1 与 pass^k）*。

- [ ] **T:** `Outcome_Trace` append-only contract, the 5-dimension `Evaluator`, the `Distillation`/`Trainer` learning loop, the publish gate; note where trace→candidate→publish is unwired.

  **T：** `Outcome_Trace` 只追加契约、5 维度的 `Evaluator`、`Distillation`/`Trainer` 学习循环、发布关卡；记录 trace→候选→发布 链路中尚未接通的地方。

- [ ] Commit.

  提交。

**Stretch:** OTel exporter for your trace events, viewed in a local collector.

**拓展：** 为你的 trace 事件写一个 OTel 导出器，并在本地 collector 中查看。

**Watch-outs:** deterministic checks first · judge is not a substitute for ground truth · pass^k ≠ pass@1 · pair labels by case id · fail closed on missing baseline metric · no network in tests.

**注意事项：** 先做确定性检查 · 评审不能替代真实的标准答案 · pass^k ≠ pass@1 · 按用例 id 配对标签 · 缺少基线指标时失败即关闭 · 测试中不访问网络。

---

### Week 8 — Security, governance, cost, reliability

**第 8 周 — 安全、治理、成本、可靠性**

**2026-12-07 → 12-13 · 8–10 h · Owned:** `agentlab/guard/` (errors and the attack corpus are provided — do not weaken the corpus).

**2026-12-07 → 12-13 · 8–10 小时 · 负责：** `agentlab/guard/`（错误类型和攻击语料已提供——不要削弱语料）。

**Read first:** [concept note 08](../concepts/08-security-governance.md) · [lab brief](../../labs/week08-security/README.md) · research 03 §3–7 · OWASP GenAI Top 10 2026.

**先读：** [概念笔记 08](../concepts/08-security-governance.md) · [实验简介](../../labs/week08-security/README.md) · 研究报告 03 §3–7 · OWASP GenAI Top 10 2026。

**Tests (93):** [`test_injection.py`](../../tests/week08/test_injection.py) · [`test_sandbox.py`](../../tests/week08/test_sandbox.py) · [`test_authority.py`](../../tests/week08/test_authority.py) · [`test_audit.py`](../../tests/week08/test_audit.py) · [`test_ratelimit.py`](../../tests/week08/test_ratelimit.py) · [`test_routing.py`](../../tests/week08/test_routing.py) · [`test_attacks.py`](../../tests/week08/test_attacks.py)

**Build**

**构建**

- [ ] `injection.py` — wrap/delimit untrusted content (escape delimiter spoofing, strip zero-width); normalized rule scan with findings sorted by position; screen with risk = max severity, always return the sanitized wrapped form; guarded messages state the instruction hierarchy with untrusted items as labelled data; output vetting redacts secrets/external images/data channels; lethal-trifecta assessment: 3 legs ⇒ critical, 2 ⇒ elevated, 3 legs with no mitigation ⇒ **blocked**, unknown mitigation raises.

  `injection.py` — 包裹/界定不可信内容（转义伪造的分隔符，去除零宽字符）；归一化后的规则扫描，发现结果按位置排序；筛查时风险 = 最高严重度，并始终返回清理后的包裹形式；受防护的消息要声明指令层级，不可信条目作为带标签的数据；输出审查会遮蔽秘密/外部图片/数据通道；致命三要素（lethal trifecta）评估：3 个要素 ⇒ 严重，2 个 ⇒ 升高，3 个要素且无缓解措施 ⇒ **阻止**，未知的缓解措施抛出异常。

- [ ] `sandbox.py` — URL-decode once, then reject empty/absolute/UNC/NUL/`..`; resolve and require containment in an allowed root; oversize file refused before loading; command allowlist, no shell, hard timeout, truncated output; `action_hash(tool, args)` canonical; `ApprovalLedger.consume` refuses expiry/replay; read tools no-op, write tools need a token matching tenant + exact action.

  `sandbox.py` — 先 URL 解码一次，然后拒绝空路径/绝对路径/UNC/NUL/`..`；解析路径并要求其位于允许的根目录之内；超大文件在加载前即被拒绝；命令白名单，不使用 shell，硬性超时，输出截断；规范化的 `action_hash(tool, args)`；`ApprovalLedger.consume` 拒绝过期/重放；读工具无需额外处理，写工具需要一个与租户 + 精确动作相匹配的令牌。

- [ ] `authority.py` — `effective_authority` = intersection over matching boundaries (platform-wide `None` applies to all tenants); no boundary ⇒ no grants; model claims never add grants and are recorded in `denied_claims`; empty tenant raises; delegation is a non-empty subset; caller credentials refused/stripped case-insensitively.

  `authority.py` — `effective_authority` = 所有匹配边界的交集（平台级的 `None` 适用于所有租户）；没有边界 ⇒ 没有授权；模型声称的权限永远不会增加授权，并被记录在 `denied_claims` 中；空租户抛出异常；委托必须是非空子集；调用方凭据被拒绝/剥离，且不区分大小写。

- [ ] `audit.py` — append-only JSONL with monotonic sequence + hash chain; update/delete rejected and recorded; tampered log fails integrity check; correlation ids link before/after evidence.

  `audit.py` — 只追加的 JSONL，带单调递增序号 + 哈希链；更新/删除会被拒绝并记录；被篡改的日志无法通过完整性检查；关联 id 把前后证据联系起来。

- [ ] `ratelimit.py` / `routing.py` — tenant-isolated token/cost quotas; route by price, declared order, per-request budget, latency, reliability, remaining budget; **fail closed** when no candidate is viable; fall back only on transient failures; never retry cancellation; charge successful calls to the budget.

  `ratelimit.py` / `routing.py` — 按租户隔离的 token/成本配额；按价格、声明顺序、单请求预算、延迟、可靠性、剩余预算进行路由；没有可行候选时**失败即关闭**；只在瞬时故障时回退；绝不重试取消操作；成功的调用计入预算。

- [ ] **Artifact:** `projects/security/SECURITY.md` threat model (lethal-trifecta audit, data flows, controls, residual risks, what you would not claim); a before/after table where every corpus attack moves from "succeeds" to "blocked"; one write action wired proposal → approval → sandbox → audit row with before/after evidence and one correlation id.

  **产出物：** `projects/security/SECURITY.md` 威胁模型（致命三要素审计、数据流、控制手段、残余风险、你不会做出的声明）；一张前后对比表，其中每一个语料攻击都从"成功"变为"被阻止"；一个写操作完整串起 提议 → 审批 → 沙箱 → 审计记录，带有前后证据和同一个关联 id。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week08 -m week -q` green · `uv run ruff check agentlab/guard`.

  **G：** `uv run pytest tests/week08 -m week -q` 通过 · `uv run ruff check agentlab/guard`。

- [ ] **E:** quiz 8 ≥ 8/10; teach-back: *why indirect injection is assumed to succeed, and how authority/sandbox/audit limit the blast radius*.

  **E：** 测验 8 ≥ 8/10；复述讲解：*为什么要假定间接注入一定会成功，以及权限 / 沙箱 / 审计如何限制影响范围*。

- [ ] **T:** the governance sandwich, `EffectiveAuthority` nine-source intersection, licensing/quota at ingress, execution origin — understand why each control exists, not the code.

  **T：** 治理三明治、`EffectiveAuthority` 的九源交集、入口处的许可/配额、执行来源——理解每项控制为什么存在，而不是去看代码。

- [ ] Commit.

  提交。

**Stretch:** write a one-page threat-model review of the SendOS approval path and send it to a senior engineer for critique.

**拓展：** 为 SendOS 的审批路径写一份一页纸的威胁模型评审，并发给一位资深工程师请其批评指正。

**Watch-outs:** model output can never widen authority · deny by default · sandbox path traversal (encoded too) · audit tamper detection · token passthrough is case-insensitive · write actions require approval + audit · routing fails closed.

**注意事项：** 模型输出永远不能扩大权限 · 默认拒绝 · 沙箱路径穿越（编码后的也算）· 审计篡改检测 · token 透传检查不区分大小写 · 写操作需要审批 + 审计 · 路由失败即关闭。

---

### Week 9 — Capstone: Mini-SendOS

**第 9 周 — 结业项目：Mini-SendOS**

**2026-12-14 → 12-20 · 12–16 h · Owned:** `agentlab/capstone/`, `agentlab/web/`, `tests/week09/test_capstone_extra.py`, `projects/capstone/`, `projects/portfolio/`.

**2026-12-14 → 12-20 · 12–16 小时 · 负责：** `agentlab/capstone/`、`agentlab/web/`、`tests/week09/test_capstone_extra.py`、`projects/capstone/`、`projects/portfolio/`。

**Read first:** [concept note 09](../concepts/09-production.md) · [lab brief](../../labs/week09-capstone/README.md) · [`projects/capstone/README.md`](../../projects/capstone/README.md) · [`ACCEPTANCE.md`](../../projects/capstone/ACCEPTANCE.md).

**先读：** [概念笔记 09](../concepts/09-production.md) · [实验简介](../../labs/week09-capstone/README.md) · [`projects/capstone/README.md`](../../projects/capstone/README.md) · [`ACCEPTANCE.md`](../../projects/capstone/ACCEPTANCE.md)。

**Tests (46):** [`test_catalogue.py`](../../tests/week09/test_catalogue.py) · [`test_decisions.py`](../../tests/week09/test_decisions.py)

**Build in this order (do not reorder)**

**按此顺序构建（不要调换顺序）**

- [ ] `uv run python scripts/demo_capstone.py` — read the `DEMO BLOCKED` list; it names the first gap.

  `uv run python scripts/demo_capstone.py` — 阅读 `DEMO BLOCKED` 列表；它会指出第一个缺口。

- [ ] `decisions.py` — `parse_decision`, `decision_to_wire`, `enforce_presentation_budgets`; validate fully before raising; closed union rejects unknown kinds/fields; collect **all** budget violations into one error.

  `decisions.py` — `parse_decision`、`decision_to_wire`、`enforce_presentation_budgets`；先完整校验再抛出异常；封闭联合拒绝未知的类型/字段；把**所有**预算违规收集到一个错误中。

- [ ] `catalogue.py` — `CapabilityDefinition`; `merge(connectors, published)` validates both sources, rejects duplicates within a source, published wins whole-definition on conflict, order-independent; `resolve` makes unknown and forbidden indistinguishable (no cross-tenant oracle); `list_for_tenant` sorted; fail closed on empty tenant, non-object schema, bad risk, **write without approval**, empty tenant scope.

  `catalogue.py` — `CapabilityDefinition`；`merge(connectors, published)` 校验两个来源，拒绝同一来源内的重复项，冲突时已发布的定义整体胜出，结果与顺序无关；`resolve` 让"未知"和"禁止"无法区分（不提供跨租户的探测途径）；`list_for_tenant` 有序；遇到空租户、非对象 schema、错误的风险等级、**没有审批的写操作**、空的租户范围时失败即关闭。

- [ ] `platform.py` — `action_digest` + the five lifecycle methods: typed decision → capability check → persisted proposal → bound approval → at-most-once execution → append-only audit rows.

  `platform.py` — `action_digest` + 五个生命周期方法：类型化决策 → 能力检查 → 持久化的提议 → 绑定的审批 → 至多一次执行 → 只追加的审计记录。

- [ ] `web/app.py` wiring — `create_app(platform)`; graceful when FastAPI is absent.

  `web/app.py` 接线 — `create_app(platform)`；FastAPI 不存在时优雅降级。

- [ ] **Artifact:** `tests/week09` green (plus your own invariants: cross-tenant, replay, edit-after-approval in `tests/week09/test_capstone_extra.py`); `scripts/demo_capstone.py` exits `0` offline and prints the full audit sequence; `FASTAPI_AVAILABLE` imports without FastAPI; `ACCEPTANCE.md` filled with command output; `WRITEUP.md` 800–1,500 words; a 5-minute recorded demo.

  **产出物：** `tests/week09` 通过（外加你自己的不变量测试：跨租户、重放、审批后编辑，放在 `tests/week09/test_capstone_extra.py` 中）；`scripts/demo_capstone.py` 离线运行时以 `0` 退出并打印完整的审计序列；没有 FastAPI 时 `FASTAPI_AVAILABLE` 也能导入；`ACCEPTANCE.md` 填入命令输出；`WRITEUP.md` 800–1,500 词；一段 5 分钟的演示录屏。

**Gate**

**关卡**

- [ ] **G:** `uv run pytest tests/week09 -m week -q` green · `uv run pytest -q` foundation green · demo exits 0 · `uv run ruff check agentlab/capstone agentlab/web tests/week09`.

  **G：** `uv run pytest tests/week09 -m week -q` 通过 · `uv run pytest -q` 基础测试通过 · 演示以 0 退出 · `uv run ruff check agentlab/capstone agentlab/web tests/week09`。

- [ ] **E:** quiz 9 ≥ 8/10; *draw the request path from ingress to audit row aloud, naming every failure mode and its control*.

  **E：** 测验 9 ≥ 8/10；*大声讲解从入口到审计记录的请求路径，说出每个失败模式及其控制手段*。

- [ ] **T:** one-page SendOS improvement proposal grounded in the build (recommended: durable suspend/resume for approvals, or trace→candidate evidence gating).

  **T：** 一份立足于本次构建的一页纸 SendOS 改进提案（推荐：审批的持久化挂起/恢复，或 trace→候选 的证据把关）。

- [ ] Commit.

  提交。

**Stretch:** a live-provider web UI run (tests stay offline/mock).

**拓展：** 用真实提供商运行一次 Web UI（测试仍保持离线/mock）。

**Watch-outs:** demo first, then code in build order · no network in the flow · two tenants cannot see each other's capabilities · replay cannot execute twice · edit-after-approval blocks on hash mismatch · ship at 80% — demo + write-up beats polish.

**注意事项：** 先跑演示，再按构建顺序写代码 · 流程中不访问网络 · 两个租户看不到彼此的能力 · 重放不能执行两次 · 审批后的编辑因哈希不匹配而被阻止 · 做到 80% 就交付——演示 + 总结文章胜过打磨。

---

## 6. Week 10 — Consolidation and leverage

**6. 第 10 周 — 巩固与发挥**

**2026-12-21 → 12-27 · 4–6 h · No new mechanisms.**

**2026-12-21 → 12-27 · 4–6 小时 · 不引入新机制。**

- [ ] **Re-derive from a blank file:** the agent loop, MCP discovery flow, eval design, and approval state machine. Compare to your code; gaps are your study list.

  **从空白文件重新推导：** Agent 循环、MCP 发现流程、评测设计和审批状态机。与你的代码对比；差距就是你的学习清单。

- [ ] Retake all ten quizzes closed book; every score ≥ 8/10.

  闭卷重做全部十次测验；每次得分 ≥ 8/10。

- [ ] Finish [`projects/portfolio/WRITEUP.md`](../../projects/portfolio/WRITEUP.md) and the [`DEMO-CHECKLIST.md`](../../projects/portfolio/DEMO-CHECKLIST.md).

  完成 [`projects/portfolio/WRITEUP.md`](../../projects/portfolio/WRITEUP.md) 和 [`DEMO-CHECKLIST.md`](../../projects/portfolio/DEMO-CHECKLIST.md)。

- [ ] Draft **two deep-dive posts** (e.g. "approval binding is a security mechanism", "why pass^k beats pass@1").

  起草**两篇深度解析文章**（例如"审批绑定是一种安全机制"、"为什么 pass^k 胜过 pass@1"）。

- [ ] Answer all **30 interview questions** in [`INTERVIEW.md`](INTERVIEW.md) aloud, 60–90 s each, before reading model answers.

  在阅读参考答案之前，大声回答 [`INTERVIEW.md`](INTERVIEW.md) 中全部 **30 道面试题**，每题 60–90 秒。

- [ ] Get the one-page SendOS proposal reviewed by a senior engineer; record the feedback.

  请一位资深工程师审阅那份一页纸的 SendOS 提案；记录反馈。

- [ ] Decide the next step: framework fluency (LangGraph / Microsoft Agent Framework), the learning loop (trace→eval→candidate→publish), or agentic RL/post-training.

  决定下一步：框架熟练度（LangGraph / Microsoft Agent Framework）、学习循环（trace→评测→候选→发布），或 Agent 强化学习/后训练。

- [ ] Do the end-of-course evidence check (§8) and commit `week 10: portfolio + consolidation`.

  完成课程结束时的证据检查（§8），并提交 `week 10: portfolio + consolidation`。

---

## 7. Cross-cutting mastery track (the 20% reading time)

**7. 贯穿始终的精通路线（20% 的阅读时间）**

These are not a separate project. Do them in the reading block of the week that needs them.

这些不是一个单独的项目。在需要它们的那一周的阅读时段里完成。

- [ ] **Understand the provided primitives before week 2.** Read [`tests/test_core.py`](../../tests/test_core.py), then `agentlab/types.py`, `trace.py`, `budget.py`, `pricing.py`, `config.py`, `errors.py`, `testing/mock.py`, `testing/cassettes.py`, and `tools/registry.py`. Be able to say what each primitive guarantees.

  **在第 2 周之前理解所提供的基础原语。** 阅读 [`tests/test_core.py`](../../tests/test_core.py)，然后是 `agentlab/types.py`、`trace.py`、`budget.py`、`pricing.py`、`config.py`、`errors.py`、`testing/mock.py`、`testing/cassettes.py` 和 `tools/registry.py`。要能说出每个原语保证了什么。

- [ ] **Read the scaffold contract once.** [`SCAFFOLD-CONTRACT.md`](../internals/SCAFFOLD-CONTRACT.md) explains ownership, the independence rule, and why tests are marked `pytest.mark.week`. It also tells you exactly which files are off-limits.

  **把脚手架契约读一遍。** [`SCAFFOLD-CONTRACT.md`](../internals/SCAFFOLD-CONTRACT.md) 解释了归属关系、独立性规则，以及为什么测试被标记为 `pytest.mark.week`。它还明确告诉你哪些文件是禁区。

- [ ] **Understand the test harness.** Why lab tests carry `pytestmark = pytest.mark.week`, why `pyproject.toml` excludes them by default, and why `-m week` is required. Read `tests/conftest.py` and the fixtures in `tests/week01/conftest.py`.

  **理解测试 harness（运行框架）。** 为什么实验测试带有 `pytestmark = pytest.mark.week`，为什么 `pyproject.toml` 默认排除它们，以及为什么必须加 `-m week`。阅读 `tests/conftest.py` 以及 `tests/week01/conftest.py` 中的 fixture。

- [ ] **Read the repo mechanics.** `pyproject.toml` (deliberately small dependency set + extras), `.github/workflows/ci.yml`, `tasks.ps1` (Windows runner) and `tasks.sh` (macOS/Linux runner), `scripts/check_links.py`, and `scripts/demo_capstone.py`. You should be able to reproduce CI locally with the command in §3.

  **阅读仓库的运作机制。** `pyproject.toml`（刻意精简的依赖集 + extras）、`.github/workflows/ci.yml`、`tasks.ps1`（Windows 运行器）和 `tasks.sh`（macOS/Linux 运行器）、`scripts/check_links.py` 以及 `scripts/demo_capstone.py`。你应该能用 §3 中的命令在本地复现 CI。

- [ ] **Read each concept note just-in-time** (`docs/concepts/01`–`09`), never cover-to-cover. Answer its five questions before and after the lab.

  **每篇概念笔记都在需要时再读**（`docs/concepts/01`–`09`），绝不从头读到尾。在实验之前和之后分别回答它的五个问题。

- [ ] **Read research reports by section, not end-to-end.** Use the appendix mapping in [`LEARNING-PLAN.md`](LEARNING-PLAN.md) §Appendix. Check the uncertainty registers before quoting numbers.

  **研究报告按章节读，不要从头读到尾。** 使用 [`LEARNING-PLAN.md`](LEARNING-PLAN.md) §Appendix 中的附录映射。引用数字之前先查看不确定性登记表。

- [ ] **Use the companion textbook optionally.** [`CHAPTER-MAP.md`](../books/ai-agents-in-depth/CHAPTER-MAP.md) has 6 h / 20 h / 60 h reading paths. It never replaces a lab.

  **伴读教材可选使用。** [`CHAPTER-MAP.md`](../books/ai-agents-in-depth/CHAPTER-MAP.md) 提供 6 小时 / 20 小时 / 60 小时三种阅读路径。它永远不能替代实验。

- [ ] **Run the C# bridge labs in weeks 1 and 3.** `dotnet build dotnet/AgentBridgeLabs.sln`, then `dotnet run --project dotnet/ProviderBridge -- --selftest` and `dotnet run --project dotnet/StructuredDecisionBridge -- --selftest`. Read the headers; they map line-by-line to SendOS.

  **在第 1 周和第 3 周运行 C# 对照实验。** 先 `dotnet build dotnet/AgentBridgeLabs.sln`，然后 `dotnet run --project dotnet/ProviderBridge -- --selftest` 和 `dotnet run --project dotnet/StructuredDecisionBridge -- --selftest`。阅读文件头注释；它们与 SendOS 逐行对应。

- [ ] **Read SendOS docs privately and weekly.** [`CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) §0–1 once; [`BRIDGE.md`](../sendos/BRIDGE.md) for each week's 30-minute bridge. Code wins over docs; record the five known drifts.

  **私下、每周阅读 SendOS 文档。** [`CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) §0–1 读一遍；每周 30 分钟的对照环节读 [`BRIDGE.md`](../sendos/BRIDGE.md)。代码优先于文档；记录五处已知的偏差。

- [ ] **Use the glossary for retrieval.** [`glossary.md`](../glossary.md) has ~120 terms; read only the week's group and cover the definition column.

  **用术语表做检索练习。** [`glossary.md`](../glossary.md) 收录了约 120 个术语；只读本周对应的那一组，并遮住定义列。

- [ ] **Write 2–3 ADRs** from [`templates/adr.md`](../../templates/adr.md) for decisions you want to defend (e.g. "why provider seam owns retries", "why approval binds to a hash").

  根据 [`templates/adr.md`](../../templates/adr.md) **写 2–3 份 ADR**，记录你想要为之辩护的决策（例如"为什么由 provider 接缝负责重试"、"为什么审批要绑定到哈希"）。

- [ ] **Keep the repo healthy:** `uv run ruff check .`, `uv run ruff format --check .`, `uv run python scripts/check_links.py`, and the CI command in §3. These are what CI runs.

  **保持仓库健康：** `uv run ruff check .`、`uv run ruff format --check .`、`uv run python scripts/check_links.py`，以及 §3 中的 CI 命令。这些就是 CI 运行的内容。

- [ ] **Read your own git history at week 10.** One commit per step is what makes the portfolio story legible.

  **在第 10 周阅读你自己的 git 历史。** 每一步一次提交，正是让作品集的故事清晰可读的关键。

---

## 8. Definition of mastery (the final exam)

**8. 精通的定义（期末考试）**

A week is not "done" because tests pass. You are done when all of the following are true.

一周并不因为测试通过就算"完成"。只有当以下所有条件都成立时，你才算完成。

### Evidence checklist

**证据清单**

- [ ] 9 weekly reviews in `notes/`, each with a 150-word teach-back and a failure log.

  `notes/` 中有 9 份每周复盘，每份都附有一份 150 词的复述讲解和一份失败日志。

- [ ] 8 green week suites (weeks 1–8) + the capstone (week 9).

  8 个通过的每周测试套件（第 1–8 周）+ 结业项目（第 9 周）。

- [ ] All 10 quizzes ≥ 8/10, closed book.

  全部 10 次测验 ≥ 8/10，闭卷。

- [ ] ≥ 140 flashcards reviewed at least twice (the prefilled decks in [`flashcards/`](flashcards/) hold ~15 per week; add the five you create in the weekly ritual).

  ≥ 140 张闪卡且每张至少复习过两次（[`flashcards/`](flashcards/) 中预先填好的卡组每周约 15 张；再加上你在每周仪式中创建的五张）。

- [ ] Eval report with baseline, pass^k, judge agreement/κ, and failure taxonomy.

  评测报告包含基线、pass^k、评审一致率/κ 和失败分类。

- [ ] Capstone demo runs offline; 5-minute recording exists.

  结业项目演示可离线运行；已有 5 分钟的录屏。

- [ ] [`WRITEUP.md`](../../projects/portfolio/WRITEUP.md) complete; two deep-dive posts drafted.

  [`WRITEUP.md`](../../projects/portfolio/WRITEUP.md) 已完成；已起草两篇深度解析文章。

- [ ] One-page SendOS improvement proposal reviewed by a senior engineer.

  一页纸的 SendOS 改进提案已经过一位资深工程师审阅。

- [ ] All 30 interview questions answered aloud at least once.

  全部 30 道面试题都至少大声回答过一次。

- [ ] Re-derivation exercises done from a blank file (loop, MCP discovery, eval design, approval state machine).

  从空白文件开始完成了重新推导练习（循环、MCP 发现、评测设计、审批状态机）。

- [ ] You own roughly 4–6k lines of tested Python and can point to the test that would fail if any mechanism were removed.

  你拥有大约 4–6k 行经过测试的 Python 代码，并且能指出：如果移除任何一个机制，会是哪个测试失败。

### The ten claims you must be able to make without notes (90 seconds each)

**你必须能不看笔记讲清楚的十个论断（每个 90 秒）**

| Wk<br>周 | Claim<br>论断 | ☐ |
| -- | ---------------------------------------------------------------------------------------------------- | -- |
| 1  | Why retries, SSE delta assembly and usage accounting live in the provider adapter<br>为什么重试、SSE 增量拼装和用量统计都放在 provider 适配器里 | ☐ |
| 2  | How the loop terminates, where the budget check goes, and why tool errors are observations<br>循环如何终止、预算检查放在哪里，以及为什么工具错误是观察结果 | ☐ |
| 3  | Why JSON mode is not structured output, and how bounded repair + failure metrics work<br>为什么 JSON 模式不等于结构化输出，以及有界修复 + 失败指标如何运作 | ☐ |
| 4  | How compaction, priority classes and a retention test keep a long task coherent<br>压缩、优先级分类和保持性测试如何让长任务保持连贯 | ☐ |
| 5  | What MCP standardises, and the trust model that makes it safe<br>MCP 标准化了什么，以及让它安全的信任模型 | ☐ |
| 6  | Why approval must bind to an action hash and an authority snapshot, and what at-most-once requires<br>为什么审批必须绑定到动作哈希和权限快照，以及"至多一次"需要什么条件 | ☐ |
| 7  | How to build an eval suite that catches a regression before production (pass@1 vs pass^k)<br>如何构建能在上线前捕获回归的评测套件（pass@1 与 pass^k） | ☐ |
| 8  | Why indirect injection is assumed to succeed, and how authority/sandbox/audit limit the blast radius<br>为什么要假定间接注入一定会成功，以及权限 / 沙箱 / 审计如何限制影响范围 | ☐ |
| 9  | The full request path from ingress to audit row, with every failure mode and control<br>从入口到审计记录的完整请求路径，以及其中每个失败模式和控制手段 | ☐ |
| 10 | The four runtime duties, and how SendOS maps onto them<br>运行时的四项职责，以及 SendOS 如何与之对应 | ☐ |

### The five things you should be able to do cold

**你应该能脱口而出做到的五件事**

- [ ] Draw the request path of an agent run from ingress to audit row, naming every failure mode and its control.

  画出一次 Agent 运行从入口到审计记录的请求路径，说出每个失败模式及其控制手段。

- [ ] Explain approval binding and what breaks without an action hash + authority snapshot.

  讲清楚审批绑定，以及缺少动作哈希 + 权限快照时会出什么问题。

- [ ] Design an eval suite that would catch a prompt regression before production, including pass^k reasoning.

  设计一个能在上线前捕获提示词回归的评测套件，包括 pass^k 的推理。

- [ ] Read a new agent framework's source and map its abstractions onto the primitives you built.

  阅读一个新 Agent 框架的源码，并把它的抽象映射到你构建过的基础原语上。

- [ ] Read SendOS's `DecisionRuntime` / `ApprovalCheckpoint` / `Model.Adapter` and propose a concrete improvement.

  阅读 SendOS 的 `DecisionRuntime` / `ApprovalCheckpoint` / `Model.Adapter`，并提出一项具体的改进。

---

## 9. Stop rules and anti-patterns

**9. 停止规则与反模式**

| Anti-pattern<br>反模式 | Why it costs you<br>为什么代价高 | Replacement<br>替代做法 |
| ----------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| Reading `solutions/` before green<br>在通过之前阅读 `solutions/` | Removes the productive struggle and the ability to defend the code<br>剥夺了有益的挣扎过程，以及为代码辩护的能力 | Diff only after the gate; then write one design difference<br>只在通过关卡后再做 diff；然后写下一处设计差异 |
| Editing the tests to make them pass<br>修改测试让它们通过 | Destroys the specification<br>摧毁了规格说明 | Fix the code; if you believe a test is wrong, report it, don't weaken it<br>修代码；如果你认为某个测试是错的，就报告它，而不是削弱它 |
| Starting week N+1 early<br>提前开始第 N+1 周 | Week N+1 silently assumes week N's abstractions<br>第 N+1 周默认建立在第 N 周的抽象之上 | One grace debt max, cleared in 7 days<br>最多一项宽限欠账，7 天内清掉 |
| "Study more" when a gate fails<br>关卡未通过时"多学一点" | The remedies differ by gate<br>不同关卡的补救方法不同 | Diagnose G / E / T and apply the matching fix in `CHECKPOINTS.md` §4<br>诊断是 G / E / T 中的哪一项，并应用 `CHECKPOINTS.md` §4 中对应的修复 |
| Tutorial rabbit hole / framework shopping<br>陷入教程兔子洞 / 挑选框架 | Frameworks are weeks 6–9 comparison material, not prerequisites<br>框架是第 6–9 周的对比材料，不是前置条件 | Build the loop first; cap reading at 20%<br>先构建循环；阅读时间上限 20% |
| Polishing the capstone<br>打磨结业项目 | Shipping beats polish<br>交付胜过打磨 | Demo + write-up + eval report at 80%<br>做到 80% 就交付演示 + 总结文章 + 评测报告 |
| Silent struggle<br>默默挣扎 | Self-study dies in silence<br>自学会在沉默中夭折 | 20-minute rule; write the question, ask for a hint<br>20 分钟规则；写下问题，求一个提示 |
| Unbounded live loops<br>无界的真实调用循环 | Cost and safety<br>成本与安全 | `Budget` on every live run; keep `$0.50`<br>每次真实运行都用 `Budget`；保持 `$0.50` |
| Pasting SendOS code/data<br>粘贴 SendOS 代码/数据 | Confidentiality breach; also not transferable<br>违反保密规定；而且也无法迁移 | Describe mechanisms in your own words<br>用你自己的话描述机制 |
| A second status tracker<br>第二个状态追踪表 | Two sources of truth drift<br>两个权威来源会逐渐偏离 | This file for sequence, [`PROGRESS.md`](PROGRESS.md) for status<br>本文件管顺序，[`PROGRESS.md`](PROGRESS.md) 管状态 |

---

## 10. Phase tracker

**10. 阶段追踪表**

Tick only when the phase gate is fully passed. Details belong in [`PROGRESS.md`](PROGRESS.md).

只有当阶段关卡完全通过时才打勾。细节记录在 [`PROGRESS.md`](PROGRESS.md) 中。

| Phase<br>阶段 | Weeks<br>周 | Exit condition<br>退出条件 | Done<br>完成 |
| ------------------ | ----- | ------------------------------------------------------------------ | ---- |
| 0 — Setup<br>0 — 环境搭建 | 0     | `doctor` clean, foundation green, one priced live call<br>`doctor` 无问题，基础测试通过，一次计价的真实调用 | ☐   |
| 1 — Foundations<br>1 — 基础 | 1–3  | Weeks 1–3 G+E+T; provider seam, loop, typed output all green<br>第 1–3 周 G+E+T；provider 接缝、循环、类型化输出全部通过 | ☐   |
| 2 — Capability<br>2 — 能力 | 4–6  | Weeks 4–6 G+E+T; context, MCP, approval-gated squad all green<br>第 4–6 周 G+E+T；上下文、MCP、受审批把关的小队全部通过 | ☐   |
| 3 — Production<br>3 — 生产 | 7–9  | Weeks 7–9 G+E+T; eval gate, attack suite, capstone demo offline<br>第 7–9 周 G+E+T；评测关卡、攻击套件、结业项目离线演示 | ☐   |
| 4 — Consolidation<br>4 — 巩固 | 10    | Blank-file re-derivation, portfolio, interviews, reviewed proposal<br>空白文件重新推导、作品集、面试、经过审阅的提案 | ☐   |

**Next action right now:** §2.1 — install `uv`, then run `uv sync --extra dev` and `uv run pytest -q`. Everything else follows.

**下一步立刻要做的：** §2.1 — 安装 `uv`，然后运行 `uv sync --extra dev` 和 `uv run pytest -q`。其余一切随之而来。
