# Week 7 — Evals and observability

Build the regression gate that turns *"it seems better"* into *"the numbers say it is better, and here is the proof"*.

## 1. Why this week exists

An agent you cannot evaluate is an agent you cannot improve. Without a versioned dataset, deterministic-first scoring and a baseline gate, every prompt change is a coin flip: regressions ship because nobody measured them, and improvements are indistinguishable from luck. This week builds the feedback loop that every later week (and the capstone release gate) depends on.

## 2. Prerequisites & time budget

- **8–10 hours** (build sessions of 2–3 h; the lab artifact needs a second sitting).
- Green: `pytest -m week` for weeks 1–6 as far as they are implemented (you only need the *types*, not the earlier agents, because this week is tested in isolation).
- Read first: [`docs/research/03-production-evals-ops.md`](../../docs/research/03-production-evals-ops.md) §1.1–1.6 (decision tree, pass@k vs pass^k, judge discipline, release gates) and §2 (trace/Observability — at least §2.1–2.2).
- Re-read: [`agentlab/trace.py`](../../agentlab/trace.py) (what a trace event is) and [`agentlab/testing/mock.py`](../../agentlab/testing/mock.py) (scripted providers: the only model calls this lab makes).

## 3. The spec

Implement everything under `agentlab/evals/`. The tests are the specification; the docstrings state the contract. Nothing here may call a network or a real model.

### `agentlab/evals/dataset.py` — cases as versioned data

| Item | Contract |
|---|---|
| `EvalCase`, `RubricCriterion`, `DeterministicCheck` | frozen value types; ids stable; checks are the closed set in `CHECK_KINDS` |
| `EvalDataset.validate() -> list[str]` | collect **all** problems (duplicate ids, unknown check kind, missing required params, non-positive weights, no checks *and* no rubric, bad threshold); never raise |
| `EvalDataset.content_digest() -> str` | SHA-256 over canonical case records, header metadata excluded |
| `dataset_to_records` / `dataset_from_records` | JSONL-ready dicts, header first; raise `DatasetError` with `.errors` |
| `load_dataset` / `save_dataset` | UTF-8 JSONL round-trip; save validates first (**fail closed**); malformed JSON names the line |

### `agentlab/evals/judges.py` — a calibrated instrument

| Item | Contract |
|---|---|
| `RubricJudge.judge(case, output) -> JudgeVerdict` | one provider call, `response_format={"type": "json_object"}`, rubric + output present in the messages; every criterion id exactly once; malformed/unknown/out-of-range output raises `SchemaValidationError` (never a partial verdict) |
| `JudgeVerdict` | weighted normalized score `sum(score·weight) / (2·sum(weight))`; `passed = score >= case.pass_threshold` |
| `agreement_rate` / `cohen_kappa` | raw and chance-corrected agreement over label sequences; `ValueError` on empty/length mismatch |
| `measure_agreement(verdicts, labels)` | pair by **case id** (never by position); report `n`, agreement, kappa, sorted disagreements |

### `agentlab/evals/harness.py` — deterministic checks first

| Item | Contract |
|---|---|
| `AgentRun` | the only agent↔harness seam: output, tool calls, steps, usage, optional latency, error |
| `EvalHarness.run(dataset) -> EvalRun` | validate dataset, run each case `repeats` times, capture a `Tracer` per trial; factory exceptions become failed trials; judge called **only after** deterministic checks pass; malformed judge output is a failed trial; each trace ends with a harness-emitted `eval_case` event |
| `CheckResult` / `CaseTrial` / `CaseResult` | per-check outcome, per-trial record, per-case roll-up (`pass_at_1`, `pass_all`) |
| `pass_at_1` / `pass_hat_k` | capability vs reliability: `pass_k` requires `k` trials; `k` outside `[1, repeats]` raises `ValueError` |
| `EvalRun.metrics()` | `cases`, `trials`, `pass_at_1`, `pass_hat_k`, `total_cost_usd`, `avg_cost_usd`, `avg_latency_ms`, `p95_latency_ms` |
| `failure_taxonomy` | failed trials grouped by `failure_kind` (`agent_error`, `deterministic:<kind>`, `judge_rubric`, `judge_format_error`) |

### `agentlab/evals/report.py` — report and CI gate

| Item | Contract |
|---|---|
| `check_baseline(baseline, current, thresholds) -> GateResult` | compares the four `GATE_METRICS`; pass drops are absolute, cost/latency are relative; a missing metric is a failure (**fail closed**) |
| `render_markdown(run, ...)` | sections: identity, Summary, Baseline gate, Judge calibration, Failure taxonomy, Cases; timestamp omitted unless `generated_at` is passed (byte-stable diffs) |
| `write_report(path, run, **options)` | render and write, creating parents |

## 4. Acceptance criteria

```powershell
# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest tests/week07 -m week -q   # must pass
.\.venv\Scripts\ruff.exe check agentlab/evals                   # must be clean
```

```bash
# macOS / Linux
uv run pytest tests/week07 -m week -q   # must pass
uv run ruff check agentlab/evals        # must be clean
```

The suite is offline and deterministic; it must finish in a handful of seconds. Then produce the **lab artifact** (not tested, but the point of the week):

1. An eval set of **≥ 25 cases** (`data/evals/…jsonl`) for the agents you built in weeks 2–6, with deterministic checks where ground truth exists and rubrics only where it does not.
2. A baseline report written from a real run, committed next to the dataset.
3. Change one prompt deliberately, find **three regressions** the gate catches, and keep one as a permanent case.
4. Calibrate the judge on **20–30 human-labelled** items and quote agreement/κ next to every judge-based metric (≥ 80% raw agreement is the bar; report κ too).

## 5. Hints (progressive)

1. **Re-read** research 03 §1.2 before writing any metric. `pass@1` is capability, `pass^k` is reliability; production cares about the second, and one repeat cannot measure it.
2. The dataset header exists so a report can answer *which expectations produced this number*: include `format` and `version`, keep case ids stable.
3. For validation, accumulate into a list and join at the end — fail-fast validation shows the learner one problem per run and hides the rest.
4. The harness's ordering rule ("deterministic checks first") is observable: the judge provider's call log must be empty for a case whose check failed. Write that assertion before the implementation.
5. Canonical JSON means `sort_keys=True` + compact separators + `ensure_ascii=False`; otherwise the digest changes when the environment does.
6. The gate compares **four** metrics. Ask what "missing baseline" should mean before deciding it is a pass — fail-safe systems treat unverifiable as failure.
7. Watch the boundary: "drop > 2 points fails" means exactly 2 points passes. Floating-point subtraction needs a tolerance, or `0.5 - 0.48` will surprise you.

## 6. Debugging guide

| Symptom | Likely cause |
|---|---|
| Every case hits `agent_error` | the factory signature is `(case, tracer) -> AgentRun`; a factory that raises inside the test shows up as a failed trial by design |
| Judge called for failing cases | deterministic checks were not run first, or `all(...)` over an empty check list was treated as failure |
| `pass^k` always 0 with `repeats=1` | `k` must equal the number of recorded trials; pass^k of 3 needs `repeats >= 3` |
| Round-trip loses `checks` | defaults were omitted on write but not re-applied on read (or vice versa); missing key means the default, not an error |
| Report changes between identical runs | a wall-clock timestamp leaked into `render_markdown`; use `generated_at` explicitly |
| Gate passes a regression | a metric was compared as relative instead of absolute (pass rates are absolute), or a missing metric was defaulted to zero |

## 7. SendOS bridge

Read-only reference (SendOS repo): the learning loop this week miniatures.

- `apps/Send.Usage.Collector/src/**/Domain/{OutcomeTraceEvent,OutcomeTraceEventType,OutcomeTraceLifecycleEvent}.cs` — append-only trace contract, closed event enum.
- `apps/Send.LowerLayer.Worker/src/.../Evaluation/Evaluator.cs` — the five-dimension evaluator.
- `apps/Send.LowerLayer.Worker/src/.../Distillation/{DistillationEngine,EvidenceGate}.cs` — evidence thresholds before a candidate is even proposed.
- `apps/Send.LowerLayer.Worker/src/.../ControlPlane/PublishingPipeline/PublishingService.cs` — submit-only promotion; AI never reaches `Published` without a human approval row.
- `docs/architecture/governance-architecture.md` §6b — the learning-loop governance contract.

Answer in your weekly notes:

1. Which parts of SendOS's evidence gate are *deterministic* and which require a judge? How does it keep the judge from becoming the system of record?
2. Your `EvalRun.metrics()` is a snapshot. What would you need to store to reproduce a publish decision months later — dataset digest, model version, judge version, something else?
3. SendOS attributes distillation insights to asset versions and drops unattributable ones. Where would your harness have to record the asset/prompt version to make the same claim?

## 8. Stretch (optional)

- **OTel exporter**: map your `TraceEvent`s to OTel GenAI `invoke_agent` / `chat` / `execute_tool` spans (pin the semconv version!) and view one run in a local collector. Note every attribute you had to guess because the spec is still `Development`.
- **Golden traces**: replay a sanitized production trace through the cassette provider as an eval fixture, and prove it fails on the prompt change that caused the incident.

## 9. Reflection (weekly review)

1. **Conceptual:** why is `pass^k` a better release gate than `pass@1`, and why can a single high `pass@1` number be actively misleading in a demo?
2. **Architectural:** where should the judge run in your architecture so that its failures are visible and its cost is bounded — inside the harness, behind a provider seam, or as an offline batch job? What did your design choose, and what breaks if you choose differently?
3. **Transfer:** pick a non-AI system you own. What is its versioned dataset, its deterministic checks, and its pass^k equivalent? What would it take to add the missing one?
