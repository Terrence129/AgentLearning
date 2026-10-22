# Week 8 — Security, governance, cost, reliability

**第 8 周 — 安全、治理、成本与可靠性**

Assume the model **will** be manipulated. Design so that it does not matter.

假设模型**一定会**被操纵。把系统设计成即便如此也无关紧要。

## 1. Why this week exists

**1. 为什么要有这一周**

Prompt injection is unsolved, so the security boundary cannot be the prompt — it has to be the architecture around the model. If the agent can read private data, read untrusted content *and* send data outward, an attacker who controls one document can exfiltrate everything; if the model can choose paths, commands and models freely, a jailbreak becomes RCE or a denial-of-wallet incident. This week builds the confinement layer: untrusted content is data, tools run in a sandbox with approvals, authority only narrows, audit is append-only, quotas are per tenant, and routing fails safe.

提示词注入至今没有解决，因此安全边界不能是提示词——它必须是模型周围的架构。如果 Agent 既能读取私有数据、又能读取不可信内容、*还*能向外发送数据，那么控制了一份文档的攻击者就能把一切都窃取出去；如果模型可以随意选择路径、命令和模型，一次越狱就会演变成远程代码执行（RCE）或「钱包拒绝服务」（denial-of-wallet）事故。本周构建的是约束层：不可信内容只是数据，工具在带审批的沙箱中运行，权限只会收窄，审计只能追加，配额按租户划分，路由在失败时保持安全。

## 2. Prerequisites & time budget

**2. 前置条件与时间预算**

- **8–10 hours** (security work rewards a second pass on the tests).

  **8–10 小时**（安全工作值得把测试再过第二遍）。

- Green: weeks 1–2 at minimum (`Tool`, `ToolRegistry` and the provider seam are used by this lab); weeks 3–7 help but are not required to pass `tests/week08`.

  通过（变绿）：至少第 1–2 周（本实验（lab）会用到 `Tool`、`ToolRegistry` 和 provider 接缝（seam））；第 3–7 周有帮助，但通过 `tests/week08` 并不要求它们。

- Read first: [`docs/research/03-production-evals-ops.md`](../../docs/research/03-production-evals-ops.md) §3 (threat model, MCP hardening, sandbox/audit/red team), §4.4 (multi-tenant isolation), §5 (cost/latency levers); [`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.2 (authority intersection) and §4.4 (budgeted routing).

  先读：[`docs/research/03-production-evals-ops.md`](../../docs/research/03-production-evals-ops.md) §3（威胁模型、MCP 加固、沙箱/审计/红队）、§4.4（多租户隔离）、§5（成本/延迟的调节杠杆）；[`docs/research/05-sendos-concept-map.md`](../../docs/research/05-sendos-concept-map.md) §4.2（权限交集）和 §4.4（受预算约束的路由）。

- Also read the OWASP GenAI Top 10 2026 rows for prompt injection, excessive agency and unbounded consumption (links in research 03 §3.1).

  另外请阅读 OWASP GenAI Top 10 2026 中关于提示词注入、过度代理（excessive agency）和无限制消耗（unbounded consumption）的条目（链接见研究文档 03 的 §3.1）。

## 3. The spec

**3. 规格说明**

Implement everything under `agentlab/guard/`. `errors.py` and `attacks.py` are provided; the red-team corpus is **data** — do not weaken it, extend it.

实现 `agentlab/guard/` 下的所有内容。`errors.py` 和 `attacks.py` 已提供；红队语料是**数据**——不要削弱它，而要扩充它。

### `agentlab/guard/injection.py` — untrusted content is data

**`agentlab/guard/injection.py` — 不可信内容只是数据**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `wrap_untrusted(content, source)` | delimit + label untrusted content; escape delimiter spoofing; strip zero-width characters<br>为不可信内容加上分隔符和标签；转义伪造的分隔符；去除零宽字符 |
| `scan_injection(text)` | normalized (NFKC + casefold) rule scan; findings sorted by position; categories at least instruction override, role hijack, prompt exfiltration, tool abuse, command execution, exfiltration, hidden content, encoded payloads; benign text has no findings<br>归一化（NFKC + casefold）后的规则扫描；发现项按位置排序；类别至少包括指令覆盖、角色劫持、提示词窃取、工具滥用、命令执行、数据外泄、隐藏内容、编码载荷；良性文本没有任何发现项 |
| `screen_untrusted(text, source)` | risk = max severity; `allowed = risk != "high"`; always returns the wrapped (sanitized) form<br>风险 = 最高严重程度；`allowed = risk != "high"`；始终返回包装后（已清洗）的形式 |
| `build_guarded_messages(system, user, untrusted, sources)` | one system message stating the instruction hierarchy, user turn verbatim, each untrusted item as labelled data; source-length mismatch raises `ValueError`<br>一条说明指令层级的系统消息，用户轮次原样保留，每个不可信条目都作为带标签的数据；来源数量不匹配时抛出 `ValueError` |
| `vet_output(text, secrets)` | redact secret leaks, external markdown images, data-channel URLs, credential-shaped strings; `reasons` sorted; clean text unchanged<br>遮盖泄露的密钥、外部 markdown 图片、数据通道 URL、形似凭据的字符串；`reasons` 排好序；干净的文本保持不变 |
| `assess_lethal_trifecta(profile, mitigations)` | 3 legs ⇒ critical; 2 ⇒ elevated; 3 legs with no mitigation ⇒ **blocked** with required controls; known mitigation unblocks but risk stays critical; unknown mitigation raises `ValueError`<br>三条腿 ⇒ 严重（critical）；两条 ⇒ 升高（elevated）；三条腿且无缓解措施 ⇒ **阻断**，并给出所需的控制措施；已知的缓解措施可以解除阻断，但风险仍为严重；未知的缓解措施会抛出 `ValueError` |

### `agentlab/guard/sandbox.py` — confine execution

**`agentlab/guard/sandbox.py` — 约束执行**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `resolve_sandbox_path(raw, allowed_roots)` | URL-decode once, then reject empty/absolute/UNC/NUL/`..` paths; resolve and require containment in an allowed root; `PathNotAllowed` otherwise<br>先做一次 URL 解码，然后拒绝空路径/绝对路径/UNC/NUL/`..` 路径；解析路径并要求其位于某个允许的根目录之内；否则抛出 `PathNotAllowed` |
| `read_text_limited(path, max_bytes)` | refuse oversize files before loading them (`SandboxLimitExceeded`); negative/zero limit raises `ValueError`<br>在加载之前就拒绝超大文件（`SandboxLimitExceeded`）；限制为负数或零时抛出 `ValueError` |
| `run_command(argv, allowed_commands, ...)` | empty argv `ValueError`; command must be allowlisted (`ToolNotAllowed`); no shell; hard timeout (`SandboxTimeout`); output truncated; non-zero exit is data<br>argv 为空时抛出 `ValueError`；命令必须在白名单中（`ToolNotAllowed`）；不使用 shell；硬超时（`SandboxTimeout`）；输出会被截断；非零退出码是数据 |
| `action_hash(tool, arguments)` | canonical SHA-256 binding tool **and** arguments<br>规范化的 SHA-256，同时绑定工具**和**参数 |
| `ApprovalLedger.consume(token, now)` | expiry and at-most-once replay refused with `ApprovalRequired`<br>过期以及违反最多一次的重放都会以 `ApprovalRequired` 拒绝 |
| `require_allowed_tool` / `require_approval` | allowlist check; read tools no-op, write tools need a token matching tenant + exact action, then consume it<br>白名单检查；读工具不做任何操作，写工具需要一个与租户及确切动作相匹配的令牌，然后消费掉它 |

### `agentlab/guard/authority.py` — deny by default, never widen

**`agentlab/guard/authority.py` — 默认拒绝，永不放宽**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `effective_authority(tenant_id, boundaries, model_claims)` | intersection over boundaries whose tenant matches (or is platform-wide `None`); no applicable boundary ⇒ no grants; model claims never add grants and are recorded in `denied_claims`; empty tenant raises `ValueError`<br>对租户匹配（或为全平台范围的 `None`）的边界取交集；没有适用的边界 ⇒ 没有任何授权；模型声称的权限永远不会增加授权，并会被记录在 `denied_claims` 中；租户为空时抛出 `ValueError` |
| `EffectiveAuthority.allows` / `.require` / `.delegate` | membership; raises `AuthorizationError`; delegation must be a non-empty subset of current grants<br>成员判断；抛出 `AuthorizationError`；委派必须是当前授权的非空子集 |
| `reject_credential_passthrough` / `outbound_headers` | caller credentials (case-insensitive: `authorization`, `cookie`, `x-api-key`, …) are refused/ stripped; upstream uses its own token; empty upstream token raises `ValueError`<br>调用方的凭据（不区分大小写：`authorization`、`cookie`、`x-api-key` 等）会被拒绝/剥离；上游使用自己的令牌；上游令牌为空时抛出 `ValueError` |

### `agentlab/guard/audit.py` — evidence you cannot edit

**`agentlab/guard/audit.py` — 无法篡改的证据**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `AuditRecord` | immutable row with before/after evidence, correlation id, decision, hash chain fields; `to_dict` / `from_dict` round-trip<br>不可变的记录行，包含前后对比证据、关联 id、决策和哈希链字段；`to_dict` / `from_dict` 可往返转换 |
| `AuditLog.append` | monotonic seq from 1, clock-injected ts, hash chained to the previous row, JSONL flushed immediately when file-backed; only `allowed`/`denied` decisions<br>从 1 开始单调递增的序号，由注入时钟生成的时间戳，与上一行链接的哈希，以文件为后端时立即刷新 JSONL；决策只能是 `allowed`/`denied` |
| `AuditLog.update` / `.delete` | always raise `AuditViolation`, record the attempt, change nothing (file included)<br>总是抛出 `AuditViolation`，记录这次尝试，不做任何改动（包括文件） |
| `AuditLog.records` / `.find` / `.attempts` | append order; correlation-id grouping; rejected mutation log<br>按追加顺序；按关联 id 分组；被拒绝的修改尝试日志 |
| `AuditLog.verify_integrity()` | seq contiguous from 1, prev-hash chain intact, stored hashes match recomputation (detects tampering)<br>序号从 1 开始连续，前一哈希链完整，存储的哈希与重新计算的结果一致（可检测篡改） |

### `agentlab/guard/ratelimit.py` + `routing.py` — quotas and fail-safe routing

**`agentlab/guard/ratelimit.py` + `routing.py` — 配额与失败安全的路由**

| Item<br>条目 | Contract<br>契约 |
|---|---|
| `TenantQuotaLimiter.check` / `.charge` / `.status` | fixed-window per-tenant request/token/USD budgets; `check` does not consume; `charge` is atomic and refuses without consuming; empty tenant raises `ValueError`<br>按租户的固定窗口请求数/token/美元预算；`check` 不消耗额度；`charge` 是原子的，拒绝时不消耗额度；租户为空时抛出 `ValueError` |
| `estimate_call_usd` | `None` when price is unknown (never zero)<br>价格未知时返回 `None`（绝不返回零） |
| `CostAwareRouter.select` | excludes bad task type, reliability, latency, per-request and remaining budget, and unknown price; ranks by explicit `preferred`, then cost, then name; no candidate ⇒ `RoutingError`<br>排除任务类型不符、可靠性不足、延迟过高、超出单次请求预算和剩余预算、以及价格未知的候选；先按显式的 `preferred` 排序，再按成本，最后按名称；没有候选 ⇒ `RoutingError` |
| `CostAwareRouter.complete` | fallback on **transient** `ProviderError` only; terminal errors and `RequestCancelled` propagate; re-checks budget per attempt and charges on success; attempts capped<br>仅在**瞬时性**的 `ProviderError` 上回退；终止性错误和 `RequestCancelled` 直接向上传播；每次尝试都重新检查预算，成功时计费；尝试次数有上限 |

### `agentlab/guard/attacks.py` — the corpus (provided)

**`agentlab/guard/attacks.py` — 攻击语料（已提供）**

16 attacks across 10 categories, each naming its target guard. `tests/week08/test_attacks.py` asserts **every** one is blocked or detected; the coverage test fails if a category disappears. Add cases, never remove them.

涵盖 10 个类别的 16 种攻击，每种都指明了其针对的防护。`tests/week08/test_attacks.py` 断言**每一种**都会被阻断或检测到；如果某个类别消失，覆盖率测试就会失败。只能增加用例，绝不能删除。

## 4. Acceptance criteria

**4. 验收标准**

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week08 -m week -q   # must pass
.\.venv\Scripts\ruff.exe check agentlab/guard                   # must be clean
```

```bash
# macOS / Linux
uv run pytest tests/week08 -m week -q   # must pass
uv run ruff check agentlab/guard        # must be clean
```

Then produce the **lab artifact** (not tested, but the point of the week):

然后产出**实验产物**（不受测试覆盖，但这才是本周的重点）：

1. A `projects/security/SECURITY.md` threat model for one of your agents: lethal-trifecta audit, data flows, controls, residual risks, and what you would *not* claim to a customer.

   为你的某个 Agent 编写一份 `projects/security/SECURITY.md` 威胁模型：致命三要素（lethal trifecta）审计、数据流、控制措施、残余风险，以及你*不会*向客户承诺的内容。

2. A before/after table: run the corpus against an unguarded mini-agent (no sandbox, no screen, no approvals), then against the guarded version; every attack row must move from "succeeds" to "blocked".

   一张前后对比表：先用攻击语料攻击一个无防护的迷你 Agent（无沙箱、无筛查、无审批），再攻击有防护的版本；每一行攻击都必须从「成功」变为「被阻断」。

3. One write action wired end-to-end: proposal → approval → sandbox → audit row with before/after evidence and one correlation id.

   端到端接通一个写操作：提案 → 审批 → 沙箱 → 审计记录行，并带有前后对比证据和一个关联 id。

## 5. Hints (progressive)

**5. 提示（循序渐进）**

1. **Re-read** research 03 §3.2's threat table. Every row has an *architectural* control; regexes and prompt warnings are the weakest layer, not the design.

   **重读**研究文档 03 §3.2 中的威胁表。每一行都有一个*架构层面*的控制措施；正则表达式和提示词警告是最薄弱的一层，而不是设计本身。

2. Detection is not defence: `screen_untrusted` refusing high-risk content is the last line, while delimiting, hierarchy, least privilege and approvals are what hold when the detector misses.

   检测不等于防御：`screen_untrusted` 拒绝高风险内容只是最后一道防线，而在检测器漏判时真正能守住的是分隔、层级、最小权限和审批。

3. Decode before you validate paths (`urllib.parse.unquote`), normalise separators, then `Path.resolve` and `is_relative_to` — checking the raw string misses `%2e%2e%2f`.

   在校验路径之前先解码（`urllib.parse.unquote`），统一分隔符，然后再 `Path.resolve` 和 `is_relative_to`——只检查原始字符串会漏掉 `%2e%2e%2f`。

4. Approval binding is a hash of the **action**, not the tool name: approve `issue_refund($10)` and the token must not authorise `issue_refund($10_000)`. The ledger is what makes replay impossible.

   审批绑定的是**动作**的哈希，而不是工具名称：批准了 `issue_refund($10)`，这个令牌就绝不能授权 `issue_refund($10_000)`。让重放变得不可能的是账本。

5. Intersection starts from "nothing" and can only lose grants. Adding a boundary (or a model claim) that widens the result means you built a union.

   交集从「什么都没有」开始，只会失去授权。如果加入一个边界（或一个模型声称的权限）反而让结果变宽，说明你实现的是并集。

6. Hash chains: include `prev_hash` in the hashed payload, otherwise deleting a middle row is undetectable.

   哈希链：要把 `prev_hash` 包含在被哈希的载荷中，否则删除中间的一行将无法被检测到。

7. Routing: `price is None` is not "free"; it is "unverifiable", and unverifiable budget must exclude the candidate. Cancellation is a terminal signal, never a retry.

   路由：`price is None` 不是「免费」，而是「无法验证」，无法验证的预算必须把该候选排除。取消是终止信号，绝不能重试。

## 6. Debugging guide

**6. 调试指南**

| Symptom<br>症状 | Likely cause<br>可能原因 |
|---|---|
| Traversal test passes with `..` but encoded form fails<br>路径穿越测试在使用 `..` 时通过，但编码形式却失败 | validation ran on the raw string before `unquote` (or only checked `Path.parts` on the un-decoded text)<br>校验在 `unquote` 之前就对原始字符串执行了（或者只对未解码的文本检查了 `Path.parts`） |
| Timed-out subprocess hangs the suite<br>超时的子进程让测试套件卡住 | `subprocess.run` without `timeout=`, or the timeout exception was swallowed instead of raised as `SandboxTimeout`<br>`subprocess.run` 没有传 `timeout=`，或者超时异常被吞掉了，而没有作为 `SandboxTimeout` 抛出 |
| Replay test only passes on the second call<br>重放测试只在第二次调用时才通过 | the ledger records the ticket *after* the approval checks, but the token is re-created per call with a fresh ticket id in the test — use one token object and one ledger<br>账本在审批检查*之后*才记录票据，但测试中每次调用都用新的票据 id 重新创建了令牌——应使用同一个令牌对象和同一个账本 |
| `effective_authority` returns grants for another tenant<br>`effective_authority` 返回了另一个租户的授权 | boundaries were unioned instead of filtered by `tenant_id in (None, tenant_id)`<br>对边界取了并集，而不是按 `tenant_id in (None, tenant_id)` 进行过滤 |
| Audit reload fails `verify_integrity`<br>审计日志重新加载后 `verify_integrity` 失败 | the hash payload changed between append and verify (e.g. dict ordering, or `before`/`after` stored as tuples after JSON round-trip)<br>哈希载荷在追加与校验之间发生了变化（例如字典顺序，或 `before`/`after` 以元组存储，经过 JSON 往返后变了） |
| Fallback fires on a validation error<br>校验错误触发了回退 | the `except ProviderError` branch checked only `isinstance`, not `exc.retryable`; terminal errors must re-raise<br>`except ProviderError` 分支只检查了 `isinstance`，没有检查 `exc.retryable`；终止性错误必须重新抛出 |
| A quota test fails at exactly the limit<br>配额测试恰好在上限处失败 | "requests > max" is the rule; `>=` rejects the last allowed request. Same for token/USD ceilings<br>规则是「requests > max」；用 `>=` 会拒绝最后一个本应允许的请求。token/美元上限同理 |

## 7. SendOS bridge

**7. 与 SendOS 的衔接**

Read-only reference (SendOS repo): the governance controls this week miniatures.

只读参考（SendOS 仓库）：本周以迷你形式复刻的治理控制措施。

- `.../Domain/Authority/EffectiveAuthority.cs` and `.../Application/Authority/AuthoritySources.cs` — the nine-source intersection; authority discovery vs permission.

  `.../Domain/Authority/EffectiveAuthority.cs` 和 `.../Application/Authority/AuthoritySources.cs` —— 九个来源的交集；权限发现与许可之别。

- `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` — catalogue merge with published-wins; undeclared capabilities are not invokable.

  `.../CapabilityRegistry/CapabilityCatalogueAssembler.cs:34-120` —— 目录合并时以已发布版本为准；未声明的能力不可调用。

- `.../Properties/AuthorityIntersectionNarrowingPropertyTests.cs` and `ApprovalBindingAtMostOncePropertyTests.cs` — the invariants, as property tests.

  `.../Properties/AuthorityIntersectionNarrowingPropertyTests.cs` 和 `ApprovalBindingAtMostOncePropertyTests.cs` —— 以属性测试形式表达的不变量。

- `apps/Send.Model.Adapter/src/.../Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs` and `.../Handlers/CompletionHandler.cs:60-210` — invalid never surfaces as valid; router excludes unverifiable budgets; cancellation never retries.

  `apps/Send.Model.Adapter/src/.../Structured/{StructuredCompletionHandler,JsonSchemaValidator}.cs` 和 `.../Handlers/CompletionHandler.cs:60-210` —— 无效结果永远不会以有效的面目出现；路由器排除无法验证的预算；取消永不重试。

- `docs/architecture/governance-architecture.md:223-273` — the pre/post-LLM "governance sandwich" diagram.

  `docs/architecture/governance-architecture.md:223-273` —— LLM 调用前后的「治理三明治」示意图。

Answer in your weekly notes:

在你的每周笔记中回答：

1. Which of the nine authority sources could a model plausibly influence, and how does the intersection make that harmless? Where does your mini-version diverge?

   九个权限来源中，哪些可能被模型影响？交集是如何让这种影响变得无害的？你的迷你版本在哪些地方与之不同？

2. SendOS records execution origin (real/simulated) per connector result. Why is origin an audit concern as well as a debugging one, and where would you stamp it in your design?

   SendOS 会为每个连接器结果记录执行来源（真实/模拟）。为什么来源既是调试问题，也是审计问题？在你的设计中，你会在哪里打上这个标记？

3. The licence/quota check lives at ingress. What breaks if the model can talk past it, and which of your week 8 controls would catch the resulting spend?

   许可证/配额检查位于入口处。如果模型能绕过它，会有什么东西出问题？你在第 8 周构建的哪项控制措施能拦住由此产生的开销？

## 8. Stretch (optional)

**8. 拓展（可选）**

- **Threat-model review of SendOS's approval path**: one page, using this week's vocabulary (binding, at-most-once, expiry, narrowing, audit evidence). Send it to a senior engineer for critique; note what they disagree with.

  **对 SendOS 审批路径做威胁模型评审**：写一页，使用本周的术语（绑定、最多一次、过期、收窄、审计证据）。把它发给一位资深工程师请其批评指正；记下他们不同意的地方。

- **Wire the guard into the loop**: a mini red-team runner that executes the corpus against a `MockProvider` agent, records a `guardrail_block` trace event per attack, and writes a before/after markdown table — the same shape as the week 7 report.

  **把防护接入循环**：编写一个迷你红队运行器，用攻击语料攻击一个基于 `MockProvider` 的 Agent，为每次攻击记录一个 `guardrail_block` trace 事件，并写出一张前后对比的 markdown 表格——形式与第 7 周的报告相同。

## 9. Reflection (weekly review)

**9. 反思（每周复盘）**

1. **Conceptual:** why is "remove a leg of the lethal trifecta" a stronger control than "detect the injection"? Give an attack your `scan_injection` rules would miss and explain which other layer still stops it.

   **概念层面：** 为什么「移除致命三要素中的一条腿」是比「检测注入」更强的控制措施？举一个你的 `scan_injection` 规则会漏掉的攻击，并解释是哪一层仍然能阻止它。

2. **Architectural:** where is the enforcement boundary in your design — in the tool wrapper, the model adapter, or a central policy service? What are the costs of each placement in latency, blast radius and auditability?

   **架构层面：** 在你的设计中，强制执行的边界在哪里——在工具包装层、模型适配器，还是一个集中的策略服务？每种放置方式在延迟、影响范围和可审计性方面各有什么代价？

3. **Transfer:** name one production system you run that trusts model-adjacent input (an LLM feature, a webhook, a scheduled job). Which of this week's five controls (untrusted-data handling, sandbox, authority intersection, append-only audit, per-tenant quota) does it lack, and what is the smallest first fix?

   **迁移应用：** 说出一个你运行的、信任与模型相关输入的生产系统（一个 LLM 功能、一个 webhook、一个定时任务）。它缺少本周五项控制措施（不可信数据处理、沙箱、权限交集、只追加审计、按租户配额）中的哪一项？最小的第一步修复是什么？
