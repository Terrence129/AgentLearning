"""Streaming tests: SSE frames -> ``StreamEvent`` -> assembled response.

Streaming is a protocol, not a feature flag. The tests pin the parts that break
in hand-written adapters: frames split across network chunks, tool-call JSON
arriving in fragments, usage that only appears at the end, and the ``[DONE]``
sentinel. The last test is the contract that matters most: assembling a stream
must produce the same response a non-streaming call would have returned.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from typing import Any

import httpx
import pytest
from agentlab.errors import ProviderError
from agentlab.providers.base import assemble_stream
from agentlab.types import CompletionRequest, Message

pytestmark = pytest.mark.week


class _ChunkedStream(httpx.SyncByteStream):
    """Deliver the body as exactly these chunks (no coalescing by the client)."""

    def __init__(self, chunks: Sequence[bytes]) -> None:
        self._chunks = list(chunks)

    def __iter__(self) -> Iterator[bytes]:
        yield from self._chunks


def _sse(chunks: Sequence[bytes], *, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code,
        headers={"content-type": "text/event-stream"},
        stream=_ChunkedStream(chunks),
    )


def _frame(payload: dict[str, Any]) -> bytes:
    return b"data: " + json.dumps(payload).encode() + b"\n\n"


def _done() -> bytes:
    return b"data: [DONE]\n\n"


def _request() -> CompletionRequest:
    return CompletionRequest(messages=[Message.user("hi")], model="test-model")


def _text_chunks() -> list[bytes]:
    return [
        _frame({"choices": [{"index": 0, "delta": {"role": "assistant", "content": "Hel"}}]}),
        _frame({"choices": [{"index": 0, "delta": {"content": "lo"}}]}),
        _frame({"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}),
        _done(),
    ]


def _tool_chunks() -> list[bytes]:
    return [
        _frame(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {"name": "add", "arguments": ""},
                                }
                            ]
                        },
                    }
                ]
            }
        ),
        _frame(
            {
                "choices": [
                    {"index": 0, "delta": {"tool_calls": [{"index": 0, "function": {"arguments": '{"a": '}}]}}
                ]
            }
        ),
        _frame(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {"tool_calls": [{"index": 0, "function": {"arguments": '2, "b": 3}'}}]},
                    }
                ]
            }
        ),
        _frame({"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]}),
        _done(),
    ]


def test_stream_requests_stream_mode_with_usage_option(make_provider) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _sse(_text_chunks())

    provider = make_provider(handler)
    list(provider.stream(_request()))

    body = json.loads(seen[0].content)
    assert body["stream"] is True
    assert body["stream_options"] == {"include_usage": True}


def test_stream_yields_text_deltas_and_done(make_provider) -> None:
    provider = make_provider(lambda request: _sse(_text_chunks()))

    events = list(provider.stream(_request()))

    assert [event.type for event in events] == ["text", "text", "done"]
    assert "".join(event.text or "" for event in events) == "Hello"
    assert events[-1].finish_reason == "stop"


def test_stream_handles_frames_fragmented_across_chunks(make_provider) -> None:
    body = b"".join(_text_chunks())
    cuts = [1, 8, 17, len(body) // 2, len(body) - 2]
    chunks = [body[start:end] for start, end in zip([0, *cuts], [*cuts, len(body)], strict=True)]

    provider = make_provider(lambda request: _sse(chunks))
    events = list(provider.stream(_request()))

    assert "".join(event.text or "" for event in events) == "Hello"
    assert events[-1].type == "done"


def test_stream_ignores_comments_and_non_data_fields(make_provider) -> None:
    chunks = [
        b": keep-alive\n\n",
        b"event: ping\n\n",
        _frame({"choices": [{"index": 0, "delta": {"content": "Hi"}}]}),
        b"\n",
        _done(),
    ]
    provider = make_provider(lambda request: _sse(chunks))

    events = list(provider.stream(_request()))

    assert [event.type for event in events] == ["text", "done"]
    assert events[0].text == "Hi"


def test_stream_stops_at_done_marker(make_provider) -> None:
    chunks = [
        _frame({"choices": [{"index": 0, "delta": {"content": "Hi"}}]}),
        _done(),
        _frame({"choices": [{"index": 0, "delta": {"content": "after done"}}]}),
    ]
    provider = make_provider(lambda request: _sse(chunks))

    events = list(provider.stream(_request()))

    assert "".join(event.text or "" for event in events) == "Hi"
    assert [event.type for event in events].count("done") == 1


def test_stream_emits_tool_call_deltas(make_provider) -> None:
    provider = make_provider(lambda request: _sse(_tool_chunks()))

    events = list(provider.stream(_request()))
    assembled = assemble_stream(events)

    deltas = [event for event in events if event.type == "tool_call_delta"]
    assert len(deltas) == 3
    assert assembled.tool_calls[0].id == "call_1"
    assert assembled.tool_calls[0].name == "add"
    assert assembled.tool_calls[0].arguments == {"a": 2, "b": 3}
    assert events[-1].type == "done"
    assert events[-1].finish_reason == "tool_calls"


def test_stream_emits_usage_event(make_provider) -> None:
    chunks = [
        _frame({"choices": [{"index": 0, "delta": {"content": "Hi"}}]}),
        _frame(
            {
                "choices": [],
                "usage": {
                    "prompt_tokens": 40,
                    "completion_tokens": 5,
                    "prompt_tokens_details": {"cached_tokens": 32},
                },
            }
        ),
        _done(),
    ]
    provider = make_provider(lambda request: _sse(chunks))

    events = list(provider.stream(_request()))
    usage_events = [event for event in events if event.type == "usage"]

    assert len(usage_events) == 1
    usage = usage_events[0].usage
    assert usage is not None
    assert (usage.input_tokens, usage.output_tokens, usage.cached_input_tokens) == (40, 5, 32)


def test_stream_emits_done_even_without_done_marker(make_provider) -> None:
    chunks = [
        _frame({"choices": [{"index": 0, "delta": {"content": "cut off"}}]}),
        _frame({"choices": [{"index": 0, "delta": {}, "finish_reason": "length"}]}),
    ]
    provider = make_provider(lambda request: _sse(chunks))

    events = list(provider.stream(_request()))

    assert events[-1].type == "done"
    assert events[-1].finish_reason == "length"
    assert [event.type for event in events].count("done") == 1


def test_stream_defaults_done_to_tool_calls_when_only_deltas(make_provider) -> None:
    chunks = [
        _frame(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {"index": 0, "id": "c1", "function": {"name": "ping", "arguments": "{}"}}
                            ]
                        },
                    }
                ]
            }
        ),
        _done(),
    ]
    provider = make_provider(lambda request: _sse(chunks))

    events = list(provider.stream(_request()))

    assert events[-1].finish_reason == "tool_calls"


def test_stream_http_error_raises_provider_error(make_provider) -> None:
    provider = make_provider(lambda request: httpx.Response(500, text="gateway down"))

    with pytest.raises(ProviderError) as info:
        list(provider.stream(_request()))

    assert info.value.status == 500
    assert info.value.retryable is True


def test_stream_midstream_error_frame_raises_provider_error(make_provider) -> None:
    chunks = [
        _frame({"choices": [{"index": 0, "delta": {"content": "partial"}}]}),
        _frame({"error": {"message": "rate limited mid-stream", "type": "rate_limit_error"}}),
    ]
    provider = make_provider(lambda request: _sse(chunks))

    with pytest.raises(ProviderError, match="rate limited mid-stream"):
        list(provider.stream(_request()))


def test_streamed_and_non_streamed_responses_are_equivalent(make_provider) -> None:
    complete_body = {
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Adding 1 and 2",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "add", "arguments": '{"a": 1, "b": 2}'},
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 8},
    }
    stream_chunks = [
        _frame({"choices": [{"index": 0, "delta": {"role": "assistant", "content": "Adding "}}]}),
        _frame({"choices": [{"index": 0, "delta": {"content": "1 and 2"}}]}),
        _frame(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {"name": "add", "arguments": '{"a": 1, "b": 2}'},
                                }
                            ]
                        },
                    }
                ]
            }
        ),
        _frame({"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]}),
        _frame({"choices": [], "usage": {"prompt_tokens": 20, "completion_tokens": 8}}),
        _done(),
    ]
    completing = make_provider(lambda request: httpx.Response(200, json=complete_body))
    streaming = make_provider(lambda request: _sse(stream_chunks))

    completed = completing.complete(_request())
    assembled = assemble_stream(list(streaming.stream(_request())))

    assert assembled.text == completed.text
    assert [call.to_dict() for call in assembled.tool_calls] == [
        call.to_dict() for call in completed.tool_calls
    ]
    assert assembled.usage == completed.usage
    assert assembled.finish_reason == completed.finish_reason
