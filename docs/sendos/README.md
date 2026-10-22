# `docs/sendos/` — the SendOS bridge

**`docs/sendos/` —— 通往 SendOS 的桥梁**

Everything needed to turn nine weeks of agent-engineering labs into **readable, contributable
SendOS expertise**. This folder is the bridge between the Python course in `agentlab/` and the
.NET platform the learner interns on (`D:\DevRepo\SendProjects\SendOS\SendOs`; on macOS/Linux, substitute your local SendOS checkout path).

把九周的 Agent 工程实验（lab）转化为**看得懂、能贡献的 SendOS 专业能力**所需的一切都在这里。这个文件夹是 `agentlab/` 中的 Python 课程与学习者实习所在的 .NET 平台（`D:\DevRepo\SendProjects\SendOS\SendOs`；在 macOS/Linux 上请替换为你本地 SendOS 代码检出的路径）之间的桥梁。

> **Living documents — code wins over docs.** These pages were verified against the source on
> **2026-10-18**. The platform moves faster than its own documentation; when a claim here and the
> code disagree, **the code is right**, and fixing the page is a contribution, not housekeeping.
>
> **活文档 —— 代码优先于文档。** 这些页面于 **2026-10-18** 对照源码做过核实。平台演进的速度快于它自己的文档；当这里的某个说法与代码不一致时，**以代码为准**，而修正这个页面本身就是一项贡献，而不是杂务。

---

## Contents

**目录**

| File<br>文件 | What it is<br>是什么 | When you use it<br>何时使用 |
|---|---|---|
| [`CONCEPT-MAP.md`](./CONCEPT-MAP.md) | The evidence base: what SendOS actually implements, mapped to industry terms, with status labels, ranked learning topics and the six mechanisms worth rebuilding in miniature<br>证据库：SendOS 实际实现了什么，对应到业界术语，附带状态标签、排好序的学习主题，以及值得做成微缩版重建的六个机制 | **Reference.** Read §0 once, then §4 for each mechanism. This is the page you cite when someone asks "does SendOS really do X?"<br>**参考资料。** §0 读一遍，然后每个机制读对应的 §4。当有人问"SendOS 真的做了 X 吗？"时，你引用的就是这一页 |
| [`BRIDGE.md`](./BRIDGE.md) | The week-by-week bridge: for each learning-plan week 1–9, which SendOS files to read, three questions, what maps cleanly vs differs, and a 30-minute timebox. Answers in a collapsed appendix<br>逐周桥接：针对学习计划的第 1–9 周，列出要读哪些 SendOS 文件、三个问题、哪些能干净对应、哪些有差异，以及 30 分钟的时间盒。答案在折叠的附录中 | **Every week**, once, for 30 minutes. The "Transfer" gate of the plan<br>**每周**一次，每次 30 分钟。这是计划中的"迁移（Transfer）"关卡 |
| [`READING-ORDER.md`](./READING-ORDER.md) | A 10-step reading order (~1 day total) plus three first-contribution candidates with acceptance criteria<br>一个 10 步的阅读顺序（总计约 1 天），外加三个带验收标准的首次贡献候选任务 | **Once**, in week 1–2; then again when you pick your first task<br>在第 1–2 周读**一次**；挑选第一个任务时再读一次 |
| [`../../dotnet/`](../../dotnet/) | The C# bridge labs: `ProviderBridge` (week 1) and `StructuredDecisionBridge` (week 3), each with an offline self-test<br>C# 桥接实验：`ProviderBridge`（第 1 周）和 `StructuredDecisionBridge`（第 3 周），各自带有一个离线自测 | **Week 1 and week 3**, as the language bridge to the C# codebase<br>**第 1 周和第 3 周**，作为通往 C# 代码库的语言桥梁 |

Primary inputs: [`../research/05-sendos-concept-map.md`](../research/05-sendos-concept-map.md) (the
source report) and [`../plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md) (weekly objectives).

主要输入：[`../research/05-sendos-concept-map.md`](../research/05-sendos-concept-map.md)（源报告）和 [`../plan/LEARNING-PLAN.md`](../plan/LEARNING-PLAN.md)（每周目标）。

---

## How to use it weekly

**每周如何使用**

The plan gives you ~45 minutes for the SendOS bridge in a normal week; the pages below assume a
**30-minute** session (the remaining 15 minutes are your weekly note).

在正常的一周里，计划给 SendOS 桥接留了约 45 分钟；下面的页面按每次 **30 分钟**来设计（剩下的 15 分钟用来写你的周笔记）。

| Week<br>周次 | Plan topic<br>计划主题 | Bridge section<br>桥接章节 | C# lab<br>C# 实验 | Mechanism (CONCEPT-MAP §4)<br>机制（CONCEPT-MAP §4） |
|---|---|---|---|---|
| 1 | The model, demystified<br>揭开模型的面纱 | [Week 1](./BRIDGE.md#week-1--the-model-demystified--sendmodeladapter)<br>第 1 周 | `dotnet/ProviderBridge` | §4.4 (schema-gated completion — the routing half is week 8)<br>§4.4（schema 把关的补全 —— 路由那一半在第 8 周） |
| 2 | Tools and the agent loop<br>工具与 Agent 循环 | [Week 2](./BRIDGE.md#week-2--tools-and-the-agent-loop--capabilitydefinition--registry)<br>第 2 周 | — | §4.2 (capability catalogue)<br>§4.2（能力目录） |
| 3 | Structured output, typed decisions<br>结构化输出、类型化决策 | [Week 3](./BRIDGE.md#week-3--structured-output-prompts-as-assets--istructuredcompletionhandler)<br>第 3 周 | `dotnet/StructuredDecisionBridge` | §4.1 (typed decision), §4.4<br>§4.1（类型化决策）、§4.4 |
| 4 | Context engineering and memory<br>上下文工程与记忆 | [Week 4](./BRIDGE.md#week-4--context-engineering-and-memory--sendcontextgateway)<br>第 4 周 | — | — (least-context envelope)<br>—（最小上下文信封） |
| 5 | MCP and interoperability<br>MCP 与互操作性 | [Week 5](./BRIDGE.md#week-5--mcp-and-interoperability--connector-manifests)<br>第 5 周 | — | §4.2 (declaration sources)<br>§4.2（声明来源） |
| 6 | Planning, orchestration, approval<br>规划、编排、审批 | [Week 6](./BRIDGE.md#week-6--planning-orchestration-human-approval--the-decision-first-runtime)<br>第 6 周 | — | §4.1, §4.5 |
| 7 | Evals and observability<br>评测（eval）与可观测性 | [Week 7](./BRIDGE.md#week-7--evals-and-observability--outcome_trace--evaluator)<br>第 7 周 | — | §4.3, §4.6 |
| 8 | Security, governance, cost<br>安全、治理、成本 | [Week 8](./BRIDGE.md#week-8--security-governance-cost-reliability--the-governance-sandwich)<br>第 8 周 | — | §4.2 (authority), §4.4 (budgets)<br>§4.2（权限）、§4.4（预算） |
| 9 | Capstone: Mini-SendOS<br>结业项目（capstone）：Mini-SendOS | [Week 9](./BRIDGE.md#week-9--capstone-mini-sendos--composing-the-runtime)<br>第 9 周 | — | all six<br>全部六个 |

### The weekly loop (30 minutes)

**每周循环（30 分钟）**

1. **Before the session:** open `BRIDGE.md` at your week. Do not pre-read anything else.

   **开始之前：** 打开 `BRIDGE.md` 中你所在的那一周。不要预先读其他任何东西。

2. **During:** 15 min read the listed files → 10 min write answers to the three questions → 5 min
   write the five bullets using the template in [Appendix C](./BRIDGE.md#appendix-c--weekly-bridge-log-template).

   **进行中：** 15 分钟阅读列出的文件 → 10 分钟写下三个问题的答案 → 5 分钟用 [附录 C](./BRIDGE.md#appendix-c--weekly-bridge-log-template) 中的模板写出五条要点。

3. **After:** check the answers in [Appendix A](./BRIDGE.md#appendix-a--answers) and correct them.
   The corrections are the learning; a clean match means you already knew it.

   **结束之后：** 对照 [附录 A](./BRIDGE.md#appendix-a--answers) 中的答案并加以修正。修正的过程就是学习；完全吻合说明你本来就已经懂了。

4. **If the week is short:** do the 30 minutes and skip the stretch. Never skip the bridge — it is
   the compounding part of the plan (goal A).

   **如果这周时间紧：** 完成这 30 分钟，跳过拓展部分。永远不要跳过桥接 —— 它是计划中会产生复利的那部分（目标 A）。

---

## Using the concept map well

**用好概念地图**

`CONCEPT-MAP.md` is long on purpose; do not read it cover to cover.

`CONCEPT-MAP.md` 是有意写长的；不要从头读到尾。

| You want<br>你想要 | Read<br>阅读 |
|---|---|
| To understand why these docs distrust SendOS's docs<br>理解为什么这些文档不信任 SendOS 自己的文档 | [§0](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins) — five verified drifts<br>—— 五处已核实的偏差 |
| The one-page path a request takes<br>一页看懂一个请求所走的路径 | [§1](./CONCEPT-MAP.md#1-the-machine-in-one-page) |
| To look up "how does SendOS do X?"<br>查询"SendOS 是怎么做 X 的？" | [§2](./CONCEPT-MAP.md#2-concept-map--industry-term--sendos-implementation) — 30-row concept table<br>—— 30 行的概念表 |
| A ranked list of what to learn, with labs<br>一份排好序的学习清单，附带实验 | [§3](./CONCEPT-MAP.md#3-ranked-learning-topics-20) |
| What to rebuild in miniature (and how)<br>该做成微缩版重建什么（以及怎么做） | [§4](./CONCEPT-MAP.md#4-where-a-from-scratch-build-teaches-the-most--six-mechanisms) |
| Where SendOS departs from mainstream practice<br>SendOS 在哪些地方偏离了主流做法 | [§5](./CONCEPT-MAP.md#5-where-sendos-departs-from-mainstream-practice) |
| What the analysis could not verify<br>分析中无法核实的内容 | [§7](./CONCEPT-MAP.md#7-what-i-could-not-assess) — read this before quoting anything<br>—— 引用任何内容之前先读这一节 |

**Status vocabulary used throughout:** *Implemented* (real and reachable) · *Partial* · *Dark*
(built and tested, not on the live path) · *Missing*. The distinction between "exists" and
"reachable" is the single most useful thing to carry into conversations with the team.

**全文使用的状态词汇：** *Implemented*（已实现：真实存在且可达）· *Partial*（部分实现）· *Dark*（暗置：已构建并测试，但不在实际运行路径上）· *Missing*（缺失）。"存在"与"可达"之间的区别，是你在与团队交流时最值得带上的一件事。

---

## The one framing to remember

**唯一需要记住的框架**

> **SendOS is ahead of mainstream tutorials on governance, behind on orchestration ergonomics.**
>
> **SendOS 在治理方面领先于主流教程，在编排的易用性方面则落后。**

Ahead: approval binding, authority intersection, append-only trace, publish gates, version pinning.
Behind: no graph runtime (a 5,379-line procedural `DecisionRuntime`), durable execution built but
unwired, thin observability, a dry learning loop.

领先之处：审批绑定、权限取交集、只追加的 trace、发布关卡、版本锁定。落后之处：没有图运行时（取而代之的是一个 5,379 行的过程式 `DecisionRuntime`）、持久化执行已构建但未接入、可观测性薄弱、学习闭环处于干涸状态。

Use it in both directions: when a control feels over-engineered, ask *which incident paid for it*;
when the platform feels incomplete, ask *which framework already solved this*. Both are interview
answers, and both are how you choose a contribution.

两个方向都要用：当某个控制机制显得过度设计时，问一问*是哪次事故换来了它*；当平台显得不完整时，问一问*哪个框架已经解决了这个问题*。两者都是面试时的好答案，也都是你选择贡献方向的方法。

---

## Maintenance rules

**维护规则**

1. **Code wins.** Never update a claim from documentation alone — open the file and cite it.

   **代码优先。** 永远不要仅凭文档就更新某个说法 —— 打开文件并引用它。

2. **Every claim carries a path** (`file.cs:line`). A claim without a path is an impression.

   **每个说法都要带路径**（`file.cs:line`）。没有路径的说法只是一种印象。

3. **Verified date** goes in the header of any page you change materially.

   对任何你做了实质性修改的页面，都要在页眉写上**核实日期**。

4. **When you find drift:** fix the claim, record the file/line that changed it, and add it to the
   drift table in [`CONCEPT-MAP.md` §0](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins)
   or [`BRIDGE.md` Appendix B](./BRIDGE.md#appendix-b--path-index-and-doc-drift-warnings).

   **发现偏差时：** 修正该说法，记录导致变化的文件/行号，并把它加到 [`CONCEPT-MAP.md` §0](./CONCEPT-MAP.md#0-read-this-first-the-docs-are-three-vintages-and-the-code-wins) 或 [`BRIDGE.md` 附录 B](./BRIDGE.md#appendix-b--path-index-and-doc-drift-warnings) 的偏差表中。

5. **Do not copy SendOS source into this repo.** Cite paths and quote at most a few lines; the
   learner's own code stays their own.

   **不要把 SendOS 源码复制到这个仓库。** 引用路径，最多摘录几行；学习者自己的代码始终是他们自己的。

---

## Verified status (2026-10-18)

**核实状态（2026-10-18）**

| Artifact<br>产物 | Verified how<br>核实方式 | Result<br>结果 |
|---|---|---|
| SendOS paths cited in `BRIDGE.md` / `READING-ORDER.md`<br>`BRIDGE.md` / `READING-ORDER.md` 中引用的 SendOS 路径 | Every full path checked with `Test-Path` (macOS/Linux: `test -e`) against the source checkout; every `.../` shorthand resolved to an existing file/dir under its app or library subtree; every internal markdown link and anchor checked<br>每个完整路径都用 `Test-Path`（macOS/Linux：`test -e`）对照源码检出做了检查；每个 `.../` 简写都解析到其应用或库子树下一个真实存在的文件/目录；每个内部 markdown 链接和锚点都检查过 | ✅ 0 unresolved<br>✅ 0 个未解析 |
| `CONCEPT-MAP.md` body<br>`CONCEPT-MAP.md` 正文 | Copied verbatim from `docs/research/05-sendos-concept-map.md`<br>从 `docs/research/05-sendos-concept-map.md` 逐字复制 | ✅ byte-for-byte preserved after the wrapper header<br>✅ 外层页眉之后的内容逐字节保留 |
| `dotnet/AgentBridgeLabs.sln` | `dotnet build` on SDK 10.0.303<br>在 SDK 10.0.303 上执行 `dotnet build` | ✅ 0 warnings, 0 errors<br>✅ 0 个警告，0 个错误 |
| Both C# self-tests<br>两个 C# 自测 | `--selftest` run offline<br>离线运行 `--selftest` | ✅ 11/11 and 15/15 checks pass<br>✅ 11/11 和 15/15 项检查通过 |
| Five doc drifts<br>五处文档偏差 | Re-read the cited code<br>重新阅读所引用的代码 | ✅ confirmed (see CONCEPT-MAP §0)<br>✅ 已确认（见 CONCEPT-MAP §0） |
