# Capstone Acceptance — Mini-SendOS

**结业项目验收——Mini-SendOS**

Fill this in as you go. Every row needs **evidence**: a command and its output, or a file/line reference. A checked box without evidence is not acceptance.

边做边填写。每一行都需要**证据**：一条命令及其输出，或者一个文件/行号引用。没有证据的勾选框不算验收通过。

**Student:** Terrence (Yaqi) Chen · **Date started:** · **Date completed:**

**学员：** Terrence (Yaqi) Chen · **开始日期：** · **完成日期：**

## A. Automated gates

**A. 自动化关卡**

| # | Gate<br>关卡 | Command (Windows)<br>命令（Windows） | Command (macOS / Linux)<br>命令（macOS / Linux） | Evidence (paste output summary)<br>证据（粘贴输出摘要） | Pass<br>通过 |
|---|---|---|---|---|---|
| A1 | Lab tests green<br>实验测试通过 | `.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q` | `uv run python -m pytest tests/week09 -m week -q` | | [ ] |
| A2 | Demo completes offline<br>演示离线跑完 | `.\.venv\Scripts\python.exe scripts\demo_capstone.py` (exit code)<br>`.\.venv\Scripts\python.exe scripts\demo_capstone.py`（退出码） | `uv run python scripts/demo_capstone.py` (exit code)<br>`uv run python scripts/demo_capstone.py`（退出码） | | [ ] |
| A3 | Foundation still green<br>基础测试仍然通过 | `.\.venv\Scripts\python.exe -m pytest -q` | `uv run python -m pytest -q` | | [ ] |
| A4 | Lint clean<br>Lint 检查干净 | `.\.venv\Scripts\ruff.exe check agentlab\capstone agentlab\web tests\week09` | `uv run ruff check agentlab/capstone agentlab/web tests/week09` | | [ ] |
| A5 | Web imports without the extra<br>未安装 extra 时 Web 模块也能导入 | `.\.venv\Scripts\python.exe -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"` | `uv run python -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"` | | [ ] |
| A6 | No live network in tests<br>测试中没有真实网络访问 | grep the week09 tests for `httpx`/`requests`/real URLs<br>在 week09 测试中 grep `httpx`/`requests`/真实 URL | same `grep` command<br>同样的 `grep` 命令 | | [ ] |

## B. Behavioural invariants (you write the tests)

**B. 行为不变量（由你编写测试）**

Add these to `tests/week09/test_capstone_extra.py`, marked `pytest.mark.week`, and reference the test name as evidence.

把这些测试添加到 `tests/week09/test_capstone_extra.py` 中，并标记为 `pytest.mark.week`，然后引用测试名称作为证据。

| # | Invariant<br>不变量 | What it proves<br>它证明了什么 | Test name / evidence<br>测试名称 / 证据 | Pass<br>通过 |
|---|---|---|---|---|
| B1 | A replayed approval cannot execute twice<br>重放的审批不能执行两次 | at-most-once execution<br>至多一次执行 | | [ ] |
| B2 | Editing proposal arguments after approval blocks execution<br>审批后修改提案参数会阻止执行 | approval is bound to the action hash<br>审批绑定到动作哈希 | | [ ] |
| B3 | A different tenant cannot resolve a tenant-scoped capability<br>其他租户无法解析租户范围内的能力 | no cross-tenant oracle<br>不存在跨租户的探测途径（oracle） | | [ ] |
| B4 | A write capability without `approval_required=True` is rejected<br>没有 `approval_required=True` 的写入能力会被拒绝 | fail-closed catalogue<br>故障即关闭（fail-closed）的目录 | | [ ] |
| B5 | A decision that breaks presentation budgets is refused<br>突破展示预算的决策会被拒绝 | UI contract enforced in code<br>UI 契约由代码强制执行 | | [ ] |
| B6 | Audit `seq` is strictly increasing and append-only<br>审计 `seq` 严格递增且仅追加 | replayable evidence<br>可重放的证据 | | [ ] |

## C. Manual checks

**C. 手动检查**

| # | Check<br>检查项 | Evidence<br>证据 | Pass<br>通过 |
|---|---|---|---|
| C1 | Read `audit_trail()` after the demo: the lifecycle is complete and ordered (`proposal_created` -> `approval_granted` -> `execution_started` -> `execution_finished`)<br>演示结束后阅读 `audit_trail()`：生命周期完整且有序（`proposal_created` -> `approval_granted` -> `execution_started` -> `execution_finished`） | | [ ] |
| C2 | The UI (if wired) renders the typed decision and never invents prose<br>UI（如果已接线）渲染类型化决策，并且从不自行编造文字 | screenshot path<br>截图路径 | | [ ] |
| C3 | You can explain, without notes, why the proposal is persisted before approval<br>你能不看笔记解释为什么提案要在审批之前持久化 | 150-word teach-back attached<br>附上 150 词的复述讲解（teach-back） | | [ ] |
| C4 | You can explain which week's mechanism each `platform.py` method reuses<br>你能解释 `platform.py` 的每个方法复用了哪一周的机制 | mapping table in write-up<br>总结文章中的映射表 | | [ ] |

## D. Deliverables

**D. 交付物**

| # | Artifact<br>成果 | Path<br>路径 | Pass<br>通过 |
|---|---|---|---|
| D1 | Written design + eval + cost/latency + threats<br>书面设计 + 评测（eval）+ 成本/延迟 + 威胁 | `projects/portfolio/WRITEUP.md` | [ ] |
| D2 | 5-minute demo recorded<br>已录制 5 分钟演示 | link/path<br>链接/路径 | | [ ] |
| D3 | SendOS improvement proposal (1 page)<br>SendOS 改进提案（1 页） | `notes/sendos-proposal.md` | | [ ] |

## E. Sign-off

**E. 签字确认**

- [ ] All automated gates pass from a clean shell (no environment variables beyond `.env`).

  所有自动化关卡在一个干净的 shell 中通过（除 `.env` 外没有其他环境变量）。

- [ ] A senior engineer followed the demo trace from ingress to audit row without asking a question.

  一位资深工程师在没有提任何问题的情况下，跟随演示 trace 从入口一路走到审计行。

- [ ] The write-up states at least three limitations you know about but did not fix.

  总结文章中至少写明了三个你知道但没有修复的局限。

**Notes / deviations:**

**备注 / 偏差：**
