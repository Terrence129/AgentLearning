# Learner Profile

**学习者档案**

> This file tells the AI tutor (and any future reviewer) who it is teaching. Keep it factual and current; it is read at the start of every tutoring session. Update it when constraints or goals change, not weekly.
>
> 这个文件告诉 AI 导师（以及任何未来的审阅者）它在教的是谁。请保持内容真实、及时；每次辅导会话开始时都会读取它。在约束或目标发生变化时更新它，而不是每周更新。

---

## 1. Identity and background

**1. 身份与背景**

- **Name:** Terrence (Yaqi) Chen — the repo owner.

  **姓名：** Terrence (Yaqi) Chen——本仓库的所有者。

- **Current role:** intern on **SendOS**, an enterprise `.NET` agent platform (decision-first runtime, capability catalogue, approval/governance layers, append-only outcome traces, learning loop).

  **当前角色：** 在 **SendOS** 实习，这是一个企业级 `.NET` Agent 平台（决策优先的运行时、能力目录、审批/治理层、只追加的结果 trace、学习闭环）。

- **Experience:** senior full-stack engineer — **Java/Spring**, **C#/.NET**, **React/TypeScript**, **AWS**. Comfortable with APIs, typed contracts, tests, CI, distributed systems.

  **经验：** 高级全栈工程师——**Java/Spring**、**C#/.NET**、**React/TypeScript**、**AWS**。熟悉 API、类型化契约、测试、CI 和分布式系统。

- **Education:** NUS ISS graduate diploma; CDUT BSc. Co-author of an **IEEE GNN paper** — so research papers are readable, but ML training experience is not the goal here.

  **教育背景：** NUS ISS 研究生文凭；CDUT 理学学士。一篇 **IEEE GNN 论文**的合著者——所以能读懂研究论文，但积累机器学习训练经验并不是这里的目标。

- **Prior LLM experience:** basic — has called LLM APIs, knows the chat-completions shape, no production agent systems built from scratch.

  **此前的 LLM 经验：** 基础水平——调用过 LLM API，了解 chat-completions 的结构，没有从零构建过生产级 Agent 系统。

- **Languages:** Chinese (native) and English (professional). Based in **Singapore (SGT, UTC+8)**.

  **语言：** 中文（母语）和英文（工作水平）。常驻**新加坡（SGT，UTC+8）**。

## 2. Goals (why this repo exists)

**2. 目标（这个仓库为什么存在）**

| # | Goal<br>目标 | Success looks like<br>成功的样子 | Weight<br>权重 |
|---|---|---|---|
| **A** | **Contribute meaningfully to SendOS faster**<br>**更快地为 SendOS 做出有意义的贡献** | Can read `DecisionRuntime`, `ApprovalCheckpoint`, `Send.Model.Adapter` and propose a concrete improvement; ships one reviewed proposal<br>能读懂 `DecisionRuntime`、`ApprovalCheckpoint`、`Send.Model.Adapter` 并提出具体的改进；交付一份经过评审的提案 | Highest — compounding<br>最高——复利效应 |
| **B** | **Be hireable as an AI/agent engineer**<br>**具备被聘为 AI/Agent 工程师的能力** | 8 green test suites, traced agent, eval report, capstone demo, architecture write-up, 2 posts<br>8 个通过（变绿）的测试套件、可追踪的 Agent、评测（eval）报告、结业项目（capstone）演示、架构总结文章、2 篇博文 | High (output of A+D)<br>高（A+D 的产出） |
| **C** | **Build an own agent product**<br>**打造自己的 Agent 产品** | Weeks 2–8 modules compose into a platform; week 9 ships a UI + real domain workflow<br>第 2–8 周的模块组合成一个平台；第 9 周交付 UI + 真实领域的工作流 | Medium<br>中 |
| **D** | **Deep technical mastery / research fluency**<br>**深度技术掌握 / 研究素养** | From-scratch builds, one must-read paper per week, re-derivation from a blank file at week 10<br>从零构建、每周一篇必读论文、第 10 周从空白文件重新推导 | High — compounding<br>高——复利效应 |

**Conflict rule:** when short on time, protect **A** and **D**. B and C are by-products of doing A and D well.

**冲突规则：** 时间不够时，优先保住 **A** 和 **D**。B 和 C 是把 A 和 D 做好之后的副产品。

## 3. Constraints

**3. 约束**

- **Time:** 8–12 h/week alongside the SendOS internship and NUS coursework. Realistic pattern: Tue 20:00 (2 h), Thu 20:00 (2 h), Sat 09:00–13:00 (3–4 h). Some weeks will be minimum-viable weeks (see [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md) §8).

  **时间：** 在 SendOS 实习和 NUS 课程之外，每周 8–12 小时。现实的安排：周二 20:00（2 小时）、周四 20:00（2 小时）、周六 09:00–13:00（3–4 小时）。有些周会是最低可行周（参见 [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md) §8）。

- **Budget:** DeepSeek primary (cheap, high-volume labs), OpenAI secondary (comparison labs). Total model spend target **under $5** for the whole curriculum; `AGENTLAB_RUN_BUDGET_USD=0.50` default stays on.

  **预算：** 以 DeepSeek 为主（便宜，用于大量调用的实验（lab）），OpenAI 为辅（用于对比实验）。整个课程的模型总花费目标为 **5 美元以内**；默认的 `AGENTLAB_RUN_BUDGET_USD=0.50` 始终保持开启。

- **Machine:** Windows 11 (work/reference machine); Windows PowerShell 5.1 (PowerShell 7 recommended, both work); Python 3.12 via `uv`; .NET 10 SDK available for the bridge labs. The current checkout for this run is macOS at `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`; commands are documented for both platforms.

  **机器：** Windows 11（工作/参考机器）；Windows PowerShell 5.1（推荐 PowerShell 7，两者都可用）；通过 `uv` 使用 Python 3.12；桥接实验可使用 .NET 10 SDK。本次运行的当前检出位于 macOS 上的 `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`；命令对两个平台都有文档说明。

- **Context switching:** internship work is `.NET`; the curriculum is Python. The plan deliberately uses Python for learning (sample density) and C# only for the SendOS bridge.

  **上下文切换：** 实习工作用 `.NET`；课程用 Python。计划有意用 Python 来学习（示例资料密度高），只在 SendOS 桥接部分使用 C#。

## 4. Working preferences and strengths to exploit

**4. 工作偏好与可发挥的优势**

- **Build-first, tests-first.** Learns fastest when a failing test defines the contract. Prefer "read the test, then the brief" over "read the theory, then code".

  **先动手构建，先写测试。** 当一个失败的测试定义了契约时学得最快。更倾向于「先读测试，再读任务说明」，而不是「先读理论，再写代码」。

- **Strong systems intuition.** Already knows typed contracts, retries, budgets, observability, multi-tenancy — the curriculum maps new terms onto those existing models rather than teaching them from zero.

  **很强的系统直觉。** 已经了解类型化契约、重试、预算、可观测性、多租户——课程会把新术语映射到这些已有的思维模型上，而不是从零教起。

- **Weak spots to watch:** (1) Python fluency is below Java/C# — expect friction with language idioms, not concepts; (2) no prior eval culture experience — week 7 is the highest-risk week; (3) perfectionism on artifacts — ship at 80% (the plan's explicit countermeasure).

  **需要留意的薄弱点：** (1) Python 的熟练度不如 Java/C#——预计会在语言惯用法上遇到摩擦，而不是在概念上；(2) 此前没有评测文化的经验——第 7 周是风险最高的一周；(3) 对产出物追求完美——做到 80% 就交付（这是计划中明确的应对措施）。

- **What not to do:** do not re-teach HTTP, JSON, async basics, Git, or general testing. Do not assume ML math knowledge; explain loss/RL only when week 9/10 requires it.

  **不要做的事：** 不要重新讲解 HTTP、JSON、异步基础、Git 或一般性的测试。不要假定具备机器学习数学知识；只有在第 9/10 周需要时才讲解损失函数/强化学习。

## 5. Environment facts

**5. 环境信息**

| Item<br>项目 | Value<br>值 |
|---|---|
| Repo root<br>仓库根目录 | `D:\DevRepo\MyProjects\AgentLearning` (Windows) · `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning` (current macOS checkout)<br>`D:\DevRepo\MyProjects\AgentLearning`（Windows）· `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`（当前 macOS 检出） |
| Python | 3.12 (uv-managed)<br>3.12（由 uv 管理） |
| Providers<br>模型提供商（provider） | `DEFAULT_PROVIDER=deepseek` (DeepSeek API); `OPENAI_API_KEY` optional<br>`DEFAULT_PROVIDER=deepseek`（DeepSeek API）；`OPENAI_API_KEY` 可选 |
| Budget guard<br>预算防护 | `AGENTLAB_RUN_BUDGET_USD` (default 0.50) — never disable<br>`AGENTLAB_RUN_BUDGET_USD`（默认 0.50）——永远不要禁用 |
| Tests<br>测试 | `.\tasks.ps1 test` (all, Windows) / `./tasks.sh test` (macOS/Linux); `.\tasks.ps1 week NN` / `./tasks.sh week NN` (one week)<br>`.\tasks.ps1 test`（全部，Windows）/ `./tasks.sh test`（macOS/Linux）；`.\tasks.ps1 week NN` / `./tasks.sh week NN`（单周） |
| Task runner<br>任务运行器 | `tasks.ps1` (Windows PowerShell) · `tasks.sh` (macOS/Linux bash or zsh)<br>`tasks.ps1`（Windows PowerShell）· `tasks.sh`（macOS/Linux 的 bash 或 zsh） |
| Labs<br>实验 | `labs/weekNN-*/README.md` — the brief<br>`labs/weekNN-*/README.md`——任务说明 |
| Gates<br>关卡 | [`CHECKPOINTS.md`](CHECKPOINTS.md) — Green / Explain / Transfer<br>[`CHECKPOINTS.md`](CHECKPOINTS.md)——Green（通过）/ Explain（讲解）/ Transfer（迁移） |
| Tracker<br>进度追踪 | [`PROGRESS.md`](PROGRESS.md) — updated every Saturday<br>[`PROGRESS.md`](PROGRESS.md)——每周六更新 |

## 6. Confidentiality rules (non-negotiable)

**6. 保密规则（不可协商）**

SendOS is proprietary. In this repo and with any external model:

SendOS 是专有系统。在本仓库中以及与任何外部模型交互时：

- **Never paste C# source, internal URLs, tenant data, customer names, prompts or schema dumps** from SendOS into a public model chat. Describe mechanisms in your own words.

  **永远不要把 SendOS 的 C# 源码、内部 URL、租户数据、客户名称、提示词或 schema 转储粘贴到公共模型的聊天中。** 用你自己的话描述机制。

- The "SendOS bridge" is *reading* + *abstraction* + *your own Python miniature*. It is not a copy-paste exercise.

  「SendOS 桥接」是*阅读* + *抽象* + *你自己的 Python 微缩实现*。它不是复制粘贴练习。

- If a bridge note needs an example, invent a neutral one (e.g. "a capability registry") and map it privately.

  如果桥接笔记需要一个例子，就编一个中性的例子（例如「一个能力注册表」），然后私下做映射。

- Do not record `.env` values, API keys or tokens in notes, commits or the portfolio.

  不要在笔记、提交或作品集中记录 `.env` 的值、API 密钥或 token。

---

## 7. How to use the AI tutor

**7. 如何使用 AI 导师**

The tutor has the plan, the research and the SendOS concept map. It is most useful as a **reviewer, hint-giver and interrogator** — not as a code generator.

导师掌握了计划、研究资料和 SendOS 概念图。它最有用的角色是**审阅者、提示者和提问者**——而不是代码生成器。

### 7.1 The three modes, and when to use them

**7.1 三种模式及其使用时机**

| Mode<br>模式 | Use when<br>使用时机 | Prompt pattern<br>提示词模板 |
|---|---|---|
| **Hint** (default)<br>**提示**（默认） | You are building and stuck<br>你在构建过程中卡住了 | "Week N, test `X` fails with `Y`. I tried `Z`. Give me one hint, not the answer."<br>「第 N 周，测试 `X` 失败，报错 `Y`。我试过 `Z`。给我一个提示，不要给答案。」 |
| **Review**<br>**审阅** | You have something that works<br>你已经有了能运行的东西 | "Review `agentlab/loop/react.py` against the four failure modes in the week-2 brief. Be adversarial."<br>「对照第 2 周任务说明中的四种失败模式审阅 `agentlab/loop/react.py`。请以对抗的姿态来审。」 |
| **Interrogate**<br>**拷问** | Before a quiz, gate or interview<br>在测验、关卡或面试之前 | "Quiz me on week 4 for 10 minutes. One question at a time; wait for my answer, then grade it."<br>「就第 4 周的内容考我 10 分钟。一次一道题；等我回答后再打分。」 |

### 7.2 Rules the tutor should follow with you

**7.2 导师与你互动时应遵守的规则**

1. **Hints before answers.** Escalate: question → concept → pseudocode → minimal example. Never write the lab implementation for you.

   **先给提示，再给答案。** 逐级升级：提问 → 概念 → 伪代码 → 最小示例。永远不要替你写实验的实现。

2. **Ask for the test and the error**, not the whole file. If you have not run the tests, the first response should be "run them and paste the summary".

   **索要测试和错误信息**，而不是整个文件。如果你还没跑过测试，第一条回复应该是「先跑测试，然后把摘要贴过来」。

3. **Review after attempts, not before.** Design reviews are welcome once code exists.

   **在尝试之后审阅，而不是之前。** 一旦有了代码，欢迎做设计评审。

4. **Name the failure mode.** Every explanation should end with what breaks if the mechanism is absent.

   **点出失败模式。** 每个解释的结尾都应说明：如果缺少这个机制，会坏掉什么。

5. **Push back on scope.** If you ask for something outside the current week, the answer is "later, here is the link".

   **对超出范围的请求予以回绝。** 如果你问的是当前这周之外的内容，回答应该是「以后再说，这是链接」。

6. **Keep answers short by default.** You can ask for depth; unrequested essays waste your time.

   **默认保持回答简短。** 你可以要求深入；没人要的长篇大论只会浪费你的时间。

### 7.3 Good prompts (copy these)

**7.3 好的提示词（直接复制使用）**

- "I'm on week 3. `test_repair_feeds_validation_error` fails with `KeyError: 'error'`. Hint, not answer."

  「我在第 3 周。`test_repair_feeds_validation_error` 失败，报错 `KeyError: 'error'`。给提示，不要给答案。」

- "Here is my compaction design (6 bullets). Attack it: what context would it lose that matters later?"

  「这是我的压缩（compaction）设计（6 条要点）。来挑刺吧：它会丢失哪些之后还用得着的上下文？」

- "Grade my teach-back for week 6 against the Explain gate rubric in CHECKPOINTS.md."

  「按照 CHECKPOINTS.md 中 Explain 关卡的评分标准（rubric），给我第 6 周的复述讲解（teach-back）打分。」

- "I have 45 minutes before a lecture. What is the highest-value task given my progress in PROGRESS.md?"

  「离上课还有 45 分钟。根据我在 PROGRESS.md 中的进度，价值最高的任务是什么？」

- "Explain the difference between my week-6 approval binding and SendOS's, using the abstraction, not their code."

  「用抽象层面的描述（而不是他们的代码），解释我第 6 周的审批绑定和 SendOS 的有什么区别。」

- "Quiz me on week 7, focus on evals and judge calibration, 10 minutes."

  「就第 7 周考我，重点是评测和评审校准，10 分钟。」

### 7.4 Bad prompts (avoid)

**7.4 糟糕的提示词（避免使用）**

| Prompt<br>提示词 | Why it fails<br>为什么不行 |
|---|---|
| "Write the week 4 lab for me."<br>「帮我把第 4 周的实验写了。」 | The tests are the learning; you will not be able to defend it in review or interview.<br>测试本身就是学习；你将无法在评审或面试中为它辩护。 |
| "Fix this error: [whole traceback]"<br>「修一下这个错误：[完整的 traceback]」 | Without the test name and what you tried, the tutor guesses; you learn less.<br>没有测试名和你尝试过的方法，导师只能猜；你也学得更少。 |
| "Explain everything about agents."<br>「把关于 Agent 的一切都讲一遍。」 | Too broad; you will get a summary you could have read, and it will not stick.<br>太宽泛了；你只会得到一份本可以自己读到的摘要，而且记不住。 |
| "Is this good?" (no evidence)<br>「这样好吗？」（没有证据） | Ask against a rubric or eval number instead.<br>应该改为对照评分标准或评测数字来提问。 |
| Pasting SendOS code<br>粘贴 SendOS 代码 | Confidentiality breach; also the abstraction is what transfers.<br>违反保密规定；而且真正可迁移的是抽象。 |

### 7.5 Session hygiene

**7.5 会话卫生**

- Start each tutoring session by stating week, goal and what you tried.

  每次辅导会话开始时，先说明所在周、目标以及你尝试过什么。

- End by writing **one sentence** in the lab notes: what you now understand that you did not at the start.

  结束时在实验笔记中写下**一句话**：你现在理解了哪些开始时还不理解的东西。

- If the tutor gives you an answer you asked for against these rules, convert it into a flashcard and a test — do not just apply it.

  如果你违反这些规则向导师要了答案并得到了它，就把它转化为一张闪卡和一个测试——不要只是照搬应用。

- Keep sessions under 45 minutes; long tutoring sessions crowd out the building they are meant to support.

  会话时长控制在 45 分钟以内；过长的辅导会话会挤占它本应支持的动手构建时间。
