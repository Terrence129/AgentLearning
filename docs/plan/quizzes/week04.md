# Week 4 Quiz — Context Engineering and Memory

**第 4 周测验 — 上下文工程与记忆**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** "Context rot" means:

「上下文腐化（context rot）」指的是：

- A) Old messages are deleted by the provider

  旧消息被模型提供商（provider）删除

- B) Recall/accuracy degrades as context length grows, even within the advertised window

  随着上下文长度增长，召回率 / 准确率会下降，即使仍在宣称的窗口范围之内

- C) Cached prompts expire

  缓存的提示词过期

- D) The model forgets its system prompt after 10 turns

  模型在 10 轮之后会忘记它的系统提示词

**Q2.** What is the correct ordering of context priority classes (highest first)?

上下文优先级类别的正确排序是什么（从高到低）？

- A) Recent turns > observations > task state > pinned constraints

  最近的轮次 > 观察结果 > 任务状态 > 固定约束

- B) Pinned constraints > task state > recent turns > observations > history

  固定约束 > 任务状态 > 最近的轮次 > 观察结果 > 历史

- C) Observations > history > task state > pinned constraints

  观察结果 > 历史 > 任务状态 > 固定约束

- D) All classes are equal; drop the oldest

  所有类别同等重要；丢弃最旧的即可

**Q3.** Compaction is best described as:

压缩（compaction）最恰当的描述是：

- A) Deleting the system prompt to save tokens

  删除系统提示词以节省 token

- B) Summarising old turns into a bounded carry-forward note and continuing from it

  把旧的轮次总结成一份有长度上限的延续笔记（carry-forward note），并从它继续

- C) Increasing the context window via a bigger model

  通过更大的模型来扩大上下文窗口

- D) Moving messages to a vector database

  把消息转移到向量数据库

**Q4.** Which memory type stores "customer X is on plan Y, verified on 2026-08-01"?

哪种记忆类型存储「客户 X 使用的是方案 Y，于 2026-08-01 验证」？

- A) Working memory

  工作记忆

- B) Episodic memory

  情景记忆

- C) Semantic memory with provenance

  带来源（provenance）的语义记忆

- D) Prompt cache

  提示词缓存

**Q5.** For a code repository, which retrieval strategy is often better than embeddings?

对于代码仓库，哪种检索策略通常优于 embedding？

- A) Larger context windows

  更大的上下文窗口

- B) Agentic search with `grep`/`glob`/file trees

  使用 `grep` / `glob` / 文件树的 Agent 式搜索

- C) Fine-tuning on the repo

  在仓库上进行微调

- D) Compaction

  压缩

**Q6.** What is a "retention test"?

什么是「保留测试（retention test）」？

- A) A test that the vector store persists across restarts

  测试向量存储在重启后是否依然保留

- B) A test asserting that pinned constraints survive compaction at a target rate

  断言固定约束能以目标比例在压缩后保留下来的测试

- C) A test that the model retains its API key

  测试模型是否保留了它的 API key

- D) A latency benchmark for retrieval

  检索的延迟基准测试

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** Design the retention test for the week-4 lab: what do you pin, what do you measure, and what threshold do you assert?

为第 4 周的实验（lab）设计保留测试：你要固定什么、度量什么，以及断言什么阈值？

**Q8.** Give one case where adding memory makes the system **worse**, and explain the mechanism.

举出一个加入记忆反而让系统**变差**的例子，并解释其机制。

**Q9.** Why do sub-agents help with context limits even though each sub-agent may read far more tokens than the lead agent?

为什么子 Agent 能帮助缓解上下文限制，尽管每个子 Agent 读取的 token 可能远多于主 Agent？

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This compactor runs when the token estimate exceeds the budget. Identify **three** defects.

下面这个压缩器会在 token 估算超出预算时运行。找出**三个**缺陷。

```python
def compact(messages, budget):
    if estimate_tokens(messages) > budget:
        summary = provider.complete(
            [{"role": "user", "content": "Summarize this conversation: " + str(messages)}]
        ).content
        return [{"role": "system", "content": summary}]
    return messages
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Attention degrades before the hard limit is reached — the "attention budget" is finite. Bigger windows reduce but do not remove the effect.

注意力在触及硬性上限之前就会退化——「注意力预算」是有限的。更大的窗口能减轻但无法消除这种效应。

**Q2 — B.** Pinned constraints (safety, task definition, approvals) outrank everything; task state next; recent turns and observations are cheap to regenerate. Dropping the oldest is a heuristic, not a policy.

固定约束（安全、任务定义、审批）的优先级高于一切；其次是任务状态；最近的轮次和观察结果重新生成的代价很低。丢弃最旧的只是一种启发式做法，而不是策略。

**Q3 — B.** Compaction distils the window into a bounded note that preserves decisions, open problems and constraints, then restarts from it. It is lossy by design and must be tested.

压缩把窗口内容提炼成一份有长度上限的笔记，保留决策、未解决的问题和约束，然后从它重新开始。它在设计上就是有损的，因此必须经过测试。

**Q4 — C.** Facts with provenance are semantic memory; "what happened in run 12" is episodic; the scratchpad is working memory.

带来源的事实属于语义记忆；「第 12 次运行中发生了什么」属于情景记忆；草稿区（scratchpad）属于工作记忆。

**Q5 — B.** Files are structured knowledge; path names, directories and `grep` give fresh, cheap, explainable retrieval without index staleness.

文件本身就是结构化的知识；路径名、目录和 `grep` 能提供新鲜、廉价且可解释的检索，而不存在索引过时的问题。

**Q6 — B.** It converts "seems to remember" into a measured guarantee — the lab requires ≥ 90% of pinned constraints surviving.

它把「似乎记得」变成一个可度量的保证——该实验要求 ≥ 90% 的固定约束得以保留。

**Q7 — model answer.** Pin a set of constraints (e.g. "write actions require approval", "budget is $0.20", "output is a Decision union") and a task-state tuple (current goal, open subgoal, key ids). Run the long task through at least one compaction, then assert that every pinned item is still present (verbatim or semantically) in the post-compaction context, and that the task still completes. Threshold: ≥ 90% of pinned items retained, and 100% of safety-critical constraints.

**参考答案。** 固定一组约束（例如「写操作需要审批」「预算为 $0.20」「输出是一个 Decision 联合类型」）以及一个任务状态元组（当前目标、未完成的子目标、关键 id）。让这个长任务至少经历一次压缩，然后断言每一个固定项在压缩后的上下文中依然存在（逐字或语义上），并且任务仍能完成。阈值：≥ 90% 的固定项得以保留，且安全关键约束 100% 保留。

**Q8 — model answer.** Long-lived memory of stale facts: a remembered preference or price from months ago is retrieved with high similarity and overrides fresher evidence, so the agent acts on outdated information. The mechanism is retrieval confidence without freshness/provenance weighting. Also: memory that leaks across tenants is a security failure, not a quality one.

**参考答案。** 长期保存的过时事实：几个月前记下的某个偏好或价格以很高的相似度被检索出来，压过了更新的证据，于是 Agent 基于过时的信息行事。其机制在于：检索置信度没有按新鲜度 / 来源进行加权。另外：跨租户泄露的记忆是安全故障，而不是质量问题。

**Q9 — model answer.** The lead agent's window stays small: sub-agents absorb the large exploratory reads and return condensed artifacts (often 1–2k tokens). Total tokens consumed may rise, but the lead's context stays clean and its attention budget is spent on synthesis rather than on raw data.

**参考答案。** 主 Agent 的窗口能保持精简：子 Agent 承担了大量探索性的读取，并返回浓缩后的产物（通常为 1–2k token）。消耗的总 token 数可能会上升，但主 Agent 的上下文保持干净，它的注意力预算被用在综合归纳上，而不是原始数据上。

**Q10 — model answer.** (1) It drops the system prompt and all pinned constraints/approval state — the run loses its safety and task definition. (2) It serialises the whole conversation with `str(messages)` (huge, and usually non-JSON-safe) instead of a structured, bounded summary of what matters. (3) There is no bounded output, no retention check, and no trigger for pruning stale tool outputs; also no cost accounting for the compaction call itself. A correct version preserves pinned items explicitly, summarises with a structured prompt, bounds the summary length, and asserts retention.

**参考答案。** (1) 它丢掉了系统提示词以及所有固定约束 / 审批状态——这次运行失去了安全保障和任务定义。(2) 它用 `str(messages)` 序列化整个对话（体量巨大，而且通常不是 JSON 安全的），而不是对关键内容做结构化、有长度上限的总结。(3) 没有限制输出长度，没有保留检查，也没有清理过时工具输出的触发机制；而且压缩调用本身也没有计入成本。正确的版本会显式保留固定项，使用结构化的提示词进行总结，限制总结的长度，并断言保留率。
