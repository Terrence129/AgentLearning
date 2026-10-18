"""Reference solution -- week 1: the OpenAI-compatible provider seam.

Design notes worth comparing against your own build:

- **Retries live behind the seam.** ``complete`` is the only place that knows
  about 429s, ``Retry-After`` and connection resets; callers get one exception
  type with an explicit ``retryable`` flag.
- **The wire contract is a pure function.** ``_build_payload`` and
  ``_parse_response`` do not perform I/O, which is why they can be tested
  exhaustively without a network.
- **Streaming is assembled, not special-cased.** ``stream`` yields the smallest
  honest events; folding them back into a response is the provided
  ``assemble_stream``'s job, which is what makes the stream/complete equivalence
  test possible.
"""

from __future__ import annotations

import json
import random
import time
from collections.abc import Iterator
from typing import Any

import httpx
from agentlab.config import ProviderConfig
from agentlab.errors import ProviderError
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
        """Map a ``CompletionRequest`` onto the provider's JSON body."""
        payload: dict[str, Any] = {
            "model": request.model or self.model,
            "messages": messages_to_wire(request.messages),
            "stream": stream,
        }
        if request.tools:
            payload["tools"] = [spec.as_openai_tool() for spec in request.tools]
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.response_format is not None:
            payload["response_format"] = request.response_format
        if request.stop is not None:
            payload["stop"] = request.stop
        if stream:
            # Ask for the final usage frame; servers that do not support the
            # option ignore it, servers that do will make cost measurable.
            payload["stream_options"] = {"include_usage": True}
        # Merged last by contract: callers may override any provider-specific knob.
        payload.update(request.extra)
        return payload

    @staticmethod
    def _parse_response(payload: dict[str, Any], *, fallback_model: str = "") -> CompletionResponse:
        """Turn a non-streaming response body into ``CompletionResponse``."""
        choices = payload.get("choices") or []
        if not choices:
            raise ProviderError("provider response contained no choices", retryable=False, body=payload)
        choice = choices[0]
        raw_message = choice.get("message") or {}
        message = Message.assistant(
            raw_message.get("content"),
            parse_tool_calls(raw_message.get("tool_calls")),
        )
        return CompletionResponse(
            message=message,
            usage=usage_from_wire(payload.get("usage")),
            finish_reason=choice.get("finish_reason") or "stop",
            model=payload.get("model") or fallback_model,
            raw=payload,
        )

    # -- retry helpers -----------------------------------------------------

    def _sleep_before_retry(self, failed_attempt: int, retry_after: float | None) -> None:
        """Sleep between attempts: obey the server, otherwise back off with jitter."""
        if retry_after is not None:
            delay = retry_after
        else:
            delay = self.backoff_base * (2**failed_attempt)
            if self.backoff_base > 0:
                # Jitter avoids synchronised retries (the thundering-herd bug).
                delay += random.uniform(0, self.backoff_base / 2)
        if delay > 0:
            time.sleep(delay)

    # -- Provider protocol -------------------------------------------------

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """POST to ``/chat/completions`` and return the parsed response."""
        payload = self._build_payload(request, stream=False)
        last_error: ProviderError | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.post(CHAT_COMPLETIONS_PATH, json=payload)
            except httpx.TransportError as exc:
                last_error = ProviderError(
                    f"transport error calling {self.name}: {type(exc).__name__}: {exc}",
                    retryable=True,
                )
                if attempt >= self.max_retries:
                    raise last_error from exc
                self._sleep_before_retry(attempt, None)
                continue

            retry_after = parse_retry_after(response)
            if response.status_code in RETRYABLE_STATUS:
                last_error = ProviderError(
                    f"provider {self.name} returned HTTP {response.status_code}",
                    status=response.status_code,
                    retryable=True,
                    retry_after=retry_after,
                    body=_body_text(response),
                )
                if attempt >= self.max_retries:
                    raise last_error
                self._sleep_before_retry(attempt, retry_after)
                continue

            if response.status_code >= 400:
                # Other 4xx: the request itself is wrong, so retrying repeats the bug.
                raise ProviderError(
                    f"provider {self.name} rejected the request with HTTP {response.status_code}",
                    status=response.status_code,
                    retryable=False,
                    body=_body_text(response),
                )

            try:
                body = response.json()
            except ValueError as exc:
                raise ProviderError(
                    f"provider {self.name} returned a non-JSON body: {exc}",
                    status=response.status_code,
                    retryable=False,
                    body=_body_text(response),
                ) from exc
            if not isinstance(body, dict):
                raise ProviderError(
                    f"provider {self.name} returned JSON that is not an object",
                    status=response.status_code,
                    retryable=False,
                    body=_body_text(response),
                )
            return self._parse_response(body, fallback_model=request.model or self.model)

        # The loop always returns or raises; this keeps type-checkers honest.
        raise last_error or ProviderError(f"provider {self.name} call failed", retryable=False)

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        """Consume a server-sent-events stream and yield ``StreamEvent``s."""
        payload = self._build_payload(request, stream=True)

        with self._client.stream("POST", CHAT_COMPLETIONS_PATH, json=payload) as response:
            if response.status_code != 200:
                response.read()
                raise ProviderError(
                    f"provider {self.name} returned HTTP {response.status_code} for a stream",
                    status=response.status_code,
                    retryable=response.status_code in RETRYABLE_STATUS,
                    body=_body_text(response),
                )

            last_finish_reason: str | None = None
            saw_tool_deltas = False
            done_emitted = False

            for raw_line in response.iter_lines():
                line = raw_line.strip()
                if not line or line.startswith(":"):
                    continue  # blank separator or SSE comment / heartbeat
                if not line.startswith("data:"):
                    continue  # event:, id:, retry: -- not part of the payload
                data = line[len("data:") :].strip()
                if not data:
                    continue
                if data == "[DONE]":
                    yield StreamEvent(
                        type="done", finish_reason=_done_reason(last_finish_reason, saw_tool_deltas)
                    )
                    done_emitted = True
                    break
                try:
                    chunk = json.loads(data)
                except ValueError as exc:
                    raise ProviderError(
                        f"malformed SSE frame from {self.name}: {exc} (data={data[:200]!r})",
                        retryable=False,
                    ) from exc
                if not isinstance(chunk, dict):
                    raise ProviderError(f"SSE frame from {self.name} is not a JSON object", retryable=False)
                if chunk.get("error"):
                    raise ProviderError(
                        f"provider stream error from {self.name}: {_error_message(chunk['error'])}",
                        retryable=False,
                        body=chunk,
                    )

                if chunk.get("usage"):
                    yield StreamEvent(type="usage", usage=usage_from_wire(chunk["usage"]))

                for choice in chunk.get("choices") or ():
                    delta = choice.get("delta") or {}
                    content = delta.get("content")
                    if content:
                        yield StreamEvent(type="text", text=content)
                    for tool_call in delta.get("tool_calls") or ():
                        saw_tool_deltas = True
                        function = tool_call.get("function") or {}
                        yield StreamEvent(
                            type="tool_call_delta",
                            index=tool_call.get("index"),
                            id=tool_call.get("id"),
                            name=function.get("name"),
                            arguments_delta=function.get("arguments"),
                        )
                    if choice.get("finish_reason"):
                        last_finish_reason = choice["finish_reason"]

            if not done_emitted:
                yield StreamEvent(
                    type="done", finish_reason=_done_reason(last_finish_reason, saw_tool_deltas)
                )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _done_reason(last_finish_reason: str | None, saw_tool_deltas: bool) -> str:
    if last_finish_reason:
        return last_finish_reason
    return "tool_calls" if saw_tool_deltas else "stop"


def _body_text(response: httpx.Response) -> str | None:
    """A truncated body for error reporting -- never a full HTML error page."""
    try:
        text = response.text
    except Exception:  # noqa: BLE001 - diagnostics must never mask the real error
        return None
    return text[:MAX_ERROR_BODY_CHARS]


def parse_retry_after(response: httpx.Response) -> float | None:
    """Seconds from a numeric ``Retry-After`` header, else ``None``.

    The HTTP-date form is intentionally unsupported: chat providers send seconds,
    and guessing a clock skew is how you introduce a 40-second sleep bug.
    """
    raw = response.headers.get("retry-after")
    if not raw:
        return None
    try:
        seconds = float(raw)
    except ValueError:
        return None
    return seconds if seconds >= 0 else None


def _error_message(error: Any) -> str:
    if isinstance(error, dict):
        return str(error.get("message") or error)
    return str(error)


def messages_to_wire(messages: list[Message]) -> list[dict[str, Any]]:
    """Convert core messages to the OpenAI wire shape (provided helper)."""
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
    """Normalise provider tool calls into ``ToolCall`` objects (provided helper)."""
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
    """Map provider usage fields to ``Usage`` (provided helper)."""
    raw = raw or {}
    details = raw.get("prompt_tokens_details") or {}
    return Usage(
        input_tokens=int(raw.get("prompt_tokens", 0) or 0),
        output_tokens=int(raw.get("completion_tokens", 0) or 0),
        cached_input_tokens=int(details.get("cached_tokens", 0) or 0),
    )
