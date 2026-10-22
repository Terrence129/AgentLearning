# Research reports

**研究报告**

Five deep-research reports produced on **2026-10-18** as the evidence base for this curriculum. They are deliberately opinionated, citation-dense snapshots — not tutorials.

作为本课程的证据基础，于 **2026-10-18** 产出的五份深度研究报告。它们是刻意带有鲜明观点、引用密集的快照——而不是教程。

| # | Report<br>报告 | Words<br>字数 | What it answers<br>回答什么问题 |
|---|---|---|---|
| 01 | [Agent architecture: state of the art](01-agent-architecture-sota.md)<br>[Agent 架构：前沿现状](01-agent-architecture-sota.md) | ~5,000 | How agent systems actually work in late 2026: harness duties, reasoning patterns, context engineering, memory, autonomy/HITL, durability, failure modes, and a build ladder.<br>2026 年末 Agent 系统实际上是如何运作的：harness（运行框架）的职责、推理模式、上下文工程、记忆、自主性/人在回路（HITL）、持久性、失败模式，以及一条逐级构建的阶梯。 |
| 02 | [Frameworks, SDKs & protocols](02-frameworks-protocols.md)<br>[框架、SDK 与协议](02-frameworks-protocols.md) | ~4,500 | MCP 2026-07-28, A2A v1.0, AG-UI 1.0, 19-framework comparison, provider capabilities, and what a .NET engineer should learn first.<br>MCP 2026-07-28、A2A v1.0、AG-UI 1.0、19 个框架的对比、模型提供商（provider）的能力，以及 .NET 工程师应该先学什么。 |
| 03 | [Production, evals, security & ops](03-production-evals-ops.md)<br>[生产、评测、安全与运维](03-production-evals-ops.md) | ~4,400 | Eval strategy (pass^k, judges), observability/OTel, the security threat model, reliability, cost levers, governance, a 38-item checklist.<br>评测（eval）策略（pass^k、评审）、可观测性/OTel、安全威胁模型、可靠性、成本杠杆、治理，以及一份 38 项的检查清单。 |
| 04 | [Learning resources](04-learning-resources.md)<br>[学习资源](04-learning-resources.md) | ~3,800 | Verified courses, essays, papers, codebases, books, communities, Chinese-language resources, a 50-hour essential subset.<br>经过核实的课程、文章、论文、代码库、书籍、社区、中文资源，以及一个 50 小时的精华子集。 |
| 05 | [SendOS concept map](05-sendos-concept-map.md)<br>[SendOS 概念地图](05-sendos-concept-map.md) | ~3,900 | What the SendOS platform actually implements (grounded in file:line), 20 ranked learning topics, six mechanisms worth rebuilding, and 11 departures from mainstream practice.<br>SendOS 平台实际实现了什么（以 file:line 为依据）、20 个按优先级排序的学习主题、六个值得重建的机制，以及 11 处偏离主流实践的地方。 |

---

## How to use these reports

**如何使用这些报告**

- **Do not read them cover to cover.** Each week's concept note links the relevant section.

  **不要从头读到尾。** 每周的概念笔记都会链接到相关章节。

- **Treat them as snapshots.** Frameworks, spec versions and pricing change monthly. Every report records its access date; when you act on a claim &ge; 3 months old, re-verify the primary source.

  **把它们当作快照。** 框架、规范版本和定价每个月都在变。每份报告都记录了访问日期；当你要依据一条已有 ≥ 3 个月的说法采取行动时，请重新核实一手来源。

- **Check the uncertainty registers.** Reports 01 §10, 02 §6, 03 §10 and 04 §J explicitly separate verified facts from estimates and vendor claims. Read those before quoting numbers in an interview.

  **查看不确定性登记表。** 报告 01 §10、02 §6、03 §10 和 04 §J 明确地把已核实的事实与估计值、厂商说法区分开来。在面试中引用数字之前，先读这些部分。

- **Citations are the point.** Every non-obvious claim links its source. If a link is dead, the claim is a lead, not a fact.

  **引用才是重点。** 每一条不显而易见的说法都链接了来源。如果链接失效，这条说法就只是一条线索，而不是事实。

## Refresh policy

**更新策略**

When you finish a week and find a claim is stale:

当你完成一周的学习并发现某条说法已经过时：

1. Update the concept note (or this repo's lab) with the current fact.

   用当前的事实更新概念笔记（或本仓库的实验）。

2. Append a dated line to the report's uncertainty register — do not silently rewrite history.

   在报告的不确定性登记表中追加一行带日期的记录——不要悄无声息地改写历史。

3. If the change invalidates a lab, open an issue against that lab rather than patching the research.

   如果这一变化使某个实验（lab）失效，请针对该实验提一个 issue，而不是去修补研究报告。

Reports are valuable because they are **dated**, not because they are eternal.

报告之所以有价值，是因为它们**标注了日期**，而不是因为它们永恒不变。

## Provenance

**来源**

Produced by parallel research agents with primary-source verification (spec sites, vendor docs, arXiv, official blogs, and the SendOS repository at `D:\DevRepo\SendProjects\SendOS\SendOs`; on macOS/Linux, substitute your local SendOS checkout path). SendOS analysis was read-only; the platform was not built or executed.

由多个并行的研究 Agent 产出，并经过一手来源核实（规范网站、厂商文档、arXiv、官方博客，以及位于 `D:\DevRepo\SendProjects\SendOS\SendOs` 的 SendOS 仓库；在 macOS/Linux 上，请替换为你本地的 SendOS 检出路径）。对 SendOS 的分析是只读的；该平台没有被构建或运行。
