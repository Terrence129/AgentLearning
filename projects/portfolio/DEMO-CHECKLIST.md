# Demo Checklist — 5 minutes, no surprises

> Record after the acceptance checklist is green. The recording is evidence; the checklist is what keeps the recording honest.

## Pre-demo (10 minutes before recording)

- [ ] `.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q` (Windows) · `uv run python -m pytest tests/week09 -m week -q` (macOS / Linux) → green.
- [ ] `.\.venv\Scripts\python.exe scripts\demo_capstone.py` (Windows) · `uv run python scripts/demo_capstone.py` (macOS / Linux) → exits 0 (capture the output).
- [ ] `.\.venv\Scripts\python.exe -m pytest -q` (Windows) · `uv run python -m pytest -q` (macOS / Linux) → foundation green.
- [ ] Terminal font size ≥ 14; working directory is the repo root; no secrets visible in `.env` on screen.
- [ ] Close chat windows / notifications. One clean terminal + one editor tab.
- [ ] If showing the UI: install the web extra *before* recording, start the server in a second pane.
- [ ] Known state: fresh mock run, no cached trace from a previous demo.
- [ ] Fallback ready: if a live step fails, run the recorded demo script and narrate the audit rows.

## The 5-minute script

| Time | Beat | Say / show |
|---|---|---|
| 0:00–0:30 | Hook | "A model can propose anything. This system only lets it propose something a human approved, once, with evidence." |
| 0:30–1:15 | Architecture | Show the path: goal -> typed decision -> catalogue -> proposal -> approval -> execution -> audit. Name the module behind each arrow. |
| 1:15–2:00 | Decision | Run the demo; pause on the typed decision. Say why free text would be worse (UI contract, budgets, audit). |
| 2:00–2:45 | Governance | Show the proposal (`action_hash`, `expires_at`) and the approval. Explain proposer ≠ approver and why the proposal was persisted *before* approval. |
| 2:45–3:30 | At-most-once | Show execution and attempt a replay (or show the test asserting it fails). Explain binding: id vs hash vs expiry. |
| 3:30–4:15 | Audit | Print `audit_trail()`. Point at order + `seq`. "This is the eval substrate — week 7 could score this." |
| 4:15–4:45 | Limits | Name three honest limitations (in-memory state, mock provider, single process) and the next step (durable suspend/resume). |
| 4:45–5:00 | Close | "Built from primitives over ten weeks; it is the same shape as SendOS's governed path, in miniature." |

## Do not

- Do not demo live network calls; the offline mock path is the reproducible one.
- Do not show a model-authored "approved" boolean — the point is that only a human approval row unlocks execution.
- Do not apologise for the ugly UI; it is deliberately thin.
- Do not skip the audit trail: it is the strongest evidence you have.

## After recording

- [ ] Save as `projects/portfolio/demo.mp4` (or unlisted link) and reference it from the write-up.
- [ ] Paste the demo terminal output into `projects/capstone/ACCEPTANCE.md` row A2.
- [ ] Note the runtime of the demo (5 min target, 7 min hard limit).
