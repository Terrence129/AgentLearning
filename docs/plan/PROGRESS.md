# Progress Tracker

**进度追踪表**

**Started:** 2026-10-18 · **Plan:** 9 working weeks + 1 buffer (≈95–115 h) · **Method:** [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md) · **Gates:** [`CHECKPOINTS.md`](CHECKPOINTS.md)

**开始日期：** 2026-10-18 · **计划：** 9 个工作周 + 1 个缓冲周（≈95–115 小时）· **方法：** [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md) · **关卡：** [`CHECKPOINTS.md`](CHECKPOINTS.md)

**Update ritual (Saturday, 10 minutes):** fill the row, tick the week's checklist, add the one-sentence "what I can now explain", and log any debt. Do not edit past rows after the week closes — the history is the evidence.

**更新仪式（周六，10 分钟）：** 填好当周这一行，勾选本周清单，补上一句"我现在能讲清楚什么"，并记录所有欠账。一周结束后不要再修改过去的行——历史记录本身就是证据。

---

## 1. Status at a glance

**1. 状态一览**

| Wk<br>周 | Dates<br>日期 | Theme<br>主题 | Planned h<br>计划小时 | Actual h<br>实际小时 | G | E | T | Artifact<br>产出物 | Notes<br>备注 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2026-10-18 | Setup & baseline<br>环境搭建与基线 | 3 | | ☐ | ☐ | — | baseline note<br>基线笔记 | |
| 1 | 2026-10-19 → 10-25 | Model & provider seam<br>模型与 provider 接缝 | 8–10 | | ☐ | ☐ | ☐ | `chat` streams + cost<br>`chat` 流式输出 + 成本 | |
| 2 | 2026-10-26 → 11-01 | Tools & the agent loop<br>工具与 Agent 循环 | 10–12 | | ☐ | ☐ | ☐ | 5 golden tasks + trace<br>5 个黄金任务 + trace | |
| 3 | 2026-11-02 → 11-08 | Structured output<br>结构化输出 | 8–10 | | ☐ | ☐ | ☐ | `analyze() -> Decision` | |
| 4 | 2026-11-09 → 11-15 | Context & memory<br>上下文与记忆 | 10–12 | | ☐ | ☐ | ☐ | 20-turn retention run<br>20 轮保持性运行 | |
| 5 | 2026-11-16 → 11-22 | MCP | 8–10 | | ☐ | ☐ | ☐ | server + client + checklist<br>服务器 + 客户端 + 检查清单 | |
| 6 | 2026-11-23 → 11-29 | Planning & approval<br>规划与审批 | 10–12 | | ☐ | ☐ | ☐ | mini-Squad + approval test<br>迷你小队（mini-Squad）+ 审批测试 | |
| 7 | 2026-11-30 → 12-06 | Evals & observability<br>评测与可观测性 | 8–10 | | ☐ | ☐ | ☐ | ≥ 25-case suite + report<br>≥ 25 个用例的套件 + 报告 | |
| 8 | 2026-12-07 → 12-13 | Security & governance<br>安全与治理 | 8–10 | | ☐ | ☐ | ☐ | attack suite + threat model<br>攻击套件 + 威胁模型 | |
| 9 | 2026-12-14 → 12-20 | Capstone: Mini-SendOS<br>结业项目：Mini-SendOS | 12–16 | | ☐ | ☐ | ☐ | demo + eval report + write-up<br>演示 + 评测报告 + 总结文章 | |
| 10 | 2026-12-21 → 12-27 | Consolidation & leverage<br>巩固与发挥 | 4–6 | | ☐ | ☐ | ☐ | portfolio + interview rehearsal<br>作品集 + 面试演练 | |
| buf<br>缓冲 | 2026-12-28 → 2027-01-03 | Holiday buffer / overflow<br>假期缓冲 / 溢出 | — | | | | | | |

**Totals:** planned ____ / 95–115 · actual ____ · weeks on schedule ____/10 · debt items ____

**合计：** 计划 ____ / 95–115 · 实际 ____ · 按期完成的周数 ____/10 · 欠账条目 ____

> Legend: **G** = tests green, **E** = quiz + teach-back, **T** = SendOS transfer. ☑ = passed, ☐ = not yet, ✗ = failed (see debt log).
>
> 图例：**G** = 测试通过（变绿），**E** = 测验 + 复述讲解（teach-back），**T** = 迁移到 SendOS。☑ = 已通过，☐ = 尚未完成，✗ = 未通过（见欠账日志）。

---

## 2. Weekly checklists

**2. 每周检查清单**

Copy one block per week when the week starts; tick during the Saturday review.

每周开始时复制一个清单块；在周六复盘时勾选。

### Week 0 — Setup & baseline

**第 0 周 — 环境搭建与基线**

- [ ] `.\tasks.ps1 setup` (Windows) / `./tasks.sh setup` (macOS/Linux) completed; `doctor` clean

  已完成 `.\tasks.ps1 setup`（Windows）/ `./tasks.sh setup`（macOS/Linux）；`doctor` 检查无问题

- [ ] `.env` has `DEFAULT_PROVIDER=deepseek` + `DEEPSEEK_API_KEY`

  `.env` 中已有 `DEFAULT_PROVIDER=deepseek` + `DEEPSEEK_API_KEY`

- [ ] Foundation tests green; week tests red (expected)

  基础测试通过（变绿）；各周测试失败（红，符合预期）

- [ ] One live call recorded with tokens / latency / cost in `notes/week00-baseline.md`

  在 `notes/week00-baseline.md` 中记录一次真实调用的 token / 延迟 / 成本

- [ ] Baseline answers written (token, streaming, retry failure)

  写好基线答案（token、流式输出、重试失败）

- [ ] Three sessions in the calendar

  日历中已安排三次学习时段

### Week NN — <theme>

**第 NN 周 — <主题>**

- [ ] Brief read (`labs/weekNN-*/README.md`)

  已阅读任务简介（`labs/weekNN-*/README.md`）

- [ ] Failing tests read **before** coding

  **在写代码之前**先阅读失败的测试

- [ ] Build complete against the owned module only

  只在自己负责的模块内完成实现

- [ ] `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux) green

  `.\tasks.ps1 week NN`（Windows）/ `./tasks.sh week NN`（macOS/Linux）通过

- [ ] Quiz NN taken closed book: ____/10

  闭卷完成第 NN 周测验：____/10

- [ ] 150-word teach-back written without notes

  不看笔记写出 150 词的复述讲解

- [ ] SendOS bridge note (matches / differs / would change)

  SendOS 对照笔记（一致之处 / 不同之处 / 打算改动之处）

- [ ] 5 flashcards added to `docs/plan/flashcards/weekNN.csv`

  向 `docs/plan/flashcards/weekNN.csv` 添加 5 张闪卡

- [ ] `notes/weekNN-review.md` filled from [`../../templates/weekly-review.md`](../../templates/weekly-review.md)

  根据 [`../../templates/weekly-review.md`](../../templates/weekly-review.md) 填写 `notes/weekNN-review.md`

- [ ] `git commit -m "week NN: gate green + review"`
- [ ] Next week's three sessions in the calendar

  日历中已安排下周的三次学习时段

---

## 3. What I can now explain (cumulative)

**3. 我现在能讲清楚的内容（累计）**

Tick only when you can say it **aloud, without notes, in under 90 seconds**. This is the interview asset.

只有当你能**不看笔记、在 90 秒内大声讲出来**时才打勾。这就是你的面试资本。

| Wk<br>周 | Claim<br>论断 | ☑ | Date checked<br>检查日期 |
|---|---|---|---|
| 1 | Why retries, SSE delta assembly and usage accounting live in the provider adapter<br>为什么重试、SSE 增量拼装和用量统计都放在 provider 适配器里 | ☐ | |
| 2 | How the loop terminates, where the budget check goes, and why tool errors are observations<br>循环如何终止、预算检查放在哪里，以及为什么工具错误是观察结果 | ☐ | |
| 3 | Why JSON mode is not structured output, and how bounded repair + failure metrics work<br>为什么 JSON 模式不等于结构化输出，以及有界修复 + 失败指标如何运作 | ☐ | |
| 4 | How compaction, priority classes and a retention test keep a long task coherent<br>压缩、优先级分类和保持性测试如何让长任务保持连贯 | ☐ | |
| 5 | What MCP standardises, and the trust model that makes it safe<br>MCP 标准化了什么，以及让它安全的信任模型 | ☐ | |
| 6 | Why approval must bind to an action hash and an authority snapshot, and what at-most-once requires<br>为什么审批必须绑定到动作哈希和权限快照，以及"至多一次"需要什么条件 | ☐ | |
| 7 | How to build an eval suite that catches a regression before production (pass@1 vs pass^k)<br>如何构建能在上线前捕获回归的评测套件（pass@1 与 pass^k） | ☐ | |
| 8 | Why indirect injection is assumed to succeed, and how authority/sandbox/audit limit the blast radius<br>为什么要假定间接注入一定会成功，以及权限 / 沙箱 / 审计如何限制影响范围 | ☐ | |
| 9 | The full request path from ingress to audit row, with every failure mode and control<br>从入口到审计记录的完整请求路径，以及其中每个失败模式和控制手段 | ☐ | |
| 10 | The four runtime duties, and how SendOS maps onto them<br>运行时的四项职责，以及 SendOS 如何与之对应 | ☐ | |

---

## 4. Debt log (gates carried, stretch skipped, theory deferred)

**4. 欠账日志（顺延的关卡、跳过的拓展、推迟的理论）**

| Opened<br>登记日期 | Week<br>周 | Item<br>条目 | Type (gate / stretch / theory)<br>类型（关卡 / 拓展 / 理论） | Clear by<br>清偿期限 | Status<br>状态 |
|---|---|---|---|---|---|
| | | | | | |

**Rule:** one gate debt maximum at a time, cleared within 7 days (see [`CHECKPOINTS.md`](CHECKPOINTS.md) §4). Stretch and theory debt may be dropped — record it and move on.

**规则：** 同一时间最多只能有一项关卡欠账，并须在 7 天内清掉（见 [`CHECKPOINTS.md`](CHECKPOINTS.md) §4）。拓展和理论欠账可以放弃——记录下来然后继续前进。

---

## 5. Metrics (fill monthly, not weekly)

**5. 指标（每月填写，而非每周）**

| Month<br>月份 | Hours<br>小时数 | Weeks green<br>通过的周数 | Quizzes ≥ 8<br>测验 ≥ 8 分 | Cards added<br>新增卡片 | Cards reviewed<br>复习卡片 | Artifacts shipped<br>交付的产出物 | Cost spent ($)<br>花费（$） |
|---|---|---|---|---|---|---|---|
| Oct 2026 | | | | | | | |
| Nov 2026 | | | | | | | |
| Dec 2026 | | | | | | | |

**Health checks:** build time ≥ 60% of total · no week with two failed gates · cost under $5 total · every week has a review file and a commit.

**健康检查：** 动手实现时间 ≥ 总时间的 60% · 没有任何一周有两个关卡未通过 · 总成本低于 $5 · 每周都有一份复盘文件和一次提交。

---

## 6. Session log (optional but useful for the portfolio)

**6. 学习时段日志（可选，但对作品集很有用）**

| Date<br>日期 | Session<br>时段 | Minutes<br>分钟 | What moved<br>推进了什么 | Blocked on<br>卡在哪里 |
|---|---|---|---|---|
| | | | | |

---

## 7. End-of-course evidence checklist (week 10)

**7. 课程结束时的证据清单（第 10 周）**

- [ ] 9 weekly reviews in `notes/`, each with a teach-back

  `notes/` 中有 9 份每周复盘，每份都附有复述讲解

- [ ] 8 green week test suites (+ capstone)

  8 个通过的每周测试套件（+ 结业项目）

- [ ] Flashcards imported: ≥ 140 cards reviewed at least twice

  闪卡已导入：≥ 140 张卡片且每张至少复习过两次

- [ ] Eval report with baseline, pass^k, judge agreement, failure taxonomy

  评测报告包含基线、pass^k、评审一致率和失败分类

- [ ] Capstone demo script runs offline; 5-minute recording exists

  结业项目演示脚本可离线运行；已有 5 分钟的录屏

- [ ] `projects/portfolio/WRITEUP.md` complete

  `projects/portfolio/WRITEUP.md` 已完成

- [ ] Two deep-dive posts drafted

  已起草两篇深度解析文章

- [ ] One-page SendOS improvement proposal reviewed by a senior engineer

  一页纸的 SendOS 改进提案已经过一位资深工程师审阅

- [ ] All 30 interview questions answered aloud at least once

  全部 30 道面试题都至少大声回答过一次

- [ ] Re-derivation exercises done from a blank file

  从空白文件开始完成了重新推导练习
