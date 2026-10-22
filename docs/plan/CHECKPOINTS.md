# Checkpoints — the weekly gate

**检查点 — 每周关卡**

**Purpose:** remove the "did I actually learn it?" ambiguity. Each week has three gates; you may not start week N+1 until all three pass. The gates are cheap to run (about 15 minutes) and they are the difference between a portfolio and a pile of notebooks.

**目的：** 消除「我真的学会了吗？」这种模糊感。每周有三道关卡；三道全部通过之前，你不能开始第 N+1 周。这些关卡运行成本很低（大约 15 分钟），而它们正是作品集与一堆笔记本之间的区别所在。

**Run the gate every Saturday**, and paste the evidence into [`PROGRESS.md`](PROGRESS.md) and `notes/weekNN-review.md`.

**每周六运行关卡**，并把证据粘贴到 [`PROGRESS.md`](PROGRESS.md) 和 `notes/weekNN-review.md` 中。

---

## 1. The three gates (every week)

**1. 三道关卡（每周）**

| Gate<br>关卡 | Command / evidence<br>命令 / 证据 | Pass criterion<br>通过标准 | Where it maps<br>对应目标 |
|---|---|---|---|
| **G. Green**<br>**G. 通过（Green）** | `.\tasks.ps1 week NN` (Windows) / `./tasks.sh week NN` (macOS/Linux), equivalently `pytest tests/weekNN -m week -q`<br>`.\tasks.ps1 week NN`（Windows）/ `./tasks.sh week NN`（macOS/Linux），等价于 `pytest tests/weekNN -m week -q` | All week tests pass, no skips, no xfail; suite runs offline (< 10 s)<br>本周所有测试通过，没有 skip，没有 xfail；测试套件可离线运行（< 10 秒） | Lab deliverable<br>实验（lab）交付物 |
| **E. Explain**<br>**E. 讲解（Explain）** | `docs/plan/quizzes/weekNN.md` closed book + 150-word teach-back, no notes<br>闭卷完成 `docs/plan/quizzes/weekNN.md` + 150 词的复述讲解（teach-back），不看笔记 | Quiz ≥ 8/10 **and** teach-back mentions the mechanism + one failure mode it prevents<br>测验 ≥ 8/10，**并且**复述讲解提到了机制 + 它所防止的一种失败模式 | Concepts list in Learning Plan<br>学习计划中的概念清单 |
| **T. Transfer**<br>**T. 迁移（Transfer）** | SendOS bridge note in the weekly review (what matches / what differs / what you would change)<br>每周复盘中的 SendOS 桥接笔记（哪些一致 / 哪些不同 / 你会改什么） | Three specific answers naming real C# types/files, with one open question you cannot answer yet<br>三个具体的回答，点出真实的 C# 类型/文件，外加一个你暂时还回答不了的开放问题 | Day-job goal (A)<br>日常工作目标（A） |

A week is **done** only when G + E + T all pass. Stretch goals, extra reading and a prettier demo do not substitute for a missing gate.

只有当 G + E + T 全部通过时，一周才算**完成**。拓展目标、额外阅读和更漂亮的演示都不能替代缺失的关卡。

> **Week 0** has a single gate: `doctor` clean, foundation tests green, one live call recorded with tokens/latency/cost.
>
> **第 0 周**只有一道关卡：`doctor` 检查无问题，基础测试通过（变绿），并记录一次真实调用的 token/延迟/成本。
>
> **Week 10** has G = re-derivation exercises complete, E = all 10 quizzes ≥ 8/10, T = final improvement proposal drafted.
>
> **第 10 周**的关卡为：G = 完成重新推导练习，E = 全部 10 次测验 ≥ 8/10，T = 起草最终的改进提案。

---

## 2. Per-week gate table

**2. 每周关卡表**

| Wk<br>周 | Green (tests)<br>Green（测试） | Explain (quiz + teach-back)<br>Explain（测验 + 复述讲解） | Transfer (SendOS)<br>Transfer（SendOS） | Artifact<br>产出物 | Hours<br>小时 |
|---|---|---|---|---|---|
| 0 | `.\tasks.ps1 test` (Windows) / `./tasks.sh test` (macOS/Linux), foundation only<br>`.\tasks.ps1 test`（Windows）/ `./tasks.sh test`（macOS/Linux），仅基础部分 | Baseline: what is a token / streaming / a retry failure<br>基线：什么是 token / 流式输出 / 重试失败 | — | `notes/week00-baseline.md` with one priced call<br>`notes/week00-baseline.md`，包含一次带价格的调用 | 3 |
| 1 | `tests/week01` | Quiz 1 ≥ 8; explain retries + SSE + provider seam<br>测验 1 ≥ 8；讲解重试 + SSE + provider 接缝 | `Send.Model.Adapter` — 3 shared duties, 2 missing<br>`Send.Model.Adapter`——3 项共同职责，2 项缺失 | `agentlab chat` streams + prints tokens/cost<br>`agentlab chat` 流式输出 + 打印 token/成本 | 8–10 |
| 2 | `tests/week02` | Quiz 2 ≥ 8; explain loop termination + budget placement<br>测验 2 ≥ 8；讲解循环终止 + 预算的放置位置 | `CapabilityDefinition`, registry, `DirectCapabilityHandler`<br>`CapabilityDefinition`、注册表、`DirectCapabilityHandler` | 5 golden tasks + full trace<br>5 个黄金任务 + 完整 trace | 10–12 |
| 3 | `tests/week03` | Quiz 3 ≥ 8; explain schema failure + repair economics<br>测验 3 ≥ 8；讲解 schema 失败 + 修复的经济性 | `IStructuredCompletionHandler`, `JsonSchemaValidator`, decision family<br>`IStructuredCompletionHandler`、`JsonSchemaValidator`、决策族 | `analyze() -> Decision` + failure-rate report<br>`analyze() -> Decision` + 失败率报告 | 8–10 |
| 4 | `tests/week04` | Quiz 4 ≥ 8; explain compaction + retention evidence<br>测验 4 ≥ 8；讲解压缩（compaction）+ 保留证据 | `Send.Context.Gateway`, `SpecialistContext` | 20-turn task under 12k budget, retention ≥ 90%<br>在 12k 预算内完成 20 轮任务，保留率 ≥ 90% | 10–12 |
| 5 | `tests/week05` | Quiz 5 ≥ 8; explain MCP roles + trust model<br>测验 5 ≥ 8；讲解 MCP 角色 + 信任模型 | Connector manifests vs MCP discovery<br>连接器清单与 MCP 发现机制的对比 | server + client + security checklist pass<br>服务器 + 客户端 + 安全检查清单通过 | 8–10 |
| 6 | `tests/week06` | Quiz 6 ≥ 8; explain approval binding + topology rule<br>测验 6 ≥ 8；讲解审批绑定 + 拓扑规则 | `TopologyClassifier`, `ApprovalCheckpoint`, `ExecutionPlan` | mini-Squad + approval test proving edit/replay/expiry rejection<br>迷你小队（squad）+ 审批测试，证明能拒绝篡改/重放/过期 | 10–12 |
| 7 | `tests/week07` | Quiz 7 ≥ 8; explain pass^k + judge calibration<br>测验 7 ≥ 8；讲解 pass^k + 评审校准 | `Outcome_Trace`, 5-dim `Evaluator`, publish gate<br>`Outcome_Trace`、5 维 `Evaluator`、发布关卡 | ≥ 25-case eval suite + baseline + 3 regressions + agreement ≥ 80%<br>≥ 25 个用例的评测（eval）套件 + 基线 + 3 个回归 + 一致率 ≥ 80% | 8–10 |
| 8 | `tests/week08` | Quiz 8 ≥ 8; explain lethal trifecta + authority intersection<br>测验 8 ≥ 8；讲解致命三要素 + 权限交集 | governance sandwich, `EffectiveAuthority`<br>治理三明治、`EffectiveAuthority` | attack suite (≥ 10) + threat model `SECURITY.md`<br>攻击套件（≥ 10）+ 威胁模型 `SECURITY.md` | 8–10 |
| 9 | `tests/week09` (optional)<br>`tests/week09`（可选） | Quiz 9 ≥ 8; trace one request end-to-end aloud<br>测验 9 ≥ 8；大声地端到端追踪一个请求 | one-page improvement proposal grounded in the build<br>基于所构建内容的一页改进提案 | Mini-SendOS demo + eval report + write-up<br>Mini-SendOS 演示 + 评测报告 + 总结文章 | 12–16 |
| 10 | Re-derivation: loop, MCP handshake, eval design, approval state machine from a blank file<br>重新推导：从空白文件写出循环、MCP 握手、评测设计、审批状态机 | Quizzes 1–10 revisited, all ≥ 8; teach-back without notes<br>重做测验 1–10，全部 ≥ 8；不看笔记完成复述讲解 | Proposal reviewed by a senior engineer (feedback recorded)<br>提案经一位资深工程师评审（记录反馈） | Portfolio post + 2 deep dives + interview rehearsal<br>作品集文章 + 2 篇深度剖析 + 面试演练 | 4–6 |

---

## 3. Rubric — what "pass" means at each level

**3. 评分标准（rubric）— 各等级的「通过」意味着什么**

### G. Green

**G. 通过（Green）**

| Level<br>等级 | Descriptor<br>描述 |
|---|---|
| **Fail**<br>**不通过** | Any week test fails, errors, or is skipped/xfail to make the suite green.<br>本周任何测试失败、报错，或为了让套件变绿而被 skip/xfail。 |
| **Pass**<br>**通过** | `pytest tests/weekNN -m week -q` is green, runs offline in < 10 s, and you can point to the test that would fail if you deleted your implementation.<br>`pytest tests/weekNN -m week -q` 通过，离线运行耗时 < 10 秒，并且你能指出如果删掉你的实现，哪个测试会失败。 |
| **Strong**<br>**优秀** | Pass, plus: one extra test of your own for a failure mode the brief did not cover, and no changes outside the owned module.<br>达到通过，另外：针对任务说明没有覆盖的某种失败模式，自己额外写一个测试，并且没有修改所负责模块之外的内容。 |

### E. Explain

**E. 讲解（Explain）**

| Level<br>等级 | Descriptor<br>描述 |
|---|---|
| **Fail**<br>**不通过** | Quiz < 8/10, or the teach-back is a list of terms without a mechanism, or you needed notes.<br>测验 < 8/10，或者复述讲解只是一串术语而没有机制，或者你需要看笔记。 |
| **Pass**<br>**通过** | Quiz ≥ 8/10; 150-word teach-back states the mechanism, one failure mode it prevents, and where it lives in the codebase.<br>测验 ≥ 8/10；150 词的复述讲解说明了机制、它所防止的一种失败模式，以及它在代码库中的位置。 |
| **Strong**<br>**优秀** | Pass, plus: you can answer "what would break if we removed it?" and compare it to the alternative you rejected (from the week's concepts).<br>达到通过，另外：你能回答「如果去掉它，会坏掉什么？」，并能把它与你否决的替代方案（来自本周概念）进行比较。 |

### T. Transfer

**T. 迁移（Transfer）**

| Level<br>等级 | Descriptor<br>描述 |
|---|---|
| **Fail**<br>**不通过** | Generic comparison ("SendOS has a similar layer"), no file/type names, or the section is empty.<br>泛泛的比较（「SendOS 也有类似的一层」），没有文件/类型名，或者该部分为空。 |
| **Pass**<br>**通过** | Names the matching C# types/files, states two concrete differences (what SendOS adds or omits), and one thing you would change.<br>点出对应的 C# 类型/文件，说明两处具体差异（SendOS 多了什么或少了什么），以及一处你会修改的地方。 |
| **Strong**<br>**优秀** | Pass, plus: one open question you could ask a SendOS engineer, and a hypothesis about why SendOS made its choice (regulation, multi-tenancy, scale).<br>达到通过，另外：一个可以去问 SendOS 工程师的开放问题，以及一个关于 SendOS 为何如此选择的假设（监管、多租户、规模）。 |

### Artifact quality (informs the portfolio, not a separate gate)

**产出物质量（为作品集提供依据，不是单独的关卡）**

| Level<br>等级 | Descriptor<br>描述 |
|---|---|
| **Fail**<br>**不通过** | Only works with a live key, no trace, numbers not recorded.<br>只能在有真实密钥时运行，没有 trace，没有记录数字。 |
| **Pass**<br>**通过** | Runs offline against mocks where the brief asks; emits trace events; records cost/latency; one command reproduces it.<br>在任务说明要求的地方可基于 mock 离线运行；输出 trace 事件；记录成本/延迟；一条命令即可复现。 |
| **Strong**<br>**优秀** | Pass, plus: a small table of measurements (tokens, cost, latency, pass rate) committed in the repo.<br>达到通过，另外：在仓库中提交一张小的度量表（token、成本、延迟、通过率）。 |

---

## 4. What to do when a gate fails

**4. 关卡未通过时怎么办**

Diagnose **which** gate failed — the remedies are different. Do not "study more" as a reflex.

先诊断是**哪一道**关卡没通过——补救方法各不相同。不要条件反射地「再多学一点」。

| Symptom<br>症状 | Likely cause<br>可能的原因 | Action (in order)<br>行动（按顺序） |
|---|---|---|
| Tests red at the end of the week<br>周末时测试仍是红的 | Misread the tests; implementation fought the contract<br>误读了测试；实现与契约相抵触 | Re-read the failing test names and docstrings; write down the contract in one sentence; ask the tutor for a hint with the exact error. Cut stretch.<br>重读失败测试的名称和 docstring；用一句话写下契约；带着确切的错误信息向导师要一个提示。砍掉拓展目标。 |
| Tests green but quiz < 8/10<br>测试通过但测验 < 8/10 | Retrieval gap, not comprehension gap<br>是提取（回忆）上的差距，而不是理解上的差距 | Re-read only the missed concepts; make one flashcard per miss; retake the quiz the next day (not immediately).<br>只重读答错的概念；每答错一题做一张闪卡；第二天重考（而不是立刻重考）。 |
| Quiz fine but teach-back rambles<br>测验没问题但复述讲解东拉西扯 | You recognize the terms but do not own the mechanism<br>你认得这些术语，但没有真正掌握机制 | Blank-page recall: draw the mechanism, then diff against the code. Re-do the teach-back tomorrow.<br>白纸回忆：画出机制，然后与代码做对比。明天重做复述讲解。 |
| Transfer section thin<br>迁移部分内容单薄 | You have not read the C# side<br>你还没读 C# 那一侧的代码 | 45-minute SendOS bridge session: open the mapped types, answer the three questions with file names. Ask a senior engineer one question.<br>进行 45 分钟的 SendOS 桥接会话：打开对应的类型，带着文件名回答那三个问题。向一位资深工程师提一个问题。 |
| Artifact works only live<br>产出物只能在线上真实调用时运行 | Missing mock seam or trace<br>缺少 mock 接缝（seam）或 trace | Add mock-based test path; emit events; record cost. This is usually a 90-minute fix, not a redesign.<br>添加基于 mock 的测试路径；输出事件；记录成本。这通常是 90 分钟就能修好的问题，不需要重新设计。 |
| Overrun by > 50%<br>超时 > 50% | Scope creep (usually stretch or perfectionism)<br>范围蔓延（通常是拓展目标或完美主义） | Cut stretch and polish; ship the gate at 80%. Record the debt in the review.<br>砍掉拓展目标和打磨；做到 80% 就交关卡。在复盘中记录欠下的债务。 |
| Two weeks in a row fail E<br>连续两周 E 未通过 | Method problem<br>方法问题 | Stop advancing; run one consolidation week (re-do quizzes, re-derive week N−1) before resuming.<br>停止推进；先进行一个巩固周（重做测验，重新推导第 N−1 周），然后再继续。 |

### Escalation rules

**升级规则**

1. **One week grace:** you may start the next week with **one** gate outstanding if you log it in PROGRESS.md as debt and clear it within 7 days. Never two gates, never two weeks.

   **一周宽限：** 如果你在 PROGRESS.md 中把它记为债务，并在 7 天内清掉，你可以带着**一道**未通过的关卡开始下一周。绝不能是两道关卡，也绝不能拖两周。

2. **Hard stop:** if the same gate fails twice (e.g. week 4 tests red on two consecutive Saturdays), do not start week 5. Spend the Saturday on the minimal failing test and the concept note, then ask the tutor for a review of your design.

   **强制停止：** 如果同一道关卡失败两次（例如第 4 周的测试连续两个周六都是红的），就不要开始第 5 周。把周六花在最小的失败测试和概念笔记上，然后请导师审阅你的设计。

3. **Ask for review, not answers:** "Here is my design for X; review it against these three failure modes." This keeps the productive struggle and gets you unstuck.

   **请求审阅，而不是答案：** 「这是我对 X 的设计；请对照这三种失败模式审阅它。」这样既保留了有益的挣扎，又能帮你摆脱卡顿。

---

## 5. Gate evidence block (copy into PROGRESS.md)

**5. 关卡证据块（复制到 PROGRESS.md 中）**

```
Week NN — <theme>
[G] command: ______________________ result: ______ passed, ______ failed, time ____ s
[E] quiz: __/10   teach-back written: yes/no   words: ____
[T] SendOS files read: ______________________   differences stated: ____
[A] artifact command: ______________________   cost/latency recorded: $____ / ____ ms
Hours: ____   Sessions: ______________________   Debt carried: ______________________
```

---

## 6. The honest-failure clause

**6. 诚实失败条款**

If you cannot pass a gate by the end of the week, the correct output is **a documented failure**, not a fake pass: what you tried, where it broke, what you now believe the cause is, and the next experiment. A documented failure is evidence of engineering maturity and is explicitly acceptable in the weekly review. A skipped gate recorded as "done" is the one thing that breaks the curriculum — because week N+1 silently assumes week N.

如果到周末你仍无法通过某道关卡，正确的产出是**一份有记录的失败**，而不是假装通过：你尝试了什么、在哪里出了问题、你现在认为原因是什么，以及下一个实验。有记录的失败是工程成熟度的证明，在每周复盘中是明确可以接受的。把跳过的关卡记为「已完成」，是唯一会破坏整个课程的事情——因为第 N+1 周会默认第 N 周已经完成。
