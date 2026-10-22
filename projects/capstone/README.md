# Capstone — Mini-SendOS

**结业项目——Mini-SendOS**

The capstone is not a ninth lab with a new mechanism. It is the composition of weeks 1–8 into one governed system, plus the evidence that it behaves: a demo that runs offline, an audit trail you can read, an acceptance checklist you can sign, and a write-up you can show a hiring manager.

结业项目（capstone）并不是又一个引入新机制的第九个实验（lab）。它是把第 1–8 周的内容组合成一个受治理的系统，再加上证明它行为正确的证据：一个可以离线运行的演示、一条你能读懂的审计轨迹、一份你可以签字确认的验收清单，以及一篇可以展示给招聘经理的总结文章。

**Build spec:** [`labs/week09-capstone/README.md`](../../labs/week09-capstone/README.md) — read it first; it is the authoritative week-9 brief.
**Plan context:** [`docs/plan/LEARNING-PLAN.md`](../../docs/plan/LEARNING-PLAN.md) week 9.
**Time:** 12–16 h. **Prerequisites:** weeks 1–8 green.

**构建规格：** [`labs/week09-capstone/README.md`](../../labs/week09-capstone/README.md)——请先阅读它；它是第 9 周的权威简介。
**计划背景：** [`docs/plan/LEARNING-PLAN.md`](../../docs/plan/LEARNING-PLAN.md) 第 9 周。
**时间：** 12–16 小时。**前置条件：** 第 1–8 周的测试全部通过（变绿）。

## What you are building

**你要构建什么**

```
goal (tenant + actor)
  -> typed decision            agentlab/capstone/decisions.py   (week 3 skills)
  -> capability check          agentlab/capstone/catalogue.py   (week 8 governance)
  -> persisted proposal        agentlab/capstone/platform.py    (week 6 approval)
  -> bound human approval      agentlab/capstone/platform.py
  -> at-most-once execution    agentlab/capstone/platform.py    (week 8 idempotency)
  -> append-only audit rows    agentlab/capstone/platform.py    (week 7 trace substrate)
  -> typed UI surface          agentlab/web/app.py              (optional extra)
```

## Starter layout

**起始布局**

| Path<br>路径 | State<br>状态 | You do<br>你要做的 |
|---|---|---|
| `agentlab/capstone/decisions.py` | contracts + stubs<br>契约 + 桩代码 | implement parse/serialise/budgets<br>实现解析/序列化/预算 |
| `agentlab/capstone/catalogue.py` | contracts + stubs<br>契约 + 桩代码 | implement merge/resolve/tenant rules<br>实现合并/解析/租户规则 |
| `agentlab/capstone/platform.py` | dataclasses + wiring + stubs<br>数据类 + 接线 + 桩代码 | implement the five lifecycle methods + digest<br>实现五个生命周期方法 + 摘要 |
| `agentlab/web/app.py` | complete, guarded FastAPI<br>完整的、带防护的 FastAPI | wire `create_app(platform)` into your platform<br>把 `create_app(platform)` 接入你的平台 |
| `tests/week09/` | 46 tests, red on purpose<br>46 个测试，故意处于失败（红）状态 | make them green without editing them<br>在不修改它们的前提下让它们通过（变绿） |
| `solutions/week09/` | reference implementation<br>参考实现 | open only after your tests pass<br>只有在你的测试通过后才打开 |
| `scripts/demo_capstone.py` | complete<br>已完成 | use as a prerequisite check; it exits 0 when done<br>用作前置条件检查；完成时以 0 退出 |
| `projects/capstone/ACCEPTANCE.md` | checklist<br>检查清单 | fill it with evidence<br>用证据把它填满 |
| `projects/portfolio/WRITEUP.md` | template<br>模板 | write the design story<br>写出设计故事 |

## Build order (do not reorder)

**构建顺序（不要调换）**

1. `python scripts\demo_capstone.py` (Windows) · `uv run python scripts/demo_capstone.py` (macOS / Linux) — read the "DEMO BLOCKED" list; it names the first gap.

   `python scripts\demo_capstone.py`（Windows）· `uv run python scripts/demo_capstone.py`（macOS / Linux）——阅读 "DEMO BLOCKED" 列表；它会指出第一个缺口。

2. `decisions.py` -> `pytest tests/week09 -m week -q` (decision tests go green).

   `decisions.py` -> `pytest tests/week09 -m week -q`（决策相关测试通过）。

3. `catalogue.py` -> catalogue tests go green.

   `catalogue.py` -> 目录相关测试通过。

4. `platform.py` -> the demo completes end-to-end.

   `platform.py` -> 演示端到端跑通。

5. `web/app.py` wiring -> optional demo UI.

   `web/app.py` 接线 -> 可选的演示 UI。

6. Acceptance checklist -> portfolio write-up -> 5-minute demo (recorded).

   验收清单 -> 作品集总结文章 -> 5 分钟演示（录制）。

## Deliverables

**交付物**

- [ ] `tests/week09` fully green, including at least three invariants you added yourself (replay, edit-after-approval, cross-tenant).

  `tests/week09` 全部通过，其中至少包含三个你自己添加的不变量（重放、审批后编辑、跨租户）。

- [ ] `scripts/demo_capstone.py` exits `0` offline and prints the full audit sequence.

  `scripts/demo_capstone.py` 离线运行时以 `0` 退出，并打印完整的审计序列。

- [ ] `projects/capstone/ACCEPTANCE.md` filled in with command output and evidence.

  `projects/capstone/ACCEPTANCE.md` 已用命令输出和证据填写完整。

- [ ] `projects/portfolio/WRITEUP.md` (800–1,500 words) + a 5-minute recorded demo per `DEMO-CHECKLIST.md`.

  `projects/portfolio/WRITEUP.md`（800–1,500 词）+ 一段按照 `DEMO-CHECKLIST.md` 录制的 5 分钟演示。

- [ ] One-page design proposal for a real SendOS improvement, grounded in the capstone (recommended: durable suspend/resume for approvals, or trace -> candidate evidence gating).

  一页基于结业项目、针对 SendOS 真实改进的设计提案（推荐：审批的持久化挂起/恢复，或 trace -> 候选的证据关卡）。

## Definition of done

**完成的定义**

You can draw the request path from ingress to audit row without notes; every arrow has a failure mode and a control; and a senior engineer can follow one request through the demo without asking a question.

你能不看笔记就画出从入口到审计行的请求路径；每一个箭头都有对应的失败模式和控制措施；并且一位资深工程师能够在不提任何问题的情况下，跟随一个请求走完整个演示。
