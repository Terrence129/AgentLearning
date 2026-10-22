# Week 6 Quiz — Planning, Orchestration and Approval

**第 6 周测验 — 计划、编排与审批**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** When does an orchestrator-worker topology earn its cost?

编排者—工作者拓扑在什么情况下才值回它的成本？

- A) Whenever a task has more than one step

  只要任务超过一个步骤

- B) When subtasks are genuinely parallelisable or need isolated contexts, and synthesis is the hard part

  当子任务确实可以并行，或需要相互隔离的上下文，并且综合归纳才是难点时

- C) When you want to use more agents than your competitor

  当你想比竞争对手用更多的 Agent 时

- D) Always — more agents means better results

  总是如此——Agent 越多，结果越好

**Q2.** The topology rule in the plan says:

计划中的拓扑规则是：

- A) Always start with a multi-squad and simplify later

  总是从多小队（multi-squad）开始，之后再简化

- B) Pick the smallest sufficient shape; if no shape is backed by the task's topology, report a limitation rather than guessing smaller

  选择最小的够用形态；如果任务的拓扑无法支撑任何一种形态，就报告一个局限，而不是去猜一个更小的形态

- C) Let the model choose freely between shapes

  让模型在各种形态之间自由选择

- D) Use whichever shape the previous run used

  沿用上一次运行所用的形态

**Q3.** An `ApprovalBinding` must include:

`ApprovalBinding` 必须包含：

- A) Only the approval id and timestamp

  只需审批 id 和时间戳

- B) Actor, tenant, action hash, authority snapshot and expiry

  执行者、租户、操作哈希、权限快照和过期时间

- C) The model name and temperature

  模型名称和 temperature

- D) The full conversation transcript

  完整的对话记录

**Q4.** The action hash exists to prevent:

操作哈希的存在是为了防止：

- A) Slow approvals

  审批过慢

- B) Post-approval edits — the executed action must be exactly the approved one

  审批后的篡改——被执行的操作必须与被批准的操作完全一致

- C) Duplicate tool names

  工具重名

- D) Token overflow

  token 溢出

**Q5.** "At-most-once execution" of an approved action is typically guaranteed with:

已批准操作的「至多执行一次」通常通过什么来保证：

- A) A retry loop

  一个重试循环

- B) A compare-and-swap state transition plus an idempotency record

  一次比较并交换（compare-and-swap）的状态转换，外加一条幂等记录

- C) A larger model

  一个更大的模型

- D) Asking the human twice

  向人类确认两次

**Q6.** A handoff between agents should pass:

Agent 之间的交接应该传递：

- A) The full transcript, for completeness

  完整的对话记录，以求完整

- B) A `HandoffArtifact`: specialist, summary, findings, confidence, and artifact references — not the sender's transcript

  一个 `HandoffArtifact`：专员 Agent（specialist）、摘要、发现、置信度和产物引用——而不是发送方的对话记录

- C) Only a one-line summary

  只有一行摘要

- D) The raw tool outputs

  原始的工具输出

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** Why must the proposal be persisted **before** approval, not after? Name the two failure classes this prevents.

为什么提案必须在审批**之前**而不是之后持久化？说出这能防范的两类失败。

**Q8.** Authority can change between approval and execution. Explain the scenario that makes an authority snapshot necessary and what goes wrong without it.

在审批和执行之间，权限可能会发生变化。解释一个让权限快照变得必要的场景，以及缺少快照时会出什么问题。

**Q9.** Define "smallest sufficient shape" and apply it to: "summarise this one document". Justify the shape you pick.

给「最小的够用形态」下定义，并将其应用到「总结这一份文档」上。说明你所选形态的理由。

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This approval executor is the entire governance of the action path. Identify **three** security defects.

下面这个审批执行器就是操作路径上的全部治理逻辑。找出**三个**安全缺陷。

```python
def execute(approval_id: str, action: dict):
    approval = store.get(approval_id)
    if approval.status == "approved":
        return tools.call(action["tool"], action["args"])
    raise NotApproved()
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Multi-agent pays when work is parallel or context isolation is essential and synthesis dominates. Otherwise it multiplies cost, latency and failure surface.

当工作可以并行、或上下文隔离必不可少，并且综合归纳占主导时，多 Agent 才划算。否则它只会成倍放大成本、延迟和故障面。

**Q2 — B.** Topology-driven selection with an explicit "no backed shape" limitation. Guessing a smaller shape silently under-powers the task; guessing bigger over-spends and adds control risk.

由拓扑驱动的选择，并带有一个显式的「无可支撑形态」局限。猜一个更小的形态会悄悄地让任务力不从心；猜一个更大的形态则会超支，并增加控制风险。

**Q3 — B.** Binding is what makes an approval specific and non-replayable. Approval id alone is an opaque handle anyone can reuse.

绑定让一次审批变得具体且不可重放。仅有审批 id 只是一个任何人都能复用的不透明句柄。

**Q4 — B.** The hash is recomputed at execution and compared to the approved hash; any edit between approval and execution fails the check.

哈希会在执行时重新计算，并与审批时的哈希进行比较；审批和执行之间的任何修改都无法通过检查。

**Q5 — B.** CAS on state (proposed → approved → executing → executed) plus an idempotency key prevents double execution under retries/concurrency.

对状态（proposed → approved → executing → executed）进行 CAS，再加上一个幂等键，可以防止在重试 / 并发下被重复执行。

**Q6 — B.** `HandoffArtifact(specialist, summary, findings, confidence, artifacts)` (rendered by `as_text()`) is the contract: bounded, attributable, and enough for the orchestrator to synthesise without seeing the sender's context. Full transcripts leak context and cost; one-liners lose the findings.

`HandoffArtifact(specialist, summary, findings, confidence, artifacts)`（由 `as_text()` 渲染）就是契约：有边界、可归因，并且足以让编排者在看不到发送方上下文的情况下进行综合。完整的对话记录会泄露上下文、增加成本；一行摘要则会丢失发现。

**Q7 — model answer.** Persist first so the approved object is durable and auditable: (1) crash/restart between approval and execution would otherwise lose the approval (or force a re-approval), and (2) an attacker or bug could alter the proposal after approval if the canonical record is created later. The persisted proposal is the thing the hash binds.

**参考答案。** 先持久化，被批准的对象才是持久且可审计的：(1) 否则在审批和执行之间发生崩溃 / 重启会丢失审批（或迫使重新审批）；(2) 如果权威记录是在之后才创建的，攻击者或 bug 就可能在审批之后篡改提案。哈希所绑定的正是这份被持久化的提案。

**Q8 — model answer.** A manager approves a refund; before execution the approver's role is revoked or the tenant's entitlement changes. Without a snapshot, execution re-reads current authority and may (a) execute with no valid approver, or (b) silently widen/deny based on unrelated later changes. With a snapshot, the execution decision is made against exactly the authority that justified the approval, and discrepancy is surfaced rather than silently resolved.

**参考答案。** 一位经理批准了一笔退款；在执行之前，审批人的角色被撤销了，或者租户的授权发生了变化。没有快照的话，执行时会重新读取当前权限，可能 (a) 在没有有效审批人的情况下执行，或者 (b) 基于后来无关的变更悄悄地放宽 / 拒绝。有了快照，执行决策恰好基于当初支撑该审批的那份权限做出，任何不一致都会被显式暴露出来，而不是被悄悄消化掉。

**Q9 — model answer.** The least complex execution shape whose topology the task actually supports. "Summarise this one document" is a single capability/reasoning node → direct call or one specialist; no squad, no multi-squad, no planner. Adding a squad adds cost, latency and failure modes without adding capability.

**参考答案。** 指任务拓扑实际能支撑的、复杂度最低的执行形态。「总结这一份文档」只是单一的能力 / 推理节点 → 直接调用或一个专员 Agent 即可；不需要小队（squad）、不需要多小队、也不需要规划器。加上一个小队只会增加成本、延迟和失败模式，而不会增加能力。

**Q10 — model answer.** (1) It never checks the action against the approved proposal: `action` is caller-supplied, so an approved "read" can be swapped for a "refund" — no action hash comparison. (2) No expiry check and no authority check at execution; approvals can be used forever and by anyone. (3) No at-most-once/idempotency: replaying the call executes the side effect again. Also no audit append and no tenant scoping.

**参考答案。** (1) 它从不将操作与被批准的提案进行核对：`action` 由调用方提供，因此一个已批准的「读取」可以被替换成「退款」——没有操作哈希比较。(2) 执行时没有过期检查，也没有权限检查；审批可以被任何人永久使用。(3) 没有至多一次 / 幂等保障：重放调用会再次触发副作用。另外，也没有追加审计记录，没有租户范围限定。
