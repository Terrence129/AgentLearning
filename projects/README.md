# Projects

**项目**

The labs teach individual mechanisms. The projects force you to compose them and defend the composition.

实验（lab）教的是一个个独立的机制。项目则迫使你把它们组合起来，并为这种组合方式进行辩护。

## 1. Capstone — Mini-SendOS (week 9)

**1. 结业项目（capstone）——Mini-SendOS（第 9 周）**

Build a small but complete agent platform that mirrors the governance-first architecture of SendOS:

构建一个小而完整的 Agent 平台，复刻 SendOS 治理优先的架构：

```
goal → typed decision → topology-selected execution → approval gate → authoritative execution → audit trail
                                                                        ↘ trace → evidence gate → human-approved asset promotion
```

Deliverables:

交付物：

- Working demo: `scripts/demo_capstone.py` (offline, mock provider) and a web UI (real provider).

  可运行的演示：`scripts/demo_capstone.py`（离线，mock 模型提供商（provider））和一个 Web UI（真实提供商）。

- Eval report: baseline, regressions, pass^k, cost and latency.

  评测（eval）报告：基线、回归、pass^k、成本和延迟。

- Architecture write-up: decisions, trade-offs, threats, what you would do next.

  架构总结文章：决策、权衡、威胁，以及你接下来会做什么。

- 5-minute recorded demo.

  5 分钟的录屏演示。

Acceptance criteria: [`capstone/ACCEPTANCE.md`](capstone/ACCEPTANCE.md). Write-up template: [`portfolio/WRITEUP.md`](portfolio/WRITEUP.md).

验收标准：[`capstone/ACCEPTANCE.md`](capstone/ACCEPTANCE.md)。总结文章模板：[`portfolio/WRITEUP.md`](portfolio/WRITEUP.md)。

## 2. Portfolio artifacts (ongoing)

**2. 作品集成果（持续进行）**

You are hiring-manager-visible from week 2 onward, not week 9. Each week produces one public artifact:

从第 2 周起你就要让招聘经理看得见你，而不是等到第 9 周。每周产出一个公开的成果：

| Artifact<br>成果 | When<br>时间 | Why it matters<br>为什么重要 |
|---|---|---|
| Lab report (`notes/weekNN-review.md`)<br>实验报告（`notes/weekNN-review.md`） | every week<br>每周 | Shows reasoning, not just code<br>展示推理过程，而不只是代码 |
| "Approval binding is a security mechanism" deep-dive<br>“审批绑定是一种安全机制”深度剖析 | week 6<br>第 6 周 | Demonstrates governance maturity<br>体现治理方面的成熟度 |
| "Why pass^k beats pass@1" eval write-up<br>“为什么 pass^k 胜过 pass@1”评测总结文章 | week 7<br>第 7 周 | Shows measurement discipline<br>体现度量上的严谨 |
| Capstone architecture + demo<br>结业项目架构 + 演示 | week 9<br>第 9 周 | The interview centrepiece<br>面试中的核心展示品 |

Templates are in [`../templates/`](../templates/).

模板位于 [`../templates/`](../templates/)。

## 3. Stretch ideas

**3. 拓展想法**

- [ ] Port the week-2 loop to **.NET** using `Microsoft.Extensions.AI` (`IChatClient`) and compare ergonomics.

  使用 `Microsoft.Extensions.AI`（`IChatClient`）把第 2 周的循环移植到 **.NET**，并比较开发体验。

- [ ] Reimplement the week-6 squad in **LangGraph** and **Microsoft Agent Framework**; write a 1-page comparison.

  用 **LangGraph** 和 **Microsoft Agent Framework** 重新实现第 6 周的小队（squad）；写一页对比。

- [ ] Turn the week-9 catalogue into a real **MCP server** and connect it to Claude Desktop or another host.

  把第 9 周的目录做成一个真正的 **MCP 服务器**，并把它连接到 Claude Desktop 或其他宿主。

- [ ] Add an **OTel exporter** to the trace module and view a run in a local collector.

  为 trace 模块添加一个 **OTel 导出器**，并在本地 collector 中查看一次运行。

- [ ] Implement **durable suspend/resume** for approvals with SQLite + CAS (SendOS's unwired `CaseRuntime`).

  用 SQLite + CAS 为审批实现**持久化的挂起/恢复**（对应 SendOS 中尚未接线的 `CaseRuntime`）。

- [ ] Build an **eval-gated promotion** pipeline: candidate improves a prompt only if it beats baseline on the suite.

  构建一条**以评测为关卡的晋升**流水线：候选方案只有在测试套件上胜过基线时，才会被用来改进提示词。

## Rules of thumb

**经验法则**

- A project you cannot demo in 5 minutes is not finished.

  无法在 5 分钟内演示的项目就不算完成。

- Every number you report (cost, accuracy, latency) needs its measurement method in the report.

  你报告的每一个数字（成本、准确率、延迟）都需要在报告中写明其度量方法。

- Write the "what I would do differently" section first; it is the most valuable part.

  先写“我会怎样换种做法”这一部分；它是最有价值的部分。
