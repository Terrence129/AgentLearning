# Week 8 Quiz — Security, Governance, Cost, Reliability

**第 8 周测验 — 安全、治理、成本与可靠性**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** Indirect prompt injection arrives via:

间接提示词注入是通过什么途径进来的：

- A) The user typing "ignore previous instructions"

  用户输入「忽略之前的指令」

- B) Content the agent reads — web pages, files, tool results, emails

  Agent 读取的内容——网页、文件、工具结果、电子邮件

- C) A malicious API key

  一个恶意的 API key

- D) A malformed JSON schema

  一个格式错误的 JSON schema

**Q2.** The "lethal trifecta" is:

「致命三要素（lethal trifecta）」是指：

- A) Three agents in one squad

  一个小队（squad）里有三个 Agent

- B) Private data + untrusted content + external communication in the same agent

  同一个 Agent 同时具备私有数据 + 不可信内容 + 对外通信

- C) Three retries without backoff

  不带退避的三次重试

- D) Read, write and delete tools together

  读、写、删除工具同时存在

**Q3.** Effective authority should be computed as:

有效权限应当如何计算：

- A) The union of all grants so the agent is never blocked

  取所有授权的并集，让 Agent 永远不会被阻拦

- B) The intersection over independent grants, deny-by-default

  对各个独立授权取交集，默认拒绝

- C) Whatever the model proposes

  模型提议什么就是什么

- D) The last grant applied

  以最后应用的授权为准

**Q4.** The safest default for an autonomous system is:

对于自主系统，最安全的默认设置是：

- A) Allow, then audit

  先允许，再审计

- B) Deny by default; require explicit grants

  默认拒绝；要求显式授权

- C) Ask the model to self-police

  让模型自我约束

- D) Allow only during business hours

  只在工作时间内允许

**Q5.** `read_file` must validate paths against an allowlist because:

`read_file` 必须根据白名单校验路径，因为：

- A) It improves latency

  这能降低延迟

- B) Path traversal (`../`) and absolute paths can reach outside the workspace

  路径穿越（`../`）和绝对路径可以访问到工作区之外

- C) The model cannot generate paths

  模型无法生成路径

- D) It reduces token usage

  这能减少 token 用量

**Q6.** The difference between a trace and an audit log is:

trace 与审计日志的区别在于：

- A) They are the same thing

  它们是同一个东西

- B) Traces debug behaviour; audit logs are tamper-evident evidence of actions with before/after state

  trace 用于调试行为；审计日志是带有前后状态、可发现篡改的操作证据

- C) Audit logs are cheaper

  审计日志更便宜

- D) Traces contain PII, audit logs do not

  trace 包含个人身份信息（PII），审计日志不包含

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** Explain credential isolation as a structural defence and why it beats better prompting.

解释为什么凭据隔离是一种结构性防御，以及它为什么胜过更好的提示词。

**Q8.** Give a concrete fail-closed vs fail-open decision for a model router: which failures should route to a fallback and which must abort? Justify.

为模型路由器给出一个具体的失败关闭（fail-closed）与失败开放（fail-open）决策：哪些失败应当路由到备选项，哪些必须中止？说明理由。

**Q9.** Your `read_file` tool will be exposed to an untrusted-content workflow. List the defence-in-depth controls you would stack, beyond the allowlist check.

你的 `read_file` 工具将被暴露给一个处理不可信内容的工作流。除了白名单检查之外，列出你会叠加的纵深防御控制措施。

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This tool is the only filesystem guard in the system. Identify **three** defects.

下面这个工具是系统中唯一的文件系统防护。找出**三个**缺陷。

```python
WORKSPACE = "/srv/agent/workspace"


def read_file(path: str) -> str:
    if not path.startswith(WORKSPACE):
        raise PermissionError("outside workspace")
    with open(path) as f:
        return f.read()
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Indirect injection is the dominant real-world attack: the agent trusts content it fetched, and that content contains instructions.

间接注入是现实世界中最主要的攻击方式：Agent 信任它获取到的内容，而这些内容中包含指令。

**Q2 — B.** Any two of the three are manageable; all three in one agent means a successful injection can exfiltrate private data outward.

三者中任意两者都可以管控；三者同时出现在一个 Agent 中，意味着一次成功的注入就能把私有数据外泄出去。

**Q3 — B.** Intersection prevents one source (or the model) widening access. Union is how privilege-escalation bugs are born.

取交集可以防止某一个来源（或模型）扩大访问范围。取并集正是权限提升 bug 的由来。

**Q4 — B.** Deny-by-default with explicit grants is the only default that fails safely.

默认拒绝加显式授权，是唯一能够安全失败的默认设置。

**Q5 — B.** String prefix checks are not path validation; traversal, symlinks and normalization defeat them.

字符串前缀检查并不是路径校验；路径穿越、符号链接和路径规范化都能绕过它。

**Q6 — B.** Audit is evidence with integrity and before/after payloads, retained for compliance; traces are for debugging and may be sampled.

审计是具有完整性、带有前后 payload 的证据，为合规而保留；trace 用于调试，可以被采样。

**Q7 — model answer.** Keep secrets out of the sandbox where model-generated code runs: tokens live in a vault/proxy, and the sandbox gets short-lived capability-scoped handles instead. If injection succeeds, the agent still cannot read the credential, so it cannot spawn new sessions or exfiltrate. Prompt-level instructions ("never reveal secrets") are probabilistic and fail exactly under the adversarial conditions that matter.

**参考答案。** 让密钥远离运行模型生成代码的沙箱：token 存放在保险库 / 代理中，沙箱拿到的只是短期有效、按能力限定范围的句柄。即使注入成功，Agent 仍然读不到凭据，因此无法创建新会话，也无法外泄。提示词层面的指令（「绝不泄露密钥」）是概率性的，恰恰会在最关键的对抗性条件下失效。

**Q8 — model answer.** Degrade by *bounded fallback*, never by bypass. `CostAwareRouter.complete` falls back to the next viable candidate on a transient `ProviderError(retryable=True)`, up to `max_attempts`; non-retryable provider errors and `RequestCancelled` propagate immediately, the budget is re-checked before each attempt, and `BudgetExceeded` propagates. `select` fails closed: if no candidate is viable it raises `RoutingError` with the exclusion map rather than "pick anything". So an availability failure may shift model, while authority, budget, cancellation and policy failures abort — routing around a control defeats the control.

**参考答案。** 通过*有上限的回退*来降级，绝不通过绕过来降级。`CostAwareRouter.complete` 在遇到瞬时的 `ProviderError(retryable=True)` 时，会回退到下一个可用的候选项，最多 `max_attempts` 次；不可重试的提供商错误和 `RequestCancelled` 会立即向上传播，每次尝试之前都会重新检查预算，`BudgetExceeded` 也会向上传播。`select` 采用失败关闭：如果没有可用的候选项，它会抛出带有排除映射表的 `RoutingError`，而不是「随便选一个」。因此，可用性故障可以切换模型，而权限、预算、取消和策略方面的失败则必须中止——绕开一项控制就等于让这项控制失效。

**Q9 — model answer.** (1) Resolve and normalize the path (realpath) before the allowlist check; reject symlinks that escape. (2) Cap size and apply truncation with an explicit marker. (3) Treat file content as untrusted: wrap it in delimited data markers and never let it act as instructions. (4) Redact or refuse likely-secret files (`.env`, key material) via pattern/basename rules. (5) Log an audit record per read with correlation id. (6) Keep read tools separate from write tools and require approval for writes.

**参考答案。** (1) 在白名单检查之前先解析并规范化路径（realpath）；拒绝逃逸出去的符号链接。(2) 限制大小，并在截断时加上显式标记。(3) 把文件内容视为不可信：用定界的数据标记包裹起来，绝不让它充当指令。(4) 通过模式 / 文件名规则，对疑似包含密钥的文件（`.env`、密钥材料）进行脱敏或拒绝读取。(5) 每次读取都记录一条带关联 id 的审计记录。(6) 把读类工具和写类工具分开，写操作需要审批。

**Q10 — model answer.** (1) Prefix check on the raw string is bypassable: `"/srv/agent/workspace/../etc/passwd"` starts with the workspace, and `os.path.realpath`/`normpath` is never applied; absolute-vs-relative forms also slip through. (2) No symlink handling — a link inside the workspace can point outside. (3) No size limit, no truncation, no encoding/error handling and no audit event. Fix: resolve with `Path.resolve()`, assert it is relative to the resolved workspace root, reject symlinks that resolve outside, cap read size, and record an audit row.

**参考答案。** (1) 对原始字符串做前缀检查是可以被绕过的：`"/srv/agent/workspace/../etc/passwd"` 以工作区路径开头，而 `os.path.realpath` / `normpath` 从未被调用；绝对路径与相对路径的不同写法也能蒙混过关。(2) 没有处理符号链接——工作区内的一个链接可以指向外部。(3) 没有大小限制，没有截断，没有编码 / 错误处理，也没有审计事件。修复：用 `Path.resolve()` 解析路径，断言它位于解析后的工作区根目录之下，拒绝解析到外部的符号链接，限制读取大小，并记录一条审计记录。
