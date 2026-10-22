# 03 — Context Engineering

**03 — 上下文工程**

> **Weeks 3–4 · just-in-time concept note.** Read before week 3's [structured-output lab](../../labs/week03-structured-output/README.md) (~20 min) and re-read before week 4's [context & memory lab](../../labs/week04-context-memory/README.md). Week 3 teaches you that prompts are versioned assets; week 4 makes context a budget you manage at runtime.
>
> **第 3–4 周 · 即时概念笔记。** 在做第 3 周的[结构化输出实验](../../labs/week03-structured-output/README.md)之前阅读（约 20 分钟），并在做第 4 周的[上下文与记忆实验](../../labs/week04-context-memory/README.md)之前重读。第 3 周教你认识到提示词是有版本的资产；第 4 周则让上下文成为你在运行时管理的一项预算。

## The failure mode this prevents

**本机制防止的失败模式**

The agent that forgot the one constraint that mattered. It starts with a system prompt containing the policy — "never discount below 15%, never email a customer without approval" — then works for forty turns, accumulates 90k tokens of search results, compacts to stay alive, and proposes a 30% discount. Compaction preserved the *task* but not the *constraint*, because nobody marked the constraint as pinned. A second version: a tool returns a stale wiki page saying the refund window is 90 days (it is 30), the agent answers confidently, and no later observation contradicts it — context poisoning.

一个忘记了唯一关键约束的 Agent。它一开始的系统提示词里写着策略——“折扣绝不能低于 15%，未经审批绝不能给客户发邮件”——然后工作了四十轮，积累了 90k token 的搜索结果，为了维持运行而进行了压缩，接着就提出了 30% 的折扣。压缩保留了*任务*，却没有保留*约束*，因为没有人把这条约束标记为固定（pinned）。第二种形态：某个工具返回了一个过时的 wiki 页面，上面写着退款期限是 90 天（实际是 30 天），Agent 自信地作答，之后也没有任何观察结果与之矛盾——这就是上下文投毒（context poisoning）。

Context engineering makes all three structurally unlikely: context as an attention budget, explicit priority classes, compaction that knows what must survive, state externalised to files, and provenance on anything retrieved.

上下文工程让这三种情况在结构上都不太可能发生：把上下文视为注意力预算、明确的优先级类别、知道哪些内容必须保留的压缩、外置到文件中的状态，以及为一切检索内容标注来源（provenance）。

## If you remember five things

**如果只记住五件事**

> 1. **Context is an attention budget, not a bucket.** Accuracy degrades non-uniformly as input grows — even at constant task difficulty ([Chroma, 2025](https://www.trychroma.com/research/context-rot)) — and every extra token costs money and latency.
>
>    **上下文是一项注意力预算，而不是一个桶。** 随着输入增长，准确率会非均匀地下降——即使任务难度保持不变也是如此（[Chroma, 2025](https://www.trychroma.com/research/context-rot)）——而且每多一个 token 都要付出金钱和延迟的代价。
>
> 2. **Classify before you trim.** Pinned constraints (policy, authority, approval state) are never evicted; then task state, recent turns, tool observations, history. Eviction order is the opposite of importance order.
>
>    **先分类，再裁剪。** 固定约束（策略、权限、审批状态）永远不会被逐出；其次是任务状态、最近的轮次、工具观察结果、历史记录。逐出顺序与重要性顺序正好相反。
>
> 3. **Compaction order matters:** clear stale tool results first, then summarise. Preserve decisions, unresolved bugs, artifacts and the recent working set; tune the prompt on real traces, recall first.
>
>    **压缩的顺序很重要：** 先清除过时的工具结果，再做摘要。保留决策、未解决的 bug、产出物和最近的工作集；基于真实的 trace 调优提示词，召回率优先。
>
> 4. **Externalise state before you need to.** A progress file, a JSON feature list and git history survive a context reset better than any prompt. Files-as-context + just-in-time retrieval is the production pattern.
>
>    **在需要之前就把状态外置。** 进度文件、JSON 功能列表和 git 历史在上下文重置后的存活能力胜过任何提示词。文件即上下文 + 即时检索，是生产环境的模式。
>
> 5. **Poisoning is a context problem.** Every retrieved fact needs provenance, untrusted content must be delimited as data, and policy lives in pinned context — never in something a tool returned.
>
>    **投毒是一个上下文问题。** 每条检索到的事实都需要来源，不可信的内容必须作为数据加上分隔标记，而策略要放在固定上下文中——绝不能放在工具返回的内容里。

## The model in one page

**一页看懂模型**

### The evidence: context rot is real and non-uniform

**证据：上下文腐化（context rot）真实存在，且是非均匀的**

Chroma evaluated 18 models while holding task difficulty constant and varying only input length: performance degrades with length; lower needle–question similarity degrades faster; a single distractor hurts and four compound; shuffled haystacks outperform coherent ones; and on LongMemEval, **focused inputs (~300 tokens) beat full inputs (~113k tokens)** across every model family ([Chroma, 2025](https://www.trychroma.com/research/context-rot)). Anthropic's explanation is an "attention budget" depleted per token, with n² attention relationships stretched thin as context grows ([Anthropic, 2025-09](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). A larger window is *capacity*, not *quality*: treat every retrieval, tool result and summary as a spend whose exchange rate you can measure only on your own tasks.

Chroma 在保持任务难度不变、只改变输入长度的条件下评测了 18 个模型：性能随长度增加而下降；“针”与问题的相似度越低，下降得越快；单个干扰项就会造成损害，四个干扰项则会叠加；打乱顺序的“干草堆”反而比连贯的表现更好；而在 LongMemEval 上，**聚焦的输入（约 300 token）在所有模型家族上都胜过完整输入（约 113k token）**（[Chroma, 2025](https://www.trychroma.com/research/context-rot)）。Anthropic 的解释是存在一个按 token 消耗的“注意力预算”，随着上下文增长，n² 个注意力关系被摊得越来越薄（[Anthropic, 2025-09](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。更大的窗口意味着*容量*，而不是*质量*：把每一次检索、每一个工具结果和每一份摘要都看作一笔开支，而它的汇率只能在你自己的任务上测量。

### What is actually in the window

**窗口里实际装着什么**

| Segment<br>段 | Mutability<br>可变性 | Eviction policy<br>逐出策略 |
|---|---|---|
| System prompt, policy, tool definitions<br>系统提示词、策略、工具定义 | versioned assets / per step<br>有版本的资产 / 每步 | never; prune tools instead<br>从不逐出；改为精简工具 |
| Pinned constraints: goal, authority, approvals<br>固定约束：目标、权限、审批 | immutable per run<br>单次运行内不可变 | **never**<br>**从不逐出** |
| Task state / notes<br>任务状态 / 笔记 | agent-written<br>由 Agent 写入 | keep, compact<br>保留，可压缩 |
| Recent turns<br>最近的轮次 | rolling<br>滚动 | keep the last N<br>保留最后 N 轮 |
| Tool observations<br>工具观察结果 | per step<br>每步 | truncate at source; clear stale results first<br>在源头截断；优先清除过时结果 |
| Retrieved artifacts<br>检索到的产出物 | per step<br>每步 | references first, bodies on demand<br>先给引用，正文按需加载 |

The week-4 `agentlab/context/window.py` lab asks you to implement exactly this: a token estimate, priority classes, and a budget policy in which pinned constraints cannot be evicted.

第 4 周的 `agentlab/context/window.py` 实验要求你实现的正是这些：token 估算、优先级类别，以及一个固定约束不可被逐出的预算策略。

### Assembly: a budget policy, not string concatenation

**组装：一项预算策略，而不是字符串拼接**

```python
order = [pinned_constraints, task_state, recent_turns, tool_observations, summary]
if tokens(pinned_constraints) > budget: raise ContextBudgetError  # fail closed
fill in order, cap each class, drop from the bottom first
```

Two rules prevent most incidents: **fail closed** when pinned content does not fit (a run with a policy it cannot see is worse than one that refuses), and **estimate tokens conservatively** (characters/3.5 for code-heavy English beats /4; never trust a provider count you have not measured).

两条规则就能防止大多数事故：当固定内容放不下时要**失败即关闭（fail closed）**（一个看不到策略的运行比一个拒绝执行的运行更糟），以及**保守地估算 token**（对于代码较多的英文，用字符数/3.5 比 /4 更好；绝不要信任一个你没有亲自测量过的模型提供商（provider）计数）。

### Compaction: cheap first, summary second

**压缩：先做便宜的，再做摘要**

Compaction = replacing a near-full transcript with a bounded carry-forward note. Order of operations, cheapest first:

压缩（compaction）= 用一份有长度上限的延续笔记（carry-forward note）替换一份快要占满窗口的对话记录。操作顺序如下，最便宜的在前：

1. **Clear stale tool results.** Once a result has been consumed (a file read that produced an edit, a search that produced a decision), the raw payload usually has no further value. Anthropic ships context editing for this; on their agentic-search eval, context editing alone improved performance **29%**, memory tool + context editing **39%**, with **84%** fewer tokens on a 100-turn web-search eval ([Anthropic, 2025-09](https://claude.com/resources/articles/context-management)).

   **清除过时的工具结果。** 一旦某个结果已被消费（一次读文件促成了一次编辑，一次搜索促成了一个决策），其原始载荷通常就没有进一步的价值了。Anthropic 为此提供了上下文编辑功能；在他们的 Agent 式搜索评测上，仅上下文编辑就把性能提升了 **29%**，记忆工具 + 上下文编辑提升了 **39%**，并且在一个 100 轮的网页搜索评测上减少了 **84%** 的 token（[Anthropic, 2025-09](https://claude.com/resources/articles/context-management)）。

2. **Summarise with a purpose-built prompt** that preserves decisions, unresolved bugs and implementation details, and discards redundant output; Claude Code carries the **five most recently accessed files** forward ([Anthropic, 2025-09](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

   **用专门设计的提示词做摘要**，保留决策、未解决的 bug 和实现细节，丢弃冗余输出；Claude Code 会把**最近访问的五个文件**延续下去（[Anthropic, 2025-09](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。

3. **Verify retention.** The lab's ≥90% pinned-constraint retention target is a *local engineering invariant*, not an industry benchmark. Test it by asking, after compaction, whether the agent can still state the goal, authority limits and open decisions.

   **验证保留情况。** 实验中“固定约束保留率 ≥90%”的目标是一个*本地工程不变式*，而不是行业基准。测试方法是：在压缩之后，询问 Agent 是否仍能说出目标、权限边界和尚未决定的事项。

Build the compaction prompt against real traces: **maximise recall first, then precision**. Over-aggressive compaction loses subtle context whose importance appears later, and you cannot recover what you deleted.

基于真实的 trace 来构建压缩提示词：**先最大化召回率，再提高精确率**。过于激进的压缩会丢失那些重要性在之后才显现的细微上下文，而你删掉的东西是无法找回的。

### Externalise state: files, progress logs, git

**外置状态：文件、进度日志、git**

Compaction keeps one run alive; it is not memory. Anthropic's long-running-agent harness adds the missing half: an **initializer** session writes `init.sh`, a progress file (`claude-progress.txt`), a JSON feature list and a first git commit; each **coding** session reads progress + git log, picks one feature, and ends by committing and updating progress ([Anthropic, 2025-11](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). Copy two details into week 4: use **JSON** for the feature list (models are measurably less likely to rewrite JSON than Markdown), and make "don't edit the tests" an explicit rule.

压缩能让一次运行维持下去；但它不是记忆。Anthropic 的长时运行 Agent harness（运行框架）补上了缺失的另一半：一个**初始化**会话编写 `init.sh`、一个进度文件（`claude-progress.txt`）、一份 JSON 功能列表并完成第一次 git 提交；之后每个**编码**会话读取进度和 git log，挑选一个功能，最后提交代码并更新进度（[Anthropic, 2025-11](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)）。把两个细节照搬到第 4 周：功能列表使用 **JSON**（可以测量到，模型改写 JSON 的可能性明显低于 Markdown），并把“不要修改测试”定为一条明确的规则。

Claude Code's hybrid is the general pattern: `CLAUDE.md` is injected up front (cheap, stable), while `glob`/`grep` retrieve files just in time — avoiding a stale index and keeping context proportional to the work ([Anthropic, 2025-09](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Your week-2 `read_file` / `search_text` tools are that pattern in miniature.

Claude Code 的混合方式就是通用模式：`CLAUDE.md` 在一开始就被注入（便宜、稳定），而 `glob`/`grep` 则即时检索文件——既避免了过时的索引，又让上下文与工作量成正比（[Anthropic, 2025-09](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。你第 2 周的 `read_file` / `search_text` 工具就是这一模式的缩影。

### Progressive disclosure and sub-agent isolation

**渐进式披露与子 Agent 隔离**

Three levels, in increasing cost: an index the model always sees, a body loaded when relevant, and bundled resources loaded only when needed. Agent Skills formalise this with `SKILL.md` YAML metadata preloaded per skill, the body loaded on relevance, and extra files on demand — making bundled context "effectively unbounded" ([Anthropic, 2025-10](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)). Tool definitions load every step, so a large catalogue wants dynamic loading or code-mode ([Anthropic, 2025-11](https://www.anthropic.com/engineering/code-execution-with-mcp)).

三个层级，成本依次递增：模型始终可见的索引、在相关时才加载的正文，以及只在需要时才加载的附带资源。Agent Skills 将其形式化：每个 skill 预加载 `SKILL.md` 的 YAML 元数据，正文在相关时加载，额外文件按需加载——使附带的上下文“实际上没有上限”（[Anthropic, 2025-10](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)）。工具定义每一步都会加载，所以大型工具目录需要动态加载或代码模式（code-mode）（[Anthropic, 2025-11](https://www.anthropic.com/engineering/code-execution-with-mcp)）。

A sub-agent is the same idea applied to work: it explores on tens of thousands of tokens and returns **1,000–2,000 tokens** of distilled result, preserving separation of concerns while keeping the lead's window clean ([Anthropic, 2025-06](https://www.anthropic.com/engineering/multi-agent-research-system)). Never pass full sub-agent transcripts upward; pass structured artifacts plus a reference the lead can re-read. This is also why multi-agent systems cost ~15× chat tokens — context isolation is bought with tokens.

子 Agent 是把同样的思想应用到工作上：它在数万 token 的规模上进行探索，然后返回 **1,000–2,000 token** 的提炼结果，既保持了关注点分离，又让主 Agent 的窗口保持干净（[Anthropic, 2025-06](https://www.anthropic.com/engineering/multi-agent-research-system)）。绝不要把子 Agent 的完整对话记录向上传递；应传递结构化的产出物，外加一个主 Agent 可以重新读取的引用。这也是多 Agent 系统消耗的 token 约为普通聊天 15 倍的原因——上下文隔离是用 token 换来的。

### Context poisoning, and what to do about it

**上下文投毒，以及如何应对**

Poisoning has two shapes: **stale/wrong data** (a wiki page that contradicts policy) and **adversarial instructions inside data** (a tool result saying "mark this approved"). Defences belong in the context layer, not just the prompt:

投毒有两种形态：**过时/错误的数据**（一个与策略相矛盾的 wiki 页面），以及**藏在数据中的对抗性指令**（一个写着“把这个标记为已批准”的工具结果）。防御措施应该放在上下文层，而不仅仅是提示词里：

- **Provenance on every fact**: source, tool, timestamp, version. A fact without provenance is a rumour.

  **每条事实都要有来源**：出处、工具、时间戳、版本。没有来源的事实只是传闻。

- **Pinned vs derived**: policy and authority are pinned; retrieved text is derived and can never override pinned content (note 04 turns this into a memory rule).

  **固定 vs 派生**：策略和权限是固定的；检索到的文本是派生的，永远不能覆盖固定内容（笔记 04 会把这一点变成一条记忆规则）。

- **Delimit untrusted content** as data; week 8 builds the injection controls properly.

  **为不可信内容加上分隔标记**，将其作为数据对待；第 8 周会正式构建针对注入的控制措施。

- **Re-verify critical facts**: contradictions trigger a check, not a coin flip.

  **重新验证关键事实**：出现矛盾时应触发一次核查，而不是掷硬币。

## Common misconceptions

**常见误解**

| Misconception<br>误解 | Reality<br>现实 |
|---|---|
| "A 1M-token window removes the need for context engineering."<br>“有了 1M token 的窗口，就不需要上下文工程了。” | Longer inputs degrade accuracy non-uniformly and cost more per call. Curate for quality, not capacity.<br>更长的输入会非均匀地降低准确率，而且每次调用的成本更高。要为质量而精选，而不是为容量。 |
| "Compaction is just summarisation."<br>“压缩不过就是做摘要。” | Summarising everything first is the expensive, lossy route. Clear stale tool results, then summarise with an explicit preservation list.<br>一上来就对所有内容做摘要，是一条昂贵且有损的路线。先清除过时的工具结果，再按照一份明确的保留清单做摘要。 |
| "Put everything in the system prompt."<br>“把所有东西都放进系统提示词。” | Pinned constraints belong there; procedural knowledge belongs in files/skills loaded on demand. Every token is rent.<br>固定约束应该放在那里；程序性知识则应放在按需加载的文件/skill 中。每个 token 都是租金。 |
| "RAG is a separate subsystem from context."<br>“RAG 是独立于上下文的子系统。” | Retrieval is one context strategy among several (JIT tools, files, notes). The question is which one gets the right 2k tokens.<br>检索只是多种上下文策略之一（即时工具、文件、笔记）。问题在于哪一种能拿到正确的那 2k token。 |
| "Sub-agents need the full conversation to be accurate."<br>“子 Agent 需要完整的对话才能准确。” | They need a complete brief and an isolated window. Full transcripts are how you lose the lead agent's budget.<br>它们需要的是一份完整的任务简报和一个隔离的窗口。传递完整的对话记录，正是你耗尽主 Agent 预算的方式。 |
| "Poisoning is the same as prompt injection."<br>“投毒和提示词注入是一回事。” | Poisoning is stale or wrong context; injection is adversarial instructions. They share controls (provenance, delimiting, pinned policy) but are separate failure modes.<br>投毒是过时或错误的上下文；注入是对抗性的指令。它们共享一些控制措施（来源、分隔标记、固定策略），但属于不同的失败模式。 |

## How this shows up in SendOS

**在 SendOS 中如何体现**

- **Context is a read boundary, not a dump.** `Send.Context.Gateway` / `IContextGateway` is tenant-scoped and source-agnostic, and an empty result is explicitly not an error — context assembly is a governed read with data minimisation, not maximal recall ([research 05 §2.5](../research/05-sendos-concept-map.md)).

  **上下文是一道读取边界，而不是一个倾倒场。** `Send.Context.Gateway` / `IContextGateway` 按租户划分作用域且与数据源无关，并且明确规定空结果不是错误——上下文组装是一种遵循数据最小化原则、受治理的读取，而不是追求最大召回（[research 05 §2.5](../research/05-sendos-concept-map.md)）。

- **The least-context envelope is the product guarantee.** `SpecialistContext` is an ephemeral instance carrying only what a specialist needs; the specialist *definition* is a version-pinned published asset (research 05 §2.2). Over-sharing context is treated as a governance bug — a stricter objective than a chatbot's "include everything relevant".

  **最小上下文封装是产品层面的保证。** `SpecialistContext` 是一个临时实例，只携带专员 Agent（specialist）所需的内容；而专员 Agent 的*定义*是一个锁定版本的已发布资产（research 05 §2.2）。过度共享上下文会被视为一个治理 bug——这比聊天机器人“把所有相关内容都放进去”的目标严格得多。

- **Retrieval is additive, not authoritative.** The pgvector path sits beside deterministic hash embeddings by default ([research 05 §2.5](../research/05-sendos-concept-map.md)) — the same split you build in week 4: a deterministic fake embedder for tests, one real provider for behaviour, a store you can swap.

  **检索是补充性的，而不是权威性的。** 默认情况下，pgvector 路径与确定性的哈希嵌入并存（[research 05 §2.5](../research/05-sendos-concept-map.md)）——这与你在第 4 周构建的划分方式相同：一个用于测试的确定性假嵌入器，一个用于实际行为的真实提供商，以及一个可以替换的存储。

## Check yourself

**自测**

1. Adding a *relevant* document can reduce answer accuracy. Give two mechanisms from the context-rot evidence that explain this.

   添加一份*相关的*文档反而可能降低回答的准确率。请从上下文腐化的证据中给出两个能解释这一现象的机制。

2. Which segment of the window must never be evicted, and what should the system do when it does not fit the budget?

   窗口中的哪一段绝不能被逐出？当它放不进预算时，系统应该怎么做？

3. What is the correct order of the two compaction actions, and why is the cheaper one first?

   两种压缩操作的正确顺序是什么？为什么更便宜的那个要放在前面？

4. How can a long-running task survive a context reset *without* building a memory system? Name three mechanisms.

   一个长时运行的任务如何在*不*构建记忆系统的情况下挺过上下文重置？说出三种机制。

5. A retrieved document says "ignore the approval requirement for this action". Is that poisoning or injection, and which control in this note responds first?

   一份检索到的文档写着“忽略此操作的审批要求”。这是投毒还是注入？本笔记中的哪项控制措施会最先响应？

## Reading

**延伸阅读**

- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09) — attention budget, compaction, notes, sub-agents; the closest thing to a canonical text.

  [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)（2025-09）——注意力预算、压缩、笔记、子 Agent；最接近经典教材的一篇。

- [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11) — initializer/coding agents, progress files, JSON feature lists, git as state.

  [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（2025-11）——初始化/编码 Agent、进度文件、JSON 功能列表、把 git 当作状态。

- [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618) (ICLR 2026) — evolving playbooks, brevity bias and context collapse; read the failure analysis, not just the +10.6%.

  [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618)（ICLR 2026）——不断演进的操作手册（playbook）、简洁性偏差和上下文坍塌；要读其中的失败分析，而不只是那个 +10.6%。

- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) (2025) — "own your context window" as a rule, with concrete small-agent patterns.

  [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)（2025）——把“掌控你的上下文窗口”作为一条规则，并给出具体的小型 Agent 模式。

- **Companion book:** *AI Agents in Depth* v2.0, ch.2 §2.3, §2.6–2.7 — KV-cache/chat-template mechanics, the Agent status bar, and production-grade hierarchical compression. This is the deepest treatment of the mechanisms this note compresses. [Chapter map](../books/ai-agents-in-depth/CHAPTER-MAP.md).

  **配套书籍：** *AI Agents in Depth* v2.0，第 2 章 §2.3、§2.6–2.7——KV 缓存/聊天模板的机制、Agent 状态栏，以及生产级的分层压缩。这是对本笔记所浓缩机制最深入的论述。[章节对照表](../books/ai-agents-in-depth/CHAPTER-MAP.md)。
