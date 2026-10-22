# 04 — Learning Resources: A Verified, Ranked Map for Agent Engineering

**04 — 学习资源：经过验证、按优先级排序的 Agent 工程资源地图**

**Compiled:** 2026-10-18 · **Access date for every link:** 2026-10-18
**Audience:** senior full-stack engineer (Java / C# / React / AWS), minimal prior LLM-app experience, ~6 h/week alongside an internship and coursework, working on an enterprise .NET agent platform, Chinese speaker based in Singapore.
**Verification:** every item below was status-checked on 2026-10-18 (HTTP 200 unless flagged); the 15 highest-value links were additionally fetched with content read (`✅`; a few are JS-rendered shells where only existence/HTTP status could be confirmed). Items marked `⚠️` resolve only after a redirect; `❌` is dead; `🔒` is paywalled or bot-blocked. See §J for the full ledger.

**整理日期：** 2026-10-18 · **所有链接的访问日期：** 2026-10-18
**目标读者：** 资深全栈工程师（Java / C# / React / AWS），此前几乎没有 LLM 应用开发经验，在实习和课业之余每周约投入 6 小时，正在开发一个企业级 .NET Agent 平台，母语为中文，常驻新加坡。
**验证情况：** 下列每一项都在 2026-10-18 做过状态检查（除非另有标注，均为 HTTP 200）；其中价值最高的 15 个链接还额外抓取并阅读了内容（`✅`；少数是 JS 渲染的空壳页面，只能确认其存在/HTTP 状态）。标注 `⚠️` 的条目需经过一次重定向才能访问；`❌` 表示已失效；`🔒` 表示有付费墙或屏蔽爬虫。完整记录见 §J。

## 2026 state of play (read this first, ~10 min)

**2026 年现状（先读这一节，约 10 分钟）**

Three shifts should shape what you learn. (1) **Harnesses beat frameworks**: the durable skill is owning the loop, context, state and tools — not memorising a framework's API. Anthropic's own engineers now write about *harnesses* as the unit of design and even ship a "meta-harness" ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), updated with a 2026 note; [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents), 2026-04-08). (2) **Context engineering is the craft**: compaction, note-taking, just-in-time retrieval and sub-agents ([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), 2025-09-29). (3) **MCP is infrastructure**: the spec is now versioned and dated ([MCP docs, spec 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)), and both .NET and Python SDKs are first-class, which matters directly for your platform.

有三个转变应当决定你学什么。(1) **harness（运行框架）胜过框架**：真正持久的技能是掌控循环、上下文、状态和工具——而不是背诵某个框架的 API。Anthropic 自己的工程师现在把 *harness* 当作设计的基本单元来撰文，甚至发布了一个「元 harness」（meta-harness）（[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)，附有 2026 年的更新说明；[Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)，2026-04-08）。(2) **上下文工程才是真正的手艺**：压缩（compaction）、做笔记、即时（just-in-time）检索和子 Agent（[Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)，2025-09-29）。(3) **MCP 已成为基础设施**：规范现在带有版本号和日期（[MCP 文档，规范 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)），而且 .NET 和 Python SDK 都是一等公民，这对你的平台有直接影响。

For your situation the highest-leverage path is **Python to learn concepts → C#/.NET Agent Framework to ship**. Learn the concepts in Python first (sample density is 10× higher), then map them to [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) and the [.NET MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) — days of work, not months.

就你的情况而言，杠杆最高的路径是 **用 Python 学概念 → 用 C#/.NET Agent Framework 交付**。先用 Python 学习概念（示例密度高出 10 倍），再把它们映射到 [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) 和 [.NET MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk)——这只需要几天的工作量，而不是几个月。

---

## A. Ten-week self-study track (~63 h core + ~8 h reading buffer)

**A. 十周自学路线（约 63 小时核心内容 + 约 8 小时阅读缓冲）**

Designed for **6 h/week** with one heavier capstone week. Weeks 4 and 9 are the flexible ones: split either across two weeks to stretch to 12 weeks, or drop Week 9 and merge 6+7 to compress to 8 weeks.

按 **每周 6 小时** 设计，其中有一周是工作量更重的结业项目（capstone）周。第 4 周和第 9 周是弹性周：可以把其中任意一周拆成两周，从而拉长到 12 周；或者去掉第 9 周、把第 6 周和第 7 周合并，从而压缩到 8 周。

| Wk<br>周 | Focus<br>重点 | Hrs<br>小时 | Concrete output (do, don't watch)<br>具体产出（动手做，别只看） | Primary sources<br>主要资料 |
|----|-------|-----|-----------------------------------|-----------------|
| 1 | Mental model + a loop from scratch<br>心智模型 + 从零写一个循环 | 6 | 80-line Python ReAct agent: raw chat-completions API, 3 tools, `while` loop, structured tool calls, max-iteration guard. No framework.<br>一个 80 行的 Python ReAct Agent：直接调用原始的 chat-completions API，3 个工具，`while` 循环，结构化工具调用，最大迭代次数防护。不使用任何框架。 | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents); [Chip Huyen — Agents](https://huyenchip.com/2025/01/07/agents.html) |
| 2 | Tools, schemas, MCP<br>工具、schema、MCP | 6 | Wrap two internal APIs as tools; write descriptions to the "junior-dev docstring" standard; build a small MCP server and call it from Claude Desktop or VS Code.<br>把两个内部 API 封装成工具；按「写给初级开发者看的 docstring」标准编写工具描述；构建一个小型 MCP 服务器，并在 Claude Desktop 或 VS Code 中调用它。 | [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents); [MCP docs](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro); [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) |
| 3 | Context engineering + retrieval<br>上下文工程 + 检索 | 7 | Agentic search over a repo/DB with `grep`/SQL tools instead of a vector DB; add a "just-in-time" file reader; measure tokens per task.<br>用 `grep`/SQL 工具在代码仓库/数据库上做 Agent 式搜索（agentic search），而不是使用向量数据库；加一个「即时」文件读取器；测量每个任务消耗的 token 数。 | [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) |
| 4 | Evals + observability (**do not skip**)<br>评测（eval）+ 可观测性（**不要跳过**） | 7 | 20-case golden set for week-1 agent, LLM-as-judge rubric, trace logging, pass-rate dashboard; fail-then-fix one regression.<br>为第 1 周的 Agent 建立 20 个用例的黄金集（golden set）、LLM 评审（LLM-as-judge）评分标准（rubric）、trace 日志和通过率仪表盘；先让一个回归失败，再修复它。 | [Hamel Husain — Your AI product needs evals](https://hamel.dev/blog/posts/evals/); [Inspect](https://inspect.aisi.org.uk/); [Langfuse](https://langfuse.com/) |
| 5 | Memory & long-horizon tasks<br>记忆与长周期任务 | 6 | Add compaction + a `NOTES.md`/progress-file memory; run a 3-session task and show continuity after context reset.<br>加入压缩 + 基于 `NOTES.md`/进度文件的记忆；运行一个跨 3 个会话的任务，并展示上下文重置之后的连续性。 | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents); [MemGPT paper](https://arxiv.org/abs/2310.08560); [Letta docs](https://docs.letta.com/) |
| 6 | Multi-agent & orchestration<br>多 Agent 与编排 | 6 | Orchestrator + 2 workers with a hard budget; compare against a single agent on the same eval set; write down where multi-agent lost.<br>一个编排者 + 2 个工作者，并设定硬性预算；在同一个评测集上与单 Agent 对比；写下多 Agent 在哪些地方表现更差。 | [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system); [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview) |
| 7 | Coding & computer-use agents (security)<br>编码 Agent 与电脑操作（computer-use）Agent（安全） | 6 | Read SWE-agent's ACI; run a coding agent in a throwaway container; demonstrate one prompt-injection attack and one mitigation (credential isolation, allow-list).<br>阅读 SWE-agent 的 ACI；在一次性容器中运行一个编码 Agent；演示一次提示词注入攻击和一种缓解措施（凭证隔离、允许列表）。 | [SWE-agent](https://arxiv.org/abs/2405.15793); [SWE-agent repo](https://github.com/SWE-agent/SWE-agent); [OpenHands](https://github.com/All-Hands-AI/OpenHands) |
| 8 | Production hardening on .NET + AWS<br>在 .NET + AWS 上做生产加固 | 6 | Port week-1 agent to Microsoft Agent Framework (C#): middleware, telemetry, human approval gate, MCP hosted tool; plan AWS deployment surface.<br>把第 1 周的 Agent 移植到 Microsoft Agent Framework（C#）：中间件、遥测、人工审批关卡、MCP 托管工具；规划 AWS 部署面。 | [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview); [Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/); [.NET AI docs](https://learn.microsoft.com/en-us/dotnet/ai/) |
| 9 | Model layer: RL, fine-tuning, DSPy (optional)<br>模型层：强化学习、微调、DSPy（可选） | 5 | One-page decision memo: when to fine-tune vs prompt vs nothing; run one DSPy or prompt-optimisation experiment.<br>写一页决策备忘录：什么时候该微调、什么时候该改提示词、什么时候什么都不做；运行一次 DSPy 或提示词优化实验。 | [Agentic RL survey](https://arxiv.org/abs/2509.02547); [DSPy](https://github.com/stanfordnlp/dspy); [ACE paper](https://arxiv.org/abs/2510.04618) |
| 10 | Capstone + write-up<br>结业项目 + 总结文章 | 8 | One agent that removes real drudgery from your internship (e.g. ticket triage, PR-review checklist); eval report + cost/latency numbers + a 1,000-word post.<br>做一个能为你的实习消除真实繁琐工作的 Agent（例如工单分诊、PR 评审清单）；评测报告 + 成本/延迟数据 + 一篇 1,000 词的文章。 | Everything above; [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) ch. on agents/evals 🔒<br>以上全部；[AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) 中关于 Agent/评测的章节 🔒 |

**Pacing rules that matter more than the schedule:** cap passive video at 30% of each week; every week ends with a runnable artefact; keep a single `notes/` repo of traces and failures — that repo becomes your interview portfolio. If you fall behind, cut Week 9 first, then shrink Week 6; never cut Week 4 (evals are the actual job).

**比日程本身更重要的节奏规则：** 被动看视频的时间不超过每周的 30%；每周结束时都要有一个可运行的产物；只维护一个 `notes/` 仓库，存放 trace 和失败记录——这个仓库会成为你面试时的作品集。如果进度落后，先砍掉第 9 周，再压缩第 6 周；永远不要砍第 4 周（评测才是真正的工作）。

---

## B. Courses (ranked, with duration / cost / prerequisites)

**B. 课程（按优先级排序，附时长 / 费用 / 先修要求）**

| Course<br>课程 | Provider<br>提供方 | Duration<br>时长 | Cost<br>费用 | Prereqs<br>先修要求 | Verdict<br>评价 | Link<br>链接 |
|--------|----------|----------|------|---------|---------|------|
| **Agentic AI** (Andrew Ng) | DeepLearning.AI | 9 h 55 m, intermediate<br>9 小时 55 分钟，中级 | Free to audit; paid certificate/Pro<br>免费旁听；证书/Pro 需付费 | Confident Python<br>熟练掌握 Python | **Best single structured intro.** Modernised version of the old 4-course agent series; do the notebooks, skip the hype framing.<br>**最佳的单一结构化入门课。** 是旧版 4 门 Agent 系列课程的现代化版本；动手做 notebook，跳过那些炒作式的叙述。 | [Course](https://www.deeplearning.ai/courses/agentic-ai/) ⚠️ |
| **AI Agents Course** | Hugging Face | 4 units + final project, ~20–30 h (est.)<br>4 个单元 + 期末项目，约 20–30 小时（估算） | Free; optional certificate<br>免费；证书可选 | Python + basic LLM concepts<br>Python + 基础 LLM 概念 | **Best hands-on fundamentals.** Unit 1 implements the loop by hand; then smolagents / LlamaIndex / LangGraph. Do Units 1–2 + bonus evaluation unit.<br>**最佳的动手基础课。** 第 1 单元手写实现循环；随后是 smolagents / LlamaIndex / LangGraph。做第 1–2 单元 + 附加的评测单元。 | [HF Agents Course](https://huggingface.co/learn/agents-course) ✅ |
| **MCP Course** | Hugging Face | ~6–10 h (est.)<br>约 6–10 小时（估算） | Free<br>免费 | Python or TS<br>Python 或 TS | **Best free MCP end-to-end.** Pairs directly with the [.NET MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) for your platform work.<br>**最好的免费端到端 MCP 课程。** 可直接与 [.NET MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) 配合，用于你的平台工作。 | [HF MCP Course](https://huggingface.co/learn/mcp-course) |
| **AI Agents for Beginners** (18 lessons) | Microsoft | ~10–15 h<br>约 10–15 小时 | Free<br>免费 | Python or C#<br>Python 或 C# | Most enterprise-flavoured free curriculum; strong on tool use, agentic RAG, and MCP. Cherry-pick lessons 1–4, MCP, and multi-agent.<br>最具企业风格的免费课程体系；在工具使用、Agent 式 RAG（agentic RAG）和 MCP 方面很扎实。挑选第 1–4 课、MCP 和多 Agent 相关课程来学。 | [Repo](https://github.com/microsoft/ai-agents-for-beginners) ✅ |
| **Microsoft Agent Framework docs + tutorials** | Microsoft Learn | Self-paced<br>自定进度 | Free<br>免费 | C#/.NET | **Required for your platform.** The official successor to Semantic Kernel + AutoGen, with workflows, middleware, telemetry, MCP, and Python/Go parity. Last updated 2026-08-25.<br>**你的平台必修。** 它是 Semantic Kernel + AutoGen 的官方继任者，具备工作流、中间件、遥测、MCP，并且 Python/Go 版本功能对等。最近更新于 2026-08-25。 | [Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) ✅ · [Tutorials](https://learn.microsoft.com/en-us/agent-framework/tutorials/overview) |
| **LLM Agents MOOC** (Dawn Song, UC Berkeley) | Berkeley RDI | 12 × ~2 h lectures + labs<br>12 讲 × 约 2 小时 + 实验 | Free (latest iteration Spring 2025; certificates closed)<br>免费（最新一期为 2025 年春季；证书已关闭） | Basic ML helps<br>有机器学习基础会更好 | Best research-grade survey, guest lectures from OpenAI/Anthropic/DeepMind/CMU. **Selective**: reasoning, tool use, SWE agents, evaluation. No newer cohort is published — the site redirects to Spring 2025.<br>最佳的研究级综述课程，有来自 OpenAI/Anthropic/DeepMind/CMU 的客座讲座。**有选择地看**：推理、工具使用、SWE Agent、评测。没有发布更新的一期——网站会重定向到 2025 年春季版。 | [Spring 2025](https://llmagents-learning.org/sp25) · [Fall 2024 archive](https://llmagents-learning.org/f24) ✅ |
| **Claude Academy / Anthropic courses** | Anthropic | 1–5 h per course<br>每门课 1–5 小时 | Free<br>免费 | API basics<br>API 基础 | Vendor-authoritative and the most current material on Agent SDK, Claude Code, MCP and tool design. Start with the Agent SDK track.<br>厂商权威，也是关于 Agent SDK、Claude Code、MCP 和工具设计最新的资料。从 Agent SDK 课程路线开始。 | [academy.claude.com](https://academy.claude.com) · [Agent SDK docs](https://platform.claude.com/docs/en/agent-sdk/overview) |
| **Introduction to LangGraph** | LangChain Academy | ~6–8 h<br>约 6–8 小时 | Free<br>免费 | Python | Only worth it if you choose LangGraph; best explanation of checkpointing/state graphs. Otherwise skip — the concepts are in the essays.<br>只有在你选择 LangGraph 时才值得学；对检查点/状态图的讲解最好。否则跳过——这些概念在那些文章里都有。 | [Course](https://academy.langchain.com/courses/intro-to-langgraph) · [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview) |
| **Google Agent Development Kit (ADK)** | Google | Self-paced codelabs<br>自定进度的 codelab | Free<br>免费 | Python | Contrast framework; only if your team evaluates it. Good reference for tool/agent config in YAML-and-code style.<br>作为对照框架；只有在你的团队要评估它时才学。是以「YAML 加代码」方式配置工具/Agent 的好参考。 | [ADK docs](https://google.github.io/adk-docs/) · [Repo](https://github.com/google/adk-python) |
| **COS 597R: Deep Dive into LLMs** | Princeton | Archived seminar<br>已归档的研讨课 | Free<br>免费 | Stronger math/ML<br>较强的数学/机器学习基础 | Optional, research-oriented, **not agent-specific**. Useful only for model-level intuition.<br>可选，偏研究方向，**并非专门针对 Agent**。只对建立模型层面的直觉有用。 | [Course site](https://princeton-cos597r.github.io/) |
| **CS 886: Multiagent Systems** | U. Waterloo | Archived seminar (Winter 2025)<br>已归档的研讨课（2025 年冬季） | Free<br>免费 | Classical MAS theory<br>经典多智能体系统（MAS）理论 | Optional. Classical multi-agent foundations (coordination, game theory); does not cover LLM agents.<br>可选。经典的多智能体基础（协调、博弈论）；不涉及 LLM Agent。 | [Course site](https://cs.uwaterloo.ca/~klarson/teaching/W25-886/) |

**Note on .NET parity:** every course above is taught in Python, which is correct for learning. For your day job, the mapping to keep in mind is Agent Framework (`Microsoft.Agents.AI`) + `ModelContextProtocol` C# SDK + OpenTelemetry, and Anthropic's [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) if your platform is Claude-based.

**关于 .NET 对等的说明：** 上面所有课程都用 Python 授课，这对学习来说是正确的。就你的日常工作而言，要记住的映射是 Agent Framework（`Microsoft.Agents.AI`）+ `ModelContextProtocol` C# SDK + OpenTelemetry；如果你的平台基于 Claude，还要加上 Anthropic 的 [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)。

---

## C. Canonical essays and blog posts (with dates and "why read it")

**C. 经典文章与博客（附日期和「为什么要读」）**

| Date<br>日期 | Piece<br>文章 | Author / org<br>作者 / 机构 | Why read it<br>为什么要读 | Link<br>链接 |
|------|-------|--------------|-------------|------|
| 2024-12-19 (2026 update note)<br>2024-12-19（附 2026 年更新说明） | Building effective agents | Anthropic | The one essay that gives you the shared vocabulary: workflows vs agents, prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimizer, and ACI/tool-design appendix.<br>能让你掌握通用词汇的那一篇文章：工作流 vs Agent、提示词链（prompt chaining）、路由、并行化、编排者-工作者、评估者-优化者（evaluator-optimizer），以及 ACI/工具设计附录。 | [Anthropic](https://www.anthropic.com/engineering/building-effective-agents) ✅ |
| 2025-09-29 | Effective context engineering for AI agents | Anthropic | Reframes prompting as attention-budget management; the clearest treatment of compaction, structured note-taking and sub-agent context isolation.<br>把提示词工程重新定义为注意力预算管理；对压缩、结构化笔记和子 Agent 上下文隔离讲得最清楚。 | [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) ✅ |
| 2025-06 (approx.)<br>2025-06（约） | How we built our multi-agent research system | Anthropic | Rare honest production post: token economics, orchestrator-worker design, eval of a non-deterministic research agent, and where multi-agent fails.<br>难得坦诚的生产实践文章：token 经济学、编排者-工作者设计、如何评测一个非确定性的研究 Agent，以及多 Agent 会在哪里失败。 | [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 2025-09 | Writing effective tools for agents — with agents | Anthropic | Tool definitions are prompts: naming, token-efficient returns, error surfaces, and the write-tests-for-tools loop. Directly applicable to .NET tool plugins.<br>工具定义就是提示词：命名、节省 token 的返回值、错误呈现，以及「为工具写测试」的循环。可直接用于 .NET 工具插件。 | [Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents) |
| 2025-11-26 | Effective harnesses for long-running agents | Anthropic | The best practical answer to "how do I make an agent work across many context windows": initializer agent, feature-list JSON, progress file, git as memory.<br>对「如何让 Agent 跨越多个上下文窗口持续工作」最好的实践答案：初始化 Agent、功能列表 JSON、进度文件、用 git 作为记忆。 | [Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) ✅ |
| 2026-04-08 | Scaling Managed Agents: decoupling the brain from the hands | Anthropic | Most advanced 2026 architecture writing: session / harness / sandbox as interfaces, stateless harnesses, credential isolation from the sandbox. Read after Week 7.<br>2026 年最前沿的架构文章：把会话 / harness / 沙箱作为接口、无状态 harness、将凭证与沙箱隔离。在第 7 周之后阅读。 | [Anthropic](https://www.anthropic.com/engineering/managed-agents) ✅ |
| 2025 | A practical guide to building agents (PDF) | OpenAI | Vendor-neutral-ish playbook: single vs multi-agent, guardrails, human-in-the-loop gates, and a useful "when not to build an agent" section. PDF only.<br>一份大体上厂商中立的实践手册：单 Agent vs 多 Agent、护栏、人在回路（HITL）关卡，以及很有用的「什么时候不该构建 Agent」一节。仅有 PDF 版。 | [OpenAI guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) |
| 2025 | 12-Factor Agents | Dex Horthy / HumanLayer | The production checklist your enterprise reviewers will implicitly want: own your prompts, context window, control flow and state; tools as structured outputs; compact errors; small focused agents; stateless reducer.<br>你的企业评审者会默认期望的生产检查清单：掌控你自己的提示词、上下文窗口、控制流和状态；把工具当作结构化输出；精简错误信息；小而专注的 Agent；无状态 reducer。 | [Repo](https://github.com/humanlayer/12-factor-agents) ✅ |
| 2025-01-07 | Agents | Chip Huyen | The sober systems view: agent taxonomy, planning/feedback/failure modes, cost and latency budgets. The antidote to demo-driven enthusiasm.<br>冷静的系统视角：Agent 分类、规划/反馈/失败模式、成本与延迟预算。是对演示驱动式热情的解药。 | [Huyenchip.com](https://huyenchip.com/2025/01/07/agents.html) |
| 2023-06-23 | LLM Powered Autonomous Agents | Lilian Weng | Still the cleanest conceptual decomposition (planning, memory, tool use) and the origin of many interview questions. Read once, skim later.<br>仍然是最清晰的概念拆解（规划、记忆、工具使用），也是许多面试题的出处。读一遍，之后再略读。 | [Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/) |
| 2024-03 | Your AI product needs evals | Hamel Husain | Turns "vibes" into unit tests: assertions, LLM-as-judge, trace review. The single highest-ROI post for a senior engineer entering this field.<br>把「凭感觉」变成单元测试：断言、LLM 评审、trace 审查。对进入这个领域的资深工程师来说，投入产出比最高的一篇文章。 | [Hamel.dev](https://hamel.dev/blog/posts/evals/) |
| 2023-07 | Patterns for building LLM-based systems & products | Eugene Yan | RAG, guardrails, evaluation, cost/latency trade-offs in system-design vocabulary you already own.<br>用你早已熟悉的系统设计词汇讲 RAG、护栏、评测和成本/延迟权衡。 | [Eugeneyan.com](https://eugeneyan.com/writing/llm-patterns/) |
| 2025 | Agents tag / "agents are LLMs using tools in a loop"<br>Agents 标签 /「Agent 就是在循环中使用工具的 LLM」 | Simon Willison | Sharp, sceptical, frequently updated; the best filter for hype. Start from the tag page rather than any single post.<br>犀利、持怀疑态度、更新频繁；过滤炒作的最佳工具。从标签页开始看，而不是从某一篇文章开始。 | [Tag page](https://simonwillison.net/tags/agents/) |
| 2025 | Code execution with MCP | Anthropic | 2025–2026 pattern: let the agent write code that calls MCP tools instead of piping every tool result through context. Big token savings; pairs with Week 3.<br>2025–2026 年的模式：让 Agent 编写调用 MCP 工具的代码，而不是让每个工具结果都经过上下文。能大幅节省 token；与第 3 周配合。 | [Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp) |

---

## D. Papers (must-read vs optional)

**D. 论文（必读 vs 可选）**

| Paper<br>论文 | Year / venue<br>年份 / 会议 | Status<br>类别 | One-line contribution<br>一句话贡献 | Link<br>链接 |
|-------|--------------|--------|-----------------------|------|
| ReAct: Synergizing Reasoning and Acting | 2022 / ICLR 2023 | **Must**<br>**必读** | Interleaved thought→action→observation; the loop every agent still runs.<br>思考→行动→观察交替进行；至今每个 Agent 仍在运行的那个循环。 | [arXiv 2210.03629](https://arxiv.org/abs/2210.03629) |
| Toolformer | 2023 / NeurIPS 2023 | Optional<br>可选 | Self-supervised teaching of API calls; historical origin of "tools as tokens".<br>以自监督方式教模型调用 API；「工具即 token」的历史起源。 | [arXiv 2302.04761](https://arxiv.org/abs/2302.04761) |
| Reflexion | 2023 / NeurIPS 2023 | Optional<br>可选 | Verbal self-reflection as memory; explains why retry-with-critique works.<br>把语言化的自我反思当作记忆；解释了为什么「带批评的重试」有效。 | [arXiv 2303.11366](https://arxiv.org/abs/2303.11366) |
| MemGPT: LLMs as Operating Systems | 2023 | **Must**<br>**必读** | Memory hierarchy + paging for context; the intellectual root of Letta and most "agent memory" products.<br>记忆层级 + 上下文分页；Letta 和大多数「Agent 记忆」产品的思想源头。 | [arXiv 2310.08560](https://arxiv.org/abs/2310.08560) |
| Generative Agents | 2023 / UIST 2023 | Optional<br>可选 | Memory stream + reflection + planning; the simulation paper that popularised agent societies.<br>记忆流 + 反思 + 规划；让「Agent 社会」流行起来的那篇模拟论文。 | [arXiv 2304.03442](https://arxiv.org/abs/2304.03442) |
| AutoGen | 2023 | Optional<br>可选 | Multi-agent conversation as a programming model; useful history now that it merged into Agent Framework.<br>把多 Agent 对话作为一种编程模型；既然它已并入 Agent Framework，作为历史了解很有用。 | [arXiv 2308.08155](https://arxiv.org/abs/2308.08155) |
| ToolLLM | 2023 / ICLR 2024 | Optional<br>可选 | 16k real APIs + tool-retrieval; why tool selection degrades with large toolsets.<br>16k 个真实 API + 工具检索；解释了为什么工具集越大，工具选择效果越差。 | [arXiv 2307.16789](https://arxiv.org/abs/2307.16789) |
| SWE-agent (ACI) | 2024 / NeurIPS 2024 | **Must**<br>**必读** | Agent-computer interface design changes benchmark scores more than model swaps — the core lesson for platform builders.<br>Agent-计算机接口（ACI）的设计对基准分数的影响比换模型更大——这是平台构建者最核心的一课。 | [arXiv 2405.15793](https://arxiv.org/abs/2405.15793) |
| AgentBench | 2023 / ICLR 2024 | Optional<br>可选 | First broad multi-environment agent benchmark; good failure taxonomy.<br>第一个覆盖多种环境的综合性 Agent 基准；有很好的失败分类。 | [arXiv 2308.03688](https://arxiv.org/abs/2308.03688) |
| GAIA | 2023 / ICLR 2024 | **Must**<br>**必读** | Real assistant tasks that are easy for humans, hard for agents; the benchmark to quote when someone claims AGI.<br>对人类容易、对 Agent 困难的真实助手任务；有人宣称实现了 AGI 时就该引用的基准。 | [arXiv 2311.12983](https://arxiv.org/abs/2311.12983) |
| τ-bench (TAU-bench) | 2024 | **Must**<br>**必读** | Tool-agent-user interaction with domain policies — the closest public analogue to enterprise support agents.<br>带领域策略的工具-Agent-用户交互——与企业客服 Agent 最接近的公开对应物。 | [arXiv 2406.12045](https://arxiv.org/abs/2406.12045) |
| SWE-bench | 2023 / ICLR 2024 | **Must**<br>**必读** | Real GitHub issues + tests; taught the field that verifiable tasks are where agents win.<br>真实的 GitHub issue + 测试；让整个领域认识到，可验证的任务才是 Agent 的主场。 | [arXiv 2310.06770](https://arxiv.org/abs/2310.06770) |
| CodeAct | 2024 / ICML 2024 | Optional<br>可选 | Executable Python actions beat JSON tool calls on many agent tasks; justifies code-mode tools.<br>在许多 Agent 任务上，可执行的 Python 动作胜过 JSON 工具调用；为代码模式的工具提供了依据。 | [arXiv 2402.01030](https://arxiv.org/abs/2402.01030) |
| Agentic Context Engineering (ACE) | 2025, ICLR 2026 | **Must**<br>**必读** | Treat context as an evolving playbook; +10.6% on agents and +8.6% on finance over strong baselines, without labelled supervision. Updated v3, 2026-03.<br>把上下文当作不断演进的行动手册（playbook）；在无需标注监督的情况下，相比强基线在 Agent 任务上提升 +10.6%、在金融任务上提升 +8.6%。2026-03 更新为 v3。 | [arXiv 2510.04618](https://arxiv.org/abs/2510.04618) ✅ |
| A Survey of Context Engineering for LLMs | 2025 | Optional (reference)<br>可选（参考） | Taxonomy to look things up in rather than read end-to-end.<br>用来查阅的分类体系，而不是要从头读到尾的东西。 | [arXiv 2507.13334](https://arxiv.org/abs/2507.13334) |
| The Landscape of Agentic RL for LLMs | 2025 | Optional<br>可选 | Where RL-for-agents stands; enough to talk to ML teams credibly.<br>面向 Agent 的强化学习目前进展到了哪一步；足以让你与机器学习团队进行可信的对话。 | [arXiv 2509.02547](https://arxiv.org/abs/2509.02547) |
| Mem0 | 2025 | Optional<br>可选 | Production memory extraction/consolidation with latency/cost numbers.<br>生产级的记忆抽取/整合，附延迟/成本数据。 | [arXiv 2504.19413](https://arxiv.org/abs/2504.19413) |
| A-MEM: Agentic Memory | 2025 | Optional<br>可选 | Zettelkasten-style linked memory notes; contrasts with flat vector memory.<br>Zettelkasten（卡片盒笔记法）式的互相链接的记忆笔记；与扁平的向量记忆形成对比。 | [arXiv 2502.12110](https://arxiv.org/abs/2502.12110) |
| τ²-bench | 2025 | Optional<br>可选 | Dual-control conversational agents (both sides act); next-gen telecom-style domains.<br>双重控制的对话式 Agent（双方都会采取行动）；下一代电信类领域。 | [arXiv 2506.07982](https://arxiv.org/abs/2506.07982) |
| WebArena | 2023 | Optional<br>可选 | Reproducible web environments for agents; useful for eval design inspiration.<br>为 Agent 提供可复现的网页环境；有助于为评测设计提供灵感。 | [arXiv 2307.13854](https://arxiv.org/abs/2307.13854) |
| OSWorld | 2024 | Optional<br>可选 | Real-OS computer-use benchmark; calibrates how far computer-use agents actually are.<br>基于真实操作系统的电脑操作基准；用来校准电脑操作 Agent 实际上走到了哪一步。 | [arXiv 2404.07972](https://arxiv.org/abs/2404.07972) |

**Reading strategy:** read the four *Must* papers from 2022–2024 in Week 1–2 (they are short), then SWE-agent + τ-bench in Week 4 when you build evals. ACE is the one 2025–2026 paper to read closely — it is the current best mental model for context.

**阅读策略：** 在第 1–2 周读完 2022–2024 年的四篇*必读*论文（它们都很短），然后在第 4 周构建评测时读 SWE-agent + τ-bench。ACE 是 2025–2026 年唯一需要精读的论文——它是目前关于上下文最好的心智模型。

---

## E. Codebases to read or run (what to look at inside)

**E. 值得阅读或运行的代码库（以及里面该看什么）**

| Repo<br>仓库 | Lang<br>语言 | What to look at inside<br>里面该看什么 | How to use it<br>如何使用 | Link<br>链接 |
|------|------|------------------------|---------------|------|
| Anthropic Cookbook · `patterns/agents` | Python | Minimal implementations of prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimizer — a few files each.<br>提示词链、路由、并行化、编排者-工作者、评估者-优化者的最小实现——每种只有几个文件。 | **Read** in Week 1; copy the patterns into your own loop.<br>在第 1 周**阅读**；把这些模式复制到你自己的循环里。 | [Repo path](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) |
| OpenAI Cookbook | Python | Tool-calling recipes, structured outputs, evals notebooks.<br>工具调用示例、结构化输出、评测 notebook。 | **Run** selectively; ignore the product-launch notebooks.<br>有选择地**运行**；忽略那些产品发布类的 notebook。 | [Repo](https://github.com/openai/openai-cookbook) |
| smolagents | Python | A ~1k-line agent core: `CodeAgent`, tool decorators, executor, memory. The best "read the whole thing" agent codebase.<br>一个约 1k 行的 Agent 核心：`CodeAgent`、工具装饰器、执行器、记忆。最值得「把代码全部读一遍」的 Agent 代码库。 | **Read end-to-end** in Week 2.<br>在第 2 周**从头到尾阅读**。 | [Repo](https://github.com/huggingface/smolagents) |
| 12-factor-agents | Python/TS | Reference implementations showing pause/resume, human-in-the-loop tool calls, and stateless reducers.<br>参考实现，展示了暂停/恢复、人在回路的工具调用和无状态 reducer。 | **Run** the human-approval example in Week 8.<br>在第 8 周**运行**人工审批示例。 | [Repo](https://github.com/humanlayer/12-factor-agents) |
| MCP Python SDK + Servers | Python | Server primitives (tools/resources/prompts), transports, and reference servers (`filesystem`, `git`) as tool-design exemplars.<br>服务器原语（tools/resources/prompts）、传输方式，以及可作为工具设计范例的参考服务器（`filesystem`、`git`）。 | **Run** in Week 2; port one server to C#.<br>在第 2 周**运行**；把其中一个服务器移植到 C#。 | [SDK](https://github.com/modelcontextprotocol/python-sdk) · [Servers](https://github.com/modelcontextprotocol/servers) |
| MCP C# SDK | C# | Attribute-based tool declaration, DI integration, stdio/HTTP transports.<br>基于特性（attribute）的工具声明、依赖注入（DI）集成、stdio/HTTP 传输。 | **Build** your enterprise server with it (Week 8).<br>用它**构建**你的企业级服务器（第 8 周）。 | [Repo](https://github.com/modelcontextprotocol/csharp-sdk) |
| Microsoft Agent Framework | C#/Python/Go | `AIAgent` abstraction, agent sessions, middleware/filters, workflows, MCP integration, harness agent.<br>`AIAgent` 抽象、Agent 会话、中间件/过滤器、工作流、MCP 集成、harness Agent。 | **Port** your Week 1 agent in Week 8.<br>在第 8 周**移植**你第 1 周的 Agent。 | [Repo](https://github.com/microsoft/agent-framework) |
| SWE-agent | Python | ACI implementation: view/edit commands, search, guardrails, trajectory format.<br>ACI 实现：查看/编辑命令、搜索、护栏、轨迹格式。 | **Read** `agent/` + config in Week 7.<br>在第 7 周**阅读** `agent/` + 配置。 | [Repo](https://github.com/SWE-agent/SWE-agent) |
| OpenHands | Python | Event-stream architecture, runtime sandbox/container isolation, state management, delegation.<br>事件流架构、运行时沙箱/容器隔离、状态管理、委派。 | **Read** architecture docs, not the whole codebase.<br>**阅读**架构文档，而不是整个代码库。 | [Repo](https://github.com/All-Hands-AI/OpenHands) · [Paper](https://arxiv.org/abs/2407.16741) |
| Aider | Python | Repo map (tree-sitter ranking), edit formats (whole-file vs diff), git integration.<br>仓库地图（基于 tree-sitter 的排序）、编辑格式（整文件 vs diff）、git 集成。 | **Read** the repo-map module — great lesson in context selection.<br>**阅读** repo-map 模块——这是关于上下文选择的绝佳一课。 | [Repo](https://github.com/Aider-AI/aider) |
| LangGraph | Python/TS | Graph state, checkpointing, interrupts, subgraphs.<br>图状态、检查点、中断、子图。 | **Read** only if you adopt it.<br>只有在你采用它时才**阅读**。 | [Repo](https://github.com/langchain-ai/langgraph) · [Docs](https://docs.langchain.com/oss/python/langgraph/overview) |
| OpenAI Agents SDK | Python | Minimal handoff/guardrail/tracing primitives; readable in an afternoon.<br>极简的交接（handoff）/护栏/追踪原语；一个下午就能读完。 | **Read** for API design taste.<br>**阅读**它来培养 API 设计品味。 | [Repo](https://github.com/openai/openai-agents-python) |
| HelloAgents (中文) | Python | From-scratch framework written for teaching; mirrors the Hello-Agents book chapters.<br>为教学而从零编写的框架；与 Hello-Agents 一书的章节一一对应。 | **Run** alongside the Chinese course.<br>配合中文课程一起**运行**。 | [Repo](https://github.com/jjyaoao/helloagents) |
| Inspect (UK AISI) | Python | Serious eval framework: datasets, solvers, scorers, log viewer.<br>严肃的评测框架：数据集、求解器（solver）、评分器（scorer）、日志查看器。 | **Adopt** for Week 4 evals if you want rigour.<br>如果你追求严谨，就在第 4 周的评测中**采用**它。 | [Docs](https://inspect.aisi.org.uk/) · [Repo](https://github.com/UKGovernmentBEIS/inspect_ai) |
| Langfuse / Phoenix | Python/TS | Tracing, sessions, prompt management, eval scores.<br>追踪、会话、提示词管理、评测分数。 | **Instrument** one agent; traces are your debugging superpower.<br>给一个 Agent **接入埋点**；trace 是你调试时的超能力。 | [Langfuse](https://langfuse.com/) · [Phoenix](https://github.com/Arize-ai/phoenix) |

**Anti-pattern to avoid:** cloning 5 agent frameworks and reading none. Read **smolagents** fully, ship on **Agent Framework**, pick **one** eval tool.

**要避免的反模式：** 克隆了 5 个 Agent 框架，却一个都没读。完整读一遍 **smolagents**，用 **Agent Framework** 交付，只选**一个**评测工具。

---

## F. Books, newsletters, podcasts, conferences, communities

**F. 书籍、新闻通讯、播客、会议、社区**

**Books** (all optional; read 1, not 4)

**书籍**（均为可选；读 1 本就够，不必读 4 本）

| Book<br>书籍 | Why / verdict<br>理由 / 评价 | Link<br>链接 |
|------|---------------|------|
| ***AI Agents in Depth* / 《深入理解 AI Agent》** — 李博杰 (Bojie Li), v2.0 2026, Apache-2.0 | **Adopted as this repo's companion textbook.** Best free 2026 textbook: harness engineering, context engineering (KV cache, skills, compression), memory/RAG, tools/MCP, coding agents, interaction (voice/computer-use), evals (pass@k vs pass^k, failure attribution, significance), post-training, continual evolution, multi-agent taxonomy. **109 experiments** with ★ difficulty ratings. Chinese original; community EN translation. Not a replacement for the labs — see the gap table.<br>**已被本仓库采用为配套教材。** 2026 年最好的免费教材：harness 工程、上下文工程（KV cache、skills、压缩）、记忆/RAG、工具/MCP、编码 Agent、交互（语音/电脑操作）、评测（pass@k vs pass^k、失败归因、显著性）、后训练、持续进化、多 Agent 分类。**109 个实验**，带 ★ 难度评级。中文为原版；有社区英文译本。它不能替代本仓库的实验——参见差距对照表。 | [Repo](https://github.com/bojieli/ai-agent-book) ✅ · [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md) |
| *AI Engineering* — Chip Huyen (O'Reilly, 2025) | Best systems-level book: evals, RAG, finetuning, cost/latency. Chapters 6–9 cover agents and evals. Paywalled.<br>最好的系统层面书籍：评测、RAG、微调、成本/延迟。第 6–9 章涉及 Agent 和评测。需付费。 | [O'Reilly](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) 🔒 |
| *Build a Large Language Model (From Scratch)* — S. Raschka (Manning, 2024) | Only if you want model internals; excellent but ~40 h — do it after the capstone, not before.<br>只在你想了解模型内部原理时才读；非常出色，但需要约 40 小时——在结业项目之后再做，而不是之前。 | [Manning](https://www.manning.com/books/build-a-large-language-model-from-scratch) · [Repo](https://github.com/rasbt/LLMs-from-scratch) |
| *Hands-On Large Language Models* — Alammar & Grootendorst (O'Reilly, 2024) | Fast visual intuition for tokens/embeddings/attention; skippable if you already know transformers.<br>快速建立对 token/嵌入/注意力的直观理解；如果你已经了解 Transformer，可以跳过。 | [Book site](https://www.llm-book.com/) |
| 《Hello-Agents》 (free PDF, Chinese)<br>《Hello-Agents》（免费 PDF，中文） | The best free agent-engineering textbook in Chinese; see §G.<br>最好的免费中文 Agent 工程教材；见 §G。 | [Repo](https://github.com/datawhalechina/hello-agents) |

**Newsletters** (subscribe to 3 max): [Import AI](https://importai.substack.com/) (policy/research signal) · [The Batch](https://www.deeplearning.ai/the-batch/) (weekly industry) · [Latent Space](https://www.latent.space/) (AI-engineer practitioner) · [Interconnects](https://www.interconnects.ai/) (research analysis) · [Chip Huyen](https://newsletter.languagemodels.co/) · [One Useful Thing](https://www.oneusefulthing.org/) (adoption patterns) · [Simon Willison](https://simonwillison.net/) (tooling/scepticism) · [Hamel Husain](https://hamel.dev/) (evals).

**新闻通讯**（最多订阅 3 个）：[Import AI](https://importai.substack.com/)（政策/研究信号）· [The Batch](https://www.deeplearning.ai/the-batch/)（每周行业动态）· [Latent Space](https://www.latent.space/)（AI 工程师的实践视角）· [Interconnects](https://www.interconnects.ai/)（研究分析）· [Chip Huyen](https://newsletter.languagemodels.co/) · [One Useful Thing](https://www.oneusefulthing.org/)（落地采用模式）· [Simon Willison](https://simonwillison.net/)（工具/怀疑精神）· [Hamel Husain](https://hamel.dev/)（评测）。

**Podcasts:** [Latent Space](https://www.latent.space/) (best for agent engineers) · [The TWIML AI Podcast](https://twimlai.com/) (technical interviews) · [Cognitive Revolution](https://www.cognitiverevolution.ai/) (product/industry) · [No Priors](https://www.nopriors.com/) (leadership-level framing). Commute-sized: 1 episode/week, skip news roundups.

**播客：** [Latent Space](https://www.latent.space/)（最适合 Agent 工程师）· [The TWIML AI Podcast](https://twimlai.com/)（技术访谈）· [Cognitive Revolution](https://www.cognitiverevolution.ai/)（产品/行业）· [No Priors](https://www.nopriors.com/)（管理层视角的解读）。按通勤时长来安排：每周 1 集，跳过新闻汇总类节目。

**Conferences:** [AI Engineer World's Fair](https://www.ai.engineer/worldsfair/2026/) ⚠️ (San Francisco Moscone, typically June — the practitioner conference; talks land on YouTube free) · [AI Engineer Summit](https://www.ai.engineer/summit) ⚠️ (NYC, autumn) · [Interrupt](https://interrupt.langchain.com/) (LangChain's agent conference; talks online) · [NeurIPS](https://neurips.cc/) · [ICLR](https://iclr.cc/) (2026 papers, e.g. ACE). For Singapore: [AI Singapore](https://www.aisingapore.org/) runs community/AI-certification programmes and local events — the cheapest local network. Timezone note: SF events are 15–16 h behind SGT; conference videos are the realistic option during term.

**会议：** [AI Engineer World's Fair](https://www.ai.engineer/worldsfair/2026/) ⚠️（旧金山 Moscone 会展中心，通常在 6 月——面向实践者的会议；演讲视频会免费发布到 YouTube）· [AI Engineer Summit](https://www.ai.engineer/summit) ⚠️（纽约，秋季）· [Interrupt](https://interrupt.langchain.com/)（LangChain 的 Agent 会议；演讲可在线观看）· [NeurIPS](https://neurips.cc/) · [ICLR](https://iclr.cc/)（2026 年的论文，例如 ACE）。新加坡本地：[AI Singapore](https://www.aisingapore.org/) 举办社区/AI 认证项目和本地活动——这是成本最低的本地人脉网络。时区提示：旧金山的活动比新加坡时间（SGT）晚 15–16 小时；学期期间，看会议视频才是现实的选择。

**Communities:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) (practical, noisy) · [Hugging Face Discord](https://huggingface.co/join/discord) (course help) · [LangChain Forum](https://forum.langchain.com/) (framework Q&A) · MCP [Discord](https://discord.gg/6CSzBmMkjX) (invite may expire; find it via the docs) · Datawhale reader groups via [Hello-Agents](https://github.com/datawhalechina/hello-agents).

**社区：** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)（实用，但噪音大）· [Hugging Face Discord](https://huggingface.co/join/discord)（课程答疑）· [LangChain Forum](https://forum.langchain.com/)（框架问答）· MCP [Discord](https://discord.gg/6CSzBmMkjX)（邀请链接可能过期；可通过文档找到）· 通过 [Hello-Agents](https://github.com/datawhalechina/hello-agents) 加入 Datawhale 读者群。

---

## G. Chinese-language resources (中文资源)

| Resource<br>资源 | What it is<br>是什么 | Why it's worth your time<br>为什么值得花时间 | Link<br>链接 |
|----------|-----------|--------------------------|------|
| **《深入理解 AI Agent：设计原理与工程实践》** | 李博杰著，v2.0（2026-09-23），Apache-2.0 开源，10 章正文 + 109 个带 ★ 难度评级的实验。中文是正本，英文等 15 种语言为社区翻译。 | **本仓库采用的配套教材。** 你读中文正本会比英文译本快；上下文工程（KV Cache、Skills、状态栏、压缩）、记忆/RAG、工具/MCP、Coding Agent、评估（pass@k vs pass^k、失败归因、统计显著性）、后训练、持续进化、多 Agent 协作全部覆盖。第 10 章的信息增益判据和六种失效模式尤其适合对照第 6 周；第 9 章是从轨迹中学习的理论版，正好补 SendOS 的 distillation 闭环。 | [Repo](https://github.com/bojieli/ai-agent-book) ✅ · [在线阅读](https://bojieli.github.io/ai-agent-book/astro/) · [章节映射](../books/ai-agents-in-depth/CHAPTER-MAP.md) |
| **Hello-Agents《从零开始构建智能体》** | Datawhale open book: 16 chapters from agent history → ReAct/Plan-and-Solve/Reflection implemented by hand → Context Engineering → MCP/A2A/ANP → Agentic-RL (SFT→GRPO) → evals → 3 capstones. Free PDF + online.<br>Datawhale 的开源书籍：共 16 章，从 Agent 发展史 → 手写实现 ReAct/Plan-and-Solve/Reflection → 上下文工程 → MCP/A2A/ANP → Agentic-RL（SFT→GRPO）→ 评测 → 3 个结业项目。免费 PDF + 在线阅读。 | **Best Chinese resource, full stop.** Matches this track week-for-week; the Agentic-RL chapter is material no English course covers this hands-on. Mandarin-first means faster for you.<br>**最好的中文资源，没有之一。** 与本路线逐周对应；其中 Agentic-RL 一章的动手程度是任何英文课程都没有的。以中文为第一语言，意味着你读起来更快。 | [Repo](https://github.com/datawhalechina/hello-agents) ✅ · [在线阅读](https://datawhalechina.github.io/hello-agents/) |
| **Agent-Learning-Hub** | Datawhale's 2026-updated agent learning roadmap (published May 2026).<br>Datawhale 于 2026 年更新的 Agent 学习路线图（2026 年 5 月发布）。 | Use it to sanity-check sequencing; it is more Chinese-ecosystem-oriented (Dify/Coze/domestic models).<br>用它来检验学习顺序是否合理；它更偏向中文生态（Dify/Coze/国产模型）。 | [Repo](https://github.com/datawhalechina/Agent-Learning-Hub) |
| 李宏毅 (Hung-yi Lee) 生成式AI導論 | NTU lecture series (Traditional Chinese audio, slides). The 2024 edition remains the canonical GenAI course.<br>台湾大学（NTU）的系列讲座（繁体中文授课的音频、幻灯片）。2024 年版仍是经典的生成式 AI 课程。 | Best Chinese-language *lecture* explanation of how LLMs work; watch the transformer/agent lectures, skip the rest.<br>讲解 LLM 工作原理最好的中文*讲座*；看 Transformer/Agent 相关的几讲，其余跳过。 | [GenAI 2024](https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring.php) · [ML 2025](https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php) |
| 宝玉 (baoyu.io) | Translations/annotations of Anthropic/OpenAI engineering posts and agent guides.<br>Anthropic/OpenAI 工程文章和 Agent 指南的翻译/注解。 | High-fidelity Chinese versions of exactly the essays in §C — good for a second pass or for sharing with teammates.<br>恰好是 §C 中那些文章的高保真中文版——适合第二遍阅读，或分享给团队成员。 | [baoyu.io](https://baoyu.io/) |
| Prompt Engineering Guide 中文版 | DAIR.AI guide, Chinese translation.<br>DAIR.AI 指南的中文译本。 | Quick reference for prompting techniques; do not read cover-to-cover.<br>提示词技巧的速查参考；不要从头读到尾。 | [中文版](https://www.promptingguide.ai/zh) |
| 机器之心 / 量子位 | AI news and paper summaries in Chinese.<br>中文的 AI 新闻和论文解读。 | Fast scanning of 2026 releases; treat claims sceptically and follow the source link.<br>快速浏览 2026 年的新发布；对其中的说法保持怀疑，并顺着原始来源链接去核实。 | [机器之心](https://www.jiqizhixin.com/) · [量子位](https://www.qbitai.com/) |
| 扣子 Coze 文档 | ByteDance low-code agent platform docs.<br>字节跳动低代码 Agent 平台的文档。 | Relevant if your enterprise also ships low-code agents; not a substitute for learning the loop.<br>如果你的企业也在交付低代码 Agent，就与你相关；但它不能替代对 Agent 循环的学习。 | [Docs](https://www.coze.cn/docs) |
| 阿里云百炼 Model Studio / 智谱 / Qwen | Domestic model-platform and agent docs.<br>国产模型平台及 Agent 文档。 | Useful if your platform must support domestic models or data residency.<br>如果你的平台必须支持国产模型或满足数据驻留要求，就很有用。 | [百炼](https://help.aliyun.com/zh/model-studio/) · [智谱](https://docs.bigmodel.cn/) · [Qwen](https://qwen.readthedocs.io/) |
| 掘金 (juejin.cn) | Chinese dev blog platform.<br>中文开发者博客平台。 | Occasional excellent engineering post-mortems; quality varies wildly. Search by concrete error messages, not by "Agent 入门".<br>偶尔有出色的工程复盘文章；质量参差不齐。用具体的错误信息去搜索，而不是搜「Agent 入门」。 | [juejin.cn](https://juejin.cn/) |

**Language strategy for Singapore:** read English primary sources (they are always first), use Chinese resources for reinforcement and for explaining concepts to Chinese-speaking stakeholders. Hello-Agents is the one Chinese resource worth going through systematically.

**身在新加坡的语言策略：** 以英文一手资料为主（它们总是最先发布），用中文资源来巩固，以及向说中文的利益相关方解释概念。Hello-Agents 是唯一值得系统学完的中文资源。

---

## H. If you only have 50 hours

**H. 如果你只有 50 小时**

| # | Block<br>模块 | Hrs<br>小时 | Why it made the cut<br>入选理由 | Source<br>来源 |
|---|-------|-----|---------------------|--------|
| 1 | Building effective agents + 12-Factor Agents | 3 | Shared vocabulary + production checklist<br>通用词汇 + 生产检查清单 | [Essay](https://www.anthropic.com/engineering/building-effective-agents) · [Repo](https://github.com/humanlayer/12-factor-agents) |
| 2 | Chip Huyen "Agents" + ReAct paper<br>Chip Huyen 的「Agents」+ ReAct 论文 | 3 | Systems frame + the loop's origin<br>系统框架 + 循环的起源 | [Post](https://huyenchip.com/2025/01/07/agents.html) · [arXiv](https://arxiv.org/abs/2210.03629) |
| 3 | Build a ReAct loop from scratch (no framework)<br>从零构建一个 ReAct 循环（不用框架） | 6 | Nothing teaches faster than owning the loop<br>没有什么比亲手掌控循环学得更快 | [HF Agents Course §1](https://huggingface.co/learn/agents-course) |
| 4 | Tool design + MCP server (Python, then C#)<br>工具设计 + MCP 服务器（先 Python，后 C#） | 7 | Directly reusable in your .NET platform<br>可直接复用到你的 .NET 平台 | [Anthropic tools](https://www.anthropic.com/engineering/writing-tools-for-agents) · [MCP](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro) |
| 5 | Context engineering + compaction<br>上下文工程 + 压缩 | 4 | The 2026 differentiating skill<br>2026 年拉开差距的技能 | [Essay](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| 6 | Evals: 20-case golden set + judge + traces<br>评测：20 个用例的黄金集 + 评审 + trace | 8 | Everything else is guesswork without this<br>没有这一块，其他一切都只是猜测 | [Hamel](https://hamel.dev/blog/posts/evals/) · [Inspect](https://inspect.aisi.org.uk/) |
| 7 | Read smolagents end-to-end<br>从头到尾阅读 smolagents | 4 | Whole-agent comprehension in one repo<br>在一个仓库里理解完整的 Agent | [Repo](https://github.com/huggingface/smolagents) |
| 8 | Multi-agent research system post + one experiment<br>多 Agent 研究系统那篇文章 + 一个实验 | 4 | Know when multi-agent pays and when it does not<br>弄清多 Agent 什么时候划算、什么时候不划算 | [Post](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 9 | SWE-agent ACI + prompt-injection demo/mitigation<br>SWE-agent ACI + 提示词注入演示/缓解 | 5 | Security is the enterprise blocker<br>安全是企业落地的拦路虎 | [Paper](https://arxiv.org/abs/2405.15793) · [Essay](https://www.anthropic.com/engineering/managed-agents) |
| 10 | Microsoft Agent Framework port + MCP C# SDK<br>移植到 Microsoft Agent Framework + MCP C# SDK | 6 | Makes it your day job, not a hobby<br>让它成为你的本职工作，而不是业余爱好 | [Docs](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) · [SDK](https://github.com/modelcontextprotocol/csharp-sdk) |
| **Total**<br>**合计** | | **50** | | |

**Deliberately not in the 50:** fine-tuning/RL (Week 9), classical multi-agent theory, vector-database internals, computer-use, LangGraph mastery. Those are 2027 problems for you.

**刻意没有放进这 50 小时的内容：** 微调/强化学习（第 9 周）、经典多智能体理论、向量数据库内部原理、电脑操作、精通 LangGraph。对你来说，那些是 2027 年才需要考虑的问题。

---

## I. Deliberately skipped hype (and why)

**I. 刻意跳过的炒作内容（以及原因）**

- **"Build 10 agents in 10 days" listicles and awesome-* aggregator repos.** Breadth without a loop, evals or failure analysis teaches nothing; they also rot within months. Skip.

  **「10 天构建 10 个 Agent」式的清单文章，以及 awesome-* 聚合仓库。** 只有广度，没有循环、评测或失败分析，什么也学不到；而且它们几个月内就会过时。跳过。

- **Framework tourism (CrewAI / AutoGen / Swarm / Dify / n8n first).** OpenAI's [Swarm](https://github.com/openai/swarm) is explicitly an educational experiment superseded by the Agents SDK; AutoGen and Semantic Kernel have been folded into [Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview). Learning a framework's API before you know what the framework abstracts is backwards. Build the loop first.

  **框架观光（一上来就学 CrewAI / AutoGen / Swarm / Dify / n8n）。** OpenAI 的 [Swarm](https://github.com/openai/swarm) 明确只是一个教学实验，已被 Agents SDK 取代；AutoGen 和 Semantic Kernel 已被并入 [Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)。在你还不知道一个框架抽象了什么之前就去学它的 API，是本末倒置。先构建循环。

- **Low-code platforms (Coze, Dify, n8n) as a learning path.** They are shipping tools for product teams, not concept-builders. Read the docs when your employer adopts one.

  **把低代码平台（Coze、Dify、n8n）当作学习路径。** 它们是供产品团队交付用的工具，而不是帮你建立概念的工具。等你的雇主采用其中某一个时再去读文档。

- **Prompt-engineering mega-courses and "secret prompt" content.** Diminishing returns; context engineering subsumes most of it.

  **提示词工程大型课程和「秘密提示词」类内容。** 收益递减；上下文工程已经涵盖了其中大部分。

- **Vector-database deep dives and "RAG from scratch" curricula.** For agents, agentic search (`grep`, SQL, file trees) often beats embeddings, and you can learn retrieval in a week. Defer.

  **向量数据库深度剖析和「从零实现 RAG」课程。** 对 Agent 而言，Agent 式搜索（`grep`、SQL、文件树）往往胜过嵌入，而检索你一周就能学会。推后再学。

- **Fine-tuning / pre-training courses as a first step.** Premature: 95% of production value in your platform comes from tools, context and evals. See Week 9 decision memo instead.

  **把微调 / 预训练课程作为第一步。** 为时过早：你的平台中 95% 的生产价值来自工具、上下文和评测。请改看第 9 周的决策备忘录。

- **"Fully autonomous AI employee" / agent-marketplace-token content.** Unfalsifiable claims, no eval methodology. The [GAIA](https://arxiv.org/abs/2311.12983) and [τ-bench](https://arxiv.org/abs/2406.12045) numbers are the honest counterweight.

  **「完全自主的 AI 员工」/ Agent 市场代币类内容。** 无法证伪的说法，没有评测方法论。[GAIA](https://arxiv.org/abs/2311.12983) 和 [τ-bench](https://arxiv.org/abs/2406.12045) 的数据才是诚实的制衡。

- **Computer-use as a first project.** Impressive demos, fragile and expensive in practice; read [OSWorld](https://arxiv.org/abs/2404.07972) before investing.

  **把电脑操作作为第一个项目。** 演示很惊艳，但实际使用中脆弱又昂贵；投入之前先读 [OSWorld](https://arxiv.org/abs/2404.07972)。

- **Paid "agent engineer bootcamps" and certifications.** The free vendor + Berkeley/HF material is better and more current; certificates carry little weight compared with a traced, evaluated capstone in your portfolio.

  **付费的「Agent 工程师训练营」和认证。** 免费的厂商资料 + Berkeley/HF 的资料更好、更新；与作品集中一个有 trace、经过评测的结业项目相比，证书几乎没有分量。

- **Benchmark-chasing (SWE-bench leaderboard drama).** Useful as context, not as a goal; your enterprise tasks are not public benchmarks.

  **追逐基准分数（SWE-bench 排行榜风波）。** 作为背景有用，但不应作为目标；你的企业任务并不是公开基准。

---

## J. Link-verification ledger (2026-10-18)

**J. 链接验证记录（2026-10-18）**

**Method:** HTTP status checks against every cited URL; 15 highest-value pages fetched with content read (`✅`): Anthropic building-effective-agents, effective context engineering, managed agents, effective harnesses, 12-factor repo, HF Agents Course, Microsoft AI Agents for Beginners, Microsoft Agent Framework overview, Berkeley MOOC (F24 + root), DeepLearning.AI catalog, MCP docs (2026-07-28), Hello-Agents README, ACE paper, LangChain Academy (JS-rendered shell — existence only).

**方法：** 对每个引用的 URL 做 HTTP 状态检查；抓取并阅读了价值最高的 15 个页面的内容（`✅`）：Anthropic 的 building-effective-agents、effective context engineering、managed agents、effective harnesses，12-factor 仓库，HF Agents Course，Microsoft AI Agents for Beginners，Microsoft Agent Framework 概览，Berkeley MOOC（F24 + 根页面），DeepLearning.AI 课程目录，MCP 文档（2026-07-28），Hello-Agents README，ACE 论文，LangChain Academy（JS 渲染的空壳页面——仅确认存在）。

**Dead or changed (use the replacement, not the original):**

**已失效或已变更（请使用替代链接，而不是原链接）：**

- `https://llmagents-learning.org/` → **redirects** to `/sp25` (Spring 2025). There is **no 2026 edition**; the Fall 2024 and Spring 2025 archives are the current content. Certificates are closed.

  `https://llmagents-learning.org/` → **重定向**到 `/sp25`（2025 年春季）。**没有 2026 年版**；2024 年秋季和 2025 年春季的归档就是当前内容。证书已关闭。

- `https://strandsagents.com/latest/` (linked from Anthropic's essay) → **404**; the project root [strandsagents.com](https://strandsagents.com/) resolves. Strands is Python/TypeScript-focused; I found no first-class .NET SDK, so verify before prioritising it.

  `https://strandsagents.com/latest/`（Anthropic 的文章中有此链接）→ **404**；项目根页面 [strandsagents.com](https://strandsagents.com/) 可以正常访问。Strands 主要面向 Python/TypeScript；我没有找到一等支持的 .NET SDK，所以在优先考虑它之前请先核实。

- `https://simonwillison.net/2025/Sep/18/agents/` → request **failed/timed out** on 2026-10-18; the [agents tag page](https://simonwillison.net/tags/agents/) and blog root resolve normally, so treat the specific post URL as **uncertain** and navigate from the tag page.

  `https://simonwillison.net/2025/Sep/18/agents/` → 在 2026-10-18 请求**失败/超时**；[agents 标签页](https://simonwillison.net/tags/agents/) 和博客根页面都能正常访问，因此请把这篇具体文章的 URL 视为**不确定**，从标签页进入。

- `https://github.com/langchain-ai/langgraph/tree/main/docs/docs/tutorials`, `https://github.com/openai/openai-cookbook/tree/main/examples/agents`, `https://github.com/letta-ai/letta-quickstart` → **404** (paths moved); replaced in this document with the [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview), [cookbook root](https://github.com/openai/openai-cookbook), [Letta docs](https://docs.letta.com/).

  `https://github.com/langchain-ai/langgraph/tree/main/docs/docs/tutorials`、`https://github.com/openai/openai-cookbook/tree/main/examples/agents`、`https://github.com/letta-ai/letta-quickstart` → **404**（路径已移动）；本文档中已分别替换为 [LangGraph 文档](https://docs.langchain.com/oss/python/langgraph/overview)、[cookbook 根目录](https://github.com/openai/openai-cookbook)、[Letta 文档](https://docs.letta.com/)。

- `https://conf.langchain.com/` → **DNS/connection error**; the live conference site is [interrupt.langchain.com](https://interrupt.langchain.com/).

  `https://conf.langchain.com/` → **DNS/连接错误**；当前在线的会议网站是 [interrupt.langchain.com](https://interrupt.langchain.com/)。

- `https://blog.google/technology/developers/introducing-agent-development-kit/` → error; use [ADK docs](https://google.github.io/adk-docs/) or the [repo](https://github.com/google/adk-python).

  `https://blog.google/technology/developers/introducing-agent-development-kit/` → 出错；请使用 [ADK 文档](https://google.github.io/adk-docs/) 或 [仓库](https://github.com/google/adk-python)。

- `https://speech.ee.ntu.edu.tw/~hylee/genai/2025-spring.php` → **404**; Lee's GenAI course site only exists for 2024 (`/genai/2024-spring.php`); his 2025 course is the ML course at `/ml/2025-spring.php`.

  `https://speech.ee.ntu.edu.tw/~hylee/genai/2025-spring.php` → **404**；李宏毅的生成式 AI 课程网站只有 2024 年版（`/genai/2024-spring.php`）；他 2025 年的课程是位于 `/ml/2025-spring.php` 的机器学习课程。

**Paywalled or bot-blocked (real for humans, 403 to scripts):**

**付费墙或屏蔽爬虫（人类可以访问，对脚本返回 403）：**

- [O'Reilly — AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) 🔒 (subscription; check whether your university library — NUS/NTU — provides O'Reilly Learning access).

  [O'Reilly — AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) 🔒（需要订阅；可以查一下你的大学图书馆——NUS/NTU——是否提供 O'Reilly Learning 的访问权限）。

- `openai.com/index/*` pages (e.g. BrowseComp, Agents SDK announcement, new agent tools) → 403 to automated requests; read via search/Google cache or the [OpenAI docs](https://platform.openai.com/docs/guides/agents).

  `openai.com/index/*` 页面（例如 BrowseComp、Agents SDK 发布公告、新的 Agent 工具）→ 对自动化请求返回 403；可通过搜索/Google 缓存或 [OpenAI 文档](https://platform.openai.com/docs/guides/agents) 阅读。

- `ruanyifeng.com` → 403 to bots; works in a browser (not cited above).

  `ruanyifeng.com` → 对爬虫返回 403；在浏览器中可正常访问（上文未引用）。

- [OpenAI practical guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) → **HTTP 200 but PDF**: my fetch tool cannot extract PDF text, so I verified existence/status only, not page content. Treat as *exists, unread*.

  [OpenAI 实践指南](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) → **HTTP 200，但是 PDF**：我的抓取工具无法提取 PDF 文本，所以只验证了存在性/状态，没有验证页面内容。请视为*存在，未读*。

**Redirects to expect (`⚠️`, resolve in browser):** `deeplearning.ai/short-courses/` → `/courses`; `deeplearning.ai/courses/agentic-ai/` → 308 (canonical redirect); `ai.engineer/worldsfair/2026/` and `ai.engineer/summit` → 308; `anthropic.com/engineering/building-agents-with-the-claude-agent-sdk` and `.../claude-code-best-practices` → 308; `docs.bigmodel.cn` → 308; MCP docs unversioned URL → versioned `/docs/2026-07-28/`.

**预期会遇到的重定向（`⚠️`，在浏览器中可正常访问）：** `deeplearning.ai/short-courses/` → `/courses`；`deeplearning.ai/courses/agentic-ai/` → 308（规范化重定向）；`ai.engineer/worldsfair/2026/` 和 `ai.engineer/summit` → 308；`anthropic.com/engineering/building-agents-with-the-claude-agent-sdk` 和 `.../claude-code-best-practices` → 308；`docs.bigmodel.cn` → 308；MCP 文档不带版本号的 URL → 带版本号的 `/docs/2026-07-28/`。

**Stability caveats:** `eugeneyan.com` root timed out (article URL 200s); Discord invites expire; 2027 conference dates are unpublished. Re-run this status check quarterly — roughly 10% of this list moves within a year, so treat it as dated **2026-10-18**.

**稳定性注意事项：** `eugeneyan.com` 根页面超时（文章 URL 返回 200）；Discord 邀请链接会过期；2027 年的会议日期尚未公布。每季度重新运行一次这项状态检查——这份清单大约有 10% 会在一年内变动，因此请把它视为截至 **2026-10-18** 的版本。

---

### If you remember one thing

**如果只记住一件事**

Read *Building effective agents*, *Effective context engineering*, Chip Huyen's *Agents*, *12-Factor Agents* and Hamel's evals post (≈4 h). Build a ReAct loop by hand (6 h), add tools + an MCP server (7 h), build a 20-case eval harness with traces (8 h), read `smolagents` end-to-end (4 h), then port it to [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) with the [C# MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) (6 h). That is the whole game; everything else here is depth, optional research, or Chinese-language reinforcement.

读 *Building effective agents*、*Effective context engineering*、Chip Huyen 的 *Agents*、*12-Factor Agents* 和 Hamel 的评测文章（≈4 小时）。手写一个 ReAct 循环（6 小时），加上工具 + 一个 MCP 服务器（7 小时），构建一个带 trace 的 20 用例评测 harness（8 小时），从头到尾读一遍 `smolagents`（4 小时），然后借助 [C# MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk) 把它移植到 [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)（6 小时）。这就是全部要点；这里的其他内容都是深入延伸、可选的研究，或中文的巩固材料。
