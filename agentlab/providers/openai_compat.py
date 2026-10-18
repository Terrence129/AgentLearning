"""OpenAI-compatible chat-completions provider -- YOUR WEEK 1 BUILD.

DeepSeek, Qwen (DashScope compatible mode), Moonshot, local vLLM/Ollama servers
and OpenAI itself all speak the same wire format. That is why one adapter can
cover all of them: only ``base_url``, the key, and the model name change.

Everything below the constructor is intentionally unimplemented. Read the method
docstrings, then implement them in order:

1. ``_build_payload``      -- request object  -> JSON body
2. ``_parse_response``     -- JSON body       -> CompletionResponse
3. ``complete``            -- POST + retries + error taxonomy
4. ``stream``              -- SSE frames      -> StreamEvent iterator

The tests in ``tests/week01/`` are the specification, including the HTTP-level
edge cases (429 with Retry-After, 5xx, malformed tool arguments, fragmented SSE).

Hints kept deliberately few:
- Read the provider's API reference for the exact field names; do not guess.
- ``httpx.Client`` is injected in tests, so never construct one inside a method.
- Retries belong *here*, never in the agent loop.
- Sleep with ``time.sleep`` (tests patch it); sleep 0 when ``backoff_base`` is 0.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx

from agentlab.config import ProviderConfig
from agentlab.providers.base import parse_tool_arguments
from agentlab.types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    StreamEvent,
    ToolCall,
    Usage,
)

#: HTTP statuses that are worth retrying with backoff.
RETRYABLE_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})

#: Path appended to the provider's base URL (the client already knows the base).
CHAT_COMPLETIONS_PATH = "/chat/completions"

#: Error bodies are truncated to this many characters when surfaced in errors.
MAX_ERROR_BODY_CHARS = 200


class OpenAICompatibleProvider:
    """See module docstring. This class is the week 1 lab."""

    name: str
    model: str

    def __init__(
        self,
        config: ProviderConfig,
        *,
        timeout: float = 60.0,
        max_retries: int = 3,
        backoff_base: float = 0.5,
        client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config
        self.name = config.name
        self.model = config.model
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=config.base_url.rstrip("/"),
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
            transport=transport,
        )

    # -- lifecycle ---------------------------------------------------------

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenAICompatibleProvider:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- wire mapping ------------------------------------------------------

    def _build_payload(self, request: CompletionRequest, *, stream: bool) -> dict[str, Any]:
        """Map a ``CompletionRequest`` onto the provider's JSON body.

        Requirements:
        - ``model``: the request's model, or ``self.model`` when it is empty.
        - ``messages``: use ``messages_to_wire`` below. System/user/assistant/tool
          roles map 1:1; assistant tool calls must include ``tool_calls``; tool
          messages must include ``tool_call_id``.
        - ``tools``: ``[spec.as_openai_tool() for spec in request.tools]``; omit
          the key entirely when there are no tools (some servers reject []).
        - ``temperature`` / ``max_tokens`` / ``response_format`` / ``stop``:
          include only when not ``None``. Never send ``null`` values.
        - ``stream``: pass the argument through as a bool.
        - When ``stream`` is true, also set
          ``"stream_options": {"include_usage": True}`` so providers that support
          it emit a final usage frame. (Unsupported servers ignore the option.)
        - ``request.extra``: merged **last** via ``payload.update(request.extra)``,
          so callers can override any key, including provider-specific knobs.

        Returns a fresh dict. Must not mutate ``request``.

        TODO(week01): implement.
        """
        raise NotImplementedError("Week 1 lab: implement _build_payload")

    @staticmethod
    def _parse_response(payload: dict[str, Any], *, fallback_model: str = "") -> CompletionResponse:
        """Turn a non-streaming response body into ``CompletionResponse``.

        Mapping notes (``choices`` is a list; use the first element):
        - ``choices[0].message.content`` -> assistant text (may be null).
        - ``choices[0].message.tool_calls[*]`` -> ``ToolCall`` with parsed JSON
          arguments via ``parse_tool_calls`` below (which uses
          ``parse_tool_arguments``). A malformed argument string must raise
          ``ProviderError`` -- never crash the run with a raw ``JSONDecodeError``.
        - ``choices[0].finish_reason`` -> finish reason; default ``"stop"`` when
          missing or null.
        - ``usage`` -> ``Usage`` via ``usage_from_wire`` below (prompt_tokens ->
          input, completion_tokens -> output, prompt_tokens_details.cached_tokens
          -> cached_input_tokens). Missing usage means zeroes.
        - ``model`` -> ``payload["model"]`` or ``fallback_model`` when absent.
        - ``raw`` -> the original payload dict, retained for provenance.

        A payload with no ``choices`` is a provider/protocol error: raise
        ``ProviderError(..., retryable=False)``.

        TODO(week01): implement.
        """
        raise NotImplementedError("Week 1 lab: implement _parse_response")

    # -- Provider protocol -------------------------------------------------

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """POST to ``/chat/completions`` and return the parsed response.

        Requirements:
        - Make at most ``max_retries + 1`` attempts (so ``max_retries=0`` means a
          single attempt).
        - Retry when the status is in ``RETRYABLE_STATUS`` or when ``httpx``
          raises a ``TransportError`` (connection reset, timeout, ...).
        - Do **not** retry other 4xx responses: raise immediately with
          ``retryable=False`` (a malformed request stays malformed).
        - Delay policy between attempts:
          * if the response has a numeric ``Retry-After`` header, sleep exactly
            that many seconds (the server asked; do not second-guess it);
          * otherwise sleep ``backoff_base * 2 ** failed_attempt`` plus uniform
            jitter in ``[0, backoff_base / 2)`` (``failed_attempt`` is 0 for the
            first failure), and sleep 0 when ``backoff_base`` is 0.
        - Every final failure becomes ``ProviderError`` carrying ``status``
          (``None`` for transport errors), ``retryable``, ``retry_after`` and a
          truncated response body (``MAX_ERROR_BODY_CHARS``, ``None`` if there
          was no body). Never let an ``httpx`` exception escape this seam.
        - On success, return ``_parse_response(response.json(),
          fallback_model=request.model or self.model)``.
        - Log nothing here; the caller decides what to trace.

        TODO(week01): implement.
        """
        raise NotImplementedError("Week 1 lab: implement complete()")

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        """Consume a server-sent-events stream and yield ``StreamEvent``s.

        Requirements:
        - Request with ``stream=True`` (the ``_build_payload`` contract adds the
          usage option); the hidden tests assert what actually goes on the wire.
        - A non-200 status is an error: raise ``ProviderError`` with the status
          and body. Streaming does **not** retry (tokens may already be
          consumed); the caller decides whether to re-issue the request.
        - Parse SSE: iterate response lines; ignore blank lines, comment lines
          (``:`` prefix) and non-``data:`` fields (``event:``, ``id:``, ...).
          ``data: [DONE]`` ends the stream. Arguments can arrive split across
          network chunks -- line assembly must not assume one line per chunk.
        - ``choices[0].delta.content`` (truthy string) -> ``StreamEvent(type=
          "text", text=...)``.
        - ``choices[0].delta.tool_calls[*]`` -> one ``StreamEvent(type=
          "tool_call_delta", index=..., id=..., name=..., arguments_delta=...)``
          per entry. The JSON arguments arrive as *fragments*: forward each
          ``function.arguments`` fragment verbatim; never ``json.loads`` it.
        - A frame with a truthy ``usage`` object -> ``StreamEvent(type="usage",
          usage=usage_from_wire(...))``.
        - A frame containing an ``error`` object, or a malformed JSON data frame,
          raises ``ProviderError(retryable=False)``.
        - Emit exactly one ``StreamEvent(type="done", finish_reason=...)`` when
          the provider sends ``[DONE]`` **or** when the stream ends without it.
          Use the last non-null ``finish_reason`` seen; if the provider never
          sent one, default to ``"tool_calls"`` when tool-call deltas were seen,
          else ``"stop"``.

        This is an iterator: do not buffer the whole stream before yielding.

        TODO(week01): implement.
        """
        raise NotImplementedError("Week 1 lab: implement stream()")


# ---------------------------------------------------------------------------
# Small helpers you may use once you have implemented the methods above.
# ---------------------------------------------------------------------------


def messages_to_wire(messages: list[Message]) -> list[dict[str, Any]]:
    """Convert core messages to the OpenAI wire shape.

    This one is provided because it is mechanical; study it, then use it from
    ``_build_payload``.
    """
    wire: list[dict[str, Any]] = []
    for message in messages:
        item: dict[str, Any] = {"role": message.role, "content": message.content}
        if message.tool_calls:
            item["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {"name": call.name, "arguments": json.dumps(call.arguments)},
                }
                for call in message.tool_calls
            ]
        if message.tool_call_id is not None:
            item["tool_call_id"] = message.tool_call_id
        if message.name is not None:
            item["name"] = message.name
        wire.append(item)
    return wire


def parse_tool_calls(raw_calls: list[dict[str, Any]] | None) -> list[ToolCall]:
    """Normalise provider tool calls into ``ToolCall`` objects.

    Provided for the same reason as ``messages_to_wire``: the shape juggling is
    not the lesson. The *error policy* around malformed arguments is the lesson,
    and that stays in ``_parse_response``.
    """
    calls: list[ToolCall] = []
    for index, raw in enumerate(raw_calls or ()):
        function = raw.get("function", {})
        calls.append(
            ToolCall(
                id=raw.get("id") or f"call_{index}",
                name=function.get("name", ""),
                arguments=parse_tool_arguments(function.get("arguments", "")),
            )
        )
    return calls


def usage_from_wire(raw: dict[str, Any] | None) -> Usage:
    """Map provider usage fields to ``Usage``. Provided: mechanical, not the lesson."""
    raw = raw or {}
    details = raw.get("prompt_tokens_details") or {}
    return Usage(
        input_tokens=int(raw.get("prompt_tokens", 0) or 0),
        output_tokens=int(raw.get("completion_tokens", 0) or 0),
        cached_input_tokens=int(details.get("cached_tokens", 0) or 0),
    )
