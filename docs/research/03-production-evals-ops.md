# 03 — Production Evals, Observability, Security & Operations for Agent Platforms

**03 — Agent 平台的生产级评测、可观测性、安全与运维**

*Research note, 2026-10-18. Audience: senior Java/C#/React/AWS engineer building an enterprise .NET agent platform with licensing, multi-tenancy, and audit obligations. Citation convention: `(link, accessed 2026-10-18)` — all links were fetched on that date unless a different date is given. **[established]** = vendor docs/standards/peer-reviewed; **[unsettled]** = thin or moving evidence. Numbers marked "~" are practitioner estimates, not guarantees.*

*研究笔记，2026-10-18。读者对象：正在构建企业级 .NET Agent 平台、并需承担许可（licensing）、多租户和审计义务的资深 Java/C#/React/AWS 工程师。引用约定：`(link, accessed 2026-10-18)`——除非另注日期，所有链接均于该日抓取。**[established]**（已确立）= 厂商文档/标准/同行评审；**[unsettled]**（未确定）= 证据稀少或仍在变化。标注「~」的数字是从业者的估算，不作保证。*

---

## 0. The frame

**0. 总体框架**

The hard part of production agents is not model quality; it is **trustworthy behaviour under uncertainty**. Three properties must be engineered, not prompted: you can prove **what the agent did** (traces/audit), that it **still works** (calibrated evals), and that **when the model is fooled, nothing important breaks**. OWASP's 2026 preface puts it bluntly: "Stop trying to build a model that cannot be fooled. Build the system around it, so that when the model is fooled, and it will be, nothing important breaks." ([OWASP GenAI LLM Top 10 2026 preface](https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md), accessed 2026-10-18)

生产级 Agent 的难点不在于模型质量，而在于**不确定性下的可信行为**。有三项属性必须靠工程来保证，而不是靠提示词：你能证明 **Agent 做了什么**（trace/审计），能证明它**仍然有效**（经过校准的评测（eval）），并且能证明**当模型被骗时，不会有重要的东西坏掉**。OWASP 2026 年版的前言说得很直白：「别再试图构建一个不会被骗的模型了。围绕它构建系统，让模型被骗时——它一定会被骗——不会有任何重要的东西坏掉。」（[OWASP GenAI LLM Top 10 2026 前言](https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md)，访问于 2026-10-18）

For a .NET platform this maps onto familiar disciplines: evals ≈ acceptance tests, traces ≈ distributed tracing, durable execution ≈ workflow engine, tenancy ≈ SaaS control plane. What is genuinely new: **non-determinism**, **untrusted natural language treated as instructions**, and **cost that scales with behaviour, not requests**.

对一个 .NET 平台而言，这些都能对应到熟悉的工程学科：评测 ≈ 验收测试，trace ≈ 分布式追踪，持久化执行 ≈ 工作流引擎，租户 ≈ SaaS 控制平面。真正新的东西是：**非确定性**、**被当作指令对待的不可信自然语言**，以及**随行为而非请求数量增长的成本**。

---

## 1. Evaluation strategy

**1. 评测策略**

### 1.1 Decision tree

**1.1 决策树**

```
Machine-checkable ground truth?
├─ YES (DB state, test pass, exit code, schema, side-effect)
│   → deterministic assertion on state, not text similarity
│   → if multi-step: score trajectory too (tools, args, policy, steps)
│   → gate on pass^k over k trials, not single-run pass@1
└─ NO (open-ended quality)
    ├─ failure cheap/reversible → sampled human preference + light judge
    └─ failure expensive/regulated → rubric + calibrated judge + human adjudication,
       published with judge-vs-human agreement

Multi-turn / long-horizon?
├─ YES → add goal state, policy compliance, step count, $/task,
│         error recovery, human-intervention rate
└─ NO  → final answer + cost/latency usually suffice

Production traffic?
├─ YES → online eval on sampled traces, A/B, drift alerts
└─ NO  → replay a dataset seeded from real requests, not synthetic happy paths
```

Deterministic assertions are the default; LLM judges are an instrument that must itself be calibrated.

确定性断言是默认选择；LLM 评审（LLM-as-judge）是一件本身也必须经过校准的仪器。

### 1.2 pass@k vs pass^k

**1.2 pass@k 与 pass^k**

`pass@k` ("at least one of k succeeds") is a capability metric. `pass^k` ("all k trials succeed") is a reliability metric — and production cares about reliability. τ-bench introduced pass^k and reported strong function-calling agents succeeding on **<50%** of tasks with **pass^8 < 25%** in retail ([τ-bench](https://arxiv.org/abs/2406.12045), accessed 2026-10-18).

`pass@k`（「k 次中至少一次成功」）是能力指标。`pass^k`（「k 次试验全部成功」）是可靠性指标——而生产环境关心的是可靠性。τ-bench 提出了 pass^k，并报告称：在零售场景中，强大的函数调用 Agent 只在 **<50%** 的任务上成功，且 **pass^8 < 25%**（[τ-bench](https://arxiv.org/abs/2406.12045)，访问于 2026-10-18）。

Implications: publish **pass^k (k = 3–8)** for irreversible actions (refunds, provisioning, ticket closure); track **variance across identical trials** — that variance is the real production error rate, and temperature 0 does not remove it at provider scale; budget eval cost as `k × cases × tokens` and use batch + caching to pay for it.

启示：对不可逆操作（退款、资源开通、关闭工单）公布 **pass^k（k = 3–8）**；跟踪**相同试验之间的方差**——这个方差才是真实的生产错误率，而且在模型提供商（provider）的规模下，temperature 0 并不能消除它；按 `k × cases × tokens` 为评测成本做预算，并用批处理 + 缓存来支付这笔开销。

**[established]** pass^k as a reliability metric; **[unsettled]** what k is defensible, and whether k should scale with action consequence.

**[established]** pass^k 作为可靠性指标；**[unsettled]** 多大的 k 才站得住脚，以及 k 是否应随操作后果的严重程度而增大。

### 1.3 What to assert on a trajectory

**1.3 轨迹上应断言什么**

| Dimension<br>维度 | Deterministic check<br>确定性检查 | Why it matters<br>为何重要 |
|---|---|---|
| Tool selection<br>工具选择 | Expected/forbidden tool sets<br>预期/禁用的工具集合 | Detects capability creep<br>发现能力蔓延 |
| Tool arguments<br>工具参数 | JSON schema + business rules + tenant-ID equality<br>JSON schema + 业务规则 + 租户 ID 相等性 | Blocks cross-tenant IDOR at eval time<br>在评测阶段拦截跨租户 IDOR |
| Policy compliance<br>策略合规 | Rule engine over the trace ("no refund > $500 without approval")<br>基于 trace 的规则引擎（「未经审批不得退款超过 $500」） | Turns compliance policy into tests<br>把合规策略变成测试 |
| Efficiency<br>效率 | Steps, tokens, wall-clock, retries<br>步数、token、挂钟时间、重试次数 | Cost regression gate<br>成本回归关卡 |
| Error recovery<br>错误恢复 | Injected tool failure → correct fallback<br>注入工具失败 → 正确回退 | The behaviour that actually breaks in prod<br>生产环境中真正会出问题的行为 |
| Human handoff<br>转交人工 | Escalation fires exactly when it should<br>升级恰好在应当触发时触发 | Protects review capacity and SLA<br>保护审核产能和 SLA |

OTel models `plan` and `execute_tool` as distinct spans — the right unit of eval granularity ([OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18).

OTel 把 `plan` 和 `execute_tool` 建模为不同的 span——这正是评测粒度的合适单位（[OTel GenAI Agent span](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)，访问于 2026-10-18）。

### 1.4 Judge discipline

**1.4 评审纪律**

LLM-as-judge works only as a calibrated instrument. The MT-Bench work documents **position, verbosity, self-enhancement biases and limited reasoning**, while showing strong judges reach >80% human agreement — roughly human-human ([LLM-as-a-Judge](https://arxiv.org/abs/2306.05685), accessed 2026-10-18). Minimum hygiene:

LLM 评审只有作为经过校准的仪器才有效。MT-Bench 相关研究记录了**位置偏差、冗长偏差、自我增强偏差以及有限的推理能力**，同时表明强评审模型与人类的一致率可超过 80%——大致相当于人与人之间的一致率（[LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)，访问于 2026-10-18）。最低限度的卫生要求：

1. Rubric with **atomic criteria** (0–2 each), not one holistic 1–10.

   评分标准（rubric）由**原子化的评分项**组成（每项 0–2 分），而不是一个整体的 1–10 分。

2. **30–50 human-labelled calibration items per rubric**, double-labelled; report agreement/κ; re-calibrate on any judge or prompt change.

   **每个评分标准配 30–50 条人工标注的校准样本**，双人标注；报告一致率/κ；评审模型或提示词一旦有任何变更就重新校准。

3. **Order-swap** pairwise comparisons; randomize length; strip formatting that triggers verbosity bias.

   成对比较时**交换顺序**；随机化长度；去除会引发冗长偏差的格式。

4. **Pin the judge model version**; cache the rubric prefix — a fixed-rubric judge can reach ~70% cache-hit rate ([OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18).

   **固定评审模型的版本**；缓存评分标准前缀——使用固定评分标准的评审可以达到约 70% 的缓存命中率（[OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching)，访问于 2026-10-18）。

5. Never let a model family judge itself in customer-visible quality metrics.

   在面向客户的质量指标中，绝不让某个模型家族评审它自己。

6. Log judge inputs/outputs into the same trace system or you cannot debug score drift.

   把评审的输入/输出记录到同一个 trace 系统中，否则你无法调试分数漂移。

### 1.5 Public benchmarks: what they measure

**1.5 公开基准：它们衡量的是什么**

Use these for **model/vendor selection and coding capability**, never as proof your product works. Build a private set from your own incidents.

把它们用于**模型/厂商选型和编码能力评估**，绝不要把它们当作你的产品可用的证明。用你自己的事故构建一个私有评测集。

| Benchmark<br>基准 | Measures<br>衡量内容 | Caveat<br>注意事项 | Use for<br>用途 |
|---|---|---|---|
| **SWE-bench Verified** | Repo issue → patch, graded by tests; 500 human-confirmed-solvable tasks ([repo](https://github.com/SWE-bench/SWE-bench), accessed 2026-10-18)<br>仓库 issue → 补丁，由测试评分；500 个经人工确认可解的任务（[仓库](https://github.com/SWE-bench/SWE-bench)，访问于 2026-10-18） | Harness/leak sensitivity; Multimodal v2 (480 tasks) open-sourced 2026-09-01<br>对 harness（运行框架）/数据泄漏敏感；Multimodal v2（480 个任务）已于 2026-09-01 开源 | Shortlisting coding agents<br>筛选编码 Agent 候选 |
| **τ-bench** | Tool-agent-user with simulated user; scores final DB state; introduces pass^k ([paper](https://arxiv.org/abs/2406.12045))<br>工具-Agent-用户三方交互，使用模拟用户；为最终数据库状态打分；提出了 pass^k（[论文](https://arxiv.org/abs/2406.12045)） | Simulated user ≠ real user<br>模拟用户 ≠ 真实用户 | Closest public analogue to enterprise tool use<br>最接近企业工具使用场景的公开对照 |
| **GAIA** | 466 real-world questions needing browsing/multimodality/tools; 92% human vs 15% GPT-4+plugins; 300 answers held out ([paper](https://arxiv.org/abs/2311.12983), accessed 2026-10-18)<br>466 个需要浏览/多模态/工具的真实世界问题；人类 92% vs GPT-4+插件 15%；300 个答案未公开（[论文](https://arxiv.org/abs/2311.12983)，访问于 2026-10-18） | Web drift; time-sensitive<br>网页漂移；有时效性 | General assistant competence<br>通用助手能力 |
| **Terminal-Bench 4.0** | End-to-end terminal tasks; leaderboard reports **resolution rate, cost, tokens** ([tbench.ai](https://www.tbench.ai/), accessed 2026-10-18)<br>端到端终端任务；排行榜报告**解决率、成本、token**（[tbench.ai](https://www.tbench.ai/)，访问于 2026-10-18） | New cost dimension<br>新增成本维度 | CLI/devops agents, cost-aware ranking<br>CLI/devops Agent，考虑成本的排名 |
| **WebArena / AgentBench** | Browser environments / multi-environment breadth ([WebArena](https://arxiv.org/abs/2307.13854), [AgentBench](https://arxiv.org/abs/2307.10928))<br>浏览器环境 / 多环境广度（[WebArena](https://arxiv.org/abs/2307.13854)，[AgentBench](https://arxiv.org/abs/2307.10928)） | 2026 leaderboards not re-verified here; orient only<br>本文未重新核实 2026 年排行榜；仅供定位参考 | Historical comparison<br>历史对比 |

**[unsettled]** Leaderboards are contaminated to varying degrees and not comparable across harness versions; a few points of delta is noise.

**[unsettled]** 各排行榜都存在不同程度的数据污染，且不同 harness 版本之间不可比；几个百分点的差距只是噪声。

### 1.6 Online evals and release gates

**1.6 在线评测与发布关卡**

Make both gates concrete and blocking:

让两道关卡都具体且具有阻断性：

- **Offline (blocking):** pass^k drop >2 points, or p95 cost rise >15%, fails the build.

  **离线（阻断）：** pass^k 下降超过 2 个百分点，或 p95 成本上升超过 15%，即判定构建失败。

- **Online (canary 1–5%):** compare task-success proxy, escalation rate, thumbs-down, judge score, refusal rate; auto-rollback on threshold breach.

  **在线（1–5% 金丝雀）：** 比较任务成功代理指标、升级率、差评（thumbs-down）、评审分数、拒答率；超过阈值时自动回滚。

- **Golden traces as fixtures:** sanitized production traces replayed on every prompt/model change — the highest-ROI eval investment.

  **把黄金 trace 当作测试夹具（fixture）：** 每次提示词/模型变更时，回放脱敏后的生产 trace——这是投资回报率最高的评测投入。

- **Incident → test:** every customer-visible failure becomes a regression case within one sprint.

  **事故 → 测试：** 每个客户可见的失败都要在一个迭代（sprint）内变成一个回归用例。

LangSmith, Langfuse, Braintrust and Phoenix all cover datasets + experiments + online scoring, so selection is mostly deployment model and ergonomics. Braintrust documents instrument → observe → annotate → evaluate → deploy with online scoring ([Braintrust evaluate](https://www.braintrust.dev/docs/evaluate/index), accessed 2026-10-18); Langfuse documents online evaluation of production traces, datasets, and LLM-judge/code/human evaluators ([Langfuse](https://langfuse.com/docs), accessed 2026-10-18).

LangSmith、Langfuse、Braintrust 和 Phoenix 都覆盖了数据集 + 实验 + 在线评分，因此选型主要取决于部署模式和易用性。Braintrust 的文档描述了「插桩 → 观测 → 标注 → 评测 → 部署」的流程，并支持在线评分（[Braintrust evaluate](https://www.braintrust.dev/docs/evaluate/index)，访问于 2026-10-18）；Langfuse 的文档描述了对生产 trace 的在线评测、数据集，以及 LLM 评审/代码/人工评测器（[Langfuse](https://langfuse.com/docs)，访问于 2026-10-18）。

---

## 2. Observability

**2. 可观测性**

### 2.1 OTel GenAI conventions: adopt now, pin versions

**2.1 OTel GenAI 语义约定：现在就采用，但要固定版本**

Two 2026 facts matter operationally. First, **the conventions moved** to `open-telemetry/semantic-conventions-genai`, extending core conventions via Weaver; old doc pages are stubs ([repo README](https://github.com/open-telemetry/semantic-conventions-genai), accessed 2026-10-18). Second, **they are `Development`, not stable** — every agent span and attribute carries a Development badge ([agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18).

2026 年有两个事实在运维上很重要。第一，**这些约定已经迁移**到 `open-telemetry/semantic-conventions-genai`，通过 Weaver 扩展核心约定；旧的文档页面只剩下占位内容（[仓库 README](https://github.com/open-telemetry/semantic-conventions-genai)，访问于 2026-10-18）。第二，**它们处于 `Development` 状态，而非稳定版**——每个 Agent span 和属性都带有 Development 标记（[Agent span](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)，访问于 2026-10-18）。

Adopt anyway, but **pin the semconv version, emit attributes through one `AgentTelemetry` abstraction in .NET, and never let dashboards query raw attributes directly**. Plan one breaking rename per year; proprietary schemas cost more to unwind.

无论如何都要采用，但要**固定 semconv 版本，在 .NET 中通过唯一的 `AgentTelemetry` 抽象来发出属性，并且绝不让仪表盘直接查询原始属性**。按每年一次破坏性改名来做计划；专有 schema 的拆除成本更高。

Spec span taxonomy (all Development): `create_agent`, `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool`, plus skill and command-execution spans, with operation recorded in `gen_ai.operation.name` (same source). Model, provider, agent identity, conversation identity and token usage are modelled; `gen_ai.input.messages` / `gen_ai.output.messages` / `gen_ai.system_instructions` are **opt-in with an explicit PII warning**.

规范中的 span 分类（全部为 Development）：`create_agent`、`invoke_agent`、`invoke_workflow`、`plan`、`execute_tool`，外加 skill 和命令执行 span，操作名记录在 `gen_ai.operation.name` 中（同一来源）。模型、提供商、Agent 身份、会话身份和 token 用量都有建模；`gen_ai.input.messages` / `gen_ai.output.messages` / `gen_ai.system_instructions` 则**需显式开启（opt-in），并附有明确的 PII 警告**。

### 2.2 Trace data model sketch

**2.2 Trace 数据模型草图**

```
Trace (one per user turn / trigger)
└── span invoke_workflow {workflow}              INTERNAL
    ├── span invoke_agent {agent.name}           INTERNAL
    │   ├── span plan {agent.name}               INTERNAL
    │   ├── span chat {model}                    CLIENT
    │   ├── span execute_tool {tool}             INTERNAL
    │   │   └── span {http/db/sandbox call}      CLIENT
    │   └── span hitl.wait {approval}            INTERNAL
    ├── span policy.evaluate {ruleset}           INTERNAL  (custom)
    └── span retrieval {index}                   INTERNAL
```

| Layer<br>层 | Attributes<br>属性 | Notes<br>说明 |
|---|---|---|
| Identity<br>身份 | `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model` | Required-level; needed for sampling at span creation<br>必需级别；在创建 span 时用于采样 |
| Agent | `gen_ai.agent.id`, `.name`, `.version` | Stable registry ID, not in-memory instance ID<br>稳定的注册表 ID，而不是内存中的实例 ID |
| Session<br>会话 | `gen_ai.conversation.id` | Only a real conversation ID; the spec forbids synthesising one<br>只能是真实的会话 ID；规范禁止自行合成一个 |
| Usage<br>用量 | input/output tokens, cache-read counts, `gen_ai.response.finish_reasons`<br>输入/输出 token、缓存读取计数、`gen_ai.response.finish_reasons` | Without cache-read tokens, cache savings are invisible<br>没有缓存读取 token，缓存带来的节省就不可见 |
| Content<br>内容 | input/output messages, system instructions<br>输入/输出消息、系统指令 | Opt-in; hash/redact by default<br>需显式开启；默认做哈希/脱敏 |
| Platform<br>平台 | `app.tenant.id`, `app.license.plan`, `app.prompt.version`, `app.policy.decision`, `app.tool.idempotency_key`, `app.cost.usd`, `app.budget.remaining` | What billing, audit and incident review actually need<br>计费、审计和事故复盘真正需要的东西 |
| Linkage<br>关联 | span links approval↔resumed run<br>用 span link 关联审批↔恢复后的运行 | A suspended agent is two traces otherwise<br>否则一个被挂起的 Agent 会变成两条 trace |

Two rules that save pain: **`app.tenant.id` on every span, enforced by a processor that quarantines non-conforming spans** (same discipline as tenant-scoped .NET middleware); and **cost per span**, so regressions attribute to a tool or prompt version rather than "the agent got expensive".

两条能省掉很多痛苦的规则：**每个 span 都带 `app.tenant.id`，并由一个隔离不合规 span 的处理器强制执行**（与租户作用域的 .NET 中间件是同一种纪律）；以及**按 span 计成本**，这样回归就能归因到某个工具或提示词版本，而不是笼统地说「Agent 变贵了」。

### 2.3 Content capture, PII, retention

**2.3 内容采集、PII 与保留期**

The spec itself warns message attributes likely contain PII. Default to **no bodies**: hashes, lengths, redacted previews. Full capture only on tenant opt-in, with short TTL, field-level redaction, and access logging. Keep **audit** (who/what/approval/result) separate from **debug** (prompts/messages): different retention, access control and legal basis.

规范本身就警告说，消息属性很可能包含 PII。默认**不采集正文**：只记录哈希、长度、脱敏预览。只有在租户显式开启时才完整采集，并配合短 TTL、字段级脱敏和访问日志。把**审计**（谁/做了什么/审批/结果）与**调试**（提示词/消息）分开：两者的保留期、访问控制和法律依据都不同。

### 2.4 Tooling comparison (late 2026)

**2.4 工具对比（2026 年末）**

| Tool<br>工具 | Self-host<br>自托管 | Strengths<br>优势 | Watch-outs<br>注意事项 |
|---|---|---|---|
| **LangSmith** — traces, dashboards, automations, online evals ([docs](https://docs.langchain.com/langsmith/observability), accessed 2026-10-18)<br>**LangSmith** —— trace、仪表盘、自动化、在线评测（[文档](https://docs.langchain.com/langsmith/observability)，访问于 2026-10-18） | Commercial/enterprise options<br>商业版/企业版选项 | Mature eval UX; deepest with LangChain<br>评测体验成熟；与 LangChain 集成最深 | Verify residency/DPA and .NET client maturity<br>需核实数据驻留/DPA 以及 .NET 客户端的成熟度 |
| **Langfuse** — OSS, OTel-based; v4 released 2026-08 ([docs](https://langfuse.com/docs), accessed 2026-10-18)<br>**Langfuse** —— 开源，基于 OTel；v4 于 2026-08 发布（[文档](https://langfuse.com/docs)，访问于 2026-10-18） | **Yes** (Docker/K8s)<br>**是**（Docker/K8s） | Best default for on-prem/regulated; prompts+evals+sessions+agent graphs<br>本地部署/受监管场景的最佳默认选择；提示词 + 评测 + 会话 + Agent 图 | You own HA/upgrades; check license for embedding in a commercial product<br>高可用/升级由你自己负责；嵌入商业产品前需检查许可证 |
| **Braintrust** — instrument→evaluate→deploy, online scoring, audit logs, SCIM ([docs](https://www.braintrust.dev/docs), accessed 2026-10-18)<br>**Braintrust** —— 插桩→评测→部署、在线评分、审计日志、SCIM（[文档](https://www.braintrust.dev/docs)，访问于 2026-10-18） | Enterprise options<br>企业版选项 | Strong experiments and human review<br>实验和人工审核能力强 | SaaS-first; confirm self-host and audit-log export<br>以 SaaS 为主；需确认自托管和审计日志导出 |
| **Arize Phoenix** — OSS tracing + evals, OpenInference, RBAC/secrets/retention ([docs](https://arize.com/docs/phoenix), accessed 2026-10-18)<br>**Arize Phoenix** —— 开源追踪 + 评测、OpenInference、RBAC/密钥/保留期（[文档](https://arize.com/docs/phoenix)，访问于 2026-10-18） | **Yes**<br>**是** | Good OTel/OpenInference fit; judge + datasets built in<br>与 OTel/OpenInference 契合良好；内置评审 + 数据集 | Smaller ecosystem than commercial suites<br>生态比商业套件小 |
| **W&B Weave / LangWatch** ([Weave](https://docs.wandb.ai/weave), [LangWatch](https://langwatch.ai)) | Varies<br>视情况而定 | Evaluation-first UX<br>以评测为先的体验 | Content not independently re-verified for this note<br>本文未独立重新核实其内容 |

**Recommendation:** two layers — OTel-native instrumentation you own, exporting to a swappable backend. Self-hosted Langfuse or Phoenix for on-prem/licensed tiers; whichever passes procurement for SaaS. Never let the eval product become the system of record for audit.

**建议：** 分两层——由你自己掌控的 OTel 原生插桩，导出到一个可替换的后端。本地部署/许可分级使用自托管的 Langfuse 或 Phoenix；SaaS 则选择能通过采购审核的那一个。绝不让评测产品成为审计的记录系统（system of record）。

### 2.5 Metrics and SLOs

**2.5 指标与 SLO**

Beyond latency/errors: **task success proxy**, **pass^k trend**, **cost per successful task**, **cache-hit rate**, **steps per task**, **tool error rate by tool**, **approval queue depth/age**, **guardrail-block rate**, **judge-score drift vs 7-day baseline**. Cost per successful task is the most useful business metric — it captures model choice *and* agent efficiency.

除了延迟/错误之外：**任务成功代理指标**、**pass^k 趋势**、**每个成功任务的成本**、**缓存命中率**、**每个任务的步数**、**按工具划分的工具错误率**、**审批队列深度/等待时长**、**护栏拦截率**、**评审分数相对 7 天基线的漂移**。每个成功任务的成本是最有用的业务指标——它同时反映了模型选择*和* Agent 效率。

---

## 3. Security threat model

**3. 安全威胁模型**

### 3.1 The premise

**3.1 前提**

Prompt injection is unsolved. Willison's **lethal trifecta** — private data + untrusted content + external communication — lets an attacker controlling content the agent reads exfiltrate data; he argues vendors claiming "95% of attacks blocked" are failing by web-security standards ([lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/), accessed 2026-10-18). Make **removing one leg** a product decision, not a prompt tweak.

提示词注入尚未被解决。Willison 提出的**致命三要素（lethal trifecta）**——私有数据 + 不可信内容 + 对外通信——让能够控制 Agent 所读内容的攻击者得以窃取数据；他认为，那些宣称「拦截了 95% 攻击」的厂商，按 Web 安全的标准衡量是不及格的（[致命三要素](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)，访问于 2026-10-18）。要把**去掉其中一条腿**作为产品决策，而不是一次提示词微调。

OWASP's 2026 list now folds in incident evidence (7,714 incidents, 6,639 classified): **Excessive Agency rose to #3**, Unbounded Consumption rose four places, Improper Output Handling fell 5th→10th, and System Prompt Leakage became **Hidden Context Exposure** ([OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/); [source](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final), accessed 2026-10-18). When the model becomes an **actor** — tools, memory, consequences — pair it with the **Agentic Top 10** ([OWASP Agentic 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), accessed 2026-10-18). **[unsettled] verify ASI numbering against the PDF before customer-facing use.**

OWASP 2026 年版榜单现在纳入了事故证据（7,714 起事故，其中 6,639 起已分类）：**Excessive Agency（过度代理）升至第 3 位**，Unbounded Consumption（无限制消耗）上升了四位，Improper Output Handling（不当输出处理）从第 5 位跌至第 10 位，System Prompt Leakage（系统提示词泄露）则变成了 **Hidden Context Exposure（隐藏上下文暴露）**（[OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)；[源文件](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final)，访问于 2026-10-18）。当模型成为一个**行动者**——拥有工具、记忆，并会产生后果——时，要搭配 **Agentic Top 10** 一起使用（[OWASP Agentic 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)，访问于 2026-10-18）。**[unsettled] 在面向客户使用前，需对照 PDF 核实 ASI 编号。**

### 3.2 Threat model

**3.2 威胁模型**

| Attack<br>攻击 | Mechanism<br>机制 | Control (architectural, not prompt-based)<br>控制措施（架构层面，而非基于提示词） |
|---|---|---|
| Direct injection / jailbreak<br>直接注入 / 越狱 | User text tells agent to ignore policy<br>用户文本让 Agent 忽略策略 | Instruction hierarchy, allowlisted actions, output-schema validation, per-action authorisation; bound blast radius<br>指令层级、动作白名单、输出 schema 校验、逐动作授权；限制爆炸半径 |
| **Indirect** injection<br>**间接**注入 | Poisoned doc/web/email/ticket/tool result carries instructions<br>被投毒的文档/网页/邮件/工单/工具结果中夹带指令 | Treat retrieved content as **data**; never auto-execute retrieved instructions; require explicit intent for consequential actions; provenance labels<br>把检索到的内容当作**数据**；绝不自动执行检索到的指令；有后果的操作需要明确的意图；来源（provenance）标签 |
| Lethal-trifecta exfiltration<br>致命三要素式数据窃取 | Agent reads private data and can send outward (HTTP/email/image URL/PR comment)<br>Agent 读取私有数据，并且能向外发送（HTTP/邮件/图片 URL/PR 评论） | Break one leg: egress allowlist, outbound DLP, no unattended external send, human approval<br>断掉一条腿：出站白名单、出站 DLP、禁止无人值守的对外发送、人工审批 |
| Tool poisoning / malicious MCP server<br>工具投毒 / 恶意 MCP 服务器 | Tool *descriptions* hide instructions; server changes after approval ("rug pull")<br>工具*描述*中藏有指令；服务器在获批后发生变化（「rug pull」，即获批后偷换） | Allowlist + pin version/digest; review descriptions as code; no untrusted dynamic discovery; scope minimisation ([MCP security](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices), accessed 2026-10-18)<br>白名单 + 固定版本/摘要；像审查代码一样审查描述；不做不可信的动态发现；最小化权限范围（[MCP security](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)，访问于 2026-10-18） |
| Confused deputy / token theft<br>混淆代理（confused deputy）/ token 窃取 | Static client credentials in proxy; token passed upstream<br>代理中使用静态客户端凭据；token 被透传到上游 | Audience-bound tokens, **no token passthrough**, per-request consent, separate client registration (same source; [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization))<br>绑定受众（audience）的 token、**禁止 token 透传**、逐请求授权同意、独立的客户端注册（同一来源；[MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)） |
| Excessive agency<br>过度代理 | Broad scopes, auto-approve, long-lived credentials<br>宽泛的权限范围、自动批准、长期有效的凭据 | Least privilege per task, short-lived capability tokens, step-up auth, approval gates for irreversible actions<br>按任务最小权限、短期有效的能力 token、升级认证（step-up auth）、对不可逆操作设审批关卡 |
| Sandbox escape / RCE<br>沙箱逃逸 / RCE | Model-generated code or shell<br>模型生成的代码或 shell 命令 | microVM/container isolation, no credentials inside sandbox, egress allowlist, ephemeral, resource-capped<br>microVM/容器隔离、沙箱内不放凭据、出站白名单、临时性、资源受限 |
| Secret exposure<br>密钥泄露 | Secrets in prompt, tool output or trace bodies<br>密钥出现在提示词、工具输出或 trace 正文中 | Secret broker resolves inside the tool boundary; never in context; collector-side redaction<br>由密钥代理在工具边界内解析；绝不进入上下文；在采集器侧脱敏 |
| Memory/context poisoning<br>记忆/上下文投毒 | Attacker writes long-term memory or shared index<br>攻击者写入长期记忆或共享索引 | Tenant-scoped memory, provenance + TTL, validate writes, never promote untrusted content to system instructions<br>租户作用域的记忆、来源 + TTL、校验写入、绝不把不可信内容提升为系统指令 |
| Supply chain<br>供应链 | Compromised model artifact or MCP/agent package<br>被攻破的模型制品或 MCP/Agent 包 | Pin model versions, AI-BOM ([OWASP AIBOM](https://github.com/GenAI-Security-Project/aibom-generator), accessed 2026-10-18), eval gate before upgrade<br>固定模型版本、AI-BOM（[OWASP AIBOM](https://github.com/GenAI-Security-Project/aibom-generator)，访问于 2026-10-18）、升级前设评测关卡 |
| Cross-tenant access<br>跨租户访问 | Tool call omits tenant filter; IDOR via arguments<br>工具调用遗漏租户过滤；通过参数实施 IDOR | Tenant ID bound by the platform, not the model; RLS; cross-tenant regression tests<br>租户 ID 由平台绑定，而非由模型提供；RLS；跨租户回归测试 |
| Denial of wallet<br>钱包耗尽攻击（denial of wallet） | Loops, huge context, tool recursion<br>循环、超大上下文、工具递归 | Per-run token/$ caps, max steps, loop detection, per-tenant limits, backpressure<br>每次运行的 token/$ 上限、最大步数、循环检测、按租户限额、背压 |
| Trust exploitation<br>信任利用 | Agent asserts authority ("your manager approved")<br>Agent 声称拥有授权（「你的经理已经批准了」） | Provenance in UI, confirmation with concrete action diff, immutable audit<br>在 UI 中展示来源、附带具体操作差异（diff）的确认、不可篡改的审计 |

### 3.3 MCP hardening

**3.3 MCP 加固**

MCP is now a Linux Foundation project under the **Agentic AI Foundation** (donated 2025-12-09; co-founded by Anthropic, Block, OpenAI, with Google, Microsoft, AWS, Cloudflare, Bloomberg), with >10,000 public servers and a community registry; the 2025-11-25 spec added async operations, statelessness, server identity and extensions ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), accessed 2026-10-18).

MCP 现已成为 Linux 基金会旗下 **Agentic AI Foundation** 的一个项目（于 2025-12-09 捐赠；由 Anthropic、Block、OpenAI 联合创立，Google、Microsoft、AWS、Cloudflare、Bloomberg 参与），拥有超过 10,000 个公开服务器和一个社区注册表；2025-11-25 版规范新增了异步操作、无状态化、服务器身份和扩展机制（[Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)，访问于 2026-10-18）。

Practical controls: **registry + allowlist, not open marketplace**; OAuth 2.1 with audience-bound tokens and step-up scopes; **no token passthrough, no static client secrets**; tool descriptions reviewed like code (they are prompt content); **per-tenant credentials**, never a shared service identity.

实用的控制措施：**注册表 + 白名单，而不是开放市场**；采用 OAuth 2.1，配合绑定受众的 token 和升级权限范围（step-up scopes）；**禁止 token 透传，禁止静态客户端密钥**；像审查代码一样审查工具描述（它们就是提示词内容）；**按租户分配凭据**，绝不使用共享的服务身份。

### 3.4 Sandboxing, audit, red teaming

**3.4 沙箱、审计与红队测试**

Anything executing model-authored code or driving a browser is a hostile-code boundary: ephemeral microVM/container per session, no host mounts, no ambient cloud credentials, egress allowlist, CPU/memory/disk/time caps, kill switch. E2B documents sandbox templates, network and secrets/identity ([E2B](https://docs.e2b.dev), accessed 2026-10-18); Daytona documents orgs, SSO, limits and multi-language SDKs incl. Java ([Daytona](https://www.daytona.io/docs/en/), accessed 2026-10-18); AWS now offers **Lambda MicroVMs** (8-hour max, 400 GB aggregate memory) for managed isolation inside your AWS account ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18).

任何执行模型编写的代码或驱动浏览器的东西，都是一道敌对代码边界：每个会话一个临时的 microVM/容器、不挂载宿主机目录、环境中没有隐式的云凭据、出站白名单、CPU/内存/磁盘/时间上限、终止开关。E2B 的文档涵盖沙箱模板、网络以及密钥/身份（[E2B](https://docs.e2b.dev)，访问于 2026-10-18）；Daytona 的文档涵盖组织、SSO、限额以及包括 Java 在内的多语言 SDK（[Daytona](https://www.daytona.io/docs/en/)，访问于 2026-10-18）；AWS 现在提供 **Lambda MicroVMs**（最长 8 小时，聚合内存 400 GB），用于在你自己的 AWS 账户内实现托管隔离（[Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)，访问于 2026-10-18）。

**Audit is a separate product from observability.** Per consequential action record: timestamp, tenant, user, agent ID+version, prompt version, model+version, tool, redacted arguments, policy decision + rule ID, approver, result, idempotency key, trace ID. Append-only storage, retention aligned to contract/regulation, customer-readable export.

**审计是独立于可观测性的另一个产品。** 对每个有后果的操作记录：时间戳、租户、用户、Agent ID+版本、提示词版本、模型+版本、工具、脱敏后的参数、策略决策 + 规则 ID、审批人、结果、幂等键、trace ID。采用仅追加（append-only）存储，保留期与合同/法规对齐，并提供客户可读的导出。

**Red teaming is continuous**, not a one-off pen test: injection corpora (direct/indirect), tool-poisoning payloads, exfiltration attempts, cross-tenant probes, budget-exhaustion loops, refreshed weekly in CI. **[unsettled]** No agent red-team benchmark maps credibly to enterprise risk yet; OWASP's incident corpus and AISVS mapping are the closest anchors.

**红队测试是持续性的**，而不是一次性的渗透测试：注入语料（直接/间接）、工具投毒载荷、数据窃取尝试、跨租户探测、预算耗尽循环，每周在 CI 中刷新。**[unsettled]** 目前还没有哪个 Agent 红队基准能可信地映射到企业风险；OWASP 的事故语料库和 AISVS 映射是最接近的锚点。

---

## 4. Reliability engineering

**4. 可靠性工程**

### 4.1 Durable execution is the default for agent loops

**4.1 持久化执行是 Agent 循环的默认选择**

An agent loop is a long-running, stateful workflow whose steps fail independently. Temporal documents exactly this mapping: the loop is a Workflow, each model and tool call an Activity, crashes resume rather than restart, and human-in-the-loop is a durable Signal + Timer with an Approval design pattern ([Temporal use cases](https://docs.temporal.io/evaluate/use-cases-design-patterns), accessed 2026-10-18). It also names the broker failure mode this avoids: a queue with a short visibility timeout can hand the same message to a second consumer while the first is still working (same source). Temporal has a **.NET SDK**.

Agent 循环是一个长时间运行、有状态的工作流，其各个步骤会各自独立地失败。Temporal 的文档恰好描述了这种映射：循环是一个 Workflow，每次模型调用和工具调用是一个 Activity，崩溃后是恢复而非重启，而人在回路（HITL）是一个持久化的 Signal + Timer，并配有 Approval 设计模式（[Temporal use cases](https://docs.temporal.io/evaluate/use-cases-design-patterns)，访问于 2026-10-18）。它还点出了由此规避的消息代理失败模式：可见性超时较短的队列，可能在第一个消费者仍在处理时，把同一条消息交给第二个消费者（同一来源）。Temporal 提供 **.NET SDK**。

Alternatives by operational weight: **Temporal/Inngest/Step Functions** (full replay, timers, human waits; Inngest markets durable execution, flow control, agent evals, sandboxes, SOC 2 Type II — [Inngest](https://www.inngest.com/platform/durable-execution), accessed 2026-10-18); **AWS Lambda durable functions** — 5M running executions/region (10M in us-east-1/us-west-2/eu-west-1), 30,000 durable operations per execution, 100 MB persisted per execution ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18); **roll-your-own queue + checkpoint table** — acceptable only for short loops with idempotent tools.

按运维负担排列的替代方案：**Temporal/Inngest/Step Functions**（完整回放、定时器、人工等待；Inngest 宣传其具备持久化执行、流量控制、Agent 评测、沙箱、SOC 2 Type II——[Inngest](https://www.inngest.com/platform/durable-execution)，访问于 2026-10-18）；**AWS Lambda durable functions**——每个区域 5M 个运行中的执行（us-east-1/us-west-2/eu-west-1 为 10M），每次执行 30,000 个持久化操作，每次执行持久化 100 MB（[Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)，访问于 2026-10-18）；**自建队列 + 检查点表**——仅适用于使用幂等工具的短循环。

### 4.2 Idempotency, retries, timeouts

**4.2 幂等、重试与超时**

- **Idempotency key per tool invocation**, derived from `(run_id, step_no, tool, canonical_args_hash)`, persisted before the call and checked on retry — the only reliable defence against duplicate side effects.

  **每次工具调用一个幂等键**，由 `(run_id, step_no, tool, canonical_args_hash)` 派生，在调用前持久化并在重试时检查——这是防止重复副作用的唯一可靠手段。

- **Retry only idempotent or key-protected operations**; never blind-retry payments, emails or ticket creation.

  **只重试幂等的或受幂等键保护的操作**；绝不盲目重试支付、邮件或工单创建。

- **Exponential backoff with jitter** for 429/5xx, capped attempts and total elapsed per step ([AWS backoff/jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), accessed 2026-10-18).

  对 429/5xx 采用**带抖动（jitter）的指数退避**，并限制尝试次数和每一步的总耗时（[AWS backoff/jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)，访问于 2026-10-18）。

- **Distinguish retryable from terminal** (validation, policy denial, auth failure = terminal).

  **区分可重试错误和终止性错误**（校验失败、策略拒绝、认证失败 = 终止性）。

- **Circuit breakers per provider+model and per critical tool**, with closed/open/half-open states and manual override ([Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker), accessed 2026-10-18).

  **按提供商+模型以及按关键工具设置熔断器**，具备闭合/断开/半开状态和手动覆盖（[熔断器模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)，访问于 2026-10-18）。

- **Timeouts from p99** per model+prompt size, plus a **per-run wall-clock deadline** communicated to the model as a remaining budget.

  **依据 p99 设置超时**，按模型+提示词大小区分，外加一个**每次运行的挂钟截止时间**，并以剩余预算的形式告知模型。

### 4.3 Human-in-the-loop: suspend, don't block

**4.3 人在回路：挂起，而不是阻塞**

Never park an HTTP request or worker thread for a 10-minute approval. Model it: agent proposes → orchestrator writes an approval request (action, redacted diff, policy context, expiry) and transitions to `waiting_approval` → worker released, state and trace link persisted → approver acts in UI/Teams/Slack → a Signal/Update resumes. Timeout policy is auto-deny or escalate; **never auto-approve on timeout**. Record approver + timestamp in audit and link the two traces.

绝不要为了一个 10 分钟的审批而挂住一个 HTTP 请求或工作线程。应当这样建模：Agent 提出建议 → 编排者写入一条审批请求（操作、脱敏后的 diff、策略上下文、过期时间）并转换到 `waiting_approval` 状态 → 释放工作者，持久化状态和 trace 链接 → 审批人在 UI/Teams/Slack 中操作 → 由一个 Signal/Update 恢复执行。超时策略是自动拒绝或升级；**绝不在超时时自动批准**。在审计中记录审批人 + 时间戳，并把两条 trace 关联起来。

### 4.4 Multi-tenant isolation

**4.4 多租户隔离**

| Dimension<br>维度 | Mechanism<br>机制 | Failure if missed<br>缺失时的失败后果 |
|---|---|---|
| Data<br>数据 | Tenant ID enforced in data layer + RLS; never model-supplied filters<br>在数据层 + RLS 中强制租户 ID；绝不使用模型提供的过滤条件 | Cross-tenant read via tool args<br>通过工具参数跨租户读取 |
| Credentials<br>凭据 | Per-tenant secrets/OAuth grants<br>按租户的密钥/OAuth 授权 | One breach compromises all<br>一处被攻破，全部沦陷 |
| Compute<br>计算 | Tenant-scoped queues/workers; durable engines expose task-queue priority and fairness (Temporal documents this for shared workers)<br>租户作用域的队列/工作者；持久化引擎提供任务队列优先级和公平性（Temporal 针对共享工作者记录了这一点） | Batch tenant starves interactive<br>批处理租户把交互式租户饿死 |
| Prompt/memory<br>提示词/记忆 | Tenant-partitioned memory and vector namespaces<br>按租户分区的记忆和向量命名空间 | Retrieval leaks<br>检索泄漏 |
| Caches<br>缓存 | Per-customer cache-accounting keys; OpenAI documents `prompt_cache_key` to separate accounting and prevent cache-hit probing ([OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18)<br>按客户划分的缓存计量键；OpenAI 文档说明可用 `prompt_cache_key` 来分开计量并防止缓存命中探测（[OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching)，访问于 2026-10-18） | Billing opacity; side-channel probing<br>计费不透明；侧信道探测 |
| Rate/cost<br>速率/成本 | Per-tenant token and $ budgets at the gateway<br>在网关处设置按租户的 token 和 $ 预算 | Denial of wallet; unfair allocation<br>钱包耗尽；分配不公 |
| Audit<br>审计 | Tenant-scoped views + platform immutable copy<br>租户作用域的视图 + 平台侧不可篡改副本 | Can't answer "what did our agents do"<br>无法回答「我们的 Agent 做了什么」 |

**[established]** the dimensions; **[unsettled]** fair allocation of shared prompt-cache costs across tenants — pick a policy (attribute by cache key) and put it in the contract.

**[established]** 上述各维度；**[unsettled]** 共享提示词缓存的成本如何在租户之间公平分摊——选定一种策略（按缓存键归属）并写进合同。

---

## 5. Cost and latency levers

**5. 成本与延迟的调节杠杆**

Cost is dominated by **input tokens × context length × turns**, so token/turn levers beat millisecond levers.

成本主要由**输入 token × 上下文长度 × 轮数**决定，因此 token/轮数层面的杠杆胜过毫秒级的杠杆。

| Lever<br>杠杆 | Mechanism<br>机制 | Expected impact<br>预期效果 | Cost / risk<br>代价 / 风险 |
|---|---|---|---|
| **Prompt caching**<br>**提示词缓存** | Reuse stable prefix (system prompt, tools, examples, history)<br>复用稳定前缀（系统提示词、工具、示例、历史） | Cache reads **0.1×** input price (0.05× on Anthropic Opus/Sonnet 5.5-class, 0.025× on Fable/Mythos 5.1-class); OpenAI **0.1× read / 1.25× write** on current GPT-5.6+ models; a documented multi-turn agent pattern reported **>90% cache-hit** ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), accessed 2026-10-18)<br>缓存读取价格为输入价格的 **0.1×**（Anthropic Opus/Sonnet 5.5 级别为 0.05×，Fable/Mythos 5.1 级别为 0.025×）；OpenAI 在当前 GPT-5.6+ 模型上为 **0.1× 读取 / 1.25× 写入**；一个有文档记录的多轮 Agent 模式报告了 **>90% 的缓存命中率**（[Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)，[OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching)，访问于 2026-10-18） | Writes cost more; 5-min (Anthropic) / 30-min (OpenAI GPT-5.6+) TTL; any dynamic prefix kills reuse<br>写入更贵；TTL 为 5 分钟（Anthropic）/ 30 分钟（OpenAI GPT-5.6+）；任何动态前缀都会破坏复用 |
| **Stable-prefix hygiene**<br>**稳定前缀卫生** | Static content first, dynamic last, append never rewrite<br>静态内容在前，动态内容在后，只追加、不改写 | Turns ~30% hit rate into ~80–90% on long sessions<br>在长会话中把约 30% 的命中率提升到约 80–90% | Requires prompt architecture + versioning<br>需要提示词架构 + 版本管理 |
| **Compaction / tool-result clearing**<br>**压缩（compaction）/ 工具结果清理** | Summarize near window limit; drop stale raw output<br>接近窗口上限时做摘要；丢弃过时的原始输出 | ~40–70% context reduction on long runs (~)<br>长运行中上下文减少约 40–70%（~） | Loses detail; tuned on real traces; resets cache on next call ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), accessed 2026-10-18)<br>会丢失细节；需在真实 trace 上调优；会在下一次调用时重置缓存（[Anthropic 上下文工程](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)，访问于 2026-10-18） |
| **Model routing/cascade**<br>**模型路由/级联** | Small model for easy turns, escalate on confidence/failure<br>简单轮次用小模型，依据置信度/失败情况升级 | ~50–80% cost cut with equal quality when routed well (~)<br>路由得当时，在质量相当的情况下成本降低约 50–80%（~） | Two models to eval/monitor; routing errors visible ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [RouteLLM](https://arxiv.org/abs/2406.18665), accessed 2026-10-18)<br>需要评测/监控两个模型；路由错误会显现出来（[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)，[RouteLLM](https://arxiv.org/abs/2406.18665)，访问于 2026-10-18） |
| **Parallel tool calls**<br>**并行工具调用** | Independent calls in one turn<br>在一轮中发起相互独立的调用 | Wall clock ≈ max instead of sum (~2–5× on fan-out)<br>挂钟时间 ≈ 最大值而非总和（扇出时约 2–5×） | Concurrency load; ordering must be explicit<br>并发负载；顺序必须显式指定 |
| **Deferred tool loading**<br>**延迟加载工具** | Load relevant tool definitions only<br>只加载相关的工具定义 | Large static schemas leave every request<br>庞大的静态 schema 不再出现在每个请求中 | Extra round trip; selection errors ([Anthropic/MCP](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation))<br>额外的往返；选择错误（[Anthropic/MCP](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)） |
| **Batch APIs**<br>**批处理 API** | Async bulk at provider discount<br>以提供商折扣价进行异步批量处理 | Historically ~50% cheaper, higher latency<br>历史上便宜约 50%，延迟更高 | Not interactive; **[unsettled] verify current %** ([Anthropic batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing), [OpenAI batch](https://developers.openai.com/api/docs/guides/batch))<br>非交互式；**[unsettled] 需核实当前的折扣比例**（[Anthropic batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing)，[OpenAI batch](https://developers.openai.com/api/docs/guides/batch)） |
| **Hard budget caps + output discipline**<br>**硬性预算上限 + 输出纪律** | Per-run/user/tenant ceilings; structured outputs, max tokens, stop sequences<br>按运行/用户/租户设上限；结构化输出、最大 token 数、停止序列 | Unbounded-cost incidents become bounded<br>无上限的成本事故变得有上限 | Enforce at gateway, never via prompt ([budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/))<br>在网关处强制执行，绝不靠提示词（[预算上限](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/)） |

**Order of attack:** measure cache-hit rate and cost per successful task → stabilise prefix → cap budgets → compact long runs → route easy turns → batch non-interactive work. Most teams recover 50–80% of spend from the first three.

**着手顺序：** 测量缓存命中率和每个成功任务的成本 → 稳定前缀 → 设置预算上限 → 压缩长运行 → 路由简单轮次 → 批处理非交互式工作。大多数团队仅靠前三步就能收回 50–80% 的支出。

---

## 6. Deployment and infrastructure

**6. 部署与基础设施**

**Serverless vs workers.** AWS Lambda caps a single invocation at **15 minutes** (90-minute async only for managed instances), and durable functions cap at 30,000 operations per execution ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed 2026-10-18). Agent runs routinely exceed that or wait hours on humans. Therefore four tiers: stateless **API/edge** (streams, no loop), **orchestration** (durable engine owns state), **execution workers** (tools/sandboxes, scale on queue depth), and **sandbox** (ephemeral, network-restricted). This is your order-processing shape; the new part is that **step count is model-chosen**, so queue-depth scaling must be paired with step and budget caps.

**Serverless 与工作者。** AWS Lambda 单次调用上限为 **15 分钟**（90 分钟的异步调用仅适用于托管实例），durable functions 每次执行最多 30,000 个操作（[Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)，访问于 2026-10-18）。Agent 运行经常超出这一限制，或者要等人类好几个小时。因此分为四层：无状态的 **API/边缘层**（流式输出，不跑循环）、**编排层**（由持久化引擎掌管状态）、**执行工作者层**（工具/沙箱，按队列深度伸缩），以及**沙箱层**（临时性、网络受限）。这就是你熟悉的订单处理架构形态；新的地方在于**步数是由模型决定的**，所以按队列深度伸缩必须与步数上限和预算上限搭配使用。

**Sandbox providers:** E2B ([docs](https://docs.e2b.dev), accessed 2026-10-18); Daytona ([docs](https://www.daytona.io/docs/en/), accessed 2026-10-18); AWS Lambda MicroVMs ([quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)); self-hosted microVM if you already run a hardened container platform. Select on cold-start, egress granularity, snapshot/persistence, secret-injection model, per-tenant isolation guarantee, log export, and compliance boundary.

**沙箱提供商：** E2B（[文档](https://docs.e2b.dev)，访问于 2026-10-18）；Daytona（[文档](https://www.daytona.io/docs/en/)，访问于 2026-10-18）；AWS Lambda MicroVMs（[配额](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)）；如果你已经在运行加固过的容器平台，也可以自托管 microVM。选型依据：冷启动、出站控制粒度、快照/持久化、密钥注入模式、按租户的隔离保证、日志导出以及合规边界。

**Browser automation:** isolated browser session per tenant, credential brokering (never type customer passwords from model context), DOM-level action logging, domain allowlist, session recording for disputes. **[unsettled]** least standardised layer; expect Playwright + hosted sessions.

**浏览器自动化：** 每个租户一个隔离的浏览器会话、凭据代理（绝不从模型上下文中输入客户密码）、DOM 级别的操作日志、域名白名单、用于争议处理的会话录制。**[unsettled]** 这是标准化程度最低的一层；预计会是 Playwright + 托管会话。

**Memory/vector stores:** namespace/index per tenant for regulated customers; shared index + mandatory filter only for low-sensitivity tiers, with tests proving tool arguments cannot bypass the filter. Memory needs TTL, provenance, user-visible edit/delete (GDPR), and a hard rule that retrieved content never becomes system instructions. Evaluate retrieval recall@k and answer groundedness separately — a bad index looks like a bad model.

**记忆/向量存储：** 对受监管客户按租户划分命名空间/索引；共享索引 + 强制过滤只用于低敏感度层级，并用测试证明工具参数无法绕过该过滤。记忆需要 TTL、来源、用户可见的编辑/删除（GDPR），以及一条硬性规则：检索到的内容绝不能变成系统指令。分别评测检索的 recall@k 和回答的有据性（groundedness）——糟糕的索引看起来就像糟糕的模型。

---

## 7. Governance and compliance

**7. 治理与合规**

### 7.1 EU AI Act — the 2026 timetable

**7.1 欧盟 AI 法案——2026 年时间表**

The Commission page is now explicit: in force 2024-08-01, applicable **2026-08-02** with exceptions; the **AI Omnibus** was adopted 2025-11-19, politically agreed 2026-05-07, **in force 2026-07-27**, moving Annex III high-risk to **2027-12-02** and Annex I product-embedded high-risk to **2028-08-02** ([European Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai), accessed 2026-10-18; [Omnibus text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744); Parliament's final approval 2026-06-16 per [Morgan Lewis](https://www.morganlewis.com/zh-cn/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know), accessed 2026-10-18).

欧盟委员会的页面现在已经明确：该法案于 2024-08-01 生效，自 **2026-08-02** 起适用（有例外）；**AI Omnibus**（AI 综合修订案）于 2025-11-19 通过，2026-05-07 达成政治协议，**2026-07-27 生效**，将附件 III 高风险义务推迟到 **2027-12-02**，将附件 I 产品内嵌高风险义务推迟到 **2028-08-02**（[欧盟委员会](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)，访问于 2026-10-18；[Omnibus 文本](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744)；据 [Morgan Lewis](https://www.morganlewis.com/zh-cn/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know)，议会于 2026-06-16 最终批准，访问于 2026-10-18）。

| Date<br>日期 | Obligation<br>义务 | Impact<br>影响 |
|---|---|---|
| 2025-02-02 | Prohibitions (1–8), AI literacy<br>禁止性条款（1–8）、AI 素养 | No social scoring, manipulative practices, workplace emotion recognition<br>禁止社会评分、操纵性做法、工作场所情绪识别 |
| 2025-08-02 | GPAI obligations + governance<br>GPAI 义务 + 治理 | Upstream providers comply; you inherit artefacts/contracts<br>上游提供商负责合规；你继承相应的文档制品/合同 |
| **2026-08-02** | **Main applicability; AI Office enforcement**<br>**主体条款适用；AI 办公室开始执法** | Document requests, model evaluation, corrective measures, fines ([Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai))<br>文件调取、模型评估、纠正措施、罚款（[欧盟委员会](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)） |
| 2026-08 | Transparency (chatbot disclosure, content marking)<br>透明度（聊天机器人披露、内容标记） | UI must disclose AI interaction; marking Code of Practice exists<br>UI 必须披露正在与 AI 交互；关于内容标记的行为准则（Code of Practice）已经存在 |
| 2026-12-02 | "Nudification" ban; watermarking transition ends<br>「去衣化（nudification）」禁令；水印过渡期结束 | Content safety and provenance controls<br>内容安全和来源控制 |
| **2027-12-02** | Annex III high-risk (employment, credit, education, critical infra…)<br>附件 III 高风险（就业、信贷、教育、关键基础设施……） | If your agent decides anything about people: logging, human oversight, risk management, technical documentation<br>如果你的 Agent 会对人做出任何决定：日志记录、人工监督、风险管理、技术文档 |
| 2028-08-02 | Annex I product-embedded high-risk<br>附件 I 产品内嵌高风险 | Only for regulated products<br>仅适用于受监管产品 |

**Opinionated read:** the delay is a scheduling reprieve, not a scope reduction. Build **logging, human oversight and risk-management artefacts now** — the §2/§3.5 trace and audit investments *are* the compliance evidence. Note also the July 2026 Cybersecurity and AI action plan and planned EU model-evaluation capacity by 2027 ([Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)): expect third-party model evaluation in procurement.

**带观点的解读：** 这次推迟只是时间表上的缓刑，而不是范围的缩减。**现在就构建日志记录、人工监督和风险管理的制品**——§2/§3.5 中对 trace 和审计的投入*本身就是*合规证据。还要注意 2026 年 7 月的网络安全与 AI 行动计划，以及计划到 2027 年建成的欧盟模型评估能力（[欧盟委员会](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)）：预计采购中会出现第三方模型评估的要求。

### 7.2 NIST AI RMF and ISO/IEC 42001

**7.2 NIST AI RMF 与 ISO/IEC 42001**

**NIST AI RMF 1.0** (2023-01-26) plus the **Generative AI Profile** (NIST-AI-600-1, 2024-07-26); NIST states RMF 1.0 **is being revised** under the White House AI Action Plan, and released a Critical Infrastructure profile concept note on 2026-04-07 ([NIST](https://www.nist.gov/itl/ai-risk-management-framework), accessed 2026-10-18; [AI 600-1](https://doi.org/10.6028/NIST.AI.600-1)). Use it as a **control taxonomy** (Govern/Map/Measure/Manage) mapped to SOC 2. **[unsettled]** the revision will change vocabulary; don't hard-code clause numbers into contracts.

**NIST AI RMF 1.0**（2023-01-26）以及**生成式 AI 配置文件**（Generative AI Profile，NIST-AI-600-1，2024-07-26）；NIST 表示 RMF 1.0 **正在依据白宫 AI 行动计划进行修订**，并于 2026-04-07 发布了关键基础设施配置文件的概念说明（[NIST](https://www.nist.gov/itl/ai-risk-management-framework)，访问于 2026-10-18；[AI 600-1](https://doi.org/10.6028/NIST.AI.600-1)）。把它用作一套**控制分类体系**（Govern/Map/Measure/Manage），并映射到 SOC 2。**[unsettled]** 修订会改变术语；不要把条款编号硬编码进合同。

**ISO/IEC 42001:2023** specifies an AI Management System with PDCA-style continual improvement (51 pages, JTC 1/SC 42); pair with **ISO/IEC 42005:2025** for AI impact assessment ([ISO](https://www.iso.org/standard/42001), accessed 2026-10-18). This is the certification enterprise procurement is most likely to demand in 2027.

**ISO/IEC 42001:2023** 规定了一套采用 PDCA 式持续改进的 AI 管理体系（51 页，JTC 1/SC 42）；可搭配用于 AI 影响评估的 **ISO/IEC 42005:2025**（[ISO](https://www.iso.org/standard/42001)，访问于 2026-10-18）。这是 2027 年企业采购最有可能要求的认证。

### 7.3 SOC 2, licensing, agent registry

**7.3 SOC 2、许可与 Agent 注册表**

**SOC 2 Type II** stays the baseline; agent-specific additions are subprocessors covering model and sandbox vendors, retention/deletion for prompts and traces, change management for prompts and model versions, and access control on the eval/observability platform itself.

**SOC 2 Type II** 仍然是基线；Agent 特有的补充项包括：涵盖模型和沙箱厂商的子处理方（subprocessor）、提示词和 trace 的保留/删除、提示词和模型版本的变更管理，以及对评测/可观测性平台本身的访问控制。

**Licensing:** meter per run or per seat with **auditable** counters enforced at the gateway (the model must not be able to talk past a license check); derive per-tenant cost from `app.cost.usd` span attributes.

**许可：** 按运行次数或按席位计量，使用在网关处强制执行的**可审计**计数器（绝不能让模型靠「说服」绕过许可检查）；从 `app.cost.usd` span 属性推导每个租户的成本。

**Agent registry:** emerging but already visible in standards — OTel recommends provider-assigned agent IDs such as AWS Bedrock agent ARNs or GCP Agent Registry identifiers in `gen_ai.agent.id` ([agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), accessed 2026-10-18). Build an internal registry now: owner, business purpose, model + tools + data scopes, eval status, last review, risk tier. It is the first artefact auditors request. **[unsettled]** no dominant registry standard; expect convergence over 2027.

**Agent 注册表：** 尚在兴起，但已在标准中可见——OTel 建议在 `gen_ai.agent.id` 中使用提供商分配的 Agent ID，例如 AWS Bedrock Agent ARN 或 GCP Agent Registry 标识符（[Agent span](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)，访问于 2026-10-18）。现在就构建一个内部注册表：负责人、业务目的、模型 + 工具 + 数据范围、评测状态、上次评审时间、风险等级。这是审计人员最先索要的制品。**[unsettled]** 目前还没有占主导地位的注册表标准；预计会在 2027 年间逐步收敛。

---

## 8. Production-readiness checklist (38 items)

**8. 生产就绪检查清单（38 项）**

**Evaluation**

**评测**

1. Private eval set of ≥30 cases from real requests, versioned in git.

   由真实请求构建的私有评测集，至少 30 个用例，在 git 中做版本管理。

2. pass^k (k≥3) reported for every release alongside pass@1.

   每次发布都在报告 pass@1 的同时报告 pass^k（k≥3）。

3. Deterministic assertions preferred; judges only where ground truth is unavailable.

   优先使用确定性断言；只有在没有标准答案（ground truth）的地方才使用评审。

4. Every judge has a rubric, a 30–50 item human-labelled set, and a documented agreement score.

   每个评审都有评分标准、一个 30–50 条人工标注的样本集，以及一个有记录的一致率分数。

5. Trajectory checks (tools, args, policy, steps) exist for every multi-step agent.

   每个多步 Agent 都有轨迹检查（工具、参数、策略、步数）。

6. Cost and latency asserted in CI, not only quality.

   在 CI 中对成本和延迟做断言，而不只是质量。

7. Every production incident becomes a regression case within one sprint.

   每个生产事故都在一个迭代内变成一个回归用例。

**Observability**
8. OTel GenAI semconv adopted with a pinned version and one internal emission layer.
9. Every span carries tenant ID, agent ID/version, model, prompt version, cost.
10. Content capture is opt-in, redacted, short-TTL, access-logged.
11. Audit log is separate from debug traces and append-only.
12. Dashboards cover pass^k trend, cost per successful task, cache-hit rate, tool error rate, approval queue age.
13. Alerts fire on judge-score drift and refusal-rate spikes, not only 5xx.
14. OTLP/JSON export tested — no vendor lock on evidence.

**可观测性**
8. 已采用 OTel GenAI semconv，固定了版本，并且只有一个内部发出层。
9. 每个 span 都带有租户 ID、Agent ID/版本、模型、提示词版本、成本。
10. 内容采集需显式开启、经过脱敏、短 TTL、有访问日志。
11. 审计日志与调试 trace 分开，且仅追加。
12. 仪表盘覆盖 pass^k 趋势、每个成功任务的成本、缓存命中率、工具错误率、审批队列等待时长。
13. 告警会在评审分数漂移和拒答率激增时触发，而不只是 5xx。
14. 已测试 OTLP/JSON 导出——证据不被厂商锁定。

**Security**
15. Lethal-trifecta audit done per agent; at least one leg removed or gated.
16. Tools use least-privilege, short-lived credentials; no ambient secrets.
17. MCP servers allowlisted, digest-pinned, reviewed like code.
18. MCP auth uses audience-bound tokens with no token passthrough.
19. Tool output treated as untrusted data; no auto-execution of retrieved instructions.
20. Irreversible actions require human approval with a concrete action diff.
21. Code execution and browsing run in ephemeral, egress-restricted sandboxes with no cloud credentials.
22. Cross-tenant probes are automated tests, not code-review conventions.
23. Red-team corpus runs in CI and is refreshed regularly.
24. AI-BOM covers models, MCP servers, and agent packages.

**安全**
15. 已对每个 Agent 做过致命三要素审计；至少去掉或管控了其中一条腿。
16. 工具使用最小权限、短期有效的凭据；环境中没有隐式密钥。
17. MCP 服务器已列入白名单、按摘要固定版本、像代码一样经过审查。
18. MCP 认证使用绑定受众的 token，且没有 token 透传。
19. 工具输出被当作不可信数据；不自动执行检索到的指令。
20. 不可逆操作需要附带具体操作 diff 的人工审批。
21. 代码执行和浏览在临时性、出站受限且没有云凭据的沙箱中运行。
22. 跨租户探测是自动化测试，而不是代码审查惯例。
23. 红队语料在 CI 中运行，并定期刷新。
24. AI-BOM 覆盖模型、MCP 服务器和 Agent 包。

**Reliability**
25. Agent loop runs on a durable engine with replay, not an in-process loop.
26. Every tool call has an idempotency key persisted before invocation.
27. Timeouts are per-model/per-tool from measured p99; every run has a wall-clock deadline.
28. Circuit breakers exist per provider+model and per critical tool.
29. HITL is durable suspend/resume, never a blocked thread or held request.
30. Per-tenant rate limits and quotas protect interactive traffic from batch load.

**可靠性**
25. Agent 循环运行在支持回放的持久化引擎上，而不是进程内循环。
26. 每次工具调用都有一个在调用前持久化的幂等键。
27. 超时按模型/按工具依据实测 p99 设置；每次运行都有挂钟截止时间。
28. 按提供商+模型以及按关键工具设有熔断器。
29. HITL 是持久化的挂起/恢复，绝不是阻塞的线程或挂住的请求。
30. 按租户的速率限制和配额保护交互式流量不受批处理负载影响。

**Cost, tenancy, governance**
31. Hard token/$ caps per run, user and tenant enforced at the gateway; cache-hit rate is a monitored SLO.
32. Per-tenant data, credential, memory/index and cache-accounting isolation documented and tested.
33. Agent registry entry exists (owner, purpose, model, tools, data scopes, risk tier, review date).
34. EU AI Act classification recorded per agent with logging/oversight evidence mapped to obligations.
35. NIST AI RMF / ISO 42001 control mappings exist for procurement questionnaires.
36. Release includes a model/prompt eval gate and a documented rollback.
37. Runbooks exist for provider outage, runaway loop, injection incident, cross-tenant suspicion, cost spike.
38. Cost attribution per tenant/feature reconciles monthly against invoices.

**成本、租户与治理**
31. 在网关处对每次运行、每个用户和每个租户强制执行硬性 token/$ 上限；缓存命中率是一项受监控的 SLO。
32. 按租户的数据、凭据、记忆/索引和缓存计量隔离均有文档记录并经过测试。
33. 存在 Agent 注册表条目（负责人、目的、模型、工具、数据范围、风险等级、评审日期）。
34. 为每个 Agent 记录欧盟 AI 法案分类，并把日志/监督证据映射到对应义务。
35. 为采购问卷准备了 NIST AI RMF / ISO 42001 控制映射。
36. 发布流程包含模型/提示词评测关卡和有文档记录的回滚方案。
37. 针对提供商故障、失控循环、注入事故、疑似跨租户、成本激增均有运行手册（runbook）。
38. 按租户/功能的成本归属每月与发票对账。

---

## 9. Top 10 anti-patterns

**9. 十大反模式**

1. **Demo-driven development** — shipping what looked good in five cherry-picked chats; pass^k collapses on trials 6–8 ([τ-bench](https://arxiv.org/abs/2406.12045)).

   **演示驱动开发**——上线的是在五次精挑细选的对话中看起来不错的东西；pass^k 在第 6–8 次试验时崩溃（[τ-bench](https://arxiv.org/abs/2406.12045)）。

2. **Leaderboard-as-quality-proof** — SWE-bench/GAIA numbers offered as evidence your product is safe or correct.

   **把排行榜当质量证明**——拿 SWE-bench/GAIA 的分数当作你的产品安全或正确的证据。

3. **Uncalibrated judge as sole oracle** — documented position/verbosity/self-enhancement biases drift your metric silently ([MT-Bench](https://arxiv.org/abs/2306.05685)).

   **把未校准的评审当作唯一的判定依据**——已有记录的位置/冗长/自我增强偏差会让你的指标悄无声息地漂移（[MT-Bench](https://arxiv.org/abs/2306.05685)）。

4. **Blocking a thread for human approval** — ties up workers, breaks on deploy, loses state ([Temporal patterns](https://docs.temporal.io/evaluate/use-cases-design-patterns)).

   **为人工审批阻塞线程**——占用工作者、部署时中断、丢失状态（[Temporal 模式](https://docs.temporal.io/evaluate/use-cases-design-patterns)）。

5. **Blind retries on non-idempotent tools** — the duplicate-refund incident.

   **对非幂等工具盲目重试**——重复退款事故就是这么来的。

6. **One agent with private data, untrusted input and egress** — the lethal trifecta, shipped deliberately ([Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)).

   **同一个 Agent 同时拥有私有数据、不可信输入和出站能力**——等于刻意上线了致命三要素（[Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)）。

7. **Secrets in the prompt or system instructions** — they surface in traces, logs and output; resolve secrets inside the tool boundary ([OWASP 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)).

   **把密钥放在提示词或系统指令里**——它们会出现在 trace、日志和输出中；应在工具边界内解析密钥（[OWASP 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)）。

8. **Unbounded loops with no step/budget cap** — denial of wallet; OWASP 2026 raised Unbounded Consumption four places ([preface](https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md)).

   **没有步数/预算上限的无界循环**——钱包耗尽；OWASP 2026 把 Unbounded Consumption 上调了四位（[前言](https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md)）。

9. **Tenancy as a row filter only** — no per-tenant queues, keys, caches or memory namespaces.

   **租户隔离只靠行过滤**——没有按租户的队列、密钥、缓存或记忆命名空间。

10. **Vacuum observability** — capturing everything with no retention or access policy: a PII liability and an audit finding that still cannot explain failures because content is unlabelled.

    **真空式可观测性**——什么都采集，却没有保留期或访问策略：既是 PII 负债，又是一条审计发现项，而且由于内容没有标注，仍然无法解释失败。

---

## 10. Established vs unsettled, and what to verify

**10. 已确立与未确定的内容，以及需要核实什么**

**Established:** OTel-style tracing as the model; prompt-caching mechanics and multipliers; durable-execution patterns for long loops; idempotency keys + backoff + circuit breakers; batch APIs; least privilege and sandbox isolation; eval datasets plus regression suites; the EU AI Act dates and the 2026 Omnibus delay; ISO/IEC 42001 as an AIMS.

**已确立：** 以 OTel 风格的追踪作为模型；提示词缓存的机制和价格倍率；面向长循环的持久化执行模式；幂等键 + 退避 + 熔断器；批处理 API；最小权限和沙箱隔离；评测数据集加回归测试套件；欧盟 AI 法案的各项日期以及 2026 年 Omnibus 的推迟；ISO/IEC 42001 作为一套 AI 管理体系（AIMS）。

**Unsettled / verify before committing:**

**未确定 / 投入之前需要核实：**

- **OTel GenAI semconv stability** — all agent spans are `Development`; names will change. Pin, wrap, expect migration ([spec](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)).

  **OTel GenAI semconv 的稳定性**——所有 Agent span 都处于 `Development` 状态；名称会变。固定版本、封装起来、做好迁移准备（[规范](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)）。

- **Prompt-injection defences** — capability separation, dual-LLM and "rule of two" are promising, not proven at enterprise scale. Never promise customers "injection-proof".

  **提示词注入防御**——能力隔离、双 LLM 以及「rule of two」都很有前景，但尚未在企业规模上得到验证。绝不要向客户承诺「免疫注入」。

- **Agentic Top 10 IDs/scope** — use as taxonomy; verify ASI numbering against the published PDF.

  **Agentic Top 10 的 ID/范围**——作为分类体系使用；对照已发布的 PDF 核实 ASI 编号。

- **Batch discounts and cache pricing** — percentages here are as documented on 2026-10-18; re-check pricing pages before financial modelling.

  **批处理折扣和缓存定价**——此处的百分比以 2026-10-18 的文档为准；做财务建模前请重新查看定价页面。

- **NIST AI RMF revision** — vocabulary may change; keep control mapping abstract.

  **NIST AI RMF 修订**——术语可能变化；让控制映射保持抽象。

- **WebArena/AgentBench leaderboards** — not re-verified for 2026; orientation only.

  **WebArena/AgentBench 排行榜**——未针对 2026 年重新核实；仅供定位参考。

- **Cost-reduction "~" numbers** — practitioner estimates; measure on your own traces.

  **成本降低方面带「~」的数字**——从业者估算；请在你自己的 trace 上实测。

- **Agent identity/authorisation standards** — converging (MCP OAuth 2.1, AAIF governance) but not settled; design for swap-ability.

  **Agent 身份/授权标准**——正在收敛（MCP OAuth 2.1、AAIF 治理）但尚未定型；设计时要考虑可替换性。

---

## Appendix: primary sources (all accessed 2026-10-18)

**附录：一手资料（均访问于 2026-10-18）**

**Evals:** [τ-bench](https://arxiv.org/abs/2406.12045) · [SWE-bench](https://github.com/SWE-bench/SWE-bench) · [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) · [Terminal-Bench](https://www.tbench.ai/) · [GAIA](https://arxiv.org/abs/2311.12983) · [WebArena](https://arxiv.org/abs/2307.13854) · [AgentBench](https://arxiv.org/abs/2307.10928) · [LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) · [RouteLLM](https://arxiv.org/abs/2406.18665)

**评测：** [τ-bench](https://arxiv.org/abs/2406.12045) · [SWE-bench](https://github.com/SWE-bench/SWE-bench) · [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) · [Terminal-Bench](https://www.tbench.ai/) · [GAIA](https://arxiv.org/abs/2311.12983) · [WebArena](https://arxiv.org/abs/2307.13854) · [AgentBench](https://arxiv.org/abs/2307.10928) · [LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) · [RouteLLM](https://arxiv.org/abs/2406.18665)

**Observability:** [OTel GenAI repo](https://github.com/open-telemetry/semantic-conventions-genai) · [OTel GenAI docs](https://opentelemetry.io/docs/specs/semconv/gen-ai/) · [LangSmith](https://docs.langchain.com/langsmith/observability) · [Langfuse](https://langfuse.com/docs) · [Braintrust](https://www.braintrust.dev/docs) · [Arize Phoenix](https://arize.com/docs/phoenix) · [W&B Weave](https://docs.wandb.ai/weave) · [LangWatch](https://langwatch.ai)

**可观测性：** [OTel GenAI 仓库](https://github.com/open-telemetry/semantic-conventions-genai) · [OTel GenAI 文档](https://opentelemetry.io/docs/specs/semconv/gen-ai/) · [LangSmith](https://docs.langchain.com/langsmith/observability) · [Langfuse](https://langfuse.com/docs) · [Braintrust](https://www.braintrust.dev/docs) · [Arize Phoenix](https://arize.com/docs/phoenix) · [W&B Weave](https://docs.wandb.ai/weave) · [LangWatch](https://langwatch.ai)

**Security:** [OWASP LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) · [OWASP source](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final) · [OWASP Agentic 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · [AIBOM](https://github.com/GenAI-Security-Project/aibom-generator) · [Lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) · [MCP security](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) · [MCP → AAIF](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)

**安全：** [OWASP LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) · [OWASP 源文件](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final) · [OWASP Agentic 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · [AIBOM](https://github.com/GenAI-Security-Project/aibom-generator) · [致命三要素](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) · [MCP 安全](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · [MCP 授权](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) · [MCP → AAIF](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)

**Reliability/infra:** [Temporal](https://docs.temporal.io/evaluate/use-cases-design-patterns) · [Inngest](https://www.inngest.com/platform/durable-execution) · [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) · [Circuit Breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) · [Backoff/jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) · [E2B](https://docs.e2b.dev) · [Daytona](https://www.daytona.io/docs/en/)

**可靠性/基础设施：** [Temporal](https://docs.temporal.io/evaluate/use-cases-design-patterns) · [Inngest](https://www.inngest.com/platform/durable-execution) · [Lambda 配额](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) · [熔断器](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) · [退避/抖动](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) · [E2B](https://docs.e2b.dev) · [Daytona](https://www.daytona.io/docs/en/)

**Cost/latency:** [Anthropic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) · [OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching) · [Anthropic batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing) · [OpenAI batch](https://developers.openai.com/api/docs/guides/batch) · [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [Budget caps](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/)

**成本/延迟：** [Anthropic 缓存](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) · [OpenAI 缓存](https://developers.openai.com/api/docs/guides/prompt-caching) · [Anthropic 批处理](https://platform.claude.com/docs/en/build-with-claude/batch-processing) · [OpenAI 批处理](https://developers.openai.com/api/docs/guides/batch) · [上下文工程](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [预算上限](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/)

**Governance:** [EU Commission AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) · [AI Act text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689) · [Omnibus text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744) · [Morgan Lewis](https://www.morganlewis.com/zh-cn/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know) · [GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) · [NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1) · [ISO/IEC 42001](https://www.iso.org/standard/42001)

**治理：** [欧盟委员会 AI 法案页面](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) · [AI 法案文本](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689) · [Omnibus 文本](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744) · [Morgan Lewis](https://www.morganlewis.com/zh-cn/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know) · [GPAI 行为准则](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) · [NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1) · [ISO/IEC 42001](https://www.iso.org/standard/42001)
