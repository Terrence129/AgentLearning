"""Dataset tests: versioned JSONL, validation, digests."""

from __future__ import annotations

import json

import pytest
from agentlab.evals.dataset import (
    FORMAT,
    DatasetError,
    DeterministicCheck,
    EvalCase,
    EvalDataset,
    RubricCriterion,
    dataset_from_records,
    dataset_to_records,
    load_dataset,
    save_dataset,
)

pytestmark = pytest.mark.week


def _dataset() -> EvalDataset:
    return EvalDataset(
        version="2026-10-18",
        cases=[
            EvalCase(
                id="refund-001",
                input="Refund order 42",
                checks=[DeterministicCheck(kind="contains", params={"text": "REFUND-42"})],
                rubric=[RubricCriterion(id="correct", description="States the refund decision")],
                tags=["smoke"],
            ),
            EvalCase(
                id="policy-002",
                input="Is a refund allowed after 40 days?",
                checks=[
                    DeterministicCheck(kind="tool_called", params={"name": "policy_lookup"}),
                    DeterministicCheck(kind="max_steps", params={"limit": 5}, weight=0.5),
                ],
                pass_threshold=0.9,
                metadata={"source": "incident-17"},
            ),
        ],
        metadata={"owner": "curriculum"},
    )


def test_round_trip_preserves_cases(tmp_path):
    original = _dataset()
    path = save_dataset(original, tmp_path / "dataset.jsonl")
    loaded = load_dataset(path)

    assert loaded.version == "2026-10-18"
    assert [case.id for case in loaded.cases] == ["refund-001", "policy-002"]
    assert loaded.cases[0].checks[0].kind == "contains"
    assert loaded.cases[0].checks[0].params == {"text": "REFUND-42"}
    assert loaded.cases[0].tags == ["smoke"]
    assert loaded.cases[1].pass_threshold == pytest.approx(0.9)
    assert loaded.cases[1].metadata == {"source": "incident-17"}
    assert loaded.metadata == {"owner": "curriculum"}
    assert loaded.content_digest() == original.content_digest()


def test_saved_file_is_jsonl_with_header_first(tmp_path):
    path = save_dataset(_dataset(), tmp_path / "dataset.jsonl")
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    assert lines[0]["kind"] == "header"
    assert lines[0]["format"] == FORMAT
    assert lines[0]["version"] == "2026-10-18"
    assert [record["kind"] for record in lines[1:]] == ["case", "case"]
    assert lines[1]["id"] == "refund-001"


def test_load_rejects_dataset_without_header(tmp_path):
    path = tmp_path / "no-header.jsonl"
    record = {
        "kind": "case",
        "id": "c1",
        "input": "hi",
        "checks": [{"kind": "contains", "params": {"text": "hi"}}],
    }
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(DatasetError, match="header"):
        load_dataset(path)


def test_load_reports_malformed_json_line(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text(
        '{"kind": "header", "format": "agentlab.evals/v1", "version": "v1"}\nnot json\n',
        encoding="utf-8",
    )

    with pytest.raises(DatasetError, match="line 2"):
        load_dataset(path)


def test_validate_reports_duplicate_case_ids():
    case = EvalCase(
        id="dup",
        input="a",
        checks=[DeterministicCheck(kind="contains", params={"text": "a"})],
    )
    errors = EvalDataset(version="v1", cases=[case, case]).validate()

    assert any("duplicate case id" in error for error in errors)


def test_validate_reports_unknown_check_kind():
    case = EvalCase(
        id="c1",
        input="i",
        checks=[DeterministicCheck(kind="vibes", params={})],
    )
    errors = EvalDataset(version="v1", cases=[case]).validate()

    assert any("unknown check kind" in error for error in errors)


def test_validate_reports_missing_check_parameters():
    case = EvalCase(
        id="c1",
        input="i",
        checks=[DeterministicCheck(kind="contains", params={})],
    )
    errors = EvalDataset(version="v1", cases=[case]).validate()

    assert any("missing required params" in error and "text" in error for error in errors)


def test_validate_accepts_well_formed_dataset():
    assert _dataset().validate() == []


def test_case_without_checks_or_rubric_is_invalid():
    errors = EvalDataset(version="v1", cases=[EvalCase(id="empty", input="i")]).validate()

    assert any("at least one deterministic check or rubric criterion" in error for error in errors)


def test_content_digest_is_stable_and_content_sensitive():
    first = _dataset()
    same = _dataset()
    changed = _dataset()
    changed.cases[0] = EvalCase(
        id="refund-001",
        input="Refund order 42",
        checks=[DeterministicCheck(kind="contains", params={"text": "APPROVED"})],
        rubric=first.cases[0].rubric,
        tags=["smoke"],
    )
    digest = first.content_digest()

    assert len(digest) == 64
    assert all(char in "0123456789abcdef" for char in digest)
    assert same.content_digest() == digest
    assert changed.content_digest() != digest


def test_save_rejects_invalid_dataset(tmp_path):
    invalid = EvalDataset(version="v1", cases=[EvalCase(id="empty", input="i")])
    path = tmp_path / "invalid.jsonl"

    with pytest.raises(DatasetError) as excinfo:
        save_dataset(invalid, path)

    assert not path.exists()
    assert excinfo.value.errors


def test_records_round_trip():
    records = dataset_to_records(_dataset())
    rebuilt = dataset_from_records(records)

    assert rebuilt.content_digest() == _dataset().content_digest()
    assert rebuilt.validate() == []
