# Concept Notes

**概念笔记**

Nine just-in-time notes, one per mechanism you build. They are **not reference material to read later** — each one is 25 minutes before its lab, and it exists to explain *why* the failing tests are shaped the way they are. Every note answers the same question first: **what failure does this mechanism prevent?**

九篇即时（just-in-time）笔记，每篇对应你要构建的一个机制。它们**不是留到以后再读的参考资料**——每篇都安排在对应实验（lab）之前用 25 分钟阅读，存在的意义是解释*为什么*那些失败的测试会是现在这个样子。每篇笔记都会首先回答同一个问题：**这个机制防止的是什么失败？**

Read the note, answer its five questions in your own words, then open the lab. After the lab's tests are green, re-answer the five questions — if you still miss one, you have found the gap the lab did not close.

先读笔记，用自己的话回答其中的五个问题，然后再打开实验。等实验的测试全部通过（变绿）后，再重新回答这五个问题——如果仍有一个答不上来，你就找到了实验没有补上的那个缺口。

## The contract for every note

**每篇笔记的约定**

| Section<br>章节 | What it gives you<br>能带给你什么 |
|---|---|
| **The failure mode this prevents**<br>**本机制防止的失败模式** | A concrete incident story — the bug this week's mechanism is designed to make impossible<br>一个具体的事故故事——本周的机制正是为了让这个 bug 不可能发生而设计的 |
| **If you remember five things**<br>**如果只记住五件事** | The minimum viable mental model; read this first if you are short on time<br>最小可用的心智模型；时间紧的话先读这一节 |
| **The model in one page**<br>**一页看懂模型** | Mechanism, numbers with sources, and the one code sketch worth internalising<br>机制、附带来源的数字，以及一段值得内化的代码草图 |
| **Common misconceptions**<br>**常见误解** | Belief → reality → consequence; the fastest way to find what you have wrong<br>认知 → 现实 → 后果；找出自己哪里理解错了的最快方式 |
| **How this shows up in SendOS**<br>**在 SendOS 中如何体现** | 2–4 real mechanisms from the platform you work on, so the transfer is explicit<br>来自你所工作的平台的 2–4 个真实机制，让知识迁移变得明确 |
| **Check yourself**<br>**自测** | Five questions, no answers. If you cannot answer one, re-read that section before the lab<br>五个问题，不提供答案。如果有一个答不上来，就在做实验前重读对应的小节 |
| **Reading**<br>**延伸阅读** | 2–4 primary sources, ranked; the full map is in [research 04](../research/04-learning-resources.md)<br>2–4 个一手资料，按优先级排序；完整的资源地图见 [research 04](../research/04-learning-resources.md) |

## Index

**索引**

| # | Note<br>笔记 | Weeks<br>周次 | Read before<br>阅读时机 | Lab<br>实验 | Grounded in<br>依据 |
|---|---|---|---|---|---|
| 01 | [The agent loop](01-agent-loop.md)<br>Agent 循环 | 1–2 | Week 1, day 1<br>第 1 周第 1 天 | [`week01-provider`](../../labs/week01-provider/README.md), [`week02-agent-loop`](../../labs/week02-agent-loop/README.md) | [research 01 §1–2](../research/01-agent-architecture-sota.md) |
| 02 | [Tool design](02-tool-design.md)<br>工具设计 | 2 | Week 2, before the loop build<br>第 2 周，构建循环之前 | [`week02-agent-loop`](../../labs/week02-agent-loop/README.md) | [research 01 §1.4](../research/01-agent-architecture-sota.md), [research 02 §2](../research/02-frameworks-protocols.md) |
| 03 | [Context engineering](03-context-engineering.md)<br>上下文工程 | 3–4 | Week 3 (prompts as assets), re-read week 4<br>第 3 周（提示词即资产），第 4 周重读 | [`week03-structured-output`](../../labs/week03-structured-output/README.md), [`week04-context-memory`](../../labs/week04-context-memory/README.md) | [research 01 §3](../research/01-agent-architecture-sota.md) |
| 04 | [Memory](04-memory.md)<br>记忆 | 4 | Week 4, after note 03<br>第 4 周，在笔记 03 之后 | [`week04-context-memory`](../../labs/week04-context-memory/README.md) | [research 01 §4](../research/01-agent-architecture-sota.md) |
| 05 | [MCP and interoperability](05-mcp-interop.md)<br>MCP 与互操作性 | 5 | Week 5, with the current spec open<br>第 5 周，同时打开当前规范 | [`week05-mcp`](../../labs/week05-mcp/README.md) | [research 02 §1](../research/02-frameworks-protocols.md), [research 01 §10](../research/01-agent-architecture-sota.md) |
| 06 | [Orchestration and approval](06-orchestration.md)<br>编排与审批 | 6 | Week 6<br>第 6 周 | [`week06-squads`](../../labs/week06-squads/README.md) | [research 01 §2, §6](../research/01-agent-architecture-sota.md), [research 05 §4.5](../research/05-sendos-concept-map.md) |
| 07 | [Evals and observability](07-evals-observability.md)<br>评测与可观测性 | 7 | Week 7<br>第 7 周 | [`week07-evals`](../../labs/week07-evals/README.md) | [research 03 §1–2](../research/03-production-evals-ops.md) |
| 08 | [Security and governance](08-security-governance.md)<br>安全与治理 | 8 | Week 8<br>第 8 周 | [`week08-security`](../../labs/week08-security/README.md) | [research 03 §3–7](../research/03-production-evals-ops.md) |
| 09 | [Production: durability, cost, checks](09-production.md)<br>生产化：持久性、成本、检查 | 9+ | Week 9<br>第 9 周 | [`week09-capstone`](../../labs/week09-capstone/README.md) | [research 03 §4–8](../research/03-production-evals-ops.md) |

## Dependencies between notes

**笔记之间的依赖关系**

> Lab links above point at each week's brief; those files land with the lab scaffolds, so a link may 404 for a few days while a week is being built. The note and the weekly brief in [`docs/plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md) stay authoritative in the meantime.
>
> 上面的实验链接指向每周的实验说明；这些文件会随实验脚手架一起上线，因此在某一周还在构建期间，链接可能会有几天返回 404。在此期间，以本笔记和 [`docs/plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md) 中的每周说明为准。

The notes are numbered in build order, but three dependencies are worth respecting:

这些笔记按构建顺序编号，但有三处依赖关系值得遵守：

- **01 before 02.** Tool design only makes sense once you know that the loop appends observations and checks budgets; a tool is the action surface of a loop you have already built.

  **先 01 后 02。** 只有当你知道循环会追加观察结果并检查预算之后，工具设计才有意义；工具是你已经构建好的那个循环的行动界面。

- **03 before 04.** Context engineering keeps one run coherent; memory is what survives between runs. Building memory first produces a vector database with no write policy and no eval.

  **先 03 后 04。** 上下文工程让单次运行保持连贯；记忆则是在多次运行之间留存下来的东西。先构建记忆，得到的只会是一个没有写入策略、也没有评测（eval）的向量数据库。

- **02 before 05.** MCP is a transport and discovery layer on top of the tool contract you designed in week 2; if tool descriptions and schemas are vague locally, they are vague over the wire too.

  **先 02 后 05。** MCP 是建立在你第 2 周设计的工具契约之上的传输与发现层；如果工具描述和 schema 在本地就含糊不清，那么通过网络传输时同样含糊不清。

Notes 06–09 assume the earlier mechanisms exist. They are still readable standalone, but the SendOS references land harder after the labs.

笔记 06–09 假定前面的机制都已存在。它们仍然可以单独阅读，但做完实验之后，其中关于 SendOS 的引用会更有感触。

## How to use them with the rest of the repo

**如何与仓库其他部分配合使用**

- **Before the week:** read the week's note (25 min), write three goals for the week, and skim the week's lab brief.

  **每周开始前：** 阅读本周的笔记（25 分钟），写下本周的三个目标，并浏览本周的实验说明。

- **During the week:** keep the note open next to the failing tests. The "Common misconceptions" table is the fastest debugging heuristic when a test fails for a conceptual reason.

  **本周进行中：** 把笔记开在失败的测试旁边。当测试因概念性原因失败时，“常见误解”表格是最快的调试启发式工具。

- **Saturday:** answer the five questions from memory, then write the weekly teach-back. The [glossary](../glossary.md) and weekly flashcards are the spaced-repetition layer; this folder is the just-in-time layer.

  **周六：** 凭记忆回答五个问题，然后写本周的复述讲解（teach-back）。[术语表](../glossary.md)和每周闪卡是间隔重复层；这个文件夹则是即时学习层。

- **When you are stuck:** the relevant section of a note plus the lab's hints should unblock you; if not, ask the tutor with the test name and what you tried.

  **卡住的时候：** 笔记中的相关小节加上实验的提示应该能帮你解围；如果还不行，就带着测试名和你已经尝试过的做法去问导师。

- **Companion textbook:** each note's *Reading* section points at the matching chapter of [*AI Agents in Depth*](../books/ai-agents-in-depth/README.md) v2.0 — deeper theory plus 109 experiments. The week-by-week map, reading paths and the gap analysis are in [CHAPTER-MAP](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套教材：** 每篇笔记的*延伸阅读*小节都指向 [*AI Agents in Depth*](../books/ai-agents-in-depth/README.md) v2.0 中对应的章节——更深入的理论外加 109 个实验。逐周对照表、阅读路径和差距分析见 [CHAPTER-MAP](../books/ai-agents-in-depth/CHAPTER-MAP.md)。

The full nine-week schedule lives in [`docs/plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md); the lab index is [`labs/README.md`](../../labs/README.md); the research reports these notes compress are in [`docs/research/`](../research/01-agent-architecture-sota.md).

完整的九周日程见 [`docs/plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md)；实验索引是 [`labs/README.md`](../../labs/README.md)；这些笔记所浓缩的研究报告位于 [`docs/research/`](../research/01-agent-architecture-sota.md)。

## Scope and honesty

**范围与诚实性**

These notes deliberately compress. Where a claim is contested, unverified, or based on 2025-era models, the research report says so in its §10 — and you should treat it as a live question rather than settled fact. The most important habit to build from this folder: **every number has a source, and every mechanism has a failure mode it exists to prevent.**

这些笔记是有意压缩过的。凡是有争议、未经验证或基于 2025 年代模型的论断，研究报告都会在其 §10 中说明——你应当把它当作一个仍在讨论中的问题，而不是定论。从这个文件夹里最应该养成的习惯是：**每个数字都有来源，每个机制都有它要防止的失败模式。**
