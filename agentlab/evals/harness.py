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

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from agentlab.evals.dataset import EvalCase, EvalDataset
from agentlab.evals.judges import Judge, JudgeVerdict
from agentlab.pricing import ModelPrice
from agentlab.trace import TraceEvent, Tracer
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
        raise NotImplementedError("Week 7 lab: implement CaseResult.pass_at_1")

    @property
    def pass_all(self) -> bool:
        """Whether every recorded trial passed (the reliability view)."""
        raise NotImplementedError("Week 7 lab: implement CaseResult.pass_all")


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
        raise NotImplementedError("Week 7 lab: implement EvalRun.pass_at_1")

    def pass_hat_k(self, k: int | None = None) -> float:
        """Fraction of cases where *all* of the first ``k`` trials passed.

        Fraction of cases where all *k* trials passed, i.e. reliability. Defaults
        to ``k=self.repeats``. Raises ``ValueError`` for ``k`` outside
        ``[1, repeats]``.
        """
        raise NotImplementedError("Week 7 lab: implement EvalRun.pass_hat_k")

    def total_cost_usd(self) -> float:
        """Sum of estimated cost over every trial."""
        raise NotImplementedError("Week 7 lab: implement EvalRun.total_cost_usd")

    def latency_percentile(self, percentile: float) -> float:
        """Nearest-rank percentile of trial latencies, in milliseconds.

        ``percentile`` is in ``(0, 100]``; raises ``ValueError`` otherwise.
        """
        raise NotImplementedError("Week 7 lab: implement EvalRun.latency_percentile")

    def metrics(self) -> dict[str, float]:
        """Flat metric dict, the contract used by report gates and baselines.

        Keys (all floats): ``cases``, ``trials``, ``pass_at_1``, ``pass_hat_k``,
        ``total_cost_usd``, ``avg_cost_usd`` (per case), ``avg_latency_ms``,
        ``p95_latency_ms``.
        """
        raise NotImplementedError("Week 7 lab: implement EvalRun.metrics")

    def failure_taxonomy(self) -> dict[str, int]:
        """Count of failed trials per ``failure_kind``, sorted by label."""
        raise NotImplementedError("Week 7 lab: implement EvalRun.failure_taxonomy")


def pass_at_1(case_results: Sequence[CaseResult]) -> float:
    """Capability metric: fraction of cases passing on the first attempt."""
    raise NotImplementedError("Week 7 lab: implement pass_at_1")


def pass_hat_k(case_results: Sequence[CaseResult], k: int) -> float:
    """Reliability metric: fraction of cases where all first ``k`` trials passed."""
    raise NotImplementedError("Week 7 lab: implement pass_hat_k")


def failure_taxonomy(case_results: Sequence[CaseResult]) -> dict[str, int]:
    """Group failed trials by ``failure_kind`` so a report can rank root causes."""
    raise NotImplementedError("Week 7 lab: implement failure_taxonomy")


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
        raise NotImplementedError("Week 7 lab: implement EvalHarness.run")
