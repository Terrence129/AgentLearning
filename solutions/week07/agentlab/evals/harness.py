"""Run an agent over a dataset, capture traces, score with checks first.

The harness is the bridge between "a script that runs my agent" and "a
regression gate". It does five things, in this order, for every trial:

1. calls an **agent factory** with the case and a fresh ``Tracer``;
2. captures the trace (the factory emits events; the harness records them);
3. evaluates the case's deterministic checks -- these run first and always;
4. only if those pass, asks the rubric judge (a model call costs money and is
   the least trustworthy part of the pipeline);
5. records cost, latency and a failure label for the taxonomy.

Failure policy: an exception from the factory becomes a *failed trial*
(``failure_kind="agent_error"``), not an aborted eval run. One broken case must
not hide the other 24 results -- the same reason production collectors drop bad
spans instead of dropping the trace.

Repeat policy: pass@1 answers "can it do this at all?"; pass^k answers "does it
do this every time?". Run each case ``repeats`` times and report both. See
``docs/research/03-production-evals-ops.md`` §1.2.

Read first: ``agentlab/trace.py`` (what a trace event is) and
``agentlab/testing/mock.py`` (how the factories in the tests are scripted).
"""

from __future__ import annotations

import math
import re
import time
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from agentlab.errors import ConfigError, SchemaValidationError
from agentlab.evals.dataset import DatasetError, EvalCase, EvalDataset
from agentlab.evals.judges import Judge, JudgeVerdict
from agentlab.pricing import ModelPrice, estimate_cost
from agentlab.trace import MemorySink, TraceEvent, Tracer
from agentlab.types import ToolCall, Usage

#: Failure label for an exception escaping the agent factory.
FAILURE_AGENT_ERROR = "agent_error"
#: Failure label for a judge score below the case's ``pass_threshold``.
FAILURE_JUDGE = "judge_rubric"
#: Failure label for a judge that did not return parseable, valid JSON.
FAILURE_JUDGE_FORMAT = "judge_format_error"


@dataclass(slots=True)
class AgentRun:
    """What an agent factory returns for one case.

    The harness knows nothing about loops, prompts or providers: this is the
    entire seam between an agent and its evaluation. Keep it small.

    Attributes:
        output: the final answer text shown to the user.
        tool_calls: every tool call the run made, in order.
        steps: agent loop iterations (efficiency metric).
        usage: token usage for the run (cost is derived from it).
        latency_ms: wall-clock time. ``None`` means "the factory did not
            measure it; harness, please measure".
        error: set when the run failed; the harness records it as a failed
            trial instead of raising.
    """

    output: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    steps: int = 0
    usage: Usage = field(default_factory=Usage)
    latency_ms: float | None = None
    error: str | None = None


#: ``(case, tracer) -> AgentRun``. The harness owns the tracer; the agent emits
#: ``run_start`` / ``step`` / ``model_call`` / ``tool_call`` events into it.
AgentFactory = Callable[[EvalCase, Tracer], AgentRun]


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Outcome of one deterministic check.

    Attributes:
        kind: the check kind from the dataset (``contains``, ``max_steps``, ...).
        passed: whether the observed run satisfied the expectation.
        detail: human-readable explanation used in reports, e.g.
            ``"output missing 'REFUND-42'"``.
        weight: relative importance in the deterministic score.
    """

    kind: str
    passed: bool
    detail: str
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class CaseTrial:
    """One execution of one case.

    Attributes:
        case_id: dataset case id.
        trial: zero-based repeat index.
        passed: deterministic checks all pass AND, when a judge ran, the rubric
            score reached the case's ``pass_threshold``.
        output: final answer text.
        deterministic_score: weighted fraction of checks that passed, in
            ``[0, 1]``; ``None`` when the case has no deterministic checks.
        check_results: per-check outcomes, in declaration order.
        judge_verdict: judge output; ``None`` when the judge did not run.
        cost_usd: estimated cost of this trial.
        latency_ms: wall-clock milliseconds for this trial.
        failure_kind: taxonomy label for failures (see ``FAILURE_*``), ``None``
            when the trial passed.
        trace: captured trace events, including the harness's ``eval_case`` event.
    """

    case_id: str
    trial: int
    passed: bool
    output: str = ""
    deterministic_score: float | None = None
    check_results: tuple[CheckResult, ...] = ()
    judge_verdict: JudgeVerdict | None = None
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    failure_kind: str | None = None
    trace: tuple[TraceEvent, ...] = ()
    usage: Usage = field(default_factory=Usage)


@dataclass(slots=True)
class CaseResult:
    """All trials for one case. Metrics are computed from the trial list."""

    case_id: str
    trials: list[CaseTrial]

    @property
    def pass_at_1(self) -> bool:
        """Whether the *first* trial passed (the single-attempt capability)."""
        return bool(self.trials) and self.trials[0].passed

    @property
    def pass_all(self) -> bool:
        """Whether every recorded trial passed (the reliability view)."""
        return bool(self.trials) and all(trial.passed for trial in self.trials)


@dataclass(slots=True)
class EvalRun:
    """The scored dataset: per-case trials plus the numbers a gate compares.

    Attributes:
        dataset_version: version of the dataset that was scored.
        model: model name used for pricing this run.
        repeats: trials per case (``k``).
        case_results: one result per dataset case, in dataset order.
    """

    dataset_version: str
    model: str
    repeats: int
    case_results: list[CaseResult]

    def pass_at_1(self) -> float:
        """Fraction of cases whose first trial passed, in ``[0, 1]``."""
        return pass_at_1(self.case_results)

    def pass_hat_k(self, k: int | None = None) -> float:
        """Fraction of cases where *all* of the first ``k`` trials passed.

        Fraction of cases where all *k* trials passed, i.e. reliability. Defaults
        to ``k=self.repeats``. Raises ``ValueError`` for ``k`` outside
        ``[1, repeats]``.
        """
        return pass_hat_k(self.case_results, self.repeats if k is None else k)

    def total_cost_usd(self) -> float:
        """Sum of estimated cost over every trial."""
        return sum(trial.cost_usd for case in self.case_results for trial in case.trials)

    def latency_percentile(self, percentile: float) -> float:
        """Nearest-rank percentile of trial latencies, in milliseconds.

        ``percentile`` is in ``(0, 100]``; raises ``ValueError`` otherwise.
        """
        if not (0 < percentile <= 100):
            raise ValueError(f"percentile must be in (0, 100], got {percentile!r}")
        latencies = sorted(trial.latency_ms for case in self.case_results for trial in case.trials)
        if not latencies:
            raise ValueError("cannot compute a latency percentile for zero trials")
        rank = math.ceil(percentile / 100.0 * len(latencies))
        index = min(max(rank - 1, 0), len(latencies) - 1)
        return latencies[index]

    def metrics(self) -> dict[str, float]:
        """Flat metric dict, the contract used by report gates and baselines.

        Keys (all floats): ``cases``, ``trials``, ``pass_at_1``, ``pass_hat_k``,
        ``total_cost_usd``, ``avg_cost_usd`` (per case), ``avg_latency_ms``,
        ``p95_latency_ms``.
        """
        trials = [trial for case in self.case_results for trial in case.trials]
        total_cost = self.total_cost_usd()
        case_count = len(self.case_results)
        trial_count = len(trials)
        return {
            "cases": float(case_count),
            "trials": float(trial_count),
            "pass_at_1": self.pass_at_1(),
            "pass_hat_k": self.pass_hat_k(),
            "total_cost_usd": total_cost,
            "avg_cost_usd": total_cost / case_count if case_count else 0.0,
            "avg_latency_ms": (
                sum(trial.latency_ms for trial in trials) / trial_count if trial_count else 0.0
            ),
            "p95_latency_ms": self.latency_percentile(95.0),
        }

    def failure_taxonomy(self) -> dict[str, int]:
        """Count of failed trials per ``failure_kind``, sorted by label."""
        return failure_taxonomy(self.case_results)


def pass_at_1(case_results: Sequence[CaseResult]) -> float:
    """Capability metric: fraction of cases passing on the first attempt."""
    if not case_results:
        raise ValueError("cannot compute pass@1 for zero cases")
    return sum(1 for case in case_results if case.pass_at_1) / len(case_results)


def pass_hat_k(case_results: Sequence[CaseResult], k: int) -> float:
    """Reliability metric: fraction of cases where all first ``k`` trials passed."""
    if not case_results:
        raise ValueError("cannot compute pass^k for zero cases")
    if k < 1:
        raise ValueError(f"k must be >= 1 for pass^k, got {k}")
    for case in case_results:
        if len(case.trials) < k:
            raise ValueError(
                f"pass^k needs at least {k} trials per case; case {case.case_id!r} has {len(case.trials)}"
            )
    reliable = sum(1 for case in case_results if all(trial.passed for trial in case.trials[:k]))
    return reliable / len(case_results)


def failure_taxonomy(case_results: Sequence[CaseResult]) -> dict[str, int]:
    """Group failed trials by ``failure_kind`` so a report can rank root causes."""
    counts: Counter[str] = Counter()
    for case in case_results:
        for trial in case.trials:
            if trial.passed:
                continue
            counts[trial.failure_kind or "unknown"] += 1
    return dict(sorted(counts.items()))


class EvalHarness:
    """Scores an agent factory over a dataset.

    The harness is deliberately provider-agnostic: the factory may call any
    model or no model at all. Injecting the judge makes the "deterministic
    checks first" rule observable -- the judge provider is simply never called
    for a case whose checks failed.

    Args:
        agent_factory: builds the run for one case, emitting trace events into
            the supplied tracer.
        judge: optional rubric judge; required when any case has rubric criteria.
        model: model name used for cost estimation.
        prices: optional price overrides for ``agentlab.pricing``.
        repeats: trials per case (``k`` for pass^k). Must be >= 1.
    """

    def __init__(
        self,
        agent_factory: AgentFactory,
        *,
        judge: Judge | None = None,
        model: str = "mock-1",
        prices: dict[str, ModelPrice] | None = None,
        repeats: int = 1,
    ) -> None:
        if repeats < 1:
            raise ValueError(f"repeats must be >= 1, got {repeats}")
        self.agent_factory = agent_factory
        self.judge = judge
        self.model = model
        self.prices = prices
        self.repeats = repeats

    def run(self, dataset: EvalDataset) -> EvalRun:
        """Score every case in ``dataset``, ``repeats`` times each.

        Rules:
            - invalid datasets raise ``DatasetError`` before any model call;
            - a dataset case with rubric criteria but no configured judge raises
              ``ConfigError``;
            - factory exceptions become failed trials (``FAILURE_AGENT_ERROR``);
            - deterministic checks run first; the judge is called only when they
              all pass (and only for cases that have rubric criteria);
            - malformed judge output raises ``SchemaValidationError`` inside the
              judge and becomes ``FAILURE_JUDGE_FORMAT`` on the trial, not an
              aborted run;
            - every trial's trace ends with a harness-emitted ``eval_case`` event
              carrying ``{"trial", "passed", "score"}``.

        Returns an ``EvalRun`` in dataset order.
        """
        validation_errors = dataset.validate()
        if validation_errors:
            raise DatasetError(
                f"cannot score an invalid dataset ({len(validation_errors)} problem(s))",
                errors=validation_errors,
            )
        if self.judge is None and any(case.rubric for case in dataset.cases):
            raise ConfigError(
                "dataset cases have rubric criteria but no judge is configured; "
                "inject a RubricJudge or score deterministic checks only"
            )

        case_results: list[CaseResult] = []
        for case in dataset.cases:
            trials = [self._run_trial(case, trial_index) for trial_index in range(self.repeats)]
            case_results.append(CaseResult(case_id=case.id, trials=trials))
        return EvalRun(
            dataset_version=dataset.version,
            model=self.model,
            repeats=self.repeats,
            case_results=case_results,
        )

    # -- one trial ---------------------------------------------------------

    def _run_trial(self, case: EvalCase, trial_index: int) -> CaseTrial:
        sink = MemorySink()
        tracer = Tracer(sinks=[sink])
        started = time.perf_counter()
        try:
            run = self.agent_factory(case, tracer)
        except Exception as exc:  # a broken case must not abort the whole eval
            run = AgentRun(error=f"{type(exc).__name__}: {exc}")
        measured_ms = (time.perf_counter() - started) * 1000.0
        latency_ms = run.latency_ms if run.latency_ms is not None else measured_ms
        cost_usd = estimate_cost(self.model, run.usage, self.prices)

        check_results = tuple(
            self._evaluate_check(check, run=run, cost_usd=cost_usd) for check in case.checks
        )
        deterministic_passed = all(result.passed for result in check_results)
        deterministic_score: float | None = None
        if check_results:
            total_weight = sum(result.weight for result in check_results)
            passed_weight = sum(result.weight for result in check_results if result.passed)
            deterministic_score = passed_weight / total_weight

        failure_kind: str | None = None
        if run.error is not None:
            failure_kind = FAILURE_AGENT_ERROR
        elif not deterministic_passed:
            first_failed = next(result for result in check_results if not result.passed)
            failure_kind = f"deterministic:{first_failed.kind}"

        judge_verdict: JudgeVerdict | None = None
        judge_ok = True
        should_judge = (
            self.judge is not None and bool(case.rubric) and deterministic_passed and run.error is None
        )
        if should_judge:
            assert self.judge is not None
            try:
                judge_verdict = self.judge.judge(case, run.output)
            except SchemaValidationError:
                judge_ok = False
                failure_kind = failure_kind or FAILURE_JUDGE_FORMAT
            else:
                judge_ok = judge_verdict.passed
                if not judge_ok:
                    failure_kind = failure_kind or FAILURE_JUDGE

        passed = run.error is None and deterministic_passed and judge_ok
        tracer.emit(
            "eval_case",
            case.id,
            {"trial": trial_index, "passed": passed, "score": deterministic_score},
        )
        return CaseTrial(
            case_id=case.id,
            trial=trial_index,
            passed=passed,
            output=run.output,
            deterministic_score=deterministic_score,
            check_results=check_results,
            judge_verdict=judge_verdict,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            failure_kind=failure_kind,
            trace=tuple(sink.events),
            usage=run.usage,
        )

    @staticmethod
    def _evaluate_check(check, *, run: AgentRun, cost_usd: float) -> CheckResult:
        params = check.params
        kind = check.kind
        if kind == "contains":
            text = str(params["text"])
            passed = text in run.output
            detail = f"output {'contains' if passed else 'missing'} {text!r}"
        elif kind == "not_contains":
            text = str(params["text"])
            passed = text not in run.output
            detail = f"output {'must not contain' if not passed else 'does not contain'} {text!r}"
        elif kind == "regex":
            pattern = str(params["pattern"])
            matched = re.search(pattern, run.output) is not None
            passed = matched
            detail = f"output {'matches' if matched else 'does not match'} /{pattern}/"
        elif kind == "tool_called":
            name = str(params["name"])
            called = [call.name for call in run.tool_calls]
            passed = name in called
            detail = f"tool {name!r} {'was' if passed else 'was not'} called; saw {called}"
        elif kind == "tool_not_called":
            name = str(params["name"])
            called = [call.name for call in run.tool_calls]
            passed = name not in called
            detail = f"tool {name!r} {'was not' if passed else 'was'} called; saw {called}"
        elif kind == "max_steps":
            limit = int(params["limit"])
            passed = run.steps <= limit
            detail = f"run used {run.steps} steps (limit {limit})"
        elif kind == "max_cost_usd":
            limit = float(params["limit"])
            passed = cost_usd <= limit
            detail = f"run cost ${cost_usd:.6f} (limit ${limit:.6f})"
        else:  # pragma: no cover - datasets are validated before running
            raise DatasetError(f"unknown check kind {kind!r}")
        return CheckResult(kind=kind, passed=passed, detail=detail, weight=check.weight)
