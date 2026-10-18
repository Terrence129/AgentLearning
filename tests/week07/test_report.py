"""Report tests: markdown rendering and the fail-closed baseline gate."""

from __future__ import annotations

import pytest
from agentlab.evals.harness import CaseResult, CaseTrial, EvalRun
from agentlab.evals.judges import AgreementReport
from agentlab.evals.report import (
    GATE_METRICS,
    check_baseline,
    render_markdown,
    write_report,
)

pytestmark = pytest.mark.week


def _trial(
    case_id: str,
    *,
    trial: int = 0,
    passed: bool = True,
    score: float | None = 1.0,
    cost: float = 0.001,
    latency: float = 100.0,
    failure: str | None = None,
) -> CaseTrial:
    return CaseTrial(
        case_id=case_id,
        trial=trial,
        passed=passed,
        output="answer",
        deterministic_score=score,
        cost_usd=cost,
        latency_ms=latency,
        failure_kind=failure,
    )


def _run() -> EvalRun:
    return EvalRun(
        dataset_version="2026-10-18",
        model="gpt-4.1-mini",
        repeats=1,
        case_results=[
            CaseResult(case_id="refund-001", trials=[_trial("refund-001")]),
            CaseResult(
                case_id="policy-002",
                trials=[_trial("policy-002", passed=False, failure="deterministic:contains")],
            ),
        ],
    )


def _baseline(**overrides: float) -> dict[str, float]:
    metrics: dict[str, float] = {
        "pass_at_1": 0.5,
        "pass_hat_k": 0.5,
        "avg_cost_usd": 0.001,
        "p95_latency_ms": 100.0,
    }
    metrics.update(overrides)
    return metrics


def test_render_contains_identity_and_summary():
    report = render_markdown(_run())

    assert report.startswith("# Eval report — 2026-10-18")
    assert "`gpt-4.1-mini`" in report
    assert "## Summary" in report
    assert "| pass_at_1 | 50.0% |" in report
    assert "## Cases" in report
    assert "`refund-001`" in report


def test_render_includes_failure_taxonomy():
    report = render_markdown(_run())

    assert "## Failure taxonomy" in report
    assert "| `deterministic:contains` | 1 |" in report


def test_render_omits_timestamp_by_default_but_accepts_one():
    assert "Generated" not in render_markdown(_run())
    assert "2026-10-19" in render_markdown(_run(), generated_at="2026-10-19T10:00:00Z")


def test_render_baseline_gate_fails_on_regression():
    baseline = _baseline(pass_at_1=0.9, pass_hat_k=0.9)

    report = render_markdown(_run(), baseline=baseline)

    assert "## Baseline gate" in report
    assert "**FAIL**" in report
    assert "pass_at_1 dropped" in report


def test_render_baseline_gate_passes_within_tolerance():
    baseline = _baseline(avg_cost_usd=0.0011, p95_latency_ms=110.0)

    report = render_markdown(_run(), baseline=baseline)

    assert "**PASS**" in report


def test_render_includes_judge_calibration():
    agreement = AgreementReport(n=10, agreement=0.9, kappa=0.78, disagreements=("policy-002",))

    report = render_markdown(_run(), agreement=agreement)

    assert "## Judge calibration" in report
    assert "90.0%" in report
    assert "0.780" in report
    assert "policy-002" in report


def test_check_baseline_passes_when_metrics_are_equal():
    result = check_baseline(_baseline(), _baseline())

    assert result.passed is True
    assert result.failures == ()
    assert result.deltas["pass_at_1"] == pytest.approx(0.0)


def test_check_baseline_allows_drops_within_tolerance():
    current = _baseline(pass_at_1=0.48, pass_hat_k=0.48, avg_cost_usd=0.00114, p95_latency_ms=124.0)

    result = check_baseline(_baseline(), current)

    assert result.passed is True


def test_check_baseline_fails_on_cost_regression():
    current = _baseline(avg_cost_usd=0.002)

    result = check_baseline(_baseline(), current)

    assert result.passed is False
    assert any("avg_cost_usd" in failure for failure in result.failures)
    assert result.deltas["avg_cost_usd"] == pytest.approx(1.0)


def test_check_baseline_fails_closed_on_missing_metric():
    incomplete = {"pass_at_1": 0.5, "pass_hat_k": 0.5, "avg_cost_usd": 0.001}

    result = check_baseline(incomplete, _baseline())

    assert GATE_METRICS == ("pass_at_1", "pass_hat_k", "avg_cost_usd", "p95_latency_ms")
    assert result.passed is False
    assert any("missing metric: p95_latency_ms" in failure for failure in result.failures)


def test_write_report_creates_a_file(tmp_path):
    path = write_report(tmp_path / "reports" / "week07.md", _run(), baseline=_baseline())

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Eval report")
    assert "## Baseline gate" in text
