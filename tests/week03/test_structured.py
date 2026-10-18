"""Tests for ``StructuredExtractor``: the schema-gated extraction pipeline.

The contract under test is narrow and absolute: a valid result carries a typed
value, an invalid result carries ``value=None`` plus the raw output and errors,
the repair loop is bounded, and a flaky provider is never mistaken for a schema
failure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from agentlab.errors import ProviderError
from agentlab.providers.base import Provider
from agentlab.schemas.structured import (
    StructuredExtractor,
    extract_json,
    response_format_for,
)
from agentlab.testing import MockProvider, text_turn
from agentlab.testing.cassettes import CassetteProvider
from agentlab.types import Message
from pydantic import BaseModel

pytestmark = pytest.mark.week


class Answer(BaseModel):
    answer: str
    confidence: float = 0.0


def _messages() -> list[Message]:
    return [Message.user("What is the answer?")]


def _valid_json(**overrides: Any) -> str:
    payload: dict[str, Any] = {"answer": "42", "confidence": 0.9}
    payload.update(overrides)
    return json.dumps(payload)


def test_extract_returns_typed_value_on_first_valid_response() -> None:
    provider = MockProvider([text_turn(_valid_json())])
    messages = _messages()

    result = StructuredExtractor(provider).extract(messages, Answer)

    assert result.valid is True
    assert isinstance(result.value, Answer)
    assert result.value.answer == "42"
    assert result.repairs == 0
    assert result.errors == []
    assert result.raw == _valid_json()
    assert len(provider.calls) == 1
    assert len(messages) == 1  # the caller's list is not mutated


def test_extract_request_carries_schema_temperature_and_prompt() -> None:
    provider = MockProvider([text_turn(_valid_json())])
    StructuredExtractor(provider).extract(_messages(), Answer)

    call = provider.calls[0]
    assert call.model == "mock-1"
    assert call.temperature == 0.0
    response_format = call.response_format
    assert response_format is not None
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["name"] == "Answer"
    assert response_format["json_schema"]["strict"] is True
    schema = response_format["json_schema"]["schema"]
    assert schema["properties"]["answer"]["type"] == "string"
    assert schema["additionalProperties"] is False
    assert call.messages[0].role == "system"
    assert "Answer" in (call.messages[0].content or "")
    assert "JSON Schema" in (call.messages[0].content or "")
    assert call.messages[1].content == "What is the answer?"


def test_extract_strips_markdown_fences() -> None:
    provider = MockProvider([text_turn('```json\n{"answer": "42"}\n```')])

    result = StructuredExtractor(provider).extract(_messages(), Answer)

    assert result.valid is True
    assert result.value is not None
    assert result.value.answer == "42"


def test_extract_repairs_invalid_json_once() -> None:
    provider = MockProvider([text_turn("this is not json"), text_turn(_valid_json())])

    result = StructuredExtractor(provider).extract(_messages(), Answer, max_repairs=1)

    assert result.valid is True
    assert result.value is not None
    assert result.repairs == 1
    assert len(provider.calls) == 2
    repair_request = provider.calls[1]
    assert [message.role for message in repair_request.messages] == [
        "system",
        "user",
        "assistant",
        "user",
    ]
    assert repair_request.messages[2].content == "this is not json"
    assert "JSON" in (repair_request.messages[3].content or "")
    assert repair_request.response_format == provider.calls[0].response_format


def test_extract_repairs_schema_violation_with_field_feedback() -> None:
    provider = MockProvider([text_turn(_valid_json(answer=42)), text_turn(_valid_json())])

    result = StructuredExtractor(provider).extract(_messages(), Answer, max_repairs=1)

    assert result.valid is True
    assert result.repairs == 1
    repair_instruction = provider.calls[1].messages[-1].content or ""
    assert "answer" in repair_instruction
    assert "Answer" in repair_instruction


def test_extract_fails_after_bounded_repairs() -> None:
    provider = MockProvider([text_turn("bad one"), text_turn("bad two")])

    result = StructuredExtractor(provider).extract(_messages(), Answer, max_repairs=1)

    assert result.valid is False
    assert result.value is None
    assert result.repairs == 1
    assert result.raw == "bad two"
    assert result.errors
    assert len(provider.calls) == 2


def test_extract_with_max_repairs_zero_makes_one_call() -> None:
    provider = MockProvider([text_turn("not json")])

    result = StructuredExtractor(provider).extract(_messages(), Answer, max_repairs=0)

    assert result.valid is False
    assert result.value is None
    assert result.repairs == 0
    assert len(provider.calls) == 1


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "not json at all",
        '```json\n{"answer": 1}\n```',
        "[]",
        '{"wrong_field": "x"}',
    ],
)
def test_invalid_output_never_surfaces_as_valid(raw: str) -> None:
    provider = MockProvider([text_turn(raw)])

    result = StructuredExtractor(provider).extract(_messages(), Answer, max_repairs=0)

    assert result.valid is False
    assert result.value is None
    assert result.raw == raw
    assert result.errors


def test_provider_error_propagates_instead_of_becoming_a_schema_failure() -> None:
    extractor = StructuredExtractor(MockProvider([]))

    with pytest.raises(ProviderError):
        extractor.extract(_messages(), Answer)


def test_stats_track_clean_repaired_and_failed_extractions() -> None:
    provider = MockProvider([])
    provider.queue(
        text_turn(_valid_json()),
        text_turn("bad"),
        text_turn(_valid_json()),
        text_turn("bad"),
        text_turn("bad"),
    )
    extractor = StructuredExtractor(provider)

    extractor.extract(_messages(), Answer)
    extractor.extract(_messages(), Answer)
    extractor.extract(_messages(), Answer, max_repairs=1)

    stats = extractor.stats
    assert (stats.total, stats.clean, stats.repaired, stats.failed) == (3, 1, 1, 1)
    assert stats.failure_rate == pytest.approx(1 / 3)
    assert stats.repair_rate == pytest.approx(1 / 3)


def test_extract_json_decodes_plain_and_fenced_json() -> None:
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_rejects_empty_and_invalid_output() -> None:
    with pytest.raises(ValueError, match="empty"):
        extract_json("   ")

    with pytest.raises(ValueError, match="not valid JSON"):
        extract_json("nope")


def test_response_format_for_builds_strict_json_schema_object() -> None:
    response_format = response_format_for(Answer)

    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["name"] == "Answer"
    assert response_format["json_schema"]["strict"] is True
    schema = response_format["json_schema"]["schema"]
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"answer", "confidence"}
    assert response_format_for(Answer, name="Custom", strict=False)["json_schema"]["name"] == "Custom"


class _ReplayProvider:
    """Give a replaying cassette the model name the recording was made with."""

    def __init__(self, inner: CassetteProvider, *, model: str = "mock-1") -> None:
        self.inner = inner
        self.name = "cassette"
        self.model = model

    def complete(self, request: Any) -> Any:
        return self.inner.complete(request)

    def stream(self, request: Any) -> Any:
        return self.inner.stream(request)


def test_cassette_replay_feeds_the_extractor_offline(tmp_path: Path) -> None:
    path = tmp_path / "cassette.json"
    recorder = CassetteProvider(MockProvider([text_turn(_valid_json())]), path, mode="record")
    recorded = StructuredExtractor(recorder).extract(_messages(), Answer)
    recorder.close()

    replay = CassetteProvider(None, path, mode="replay")
    replayed = StructuredExtractor(_ReplayProvider(replay)).extract(_messages(), Answer)

    assert recorded.valid is True
    assert replayed.valid is True
    assert replayed.raw == recorded.raw
    assert replayed.value is not None
    assert replayed.value.answer == "42"


def test_extractor_accepts_a_provider_protocol_implementation() -> None:
    provider: Provider = MockProvider([text_turn(_valid_json())])

    result = StructuredExtractor(provider).extract(_messages(), Answer)

    assert result.valid is True
