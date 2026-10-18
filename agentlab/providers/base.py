"""The provider seam: one interface, many model vendors.

This is the same architectural move as SendOS's ``Send.Model.Adapter``: the rest
of the system talks to ``Provider``, and provider-specific concerns (auth,
retries, wire formats, streaming frames) stay behind it.

Two rules keep this seam honest:

1. **The seam owns retries, not the caller.** Rate limits and 5xx are provider
   problems; the agent loop should never contain vendor-specific error codes.
2. **The seam is where cost is measured.** Every call returns ``Usage``; that is
   what makes budget enforcement and cost-per-task possible.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from typing import Any, Protocol, runtime_checkable

from agentlab.errors import ProviderError
from agentlab.types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    StreamEvent,
    ToolCall,
    Usage,
)


@runtime_checkable
class Provider(Protocol):
    """A chat-completion backend.

    Deliberately synchronous: one call, one result, easy to debug and to test.
    Production systems usually expose async methods as well; converting this
    interface to ``async`` is a good week 6 stretch exercise.
    """

    name: str
    model: str

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Return one full completion. Raises ``ProviderError`` on failure."""
        ...

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        """Yield incremental events. Must end with a ``done`` event."""
        ...


def parse_tool_arguments(raw: str) -> dict[str, Any]:
    """Parse the JSON string a provider sends for tool arguments.

    Providers are inconsistent here: some send ``""`` for no arguments, some
    send ``"{}"``, some send malformed JSON when a model is confused. Never let
    a parse error crash the run -- surface it as ``ProviderError`` so the caller
    can retry or feed the error back to the model.
    """
    text = (raw or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"tool arguments are not valid JSON: {exc.msg} (raw={text[:200]!r})", retryable=False
        ) from exc
    if not isinstance(parsed, dict):
        raise ProviderError(
            f"tool arguments must be a JSON object, got {type(parsed).__name__}", retryable=False
        )
    return parsed


def assemble_stream(events: Sequence[StreamEvent]) -> CompletionResponse:
    """Fold a stream of events back into one ``CompletionResponse``.

    Streaming is an optimisation, not a different protocol: the assembled result
    must be equivalent to what a non-streaming call would have returned. Labs
    assert exactly that equivalence.
    """
    text_parts: list[str] = []
    # index -> {"id","name","arguments" accumulated as text}
    calls: dict[int, dict[str, str]] = {}
    usage = Usage()
    finish_reason = "stop"

    for event in events:
        if event.type == "text" and event.text:
            text_parts.append(event.text)
        elif event.type == "tool_call_delta":
            index = event.index if event.index is not None else 0
            slot = calls.setdefault(index, {"id": "", "name": "", "arguments": ""})
            if event.id:
                slot["id"] = event.id
            if event.name:
                slot["name"] = event.name
            if event.arguments_delta:
                slot["arguments"] += event.arguments_delta
        elif event.type == "usage" and event.usage is not None:
            usage = event.usage
        elif event.type == "done":
            finish_reason = event.finish_reason or finish_reason

    tool_calls = [
        ToolCall(
            id=slot["id"] or f"call_{index}",
            name=slot["name"],
            arguments=parse_tool_arguments(slot["arguments"]),
        )
        for index, slot in sorted(calls.items())
        if slot["name"]
    ]
    message = Message.assistant("".join(text_parts) or None, tool_calls)
    return CompletionResponse(message=message, usage=usage, finish_reason=finish_reason)
