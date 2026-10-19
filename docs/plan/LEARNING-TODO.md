# Learning TODO — AgentLab, from scaffold to mastery

**Created:** 2026-10-19 (Monday) · **Plan:** [`LEARNING-PLAN.md`](LEARNING-PLAN.md) · **Gates:** [`CHECKPOINTS.md`](CHECKPOINTS.md) · **Rhythm:** [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)

**Verified starting state when this file was created**

| Check                                         | Result                                                                                                      |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Foundation suite (`pytest -q`)              | **30 passed**                                                                                         |
| Lab suite (`pytest -m week --collect-only`) | **563 collected — all red on purpose**                                                               |
| `agentlab doctor`                           | `python ok` · `.env warn` · `provider fail` (expected until week 0 is done)                         |
| Git                                           | clean tree on `main` at `aacfdc4`                                                                       |
| Machine                                      | macOS; repo at `/Users/chenyaqi/dev_repo/MyProjects/AgentLearning`; `uv` 0.13.1 + `.venv` ready (phase 0 done) |

This file is the **ordered execution list**. It does not replace the curriculum: the lab brief is the build spec, the tests are the definition of done, and [`PROGRESS.md`](PROGRESS.md) is the status tracker. Tick a box only when the evidence exists (a green command, a review note, a commit). Work one week at a time; do not start week N+1 before week N passes all three gates.

**Source of truth**

| Question                      | File                                                                   |
| ----------------------------- | ---------------------------------------------------------------------- |
| What am I building this week? | [`labs/weekNN-*/README.md`](../../labs/)                              |
| What does "done" mean?        | [`tests/weekNN/`](../../tests/) + [`CHECKPOINTS.md`](CHECKPOINTS.md) |
| What theory do I need first?  | [`docs/concepts/`](../concepts/README.md) — one note per week        |
| How do I spend the hours?     | [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md)                                |
| Where do I record evidence?   | [`PROGRESS.md`](PROGRESS.md) + `notes/weekNN-review.md`             |
| Where is the sequence?        | this file                                                              |

> **Today is 2026-10-19, the Monday that starts learning-plan week 1.** Week 0 (setup) was scheduled for 2026-10-18; do it today first — it is only 3–4 hours. If you start later, keep the 7-day cadence() and shift the dates, not the order.

---

## 0. Non-negotiable rules (all ten weeks)

- [X] **Tests are the contract.** Run the suite, read the failing test names and docstrings, then ask for help. Never read `solutions/` until your own tests are green.
- [X] **One week at a time.** A week is done only when **G + E + T** pass (§4). One grace debt maximum, cleared within 7 days; two weeks of debt means stop and clear.
- [X] **Own only this week's module.** The edit map is in [`SCAFFOLD-CONTRACT.md`](../internals/SCAFFOLD-CONTRACT.md). Do not edit `agentlab/{types,config,trace,budget,pricing,errors,cli}.py`, `agentlab/testing/*`, `agentlab/tools/registry.py`, `tests/test_core.py`, `tests/conftest.py`, `pyproject.toml`, `README.md`, `START-HERE.md`, or the plan docs.
- [X] **No live model calls in tests.** Use `MockProvider` and cassettes. Any live run must go through `agentlab.budget.Budget`; keep `AGENTLAB_RUN_BUDGET_USD=0.50`.
- [X] **One commit per step.** `week NN: <what moved>` then `week NN: gate green + review`. The git history is portfolio evidence.
- [X] **20-minute unstuck rule.** Write what you expected / what happened / what you tried; shrink it to the smallest failing test; ask for a hint, never the answer.
- [X] **70 / 20 / 10.** 70% building, 20% reading, 10% reflection. If reading exceeds 30% of a week, cut it.
- [X] **Stop at the timer**, leaving a written next step.
- [X] **Never paste SendOS source, internal URLs, tenant data, or secrets** into an external model or into this repo. The bridge is abstraction, not copy-paste.
- [X] **One tracker only:** [`PROGRESS.md`](PROGRESS.md). Do not maintain a second status system.

---

## 1. Roadmap at a glance

| Phase              | Wk  | Dates                       | Theme                                | You build                                         | Lab tests | Hours  |
| ------------------ | --- | --------------------------- | ------------------------------------ | ------------------------------------------------- | --------- | ------ |
| 0                  | 0   | 2026-10-18 (catch up 10-19) | Setup & baseline                     | Working env; one priced live call                 | 0         | 3–4   |
| 1 — Foundations   | 1   | 10-19 → 10-25              | Model & provider seam                | `agentlab/providers/openai_compat.py`           | 43        | 8–10  |
| 1 — Foundations   | 2   | 10-26 → 11-01              | Tools & the agent loop               | `agentlab/loop/`, `agentlab/tools/builtin.py` | 67        | 10–12 |
| 1 — Foundations   | 3   | 11-02 → 11-08              | Structured output                    | `agentlab/schemas/`                             | 61        | 8–10  |
| 2 — Capability    | 4   | 11-09 → 11-15              | Context & memory                     | `agentlab/context/`                             | 55        | 10–12 |
| 2 — Capability    | 5   | 11-16 → 11-22              | MCP interoperability                 | `agentlab/mcp/`                                 | 68        | 8–10  |
| 2 — Capability    | 6   | 11-23 → 11-29              | Planning & squads                    | `agentlab/orchestrator/`                        | 82        | 10–12 |
| 3 — Production    | 7   | 11-30 → 12-06              | Evals & observability                | `agentlab/evals/`                               | 48        | 8–10  |
| 3 — Production    | 8   | 12-07 → 12-13              | Security & governance                | `agentlab/guard/`                               | 93        | 8–10  |
| 3 — Production    | 9   | 12-14 → 12-20              | Capstone: Mini-SendOS                | `agentlab/capstone/`, `agentlab/web/`         | 46        | 12–16 |
| 4 — Consolidation | 10  | 12-21 → 12-27              | Portfolio, interviews, re-derivation | Evidence, not new code                            | —        | 4–6   |
| Buffer             | buf | 12-28 → 2027-01-03         | Overflow / holiday                   | —                                                | —        | —     |

**The five failure modes this curriculum exists to prevent** (keep them in view all ten weeks): treating the API as magic · an agent loop with no budget or stop condition · unvalidated model output · context that silently rots · a system you cannot evaluate, secure, or audit.

---

## 2. Phase 0 — Environment and baseline (Week 0, ~3–4 h)

Do this today. Target state: `doctor` has **no blocking problem**, the foundation is green, the lab suites are red by design, and one live call is priced.

### 2.1 Install the toolchain

- [X] Install `uv` (macOS / Linux):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  exec "$SHELL" -l        # or open a new terminal
  uv --version
  ```

  Windows equivalent: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`.
- [X] `uv python install 3.12`
- [X] `uv sync --extra dev` — creates `.venv/` and installs the pinned dev dependencies.
- [X] Or, one command: `./tasks.sh setup` (Windows: `.\tasks.ps1 setup`) — installs Python, syncs deps, creates `.env`, and runs `doctor`.
- [X] Point your editor at `.venv/bin/python` (VS Code: **Python: Select Interpreter**).

### 2.2 Configure a provider

- [X] `cp .env.example .env`
- [X] Edit `.env`: set `DEFAULT_PROVIDER=deepseek` and a real `DEEPSEEK_API_KEY=sk-...` (or `OPENAI_API_KEY`). No quotes, no spaces. **Never commit `.env`.**
- [X] `uv run python -m agentlab.cli doctor` → every row `ok`/`info`, `provider ok`.
- [X] `uv run agentlab --help` works.

### 2.3 See the starting line

- [X] `uv run pytest -q` → **30 passed** (the provided foundation; not your work).
- [X] `uv run pytest -m week -q` → **563 failed** — the whole curriculum red on purpose.
- [X] `uv run pytest tests/week01 -m week -q` → **43 failed**; that is your first lab.
- [X] `uv run agentlab chat` → prints the "Week 1 lab not implemented yet" panel (exit code 3). Correct.

### 2.4 Baseline note and ritual

- [ ] Read [`START-HERE.md`](../../START-HERE.md) §3–5, [`WEEKLY-RHYTHM.md`](WEEKLY-RHYTHM.md), [`CHECKPOINTS.md`](CHECKPOINTS.md), and weeks 0–1 of [`LEARNING-PLAN.md`](LEARNING-PLAN.md).
- [ ] Skim the repository map in [`README.md`](../../README.md) once, so you know where everything lives.
- [ ] Make **one live call** with a throwaway script or `curl`. Record model, input/output tokens, wall-clock latency, and cost (use `agentlab.pricing.estimate_cost`) in `notes/week00-baseline.md`.
- [ ] Write your baseline answers, then correct them: *What is a token? Why does streaming exist? What can go wrong in a retry?*
- [ ] Fill the week 0 row of [`PROGRESS.md`](PROGRESS.md); put three sessions in your calendar (Tue 20:00, Thu 20:00, Sat 09:00–13:00).
- [ ] `cp templates/weekly-review.md notes/week01-review.md` and leave it open all week.
- [ ] Commit: `git add -A && git commit -m "week 0: environment + baseline"`.

**Week 0 gate:** `doctor` clean · foundation 30 green · one priced live call recorded.

> **macOS vs Windows:** there are two equivalent task runners at the repo root — [`tasks.ps1`](../../tasks.ps1) for Windows PowerShell and [`tasks.sh`](../../tasks.sh) for macOS/Linux bash or zsh. They expose the same subcommands. On this machine use `./tasks.sh <task>` or the `uv` commands in §3; they are exactly what the task runners wrap. If you install PowerShell 7 (`pwsh`), `./tasks.ps1 week 1` also works, but it is not required.

---

## 3. Command reference

Default pytest behaviour excludes lab tests (`addopts = -m "not week"`); the `-m week` flag is required for any week test.

| Purpose                | macOS (this checkout)                                                                                         | Windows (`tasks.ps1`)    |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Setup                  | `./tasks.sh setup` or `uv sync --extra dev`                                                                | `.\tasks.ps1 setup`      |
| Any task runner command | `./tasks.sh <task>` (same subcommands)                                                                     | `.\tasks.ps1 <task>`     |
| Doctor                 | `uv run python -m agentlab.cli doctor`                                                                      | `.\tasks.ps1 doctor`     |
| Foundation tests       | `uv run pytest -q`                                                                                          | `.\tasks.ps1 test`       |
| One week's tests       | `uv run pytest tests/week01 -m week -q`                                                                     | `.\tasks.ps1 week 1`     |
| All lab tests          | `uv run pytest -m week -q`                                                                                  | `.\tasks.ps1 labs`       |
| One test / one file    | `uv run pytest tests/week01/test_retry.py -m week -vv`                                                      | —                         |
| Interactive chat       | `uv run agentlab chat`                                                                                      | `.\tasks.ps1 chat`       |
| Lint                   | `uv run ruff check .`                                                                                       | `.\tasks.ps1 lint`       |
| Format                 | `uv run ruff format .`                                                                                      | `.\tasks.ps1 fmt`        |
| What CI runs           | `uv run ruff check . && uv run ruff format --check . && uv run pytest -q`                                   | `.\tasks.ps1 check`      |
| Internal link check    | `uv run python scripts/check_links.py`                                                                      | same                       |
| Capstone demo          | `uv run python scripts/demo_capstone.py`                                                                    | `.\tasks.ps1`-equivalent |
| C# bridge              | `dotnet build dotnet/AgentBridgeLabs.sln` then `dotnet run --project dotnet/ProviderBridge -- --selftest` | same                       |
| Solution (last resort) | `cp -R solutions/week01/. .` then `git restore .` to undo                                                 | `.\tasks.ps1 solution 1` |

**Environment variables worth knowing**

| Variable                                       | Default                   | Meaning                                               |
| ---------------------------------------------- | ------------------------- | ----------------------------------------------------- |
| `DEFAULT_PROVIDER`                           | `deepseek`              | `deepseek` \| `openai` \| a `COMPAT_*` provider |
| `DEEPSEEK_API_KEY` / `OPENAI_API_KEY`      | —                        | provider keys; placeholders are rejected              |
| `AGENTLAB_RUN_BUDGET_USD`                    | `0.50`                  | hard ceiling per lab run — leave it on               |
| `AGENTLAB_ALLOW_NETWORK`                     | `0`                     | `1` enables `-m network` tests                    |
| `AGENTLAB_DATA_DIR` / `AGENTLAB_TRACE_DIR` | `./data` / `./traces` | runtime artifacts                                     |

---

## 4. The weekly loop and the gate

Copy this block into `notes/weekNN-review.md`, or keep it open on Saturday.

### Session A — Build A (Tue, 90–120 min)

- [ ] Five flashcards from an older week, closed book.
- [ ] Read the week's concept note (25 min): `docs/concepts/NN-*.md`.
- [ ] Skim the lab brief: `labs/weekNN-*/README.md`.
- [ ] Run the week's tests; read the first failing test's name and docstring.
- [ ] Write this block's target in one sentence.
- [ ] Implement the smallest failing test; stop at the timer with a written next step.

### Session B — Build B (Thu, 90–120 min)

- [ ] Five flashcards.
- [ ] Continue from the written next step.
- [ ] Make the lab **artifact** run end-to-end — tests green is not the same as the deliverable working.
- [ ] Close-out log: what moved, what is next, what confused me.

### Session C — Deep session (Sat, 3–4 h)

- [ ] Integration and remaining tests.
- [ ] Theory: 90 min — one must-read from the week, not a reading list.
- [ ] SendOS bridge: 30–45 min — three questions, three bullets, one open question.
- [ ] Run the gate (below).
- [ ] Weekly review + five flashcards + [`PROGRESS.md`](PROGRESS.md) + commit.
- [ ] Put next week's three sessions in the calendar.

### The gate (all three, every week)

- [ ] **G — Green:** `uv run pytest tests/weekNN -m week -q` passes, no skips/xfails, offline, under ~10 s. Foundation (`uv run pytest -q`) still green; `uv run ruff check <owned path>` clean.
- [ ] **E — Explain:** quiz `docs/plan/quizzes/weekNN.md` closed book **≥ 8/10**, plus a **150-word teach-back without notes** that names the mechanism, one failure mode it prevents, and where it lives in the code.
- [ ] **T — Transfer:** SendOS bridge note naming real C# types/files, two concrete differences, one thing you would change, and one open question you cannot answer yet.
- [ ] **Artifact:** the week's deliverable runs offline where the brief allows, emits trace events, and records cost/latency.
- [ ] **Commit:** `git commit -m "week NN: gate green + review"`.

**Minimum viable week (4–5 h, when internship/coursework explodes):** Session 1 = brief + first failing test; Session 2 = finish until green; Gate = quiz ×10 + teach-back + five cards. Skip theory, bridge, and stretch — but record them as debt. A partial week with a record beats a skipped week with none.

**If a gate fails:** diagnose *which* gate failed using [`CHECKPOINTS.md`](CHECKPOINTS.md) §4. Do not "study more" as a reflex. One grace debt maximum, cleared within 7 days; two consecutive debt weeks means stop and clear.

---

## 5. The nine labs

Each week below lists: the only files you own, what to read first, the tests that define done, the build checklist, the **artifact** (which tests do not prove), the three gates, the stretch, and the traps.

### Week 1 — The model, demystified (provider seam)

**2026-10-19 → 10-25 · 8–10 h · Owned:** `agentlab/providers/openai_compat.py` only.

**Read first:** [concept note 01](../concepts/01-agent-loop.md) · [lab brief](../../labs/week01-provider/README.md) · the OpenAI and DeepSeek chat-completions docs side by side.

**Tests (43):** [`test_request_mapping.py`](../../tests/week01/test_request_mapping.py) · [`test_response_parsing.py`](../../tests/week01/test_response_parsing.py) · [`test_retry.py`](../../tests/week01/test_retry.py) · [`test_streaming.py`](../../tests/week01/test_streaming.py)

**Build**

- [ ] `_build_payload` — model fallback; message mapping; omit unset optionals; omit empty tools; `stream_options={"include_usage": True}` when streaming; `extra` merged **last**; never mutate the request.
- [ ] `_parse_response` — first choice → assistant `Message` (text and/or tool calls); JSON arguments parsed; `Usage` including cached tokens; `finish_reason`; raw payload retained; malformed arguments or missing `choices` → `ProviderError`.
- [ ] `complete` — POST `{base_url}/chat/completions`; at most `max_retries + 1` attempts; retry 429/5xx/transport; exact numeric `Retry-After`, else exponential backoff with jitter; no retry on other 4xx; every failure becomes `ProviderError`; never leak `httpx` types.
- [ ] `stream` — SSE `data:` lines only; ignore comments/`event:`; `[DONE]` terminates; tolerate frames fragmented across chunks; forward tool-call argument fragments verbatim; emit `text` / `tool_call_delta` / `usage` and exactly one `done`; mid-stream error frames raise; no retries mid-stream.
- [ ] Prove the equivalence contract: `assemble_stream(provider.stream(req))` equals `provider.complete(req)` for the same logical response.
- [ ] **Artifact:** `uv run agentlab chat` streams one turn and prints per-turn tokens/cost; `/cost`, `/reset`, `/quit` work; compare `--stream` vs `--no-stream` on the same prompt.

**Gate**

- [ ] **G:** `uv run pytest tests/week01 -m week -q` green · `uv run pytest -q` (30) green · `uv run ruff check agentlab/providers/openai_compat.py`.
- [ ] **E:** quiz 1 ≥ 8/10; teach-back: *why retries, SSE delta assembly and usage accounting live in the provider adapter*.
- [ ] **T:** `Send.Model.Adapter` — three duties your seam shares, two it lacks (budget-aware routing, structured completion), one open question.
- [ ] Commit `week 1: provider seam green` and `week 1: review + flashcards`.

**Stretch (only after the gate):** an Anthropic adapter behind the same `Provider` protocol — different system-prompt placement, content blocks, tool schema.

**Watch-outs:** `extra` wins last · no mutation · never retry terminal 4xx · fragmented SSE frames · don't treat a `finish_reason: "length"` response as a complete answer.

---

### Week 2 — Tools and the agent loop (the most important week)

**2026-10-26 → 11-01 · 10–12 h · Owned:** `agentlab/loop/` and `agentlab/tools/builtin.py`.

**Read first:** [concept note 02](../concepts/02-tool-design.md) · [lab brief](../../labs/week02-agent-loop/README.md) · research 01 §1–2 · Anthropic *Building effective agents*.

**Tests (67):** [`test_builtin_tools.py`](../../tests/week02/test_builtin_tools.py) · [`test_loop.py`](../../tests/week02/test_loop.py) · [`test_runner.py`](../../tests/week02/test_runner.py) · [`test_stop.py`](../../tests/week02/test_stop.py)

**Build**

- [ ] `safe_eval` — whitelisted AST only: literals, parentheses, unary, `+ - * / // % **`; reject names/calls/attributes and abusive exponents; division by zero becomes a clear error.
- [ ] `FileSandbox` — `resolve`/`read_text`/`list_dir`/`write_text`/`search_text`; every path resolves under one root; absolute paths and traversal rejected; writes marked `is_write=True`; missing files are observations.
- [ ] `build_builtin_tools` — `calculator`, `read_file`, `list_dir`, `write_file`, `search_text`; pydantic schemas → JSON Schema; output truncation; `search_text` literal, skips binaries/ignored dirs, caps results.
- [ ] `run_loop` — budget check at the **top** of every iteration; model call; stop conditions; natural answer when no tool calls; execute tools; append assistant message then tool observations (success *and* failure); parallel tool calls in request order; charge budget per call; `LoopOutcome.stop_reason` ∈ `answer / budget / max_steps / error / <condition>`; emit `step`, `model_call`, `tool_call`, `tool_result` trace events.
- [ ] `AgentRunner.run` — system prompt then goal; `run_start`/`run_end`; map `LoopOutcome` → `AgentResult`; partial results survive budget/step stops.
- [ ] `stop.py` — `PredicateStop`, `FinishReasonStop`, `RepeatedToolCallStop`, `AnyOf`; first halt wins; truncation/filter ends the run rather than counting as an answer.
- [ ] **Artifact:** the five golden tasks in `test_runner.py` pass, and a live run writes `traces/week02-run.jsonl`; read it back with `agentlab.trace.load_trace` and confirm every `tool_call` has a matching `tool_result` with the same `tool_call_id`.

**Gate**

- [ ] **G:** `uv run pytest tests/week02 -m week -q` green · foundation green · `uv run ruff check agentlab/loop agentlab/tools/builtin.py`.
- [ ] **E:** quiz 2 ≥ 8/10; teach-back: *how the loop terminates, where the budget check goes, and why tool errors are observations*.
- [ ] **T:** `CapabilityDefinition`, capability registry, `DirectCapabilityHandler` — compare their typed plan with your loop; note risk level, approval requirement, read vs write.
- [ ] Commit.

**Stretch:** implement the loop twice — text-parsed ReAct and native tool calling — and write 150 words on when each is preferable.

**Watch-outs:** budget at the top, not bottom · assistant message before tool observations · unknown tool must not crash the loop · tool errors are data · `max_steps` returns partial work · no unbounded loops.

---

### Week 3 — Structured output, prompts as assets, deterministic tests

**2026-11-02 → 11-08 · 8–10 h · Owned:** `agentlab/schemas/`.

**Read first:** [concept note 03](../concepts/03-context-engineering.md) · [lab brief](../../labs/week03-structured-output/README.md) · provider structured-output docs.

**Tests (61):** [`test_structured.py`](../../tests/week03/test_structured.py) · [`test_repair.py`](../../tests/week03/test_repair.py) · [`test_prompts.py`](../../tests/week03/test_prompts.py) · [`test_decisions.py`](../../tests/week03/test_decisions.py)

**Build**

- [ ] `extract_json` — tolerate markdown fences; reject empty/invalid output.
- [ ] `response_format_for` — pydantic model → `{"type": "json_schema", ...}` strict request.
- [ ] `StructuredExtractor.extract` — versioned system prompt + schema; validate locally; on failure repair at most `max_repairs` times by feeding back the invalid output and field-level errors; return `valid=True, value=<model>` **or** `valid=False, value=None, raw=<last>, errors=[...], repairs=<n>`; record stats; provider errors propagate.
- [ ] `format_validation_errors` / `build_repair_messages` / `RepairStats` — `"field.path: message"`; statistics for clean/repaired/failed; `repair_rate` and `failure_rate` are 0.0 when empty.
- [ ] `PromptTemplate` / `PromptRegistry` — immutable `id`/`version`/`template`; missing placeholder raises; hash = sha256(id + template), version-independent; reject duplicate id+version and non-numeric versions; resolve latest numerically.
- [ ] `PresentationBudget` + decision family — headline ≤ 12 words, meaning ≤ 2 sentences, next moves ≤ 4, clarification options ≤ 3; `ActionProposal.requires_approval` is always `True`; `parse_decision` selects by `kind`, never guesses; `decision_schema()` is a discriminated union.
- [ ] **Artifact:** `analyze(text) -> Decision` over ~20 cases (scripted provider is fine) plus a one-paragraph failure-rate report from `extractor.stats` (clean / repaired / failed). Offline only; scrub cassettes before committing.

**Gate**

- [ ] **G:** `uv run pytest tests/week03 -m week -q` green · foundation green · `uv run ruff check agentlab/schemas`.
- [ ] **E:** quiz 3 ≥ 8/10; teach-back: *why JSON mode is not structured output, and how bounded repair + failure metrics work*.
- [ ] **T:** `IStructuredCompletionHandler`, `JsonSchemaValidator`, the `DecisionInteraction` family, `PresentationBudgetEnforcer` — and the validate-after vs impossible-to-emit trade-off.
- [ ] Commit.

**Stretch:** measure schema failure rate at three nesting depths; write when hand-rolled validation beats provider-native schemas.

**Watch-outs:** invalid output must **never** surface as valid · bounded repairs · provider error ≠ schema failure · prompt version bump is the immutable edit · `ActionProposal` cannot self-approve · never commit unscrubbed recorded bodies.

---

### Week 4 — Context engineering and memory

**2026-11-09 → 11-15 · 10–12 h · Owned:** `agentlab/context/`.

**Read first:** [concept note 03](../concepts/03-context-engineering.md) and [note 04](../concepts/04-memory.md) · [lab brief](../../labs/week04-context-memory/README.md) · research 01 §3–4 (read the context-rot section twice).

**Tests (55):** [`test_window.py`](../../tests/week04/test_window.py) · [`test_compaction.py`](../../tests/week04/test_compaction.py) · [`test_retrieval.py`](../../tests/week04/test_retrieval.py) · [`test_memory.py`](../../tests/week04/test_memory.py)

**Build**

- [ ] `window.py` — deterministic ~4-chars/token estimate with per-message overhead; priority classes PINNED > TASK_STATE > RECENT_TURNS > OBSERVATIONS > HISTORY; `input_budget = max_tokens - reserve_output_tokens`; newer wins within a class; insertion order preserved; duplicate ids rejected; pinned-over-budget is reported (`over_budget`), never silently dropped.
- [ ] `compaction.py` — `should_compact`; pinned items always survive; last `keep_recent_items` verbatim; stale tool observations replaced by a placeholder *before* summarising; summariser called at most once; carry-forward note prefixed with the objective and hard-truncated; invalid policy raises.
- [ ] `retrieval.py` — `[a-z0-9]+` tokenizer; deterministic blake2b signed-hashing embedder (unit-norm, zero vector for no tokens); cosine similarity with defined zero-vector/dimension behavior; word-preserving overlapping chunks ≤ `max_chars`; SQLite store records dimension (reopen mismatch raises), rejects duplicate ids/wrong lengths, exact top-k by score then id; `VectorIndex` re-index replaces a document.
- [ ] `memory.py` — bounded run-scoped working memory; append-only episodic memory with audited forget; semantic memory requiring provenance, idempotent, contradiction supersedes but keeps history, consolidation across keys, audited erase (the memory kill-switch); policy rejects short content, missing provenance, emails/API-key-shaped secrets/SSNs, unlisted kinds.
- [ ] **Artifact:** a 20-turn research task under a 12k input-token budget, with before/after cost and a retention check showing **≥ 90% of pinned constraints and task state survive every compaction**. Keep the driver local; do not edit `tests/week04/`.

**Gate**

- [ ] **G:** `uv run pytest tests/week04 -m week -q` green · foundation green · `uv run ruff check agentlab/context tests/week04`.
- [ ] **E:** quiz 4 ≥ 8/10; teach-back: *how compaction, priority classes and a retention test keep a long task coherent*.
- [ ] **T:** `Send.Context.Gateway`, the "least-context envelope" (`SpecialistContext`), the semantic retriever + pgvector adapter — data minimisation, not maximal recall.
- [ ] Commit.

**Stretch:** poison the context with a contradicting instruction and design a defence.

**Watch-outs:** pinned constraints are invariant · pruning before summarising · hard token bounds · deterministic embeddings in tests · PII/secret rejection · audited erase · retention threshold is a local invariant you define and measure, not a published benchmark.

---

### Week 5 — MCP and interoperability

**2026-11-16 → 11-22 · 8–10 h · Owned:** `agentlab/mcp/`.

> **Read the current MCP changelog before coding.** The 2026 spec is **stateless**: `initialize` and session ids are gone, `server/discover` is mandatory, and `_meta` carries version negotiation. Most tutorials still describe the removed 2025 flow. The lab tests target the current revision.

**Read first:** [concept note 05](../concepts/05-mcp-interop.md) · [lab brief](../../labs/week05-mcp/README.md) · current MCP spec + changelog · research 02 §1.

**Tests (68):** [`test_jsonrpc.py`](../../tests/week05/test_jsonrpc.py) · [`test_transport.py`](../../tests/week05/test_transport.py) · [`test_server.py`](../../tests/week05/test_server.py) · [`test_client.py`](../../tests/week05/test_client.py) · [`test_security.py`](../../tests/week05/test_security.py)

**Build**

- [ ] `jsonrpc.py` — request/notification/result/error shapes; `_meta` merged into `params`, never top level; ids string/int/absent but never float/bool; `resultType` `"complete"` / `"input_required"`; reserved codes incl. `-32022`.
- [ ] `transport.py` — in-memory transport records every message; stdio framing one JSON per line; blank lines skipped; EOF raises `TransportClosed`; `serve_stdio` survives malformed lines and converts handler errors.
- [ ] `server.py` — stateless dispatch: every request must carry `params._meta[protocolVersion]`; missing → `-32602`, unsupported → `-32022` with supported/requested; `server/discover` advertises versions/identity/capabilities/ttl; deterministic sorted `tools/list`; protocol errors vs tool-level `isError`; notifications never answered; 3 demo tools + 1 resource; `python -m agentlab.mcp.server` works over stdio.
- [ ] `client.py` — every request carries `_meta`; `discover`, `list_tools` (digests), `call_tool` (failures become observations), `read_resource`; `as_tool_registry()` makes a remote tool indistinguishable from a local one; reject `input_required` as unsupported.
- [ ] `security.py` — canonical sha-256 over `{name, description, inputSchema}`; server trust list; pin-on-first-contact then verify (mutated declaration or unpinned new tool → `ToolPoisoningError`); credential-like argument keys never cross the boundary; optional tool allowlist; checks run **before** anything is sent.
- [ ] **Artifact:** a multi-step task calling a remote tool through `MCPClient.as_tool_registry()` (local mini-loop in a script; do not import `agentlab.loop` from week-5 tests), plus a security checklist pass: trust list populated, pins persisted, no credentials in arguments, origin/tenant recorded.

**Gate**

- [ ] **G:** `uv run pytest tests/week05 -m week -q` green · foundation green · `uv run ruff check agentlab/mcp tests/week05`.
- [ ] **E:** quiz 5 ≥ 8/10; teach-back: *what MCP standardises, and the trust model that makes it safe*.
- [ ] **T:** connector manifests → registry (`ICapabilityManifestProvider`) vs MCP discovery; execution-origin stamping; where a standard protocol reduces bespoke connector surface, and where it does not.
- [ ] Commit.

**Stretch:** expose your agent over A2A and explain what the agent card must and must not reveal.

**Watch-outs:** stateless spec · `_meta` per request · notifications never answered · deterministic cacheable tool lists · pin before use · token passthrough blocked · tool errors are `isError`, not protocol crashes.

---

### Week 6 — Planning, orchestration and human approval (highest value for the day job)

**2026-11-23 → 11-29 · 10–12 h · Owned:** `agentlab/orchestrator/`.

**Read first:** [concept note 06](../concepts/06-orchestration.md) · [lab brief](../../labs/week06-squads/README.md) · research 01 §2/§6 · [`CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) §4.1/§4.5.

**Tests (82):** [`test_plan.py`](../../tests/week06/test_plan.py) · [`test_specialist.py`](../../tests/week06/test_specialist.py) · [`test_orchestrator.py`](../../tests/week06/test_orchestrator.py) · [`test_shape.py`](../../tests/week06/test_shape.py) · [`test_approval.py`](../../tests/week06/test_approval.py)

**Build**

- [ ] `plan.py` — closed kinds `capability`/`reasoning`; unique ids, known acyclic dependencies, non-empty acceptance criteria, positive budgets; deterministic Kahn topo order; replanning drops failure + transitive dependents, respects retry budget, refuses to empty the plan.
- [ ] `specialist.py` — `ContextEnvelope` (objective/facts/constraints/references, **no transcript field**); only allowlisted tools exposed; other calls become error observations without execution; budget charged; final answer must validate as a JSON hand-off (`summary` required, `confidence` in `[0,1]`); traces record `subagent_start`/`subagent_end` on a child scope, never the transcript.
- [ ] `orchestrator.py` — pure topology classifier: one capability → direct call; one reasoning → one specialist; ≥2 connected → squad; ≥2 components → multi-squad; unbacked derived shape → `shape=None`, `backed=False`, limitation names the shape and refuses to guess smaller. Execution: validate → select → short-circuit if unbacked → deterministic dependency order; failed dependency skips dependents; missing executor/specialist is reported per workstream; aggregate budget sums ledgers.
- [ ] `approval.py` — the eight invariants, tested one by one: **persisted before approval** · **exact binding** (`actor, tenant, action_hash, authority_snapshot, expires_at`) · **proposer ≠ approver** · **tenant match** · **expiry** · **authority snapshot must be covered, and current authority must still cover it at execution** · **at-most-once** (reserve `EXECUTED` before the executor; replay rejected; deterministic idempotency key; failure marks `FAILED`, never retries) · **state machine** (every illegal transition raises; every step emits a trace event).
- [ ] **Artifact:** a miniature "should we discount this deal?" flow — meta-orchestrator → 1–2 specialists → typed decision → approval-gated write → audit row — plus your own test (outside `tests/week06/`) proving an edited, replayed, or expired approval cannot execute.

**Gate**

- [ ] **G:** `uv run pytest tests/week06 -m week -q` green · foundation green · `uv run ruff check agentlab/orchestrator tests/week06`.
- [ ] **E:** quiz 6 ≥ 8/10; teach-back: *why approval must bind to an action hash and an authority snapshot, and what at-most-once requires*.
- [ ] **T:** decision-first runtime, `ExecutionPlan`, `ExecutionShape`, `ApprovalCheckpoint`, `EffectiveAuthority`, ADR-0001 — this is the week to demo to your team.
- [ ] Commit.

**Stretch:** durable suspend/resume (SQLite + resume on callback, CAS against double-resume). This is the credible contribution proposal.

**Watch-outs:** persistence before approval · no self-approval · authority can only narrow · replay rejected · edit-after-approval blocked by hash · never downgrade an unbacked shape · specialists never receive full transcripts.

---

### Week 7 — Evals and observability (highest-risk week — no prior eval culture)

**2026-11-30 → 12-06 · 8–10 h · Owned:** `agentlab/evals/`.

**Read first:** [concept note 07](../concepts/07-evals-observability.md) · [lab brief](../../labs/week07-evals/README.md) · research 03 §1–2 · Hamel Husain on evals.

**Tests (48):** [`test_dataset.py`](../../tests/week07/test_dataset.py) · [`test_harness.py`](../../tests/week07/test_harness.py) · [`test_judges.py`](../../tests/week07/test_judges.py) · [`test_report.py`](../../tests/week07/test_report.py)

**Build**

- [ ] `dataset.py` — frozen case/rubric/check types; `validate()` collects **all** problems and never raises; `content_digest()` excludes header metadata; JSONL header-first round-trip; `save` validates first (fail closed); malformed JSON names the line.
- [ ] `judges.py` — `RubricJudge.judge` forces `response_format={"type": "json_object"}`, sends rubric + output, requires every criterion exactly once, and treats malformed/unknown/out-of-range output as `SchemaValidationError` (never a partial verdict); weighted normalized score; `agreement_rate` / `cohen_kappa`; `measure_agreement` pairs by **case id**, never position.
- [ ] `harness.py` — `AgentRun` seam; run each case `repeats` times with a per-trial `Tracer`; factory exceptions become failed trials; deterministic checks first, judge **only after** checks pass; malformed judge output = failed trial; each trace ends with an `eval_case` event; `pass@1` vs `pass^k` (`k` outside `[1, repeats]` raises); metrics incl. cost and p95 latency; failure taxonomy.
- [ ] `report.py` — markdown/HTML report with identity, summary, failure taxonomy, judge calibration, and a baseline gate that **fails closed on a missing metric**.
- [ ] **Artifact:** an eval set of **≥ 25 cases** in `data/evals/*.jsonl` for the agents from weeks 2–6; a committed baseline report from a real run; one deliberate prompt change that finds **three regressions**, keeping one as a permanent case; judge calibrated on **20–30 human-labelled** items with **≥ 80% raw agreement** and κ quoted.

**Gate**

- [ ] **G:** `uv run pytest tests/week07 -m week -q` green · `uv run ruff check agentlab/evals`.
- [ ] **E:** quiz 7 ≥ 8/10; teach-back: *how to build an eval suite that catches a regression before production (pass@1 vs pass^k)*.
- [ ] **T:** `Outcome_Trace` append-only contract, the 5-dimension `Evaluator`, the `Distillation`/`Trainer` learning loop, the publish gate; note where trace→candidate→publish is unwired.
- [ ] Commit.

**Stretch:** OTel exporter for your trace events, viewed in a local collector.

**Watch-outs:** deterministic checks first · judge is not a substitute for ground truth · pass^k ≠ pass@1 · pair labels by case id · fail closed on missing baseline metric · no network in tests.

---

### Week 8 — Security, governance, cost, reliability

**2026-12-07 → 12-13 · 8–10 h · Owned:** `agentlab/guard/` (errors and the attack corpus are provided — do not weaken the corpus).

**Read first:** [concept note 08](../concepts/08-security-governance.md) · [lab brief](../../labs/week08-security/README.md) · research 03 §3–7 · OWASP GenAI Top 10 2026.

**Tests (93):** [`test_injection.py`](../../tests/week08/test_injection.py) · [`test_sandbox.py`](../../tests/week08/test_sandbox.py) · [`test_authority.py`](../../tests/week08/test_authority.py) · [`test_audit.py`](../../tests/week08/test_audit.py) · [`test_ratelimit.py`](../../tests/week08/test_ratelimit.py) · [`test_routing.py`](../../tests/week08/test_routing.py) · [`test_attacks.py`](../../tests/week08/test_attacks.py)

**Build**

- [ ] `injection.py` — wrap/delimit untrusted content (escape delimiter spoofing, strip zero-width); normalized rule scan with findings sorted by position; screen with risk = max severity, always return the sanitized wrapped form; guarded messages state the instruction hierarchy with untrusted items as labelled data; output vetting redacts secrets/external images/data channels; lethal-trifecta assessment: 3 legs ⇒ critical, 2 ⇒ elevated, 3 legs with no mitigation ⇒ **blocked**, unknown mitigation raises.
- [ ] `sandbox.py` — URL-decode once, then reject empty/absolute/UNC/NUL/`..`; resolve and require containment in an allowed root; oversize file refused before loading; command allowlist, no shell, hard timeout, truncated output; `action_hash(tool, args)` canonical; `ApprovalLedger.consume` refuses expiry/replay; read tools no-op, write tools need a token matching tenant + exact action.
- [ ] `authority.py` — `effective_authority` = intersection over matching boundaries (platform-wide `None` applies to all tenants); no boundary ⇒ no grants; model claims never add grants and are recorded in `denied_claims`; empty tenant raises; delegation is a non-empty subset; caller credentials refused/stripped case-insensitively.
- [ ] `audit.py` — append-only JSONL with monotonic sequence + hash chain; update/delete rejected and recorded; tampered log fails integrity check; correlation ids link before/after evidence.
- [ ] `ratelimit.py` / `routing.py` — tenant-isolated token/cost quotas; route by price, declared order, per-request budget, latency, reliability, remaining budget; **fail closed** when no candidate is viable; fall back only on transient failures; never retry cancellation; charge successful calls to the budget.
- [ ] **Artifact:** `projects/security/SECURITY.md` threat model (lethal-trifecta audit, data flows, controls, residual risks, what you would not claim); a before/after table where every corpus attack moves from "succeeds" to "blocked"; one write action wired proposal → approval → sandbox → audit row with before/after evidence and one correlation id.

**Gate**

- [ ] **G:** `uv run pytest tests/week08 -m week -q` green · `uv run ruff check agentlab/guard`.
- [ ] **E:** quiz 8 ≥ 8/10; teach-back: *why indirect injection is assumed to succeed, and how authority/sandbox/audit limit the blast radius*.
- [ ] **T:** the governance sandwich, `EffectiveAuthority` nine-source intersection, licensing/quota at ingress, execution origin — understand why each control exists, not the code.
- [ ] Commit.

**Stretch:** write a one-page threat-model review of the SendOS approval path and send it to a senior engineer for critique.

**Watch-outs:** model output can never widen authority · deny by default · sandbox path traversal (encoded too) · audit tamper detection · token passthrough is case-insensitive · write actions require approval + audit · routing fails closed.

---

### Week 9 — Capstone: Mini-SendOS

**2026-12-14 → 12-20 · 12–16 h · Owned:** `agentlab/capstone/`, `agentlab/web/`, `tests/week09/test_capstone_extra.py`, `projects/capstone/`, `projects/portfolio/`.

**Read first:** [concept note 09](../concepts/09-production.md) · [lab brief](../../labs/week09-capstone/README.md) · [`projects/capstone/README.md`](../../projects/capstone/README.md) · [`ACCEPTANCE.md`](../../projects/capstone/ACCEPTANCE.md).

**Tests (46):** [`test_catalogue.py`](../../tests/week09/test_catalogue.py) · [`test_decisions.py`](../../tests/week09/test_decisions.py)

**Build in this order (do not reorder)**

- [ ] `uv run python scripts/demo_capstone.py` — read the `DEMO BLOCKED` list; it names the first gap.
- [ ] `decisions.py` — `parse_decision`, `decision_to_wire`, `enforce_presentation_budgets`; validate fully before raising; closed union rejects unknown kinds/fields; collect **all** budget violations into one error.
- [ ] `catalogue.py` — `CapabilityDefinition`; `merge(connectors, published)` validates both sources, rejects duplicates within a source, published wins whole-definition on conflict, order-independent; `resolve` makes unknown and forbidden indistinguishable (no cross-tenant oracle); `list_for_tenant` sorted; fail closed on empty tenant, non-object schema, bad risk, **write without approval**, empty tenant scope.
- [ ] `platform.py` — `action_digest` + the five lifecycle methods: typed decision → capability check → persisted proposal → bound approval → at-most-once execution → append-only audit rows.
- [ ] `web/app.py` wiring — `create_app(platform)`; graceful when FastAPI is absent.
- [ ] **Artifact:** `tests/week09` green (plus your own invariants: cross-tenant, replay, edit-after-approval in `tests/week09/test_capstone_extra.py`); `scripts/demo_capstone.py` exits `0` offline and prints the full audit sequence; `FASTAPI_AVAILABLE` imports without FastAPI; `ACCEPTANCE.md` filled with command output; `WRITEUP.md` 800–1,500 words; a 5-minute recorded demo.

**Gate**

- [ ] **G:** `uv run pytest tests/week09 -m week -q` green · `uv run pytest -q` foundation green · demo exits 0 · `uv run ruff check agentlab/capstone agentlab/web tests/week09`.
- [ ] **E:** quiz 9 ≥ 8/10; *draw the request path from ingress to audit row aloud, naming every failure mode and its control*.
- [ ] **T:** one-page SendOS improvement proposal grounded in the build (recommended: durable suspend/resume for approvals, or trace→candidate evidence gating).
- [ ] Commit.

**Stretch:** a live-provider web UI run (tests stay offline/mock).

**Watch-outs:** demo first, then code in build order · no network in the flow · two tenants cannot see each other's capabilities · replay cannot execute twice · edit-after-approval blocks on hash mismatch · ship at 80% — demo + write-up beats polish.

---

## 6. Week 10 — Consolidation and leverage

**2026-12-21 → 12-27 · 4–6 h · No new mechanisms.**

- [ ] **Re-derive from a blank file:** the agent loop, MCP discovery flow, eval design, and approval state machine. Compare to your code; gaps are your study list.
- [ ] Retake all ten quizzes closed book; every score ≥ 8/10.
- [ ] Finish [`projects/portfolio/WRITEUP.md`](../../projects/portfolio/WRITEUP.md) and the [`DEMO-CHECKLIST.md`](../../projects/portfolio/DEMO-CHECKLIST.md).
- [ ] Draft **two deep-dive posts** (e.g. "approval binding is a security mechanism", "why pass^k beats pass@1").
- [ ] Answer all **30 interview questions** in [`INTERVIEW.md`](INTERVIEW.md) aloud, 60–90 s each, before reading model answers.
- [ ] Get the one-page SendOS proposal reviewed by a senior engineer; record the feedback.
- [ ] Decide the next step: framework fluency (LangGraph / Microsoft Agent Framework), the learning loop (trace→eval→candidate→publish), or agentic RL/post-training.
- [ ] Do the end-of-course evidence check (§8) and commit `week 10: portfolio + consolidation`.

---

## 7. Cross-cutting mastery track (the 20% reading time)

These are not a separate project. Do them in the reading block of the week that needs them.

- [ ] **Understand the provided primitives before week 2.** Read [`tests/test_core.py`](../../tests/test_core.py), then `agentlab/types.py`, `trace.py`, `budget.py`, `pricing.py`, `config.py`, `errors.py`, `testing/mock.py`, `testing/cassettes.py`, and `tools/registry.py`. Be able to say what each primitive guarantees.
- [ ] **Read the scaffold contract once.** [`SCAFFOLD-CONTRACT.md`](../internals/SCAFFOLD-CONTRACT.md) explains ownership, the independence rule, and why tests are marked `pytest.mark.week`. It also tells you exactly which files are off-limits.
- [ ] **Understand the test harness.** Why lab tests carry `pytestmark = pytest.mark.week`, why `pyproject.toml` excludes them by default, and why `-m week` is required. Read `tests/conftest.py` and the fixtures in `tests/week01/conftest.py`.
- [ ] **Read the repo mechanics.** `pyproject.toml` (deliberately small dependency set + extras), `.github/workflows/ci.yml`, `tasks.ps1` (Windows runner) and `tasks.sh` (macOS/Linux runner), `scripts/check_links.py`, and `scripts/demo_capstone.py`. You should be able to reproduce CI locally with the command in §3.
- [ ] **Read each concept note just-in-time** (`docs/concepts/01`–`09`), never cover-to-cover. Answer its five questions before and after the lab.
- [ ] **Read research reports by section, not end-to-end.** Use the appendix mapping in [`LEARNING-PLAN.md`](LEARNING-PLAN.md) §Appendix. Check the uncertainty registers before quoting numbers.
- [ ] **Use the companion textbook optionally.** [`CHAPTER-MAP.md`](../books/ai-agents-in-depth/CHAPTER-MAP.md) has 6 h / 20 h / 60 h reading paths. It never replaces a lab.
- [ ] **Run the C# bridge labs in weeks 1 and 3.** `dotnet build dotnet/AgentBridgeLabs.sln`, then `dotnet run --project dotnet/ProviderBridge -- --selftest` and `dotnet run --project dotnet/StructuredDecisionBridge -- --selftest`. Read the headers; they map line-by-line to SendOS.
- [ ] **Read SendOS docs privately and weekly.** [`CONCEPT-MAP.md`](../sendos/CONCEPT-MAP.md) §0–1 once; [`BRIDGE.md`](../sendos/BRIDGE.md) for each week's 30-minute bridge. Code wins over docs; record the five known drifts.
- [ ] **Use the glossary for retrieval.** [`glossary.md`](../glossary.md) has ~120 terms; read only the week's group and cover the definition column.
- [ ] **Write 2–3 ADRs** from [`templates/adr.md`](../../templates/adr.md) for decisions you want to defend (e.g. "why provider seam owns retries", "why approval binds to a hash").
- [ ] **Keep the repo healthy:** `uv run ruff check .`, `uv run ruff format --check .`, `uv run python scripts/check_links.py`, and the CI command in §3. These are what CI runs.
- [ ] **Read your own git history at week 10.** One commit per step is what makes the portfolio story legible.

---

## 8. Definition of mastery (the final exam)

A week is not "done" because tests pass. You are done when all of the following are true.

### Evidence checklist

- [ ] 9 weekly reviews in `notes/`, each with a 150-word teach-back and a failure log.
- [ ] 8 green week suites (weeks 1–8) + the capstone (week 9).
- [ ] All 10 quizzes ≥ 8/10, closed book.
- [ ] ≥ 140 flashcards reviewed at least twice (the prefilled decks in [`flashcards/`](flashcards/) hold ~15 per week; add the five you create in the weekly ritual).
- [ ] Eval report with baseline, pass^k, judge agreement/κ, and failure taxonomy.
- [ ] Capstone demo runs offline; 5-minute recording exists.
- [ ] [`WRITEUP.md`](../../projects/portfolio/WRITEUP.md) complete; two deep-dive posts drafted.
- [ ] One-page SendOS improvement proposal reviewed by a senior engineer.
- [ ] All 30 interview questions answered aloud at least once.
- [ ] Re-derivation exercises done from a blank file (loop, MCP discovery, eval design, approval state machine).
- [ ] You own roughly 4–6k lines of tested Python and can point to the test that would fail if any mechanism were removed.

### The ten claims you must be able to make without notes (90 seconds each)

| Wk | Claim                                                                                                | ☐ |
| -- | ---------------------------------------------------------------------------------------------------- | -- |
| 1  | Why retries, SSE delta assembly and usage accounting live in the provider adapter                    | ☐ |
| 2  | How the loop terminates, where the budget check goes, and why tool errors are observations           | ☐ |
| 3  | Why JSON mode is not structured output, and how bounded repair + failure metrics work                | ☐ |
| 4  | How compaction, priority classes and a retention test keep a long task coherent                      | ☐ |
| 5  | What MCP standardises, and the trust model that makes it safe                                        | ☐ |
| 6  | Why approval must bind to an action hash and an authority snapshot, and what at-most-once requires   | ☐ |
| 7  | How to build an eval suite that catches a regression before production (pass@1 vs pass^k)            | ☐ |
| 8  | Why indirect injection is assumed to succeed, and how authority/sandbox/audit limit the blast radius | ☐ |
| 9  | The full request path from ingress to audit row, with every failure mode and control                 | ☐ |
| 10 | The four runtime duties, and how SendOS maps onto them                                               | ☐ |

### The five things you should be able to do cold

- [ ] Draw the request path of an agent run from ingress to audit row, naming every failure mode and its control.
- [ ] Explain approval binding and what breaks without an action hash + authority snapshot.
- [ ] Design an eval suite that would catch a prompt regression before production, including pass^k reasoning.
- [ ] Read a new agent framework's source and map its abstractions onto the primitives you built.
- [ ] Read SendOS's `DecisionRuntime` / `ApprovalCheckpoint` / `Model.Adapter` and propose a concrete improvement.

---

## 9. Stop rules and anti-patterns

| Anti-pattern                              | Why it costs you                                                   | Replacement                                                              |
| ----------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| Reading `solutions/` before green       | Removes the productive struggle and the ability to defend the code | Diff only after the gate; then write one design difference               |
| Editing the tests to make them pass       | Destroys the specification                                         | Fix the code; if you believe a test is wrong, report it, don't weaken it |
| Starting week N+1 early                   | Week N+1 silently assumes week N's abstractions                    | One grace debt max, cleared in 7 days                                    |
| "Study more" when a gate fails            | The remedies differ by gate                                        | Diagnose G / E / T and apply the matching fix in `CHECKPOINTS.md` §4  |
| Tutorial rabbit hole / framework shopping | Frameworks are weeks 6–9 comparison material, not prerequisites   | Build the loop first; cap reading at 20%                                 |
| Polishing the capstone                    | Shipping beats polish                                              | Demo + write-up + eval report at 80%                                     |
| Silent struggle                           | Self-study dies in silence                                         | 20-minute rule; write the question, ask for a hint                       |
| Unbounded live loops                      | Cost and safety                                                    | `Budget` on every live run; keep `$0.50`                             |
| Pasting SendOS code/data                  | Confidentiality breach; also not transferable                      | Describe mechanisms in your own words                                    |
| A second status tracker                   | Two sources of truth drift                                         | This file for sequence, [`PROGRESS.md`](PROGRESS.md) for status         |

---

## 10. Phase tracker

Tick only when the phase gate is fully passed. Details belong in [`PROGRESS.md`](PROGRESS.md).

| Phase              | Weeks | Exit condition                                                     | Done |
| ------------------ | ----- | ------------------------------------------------------------------ | ---- |
| 0 — Setup         | 0     | `doctor` clean, foundation green, one priced live call           | ☐   |
| 1 — Foundations   | 1–3  | Weeks 1–3 G+E+T; provider seam, loop, typed output all green      | ☐   |
| 2 — Capability    | 4–6  | Weeks 4–6 G+E+T; context, MCP, approval-gated squad all green     | ☐   |
| 3 — Production    | 7–9  | Weeks 7–9 G+E+T; eval gate, attack suite, capstone demo offline   | ☐   |
| 4 — Consolidation | 10    | Blank-file re-derivation, portfolio, interviews, reviewed proposal | ☐   |

**Next action right now:** §2.1 — install `uv`, then run `uv sync --extra dev` and `uv run pytest -q`. Everything else follows.
