# 04 — Memory

**04 — 记忆**

> **Week 4 · just-in-time concept note.** Read after [03 — Context Engineering](./03-context-engineering.md), before the [context & memory lab](../../labs/week04-context-memory/README.md) (~25 min). Context engineering keeps one run coherent; memory is what survives between runs — and it is the feature most often built before it is understood.
>
> **第 4 周 · 即时概念笔记。** 在读完 [03 — 上下文工程](./03-context-engineering.md)之后、做[上下文与记忆实验](../../labs/week04-context-memory/README.md)之前阅读（约 25 分钟）。上下文工程让单次运行保持连贯；记忆则是在多次运行之间留存下来的东西——而它也是最常在被理解之前就被构建出来的功能。

## The failure mode this prevents

**本机制防止的失败模式**

The agent that remembers the wrong thing. A semantic store picks up "enterprise discount cap is 25%" from a March call; the policy changes in June; in August the agent recalls the fact confidently and proposes a 25% discount. A human approver catches it — or does not. The mirror-image failure is the agent that remembers nothing: every session re-asks for the account ID, the order number, the constraint the customer already stated. And the most expensive failure is the memory project that never pays off: a vector database bolted on, six weeks of work, no measurable lift — because nobody built a cross-session eval, so nobody could tell whether recall helped or just added tokens and staleness.

一个记错了东西的 Agent。语义存储从三月份的一次通话中记下了“企业折扣上限为 25%”；六月份策略变了；到了八月，Agent 自信地回忆起这条事实，并提出了 25% 的折扣。人工审批者可能会发现它——也可能不会。与之镜像的失败是一个什么都不记得的 Agent：每个会话都要重新询问账户 ID、订单号，以及客户早已说明过的约束。而代价最高的失败，是一个永远无法回本的记忆项目：硬加上一个向量数据库，花了六周时间，却没有任何可测量的提升——因为没有人构建跨会话的评测（eval），所以没有人能判断召回到底是有帮助，还是只增加了 token 和过时内容。

Memory done well is narrow, explicit and governed: four kinds with different schemas, provenance on every fact, consolidation that prefers appending over rewriting, and a clear answer to *when not to build it*.

做得好的记忆是范围窄、显式且受治理的：四种具有不同 schema 的记忆，每条事实都有来源（provenance），整合时优先追加而非重写，并且对*什么时候不该构建它*有清晰的答案。

## If you remember five things

**如果只记住五件事**

> 1. **Four kinds, four designs.** Working (the window), episodic (what happened — append-only trace), semantic (facts with provenance), procedural (how to do things — versioned assets/skills). Conflating them is the root design error.
>
>    **四种记忆，四种设计。** 工作记忆（即窗口）、情景记忆（发生了什么——只追加的 trace）、语义记忆（带来源的事实）、程序性记忆（如何做事——有版本的资产/skill）。把它们混为一谈是根本性的设计错误。
>
> 2. **Memory is a policy plus a tool surface, not a vector database.** MemGPT's paging, Letta's memory blocks and Anthropic's memory tool are three versions of "the model performs explicit memory operations you can audit".
>
>    **记忆是一套策略加一组工具界面，而不是一个向量数据库。** MemGPT 的分页、Letta 的记忆块和 Anthropic 的记忆工具，是“模型执行你可以审计的显式记忆操作”这一思想的三个版本。
>
> 3. **Consolidation wins or loses the feature.** Extract, dedupe, resolve contradictions, delete — incrementally. Summarise-only pipelines lose detail (brevity bias) and degrade across rewrites (context collapse).
>
>    **整合决定了这个功能的成败。** 提取、去重、解决矛盾、删除——都要增量地进行。只做摘要的流水线会丢失细节（简洁性偏差，brevity bias），并在反复重写中不断退化（上下文坍塌，context collapse）。
>
> 4. **Provenance and authority are non-negotiable.** Every remembered fact carries source, time, version and tenant; semantic memory must never outrank published policy or an authoritative metric.
>
>    **来源与权威性没有商量余地。** 每条被记住的事实都要携带出处、时间、版本和租户；语义记忆的优先级绝不能高于已发布的策略或权威指标。
>
> 5. **Do not build memory until a cross-session eval exists** and stateless alternatives are exhausted. Most product "memory" requirements are better served by a retrieval index or a notes file.
>
>    **在跨会话评测存在之前，不要构建记忆**，也要先穷尽无状态的替代方案。大多数产品层面的“记忆”需求，用检索索引或笔记文件来满足会更好。

## The model in one page

**一页看懂模型**

### Four kinds of memory

**四种记忆**

| Kind<br>类型 | Question it answers<br>回答的问题 | Store<br>存储 | Retention<br>保留期 | Why it cannot be merged<br>为什么不能合并 |
|---|---|---|---|---|
| Working<br>工作记忆 | what is true *now* in this run?<br>在本次运行中，*此刻*什么是真的？ | context window<br>上下文窗口 | the run<br>本次运行 | evicted by design; compaction is its management<br>按设计会被逐出；压缩就是对它的管理 |
| Episodic<br>情景记忆 | what happened, in order?<br>按顺序发生了什么？ | append-only trace / event log<br>只追加的 trace / 事件日志 | days–months<br>数天到数月 | audit + replay require immutability<br>审计 + 重放要求不可变性 |
| Semantic<br>语义记忆 | what is true about the user/org/domain?<br>关于用户/组织/领域，什么是真的？ | vector + KV + graph<br>向量 + KV + 图 | long<br>长期 | needs contradiction resolution and versioning<br>需要矛盾消解和版本管理 |
| Procedural<br>程序性记忆 | how do we do this task?<br>这项任务该怎么做？ | skills, playbooks, prompts, code<br>skill、操作手册、提示词、代码 | versioned<br>有版本 | must be reviewed/published, never model-writable<br>必须经过评审/发布，绝不允许模型写入 |

An append-only trace is episodic memory. A published prompt is procedural memory. A pgvector index over documents is **retrieval**, not memory — it has no notion of what the agent learned or when it became stale.

只追加的 trace 是情景记忆。已发布的提示词是程序性记忆。基于文档的 pgvector 索引是**检索**，而不是记忆——它不知道 Agent 学到了什么，也不知道这些内容何时变得过时。

### The lineage: paging, blocks, files

**演进脉络：分页、记忆块、文件**

**MemGPT** `[foundational]` framed the LLM as an OS managing limited main memory, paging between a main context, recall storage (conversation history) and archival storage (vector DB) through function calls, with interrupts for memory pressure and self-directed edits ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)). **Letta** turns this into read/write *memory blocks* plus background ("sleep-time") reorganisation between turns. **Anthropic's memory tool** is the minimal version: a client-side file directory the model can create, read, update and delete, where *you* own the storage and persistence, paired with context editing ([Anthropic, 2025-09](https://claude.com/resources/articles/context-management)).

**MemGPT** `[foundational]` 把 LLM 构想成一个管理有限主存的操作系统，通过函数调用在主上下文、召回存储（对话历史）和归档存储（向量数据库）之间进行分页，并带有应对内存压力的中断机制和自主发起的编辑（[arXiv:2310.08560](https://arxiv.org/abs/2310.08560)）。**Letta** 将其变成可读写的*记忆块*，外加在轮次之间进行的后台（“睡眠时间”）重组。**Anthropic 的记忆工具**是最精简的版本：一个模型可以创建、读取、更新和删除的客户端文件目录，存储和持久化由*你*掌控，并与上下文编辑配合使用（[Anthropic, 2025-09](https://claude.com/resources/articles/context-management)）。

The shared lesson is more important than any of the implementations: **memory operations are explicit, typed and auditable**. The model calls `memory.write(...)`, not "the system silently embeds the turn". If you build the week-4 module this way, you can test it, scope it per tenant, delete it on request, and trace why a fact was recalled.

它们共同的经验比任何一种具体实现都更重要：**记忆操作是显式的、有类型的、可审计的**。模型调用的是 `memory.write(...)`，而不是“系统悄悄地把这一轮嵌入进去”。如果你按这种方式构建第 4 周的模块，你就能测试它、按租户划分其作用域、按请求删除它，并追踪某条事实为何被召回。

### Retrieval is a component, not the answer

**检索是一个组件，而不是答案**

The lab builds retrieval from scratch: chunking, an embedding interface (deterministic fake for tests, one real provider for behaviour), cosine similarity in numpy, then a SQLite store — with a written comparison to pgvector. Design choices that matter:

实验会从零构建检索：分块、一个嵌入接口（用于测试的确定性假实现，以及一个用于实际行为的真实模型提供商（provider））、用 numpy 计算余弦相似度，然后是一个 SQLite 存储——并附上一份与 pgvector 的书面对比。重要的设计选择包括：

- **Hybrid beats pure vector** in enterprise text: lexical match for IDs, product codes and names; semantic for paraphrase. Rerank the top 20 to the top 5 rather than retrieving 5 straight away.

  在企业文本中，**混合检索胜过纯向量检索**：用词法匹配处理 ID、产品编码和名称；用语义匹配处理同义改写。先取前 20 条再重排序到前 5 条，而不是直接检索 5 条。

- **Retrieval quality dominates window size.** On LongMemEval, focused inputs (~300 tokens) beat full histories (~113k tokens) for every model family tested ([Chroma, 2025](https://www.trychroma.com/research/context-rot)). The win is not "more history", it is "the right 300 tokens".

  **检索质量比窗口大小更重要。** 在 LongMemEval 上，对所有被测的模型家族而言，聚焦的输入（约 300 token）都胜过完整的历史（约 113k token）（[Chroma, 2025](https://www.trychroma.com/research/context-rot)）。取胜的关键不是“更多的历史”，而是“正确的那 300 个 token”。

- **Budget the result.** Retrieval returns tokens into an already-tight context budget; set `top_k` and a token cap per query, and return references before bodies when the model may not need the body.

  **为结果设定预算。** 检索会把 token 送进一个本已紧张的上下文预算中；为每次查询设置 `top_k` 和 token 上限，并且在模型可能用不到正文时，先返回引用再返回正文。

Retrieval answers "*what documents are relevant?*". Memory answers "*what does this agent know, from experience, that is still true?*" The second needs provenance and a write policy; the first does not.

检索回答的是“*哪些文档是相关的？*”。记忆回答的是“*这个 Agent 从经验中知道的哪些东西至今仍然成立？*”后者需要来源和写入策略；前者则不需要。

### Consolidation: where memory quality is won

**整合：记忆质量的决胜之处**

A write path, not a dump:

一条写入路径，而不是一次倾倒：

```text
candidate = extract_facts(turn)               # typed: subject, predicate, value, scope
for fact in candidate:
    fact.provenance = {source, tool, run_id, ts, asset_version}
    existing = store.search(fact.subject)
    if conflict(existing, fact):  store.mark_conflict(...)   # never silently overwrite
    elif duplicate(existing, fact): store.reinforce(existing, fact.provenance)
    else: store.append(fact)
```

Two named pathologies to design against: **brevity bias** (concise summaries drop domain insight) and **context collapse** (iterative rewriting erodes detail). ACE's fix is structured, **incremental** updates that preserve detailed knowledge instead of rewriting whole contexts ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618), ICLR 2026). Concretely: append facts and curate periodically; never let a summariser be the only copy of a decision.

设计时要防范两种有名有姓的病症：**简洁性偏差**（简洁的摘要会丢掉领域洞见）和**上下文坍塌**（反复重写会侵蚀细节）。ACE 的解决办法是采用结构化的**增量**更新，保留详细知识，而不是重写整个上下文（[arXiv:2510.04618](https://arxiv.org/abs/2510.04618)，ICLR 2026）。具体来说：追加事实并定期整理；绝不要让摘要器成为某个决策的唯一副本。

Design the **subtraction** path from day one: contradiction marking, TTLs, tenant-scoped deletion, "forget this user". A memory store you cannot delete from is a compliance liability, not a feature.

从第一天起就设计好**删减**路径：矛盾标记、TTL、按租户范围删除、“忘记这个用户”。一个无法从中删除数据的记忆存储是一项合规负债，而不是一个功能。

### Benchmarks and honest numbers

**基准测试与诚实的数字**

- **LongMemEval** ([arXiv:2410.10813](https://arxiv.org/abs/2410.10813)) is the reference conversational long-term-memory suite — and the benchmark behind the focused-context result above.

  **LongMemEval**（[arXiv:2410.10813](https://arxiv.org/abs/2410.10813)）是对话式长期记忆的参考测试集——也是上文“聚焦上下文”结论背后的基准。

- **Mem0** reports production-oriented extraction/consolidation gains at lower token cost ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413)); it is vendor-authored, so read the method and treat exact deltas as optimistic.

  **Mem0** 报告了面向生产的提取/整合收益，且 token 成本更低（[arXiv:2504.19413](https://arxiv.org/abs/2504.19413)）；它出自厂商之手，所以要读一读其方法，并把具体的提升幅度视为偏乐观的数字。

- **No public benchmark measures organisational memory**: permissions, retention, cross-tenant isolation, authority. That risk is yours to measure.

  **没有任何公开基准测量组织级记忆**：权限、保留期、跨租户隔离、权威性。这部分风险需要你自己去测量。

A credible local measurement set: cross-session task success with vs without memory; **stale-answer rate** (facts contradicted by the current authoritative source); recalled-token cost per task; and deletion correctness (does "forget" remove the fact from every store?).

一套可信的本地测量指标：有记忆与无记忆时的跨会话任务成功率；**过时回答率**（与当前权威来源相矛盾的事实）；每个任务召回内容的 token 成本；以及删除正确性（“忘记”是否会把这条事实从每一个存储中移除？）。

### When NOT to build memory

**什么时候不该构建记忆**

1. The task is stateless or single-session (most back-office automation).

   任务是无状态的或单会话的（大多数后台自动化都是如此）。

2. You have no eval that measures cross-session success — you cannot tell whether memory helps.

   你没有衡量跨会话成功率的评测——你无法判断记忆是否有帮助。

3. You cannot say what must **never** be remembered (PII, secrets, regulated data) or how deletion works.

   你说不清哪些内容**绝不能**被记住（PII、机密、受监管数据），或者删除是如何进行的。

4. A retrieval index over existing knowledge already answers the need (that is not agent memory).

   基于现有知识的检索索引已经满足了需求（那不是 Agent 记忆）。

5. The "memory" would be an unversioned prompt blob — that is procedural memory; make it a reviewed, versioned asset.

   所谓的“记忆”只是一段没有版本的提示词——那属于程序性记忆；应把它做成经过评审、有版本的资产。

6. Tenant scoping and provenance are unsolved — a shared memory pool across tenants is a data breach waiting to happen.

   租户作用域和来源问题尚未解决——跨租户共享的记忆池就是一场随时会发生的数据泄露。

### Memory and the learning loop

**记忆与学习循环**

Episodic memory (traces) is the substrate; **learning** is the process that turns it into procedural memory. That process — trace → distill → candidate → eval → human publish — is week 7's learning-loop material. SendOS names the pieces: append-only `Outcome_Trace`, a five-dimension evaluator, an evidence gate (sample ≥ 30, confidence ≥ 0.7, quality ≥ 0.5), and a **submit-only** promoter: a model can create a `Draft`, never a `Published` asset ([research 05 §2.4](../research/05-sendos-concept-map.md)). The safety property is the point: memory may remember, but only humans promote policy.

情景记忆（trace）是基础；**学习**则是把它转化为程序性记忆的过程。这个过程——trace → 提炼 → 候选 → 评测 → 人工发布——是第 7 周学习循环的内容。SendOS 为其中的各个部分都起了名字：只追加的 `Outcome_Trace`、一个五维度的评估器、一道证据关卡（样本 ≥ 30、置信度 ≥ 0.7、质量 ≥ 0.5），以及一个**只能提交**的晋升器：模型可以创建 `Draft`，但绝不能创建 `Published` 资产（[research 05 §2.4](../research/05-sendos-concept-map.md)）。要点就在于这一安全性质：记忆可以记住东西，但只有人类才能把内容晋升为策略。

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>现实 |
|---|---|
| "A vector DB is memory."<br>“向量数据库就是记忆。” | That is retrieval. Memory needs write policy, provenance, contradiction handling, retention and deletion.<br>那是检索。记忆需要写入策略、来源、矛盾处理、保留期和删除。 |
| "More remembered context is better."<br>“记住的上下文越多越好。” | Stale and contradictory facts are worse than none; context rot applies to recalled content too.<br>过时和相互矛盾的事实比没有更糟；上下文腐化（context rot）同样适用于召回的内容。 |
| "Memory should be invisible and automatic."<br>“记忆应该是隐形且自动的。” | Invisible memory is untestable and unauditable. Expose explicit operations you can trace.<br>隐形的记忆无法测试、无法审计。应暴露你可以追踪的显式操作。 |
| "Summaries are a safe way to persist knowledge."<br>“摘要是持久化知识的安全方式。” | Summaries lose detail (brevity bias) and degrade under repeated rewriting (context collapse). Append + curate.<br>摘要会丢失细节（简洁性偏差），并在反复重写中退化（上下文坍塌）。应该追加 + 整理。 |
| "One store for everything."<br>“一个存储搞定一切。” | Episodic, semantic and procedural have different schemas, retention and review processes.<br>情景记忆、语义记忆和程序性记忆有着不同的 schema、保留期和评审流程。 |
| "Memory is a user-private feature."<br>“记忆是用户私有的功能。” | In an enterprise platform it is tenant-scoped, authority-governed data. Over-sharing is a governance bug.<br>在企业平台中，它是按租户划分、受权威性治理的数据。过度共享是一个治理 bug。 |

## How this shows up in SendOS

**在 SendOS 中如何体现**

- **Episodic memory is literally an append-only log.** `Outcome_Trace` has a closed 21-event lifecycle, store-assigned monotonic `Sequence`, and a DB trigger that denies `UPDATE`/`DELETE` ([research 05 §2.4](../research/05-sendos-concept-map.md)). If the trace cannot be replayed, it cannot be trusted as memory — immutability precedes every learning mechanism built on it.

  **情景记忆实打实地就是一份只追加的日志。** `Outcome_Trace` 有一个封闭的 21 种事件的生命周期、由存储分配的单调递增 `Sequence`，以及一个拒绝 `UPDATE`/`DELETE` 的数据库触发器（[research 05 §2.4](../research/05-sendos-concept-map.md)）。如果 trace 无法重放，它就不能作为记忆被信任——不可变性先于建立在它之上的所有学习机制。

- **Semantic memory has an authority hierarchy.** The published `BusinessSemanticDefinition` is tenant-authoritative; user overlays are additive and can never override the metric formula ([research 05 §2.3](../research/05-sendos-concept-map.md)). That is the enterprise version of this note's rule: remembered facts never outrank published, versioned definitions.

  **语义记忆有一套权威层级。** 已发布的 `BusinessSemanticDefinition` 在租户内具有权威性；用户叠加层只能做补充，永远不能覆盖指标公式（[research 05 §2.3](../research/05-sendos-concept-map.md)）。这就是本笔记规则的企业版：被记住的事实的优先级永远不会高于已发布、有版本的定义。

- **Procedural memory is a published asset, not a model write.** The distillation/evidence-gate/publish pipeline keeps candidates as diffs against a base version and requires a human approval row before `Published` ([research 05 §4.3](../research/05-sendos-concept-map.md)). Your week-4 consolidation rule is the miniature of that gate.

  **程序性记忆是一个已发布的资产，而不是模型的一次写入。** 提炼/证据关卡/发布这条流水线把候选项保存为相对于基础版本的差异（diff），并要求在变为 `Published` 之前存在一条人工审批记录（[research 05 §4.3](../research/05-sendos-concept-map.md)）。你第 4 周的整合规则就是这道关卡的缩影。

## Check yourself

**自测**

1. Which memory kind does an append-only trace implement, and why does immutability matter *before* building consolidation or learning on top?

   只追加的 trace 实现的是哪种记忆？为什么在其上构建整合或学习机制*之前*，不可变性就很重要？

2. Why must semantic memory never outrank a published definition? What mechanism could enforce it, and what happens if that mechanism lives only in the prompt?

   为什么语义记忆的优先级绝不能高于已发布的定义？什么机制可以强制保证这一点？如果这个机制只存在于提示词中，会发生什么？

3. What are ACE's two named failure modes, and what design choice in your write path avoids them?

   ACE 提出的两种有名称的失败模式是什么？你的写入路径中的哪个设计选择能避免它们？

4. Name three measurements you would need before adding memory to an agent, and what each is protecting against.

   在给 Agent 添加记忆之前，你需要哪三项测量？每一项分别在防范什么？

5. A user invokes "forget me". What must your design guarantee across episodic, semantic and procedural stores — and which one is hardest to satisfy?

   一位用户发起了“忘记我”的请求。你的设计必须在情景、语义和程序性存储中保证什么——其中哪一个最难满足？

## Reading

**延伸阅读**

- [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) (2023) — the memory hierarchy and paging model; short and still the best framing.

  [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)（2023）——记忆层级与分页模型；篇幅短小，至今仍是最好的框架。

- [Mem0: production long-term memory](https://arxiv.org/abs/2504.19413) (2025) — extraction/consolidation with cost and latency numbers; read critically.

  [Mem0: production long-term memory](https://arxiv.org/abs/2504.19413)（2025）——附有成本和延迟数据的提取/整合方案；要带着批判的眼光阅读。

- [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618) (ICLR 2026) — evolving playbooks, brevity bias and context collapse.

  [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618)（ICLR 2026）——不断演进的操作手册、简洁性偏差和上下文坍塌。

- [A-MEM: Agentic Memory](https://arxiv.org/abs/2502.12110) (2025) — Zettelkasten-style linked notes; a useful contrast to flat vector memory.

  [A-MEM: Agentic Memory](https://arxiv.org/abs/2502.12110)（2025）——卡片盒（Zettelkasten）风格的互链笔记；可与扁平的向量记忆形成有益的对比。

- **Companion book:** *AI Agents in Depth* v2.0, ch.3 §3.1–3.3 — memory hierarchy and storage formats, RAG chunking/dense/sparse/hybrid retrieval, structured indexing, agentic RAG, contextual retrieval. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 3 章 §3.1–3.3——记忆层级与存储格式、RAG 分块/稠密/稀疏/混合检索、结构化索引、Agent 式 RAG、上下文检索。[章节对照表](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
