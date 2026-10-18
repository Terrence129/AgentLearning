"""Wire-shape tests: ``CompletionRequest`` -> JSON body -> HTTP request.

The payload is the provider seam's public contract. If a field is mapped wrong
here, every later week inherits the bug, so these tests read like a diff of the
request the model would actually receive.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
from agentlab.types import CompletionRequest, Message, ToolCall, ToolSpec

pytestmark = pytest.mark.week

CHAT_URL = "https://api.example.test/v1/chat/completions"


def _ok_body() -> dict[str, Any]:
    return {
        "model": "test-model",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }


def _request(**kwargs: Any) -> CompletionRequest:
    return CompletionRequest(messages=[Message.user("hi")], model="test-model", **kwargs)


def test_build_payload_maps_model_messages_and_stream(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))
    request = CompletionRequest(
        messages=[Message.system("be brief"), Message.user("hi")],
        model="",
    )

    payload = provider._build_payload(request, stream=False)

    assert payload["model"] == "test-model"
    assert payload["messages"] == [
        {"role": "system", "content": "be brief"},
        {"role": "user", "content": "hi"},
    ]
    assert payload["stream"] is False


def test_build_payload_omits_unset_optional_fields(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))

    payload = provider._build_payload(_request(), stream=False)

    for absent in ("tools", "temperature", "max_tokens", "response_format", "stop", "stream_options"):
        assert absent not in payload


def test_build_payload_includes_optional_fields_when_set(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))
    request = _request(
        temperature=0.2,
        max_tokens=64,
        response_format={"type": "json_object"},
        stop=["\n"],
    )

    payload = provider._build_payload(request, stream=False)

    assert payload["temperature"] == 0.2
    assert payload["max_tokens"] == 64
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["stop"] == ["\n"]


def test_build_payload_maps_tool_specs(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))
    spec = ToolSpec(
        name="add",
        description="Add two integers",
        parameters={"type": "object", "properties": {"a": {"type": "integer"}}},
        strict=True,
    )

    payload = provider._build_payload(_request(tools=[spec]), stream=False)

    assert payload["tools"] == [spec.as_openai_tool()]


def test_build_payload_omits_empty_tool_list(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))

    payload = provider._build_payload(_request(), stream=False)

    assert "tools" not in payload


def test_build_payload_extra_is_merged_last(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))
    request = _request(temperature=0.1, extra={"temperature": 0.9, "reasoning_effort": "low"})

    payload = provider._build_payload(request, stream=False)

    assert payload["temperature"] == 0.9
    assert payload["reasoning_effort"] == "low"


def test_build_payload_maps_assistant_tool_calls_and_tool_message(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))
    messages = [
        Message.assistant(None, [ToolCall(id="call_1", name="add", arguments={"a": 1, "b": 2})]),
        Message.tool_result("call_1", "3", name="add"),
    ]

    payload = provider._build_payload(CompletionRequest(messages=messages, model="m"), stream=False)

    assistant = payload["messages"][0]
    assert assistant["role"] == "assistant"
    assert assistant["content"] is None
    assert assistant["tool_calls"] == [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": "add", "arguments": json.dumps({"a": 1, "b": 2})},
        }
    ]
    tool_message = payload["messages"][1]
    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call_1"
    assert tool_message["name"] == "add"


def test_complete_posts_json_to_chat_completions_with_auth(make_provider) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler)
    response = provider.complete(_request())

    assert response.text == "ok"
    assert len(seen) == 1
    sent = seen[0]
    assert sent.method == "POST"
    assert str(sent.url) == CHAT_URL
    assert sent.headers["authorization"] == "Bearer sk-test-0123456789abcdef"
    assert sent.headers["content-type"] == "application/json"
    body = json.loads(sent.content)
    assert body["model"] == "test-model"
    assert body["stream"] is False


def test_request_model_overrides_provider_model(make_provider) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler)
    provider.complete(CompletionRequest(messages=[Message.user("hi")], model="other-model"))

    assert json.loads(seen[0].content)["model"] == "other-model"


def test_build_payload_does_not_mutate_request(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(200, json=_ok_body()))
    request = _request(temperature=0.1, extra={"top_p": 0.5})
    before = (request.model, dict(request.extra), request.temperature)

    payload = provider._build_payload(request, stream=False)
    payload["model"] = "mutated"

    assert (request.model, dict(request.extra), request.temperature) == before
