# Demo Checklist — 5 minutes, no surprises

**演示检查清单——5 分钟，零意外**

> Record after the acceptance checklist is green. The recording is evidence; the checklist is what keeps the recording honest.
>
> 在验收清单全部通过（变绿）之后再录制。录屏是证据；而检查清单是让录屏保持诚实的东西。

## Pre-demo (10 minutes before recording)

**演示前（录制前 10 分钟）**

- [ ] `.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q` (Windows) · `uv run python -m pytest tests/week09 -m week -q` (macOS / Linux) → green.

  `.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q`（Windows）· `uv run python -m pytest tests/week09 -m week -q`（macOS / Linux）→ 通过（变绿）。

- [ ] `.\.venv\Scripts\python.exe scripts\demo_capstone.py` (Windows) · `uv run python scripts/demo_capstone.py` (macOS / Linux) → exits 0 (capture the output).

  `.\.venv\Scripts\python.exe scripts\demo_capstone.py`（Windows）· `uv run python scripts/demo_capstone.py`（macOS / Linux）→ 以 0 退出（保存好输出）。

- [ ] `.\.venv\Scripts\python.exe -m pytest -q` (Windows) · `uv run python -m pytest -q` (macOS / Linux) → foundation green.

  `.\.venv\Scripts\python.exe -m pytest -q`（Windows）· `uv run python -m pytest -q`（macOS / Linux）→ 基础测试通过。

- [ ] Terminal font size ≥ 14; working directory is the repo root; no secrets visible in `.env` on screen.

  终端字号 ≥ 14；工作目录是仓库根目录；屏幕上看不到 `.env` 中的任何密钥。

- [ ] Close chat windows / notifications. One clean terminal + one editor tab.

  关闭聊天窗口 / 通知。只留一个干净的终端 + 一个编辑器标签页。

- [ ] If showing the UI: install the web extra *before* recording, start the server in a second pane.

  如果要展示 UI：在录制*之前*安装 web extra，并在第二个窗格中启动服务器。

- [ ] Known state: fresh mock run, no cached trace from a previous demo.

  已知状态：全新的 mock 运行，没有之前演示缓存下来的 trace。

- [ ] Fallback ready: if a live step fails, run the recorded demo script and narrate the audit rows.

  准备好后备方案：如果某个现场步骤失败，就运行录好的演示脚本，并讲解审计行。

## The 5-minute script

**5 分钟脚本**

| Time<br>时间 | Beat<br>环节 | Say / show<br>讲述 / 展示 |
|---|---|---|
| 0:00–0:30 | Hook<br>开场钩子 | "A model can propose anything. This system only lets it propose something a human approved, once, with evidence."<br>“模型可以提议任何事情。而这个系统只允许它提议经人类审批过的事情，只执行一次，并且有证据。” |
| 0:30–1:15 | Architecture<br>架构 | Show the path: goal -> typed decision -> catalogue -> proposal -> approval -> execution -> audit. Name the module behind each arrow.<br>展示路径：目标 -> 类型化决策 -> 目录 -> 提案 -> 审批 -> 执行 -> 审计。说出每个箭头背后对应的模块。 |
| 1:15–2:00 | Decision<br>决策 | Run the demo; pause on the typed decision. Say why free text would be worse (UI contract, budgets, audit).<br>运行演示；在类型化决策处暂停。说明为什么自由文本会更糟（UI 契约、预算、审计）。 |
| 2:00–2:45 | Governance<br>治理 | Show the proposal (`action_hash`, `expires_at`) and the approval. Explain proposer ≠ approver and why the proposal was persisted *before* approval.<br>展示提案（`action_hash`、`expires_at`）和审批。解释提议者 ≠ 审批者，以及为什么提案要在审批*之前*持久化。 |
| 2:45–3:30 | At-most-once<br>至多一次 | Show execution and attempt a replay (or show the test asserting it fails). Explain binding: id vs hash vs expiry.<br>展示执行过程并尝试一次重放（或展示断言重放失败的测试）。解释绑定：id、哈希与过期时间的区别。 |
| 3:30–4:15 | Audit<br>审计 | Print `audit_trail()`. Point at order + `seq`. "This is the eval substrate — week 7 could score this."<br>打印 `audit_trail()`。指出顺序 + `seq`。“这就是评测（eval）的基础数据——第 7 周的内容可以给它打分。” |
| 4:15–4:45 | Limits<br>局限 | Name three honest limitations (in-memory state, mock provider, single process) and the next step (durable suspend/resume).<br>坦诚说出三个局限（内存中的状态、mock 模型提供商（provider）、单进程）以及下一步（持久化的挂起/恢复）。 |
| 4:45–5:00 | Close<br>收尾 | "Built from primitives over ten weeks; it is the same shape as SendOS's governed path, in miniature."<br>“十周内从基本组件构建而成；它与 SendOS 的受治理路径形态相同，只是缩微版。” |

## Do not

**不要做**

- Do not demo live network calls; the offline mock path is the reproducible one.

  不要演示真实的网络调用；离线 mock 路径才是可复现的。

- Do not show a model-authored "approved" boolean — the point is that only a human approval row unlocks execution.

  不要展示由模型生成的 "approved" 布尔值——重点在于只有人类的审批行才能解锁执行。

- Do not apologise for the ugly UI; it is deliberately thin.

  不要为难看的 UI 道歉；它是刻意做得很简单的。

- Do not skip the audit trail: it is the strongest evidence you have.

  不要跳过审计轨迹：它是你手中最有力的证据。

## After recording

**录制之后**

- [ ] Save as `projects/portfolio/demo.mp4` (or unlisted link) and reference it from the write-up.

  保存为 `projects/portfolio/demo.mp4`（或一个不公开列出的链接），并在总结文章中引用它。

- [ ] Paste the demo terminal output into `projects/capstone/ACCEPTANCE.md` row A2.

  把演示的终端输出粘贴到 `projects/capstone/ACCEPTANCE.md` 的 A2 行。

- [ ] Note the runtime of the demo (5 min target, 7 min hard limit).

  记下演示的时长（目标 5 分钟，硬性上限 7 分钟）。
