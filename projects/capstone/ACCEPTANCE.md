# Capstone Acceptance — Mini-SendOS

Fill this in as you go. Every row needs **evidence**: a command and its output, or a file/line reference. A checked box without evidence is not acceptance.

**Student:** Terrence (Yaqi) Chen · **Date started:** · **Date completed:**

## A. Automated gates

| # | Gate | Command (Windows) | Command (macOS / Linux) | Evidence (paste output summary) | Pass |
|---|---|---|---|---|---|
| A1 | Lab tests green | `.\.venv\Scripts\python.exe -m pytest tests/week09 -m week -q` | `uv run python -m pytest tests/week09 -m week -q` | | [ ] |
| A2 | Demo completes offline | `.\.venv\Scripts\python.exe scripts\demo_capstone.py` (exit code) | `uv run python scripts/demo_capstone.py` (exit code) | | [ ] |
| A3 | Foundation still green | `.\.venv\Scripts\python.exe -m pytest -q` | `uv run python -m pytest -q` | | [ ] |
| A4 | Lint clean | `.\.venv\Scripts\ruff.exe check agentlab\capstone agentlab\web tests\week09` | `uv run ruff check agentlab/capstone agentlab/web tests/week09` | | [ ] |
| A5 | Web imports without the extra | `.\.venv\Scripts\python.exe -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"` | `uv run python -c "from agentlab.web import FASTAPI_AVAILABLE; print(FASTAPI_AVAILABLE)"` | | [ ] |
| A6 | No live network in tests | grep the week09 tests for `httpx`/`requests`/real URLs | same `grep` command | | [ ] |

## B. Behavioural invariants (you write the tests)

Add these to `tests/week09/test_capstone_extra.py`, marked `pytest.mark.week`, and reference the test name as evidence.

| # | Invariant | What it proves | Test name / evidence | Pass |
|---|---|---|---|---|
| B1 | A replayed approval cannot execute twice | at-most-once execution | | [ ] |
| B2 | Editing proposal arguments after approval blocks execution | approval is bound to the action hash | | [ ] |
| B3 | A different tenant cannot resolve a tenant-scoped capability | no cross-tenant oracle | | [ ] |
| B4 | A write capability without `approval_required=True` is rejected | fail-closed catalogue | | [ ] |
| B5 | A decision that breaks presentation budgets is refused | UI contract enforced in code | | [ ] |
| B6 | Audit `seq` is strictly increasing and append-only | replayable evidence | | [ ] |

## C. Manual checks

| # | Check | Evidence | Pass |
|---|---|---|---|
| C1 | Read `audit_trail()` after the demo: the lifecycle is complete and ordered (`proposal_created` -> `approval_granted` -> `execution_started` -> `execution_finished`) | | [ ] |
| C2 | The UI (if wired) renders the typed decision and never invents prose | screenshot path | | [ ] |
| C3 | You can explain, without notes, why the proposal is persisted before approval | 150-word teach-back attached | | [ ] |
| C4 | You can explain which week's mechanism each `platform.py` method reuses | mapping table in write-up | | [ ] |

## D. Deliverables

| # | Artifact | Path | Pass |
|---|---|---|---|
| D1 | Written design + eval + cost/latency + threats | `projects/portfolio/WRITEUP.md` | [ ] |
| D2 | 5-minute demo recorded | link/path | | [ ] |
| D3 | SendOS improvement proposal (1 page) | `notes/sendos-proposal.md` | | [ ] |

## E. Sign-off

- [ ] All automated gates pass from a clean shell (no environment variables beyond `.env`).
- [ ] A senior engineer followed the demo trace from ingress to audit row without asking a question.
- [ ] The write-up states at least three limitations you know about but did not fix.

**Notes / deviations:**
