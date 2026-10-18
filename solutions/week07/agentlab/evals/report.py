"""Turn an ``EvalRun`` into a human-readable report and a pass/fail gate.

Two audiences, two artifacts:

- **Markdown** for the weekly review / PR description: what passed, what
  regressed, what it cost, how long it took, and which failure taxonomy
  dominated. Readable in five seconds, diffable in git.
- **The gate** for CI: ``check_baseline`` compares the current run's metrics to
  a stored baseline and returns a ``GateResult``. A gate that only prints
  numbers is decoration; this one fails closed. Missing metrics, unknown
  baselines and unmeasurable costs are failures, never "assume unchanged".

Threshold defaults follow the production-evidence guidance in
``docs/research/03-production-evals-ops.md`` §1.6: a pass^k drop larger than two
points or a p95 cost increase above 15% blocks the build.

Baseline files are plain JSON: ``EvalRun.metrics()`` written to disk. That is
the whole contract, so any run can be compared with any other run from the same
dataset version.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentlab.evals.harness import EvalRun
from agentlab.evals.judges import AgreementReport

#: Metric names the gate requires in both baseline and current run.
GATE_METRICS: tuple[str, ...] = ("pass_at_1", "pass_hat_k", "avg_cost_usd", "p95_latency_ms")


@dataclass(frozen=True, slots=True)
class GateThresholds:
    """Tolerances for baseline comparison.

    Pass metrics are compared as absolute drops (fractions, so ``0.02`` is two
    percentage points). Cost and latency are compared as relative increases,
    because their absolute scale depends on the workload.
    """

    max_pass_at_1_drop: float = 0.02
    max_pass_hat_k_drop: float = 0.02
    max_avg_cost_increase: float = 0.15
    max_p95_latency_increase: float = 0.25


DEFAULT_THRESHOLDS = GateThresholds()


@dataclass(frozen=True, slots=True)
class GateResult:
    """Outcome of a baseline comparison.

    Attributes:
        passed: ``True`` only when every metric is present and within tolerance.
        failures: one human-readable line per violated metric (empty when
            passed). These are the lines a PR comment shows verbatim.
        deltas: metric -> signed delta vs baseline (absolute for pass rates,
            relative for cost/latency).
    """

    passed: bool
    failures: tuple[str, ...] = ()
    deltas: Mapping[str, float] = field(default_factory=dict)


def _relative_increase(baseline: float, current: float) -> float:
    if baseline > 0:
        return (current - baseline) / baseline
    return 0.0 if current <= 0 else math.inf


def check_baseline(
    baseline: Mapping[str, float],
    current: Mapping[str, float],
    *,
    thresholds: GateThresholds = DEFAULT_THRESHOLDS,
) -> GateResult:
    """Compare current metrics to a baseline; fail closed on missing data.

    Contract:
        - every name in ``GATE_METRICS`` must exist in both mappings; a missing
          metric is a failure (``"missing metric: <name> in <side>"``), because
          an unverifiable metric must never count as a pass;
        - ``pass_at_1`` / ``pass_hat_k`` fail when the drop exceeds the
          threshold (equal to the threshold passes);
        - ``avg_cost_usd`` / ``p95_latency_ms`` fail when the relative increase
          exceeds the threshold; a zero baseline with a positive current value
          is an unbounded increase and fails;
        - ``deltas`` reports absolute pass-rate deltas and relative cost/latency
          deltas.
    """
    failures: list[str] = []
    deltas: dict[str, float] = {}

    for metric in GATE_METRICS:
        if metric not in baseline:
            failures.append(f"missing metric: {metric} in baseline")
        if metric not in current:
            failures.append(f"missing metric: {metric} in current")
    if failures:
        return GateResult(passed=False, failures=tuple(failures), deltas=deltas)

    for metric in GATE_METRICS:
        previous = float(baseline[metric])
        value = float(current[metric])
        if metric in ("pass_at_1", "pass_hat_k"):
            tolerance = (
                thresholds.max_pass_at_1_drop if metric == "pass_at_1" else thresholds.max_pass_hat_k_drop
            )
            drop = previous - value
            deltas[metric] = value - previous
            if drop > tolerance + 1e-12:
                failures.append(
                    f"{metric} dropped {drop:.3f} ({previous:.3f} -> {value:.3f}), tolerance {tolerance:.3f}"
                )
        else:
            tolerance = (
                thresholds.max_avg_cost_increase
                if metric == "avg_cost_usd"
                else thresholds.max_p95_latency_increase
            )
            increase = _relative_increase(previous, value)
            deltas[metric] = increase
            if increase > tolerance + 1e-12:
                failures.append(
                    f"{metric} increased {increase:.1%} ({previous:.6g} -> {value:.6g}), "
                    f"tolerance {tolerance:.0%}"
                )

    return GateResult(passed=not failures, failures=tuple(failures), deltas=deltas)


def _format_metric(metric: str, value: float) -> str:
    if metric in ("pass_at_1", "pass_hat_k"):
        return f"{value:.1%}"
    if metric in ("total_cost_usd", "avg_cost_usd"):
        return f"${value:.6f}"
    if metric in ("avg_latency_ms", "p95_latency_ms"):
        return f"{value:.1f} ms"
    if metric in ("cases", "trials"):
        return f"{int(value)}"
    return f"{value:g}"


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = math.ceil(percentile / 100.0 * len(ordered))
    return ordered[min(max(rank - 1, 0), len(ordered) - 1)]


def _render_summary(run: EvalRun) -> list[str]:
    lines = ["## Summary", "", "| Metric | Value |", "|---|---|"]
    for metric, value in run.metrics().items():
        lines.append(f"| {metric} | {_format_metric(metric, value)} |")
    return lines


def _render_gate(
    metrics: Mapping[str, float],
    baseline: Mapping[str, float],
    thresholds: GateThresholds,
) -> list[str]:
    gate = check_baseline(baseline, metrics, thresholds=thresholds)
    lines = ["", "## Baseline gate", "", "**PASS**" if gate.passed else "**FAIL**"]
    if gate.failures:
        lines.append("")
        lines.extend(f"- {failure}" for failure in gate.failures)
    return lines


def _render_calibration(agreement: AgreementReport) -> list[str]:
    disagreements = ", ".join(agreement.disagreements) or "none"
    return [
        "",
        "## Judge calibration",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| n | {agreement.n} |",
        f"| agreement | {agreement.agreement:.1%} |",
        f"| kappa | {agreement.kappa:.3f} |",
        f"| disagreements | {disagreements} |",
    ]


def _render_taxonomy(run: EvalRun) -> list[str]:
    taxonomy = run.failure_taxonomy()
    lines = ["", "## Failure taxonomy", ""]
    if not taxonomy:
        lines.append("No failures.")
        return lines
    lines.extend(["| Failure kind | Count |", "|---|---|"])
    lines.extend(f"| `{kind}` | {count} |" for kind, count in taxonomy.items())
    return lines


def _render_cases(run: EvalRun) -> list[str]:
    lines = [
        "",
        "## Cases",
        "",
        "| Case | Trials passed | Deterministic | Cost (USD) | Latency p95 (ms) | Failure |",
        "|---|---|---|---|---|---|",
    ]
    for case in run.case_results:
        passed = sum(1 for trial in case.trials if trial.passed)
        scores = [trial.deterministic_score for trial in case.trials if trial.deterministic_score is not None]
        deterministic = f"{scores[0]:.2f}" if scores else "n/a"
        cost = sum(trial.cost_usd for trial in case.trials)
        latency = _percentile([trial.latency_ms for trial in case.trials], 95.0)
        failures = sorted({trial.failure_kind for trial in case.trials if trial.failure_kind})
        failure_text = ", ".join(failures) or "—"
        lines.append(
            f"| `{case.case_id}` | {passed}/{len(case.trials)} | {deterministic} | "
            f"{cost:.6f} | {latency:.1f} | {failure_text} |"
        )
    return lines


def render_markdown(
    run: EvalRun,
    *,
    baseline: Mapping[str, float] | None = None,
    thresholds: GateThresholds = DEFAULT_THRESHOLDS,
    agreement: AgreementReport | None = None,
    generated_at: str | None = None,
) -> str:
    """Render a markdown report for one run.

    Sections (in order):
        1. title + dataset version + model;
        2. ``## Summary`` table: every key from ``EvalRun.metrics()``, with pass
           rates shown as percentages and cost/latency with units;
        3. ``## Baseline gate`` when ``baseline`` is given: ``PASS``/``FAIL``
           plus one bullet per failure from ``check_baseline``;
        4. ``## Judge calibration`` when ``agreement`` is given: agreement and
           kappa, plus the disagreement ids;
        5. ``## Failure taxonomy`` table from ``EvalRun.failure_taxonomy()``;
        6. ``## Cases`` table: id, trials passed, deterministic score, cost,
           latency, failure label.

    ``generated_at`` is optional on purpose: tests and diffs need byte-stable
    output, so an empty value means "omit the timestamp".
    """
    lines = [
        f"# Eval report — {run.dataset_version}",
        "",
        f"- **Model:** `{run.model}`",
        f"- **Cases:** {len(run.case_results)}",
        f"- **Trials per case (k):** {run.repeats}",
    ]
    if generated_at:
        lines.append(f"- **Generated:** {generated_at}")
    lines.append("")
    lines.extend(_render_summary(run))
    if baseline is not None:
        lines.extend(_render_gate(run.metrics(), baseline, thresholds))
    if agreement is not None:
        lines.extend(_render_calibration(agreement))
    lines.extend(_render_taxonomy(run))
    lines.extend(_render_cases(run))
    return "\n".join(lines) + "\n"


def write_report(path: str | Path, run: EvalRun, **options: Any) -> Path:
    """Render and write the markdown report, creating parent directories.

    ``options`` are forwarded to ``render_markdown``. Returns the written path.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(run, **options), encoding="utf-8")
    return target
