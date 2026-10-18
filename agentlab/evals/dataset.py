"""Eval cases as versioned data.

An eval is a dataset, not a script. The moment cases live in a Python literal or
a notebook cell, three things break: a change to an expectation cannot be
reviewed in a diff, a release cannot be pinned to the exact set it was measured
against, and two runs are only comparable when both were scored by the same,
unchanged cases.

This module defines a deliberately boring on-disk format (JSONL) and its
validation rules:

- line 1 is a ``header`` record carrying ``format`` and ``version``;
- every following line is exactly one ``case`` record;
- every case must declare at least one deterministic check or rubric criterion;
- check kinds and their parameters are closed: an unknown kind is a validation
  error, never a silently ignored check.

Read first: ``docs/research/03-production-evals-ops.md`` §1.1–1.3 (the eval
decision tree and deterministic-first scoring). The theme: expectations are
data, so they can be reviewed, versioned and compared.

Validation is *collected*, not fail-fast: ``EvalDataset.validate`` returns every
problem found so a reviewer sees all of them at once, and ``load_dataset``
raises one ``DatasetError`` carrying that list.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: On-disk format marker written in the header record.
FORMAT = "agentlab.evals/v1"

#: The closed set of deterministic check kinds. See ``DeterministicCheck`` for
#: the parameters each kind requires.
CHECK_KINDS: tuple[str, ...] = (
    "contains",
    "not_contains",
    "regex",
    "tool_called",
    "tool_not_called",
    "max_steps",
    "max_cost_usd",
)

_REQUIRED_PARAMS: dict[str, tuple[str, ...]] = {
    "contains": ("text",),
    "not_contains": ("text",),
    "regex": ("pattern",),
    "tool_called": ("name",),
    "tool_not_called": ("name",),
    "max_steps": ("limit",),
    "max_cost_usd": ("limit",),
}


class DatasetError(ValueError):
    """An eval dataset is structurally invalid.

    Attributes:
        errors: every validation problem found, as human-readable strings.
    """

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors: list[str] = list(errors or [])


@dataclass(frozen=True, slots=True)
class RubricCriterion:
    """One atomic rubric criterion scored by an LLM judge.

    Atomic means it can be answered independently (typically 0–2): "the answer
    cites the invoice id" is atomic; "the answer is good" is not. A holistic
    1–10 score hides which part failed, which is exactly what a regression gate
    needs to know.
    """

    id: str
    description: str
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class DeterministicCheck:
    """One machine-checkable expectation about an agent run.

    ``kind`` determines the parameters that must be present (validated by the
    dataset, not by the check itself):

    - ``contains`` / ``not_contains``: ``{"text": str}`` -- output containment.
    - ``regex``: ``{"pattern": str}`` -- ``re.search`` on the output.
    - ``tool_called`` / ``tool_not_called``: ``{"name": str}`` -- tool usage.
    - ``max_steps``: ``{"limit": int}`` -- efficiency ceiling.
    - ``max_cost_usd``: ``{"limit": float}`` -- spend ceiling.

    Deterministic checks run first and are always required to pass; a failing
    check means the judge is never asked (do not pay a model to judge garbage).
    """

    kind: str
    params: Mapping[str, Any] = field(default_factory=dict)
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class EvalCase:
    """One input + its acceptance evidence.

    Attributes:
        id: stable, unique identifier; used in reports and as a map key. Never
            renumber ids: ids are how two runs are compared.
        input: the user/agent input for the case.
        checks: deterministic expectations, evaluated in declaration order.
        rubric: criteria for the LLM judge; requires a judge at run time.
        tags: free-form grouping labels (``smoke``, ``refund``, ...).
        pass_threshold: minimum weighted rubric score in ``(0, 1]`` for the
            judge to consider the case passed.
        metadata: anything else worth diffing (owner, source incident, ...).
    """

    id: str
    input: str
    checks: list[DeterministicCheck] = field(default_factory=list)
    rubric: list[RubricCriterion] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    pass_threshold: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvalDataset:
    """A versioned, ordered collection of eval cases.

    Attributes:
        version: opaque version string chosen by the owner (a date like
            ``"2026-10-18"``, a semver, or a git-ish tag). Bump it whenever an
            expectation changes so reports are comparable.
        cases: the cases, in report order.
        metadata: dataset-level notes (owner, source, coverage).
    """

    version: str
    cases: list[EvalCase]
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        """Return every structural problem, or ``[]`` when the dataset is valid.

        Never raises: collection lets a reviewer fix everything in one pass.
        Rules: non-empty version; at least one case; unique ids; every case has
        at least one check or rubric criterion; check kinds are known and carry
        their required parameters; weights are positive; rubric ids are unique
        per case; ``pass_threshold`` is in ``(0, 1]``.
        """
        raise NotImplementedError("Week 7 lab: implement EvalDataset.validate")

    def content_digest(self) -> str:
        """SHA-256 hex digest of the canonical case records.

        Excludes the header version/metadata on purpose: the digest fingerprints
        *what is being measured*, not the label attached to it. Two runs quoting
        the same digest were scored against identical expectations.
        """
        raise NotImplementedError("Week 7 lab: implement EvalDataset.content_digest")


def dataset_to_records(dataset: EvalDataset) -> list[dict[str, Any]]:
    """Convert a dataset to JSONL-ready records (header first, then cases).

    Default-valued fields are omitted to keep diffs small: absent ``checks`` or
    ``rubric`` means empty, absent ``pass_threshold`` means the default.
    """
    raise NotImplementedError("Week 7 lab: implement dataset_to_records")


def dataset_from_records(records: Sequence[Mapping[str, Any]]) -> EvalDataset:
    """Build and validate a dataset from decoded JSONL records.

    Raises:
        DatasetError: missing/invalid header, or any validation problem. The
            exception's ``errors`` lists all problems found.
    """
    raise NotImplementedError("Week 7 lab: implement dataset_from_records")


def load_dataset(path: str | Path) -> EvalDataset:
    """Read a JSONL dataset from ``path`` and validate it.

    A missing file raises ``FileNotFoundError`` (that is a caller bug, not bad
    data); malformed JSON or invalid content raises ``DatasetError``.
    """
    raise NotImplementedError("Week 7 lab: implement load_dataset")


def save_dataset(dataset: EvalDataset, path: str | Path) -> Path:
    """Validate, then write the dataset as UTF-8 JSONL (creating parents).

    Invalid datasets are never written: fail closed, so a broken expectation can
    never silently become the baseline. Returns the written path.
    """
    raise NotImplementedError("Week 7 lab: implement save_dataset")
