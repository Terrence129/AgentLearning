"""Response-parsing tests: JSON body -> ``CompletionResponse``.

Parsing is where a provider adapter either preserves information (usage, raw
payload, finish reason, tool calls) or silently loses it. Each test pins one
mapping so a late-night refactor cannot quietly change the shape the whole
course depends on.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from agentlab.errors import ProviderError
from agentlab.providers.openai_compat import OpenAICompatibleProvider
from agentlab.types import CompletionRequest, Message

pytestmark = pytest.mark.week


def _payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": "chatcmpl-1",
        "model": "wire-model",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "hello"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 12, "completion_tokens": 4},
    }
    payload.update(overrides)
    return payload


def _ok_body() -> dict[str, Any]:
    return _payload()


def test_parse_response_maps_text_role_and_finish_reason() -> None:
    response = OpenAICompatibleProvider._parse_response(_payload())

    assert response.message.role == "assistant"
    assert response.text == "hello"
    assert response.finish_reason == "stop"
    assert response.message.tool_calls == []


def test_parse_response_maps_usage_and_cached_tokens() -> None:
    payload = _payload(
        usage={
            "prompt_tokens": 120,
            "completion_tokens": 30,
            "prompt_tokens_details": {"cached_tokens": 100},
        }
    )

    response = OpenAICompatibleProvider._parse_response(payload)

    assert response.usage.input_tokens == 120
    assert response.usage.output_tokens == 30
    assert response.usage.cached_input_tokens == 100
    assert response.usage.total_tokens == 150


def test_parse_response_retains_raw_payload() -> None:
    payload = _payload()

    response = OpenAICompatibleProvider._parse_response(payload)

    assert response.raw == payload
    assert response.raw["id"] == "chatcmpl-1"


def test_parse_response_parses_tool_call_arguments() -> None:
    payload = _payload()
    payload["choices"][0]["message"] = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_9",
                "type": "function",
                "function": {"name": "add", "arguments": '{"a": 2, "b": 3}'},
            }
        ],
    }
    payload["choices"][0]["finish_reason"] = "tool_calls"

    response = OpenAICompatibleProvider._parse_response(payload)

    assert response.wants_tools
    assert response.text == ""
    assert response.finish_reason == "tool_calls"
    assert response.tool_calls[0].id == "call_9"
    assert response.tool_calls[0].name == "add"
    assert response.tool_calls[0].arguments == {"a": 2, "b": 3}


def test_parse_response_normalises_missing_tool_call_id() -> None:
    payload = _payload()
    payload["choices"][0]["message"] = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"type": "function", "function": {"name": "ping", "arguments": "{}"}}],
    }

    response = OpenAICompatibleProvider._parse_response(payload)

    assert response.tool_calls[0].id == "call_0"


def test_parse_response_keeps_null_content_when_only_tools() -> None:
    payload = _payload()
    payload["choices"][0]["message"] = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_1", "function": {"name": "ping", "arguments": ""}}],
    }

    response = OpenAICompatibleProvider._parse_response(payload)

    assert response.message.content is None
    assert response.tool_calls[0].arguments == {}


def test_parse_response_defaults_missing_usage_and_finish_reason() -> None:
    payload = _payload()
    del payload["usage"]
    payload["choices"][0].pop("finish_reason")

    response = OpenAICompatibleProvider._parse_response(payload)

    assert response.usage.input_tokens == 0
    assert response.usage.output_tokens == 0
    assert response.usage.cached_input_tokens == 0
    assert response.finish_reason == "stop"


def test_parse_response_uses_payload_model() -> None:
    response = OpenAICompatibleProvider._parse_response(_payload(), fallback_model="fallback")

    assert response.model == "wire-model"


def test_parse_response_falls_back_to_requested_model() -> None:
    payload = _payload()
    del payload["model"]

    response = OpenAICompatibleProvider._parse_response(payload, fallback_model="fallback")

    assert response.model == "fallback"


def test_parse_response_rejects_malformed_tool_arguments() -> None:
    payload = _payload()
    payload["choices"][0]["message"] = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_1", "function": {"name": "add", "arguments": "{not json"}}],
    }

    with pytest.raises(ProviderError, match="not valid JSON"):
        OpenAICompatibleProvider._parse_response(payload)


def test_parse_response_rejects_payload_without_choices() -> None:
    with pytest.raises(ProviderError) as info:
        OpenAICompatibleProvider._parse_response({"choices": [], "model": "m"})

    assert info.value.retryable is False


def test_complete_returns_a_parsed_response(make_provider) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler)
    response = provider.complete(CompletionRequest(messages=[Message.user("hi")], model="test-model"))

    assert response.text == "hello"
    assert response.model == "wire-model"
    assert response.usage.input_tokens == 12
