# 09 — Production: Durability, Cost, and the Checks That Matter

**09 — 生产环境：持久性、成本，以及真正重要的检查项**

> **Week 9 and beyond · just-in-time concept note.** Read before the capstone (~25 min). This note is about the runs that don't complete — and the readiness checks you are allowed to skip. **Reads with:** [research 03 §4–8](../research/03-production-evals-ops.md) · **Lab:** `week09-capstone`.
>
> **第 9 周及以后 · 即时概念笔记。** 请在开始结业项目（capstone）之前阅读（约 25 分钟）。这篇笔记讲的是那些没能跑完的运行——以及哪些上线就绪检查是你可以跳过的。**配合阅读：** [研究 03 §4–8](../research/03-production-evals-ops.md) · **实验：** `week09-capstone`。

## The failure mode this prevents

**这篇笔记要防止的失败模式**

The agent loop lives inside a request handler. At step 7 of 9 the platform deploys, the worker is recycled, the run is lost — and the client, seeing a timeout, retries. The write tool was not idempotent, so the refund executes twice. Meanwhile the invoice is 4× the estimate and nobody can attribute it to a tenant, prompt version or tool, because cost was logged as one number per day.

Agent 循环跑在一个请求处理器里。在 9 步中的第 7 步时，平台进行了部署，工作者进程被回收，这次运行就此丢失——而客户端看到超时后发起了重试。写工具不是幂等的，于是退款执行了两次。与此同时，账单是预估的 4 倍，却没有人能把它归因到某个租户、提示词版本或工具上，因为成本每天只记录成一个数字。

Production readiness is four disciplines: **durability** (runs survive), **idempotency** (side effects happen once), **cost control** (spend is attributable and bounded), **tenant isolation** (one customer cannot break another). The 38-check list in research 03 is the full map; this note is the short path.

生产就绪包含四项纪律：**持久性**（运行能够存活）、**幂等性**（副作用只发生一次）、**成本控制**（开销可归因且有上限）、**租户隔离**（一个客户无法搞坏另一个客户）。研究 03 中的 38 项检查清单是完整的地图；这篇笔记则是捷径。

## If you remember five things

**如果只记住五件事**

> 1. **An agent loop is a workflow, not a request.** Persist state, use activities, survive restarts, suspend on humans.
>
>    **Agent 循环是一个工作流，而不是一次请求。** 持久化状态，使用 activity，在重启后存活，等待人类时挂起。
>
> 2. **Every side-effecting call needs an idempotency key persisted before the call.**
>
>    **每一个有副作用的调用，都需要一个在调用之前就已持久化的幂等键。**
>
> 3. **Cost is input tokens × context length × turns** — cache, compact and route before optimising milliseconds.
>
>    **成本 = 输入 token × 上下文长度 × 轮数**——在优化毫秒级延迟之前，先做缓存、压缩和路由。
>
> 4. **The 15-minute serverless limit is shorter than many agent runs**, so separate API, orchestration, execution and sandbox tiers.
>
>    **15 分钟的无服务器时长上限比许多 Agent 运行都要短**，所以要把 API、编排、执行和沙箱分成不同的层。
>
> 5. **For a single-team product, 12 of 38 readiness checks carry most of the risk.** Do those; defer the rest deliberately.
>
>    **对于单个团队的产品，38 项就绪检查中有 12 项承载了大部分风险。** 先做这些；其余的有意识地推后。

## The model in one page

**一页看懂模型**

### Durable execution: the loop is a workflow

**持久化执行：循环就是一个工作流**

An agent loop holds state — conversation, step index, budget consumed, pending tool calls, approval status — and its steps fail independently: model timeouts, tool rate limits, humans taking hours. Keeping that state in a process is the design error.

Agent 循环持有状态——对话、步骤序号、已消耗预算、待处理的工具调用、审批状态——而它的各个步骤会各自独立地失败：模型超时、工具限流、人类要花好几个小时才回应。把这些状态保存在进程里，就是设计错误。

Temporal documents the right model: the loop is a Workflow, each model and tool call is an Activity, a crash resumes the conversation instead of restarting it, and human-in-the-loop is a durable Signal plus Timer ([Temporal](https://docs.temporal.io/evaluate/use-cases-design-patterns), accessed 2026-10-18). On AWS, a Lambda invocation is capped at **15 minutes** (90 for managed-instance async), while durable functions allow 30,000 operations per execution and MicroVMs run up to 8 hours ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18).

Temporal 记录了正确的模型：循环是一个 Workflow，每次模型调用和工具调用都是一个 Activity，崩溃后会恢复对话而不是从头开始，而人在回路（HITL）则是一个持久化的 Signal 加 Timer（[Temporal](https://docs.temporal.io/evaluate/use-cases-design-patterns)，访问于 2026-10-18）。在 AWS 上，一次 Lambda 调用的上限是 **15 分钟**（托管实例的异步调用为 90 分钟），而 durable functions 每次执行允许 30,000 个操作，MicroVM 最长可运行 8 小时（[Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)，访问于 2026-10-18）。

Minimum viable durability: a **run table** (status, step, budget, trace ref), a **checkpoint per step**, a **resume endpoint**, **CAS on resume** so a double-callback cannot double-execute, and a **deadline sweeper**. Prefer Temporal's .NET SDK or durable functions over building this.

最小可行的持久性：一张**运行表**（状态、步骤、预算、trace 引用）、**每一步一个检查点**、一个**恢复端点**、**恢复时使用 CAS（比较并交换）**，这样重复的回调就不会导致重复执行，以及一个**截止时间清扫器**。与其自己构建，不如优先使用 Temporal 的 .NET SDK 或 durable functions。

### Idempotency and at-most-once

**幂等性与最多一次**

Idempotency is a storage problem before it is a retry problem:

幂等性首先是一个存储问题，然后才是一个重试问题：

- Derive the key from `(run_id, step_no, tool, canonical_args_hash)`; canonicalise arguments (sorted keys, normalized types) or the same call yields different keys.

  从 `(run_id, step_no, tool, canonical_args_hash)` 推导出键；要对参数做规范化（键排序、类型归一化），否则同一次调用会产生不同的键。

- **Persist before invoking**, in a store with a uniqueness constraint. On retry, return the stored result or a stable rejection.

  **在调用之前持久化**，并存放在带唯一性约束的存储中。重试时，返回已存储的结果或一个稳定的拒绝结果。

- **Same key + different arguments is an error**, never a re-execution with new arguments.

  **相同的键 + 不同的参数是一个错误**，绝不能用新参数重新执行。

- An approval is **consumed** when it executes, so a replayed approval cannot execute twice.

  审批在执行时即被**消费**，因此重放的审批不可能执行两次。

Test it the boring way: same key twice → one side effect; mutated arguments → rejection.

用最朴素的方式测试它：同一个键出现两次 → 只有一次副作用；参数被改动 → 拒绝。

### Cost and latency levers, in order

**成本与延迟的杠杆，按顺序排列**

Prompt caching is the biggest lever. Cache reads cost **0.1×** input (0.05× on Anthropic's Opus/Sonnet 5.5-class, 0.025× on Fable/Mythos 5.1-class); writes cost **1.25×**; TTLs are 5 minutes (1 hour at 2×) on Anthropic and 30 minutes on current OpenAI models. A documented multi-turn agent pattern reports **>90% cache-hit** ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18).

提示词缓存是最大的杠杆。缓存读取的费用是输入价格的 **0.1 倍**（在 Anthropic 的 Opus/Sonnet 5.5 级别模型上为 0.05 倍，在 Fable/Mythos 5.1 级别模型上为 0.025 倍）；写入的费用是 **1.25 倍**；TTL 在 Anthropic 上为 5 分钟（按 2 倍价格可获得 1 小时），在当前的 OpenAI 模型上为 30 分钟。一个有文档记录的多轮 Agent 模式报告了 **>90% 的缓存命中率**（[Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)、[OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching)，访问于 2026-10-18）。

Order of attack, highest leverage first:

着手顺序，杠杆最大的排在最前：

1. **Measure** cost per successful task and cache-hit rate per tenant.

   **度量**每个成功任务的成本，以及每个租户的缓存命中率。

2. **Stabilise the prefix**: static content first (instructions, tools, examples), dynamic last, append rather than rewrite.

   **稳定前缀**：静态内容放前面（指令、工具、示例），动态内容放最后，采用追加而不是重写。

3. **Cap budgets** per run, user and tenant — enforced at the gateway, not in the prompt ([budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/), accessed 2026-10-18).

   **为预算设上限**，分别针对每次运行、每个用户和每个租户——在网关处强制执行，而不是写在提示词里（[budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/)，访问于 2026-10-18）。

4. **Compact** long runs: summarise history, clear stale tool output.

   **压缩**长时间运行的上下文：总结历史，清除过时的工具输出。

5. **Route**: cheap model for classification/extraction/easy turns, escalate on confidence or failure.

   **路由**：分类/抽取/简单的轮次用便宜的模型，根据置信度或失败情况再升级。

6. **Batch** non-interactive work — evals, nightly summaries, backfills — at provider discounts.

   **批处理**非交互式工作——评测（eval）、夜间摘要、数据回填——以享受模型提供商（provider）的折扣。

Cached input still counts toward rate limits ([OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18). Latency levers (parallel tools, streaming, deferred loading) improve UX but rarely fix cost.

缓存命中的输入仍然计入速率限制（[OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching)，访问于 2026-10-18）。延迟方面的杠杆（并行工具、流式输出、延迟加载）能改善用户体验，但很少能解决成本问题。

### Deployment topology and multi-tenancy

**部署拓扑与多租户**

Four tiers: **stateless API/edge** (auth, licensing, streaming, no loop), **orchestrator** (durable engine owns run state), **execution workers** (tool calls; scale on queue depth, not CPU), **sandbox** (ephemeral, egress-restricted). Add circuit breakers per provider+model — a throttled model is not a throttled platform — plus per-tenant rate limits and single-flight caching at the gateway.

四个层级：**无状态的 API/边缘层**（认证、许可、流式输出，不跑循环）、**编排者**（由持久化引擎持有运行状态）、**执行工作者**（执行工具调用；按队列深度而不是 CPU 来伸缩）、**沙箱**（临时的、限制出站流量）。按「提供商 + 模型」设置熔断器——一个模型被限流并不代表整个平台被限流——再在网关处加上按租户的速率限制和 single-flight 缓存。

Isolation spans more than a `WHERE tenant_id`: data (tenant ID bound by the platform, never by model arguments), credentials (per-tenant secrets and OAuth grants), compute (tenant-scoped queues so batch cannot starve interactive traffic), memory/retrieval (partitioned indexes and namespaces), caches/billing (per-customer cache-accounting keys so cost is attributable), and audit (tenant-scoped views plus platform copy). Put licensing and quota at **ingress**, before any model call, so the cheapest denial never spends tokens.

隔离远不止一个 `WHERE tenant_id`：数据（租户 ID 由平台绑定，绝不由模型参数决定）、凭据（按租户划分的密钥和 OAuth 授权）、计算（按租户划分的队列，这样批处理任务不会饿死交互式流量）、记忆/检索（分区的索引和命名空间）、缓存/计费（按客户划分的缓存计费键，让成本可以归因）、以及审计（按租户划分的视图外加一份平台副本）。把许可和配额检查放在**入口**处、在任何模型调用之前，这样最便宜的拒绝永远不会消耗 token。

### The 12 checks that matter for a single-team product

**对单团队产品真正重要的 12 项检查**

The full 38-item list is in [research 03 §8](../research/03-production-evals-ops.md). A small team cannot ship all 38 in a quarter. These 12 carry most of the incident risk; the rest mostly prevent procurement conversations.

完整的 38 项清单在 [研究 03 §8](../research/03-production-evals-ops.md) 中。一个小团队不可能在一个季度内落实全部 38 项。下面这 12 项承载了大部分事故风险；其余的大多只是为了避免在采购谈判中卡壳。

**Evidence (3).** (1) A private eval set of 30+ cases from real requests, versioned. (2) pass^k gated in CI, not just pass@1. (3) Every incident becomes a regression case; golden traces replayed on prompt/model changes.

**证据（3 项）。** (1) 一个来自真实请求、包含 30 个以上用例的私有评测集，并做版本管理。(2) 在 CI 中用 pass^k 设关卡，而不仅仅是 pass@1。(3) 每次事故都变成一个回归用例；在提示词/模型变更时回放黄金 trace。

**Security (3).** (4) A lethal-trifecta audit per agent — at least one leg removed or gated. (5) Irreversible actions require a bound approval with a concrete action diff. (6) An audit log separate from debug traces, append-only.

**安全（3 项）。** (4) 对每个 Agent 做致命三要素审查——至少拆掉一条腿或为其设置关卡。(5) 不可逆的动作需要一个带绑定的审批，并附上具体的动作差异。(6) 审计日志与调试 trace 分开存放，且只追加。

**Reliability (4).** (7) Long loops run on a durable engine with replay. (8) An idempotency key persisted before every tool call. (9) HITL is durable suspend/resume, never a held thread or request. (10) Per-model/tool timeouts and a per-run wall-clock deadline.

**可靠性（4 项）。** (7) 长循环运行在支持回放的持久化引擎上。(8) 每次工具调用之前都持久化一个幂等键。(9) 人在回路是持久化的挂起/恢复，绝不是一直挂着的线程或请求。(10) 按模型/工具设置超时，并为每次运行设置挂钟截止时间。

**Observability and cost (2).** (11) Tenant ID, prompt version, model and cost on every span, with a cache-hit-rate SLO. (12) Hard token/$ caps per run, user and tenant, enforced at the gateway.

**可观测性与成本（2 项）。** (11) 每个 span 上都带有租户 ID、提示词版本、模型和成本，并设定缓存命中率 SLO。(12) 针对每次运行、每个用户和每个租户设置 token/美元的硬上限，并在网关处强制执行。

Defer deliberately: ISO/IEC 42001 and NIST AI RMF crosswalks, a full AI-BOM, SCIM and audit export, a registry beyond a spreadsheet — until a customer or regulation forces them. One exception: if you sell into the EU, record AI Act classification and oversight evidence now, because the 2027 high-risk deadline is about evidence you should already be generating.

有意识地推后：ISO/IEC 42001 和 NIST AI RMF 的对照映射、完整的 AI-BOM、SCIM 和审计导出、比电子表格更正式的注册中心——直到客户或法规强制要求时再做。有一个例外：如果你要向欧盟销售，现在就要记录《人工智能法案》的分级归类和监督证据，因为 2027 年的高风险截止期限要的就是你本应已经在产生的证据。

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>实际情况 |
|---|---|
| "Durable execution is overkill for a two-minute agent."<br>「对一个只跑两分钟的 Agent 来说，持久化执行是杀鸡用牛刀。」 | It is about surviving deploys, retries and human waits, not duration.<br>它关乎的是能否熬过部署、重试和等待人类，而不是运行时长。 |
| "Retries are safe because the tool is read-only."<br>「重试是安全的，因为工具是只读的。」 | Money moves through writes; that is where idempotency is mandatory.<br>资金是通过写操作流动的；那正是必须保证幂等性的地方。 |
| "Caching is automatic, so there is nothing to do."<br>「缓存是自动的，所以什么都不用做。」 | Hits depend on prefix stability; if you cannot report hit rate, you do not know.<br>命中取决于前缀的稳定性；如果你报告不出命中率，你就并不清楚情况。 |
| "Batch is for big data jobs."<br>「批处理是给大数据作业用的。」 | Eval suites and nightly summaries are batch work.<br>评测套件和夜间摘要就是批处理工作。 |
| "Multi-tenancy is a column in the query."<br>「多租户就是查询里的一个字段。」 | It is also queues, keys, caches, memory, budgets and audit.<br>它还涉及队列、键、缓存、记忆、预算和审计。 |

## How this shows up in SendOS

**这在 SendOS 中如何体现**

- **`CaseRuntime` + `DecisionTask` is the durability spine — built but dark.** CAS reserve → suspend → resume plus a deadline worker exists but is not wired (`.../Domain/CaseRuntime/**`; `.../Infrastructure/CaseRuntime/**`; [research 05 §2.5](../research/05-sendos-concept-map.md)). Wiring it is the fastest credible contribution in the repo.

  **`CaseRuntime` + `DecisionTask` 是持久性的脊梁——已经构建，但处于未启用状态。** CAS 预留 → 挂起 → 恢复，外加一个截止时间工作者，这些都已存在但没有接线（`.../Domain/CaseRuntime/**`；`.../Infrastructure/CaseRuntime/**`；[研究 05 §2.5](../research/05-sendos-concept-map.md)）。把它接上，是在这个仓库里能做出的最快、也最有说服力的贡献。

- **`ActionIdempotencyStore` and the approval-consumed flag are the at-most-once pattern.** With stable replay-rejection codes (`Application/Approval/ApprovalCheckpoint.cs:341-412`), this is exactly what your lab reproduces.

  **`ActionIdempotencyStore` 和「审批已消费」标志就是最多一次的模式。** 加上稳定的重放拒绝码（`Application/Approval/ApprovalCheckpoint.cs:341-412`），这正是你的实验所复现的内容。

- **Budget-aware routing is already coded.** `HandleRoutedAsync` filters candidates by cost/latency/attempts with fail-safe budget checks; `BudgetGuard`/`IterationBudget` enforce ceilings (`apps/Send.Model.Adapter/src/.../Handlers/CompletionHandler.cs:60-210`). Read it as the production form of your week-8 `ratelimit.py`.

  **感知预算的路由已经写好了。** `HandleRoutedAsync` 按成本/延迟/尝试次数筛选候选项，并带有失败安全的预算检查；`BudgetGuard`/`IterationBudget` 负责强制执行上限（`apps/Send.Model.Adapter/src/.../Handlers/CompletionHandler.cs:60-210`）。把它当作你第 8 周 `ratelimit.py` 的生产版来读。

- **The resilience stack is composition.** `Send.Intelligence.Gateway` layers tiered cache, circuit breaker, per-connector rate limiter, single-flight and idempotency (`apps/Send.Intelligence.Gateway/src/**`) — your weeks 7–8 primitives assembled into one call path.

  **弹性技术栈是一种组合。** `Send.Intelligence.Gateway` 把分层缓存、熔断器、按连接器的速率限制器、single-flight 和幂等性逐层叠加起来（`apps/Send.Intelligence.Gateway/src/**`）——也就是把你第 7–8 周做的基础组件组装进同一条调用路径。

## Check yourself

**自我检查**

1. Where does loop state live if the process dies at step 7, and what must persist to resume without a duplicate side effect?

   如果进程在第 7 步时挂掉，循环状态保存在哪里？要在不产生重复副作用的前提下恢复，必须持久化哪些东西？

2. Derive an idempotency key for a tool call. What happens when the same key arrives with different arguments?

   为一次工具调用推导出一个幂等键。当同一个键携带不同参数到达时会发生什么？

3. Your agent's cost doubled after a prompt change while quality stayed flat. Which three metrics do you inspect first?

   一次提示词变更后，你的 Agent 成本翻了一倍，而质量没有变化。你首先要检查哪三个指标？

4. Why does a 15-minute Lambda limit force a different topology even if runs usually finish in 30 seconds?

   即使运行通常在 30 秒内就能完成，为什么 15 分钟的 Lambda 上限仍会迫使你采用不同的拓扑？

5. Which two of the 12 checks would you cut for a two-week prototype, and what risk do you accept?

   对于一个两周的原型，你会砍掉 12 项检查中的哪两项？你接受了什么风险？

## Reading

**阅读材料**

- [Temporal — use cases and design patterns](https://docs.temporal.io/evaluate/use-cases-design-patterns) — agents as workflows, HITL as signals and timers.

  [Temporal — use cases and design patterns](https://docs.temporal.io/evaluate/use-cases-design-patterns)——把 Agent 当作工作流，把人在回路当作 signal 和 timer。

- [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) — exact multipliers, TTLs and prefix rules.

  [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)——精确的价格倍数、TTL 和前缀规则。

- [AWS Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) — the 15-minute wall and 2026 durable/MicroVM options.

  [AWS Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)——15 分钟的硬墙，以及 2026 年的 durable/MicroVM 选项。

- [Research 03 §4–8](../research/03-production-evals-ops.md) — the full production and governance map.

  [研究 03 §4–8](../research/03-production-evals-ops.md)——完整的生产与治理全景图。

- **Companion book:** *AI Agents in Depth* v2.0, ch.9 §9.1–9.3 (experience → knowledge → instructions → programs → parameters; "done ≠ progress") + ch.7 §7.6/§7.9 (model selection, cost, benchmark→roadmap). The theory behind this repo's trace→eval→publish loop. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 9 章 §9.1–9.3（经验 → 知识 → 指令 → 程序 → 参数；「完成 ≠ 进步」）+ 第 7 章 §7.6/§7.9（模型选择、成本、基准测试 → 路线图）。这是本仓库 trace → 评测 → 发布循环背后的理论。[章节地图](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
