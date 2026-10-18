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

import hashlib
import json
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
        errors: list[str] = []
        if not isinstance(self.version, str) or not self.version.strip():
            errors.append("dataset version must be a non-empty string")
        if not self.cases:
            errors.append("dataset must contain at least one case")

        seen_ids: set[str] = set()
        for case in self.cases:
            if not isinstance(case.id, str) or not case.id.strip():
                errors.append("every case needs a non-empty string id")
                continue
            if case.id in seen_ids:
                errors.append(f"duplicate case id {case.id!r}")
            seen_ids.add(case.id)
            if not case.checks and not case.rubric:
                errors.append(
                    f"case {case.id!r}: must define at least one deterministic check or rubric criterion"
                )
            if not (0 < case.pass_threshold <= 1):
                errors.append(
                    f"case {case.id!r}: pass_threshold must be in (0, 1], got {case.pass_threshold!r}"
                )

            criterion_ids: set[str] = set()
            for criterion in case.rubric:
                if not isinstance(criterion.id, str) or not criterion.id.strip():
                    errors.append(f"case {case.id!r}: rubric criterion needs a non-empty id")
                    continue
                if criterion.id in criterion_ids:
                    errors.append(f"case {case.id!r}: duplicate rubric criterion id {criterion.id!r}")
                criterion_ids.add(criterion.id)
                if criterion.weight <= 0:
                    errors.append(f"case {case.id!r}: rubric criterion {criterion.id!r} weight must be > 0")

            for check in case.checks:
                if check.kind not in CHECK_KINDS:
                    errors.append(
                        f"case {case.id!r}: unknown check kind {check.kind!r}; "
                        f"known kinds: {', '.join(CHECK_KINDS)}"
                    )
                else:
                    required = _REQUIRED_PARAMS[check.kind]
                    missing = [name for name in required if name not in check.params]
                    if missing:
                        errors.append(
                            f"case {case.id!r}: check kind {check.kind!r} missing required params {missing}"
                        )
                if check.weight <= 0:
                    errors.append(f"case {case.id!r}: weight must be > 0 for check {check.kind!r}")
        return errors

    def content_digest(self) -> str:
        """SHA-256 hex digest of the canonical case records.

        Excludes the header version/metadata on purpose: the digest fingerprints
        *what is being measured*, not the label attached to it. Two runs quoting
        the same digest were scored against identical expectations.
        """
        case_records = dataset_to_records(self)[1:]
        blob = json.dumps(case_records, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _check_to_record(check: DeterministicCheck) -> dict[str, Any]:
    record: dict[str, Any] = {"kind": check.kind, "params": dict(check.params)}
    if check.weight != 1.0:
        record["weight"] = check.weight
    return record


def _criterion_to_record(criterion: RubricCriterion) -> dict[str, Any]:
    record: dict[str, Any] = {"id": criterion.id, "description": criterion.description}
    if criterion.weight != 1.0:
        record["weight"] = criterion.weight
    return record


def _case_to_record(case: EvalCase) -> dict[str, Any]:
    record: dict[str, Any] = {"kind": "case", "id": case.id, "input": case.input}
    if case.checks:
        record["checks"] = [_check_to_record(check) for check in case.checks]
    if case.rubric:
        record["rubric"] = [_criterion_to_record(criterion) for criterion in case.rubric]
    if case.tags:
        record["tags"] = list(case.tags)
    if case.pass_threshold != 0.8:
        record["pass_threshold"] = case.pass_threshold
    if case.metadata:
        record["metadata"] = dict(case.metadata)
    return record


def dataset_to_records(dataset: EvalDataset) -> list[dict[str, Any]]:
    """Convert a dataset to JSONL-ready records (header first, then cases).

    Default-valued fields are omitted to keep diffs small: absent ``checks`` or
    ``rubric`` means empty, absent ``pass_threshold`` means the default.
    """
    header: dict[str, Any] = {"kind": "header", "format": FORMAT, "version": dataset.version}
    if dataset.metadata:
        header["metadata"] = dict(dataset.metadata)
    return [header, *(_case_to_record(case) for case in dataset.cases)]


def _require_mapping(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DatasetError(f"{where} must be a JSON object, got {type(value).__name__}")
    return value


def _parse_number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DatasetError(f"{where} must be a number, got {value!r}")
    return float(value)


def _parse_check(raw: Any, where: str) -> DeterministicCheck:
    record = _require_mapping(raw, where)
    kind = record.get("kind")
    if not isinstance(kind, str) or not kind:
        raise DatasetError(f"{where}: check record needs a non-empty 'kind'")
    params = _require_mapping(record.get("params", {}), f"{where}: 'params'")
    weight = _parse_number(record.get("weight", 1.0), f"{where}: check weight")
    return DeterministicCheck(kind=kind, params=dict(params), weight=weight)


def _parse_criterion(raw: Any, where: str) -> RubricCriterion:
    record = _require_mapping(raw, where)
    criterion_id = record.get("id")
    description = record.get("description")
    if not isinstance(criterion_id, str) or not criterion_id:
        raise DatasetError(f"{where}: rubric criterion needs a non-empty 'id'")
    if not isinstance(description, str):
        raise DatasetError(f"{where}: rubric criterion {criterion_id!r} needs a 'description'")
    weight = _parse_number(record.get("weight", 1.0), f"{where}: rubric weight")
    return RubricCriterion(id=criterion_id, description=description, weight=weight)


def _parse_case(raw: Any, where: str) -> EvalCase:
    record = _require_mapping(raw, where)
    case_id = record.get("id")
    case_input = record.get("input")
    if not isinstance(case_id, str) or not case_id:
        raise DatasetError(f"{where}: case record needs a non-empty 'id'")
    if not isinstance(case_input, str):
        raise DatasetError(f"{where}: case {case_id!r} needs a string 'input'")
    checks_raw = record.get("checks", [])
    rubric_raw = record.get("rubric", [])
    tags_raw = record.get("tags", [])
    if not isinstance(checks_raw, list):
        raise DatasetError(f"{where}: case {case_id!r} 'checks' must be a list")
    if not isinstance(rubric_raw, list):
        raise DatasetError(f"{where}: case {case_id!r} 'rubric' must be a list")
    if not isinstance(tags_raw, list):
        raise DatasetError(f"{where}: case {case_id!r} 'tags' must be a list")
    pass_threshold = _parse_number(
        record.get("pass_threshold", 0.8), f"{where}: case {case_id!r} pass_threshold"
    )
    metadata = _require_mapping(record.get("metadata", {}), f"{where}: case {case_id!r} metadata")
    case_where = f"{where}: case {case_id!r}"
    return EvalCase(
        id=case_id,
        input=case_input,
        checks=[_parse_check(item, case_where) for item in checks_raw],
        rubric=[_parse_criterion(item, case_where) for item in rubric_raw],
        tags=[str(tag) for tag in tags_raw],
        pass_threshold=pass_threshold,
        metadata=dict(metadata),
    )


def dataset_from_records(records: Sequence[Mapping[str, Any]]) -> EvalDataset:
    """Build and validate a dataset from decoded JSONL records.

    Raises:
        DatasetError: missing/invalid header, or any validation problem. The
            exception's ``errors`` lists all problems found.
    """
    if not records:
        raise DatasetError("dataset is empty: expected a header record", errors=["dataset is empty"])
    header = _require_mapping(records[0], "line 1")
    if header.get("kind") != "header":
        raise DatasetError(
            "first record must be a header record",
            errors=["first record must have kind='header'"],
        )
    if header.get("format") != FORMAT:
        raise DatasetError(
            f"unsupported dataset format {header.get('format')!r}; expected {FORMAT!r}",
            errors=[f"unsupported format {header.get('format')!r}"],
        )
    version = header.get("version")
    if not isinstance(version, str) or not version.strip():
        raise DatasetError("header record must carry a non-empty version")
    metadata = _require_mapping(header.get("metadata", {}), "header metadata")
    cases = [
        _parse_case(record, f"line {line_number}") for line_number, record in enumerate(records[1:], start=2)
    ]
    dataset = EvalDataset(version=version, cases=cases, metadata=dict(metadata))
    errors = dataset.validate()
    if errors:
        raise DatasetError(f"dataset failed validation with {len(errors)} problem(s)", errors=errors)
    return dataset


def load_dataset(path: str | Path) -> EvalDataset:
    """Read a JSONL dataset from ``path`` and validate it.

    A missing file raises ``FileNotFoundError`` (that is a caller bug, not bad
    data); malformed JSON or invalid content raises ``DatasetError``.
    """
    source = Path(path)
    records: list[Mapping[str, Any]] = []
    with source.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise DatasetError(
                    f"{source}: invalid JSON on line {line_number}: {exc.msg}",
                    errors=[f"line {line_number}: {exc.msg}"],
                ) from exc
            records.append(_require_mapping(record, f"{source}: line {line_number}"))
    return dataset_from_records(records)


def save_dataset(dataset: EvalDataset, path: str | Path) -> Path:
    """Validate, then write the dataset as UTF-8 JSONL (creating parents).

    Invalid datasets are never written: fail closed, so a broken expectation can
    never silently become the baseline. Returns the written path.
    """
    errors = dataset.validate()
    if errors:
        raise DatasetError(f"refusing to save an invalid dataset ({len(errors)} problem(s))", errors=errors)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(record, ensure_ascii=False, sort_keys=False) for record in dataset_to_records(dataset)
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
