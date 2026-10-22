# Week 7 Quiz — Evals and Observability

**第 7 周测验 — 评测与可观测性**

**Time:** 15 minutes · **Closed book** · 10 questions. Pass mark: 8/10.

**时间：** 15 分钟 · **闭卷** · 10 道题。及格线：8/10。

## Part A — Multiple choice (6 questions)

**A 部分 — 选择题（6 道）**

**Q1.** The difference between an outcome eval and a trajectory eval is:

结果评测（outcome eval）与轨迹评测（trajectory eval）的区别在于：

- A) Outcome evals are always better

  结果评测总是更好

- B) Outcome scores only the final result; trajectory scores the path (tool choices, constraints respected)

  结果评测只给最终结果打分；轨迹评测给路径打分（工具选择、约束是否被遵守）

- C) Trajectory evals require no dataset

  轨迹评测不需要数据集

- D) Outcome evals use judges, trajectory evals use exact match

  结果评测使用评审，轨迹评测使用精确匹配

**Q2.** `pass^k` measures:

`pass^k` 衡量的是：

- A) Success on the first attempt only

  仅第一次尝试的成功率

- B) The probability of succeeding on all k independent attempts — a reliability measure

  在全部 k 次独立尝试中都成功的概率——一种可靠性度量

- C) Average tokens per attempt

  每次尝试的平均 token 数

- D) Judge agreement across k samples

  评审在 k 个样本上的一致性

**Q3.** An LLM judge is credible only when:

LLM 评审（LLM-as-judge）只有在什么情况下才可信：

- A) It uses the newest model

  它使用最新的模型

- B) It is calibrated against human labels, and both raw agreement and Cohen's kappa are reported

  它经过与人工标注的校准，并且同时报告原始一致率和 Cohen's kappa

- C) It gives yes/no answers

  它给出是 / 否的回答

- D) It runs at temperature 1.0

  它在 temperature 1.0 下运行

**Q4.** "Deterministic-first scoring" means:

「确定性优先的打分」指的是：

- A) Use exact checks before any judge call

  在任何评审调用之前先使用精确检查

- B) Only use deterministic agents

  只使用确定性的 Agent

- C) Fix the random seed and call the judge

  固定随机种子后再调用评审

- D) Remove all non-deterministic tests

  删除所有非确定性的测试

**Q5.** Eval leakage is:

评测泄漏是指：

- A) Eval cases leaking to users

  评测用例泄露给了用户

- B) Tuning on the eval set until it stops predicting real performance

  在评测集上反复调优，直到它不再能预测真实表现

- C) Traces containing PII

  trace 中包含个人身份信息（PII）

- D) A judge scoring too strictly

  评审打分过于严格

**Q6.** A regression gate in CI should fail when:

CI 中的回归关卡应该在什么时候失败：

- A) Any single eval case fails

  任何一个评测用例失败时

- B) A metric drops below the recorded baseline (or a pass^k floor)

  某个指标跌破记录的基线（或 pass^k 下限）时

- C) The model changes

  模型变更时

- D) Cost increases by any amount

  成本有任何增加时

## Part B — Short answer (3 questions)

**B 部分 — 简答题（3 道）**

**Q7.** You have 25 agent traces and two hours. Describe how you build a 20-case golden set that will actually catch regressions, including what makes a case good.

你手上有 25 条 Agent trace 和两个小时。描述你会如何构建一个真正能抓住回归的 20 个用例的黄金集，包括什么样的用例才算好用例。

**Q8.** Why is a trace schema a prerequisite for evals, not just for debugging?

为什么 trace schema 是评测的前提条件，而不只是调试的前提条件？

**Q9.** A teammate says "the new prompt is better, it feels more helpful." Give the three-step answer you would require before accepting the change.

一位队友说：「新的提示词更好，感觉更有帮助。」给出你在接受这项变更之前会要求的三步回答。

## Part C — Spot the bug (1 question)

**C 部分 — 找 bug（1 道）**

**Q10.** This scoring function is supposed to be the eval harness. Identify **three** methodological defects.

下面这个打分函数本应是评测的 harness（运行框架）。找出**三个**方法论上的缺陷。

```python
def score(outputs):
    good = 0
    for output in outputs:
        verdict = provider.complete(f"Is this answer good? {output.text}").content
        if "yes" in verdict.lower():
            good += 1
    return good / len(outputs)
```

---

## Answers and explanations

**答案与解析**

**Q1 — B.** Trajectory evals matter when process compliance is the requirement (approvals, no write without gate). They are more expensive to build and score.

当过程合规本身就是要求时（审批、未经关卡不得写入），轨迹评测就很重要。它们的构建和打分成本更高。

**Q2 — B.** pass@1 flatters unreliable agents: an agent that succeeds 70% of the time has a pass^5 far below 70%. Reliability is what production needs.

pass@1 会美化不可靠的 Agent：一个成功率为 70% 的 Agent，其 pass^5 远低于 70%。生产环境需要的是可靠性。

**Q3 — B.** An uncalibrated judge measures its own bias. Agreement against 20–30 human labels is the evidence — and report Cohen's kappa alongside it, because 90% raw agreement on a 90/10 label set can be κ≈0. Without calibration a judge is a random number generator with good prose.

未经校准的评审衡量的只是它自己的偏差。与 20–30 条人工标注的一致率才是证据——同时还要报告 Cohen's kappa，因为在 90/10 分布的标注集上，90% 的原始一致率对应的 κ 可能约等于 0。没有校准的评审，只是一个文笔不错的随机数生成器。

**Q4 — A.** Exact checks (schema valid, substring present, exit code, constraint count) are cheaper, faster and more reliable; judges are reserved for what cannot be checked mechanically.

精确检查（schema 合法、子串存在、退出码、约束计数）更便宜、更快也更可靠；评审只留给那些无法机械检查的内容。

**Q5 — B.** Repeated tuning against the same cases overfits: metrics rise while real quality stalls. Countermeasure: hold out cases, refresh periodically, and weight rare failures.

针对同一批用例反复调优会导致过拟合：指标在上升，真实质量却停滞不前。对策：保留留出用例，定期更新，并对罕见的失败加权。

**Q6 — B.** Baselines (and floors such as pass^k) define acceptable regression. Failing on any single case is too brittle; failing on a metric drop is the control.

基线（以及 pass^k 之类的下限）定义了可接受的回归范围。任何单个用例失败就判失败过于脆弱；以指标下降判失败才是合适的控制手段。

**Q7 — model answer.** Sample 25 traces, cluster failures by taxonomy, and pick cases to cover: happy paths (5), each failure category (8–10), safety/policy constraints (3–4), and edge/adversarial inputs (2–3). Each case needs a stable input, a deterministic check where possible, a rubric with 2–4 graded criteria, and a known baseline result. Good cases are *discriminating* (a bad agent fails them), *stable* (no flaky tool/network), and *explainable* (you can say why it failed).

**参考答案。** 抽样 25 条 trace，按分类体系对失败进行聚类，然后挑选用例以覆盖：正常路径（5 个）、每一种失败类别（8–10 个）、安全 / 策略约束（3–4 个），以及边界 / 对抗性输入（2–3 个）。每个用例都需要一个稳定的输入，尽可能有一个确定性检查，一份包含 2–4 条分级标准的评分标准（rubric），以及一个已知的基线结果。好的用例应当具有*区分度*（糟糕的 Agent 会失败）、*稳定*（不依赖不稳定的工具 / 网络），并且*可解释*（你能说清它为什么失败）。

**Q8 — model answer.** Evals consume traces: to score a trajectory you need structured events (steps, tool calls, results, stop reason) with stable ids and timings. If tracing is ad hoc logs, you cannot join a score to the steps that caused it, cannot compute pass^k reliably, and cannot reproduce the failure. The trace schema is also the contract SendOS uses between runtime and learning.

**参考答案。** 评测要消费 trace：要给一条轨迹打分，你需要带有稳定 id 和计时信息的结构化事件（步骤、工具调用、结果、停止原因）。如果追踪只是零散的日志，你就无法把分数关联到导致它的步骤上，无法可靠地计算 pass^k，也无法复现失败。trace schema 同时也是 SendOS 在运行时与学习之间使用的契约。

**Q9 — model answer.** (1) Show a baseline: run the existing eval suite on old and new prompt; no number, no change. (2) Check the shape: which cases moved, by how much, and is the change within judge noise (repeat runs / pass^k)? (3) Check for leakage and cost — did cases get tuned on, and did tokens/latency change? Only then accept, with the report attached.

**参考答案。** (1) 给出基线：在新旧提示词上分别运行现有的评测套件；没有数字，就不改。(2) 检查变化的形态：哪些用例变了，变了多少，这些变化是否在评审噪声范围之内（重复运行 / pass^k）？(3) 检查泄漏和成本——是否针对这些用例做过调优，token / 延迟是否发生变化？只有在此之后才接受变更，并附上报告。

**Q10 — model answer.** (1) No rubric and no forced structured output: a substring "yes" match on free text is not a judgement. (2) The judge is the same model as the generator (self-preference bias) and is never calibrated against human labels. (3) Single run per case, no baseline, no deterministic checks first, no failure taxonomy — the number produced is not comparable across time. Also: no cost estimate and no held-out set.

**参考答案。** (1) 没有评分标准，也没有强制结构化输出：在自由文本中匹配子串「yes」算不上评判。(2) 评审与生成器是同一个模型（自我偏好偏差），并且从未与人工标注进行校准。(3) 每个用例只运行一次，没有基线，没有先做确定性检查，也没有失败分类——得出的数字无法跨时间比较。另外：没有成本估算，也没有留出集。
