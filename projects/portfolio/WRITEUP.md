# Portfolio Write-up — Mini-SendOS

**作品集总结文章——Mini-SendOS**

> Template. Replace every `_italic prompt_` with real content; delete this block when done.
> **Target:** 800–1,500 words. Written for a senior engineer or hiring manager who has 10 minutes.
> Include one architecture diagram (ASCII or an image), one results table, and one "what I'd do next".
>
> 模板。把每一处 `_italic prompt_` 替换为真实内容；完成后删除这个块。
> **目标：** 800–1,500 词。写给只有 10 分钟的资深工程师或招聘经理看。
> 包含一张架构图（ASCII 或图片）、一张结果表，以及一段“我下一步会做什么”。

## Title

**标题**

_Mini-SendOS: a governed agent runtime built from scratch, in ten weeks_ (adjust)

_Mini-SendOS：十周内从零构建的受治理 Agent 运行时_（可调整）

**One-line summary:** _An offline, test-driven agent platform where every model output is a typed decision, every write is an approval-bound proposal, and every step is an append-only audit row — built from primitives, not frameworks._

**一句话概述：** _一个离线、测试驱动的 Agent 平台：每一次模型输出都是一个类型化决策，每一次写入都是一个绑定审批的提案，每一个步骤都是一条仅追加的审计行——由基本组件构建，而不是依赖框架。_

## 1. Problem

**1. 问题**

_What agent systems get wrong in production (pick 2–3, with evidence): model-authored approvals, duplicate side effects, unbounded cost, no trace, context loss. Why is this hard? Which failure did you personally reproduce in a lab?_

_Agent 系统在生产环境中会犯哪些错误（挑 2–3 个，并附证据）：由模型自行生成的审批、重复的副作用、无上限的成本、没有 trace、上下文丢失。为什么这很难？你亲自在哪个实验（lab）中复现过哪种失败？_

## 2. Architecture

**2. 架构**

_Paste the request-path diagram: goal -> decision -> catalogue check -> proposal -> approval -> execution -> audit. Name the module for each arrow and the week that taught it. Mark which parts are provided infrastructure and which you implemented._

_粘贴请求路径图：目标 -> 决策 -> 目录检查 -> 提案 -> 审批 -> 执行 -> 审计。为每个箭头标出对应的模块以及讲授它的那一周。标明哪些部分是现成提供的基础设施，哪些是你自己实现的。_

## 3. Decisions and trade-offs

**3. 决策与权衡**

_3–5 decisions, each as: context -> options considered -> choice -> cost of being wrong. Suggested candidates:_

_3–5 个决策，每个按如下格式：背景 -> 考虑过的选项 -> 选择 -> 选错的代价。建议的候选：_

- _Closed decision union vs free-text output with a parser._

  _封闭的决策联合类型 vs 自由文本输出加解析器。_

- _Proposal persisted before approval vs approving an in-memory object._

  _在审批前持久化提案 vs 审批一个内存中的对象。_

- _Published-wins catalogue vs field-level merge between declaration sources._

  _“已发布者优先”的目录 vs 在各声明来源之间做字段级合并。_

- _At-most-once execution via persisted approval state vs idempotency keys on the tool._

  _通过持久化的审批状态实现至多一次执行 vs 在工具上使用幂等键。_

- _Optional FastAPI surface vs server-rendered CLI output._

  _可选的 FastAPI 接口 vs 服务端渲染的 CLI 输出。_

## 4. Evidence

**4. 证据**

| Metric<br>指标 | Result<br>结果 | How measured<br>测量方式 |
|---|---|---|
| Capstone tests green<br>结业项目测试通过 | _46/46_ | `pytest tests/week09 -m week -q` |
| Demo runs offline<br>演示可离线运行 | _exit code 0_<br>_退出码 0_ | `python scripts/demo_capstone.py` |
| Foundation tests<br>基础测试 | _N passed_<br>_N 个通过_ | `pytest -q` |
| Avg. end-to-end latency (mock)<br>平均端到端延迟（mock） | _N ms_ | _timing script_<br>_计时脚本_ |
| Tokens / cost per happy path<br>每条正常路径的 token / 成本 | _N / $N_ | _trace + pricing table_<br>_trace + 价格表_ |
| Audit rows per lifecycle<br>每个生命周期的审计行数 | _N_ | `audit_trail()` |
| Security invariants tested<br>已测试的安全不变量 | _N_ | _list the B1–B6 tests_<br>_列出 B1–B6 测试_ |

## 5. What I checked, not just built

**5. 我验证了什么，而不只是构建了什么**

_List the invariants you tested yourself (replay, hash mismatch, cross-tenant, fail-closed write, budget breach). One sentence each on what would break without the control._

_列出你自己测试过的不变量（重放、哈希不匹配、跨租户、故障即关闭的写入、预算超支）。每条用一句话说明：如果没有这项控制，会出什么问题。_

## 6. Threats considered

**6. 考虑过的威胁**

_Injection via tool output, approval replay, cross-tenant access, budget exhaustion, model error. For each: control, residual risk, and what you deliberately left out of the miniature._

_通过工具输出进行的注入、审批重放、跨租户访问、预算耗尽、模型错误。对每一项写出：控制措施、残余风险，以及你在缩微版中刻意省略了什么。_

## 7. Limitations (be honest)

**7. 局限（要诚实）**

_At least three: in-memory persistence, single process, no auth, mock-only model in the demo, no retry/backoff on execution, no durable suspend/resume._

_至少三个：仅内存持久化、单进程、无身份认证、演示中只用 mock 模型、执行时没有重试/退避、没有持久化的挂起/恢复。_

## 8. What I'd do next

**8. 我下一步会做什么**

_One concretely-scoped improvement, preferably the one you proposed to SendOS. What would you build, how would you measure it, what is the risk?_

_一项范围明确的改进，最好是你向 SendOS 提出的那一项。你会构建什么？你会如何衡量它？风险是什么？_

## 9. What I can now explain without notes

**9. 我现在不看笔记就能解释的内容**

_5–8 bullets: the agent loop and where budgets are enforced; why tool output is context; compaction's order of operations; why memory needs provenance; why approvals bind to a hash; why pass^k beats pass@1; MCP's current revision and what changed; how SendOS's governance sandwich maps onto your capstone._

_5–8 条要点：Agent 循环以及预算在哪里被强制执行；为什么工具输出就是上下文；压缩（compaction）的操作顺序；为什么记忆需要来源（provenance）；为什么审批要绑定到哈希；为什么 pass^k 胜过 pass@1；MCP 的当前修订版本及其变化；SendOS 的治理“三明治”如何映射到你的结业项目（capstone）上。_

---

**Links:** _repo path, demo video, lab brief, this write-up published at …_

**链接：** _仓库路径、演示视频、实验简介、本文的发布地址 …_
