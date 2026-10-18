"""A scripted provider: the single most useful test tool in agent engineering.

Any agent is ``state -> model -> action -> state``. If you can swap the model for
a script, every test becomes as deterministic as testing a parser. This is why
"evals first" is easier than it sounds: start by making your agent testable.

Rules of thumb that these helpers encode:

- Script *behaviour*, not prompts. A test should say "the model asks to call
  ``search`` then answers", not "the prompt contains the word search".
- Keep a call log (``provider.calls``) and assert on what was sent: tool schemas,
  message order, and compaction decisions are all observable contracts.
- Make exhaustion loud. A script that runs out is a bug in the test or the loop,
  never something to silently paper over.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field

from agentlab.errors import ProviderError
from agentlab.types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    StreamEvent,
    ToolCall,
    Usage,
)


@dataclass(slots=True)
class MockTurn:
    """One scripted assistant turn."""

    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None
    usage: Usage | None = None

    def as_response(self, model: str) -> CompletionResponse:
        reason = self.finish_reason or ("tool_calls" if self.tool_calls else "stop")
        return CompletionResponse(
            message=Message.assistant(self.text, self.tool_calls),
            usage=self.usage or Usage(),
            finish_reason=reason,
            model=model,
        )


def text_turn(text: str, *, usage: Usage | None = None, finish_reason: str = "stop") -> MockTurn:
    """Assistant replies with text only."""
    return MockTurn(text=text, usage=usage, finish_reason=finish_reason)


def tool_turn(
    name: str,
    arguments: dict | None = None,
    *,
    call_id: str = "call_1",
    text: str | None = None,
    usage: Usage | None = None,
    extra_calls: Sequence[tuple[str, dict]] | None = None,
    finish_reason: str = "tool_calls",
) -> MockTurn:
    """Assistant asks to call one or more tools.

    ``extra_calls`` adds parallel tool calls: ``[("search", {"q": "x"})]``.
    """
    calls = [ToolCall(id=call_id, name=name, arguments=arguments or {})]
    for i, (extra_name, extra_args) in enumerate(extra_calls or (), start=2):
        calls.append(ToolCall(id=f"call_{i}", name=extra_name, arguments=dict(extra_args)))
    return MockTurn(text=text, tool_calls=calls, usage=usage, finish_reason=finish_reason)


class MockProvider:
    """Replays a fixed sequence of turns.

    Implements the ``Provider`` protocol, so it can be passed anywhere a real
    provider is accepted.
    """

    def __init__(
        self,
        turns: Sequence[MockTurn] | None = None,
        *,
        model: str = "mock-1",
        name: str = "mock",
        repeat_last: bool = False,
    ) -> None:
        self._turns: list[MockTurn] = list(turns or [])
        self.model = model
        self.name = name
        self.repeat_last = repeat_last
        self.calls: list[CompletionRequest] = []

    # -- script management -------------------------------------------------

    def queue(self, *turns: MockTurn) -> MockProvider:
        self._turns.extend(turns)
        return self

    @property
    def remaining(self) -> int:
        return len(self._turns)

    def _next_turn(self, request: CompletionRequest) -> MockTurn:
        self.calls.append(request)
        if not self._turns:
            raise ProviderError(
                "MockProvider script exhausted: the agent made more model calls than the "
                "test scripted. Add another turn or assert the loop should have stopped.",
                retryable=False,
            )
        if self.repeat_last and len(self._turns) == 1:
            return self._turns[0]
        return self._turns.pop(0)

    # -- Provider protocol -------------------------------------------------

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        return self._next_turn(request).as_response(self.model)

    def stream(self, request: CompletionRequest) -> Iterator[StreamEvent]:
        turn = self._next_turn(request)
        if turn.text:
            for chunk in _chunk_text(turn.text):
                yield StreamEvent(type="text", text=chunk)
        for index, call in enumerate(turn.tool_calls):
            yield StreamEvent(
                type="tool_call_delta",
                index=index,
                id=call.id,
                name=call.name,
                arguments_delta=json.dumps(call.arguments),
            )
        if turn.usage:
            yield StreamEvent(type="usage", usage=turn.usage)
        yield StreamEvent(
            type="done",
            finish_reason=turn.finish_reason or ("tool_calls" if turn.tool_calls else "stop"),
        )


def _chunk_text(text: str, size: int = 4) -> list[str]:
    """Split text into small deltas that preserve the original exactly."""
    return [text[i : i + size] for i in range(0, len(text), size)]
