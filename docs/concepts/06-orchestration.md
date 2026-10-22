# 06 — Orchestration and Approval

**06 — 编排与审批**

> **Week 6 · just-in-time concept note.** Read before the lab (~30 min). The lab builds an orchestrator, specialists and an approval gate; this note explains when each is justified and the invariants that make it trustworthy.
>
> **第 6 周 · 即时概念笔记。** 请在做实验（lab）之前阅读（约 30 分钟）。实验会构建一个编排者、若干专员 Agent（specialist）以及一道审批关卡；这篇笔记解释每一样东西在什么情况下才算合理，以及让它值得信赖的不变量。

## The failure mode this prevents

**这篇笔记要防止的失败模式**

A team ships a "swarm": one orchestrator, four specialists, a shared message bus, and a model that decides how many agents to spawn. It demos beautifully. In production it costs **~15× the tokens of a chat interaction**, runs slower than the single-agent version on most tasks, and produces inconsistent decisions: each specialist worked from a different slice of context and made conflicting implicit assumptions. Nobody can say which agent approved what, because "approval" was a boolean in the model's JSON. On retry, the write executes twice.

某个团队上线了一个「蜂群」：一个编排者、四个专员 Agent、一条共享消息总线，外加一个由模型决定要派生多少个 Agent 的机制。演示效果非常漂亮。但在生产环境里，它消耗的 token 是**一次聊天交互的约 15 倍**，在大多数任务上比单 Agent 版本还慢，而且给出的决策前后不一致：每个专员 Agent 都基于上下文的不同切片工作，各自做出了相互冲突的隐含假设。没有人能说清楚哪个 Agent 批准了什么，因为所谓「审批」只是模型 JSON 里的一个布尔值。一旦重试，写操作就会执行两次。

Orchestration is not a maturity ladder. It is a **shape** chosen from the problem's topology — and the safest default is the smallest shape that can do the job.

编排不是一架成熟度阶梯。它是根据问题的拓扑结构选出的一种**形态**——而最安全的默认选择，是能完成任务的最小形态。

## If you remember five things

**如果只记住五件事**

> 1. **Workflow vs agent is the first decision.** Workflow = LLMs/tools orchestrated through predefined code paths (deterministic, cheaper, auditable). Agent = the LLM directs its own process. Most business tasks are workflows.
>
>    **工作流还是 Agent，是第一个要做的决定。** 工作流 = 通过预先定义的代码路径来编排 LLM 和工具（确定性、更便宜、可审计）。Agent = 由 LLM 自己主导执行过程。大多数业务任务都是工作流。
>
> 2. **Choose the smallest sufficient shape.** One capability node → direct call. One reasoning node → single specialist. ≥2 connected nodes → one squad. ≥2 components → multi-squad. Unbacked shape → limitation, never a silent shrink.
>
>    **选择足够用的最小形态。** 一个能力节点 → 直接调用。一个推理节点 → 单个专员 Agent。≥2 个相连节点 → 一个小队（squad）。≥2 个连通分量 → 多小队。没有实现支撑的形态 → 返回限制说明（limitation），绝不悄悄缩小形态。
>
> 3. **Multi-agent is a cost decision, not a quality switch.** Agents use ~4× chat tokens, multi-agent systems ~15×; the headline +90.2% was on breadth-first research, not on your workflow.
>
>    **多 Agent 是一个成本决策，而不是质量开关。** Agent 消耗约 4 倍于聊天的 token，多 Agent 系统约 15 倍；那个醒目的 +90.2% 是在广度优先的研究任务上取得的，不是在你的工作流上。
>
> 4. **Context isolation is a budget, not a wall.** Pass goal, constraints, authority, acceptance criteria and artifact references — never the transcript; return a typed artifact plus evidence.
>
>    **上下文隔离是一种预算，而不是一堵墙。** 传递目标、约束、授权、验收标准和产物引用——绝不传递完整对话记录；返回一个带类型的产物以及证据。
>
> 5. **HITL is durable suspend/resume with a binding.** Persist the proposal before approval; bind actor, tenant, action hash, authority snapshot, expiry; execute at most once; reject edited, replayed, expired approvals.
>
>    **人在回路（HITL）是带绑定的持久化挂起/恢复。** 在审批之前先持久化提案；绑定操作者、租户、动作哈希、授权快照和过期时间；最多执行一次；拒绝被篡改、被重放或已过期的审批。

## The model in one page

**一页看懂模型**

### Workflow patterns you should reach for first

**应当优先考虑的工作流模式**

Anthropic's taxonomy is the clearest: **prompt chaining**, **routing**, **parallelisation** (sectioning or voting), **orchestrator-workers** (dynamic decomposition), **evaluator-optimiser**, and only then the autonomous **agent** loop ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). Each step up buys flexibility and pays in latency, cost and unpredictability. Your week-2 loop is the last rung, not the first.

Anthropic 的分类最为清晰：**提示词链（prompt chaining）**、**路由（routing）**、**并行化（parallelisation）**（分段或投票）、**编排者-工作者（orchestrator-workers）**（动态分解）、**评估者-优化者（evaluator-optimiser）**，最后才是自主的 **Agent** 循环（[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)）。每往上走一级，都是用延迟、成本和不可预测性去换取灵活性。你在第 2 周写的循环是最后一级，而不是第一级。

### The topology decision (and why a model should not make it)

**拓扑决策（以及为什么不该由模型来做）**

The planner decomposes a goal into workstreams bound to either a **capability** (tool/API) or a **reasoning** node (specialist model). Classify the graph, then pick exactly one shape:

规划器把目标分解成若干工作流（workstream），每一个都绑定到一个**能力**节点（工具/API）或一个**推理**节点（专员模型）。先对这张图进行分类，然后恰好选出一种形态：

| Plan shape<br>计划形态 | Execution shape<br>执行形态 | Why<br>原因 |
|---|---|---|
| 1 capability node<br>1 个能力节点 | Direct capability call<br>直接调用能力 | No model needed; zero coordination<br>无需模型；零协调 |
| 1 reasoning node<br>1 个推理节点 | Single specialist<br>单个专员 Agent | One context, one accountable owner<br>一份上下文，一个可问责的负责人 |
| ≥2 connected nodes<br>≥2 个相连节点 | Single squad<br>单个小队 | Specialists collaborate; one composed result<br>专员 Agent 协作；产出一个组合结果 |
| ≥2 unconnected components<br>≥2 个互不相连的分量 | Multi-squad<br>多小队 | Parallel domains; needs a coordinator<br>并行的领域；需要一个协调者 |
| Derived shape unbacked<br>推导出的形态没有实现支撑 | **Limitation**<br>**限制说明** | Fail closed; never guess a smaller shape<br>失败即关闭（fail closed）；绝不猜测一个更小的形态 |

Make the classifier **pure and deterministic** — a function of the validated graph, not an importance score or the model's mood. An LLM choosing topology is how you get fifty subagents for a refund question.

让分类器保持**纯粹且确定**——它是已校验图的函数，而不是某个重要性评分或模型的心情。让 LLM 来选拓扑，你就会为一个退款问题得到五十个子 Agent。

### Orchestrator-worker vs handoffs vs manager

**编排者-工作者 vs 交接 vs 管理者**

| Pattern<br>模式 | Who keeps control<br>谁掌握控制权 | Best for<br>最适合 | Failure mode<br>失败模式 |
|---|---|---|---|
| **Single agent + tools**<br>**单 Agent + 工具** | One loop<br>一个循环 | Most tasks; continuous context<br>大多数任务；上下文连续 | Context overflow on long tasks<br>长任务中上下文溢出 |
| **Orchestrator-workers**<br>**编排者-工作者** | Central planner<br>中央规划器 | Breadth-first independent subtasks<br>广度优先、相互独立的子任务 | Duplication, stale assumptions, 15× cost<br>重复劳动、过时假设、15 倍成本 |
| **Handoffs**<br>**交接** | Receiving agent<br>接收方 Agent | Routing across specialisations<br>在不同专长之间路由 | Context fragmentation, ping-pong loops<br>上下文碎片化、来回踢皮球的循环 |
| **Manager as tools**<br>**以管理者调用工具的方式** | Manager<br>管理者 | Delegation with one decision-maker<br>只有一个决策者的委派 | Manager becomes the bottleneck<br>管理者成为瓶颈 |

The handoff-vs-manager distinction ([OpenAI's practical guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)) usually matters less than whether you need multiple agents at all. If two specialists must agree on a detail to produce consistent output, pass that decision explicitly or do it in one agent ([Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)).

交接与管理者之间的区别（[OpenAI 的实践指南](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)）通常远没有「你到底需不需要多个 Agent」这个问题重要。如果两个专员 Agent 必须在某个细节上达成一致才能产出一致的结果，就显式地传递这个决策，或者干脆在一个 Agent 里完成（[Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)）。

### Context isolation and the hand-off artifact

**上下文隔离与交接产物**

A specialist should receive a **bounded envelope**: objective, constraints, tenant/actor and delegated authority, acceptance criteria, artifact references (row IDs/URIs, not dumps), budget, and the output schema. It returns a **typed artifact**: result, evidence, confidence, cost, open questions. Its transcript stays internal. This makes parallel work composable and stops the "game of telephone" where decisions are lost between hops.

专员 Agent 应当收到一个**有边界的信封**：目标、约束、租户/操作者及被委派的授权、验收标准、产物引用（行 ID/URI，而不是整块数据）、预算，以及输出 schema。它返回一个**带类型的产物**：结果、证据、置信度、成本、未决问题。它的对话记录留在内部。这让并行工作变得可组合，也避免了决策在一次次转手中丢失的「传话游戏」。

SendOS's `SpecialistContext` is exactly this: an ephemeral instance, never persisted. The definition (a published, version-pinned asset) is separate from the instance (one run's bound inputs). Keep that split in your lab: agents are configuration plus context, not mutable objects carrying history.

SendOS 的 `SpecialistContext` 正是这样：一个临时实例，从不持久化。定义（一个已发布、版本固定的资产）与实例（一次运行所绑定的输入）是分开的。在你的实验里也要保持这种拆分：Agent 是配置加上下文，而不是携带历史的可变对象。

### The 15× reality

**15 倍的现实**

Anthropic measured agents at ~4× chat token usage and multi-agent systems at **~15×**, with +90.2% only on breadth-first research where subtasks were genuinely independent ([multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)). The gain came from parallel context capacity, and cost scales with loops. So the test is not "would another agent help?" but "is this subtask independent enough to justify its own loop, and is the task valuable enough to pay for it?" Budget per workstream, aggregate at the orchestrator, and kill the shape when the budget cannot cover the plan.

Anthropic 测得 Agent 的 token 用量约为聊天的 4 倍，多 Agent 系统约为 **15 倍**，而 +90.2% 的提升只出现在子任务真正相互独立的广度优先研究任务上（[multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)）。收益来自并行的上下文容量，而成本随循环数量增长。所以检验标准不是「再加一个 Agent 会不会有帮助？」，而是「这个子任务是否独立到足以值得拥有自己的循环，并且这个任务是否有价值到值得为此买单？」按工作流分配预算，在编排者处汇总，当预算覆盖不了计划时就放弃这种形态。

### Human approval: the two invariants

**人工审批：两条不变量**

A human gate is not a yes/no button. It is **durable suspend/resume** with a binding:

人工关卡不是一个是/否按钮。它是带绑定的**持久化挂起/恢复**：

1. **Persist before approve.** The proposal (action, parameters, evidence) is stored before anyone is asked; the approval references the stored proposal — never the reverse.

   **先持久化，再审批。** 提案（动作、参数、证据）在询问任何人之前就已存储；审批引用的是已存储的提案——绝不能反过来。

2. **Bind what was approved to what executes.** The approval binds actor, tenant, action hash, authority snapshot and expiry. At execution: re-hash the action, re-validate authority, check expiry and unconsumed state, then transition to executed **at most once**. Edited payloads, replays and expired approvals fail closed. Proposer ≠ approver; persist transitions so the audit replays.

   **把被批准的内容与实际执行的内容绑定。** 审批绑定操作者、租户、动作哈希、授权快照和过期时间。执行时：重新计算动作哈希、重新校验授权、检查过期时间和未消费状态，然后**最多一次**地转换到已执行状态。被篡改的载荷、重放和已过期的审批都会失败即关闭。提议者 ≠ 审批者；持久化每次状态转换，以便审计可以回放。

Treat suspend/resume as state, not a paused thread: serialize pending state, let a callback or worker resume it, and guard resume with compare-and-set. SendOS built this as `CaseRuntime` but has not wired it live.

把挂起/恢复当作状态，而不是一个暂停的线程：序列化待处理状态，让回调或工作者来恢复它，并用比较并设置（compare-and-set）来保护恢复操作。SendOS 把它实现为 `CaseRuntime`，但尚未接入线上。

### When multi-agent is the wrong answer

**什么时候多 Agent 是错误答案**

- Work is sequential: each step depends on the previous one (most coding edits).

  工作是顺序的：每一步都依赖上一步（大多数代码编辑都是这样）。

- The task is cheap; a 15× multiplier turns $0.02 into $0.30 with no accuracy gain.

  任务本身很便宜；15 倍的乘数会把 $0.02 变成 $0.30，却没有任何准确率提升。

- There is no typed output contract, so "combining results" is prose merge.

  没有带类型的输出契约，所以「合并结果」就成了拼接散文。

- You cannot trace, evaluate or budget each loop — you will not debug the failures.

  你无法对每个循环进行追踪、评测或预算控制——你将无法调试其中的失败。

- Consistency matters more than throughput; shared decisions are expensive across agents.

  一致性比吞吐量更重要；跨 Agent 共享决策的代价很高。

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>实际情况 |
|---|---|
| "More agents = better accuracy."<br>「Agent 越多 = 准确率越高。」 | Only when subtasks are independent and parallelisable; otherwise coordination loss exceeds the gain.<br>只有当子任务相互独立且可并行时才成立；否则协调损耗会超过收益。 |
| "Multi-agent is how you get parallelism."<br>「多 Agent 才能实现并行。」 | Parallel tool calls inside one agent often suffice; orchestration adds planning and merge overhead.<br>在一个 Agent 内部并行发起工具调用通常就够了；编排会额外增加规划和合并的开销。 |
| "The orchestrator should decide the topology."<br>「应该由编排者来决定拓扑。」 | Topology follows from the validated plan; a pure classifier prevents fan-out driven by ambiguity.<br>拓扑由已校验的计划推导而来；纯函数分类器可以防止由歧义驱动的扇出。 |
| "Sub-agents should inherit the full transcript."<br>「子 Agent 应该继承完整的对话记录。」 | That inflates cost and contaminates context; pass decisions, constraints and artifact refs.<br>那会抬高成本并污染上下文；应传递决策、约束和产物引用。 |
| "An approval flag in model JSON is HITL."<br>「模型 JSON 里的一个审批标志就是人在回路。」 | Without persistence, binding, revalidation and at-most-once consumption, it is decoration.<br>没有持久化、绑定、重新校验和最多一次消费，它只是摆设。 |

## How this shows up in SendOS

**这在 SendOS 中如何体现**

- **Topology as a pure function.** `TopologyClassifier.cs:28-102` and `ExecutionPlanner.cs:143-230` derive one shape from the plan and emit a limitation when unbacked; ADR-0001 exists to remove fan-out driven by ambiguity. That rule is the lab's spec — copy the classifier, not any confidence heuristic.

  **拓扑是一个纯函数。** `TopologyClassifier.cs:28-102` 和 `ExecutionPlanner.cs:143-230` 从计划中推导出一种形态，在没有实现支撑时输出限制说明；ADR-0001 的存在就是为了消除由歧义驱动的扇出。这条规则就是实验的规格说明——照搬分类器，而不是任何置信度启发式。

- **Approval as state with a binding.** `ApprovalCheckpoint.cs:237-468,470-571` persists the proposal before approval, binds tenant/actor/action hash/authority snapshot/expiry (15 minutes), runs six transitions and executes at most once; `ApprovalBindingAtMostOncePropertyTests.cs` encodes the invariants. If your lab approval can be edited after approval and still execute, you missed the week.

  **审批是带绑定的状态。** `ApprovalCheckpoint.cs:237-468,470-571` 在审批前持久化提案，绑定租户/操作者/动作哈希/授权快照/过期时间（15 分钟），执行六种状态转换，并且最多执行一次；`ApprovalBindingAtMostOncePropertyTests.cs` 把这些不变量编码成了测试。如果你实验中的审批在批准后还能被修改并照样执行，那这一周你就白学了。

- **Instance vs definition.** `SpecialistContext.cs` is an ephemeral, never-persisted context; `ISquadMessageBus`/`InMemorySquadMessageBus` carries structured `SquadMessage` while the transcript stays internal and exactly one `DecisionInteraction` leaves — how a squad stays auditable.

  **实例与定义。** `SpecialistContext.cs` 是一个临时的、从不持久化的上下文；`ISquadMessageBus`/`InMemorySquadMessageBus` 传递结构化的 `SquadMessage`，而对话记录留在内部，只有恰好一个 `DecisionInteraction` 离开——这就是小队保持可审计的方式。

## Check yourself

**自我检查**

1. A plan has one reasoning node and one disconnected capability node. Which shape, and what if the derived shape is unbacked?

   一个计划包含一个推理节点和一个与之不相连的能力节点。应该选哪种形态？如果推导出的形态没有实现支撑又该怎么办？

2. What goes in a specialist's hand-off envelope, and what must never cross the boundary?

   专员 Agent 的交接信封里应该放什么？什么东西绝不能越过这条边界？

3. Estimate 1 orchestrator + 4 workers at 8 steps each versus a single agent at 12 steps. When is the squad justified?

   估算一下：1 个编排者 + 4 个工作者、每个 8 步，对比单个 Agent 走 12 步。什么情况下小队才是合理的？

4. An approval arrives expired and with an edited amount. Which invariant rejects each, at which check?

   一个审批到达时已经过期，并且金额被修改过。分别是哪条不变量、在哪一项检查中拒绝了它们？

5. Why must topology selection be a pure function, and what failure does the classifier prevent?

   为什么拓扑选择必须是一个纯函数？分类器防止了哪种失败？

## Reading

**阅读材料**

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow vs agent, the five patterns.

  [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)——工作流与 Agent 的区别，五种模式。

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — 15× cost, +90.2% only on breadth-first research.

  [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)——15 倍成本，+90.2% 只出现在广度优先的研究任务上。

- [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — context isolation, conflicting implicit decisions.

  [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)——上下文隔离，相互冲突的隐含决策。

- [Research 01 §6](../research/01-agent-architecture-sota.md) — autonomy, HITL, durable pause/resume.

  [研究 01 §6](../research/01-agent-architecture-sota.md)——自主性、人在回路、持久化的暂停/恢复。

- **Companion book:** *AI Agents in Depth* v2.0, ch.10 §10.1–10.5 + ch.2 §2.7.6 — shared vs non-shared context × topology, the information-gain test for multi-agent, and six named failure modes. It complements this note's approval-first framing. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 10 章 §10.1–10.5 + 第 2 章 §2.7.6——共享与非共享上下文 × 拓扑、判断是否需要多 Agent 的信息增益检验，以及六种有名字的失败模式。它是对本笔记「审批优先」框架的补充。[章节地图](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
