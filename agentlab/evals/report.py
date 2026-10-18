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
    raise NotImplementedError("Week 7 lab: implement check_baseline")


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
    raise NotImplementedError("Week 7 lab: implement render_markdown")


def write_report(path: str | Path, run: EvalRun, **options: Any) -> Path:
    """Render and write the markdown report, creating parent directories.

    ``options`` are forwarded to ``render_markdown``. Returns the written path.
    """
    raise NotImplementedError("Week 7 lab: implement write_report")
