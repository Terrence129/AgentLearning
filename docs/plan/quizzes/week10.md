# Week 10 Quiz — Consolidation and Leverage

**第 10 周测验 — 巩固与发挥杠杆**

**Time:** 20 minutes · **Closed book, no notes, no code editor.** Pass mark: 8/10. This quiz is the final "explain" gate before the portfolio and interviews.

**时间：** 20 分钟 · **闭卷，不看笔记，不用代码编辑器。** 及格线：8/10。本测验是进入作品集和面试之前的最后一道「讲解」关卡。

## Part A — Multiple choice (5 questions)

**A 部分 — 选择题（5 道）**

**Q1.** The point of "re-derive from memory" is to:

「凭记忆重新推导」的目的是：

- A) Produce a second implementation to ship

  产出第二份实现用于发布

- B) Test whether you own the mechanism or only recognise it

  检验你是真正掌握了这个机制，还是仅仅认得它

- C) Prove the original code was wrong

  证明原来的代码是错的

- D) Save disk space

  节省磁盘空间

**Q2.** Which is the strongest portfolio evidence for an agent engineer?

对于一名 Agent 工程师来说，哪种作品集证据最有说服力？

- A) A certificate

  一张证书

- B) A traced, evaluated system with a written architecture and measured failures

  一个带有追踪、经过评测的系统，配有成文的架构说明和经过度量的失败

- C) A list of frameworks used

  一份用过的框架清单

- D) A demo video with no code

  一段没有代码的演示视频

**Q3.** `pass^k` differs from `pass@1` because it measures:

`pass^k` 与 `pass@1` 的不同之处在于，它衡量的是：

- A) Latency

  延迟

- B) Reliability across repeated attempts

  多次重复尝试下的可靠性

- C) Token cost

  token 成本

- D) Judge agreement

  评审一致性

**Q4.** Approval must bind to an action hash because:

审批必须绑定到操作哈希，因为：

- A) Hashes are cheap

  哈希的计算成本很低

- B) Otherwise an approved proposal can be swapped or edited before execution

  否则一个已批准的提案可能在执行之前被替换或篡改

- C) It improves caching

  它能提升缓存效果

- D) It satisfies the audit log format

  它符合审计日志的格式要求

**Q5.** Which statement about the MCP spec is correct for 2026?

关于 MCP 规范，以下哪种说法在 2026 年是正确的？

- A) The `initialize` handshake is the only supported mechanism

  `initialize` 握手是唯一受支持的机制

- B) The protocol was redesigned; older tutorials describing the legacy handshake are stale

  协议经过了重新设计；描述旧版握手的老教程已经过时

- C) MCP is deprecated in favour of A2A

  MCP 已被弃用，改用 A2A

- D) Only stdio is supported

  只支持 stdio

## Part B — Short answer (4 questions)

**B 部分 — 简答题（4 道）**

**Q6.** Name the four runtime duties (observation, context, control, state/verification) and give one concrete mechanism you built for each.

说出运行时的四项职责（观察、上下文、控制、状态 / 验证），并为每一项举出一个你亲手构建的具体机制。

**Q7.** In an interview: "Tell me about a failure you found and fixed." Which of your nine weeks gives the best story, and what is the four-part structure of the answer?

面试中被问到：「讲讲你发现并修复过的一次失败。」你这九周中的哪一周能提供最好的故事？回答的四段式结构是什么？

**Q8.** How will you decide the next step after this course: framework fluency, the learning loop, or agentic RL? State the decision rule.

学完本课程之后，你将如何决定下一步：熟练掌握框架、学习循环，还是 Agent 强化学习（agentic RL）？说明你的决策规则。

**Q9.** Explain, in ≤ 60 seconds and without notes, the full request path of an agent run from ingress to audit row.

在 ≤ 60 秒内、不看笔记，讲清楚一次 Agent 运行从入口到审计记录的完整请求路径。

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This "from memory" loop was written during consolidation. Identify **three** defects.

下面这个「凭记忆写出」的循环是在巩固阶段编写的。找出**三个**缺陷。

```python
def run(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]
    while not is_done(messages):
        resp = provider.complete(messages, tools=registry.schemas())
        messages.append(resp.message)
        for call in resp.tool_calls:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": registry.call(call.name, call.arguments),
                }
            )
    return messages[-1]["content"]
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Recognition is not ownership; rebuilding from a blank file exposes every hand-waved detail.

认得不等于掌握；从一个空白文件开始重建，会暴露出每一个被含糊带过的细节。

**Q2 — B.** Traces + evals + written architecture + honest failure analysis is the combination that survives an interview loop.

trace + 评测（eval）+ 成文的架构说明 + 诚实的失败分析，这样的组合才能经受住一整轮面试的考验。

**Q3 — B.** Reliability. An agent that works 70% of the time per attempt is not production-ready; pass^k exposes that.

可靠性。一个每次尝试只有 70% 成功率的 Agent 还不具备上生产的条件；pass^k 会把这一点暴露出来。

**Q4 — B.** The hash is the binding between "what was approved" and "what executes"; without it the approval is a vague permission.

哈希把「被批准的内容」与「被执行的内容」绑定在一起；没有它，审批就只是一种含糊的许可。

**Q5 — B.** The 2026 redesign changed negotiation; the plan tells you to read the changelog before coding.

2026 年的重新设计改变了协商机制；计划要求你在写代码之前先阅读变更日志。

**Q6 — model answer.** Observation: structured step traces (`trace.py` events) with tool results and timings. Context: priority-class window + compaction with a retention test. Control: the ReAct loop with `max_steps` and top-of-iteration budget checks. State/verification: typed decisions with schema validation and the eval harness/regression gate.

**参考答案。** 观察：带有工具结果和计时信息的结构化步骤 trace（`trace.py` 事件）。上下文：按优先级类别管理的窗口 + 带保留测试的压缩（compaction）。控制：带有 `max_steps` 和迭代开头预算检查的 ReAct 循环。状态 / 验证：带 schema 校验的类型化决策，以及评测 harness（运行框架）/ 回归关卡。

**Q7 — model answer.** Week 3 (schema repair) or week 7 (eval regression) gives the best story. Structure: (1) the concrete symptom, with numbers/logs; (2) the diagnosis — which assumption was wrong and how the trace proved it; (3) the fix and the test that locks it; (4) what generalizes — the control you now add by default.

**参考答案。** 第 3 周（schema 修复）或第 7 周（评测回归）能提供最好的故事。结构：(1) 具体的症状，附上数字 / 日志；(2) 诊断——哪个假设是错的，trace 又是如何证明这一点的；(3) 修复，以及锁定这一修复的测试；(4) 可推广的经验——你现在默认会加上的那项控制。

**Q8 — model answer.** If eval/data plumbing is not solid, fix that first — RL on noisy evals optimises noise. If it is solid and your goal is SendOS impact, build the learning loop (trace→candidate→publish). Framework fluency is the cheapest, so do it only when a role or team requires that specific stack. The rule: choose the option that compounds what you already measured.

**参考答案。** 如果评测 / 数据管道还不扎实，先把它修好——在有噪声的评测上做强化学习，优化的只是噪声。如果它已经扎实，而你的目标是对 SendOS 产生影响，那就构建学习循环（trace → 候选 → 发布）。熟练掌握框架的成本最低，所以只在某个岗位或团队要求那套特定技术栈时再去做。规则是：选择能在你已度量成果之上产生复利的那个选项。

**Q9 — model answer.** Request ingress → auth/quota/tenant resolution → model adapter call (budget check, retries) → typed decision (schema validated, repaired if needed) → topology/shape selection → plan executed by specialists with isolated contexts → any write action becomes a proposal → approval check bound to actor, tenant, action hash, authority snapshot, expiry → at-most-once execution with idempotency record → same-path audit append with before/after evidence → trace/outcome event emitted for evals.

**参考答案。** 请求入口 → 鉴权 / 配额 / 租户解析 → 模型适配器调用（预算检查、重试）→ 类型化决策（经 schema 校验，必要时修复）→ 拓扑 / 形态选择 → 由拥有隔离上下文的专员 Agent（specialist）执行计划 → 任何写操作都变成一个提案 → 审批检查，绑定到执行者、租户、操作哈希、权限快照、过期时间 → 借助幂等记录实现至多一次执行 → 在同一路径上追加带前后证据的审计记录 → 发出供评测使用的 trace / 结果事件。

**Q10 — model answer.** (1) `is_done(messages)` is undefined/naive (typically a substring check) — the loop can stop on an intermediate message or never stop; termination must be "final answer with no pending tool calls" plus `max_steps`. (2) No budget check and no `max_steps` guard — runaway cost. (3) Tool exceptions crash the run instead of becoming observations; also `messages[-1]["content"]` may not be the final answer, and tool results are not truncated. Fix: explicit done predicate, step cap, top-of-loop budget check, error-as-observation, bounded outputs.

**参考答案。** (1) `is_done(messages)` 没有定义或过于幼稚（通常只是一个子串检查）——循环可能在一条中间消息上就停下，也可能永远停不下来；终止条件必须是「给出最终答案且没有待处理的工具调用」，再加上 `max_steps`。(2) 没有预算检查，也没有 `max_steps` 防护——成本会失控。(3) 工具异常会让运行崩溃，而不是变成观察结果；另外 `messages[-1]["content"]` 未必是最终答案，工具结果也没有被截断。修复：显式的完成判定、步数上限、循环开头的预算检查、把错误当作观察结果、限制输出大小。
