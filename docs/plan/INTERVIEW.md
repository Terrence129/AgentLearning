# Interview Preparation

**面试准备**

**Use:** answer each question **aloud in 60–90 seconds**, from memory, before reading the model answer. Then compare in one sentence: "what did I miss?" That gap is your flashcard. Re-test the missed ones at day 1, day 3, day 7 (spaced repetition — see [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)).

**用法：** 在阅读参考答案之前，凭记忆**用 60–90 秒大声回答**每道题。然后用一句话对比：「我漏了什么？」这个差距就是你的闪卡。对答错的题在第 1 天、第 3 天、第 7 天重新测试（间隔重复——参见 [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)）。

**Scope:** the 30 questions below cover what an AI/agent-engineer loop actually asks: loop mechanics, context, evals, security, multi-agent trade-offs, MCP and governance. Each maps to a week, so your lab is your evidence.

**范围：** 下面的 30 道题覆盖了 AI/Agent 工程师面试轮次中真正会问的内容：循环机制、上下文、评测（eval）、安全、多 Agent 的权衡、MCP 与治理。每道题都对应某一周，所以你的实验（lab）就是你的证据。

**Rule:** never answer from vocabulary. Every answer should name a mechanism and one failure mode it prevents. Where possible, add "in my capstone, …" with a number.

**规则：** 永远不要靠堆砌术语来回答。每个答案都应点出一个机制，以及它所防止的一种失败模式。只要可能，就补一句「在我的结业项目（capstone）中，……」并给出一个数字。

---

## Part 1 — 30 questions with model answers

**第 1 部分 — 30 道题及参考答案**

### A. Model & provider layer (Week 1)

**A. 模型与模型提供商（provider）层（第 1 周）**

**1. A request fails with `finish_reason: "length"`. What do you do?**
Model answer: that is an output-cap stop, not a context overflow. The loop inspects `finish_reason` and decides: raise `max_tokens`, ask for a shorter format, or split the task. In the adapter, this is a typed outcome so callers never treat truncation as success. *Failure mode prevented:* parsing half an answer as if it were complete.

**1. 一个请求以 `finish_reason: "length"` 结束。你怎么处理？**
参考答案：这是触及输出上限而停止，不是上下文溢出。循环会检查 `finish_reason` 并做出决定：调高 `max_tokens`、要求更简短的格式，或者拆分任务。在适配器中，这是一个带类型的结果，这样调用方永远不会把截断当成成功。*防止的失败模式：* 把半个答案当作完整答案来解析。

**2. How do you design retries for model calls?**
Model answer: classify first — 429/5xx/transport are retryable; 400/auth/policy are terminal. Then exponential backoff with jitter, honour `Retry-After`, cap attempts and total time, and count retries in the cost/trace record. Retries live in the adapter because the signals are provider-specific. *Failure mode prevented:* retry storms and burning budget on a malformed request.

**2. 你如何为模型调用设计重试？**
参考答案：先分类——429/5xx/传输层错误可以重试；400/鉴权/策略错误是终止性的。然后使用带抖动（jitter）的指数退避，遵守 `Retry-After`，限制尝试次数和总时长，并在成本/trace 记录中统计重试次数。重试放在适配器里，因为这些信号是各提供商特有的。*防止的失败模式：* 重试风暴，以及在格式错误的请求上白白烧掉预算。

**3. Why is streaming a protocol rather than a feature?**
Model answer: SSE frames can be fragmented, tool-call arguments arrive in deltas, and failures can occur mid-stream. This forces delta assembly keyed by tool-call id, usage accounting from the final frame, cancellation and timeout handling. Streaming also determines perceived latency (TTFT). *Failure mode prevented:* executing partial JSON from a half-received tool call.

**3. 为什么说流式输出是一种协议，而不是一个功能？**
参考答案：SSE 帧可能被分片，工具调用的参数以增量（delta）形式到达，而且失败可能发生在流的中途。这就要求按工具调用 id 组装增量、从最后一帧统计用量，并处理取消和超时。流式输出还决定了用户感知到的延迟（TTFT）。*防止的失败模式：* 执行一个只收到一半的工具调用中的残缺 JSON。

**4. How does prompt caching change prompt design?**
Model answer: only an identical prefix is cached, so stable content (system prompt, tool definitions, policy) goes first and volatile content (timestamps, user input, tool results) last. A timestamp in the system prompt destroys every cache hit. *Failure mode prevented:* paying full price and latency on every turn because a prefix changed.

**4. 提示词缓存如何改变提示词设计？**
参考答案：只有完全相同的前缀才会被缓存，所以稳定的内容（系统提示词、工具定义、策略）放在前面，易变的内容（时间戳、用户输入、工具结果）放在最后。系统提示词里的一个时间戳就会毁掉所有缓存命中。*防止的失败模式：* 因为前缀变了，每一轮都付全价、承受全额延迟。

### B. Loop & tools (Week 2)

**B. 循环与工具（第 2 周）**

**5. Native tool calling or text-parsed ReAct?**
Model answer: native tool calling by default — structured calls with ids remove brittle parsing and let the provider enforce argument shape. Text ReAct remains useful for models/providers without native support, or when you want explicit reasoning text. In my lab I built the loop so the two share one executor. *Failure mode prevented:* regex-parsing tool calls and mis-pairing results.

**5. 原生工具调用，还是基于文本解析的 ReAct？**
参考答案：默认使用原生工具调用——带 id 的结构化调用免去了脆弱的解析，并让提供商来约束参数形态。对于不支持原生工具调用的模型/提供商，或者当你想要显式的推理文本时，文本 ReAct 仍然有用。在我的实验中，我把循环设计成两者共用同一个执行器。*防止的失败模式：* 用正则解析工具调用，以及把结果配对错。

**6. What are the termination conditions of your loop?**
Model answer: four — final answer with no pending tool calls; `max_steps` reached; budget exhausted; no progress detected. Each produces a typed stop reason, and the max-steps case returns partial results instead of throwing away work. *Failure mode prevented:* infinite loops and silent overspend.

**6. 你的循环有哪些终止条件？**
参考答案：四个——给出最终答案且没有待处理的工具调用；达到 `max_steps`；预算耗尽；检测到没有进展。每一种都会产生一个带类型的停止原因，而达到最大步数的情况会返回部分结果，而不是丢弃已完成的工作。*防止的失败模式：* 无限循环和悄无声息的超支。

**7. How do tool errors reach the model?**
Model answer: as observations. The executor catches tool exceptions, formats them (type, message, hint), truncates, and returns them as the tool result so the model can retry or choose another tool. Only infrastructure failures that make the loop unable to continue abort. *Failure mode prevented:* one bad path crashing an otherwise recoverable run.

**7. 工具错误如何传达给模型？**
参考答案：作为观察结果。执行器捕获工具异常，对其格式化（类型、消息、提示）、截断，并作为工具结果返回，这样模型可以重试或选择另一个工具。只有导致循环无法继续的基础设施故障才会中止运行。*防止的失败模式：* 一条错误路径让一次本可恢复的运行崩溃。

**8. When do you build a workflow instead of an agent?**
Model answer: when the control flow is knowable in advance. Workflows are cheaper, deterministic and easier to eval and audit; agents are for open-ended tasks where the number and nature of steps depend on tool feedback. The rule is "least autonomy that passes the eval". *Failure mode prevented:* using a stochastic planner for a five-step deterministic process.

**8. 什么时候构建工作流而不是 Agent？**
参考答案：当控制流可以事先确定时。工作流更便宜、具有确定性，也更容易评测和审计；Agent 适用于开放式任务，其步骤的数量和性质取决于工具反馈。原则是「能通过评测的最小自主度」。*防止的失败模式：* 用一个随机性的规划器去处理一个五步的确定性流程。

### C. Structured output (Week 3)

**C. 结构化输出（第 3 周）**

**9. JSON mode vs structured outputs vs constrained decoding?**
Model answer: JSON mode guarantees parseable JSON only; provider structured outputs enforce a schema; constrained decoding makes invalid tokens impossible. Each step buys a stronger guarantee at the cost of portability and schema features. I always validate locally regardless, because "valid" must mean "valid against my contract". *Failure mode prevented:* acting on missing or wrong-typed fields.

**9. JSON 模式、结构化输出与约束解码有何区别？**
参考答案：JSON 模式只保证输出是可解析的 JSON；提供商的结构化输出会强制遵循某个 schema；约束解码则让无效 token 根本不可能出现。每进一步都能换来更强的保证，代价是可移植性和 schema 功能受限。无论如何我都会在本地再做校验，因为「有效」必须意味着「符合我的契约」。*防止的失败模式：* 基于缺失或类型错误的字段采取行动。

**10. How do you handle a schema validation failure?**
Model answer: bounded repair — resend a compact validation error plus the schema, allow one retry, re-validate. If it still fails, return an explicit invalid result: `ExtractionResult(valid=False, value=None, raw=<last raw>, errors=[...])`, and record it in `RepairStats` (failure rate). Schema failures are data, not exceptions; only `ProviderError` propagates. Never coerce or default invalid output into a valid-looking object. *Failure mode prevented:* silent fabrication downstream.

**10. 你如何处理 schema 校验失败？**
参考答案：有界修复——重新发送精简的校验错误和 schema，允许重试一次，再重新校验。如果仍然失败，就返回一个显式的无效结果：`ExtractionResult(valid=False, value=None, raw=<last raw>, errors=[...])`，并记录到 `RepairStats`（失败率）中。schema 失败是数据，不是异常；只有 `ProviderError` 会向上传播。永远不要把无效输出强制转换或用默认值填充成一个看似有效的对象。*防止的失败模式：* 下游悄无声息地出现捏造的数据。

### D. Context & memory (Week 4)

**D. 上下文与记忆（第 4 周）**

**11. What is context engineering, in one mechanism-level sentence?**
Model answer: selecting the smallest high-signal token set for the next call under a fixed attention budget, by curating system prompt, tools, observations and history rather than appending everything. Concretely: priority classes, compaction, just-in-time retrieval and sub-agent isolation. *Failure mode prevented:* context rot — accuracy dropping as the window fills.

**11. 用一句机制层面的话说明：什么是上下文工程？**
参考答案：在固定的注意力预算下，为下一次调用挑选最小的高信号 token 集合——通过精心整理系统提示词、工具、观察结果和历史，而不是把所有东西都追加进去。具体手段包括：优先级分类、压缩（compaction）、即时检索和子 Agent 隔离。*防止的失败模式：* 上下文腐化（context rot）——随着窗口被填满，准确率不断下降。

**12. Describe compaction without hand-waving.**
Model answer: when the estimate crosses the budget, summarise the oldest turns into a bounded carry-forward note that explicitly preserves decisions, open problems, constraints and identifiers; prune stale tool outputs; restart the window with that note plus recent turns. Then run a retention test asserting pinned constraints survive. *Failure mode prevented:* losing the task definition at the moment the task gets long.

**12. 不含糊其辞地描述一下压缩。**
参考答案：当估算值超出预算时，把最早的几轮对话总结成一份有长度上限的延续笔记（carry-forward note），其中明确保留决策、未解决的问题、约束和标识符；剪除过时的工具输出；然后用这份笔记加上最近几轮对话重新开启窗口。接着运行一个保留测试，断言被固定的约束依然存在。*防止的失败模式：* 恰恰在任务变长的时候丢失了任务定义。

**13. How do you decide what to remember?**
Model answer: three memories — working (task scratchpad), episodic (per-run summaries), semantic (durable facts with provenance). Consolidation has an explicit rule (e.g. only verified facts with a source and timestamp). Retrieval weights freshness and provenance; cross-tenant memory is never shared. *Failure mode prevented:* stale memory silently overriding fresh evidence.

**13. 你如何决定该记住什么？**
参考答案：三种记忆——工作记忆（任务草稿区）、情景记忆（每次运行的摘要）、语义记忆（带来源（provenance）的持久事实）。整合有明确的规则（例如只保留带有来源和时间戳的已验证事实）。检索时对新鲜度和来源加权；跨租户的记忆永不共享。*防止的失败模式：* 过时的记忆悄无声息地覆盖了新的证据。

**14. RAG or agentic search?**
Model answer: RAG when the corpus is document-shaped and queries are known; agentic search (`grep`, SQL, file trees) when knowledge is structured and freshness matters. Both are context-selection strategies; the decision is empirical — measure retrieval hit rate and task success. *Failure mode prevented:* building a vector index that is stale on day two.

**14. RAG 还是 Agent 式搜索？**
参考答案：当语料是文档形态且查询已知时用 RAG；当知识是结构化的且新鲜度很重要时用 Agent 式搜索（`grep`、SQL、文件树）。两者都是上下文选择策略；决策应基于实证——度量检索命中率和任务成功率。*防止的失败模式：* 建了一个第二天就过时的向量索引。

### E. MCP & protocols (Week 5)

**E. MCP 与协议（第 5 周）**

**15. Explain MCP's architecture and primitives.**
Model answer: a host runs the app and model; clients connect to servers; servers expose tools (actions), resources (data) and prompts (templates) over JSON-RPC, on stdio or streamable HTTP. Discovery is the value: one integration surface instead of bespoke connectors. *Failure mode prevented:* N×M integration explosion.

**15. 解释 MCP 的架构和原语。**
参考答案：宿主运行应用和模型；客户端连接到服务器；服务器通过 JSON-RPC（基于 stdio 或可流式 HTTP）暴露工具（动作）、资源（数据）和提示词（模板）。其价值在于发现机制：一个统一的集成面，而不是一个个定制的连接器。*防止的失败模式：* N×M 的集成爆炸。

**16. What are the security risks of MCP, and your controls?**
Model answer: tool poisoning (malicious descriptions injecting instructions), rug pulls (semantic changes after review), confused deputy (server acting with user authority), and token leakage. Controls: server trust list, description/schema digest pinning, audience-bound auth, no user-token passthrough, timeouts and error mapping, and treating every description as untrusted input. *Failure mode prevented:* a third-party server silently gaining authority.

**16. MCP 有哪些安全风险？你的控制措施是什么？**
参考答案：工具投毒（恶意描述注入指令）、「抽地毯」（审核通过后语义被改变）、混淆代理（服务器以用户的权限行事），以及 token 泄露。控制措施：服务器信任列表、描述/schema 摘要固定（digest pinning）、绑定受众（audience）的鉴权、不透传用户 token、超时与错误映射，并把每一段描述都当作不可信输入。*防止的失败模式：* 第三方服务器悄无声息地获得权限。

**17. MCP versus plain function calling?**
Model answer: function calling is an in-process request convention between your code and a model provider; MCP is an interoperability protocol across processes and vendors with discovery, auth and transport. Use function calling for local tools, MCP when the tool surface is external or multi-client. *Failure mode prevented:* reinventing a connector per integration.

**17. MCP 与普通的函数调用相比如何？**
参考答案：函数调用是你的代码与模型提供商之间的一种进程内请求约定；MCP 则是一种跨进程、跨厂商的互操作协议，带有发现、鉴权和传输机制。本地工具用函数调用，当工具面是外部的或需要多客户端时用 MCP。*防止的失败模式：* 每做一个集成就重新发明一个连接器。

### F. Orchestration & approval (Week 6)

**F. 编排与审批（第 6 周）**

**18. When does multi-agent actually pay?**
Model answer: when subtasks are genuinely parallelisable, or when a subtask needs an isolated context (deep search, large repo) and returns a distilled artifact; synthesis must be the hard part. Otherwise a single agent with better tools wins on cost, latency and debuggability. *Failure mode prevented:* paying 3× for a topology that only added failure modes.

**18. 多 Agent 什么时候才真正划算？**
参考答案：当子任务确实可以并行，或者当某个子任务需要隔离的上下文（深度搜索、大型仓库）并返回一个提炼后的产物时；综合必须是其中的难点。否则，一个配备更好工具的单 Agent 在成本、延迟和可调试性上都会胜出。*防止的失败模式：* 为一个只增加了失败模式的拓扑付出 3 倍的代价。

**19. How does topology-driven shape selection work?**
Model answer: classify the task's topology (one capability node → direct call; one reasoning node → single specialist; connected nodes → one squad; multiple components → multi-squad) and choose the *smallest sufficient shape*. If the task does not fit a backed shape, report a limitation rather than guessing smaller. *Failure mode prevented:* silent under-powering and over-engineering.

**19. 拓扑驱动的形态选择是如何工作的？**
参考答案：对任务的拓扑进行分类（一个能力节点 → 直接调用；一个推理节点 → 单个专员 Agent（specialist）；相互连接的节点 → 一个小队（squad）；多个组件 → 多小队），并选择*最小的足够形态*。如果任务不符合任何有支撑的形态，就报告这一局限，而不是猜测一个更小的形态。*防止的失败模式：* 悄无声息的能力不足与过度工程。

**20. What must an approval bind to, and why?**
Model answer: actor, tenant, action hash, authority snapshot and expiry. The hash blocks post-approval edits; the snapshot blocks executing under changed authority; actor/tenant block cross-principal reuse; expiry blocks stale approvals. *Failure mode prevented:* an approved "read" becoming a "refund" before execution.

**20. 审批必须绑定到哪些内容？为什么？**
参考答案：执行者、租户、动作哈希、权限快照和过期时间。哈希阻止审批后的篡改；快照阻止在权限已变化的情况下执行；执行者/租户阻止跨主体复用；过期时间阻止过时的审批。*防止的失败模式：* 一个已批准的「读取」在执行前变成了「退款」。

**21. How do you guarantee at-most-once execution?**
Model answer: a compare-and-swap state machine (proposed → approved → executing → executed) plus an idempotency record keyed by the action id, and rejection of replays and expired approvals. Retries return the prior result rather than executing again. *Failure mode prevented:* duplicate side effects under retries or double-resume.

**21. 你如何保证至多执行一次？**
参考答案：一个比较并交换（CAS）状态机（proposed → approved → executing → executed），加上以动作 id 为键的幂等记录，并拒绝重放和已过期的审批。重试会返回先前的结果，而不是再执行一次。*防止的失败模式：* 在重试或重复恢复时产生重复的副作用。

**22. Why is durable suspend/resume hard?**
Model answer: the run must be persisted (session + proposal + state), a callback must resume the *right* run exactly once, and CAS must reject double-resume; all of it must survive process restarts. A demo approval that blocks a thread is not an approval system. *Failure mode prevented:* approvals lost on deploy, or executed twice on retry.

**22. 为什么持久化的挂起/恢复很难？**
参考答案：运行必须被持久化（会话 + 提案 + 状态），回调必须恰好一次地恢复*正确的*那次运行，而 CAS 必须拒绝重复恢复；所有这些都必须在进程重启后依然成立。一个阻塞线程的演示版审批并不是审批系统。*防止的失败模式：* 部署时审批丢失，或在重试时被执行两次。

### G. Evals & observability (Week 7)

**G. 评测与可观测性（第 7 周）**

**23. Design an eval suite for an agent in one answer.**
Model answer: a versioned dataset of 20–50 cases covering happy paths, each failure category, safety constraints and edge inputs; deterministic checks first; a rubric-based judge calibrated to ≥80% agreement with human labels; outcome *and* selected trajectory metrics; pass@1 and pass^k; cost/latency; a baseline in CI that fails on regression. *Failure mode prevented:* "it feels better" shipping.

**23. 用一个回答为 Agent 设计一套评测套件。**
参考答案：一个有版本的数据集，包含 20–50 个用例，覆盖正常路径、每一类失败、安全约束和边界输入；先做确定性检查；一个基于评分标准（rubric）的评审，校准到与人工标注一致率 ≥80%；结果指标*以及*部分轨迹指标；pass@1 和 pass^k；成本/延迟；CI 中设置一个基线，出现回归就失败。*防止的失败模式：* 凭「感觉更好了」就上线。

**24. How do you trust an LLM judge?**
Model answer: you do not, by default. Force structured output from a rubric, measure agreement against 20–30 human labels, check bias (self-preference, verbosity, position), randomise order, and report agreement alongside every judged metric. Below ~80%, the judge is not a measurement. *Failure mode prevented:* optimising against the judge's bias.

**24. 你如何信任一个 LLM 评审？**
参考答案：默认不信任。依据评分标准强制结构化输出，用 20–30 个人工标注来度量一致率，检查偏差（自我偏好、冗长偏好、位置偏差），随机化顺序，并在每个评审得出的指标旁边报告一致率。低于约 80%，这个评审就算不上是一种度量。*防止的失败模式：* 针对评审的偏差去做优化。

**25. Why pass^k?**
Model answer: pass@1 hides unreliability. An agent at 70% per attempt succeeds on five consecutive attempts only ~17% of the time; production users experience the streak, not the average. pass^k turns reliability into a metric and a CI floor. *Failure mode prevented:* shipping a demo-grade agent as production-ready.

**25. 为什么要用 pass^k？**
参考答案：pass@1 掩盖了不可靠性。一个单次成功率为 70% 的 Agent，连续五次都成功的概率只有约 17%；生产环境中的用户体验到的是连续表现，而不是平均值。pass^k 把可靠性变成了一个指标和一条 CI 底线。*防止的失败模式：* 把一个演示级的 Agent 当作可用于生产的版本发布。

### H. Security & governance (Week 8)

**H. 安全与治理（第 8 周）**

**26. How do you defend against indirect prompt injection?**
Model answer: assume it will succeed. Treat fetched content as data (delimited, never instructions), enforce an instruction hierarchy, vet outputs before acting, and make the blast radius small: least privilege, sandbox, no secrets in the sandbox, and no external-communication tool in the same agent as private data (lethal trifecta). *Failure mode prevented:* data exfiltration through a poisoned document.

**26. 你如何防御间接提示词注入？**
参考答案：假设它一定会成功。把获取到的内容当作数据（加分隔符，绝不当作指令），强制执行指令层级，在采取行动前审查输出，并缩小爆炸半径：最小权限、沙箱、沙箱中不放密钥，并且不让同一个 Agent 既接触私有数据又拥有对外通信工具（致命三要素）。*防止的失败模式：* 通过一份被投毒的文档导致数据外泄。

**27. What is effective authority, and how is it computed?**
Model answer: the permission set actually enforced for an action — the intersection over independent grants (user, tenant, role, tool policy, risk level), deny-by-default, with the model unable to widen it. One implementation, consulted everywhere. *Failure mode prevented:* privilege escalation via union bugs or model suggestion.

**27. 什么是有效权限？它是如何计算的？**
参考答案：对某个动作实际强制执行的权限集合——对各项独立授权（用户、租户、角色、工具策略、风险等级）取交集，默认拒绝，且模型无法扩大它。只有一个实现，所有地方都查询它。*防止的失败模式：* 因取并集的 bug 或模型的建议导致权限提升。

**28. What does a sandbox have to enforce for file/shell tools?**
Model answer: resolved-path allowlist (not string prefixes), symlink escape checks, size/time/CPU limits, a process or container boundary, no secrets in the environment, and write tools gated by approval and audit. *Failure mode prevented:* `../` traversal and shell injection escaping the workspace.

**28. 对于文件/shell 工具，沙箱必须强制执行哪些限制？**
参考答案：基于解析后路径的允许列表（而不是字符串前缀）、符号链接逃逸检查、大小/时间/CPU 限制、进程或容器边界、环境中不放密钥，以及写入类工具须经审批和审计把关。*防止的失败模式：* 通过 `../` 路径穿越和 shell 注入逃出工作区。

**29. Audit log versus trace?**
Model answer: a trace is a debugging record (steps, timings, payloads, samplable); an audit log is tamper-evident evidence of consequential actions with before/after state, actor, tenant, correlation id and retention policy. They share ids but have different integrity and access requirements. *Failure mode prevented:* being unable to prove what the system did.

**29. 审计日志与 trace 有何区别？**
参考答案：trace 是调试记录（步骤、耗时、载荷，可采样）；审计日志是对有后果的动作的防篡改证据，包含前后状态、执行者、租户、关联 id 和保留策略。两者共享 id，但对完整性和访问控制的要求不同。*防止的失败模式：* 无法证明系统做过什么。

### I. Architecture (Week 9)

**I. 架构（第 9 周）**

**30. Walk me through one request in your capstone, ingress to audit row.**
Model answer: ingress → auth/tenant/quota → provider adapter with budget check and typed errors → typed decision (schema validated, repaired once if needed) → topology/shape selection → specialist plan with isolated contexts → any write becomes a proposal → approval bound to actor/tenant/action-hash/authority-snapshot/expiry → at-most-once execution with idempotency record → audit append with before/after and correlation id → trace/outcome emitted for evals. Every arrow has a failure mode and a control; I can show the trace for one real request. *Failure mode prevented:* a system you cannot explain under pressure.

**30. 带我走一遍你的结业项目中的一个请求，从入口一直到审计记录行。**
参考答案：入口 → 鉴权/租户/配额 → 带预算检查和类型化错误的提供商适配器 → 类型化决策（经 schema 校验，必要时修复一次）→ 拓扑/形态选择 → 带隔离上下文的专员计划 → 任何写操作都变成一个提案 → 审批绑定到执行者/租户/动作哈希/权限快照/过期时间 → 带幂等记录的至多一次执行 → 追加审计记录，包含前后状态和关联 id → 输出 trace/结果供评测使用。每一个箭头都有一个失败模式和一项控制措施；我可以展示一个真实请求的 trace。*防止的失败模式：* 一个你在压力下解释不清的系统。

---

## Part 2 — Five system-design prompts

**第 2 部分 — 五道系统设计题**

### How the 30-minute design interview is graded

**30 分钟设计面试如何评分**

| Dimension<br>维度 | Fail (1)<br>不通过（1） | Pass (2)<br>通过（2） | Strong (3)<br>优秀（3） |
|---|---|---|---|
| **Requirements**<br>**需求** | Starts designing immediately; no questions<br>立刻开始设计；不提任何问题 | Clarifies users, volume, latency/cost, autonomy level<br>澄清用户、规模、延迟/成本、自主程度 | Also separates must-haves from nice-to-haves and states non-goals<br>还能区分必须项与加分项，并说明非目标 |
| **Architecture**<br>**架构** | One box called "LLM agent"<br>只有一个叫「LLM Agent」的方框 | Clear components, data flow, typed boundaries<br>清晰的组件、数据流和类型化边界 | Names trade-offs per component, chooses smallest sufficient shape, explains what is deterministic<br>为每个组件说明权衡，选择最小的足够形态，解释哪些部分是确定性的 |
| **Failure & security**<br>**失败与安全** | "We'll add guardrails"<br>「我们会加护栏」 | Names injection, authority, budget, retries, human approval<br>点出注入、权限、预算、重试、人工审批 | Threat-models the lethal trifecta, binds approval, isolates credentials, defines fail-open/closed per failure<br>对致命三要素做威胁建模，绑定审批，隔离凭证，针对每种失败定义失败开放/失败关闭 |
| **Evals & ops**<br>**评测与运维** | "We'll test it"<br>「我们会测试的」 | Golden set, judge calibration, regression gate, traces<br>黄金集、评审校准、回归关卡、trace | pass^k, cost/latency budgets, failure taxonomy, rollout/rollback<br>pass^k、成本/延迟预算、失败分类、发布/回滚 |
| **Communication**<br>**沟通** | Jumps between topics; no summary<br>在话题间跳来跳去；没有总结 | Structured, answers follow-ups<br>有条理，能回答追问 | States assumptions explicitly, sums up trade-offs and what they would measure first<br>明确陈述假设，总结权衡以及会首先度量什么 |

**Pass bar:** at least "pass" on all five dimensions and "strong" on two. **Timebox:** 5 min requirements → 10 min architecture → 7 min failure/security → 5 min evals/ops → 3 min summary.

**通过线：** 五个维度全部至少达到「通过」，且其中两个达到「优秀」。**时间分配：** 5 分钟需求 → 10 分钟架构 → 7 分钟失败/安全 → 5 分钟评测/运维 → 3 分钟总结。

### Prompt 1 — Support agent with refund authority

**题目 1 — 拥有退款权限的客服 Agent**

> "Design an agent that triages support tickets and can issue refunds up to $200. It must handle 50k tickets/day, work in 12 languages, and the CFO wants no unauthorised refunds."
>
> 「设计一个 Agent，用于分诊客服工单，并能发放最高 200 美元的退款。它必须每天处理 5 万张工单，支持 12 种语言，而且 CFO 要求不能出现任何未经授权的退款。」

**What a strong answer covers:** workflow-first triage (classification → retrieval → decision), agent only for the ambiguous tail; typed decision family; refund as a capability with risk level; approval binding for above-threshold or low-confidence cases; authority intersection per tenant/agent; idempotency on refund calls; audit row per refund; eval set with a money-loss metric and pass^k; cost routing (cheap model for triage).

**优秀答案应涵盖：** 工作流优先的分诊（分类 → 检索 → 决策），只有模糊的长尾情况才交给 Agent；类型化的决策族；把退款作为带风险等级的能力；对超过阈值或低置信度的情况进行审批绑定；按租户/Agent 求权限交集；退款调用的幂等性；每笔退款一条审计记录；带资金损失指标和 pass^k 的评测集；成本路由（分诊用便宜的模型）。

**Red flags:** letting the model call the refund API directly; no threshold logic; judge-scored only; no audit.

**危险信号：** 让模型直接调用退款 API；没有阈值逻辑；只靠评审打分；没有审计。

### Prompt 2 — Contract extraction at 99% field accuracy

**题目 2 — 字段准确率 99% 的合同抽取**

> "Design a pipeline that extracts 40 fields from 200k contracts with a 99% accuracy target, and tell me how you would know you hit it."
>
> 「设计一条流水线，从 20 万份合同中抽取 40 个字段，目标准确率 99%，并告诉我你怎么知道自己达标了。」

**What a strong answer covers:** deterministic pre-processing; schema-first extraction with strict validation; confidence + field-level repair; human-review queue for low confidence (sampling strategy); stratified eval set by contract type and field; per-field accuracy and calibration; drift monitoring; cost per 1k pages; how to define "accuracy" against a labelled sample and the statistical power needed.

**优秀答案应涵盖：** 确定性的预处理；schema 优先、严格校验的抽取；置信度 + 字段级修复；针对低置信度的人工审核队列（抽样策略）；按合同类型和字段分层的评测集；逐字段的准确率与校准；漂移监控；每 1000 页的成本；如何基于标注样本定义「准确率」，以及所需的统计功效。

**Red flags:** "prompt it well and spot-check"; no confidence handling; no stratification; claiming 99% without a labelled sample.

**危险信号：** 「把提示词写好再抽查一下」；没有置信度处理；没有分层；没有标注样本就宣称达到 99%。

### Prompt 3 — Enterprise learning loop (trace → eval → publish)

**题目 3 — 企业学习闭环（trace → 评测 → 发布）**

> "Design the loop that turns production traces into better agent behaviour, with human control over what ships."
>
> 「设计一个闭环，把生产环境的 trace 转化为更好的 Agent 行为，并由人来控制哪些内容上线。」

**What a strong answer covers:** append-only trace schema with correlation ids; sampling and PII handling; failure mining/taxonomy; candidate generation (prompt/skill/policy changes); evidence gate (eval suite + pass^k + no safety regression) before promotion; human-approved publish with rollback; provenance and versioning of assets; what is automated vs human; how you avoid leaking production data into evaluation.

**优秀答案应涵盖：** 带关联 id 的只追加 trace schema；抽样与 PII 处理；失败挖掘/分类；候选生成（提示词/技能/策略变更）；晋升前的证据关卡（评测套件 + pass^k + 无安全回归）；经人工批准的发布，并可回滚；资产的来源与版本管理；哪些自动化、哪些由人负责；如何避免生产数据泄漏进评测。

**Red flags:** auto-publishing prompt changes; evals from the same traces used to tune; no rollback; no provenance.

**危险信号：** 自动发布提示词变更；评测所用的 trace 与调优所用的是同一批；没有回滚；没有来源追踪。

### Prompt 4 — MCP integration for 12 internal systems

**题目 4 — 为 12 个内部系统做 MCP 集成**

> "Your company has 12 internal systems (CRM, billing, wiki, ticketing, HR, CI…). Design how agents get tool access, safely."
>
> 「你的公司有 12 个内部系统（CRM、计费、wiki、工单、HR、CI……）。设计 Agent 如何安全地获得工具访问权限。」

**What a strong answer covers:** MCP servers per system with least-privilege scopes; host/client architecture; registry of approved servers with owner and risk level; digest pinning and review process; per-user auth via audience-bound tokens (no passthrough); read tools vs write tools with approval; rate limits and timeouts; audit of tool calls; what stays bespoke (governed entitlements, high-risk writes) and why.

**优秀答案应涵盖：** 每个系统一个 MCP 服务器，采用最小权限范围；宿主/客户端架构；已批准服务器的注册表，包含负责人和风险等级；摘要固定与审核流程；通过绑定受众的 token 做按用户鉴权（不透传）；读工具与需审批的写工具区分开；限流与超时；工具调用审计；哪些部分保持定制（受治理的授权、高风险写入）以及原因。

**Red flags:** one shared service token for all systems; exposing every tool to every agent; no approval for writes; no trust registry.

**危险信号：** 所有系统共用一个服务 token；把每个工具都暴露给每个 Agent；写入无需审批；没有信任注册表。

### Prompt 5 — Coding agent for CI failures

**题目 5 — 处理 CI 失败的编码 Agent**

> "Design an agent that takes a failing CI run on a mid-size repo and proposes a fix. It must be safe to run unattended overnight."
>
> 「设计一个 Agent，接收一个中等规模仓库上失败的 CI 运行，并提出修复方案。它必须能安全地在夜间无人值守运行。」

**What a strong answer covers:** context strategy (repo map, failure logs, `grep`/glob, not whole-repo dump); sandbox with no network/secrets, resource caps; plan-and-execute with per-step verification (tests as ground truth); bounded steps/budget; branch + PR output rather than direct push; eval on a held-out set of past CI failures; trajectory eval (did it run tests? respect allowlists?); human review; cost/latency per run.

**优秀答案应涵盖：** 上下文策略（仓库地图、失败日志、`grep`/glob，而不是把整个仓库倒进去）；无网络/无密钥、有资源上限的沙箱；计划-执行模式，每一步都做验证（以测试为基准事实）；有上限的步数/预算；输出分支 + PR，而不是直接推送；在留出的历史 CI 失败集上做评测；轨迹评测（它运行测试了吗？遵守允许列表了吗？）；人工审查；每次运行的成本/延迟。

**Red flags:** direct push to main; network access; no test-based verification; unbounded loops.

**危险信号：** 直接推送到 main；有网络访问；没有基于测试的验证；无上限的循环。

---

**Before an interview:** re-read your capstone ADRs (10 min), re-derive the request path on paper (10 min), and rehearse prompts 1 and 3 aloud (15 min). Those three cover most of what the loop will ask.

**面试之前：** 重读你的结业项目 ADR（10 分钟），在纸上重新推导一遍请求路径（10 分钟），并大声演练题目 1 和题目 3（15 分钟）。这三件事覆盖了面试轮次中会问到的大部分内容。
