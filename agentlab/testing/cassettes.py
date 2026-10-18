"""Record/replay provider calls (the "HTTP cassette" idea, simplified).

Why this matters:

- Real API responses change. A test suite that calls a live model is flaky and
  slow; a test suite that only uses hand-written mocks can drift away from what
  the provider actually sends.
- A cassette sits in between: record one real interaction, commit it, replay it
  forever. You get realism without network flakiness.

This is the same idea behind ``vcrpy`` for HTTP. Building a tiny version
yourself removes the magic.

Usage::

    inner = OpenAICompatibleProvider(config)
    provider = CassetteProvider(inner, "tests/fixtures/cassettes/week01.json", mode="record")
    provider.complete(request)          # records
    ...
    provider.close()                    # flushes to disk

    # later / CI:
    replay = CassetteProvider(None, same_path, mode="replay")
    replay.complete(request)            # never touches the network
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal

from agentlab.errors import ProviderError
from agentlab.types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    StreamEvent,
    ToolCall,
    Usage,
)

Mode = Literal["record", "replay", "auto"]

_FRAME_VERSION = 1


def request_key(request: CompletionRequest) -> str:
    """Stable content hash, so the same logical request maps to the same entry."""
    payload = {
        "model": request.model,
        "messages": [m.to_dict() for m in request.messages],
        "tools": [t.as_openai_tool() for t in request.tools],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "response_format": request.response_format,
        "stop": request.stop,
        "extra": request.extra,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _response_to_dict(response: CompletionResponse) -> dict[str, Any]:
    return {
        "message": response.message.to_dict(),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cached_input_tokens": response.usage.cached_input_tokens,
        },
        "finish_reason": response.finish_reason,
        "model": response.model,
    }


def _response_from_dict(payload: dict[str, Any]) -> CompletionResponse:
    msg = payload["message"]
    tool_calls = [
        ToolCall(id=tc["id"], name=tc["name"], arguments=tc.get("arguments", {}))
        for tc in msg.get("tool_calls", [])
    ]
    usage = payload.get("usage", {})
    return CompletionResponse(
        message=Message(
            role=msg["role"],
            content=msg.get("content"),
            tool_calls=tool_calls,
            tool_call_id=msg.get("tool_call_id"),
            name=msg.get("name"),
        ),
        usage=Usage(
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            cached_input_tokens=usage.get("cached_input_tokens", 0),
        ),
        finish_reason=payload.get("finish_reason", "stop"),
        model=payload.get("model", ""),
    )


class CassetteProvider:
    """Wraps another provider and persists its responses to a JSON file."""

    def __init__(self, inner: Any, path: str | Path, *, mode: Mode = "auto") -> None:
        self.inner = inner
        self.path = Path(path)
        self.mode = mode
        self._entries: dict[str, Any] = {}
        self._dirty = False
        if self.path.exists():
            self._entries = json.loads(self.path.read_text(encoding="utf-8")).get("entries", {})

    @property
    def name(self) -> str:
        return getattr(self.inner, "name", "cassette")

    @property
    def model(self) -> str:
        return getattr(self.inner, "model", "cassette")

    def _lookup(self, request: CompletionRequest) -> CompletionResponse:
        key = request_key(request)
        if key in self._entries:
            return _response_from_dict(self._entries[key]["response"])
        if self.mode == "replay":
            raise ProviderError(
                f"No cassette entry for request in {self.path}. "
                f"Key={key[:12]}… Record it with mode='record' first.",
                retryable=False,
            )
        if self.inner is None:
            raise ProviderError(
                f"No cassette entry and no inner provider (mode={self.mode!r}).", retryable=False
            )
        if self.mode == "auto":
            response = self.inner.complete(request)
            self._store(key, request, response)
            return response
        raise ProviderError(f"Cassette mode {self.mode!r} cannot serve an unknown request.", retryable=False)

    def _store(self, key: str, request: CompletionRequest, response: CompletionResponse) -> None:
        self._entries[key] = {
            "request": {
                "model": request.model,
                "messages": [m.to_dict() for m in request.messages],
            },
            "response": _response_to_dict(response),
        }
        self._dirty = True

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        if self.mode == "record":
            if self.inner is None:
                raise ProviderError("Cannot record without an inner provider.", retryable=False)
            response = self.inner.complete(request)
            self._store(request_key(request), request, response)
            return response
        return self._lookup(request)

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        """Streaming through a cassette is intentionally not implemented.

        Streams are awkward to serialize faithfully (partial frames, timing) and
        the labs only need cassette replay for non-streaming calls. Implementing
        this is a good stretch exercise for week 3.
        """
        raise NotImplementedError(
            "CassetteProvider.stream is not implemented by design. "
            "Record/replay non-streaming completions instead, or design your own frame format."
        )

    def close(self) -> None:
        if self._dirty:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    {"version": _FRAME_VERSION, "entries": self._entries}, indent=2, ensure_ascii=False
                ),
                encoding="utf-8",
            )
            self._dirty = False

    def __enter__(self) -> CassetteProvider:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
