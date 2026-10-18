"""Harness tests: deterministic-first scoring, pass@1, pass^k, traces, cost."""

from __future__ import annotations

import pytest
from agentlab.errors import ConfigError
from agentlab.evals.dataset import (
    DatasetError,
    DeterministicCheck,
    EvalCase,
    EvalDataset,
    RubricCriterion,
)
from agentlab.evals.harness import (
    FAILURE_AGENT_ERROR,
    FAILURE_JUDGE,
    FAILURE_JUDGE_FORMAT,
    AgentRun,
    EvalHarness,
)
from agentlab.evals.judges import RubricJudge
from agentlab.testing import MockProvider, text_turn
from agentlab.types import Usage

pytestmark = pytest.mark.week

JUDGE_OK = '{"criteria": [{"id": "good", "score": 2, "reason": "meets the bar"}]}'


def _case(case_id: str = "case-1", text: str = "42") -> EvalCase:
    return EvalCase(
        id=case_id,
        input="what is the answer?",
        checks=[DeterministicCheck(kind="contains", params={"text": text})],
    )


def _dataset(*cases: EvalCase) -> EvalDataset:
    return EvalDataset(version="2026-10-18", cases=list(cases))


def _rubric_case(case_id: str = "rubric-1") -> EvalCase:
    return EvalCase(
        id=case_id,
        input="what is the answer?",
        rubric=[RubricCriterion(id="good", description="meets the bar")],
    )


def test_run_scores_deterministic_checks_first():
    def factory(case, tracer):
        tracer.emit("run_start", case.id)
        output = "the answer is 42" if case.id == "pass" else "the answer is 41"
        tracer.emit("run_end", case.id)
        return AgentRun(output=output)

    run = EvalHarness(factory).run(_dataset(_case("pass"), _case("fail")))

    assert run.pass_at_1() == pytest.approx(0.5)
    passing, failing = run.case_results
    assert passing.trials[0].passed is True
    assert failing.trials[0].passed is False
    assert failing.trials[0].failure_kind == "deterministic:contains"
    assert [result.kind for result in failing.trials[0].check_results] == ["contains"]
    assert failing.trials[0].check_results[0].passed is False


def test_judge_is_skipped_when_deterministic_check_fails():
    provider = MockProvider([text_turn(JUDGE_OK)])
    case = _case("c1")
    case = EvalCase(
        id=case.id,
        input=case.input,
        checks=case.checks,
        rubric=[RubricCriterion(id="good", description="meets the bar")],
    )

    run = EvalHarness(lambda case, tracer: AgentRun(output="nope"), judge=RubricJudge(provider)).run(
        _dataset(case)
    )

    trial = run.case_results[0].trials[0]
    assert trial.judge_verdict is None
    assert trial.failure_kind == "deterministic:contains"
    assert provider.calls == []


def test_judge_runs_after_checks_pass_and_gates_the_trial():
    provider = MockProvider([text_turn(JUDGE_OK)])
    case = EvalCase(
        id="c1",
        input="q",
        checks=[DeterministicCheck(kind="contains", params={"text": "42"})],
        rubric=[RubricCriterion(id="good", description="meets the bar")],
    )

    run = EvalHarness(lambda case, tracer: AgentRun(output="42"), judge=RubricJudge(provider)).run(
        _dataset(case)
    )

    trial = run.case_results[0].trials[0]
    assert trial.passed is True
    assert trial.judge_verdict is not None
    assert trial.judge_verdict.passed is True
    assert len(provider.calls) == 1


def test_low_judge_score_fails_the_trial():
    provider = MockProvider([text_turn('{"criteria": [{"id": "good", "score": 0, "reason": "no"}]}')])

    run = EvalHarness(
        lambda case, tracer: AgentRun(output="42"),
        judge=RubricJudge(provider),
    ).run(_dataset(_rubric_case()))

    trial = run.case_results[0].trials[0]
    assert trial.passed is False
    assert trial.failure_kind == FAILURE_JUDGE
    assert run.failure_taxonomy() == {FAILURE_JUDGE: 1}


def test_malformed_judge_output_is_a_failed_trial_not_a_crash():
    provider = MockProvider([text_turn("not json at all")])

    run = EvalHarness(
        lambda case, tracer: AgentRun(output="42"),
        judge=RubricJudge(provider),
    ).run(_dataset(_rubric_case()))

    trial = run.case_results[0].trials[0]
    assert trial.passed is False
    assert trial.failure_kind == FAILURE_JUDGE_FORMAT


def test_repeats_give_pass_at_1_and_pass_hat_k():
    calls = {"count": 0}

    def factory(case, tracer):
        calls["count"] += 1
        return AgentRun(output="42" if calls["count"] <= 2 else "41")

    run = EvalHarness(factory, repeats=3).run(_dataset(_case()))

    assert run.repeats == 3
    assert [trial.passed for trial in run.case_results[0].trials] == [True, True, False]
    assert run.pass_at_1() == pytest.approx(1.0)
    assert run.pass_hat_k(2) == pytest.approx(1.0)
    assert run.pass_hat_k() == pytest.approx(0.0)
    assert run.metrics()["pass_hat_k"] == pytest.approx(0.0)


def test_pass_hat_k_rejects_invalid_k():
    run = EvalHarness(lambda case, tracer: AgentRun(output="42"), repeats=2).run(_dataset(_case()))

    with pytest.raises(ValueError, match="k"):
        run.pass_hat_k(0)
    with pytest.raises(ValueError, match="k"):
        run.pass_hat_k(3)


def test_factory_exception_becomes_a_failed_trial():
    def factory(case, tracer):
        raise RuntimeError("model died mid-run")

    run = EvalHarness(factory).run(_dataset(_case()))

    trial = run.case_results[0].trials[0]
    assert trial.passed is False
    assert trial.failure_kind == FAILURE_AGENT_ERROR
    assert run.failure_taxonomy() == {FAILURE_AGENT_ERROR: 1}


def test_trace_captures_agent_events_and_eval_case_event():
    def factory(case, tracer):
        tracer.emit("run_start", case.id, {"goal": case.input})
        tracer.emit("tool_call", "search")
        return AgentRun(output="42")

    run = EvalHarness(factory).run(_dataset(_case()))

    trace = run.case_results[0].trials[0].trace
    kinds = [event.kind for event in trace]
    assert kinds[:2] == ["run_start", "tool_call"]
    assert kinds[-1] == "eval_case"
    eval_event = trace[-1]
    assert eval_event.data["passed"] is True
    assert eval_event.data["trial"] == 0
    assert eval_event.data["score"] == pytest.approx(1.0)


def test_cost_is_estimated_from_usage():
    run = EvalHarness(
        lambda case, tracer: AgentRun(output="42", usage=Usage(input_tokens=1000, output_tokens=500)),
        model="gpt-4.1-mini",
    ).run(_dataset(_case()))

    trial = run.case_results[0].trials[0]
    assert trial.cost_usd == pytest.approx(0.0012)
    assert run.metrics()["total_cost_usd"] == pytest.approx(0.0012)
    assert run.metrics()["avg_cost_usd"] == pytest.approx(0.0012)


def test_latency_metrics_use_factory_reported_values():
    run = EvalHarness(lambda case, tracer: AgentRun(output="42", latency_ms=120.0)).run(
        _dataset(_case("a"), _case("b", "43"))
    )

    metrics = run.metrics()
    assert metrics["avg_latency_ms"] == pytest.approx(120.0)
    assert metrics["p95_latency_ms"] == pytest.approx(120.0)


def test_rubric_without_judge_raises_config_error():
    with pytest.raises(ConfigError, match="judge"):
        EvalHarness(lambda case, tracer: AgentRun(output="42")).run(_dataset(_rubric_case()))


def test_run_rejects_invalid_dataset():
    with pytest.raises(DatasetError):
        EvalHarness(lambda case, tracer: AgentRun(output="42")).run(EvalDataset(version="v1", cases=[]))
