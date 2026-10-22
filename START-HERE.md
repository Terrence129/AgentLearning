# START HERE

**从这里开始**

Read this once, top to bottom. It takes ~10 minutes, then ~90 minutes of setup and first contact.
Do not read the whole learning plan first — you will lose momentum. Set up, see something work, then plan.

从头到尾读一遍。阅读大约需要 10 分钟，之后是大约 90 分钟的环境搭建和初次上手。
不要先去读完整的学习计划——那会让你失去势头。先搭好环境，看到东西跑起来，然后再做计划。

---

## 1. What you are getting (2 min)

**1. 你将获得什么（2 分钟）**

You are an experienced full-stack engineer (Java/C#, React, AWS) who has called LLM APIs but not built agent systems. Over ~10 weeks you will build a small agent platform from scratch, in Python, driven by tests — and simultaneously learn to read the `.NET` agent platform you work on (SendOS) with expert eyes.

你是一名经验丰富的全栈工程师（Java/C#、React、AWS），调用过 LLM API，但还没有构建过 Agent 系统。在大约 10 周的时间里，你将用 Python、以测试驱动的方式从零构建一个小型 Agent 平台——同时学会以专家的眼光去阅读你所工作的 `.NET` Agent 平台（SendOS）。

The rule that makes this work: **you write code every week, and a failing test suite defines the finish line.**

让这一切奏效的规则是：**你每周都要写代码，并且由一个失败的测试套件来定义终点线。**

---

## 2. Setup (15 min)

**2. 环境搭建（15 分钟）**

Open a terminal in the repo root. On this macOS checkout that is `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`; on Windows it is `D:\DevRepo\MyProjects\AgentLearning`.

在仓库根目录打开一个终端。在这台 macOS 的检出副本上，它是 `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`；在 Windows 上则是 `D:\DevRepo\MyProjects\AgentLearning`。

**Windows (PowerShell 5.1 or 7):**

**Windows（PowerShell 5.1 或 7）：**

```powershell
# Windows (PowerShell)
.\tasks.ps1 setup
```

**macOS / Linux (bash or zsh):**

**macOS / Linux（bash 或 zsh）：**

```bash
# macOS / Linux
./tasks.sh setup
```

This will:

它会：

1. install Python 3.12 via `uv`,

   通过 `uv` 安装 Python 3.12，

2. create `.venv` and install dependencies,

   创建 `.venv` 并安装依赖，

3. copy `.env.example` → `.env`,

   复制 `.env.example` → `.env`，

4. run `agentlab doctor`.

   运行 `agentlab doctor`。

Expected: the doctor table prints `python ok`, `repo root ok`, `.env file ok`, and **`provider fail`**
until you add a key. That failure is your first task.

预期结果：在你添加 key 之前，doctor 表格会打印 `python ok`、`repo root ok`、`.env file ok` 以及 **`provider fail`**。这个失败就是你的第一个任务。

### Add a key

**添加 key**

Edit `.env` with VS Code or any editor (Notepad on Windows; never commit it). Minimum viable configuration:

用 VS Code 或任意编辑器（Windows 上可以用记事本）编辑 `.env`（永远不要提交它）。最小可用配置：

```dotenv
DEFAULT_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...          # https://platform.deepseek.com
```

If you have an OpenAI key, add `OPENAI_API_KEY=sk-...` too — some later labs compare providers.

如果你有 OpenAI 的 key，也把 `OPENAI_API_KEY=sk-...` 加上——后面有些实验（lab）会对比不同的模型提供商（provider）。

Then:

然后：

**Windows (PowerShell):**

```powershell
# Windows (PowerShell)
.\tasks.ps1 doctor
```

**macOS / Linux:**

```bash
# macOS / Linux
./tasks.sh doctor
```

All rows should be `ok`/`info` now.

现在所有行都应该是 `ok`/`info`。

> **Budget guard:** every run is capped by `AGENTLAB_RUN_BUDGET_USD` (default $0.50). Leave it on.
>
> **预算防护：** 每次运行都受 `AGENTLAB_RUN_BUDGET_USD`（默认 $0.50）限制。请保持开启。

### Open it in VS Code (2 min)

**在 VS Code 中打开（2 分钟）**

This repo ships a ready workspace: interpreter, test discovery, Ruff on save, task runner, and debug configs.

本仓库自带一个现成的工作区：解释器、测试发现、保存时运行 Ruff、任务运行器以及调试配置。

1. **File → Open Folder** → the repo root — `D:\DevRepo\MyProjects\AgentLearning` on Windows, `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning` on this Mac (the repo itself, not its parent).

   **File → Open Folder** → 仓库根目录——Windows 上是 `D:\DevRepo\MyProjects\AgentLearning`，这台 Mac 上是 `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`（是仓库本身，而不是它的父目录）。

2. Accept the recommended extensions prompt (Ruff, PowerShell, Markdown, Error Lens, GitLens, Todo Tree, Spell Checker). The PowerShell extension is only needed on Windows; the Python/Ruff/Markdown ones matter on both.

   接受推荐扩展的提示（Ruff、PowerShell、Markdown、Error Lens、GitLens、Todo Tree、Spell Checker）。PowerShell 扩展只在 Windows 上需要；Python/Ruff/Markdown 扩展在两个平台上都很重要。

3. `Ctrl+Shift+P` on Windows, `Cmd+Shift+P` on macOS → **Python: Select Interpreter** → `.venv\Scripts\python.exe` (Windows) / `.venv/bin/python` (macOS/Linux).

   Windows 上按 `Ctrl+Shift+P`，macOS 上按 `Cmd+Shift+P` → **Python: Select Interpreter** → `.venv\Scripts\python.exe`（Windows）/ `.venv/bin/python`（macOS/Linux）。

4. `Terminal → Run Task…` → **AgentLab: doctor**. The task uses `tasks.ps1` on Windows and `tasks.sh` on macOS/Linux automatically.

   `Terminal → Run Task…` → **AgentLab: doctor**。该任务会自动在 Windows 上使用 `tasks.ps1`，在 macOS/Linux 上使用 `tasks.sh`。

Details, a PyCharm alternative, and AI-assistant guardrails: [`docs/internals/IDE-SETUP.md`](docs/internals/IDE-SETUP.md). Rider/Visual Studio stay for SendOS `.NET` work.

详细说明、PyCharm 替代方案以及 AI 助手的护栏：[`docs/internals/IDE-SETUP.md`](docs/internals/IDE-SETUP.md)。Rider/Visual Studio 仍然用于 SendOS 的 `.NET` 工作。

---

## 3. First contact: see the foundation work (20 min)

**3. 初次上手：看到基础部分跑起来（20 分钟）**

Run the foundation tests (these are provided, not your work):

运行基础测试（这些是现成提供的，不是你的工作）：

**Windows (PowerShell):**

```powershell
# Windows (PowerShell)
.\tasks.ps1 test
```

**macOS / Linux:**

```bash
# macOS / Linux
./tasks.sh test
```

Expected: foundation tests pass; any `tests/week*` tests that exist fail on purpose — that is your work.
Read `tests/test_core.py` quickly: it demonstrates every primitive you will use later (messages, tools,
tracing, budgets, mocks, cassettes).

预期结果：基础测试通过；所有已存在的 `tests/week*` 测试都会故意失败——那是你要做的工作。
快速读一下 `tests/test_core.py`：它演示了你之后会用到的每一个基本组件（消息、工具、追踪、预算、mock、cassette（录制回放））。

Now run the environment check and a **deliberately unfinished** command:

现在运行环境检查，以及一个**故意未完成**的命令：

**Windows (PowerShell):**

```powershell
# Windows (PowerShell)
.\tasks.ps1 doctor
.\tasks.ps1 chat
```

**macOS / Linux:**

```bash
# macOS / Linux
./tasks.sh doctor
./tasks.sh chat
```

`chat` will tell you "Week 1 lab not implemented yet". That is correct. Run the week 1 tests to see why:

`chat` 会告诉你 "Week 1 lab not implemented yet"。这是正确的。运行第 1 周的测试看看原因：

**Windows (PowerShell):**

```powershell
# Windows (PowerShell)
.\tasks.ps1 week 1
```

**macOS / Linux:**

```bash
# macOS / Linux
./tasks.sh week 1
```

You will see failing tests with messages like *"Week 1 lab: implement complete()"*. **That is your first
lab.** The failing tests are the specification — read them before reading the brief.

你会看到失败的测试，带有类似 *"Week 1 lab: implement complete()"* 的消息。**这就是你的第一个实验。** 失败的测试就是规格说明——在阅读简介之前先读它们。

---

## 4. Read exactly three things (20 min)

**4. 只读三样东西（20 分钟）**

In this order:

按以下顺序：

1. [`labs/week01-provider/README.md`](labs/week01-provider/README.md) — what to build this week

   [`labs/week01-provider/README.md`](labs/week01-provider/README.md)——本周要构建什么

2. [`docs/plan/WEEKLY-RHYTHM.md`](docs/plan/WEEKLY-RHYTHM.md) — how to spend 8–12 hours well

   [`docs/plan/WEEKLY-RHYTHM.md`](docs/plan/WEEKLY-RHYTHM.md)——如何用好这 8–12 小时

3. [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md) — skim the 9 weeks, read week 1 carefully

   [`docs/plan/LEARNING-PLAN.md`](docs/plan/LEARNING-PLAN.md)——略读 9 周的内容，仔细阅读第 1 周

Do not open the research reports yet. They are reference material, indexed by week.

先不要打开研究报告。它们是参考资料，按周编排索引。

---

## 5. Ten-minute planning ritual (10 min)

**5. 十分钟规划仪式（10 分钟）**

Open [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) and fill in:

打开 [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) 并填写：

- Start date

  开始日期

- This week's three sessions in your calendar (suggested: Tue 20:00, Thu 20:00, Sat 09:00–13:00)

  在日历中安排本周的三次学习时段（建议：周二 20:00、周四 20:00、周六 09:00–13:00）

- Week 1 goal in one sentence

  用一句话写出第 1 周的目标

Then copy [`templates/weekly-review.md`](templates/weekly-review.md) to `notes/week01-review.md` and leave it
open all week. You will fill it in on Saturday.

然后把 [`templates/weekly-review.md`](templates/weekly-review.md) 复制为 `notes/week01-review.md`，并让它整周保持打开。你会在周六填写它。

---

## 6. Your first 60 minutes of real work

**6. 你真正动手的前 60 分钟**

1. Open `agentlab/providers/openai_compat.py` and read the module docstring.

   打开 `agentlab/providers/openai_compat.py`，阅读模块的 docstring。

2. Open `tests/week01/test_request_mapping.py` (or whichever order the brief gives — the other files are
   `test_response_parsing.py`, `test_retry.py`, `test_streaming.py`) and read the first failing test.

   打开 `tests/week01/test_request_mapping.py`（或者按简介给出的顺序——其他文件是 `test_response_parsing.py`、`test_retry.py`、`test_streaming.py`），阅读第一个失败的测试。

3. Implement `_build_payload` first. Run that test. Iterate.

   先实现 `_build_payload`。运行那个测试。反复迭代。

4. When stuck >20 minutes, write the question down and ask your AI tutor (see below) — do not silently struggle.

   卡住超过 20 分钟时，把问题写下来，去问你的 AI 导师（见下文）——不要默默地挣扎。

---

## 7. How to use the AI tutor (me) in this repo

**7. 如何在本仓库中使用 AI 导师（我）**

I have the full plan, the research, and the SendOS context. Good prompts:

我掌握完整的计划、研究资料以及 SendOS 的上下文。好的提示词示例：

- "I'm on week 2, test `test_agent_stops_on_max_steps` fails with X. Give me a hint, not the answer."

  “我在第 2 周，测试 `test_agent_stops_on_max_steps` 因 X 而失败。给我一个提示，而不是答案。”

- "Review my `agentlab/loop/react.py` for the four failure modes in the week 2 brief."

  “对照第 2 周简介中的四种失败模式，审查我的 `agentlab/loop/react.py`。”

- "Explain why SendOS does approval binding differently from my week 6 implementation."

  “解释为什么 SendOS 的审批绑定方式与我第 6 周的实现不同。”

- "Quiz me on week 4 concepts for 10 minutes."

  “用 10 分钟测验我第 4 周的概念。”

- "I have 45 minutes today — what is the highest-value thing to do?"

  “我今天有 45 分钟——做什么价值最高？”

Anti-patterns that waste your time:

浪费你时间的反模式：

- "Write this for me." — you will learn nothing and the tests will not teach you.

  “帮我把这个写出来。”——你什么也学不到，测试也教不了你。

- Pasting the whole error without the test name and what you tried.

  粘贴整段报错，却不附上测试名称和你尝试过的做法。

- Asking for the solution before running the tests.

  还没运行测试就要答案。

The tutor's job is to keep you in the **productive struggle zone**: hints before answers, review after attempts.

导师的职责是让你保持在**有成效的挣扎区**：先给提示再给答案，先尝试再审查。

---

## 8. Non-negotiables

**8. 不可妥协的规则**

| Rule<br>规则                                 | Reason<br>原因                                                     |
| ------------------------------------ | ---------------------------------------------------------- |
| Tests green before advancing<br>测试通过（变绿）后才推进         | The next week assumes this week's abstractions<br>下一周以本周的抽象为前提             |
| `Budget` caps on every live run<br>每次真实运行都要有 `Budget` 上限    | Never debug an agent with an uncapped loop<br>绝不要调试一个没有上限的循环的 Agent                 |
| One commit per step<br>每一步一次提交                  | Bisectable history, portfolio evidence<br>可二分查找的历史，也是作品集的证据                     |
| Weekly review + 5 flashcards<br>每周回顾 + 5 张闪卡         | Spaced repetition is the only thing that makes terms stick<br>间隔重复是让术语记牢的唯一方法 |
| SendOS bridge reading on Saturday<br>周六阅读 SendOS 桥接资料    | Transfer is the point of this whole repo<br>迁移才是整个仓库的意义所在                   |
| Ask within 20 minutes of being stuck<br>卡住 20 分钟内就提问 | Silence is the main way self-study fails<br>沉默是自学失败的主要原因                   |

---

## 9. If something breaks

**9. 如果出了问题**

| Symptom<br>症状                           | Fix<br>解决办法                                                                                                                                                                      |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `uv: command not found`         | Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` · macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh \| sh` — then restart the terminal<br>Windows：`powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` · macOS/Linux：`curl -LsSf https://astral.sh/uv/install.sh \| sh`——然后重启终端 |
| `doctor` says no provider<br>`doctor` 提示没有提供商       | Check `.env` exists, key has no quotes/spaces, `DEFAULT_PROVIDER` matches a configured provider<br>检查 `.env` 是否存在、key 中没有引号/空格、`DEFAULT_PROVIDER` 与某个已配置的提供商一致                                                                      |
| `chat` prints week 1 panel<br>`chat` 打印出第 1 周的面板      | Correct — finish the lab<br>这是正确的——去完成实验                                                                                                                                                |
| Tests fail on `import agentlab`<br>测试在 `import agentlab` 时失败 | Run `.\tasks.ps1 sync` (Windows) / `./tasks.sh sync` (macOS/Linux)<br>运行 `.\tasks.ps1 sync`（Windows）/ `./tasks.sh sync`（macOS/Linux）                                                                                                   |
| `./tasks.sh: Permission denied` | Run `chmod +x tasks.sh` (a copied checkout can lose the executable bit)<br>运行 `chmod +x tasks.sh`（复制过来的检出副本可能会丢失可执行位）                                                                                                |
| `python` version wrong<br>`python` 版本不对          | `uv python install 3.12`; the repo pins it via `.python-version`<br>`uv python install 3.12`；仓库通过 `.python-version` 固定了该版本                                                                                                     |
| Cost creeping up<br>成本逐渐上涨                  | Lower `AGENTLAB_RUN_BUDGET_USD`, use the mock provider for tests, and prefer DeepSeek for high-volume labs<br>调低 `AGENTLAB_RUN_BUDGET_USD`，测试时使用 mock 提供商，大批量的实验优先用 DeepSeek                                                             |

---

**Next step:** run `.\tasks.ps1 setup` (Windows) or `./tasks.sh setup` (macOS/Linux), then open [`labs/week01-provider/README.md`](labs/week01-provider/README.md).

**下一步：** 运行 `.\tasks.ps1 setup`（Windows）或 `./tasks.sh setup`（macOS/Linux），然后打开 [`labs/week01-provider/README.md`](labs/week01-provider/README.md)。
