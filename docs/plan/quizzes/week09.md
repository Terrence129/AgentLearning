# Week 9 Quiz — Capstone: Mini-SendOS

**第 9 周测验 — 结业项目（capstone）：Mini-SendOS**

**Time:** 20 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 20 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** The capstone is described as a *composition* because:

结业项目之所以被描述为一种*组合*，是因为：

- A) It is a ninth, unrelated project

  它是第九个、与前面无关的项目

- B) It reuses weeks 1–8 modules as vertical slices into one system

  它把第 1–8 周的模块作为纵向切片复用，组合成一个系统

- C) It copies SendOS's C# code

  它照搬了 SendOS 的 C# 代码

- D) It is only a UI

  它只是一个 UI

**Q2.** The capability catalogue merges two sources with the rule:

能力目录按照什么规则合并两个来源：

- A) Last source wins

  最后一个来源胜出

- B) Published definitions win over derived/discovered ones, with provenance recorded

  已发布的定义优先于推导 / 发现出来的定义，并记录来源（provenance）

- C) The model decides at runtime

  由模型在运行时决定

- D) Merge is random to avoid bias

  随机合并以避免偏差

**Q3.** In the capstone, governance must be:

在结业项目中，治理必须是：

- A) Optional in demo mode

  在演示模式下可选

- B) The same fail-closed path in demo and live runs

  在演示和真实运行中走同一条失败关闭（fail-closed）的路径

- C) Enforced only for write tools

  只对写类工具强制执行

- D) Delegated to the model

  交给模型处理

**Q4.** The learning loop in the capstone ends with:

结业项目中的学习循环以什么结束：

- A) Automatic prompt rewriting

  自动改写提示词

- B) A human-approved asset promotion gated on evidence (submit-only)

  一次由人工批准、以证据为关卡的资产晋升（仅提交）

- C) Fine-tuning the model

  对模型进行微调

- D) Deleting failing traces

  删除失败的 trace

**Q5.** The offline demo script uses:

离线演示脚本使用的是：

- A) A live provider with a $50 budget

  一个预算为 $50 的真实模型提供商（provider）

- B) A mock provider, so the flow is deterministic and free

  一个 mock 提供商，因此流程是确定性的，而且免费

- C) A recorded video only

  仅有一段录制好的视频

- D) No data

  不使用任何数据

**Q6.** The acceptance gate says a senior engineer must be able to:

验收关卡要求一位资深工程师必须能够：

- A) Read the README

  读懂 README

- B) Follow one request's trace from ingress to audit row without asking questions

  在不提任何问题的情况下，沿着一个请求的 trace 从入口一路跟到审计记录

- C) Run the tests

  运行测试

- D) Approve the design

  批准设计

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** List the six layers the capstone must compose and, for each, name the earlier week it comes from.

列出结业项目必须组合的六个层次，并分别说出每一层来自前面哪一周。

**Q8.** How do you demonstrate governance in a demo without live spend and without faking the control path?

如何在演示中展示治理能力，既不产生真实花费，又不伪造控制路径？

**Q9.** Your final deliverable includes a one-page improvement proposal for real SendOS. What makes such a proposal credible rather than a wish list?

你的最终交付物包含一份针对真实 SendOS 的一页改进提案。是什么让这样一份提案可信，而不是一张愿望清单？

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This is the capstone request handler. Identify **three** defects that would make the governance claims false.

下面是结业项目的请求处理函数。找出会让治理承诺落空的**三个**缺陷。

```python
def handle(request: Request):
    if os.getenv("DEMO_MODE") == "1":
        return execute_unchecked(request.action)
    decision = runtime.decide(request)
    return execute_governed(request, decision)
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Each week's module is a layer; the capstone is the first system where all layers must agree on ids, state and evidence.

每一周的模块都是一个层次；结业项目是第一个要求所有层次在 id、状态和证据上保持一致的系统。

**Q2 — B.** Precedence plus provenance: the platform team's published capability definition outranks an inferred one, but the merge records where each definition came from. This is SendOS's published-wins rule in miniature.

优先级加来源：平台团队发布的能力定义优先于推断出来的定义，但合并时会记录每个定义的出处。这就是 SendOS「已发布者胜出」规则的缩微版。

**Q3 — B.** A demo-only bypass is how untested paths reach production, and an env-flag bypass is a backdoor. Mock the provider, not the policy.

仅用于演示的绕过路径，正是未经测试的路径进入生产环境的方式，而通过环境变量开关实现的绕过就是一个后门。要 mock 的是提供商，而不是策略。

**Q4 — B.** Trace → candidate → evidence gate → human publish. Automation proposes; a human promotes; the gate is evidence, not vibes.

trace → 候选 → 证据关卡 → 人工发布。自动化负责提议；人负责晋升；关卡依据的是证据，而不是感觉。

**Q5 — B.** Deterministic, free, and reproducible in CI. Live calls are for the optional web UI demo only.

确定性、免费，并且可在 CI 中复现。真实调用只用于可选的 Web UI 演示。

**Q6 — B.** The trace is the proof that the system is what you claim: model call, plan, approval, execution, audit row, all correlated.

trace 就是系统名副其实的证明：模型调用、计划、审批、执行、审计记录，全部相互关联。

**Q7 — model answer.** (1) Provider layer (week 1) + mock + budget routing (week 8). (2) Capability catalogue (week 2 registry + week 6 risk/appoval metadata). (3) Decision runtime (week 3 typed decisions + week 6 topology/shape selection). (4) Specialists/plan (week 6). (5) Governance: authority, approval binding, audit (weeks 6 and 8). (6) Learning loop: traces + eval harness + evidence gate + human publish (week 7). Surface (FastAPI + UI) is week 9 scaffolding.

**参考答案。** (1) 提供商层（第 1 周）+ mock + 预算路由（第 8 周）。(2) 能力目录（第 2 周的工具注册表 + 第 6 周的风险 / 审批元数据）。(3) 决策运行时（第 3 周的类型化决策 + 第 6 周的拓扑 / 形态选择）。(4) 专员 Agent（specialist）/ 计划（第 6 周）。(5) 治理：权限、审批绑定、审计（第 6 周和第 8 周）。(6) 学习循环：trace + 评测 harness（运行框架）+ 证据关卡 + 人工发布（第 7 周）。对外界面（FastAPI + UI）属于第 9 周的脚手架。

**Q8 — model answer.** Point the provider seam at a scripted `MockProvider` that replays deterministic responses (including a malicious one), and run the *same* handler path used in live mode. Show: a write proposal blocked pending approval; an edited action rejected by the hash check; a replayed approval rejected by at-most-once; and the resulting audit rows. Because only the provider is mocked, the governance code exercised in the demo is the governance code that ships.

**参考答案。** 把 provider 接缝（seam）指向一个脚本化的 `MockProvider`，让它回放确定性的响应（包括一个恶意响应），并运行与真实模式*相同*的处理路径。展示：一个写操作提案在等待审批时被拦下；一个被篡改的操作被哈希检查拒绝；一次被重放的审批被至多一次机制拒绝；以及由此产生的审计记录。由于只有提供商被 mock，演示中运行的治理代码就是最终上线的治理代码。

**Q9 — model answer.** It is grounded in a mechanism you rebuilt and measured: a specific gap (e.g. `CaseRuntime` suspend/resume unwired), the failure it causes today, your miniature's design, evidence from your eval run, the smallest change to SendOS that would close it, its risks and a test plan. Credibility comes from the evidence and the small diff, not from the ambition of the proposal.

**参考答案。** 它立足于一个你亲手重建并度量过的机制：一个具体的缺口（例如 `CaseRuntime` 的挂起 / 恢复没有接通），它如今造成的失败，你的缩微版设计，来自你评测运行的证据，能够补上这个缺口的对 SendOS 的最小改动，以及其风险和测试计划。可信度来自证据和小而精的 diff，而不是提案的雄心。

**Q10 — model answer.** (1) The demo branch bypasses governance entirely (`execute_unchecked`) — the path you demo is not the path that is governed, and an env flag left set in production is a direct privilege bypass. (2) No authority/approval check is shown at all in the demo path, so the "every write is gated" claim is false under that flag. (3) No audit row is written on the demo path, so the demo cannot prove the control it claims. Fix: mock the provider only; single governed handler for both modes; flags may change data, never policy.

**参考答案。** (1) 演示分支完全绕过了治理（`execute_unchecked`）——你演示的路径并不是受治理的那条路径，而如果这个环境变量开关在生产环境中忘了关，就是一个直接的权限绕过。(2) 演示路径上根本没有任何权限 / 审批检查，因此在该开关下，「每一次写操作都经过关卡」的说法是假的。(3) 演示路径上不会写入审计记录，因此演示无法证明它所声称的控制。修复：只 mock 提供商；两种模式共用同一个受治理的处理函数；开关可以改变数据，但绝不能改变策略。
