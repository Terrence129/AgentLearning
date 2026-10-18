"""Core wire types: messages, tools, completions, usage.

These mirror the shape of every major provider API (OpenAI, DeepSeek, Qwen,
and -- with a thin adapter -- Anthropic and Gemini). Learning this shape well
is worth more than learning any single SDK, because every SDK is a wrapper
around exactly these concepts:

    messages + tools  ->  model  ->  assistant message (text and/or tool calls)
                                         |
                                         v
                              tool results appended as messages

Design notes for learners:

- ``Message`` is deliberately close to the wire format, not to a framework's
  abstraction. When you later use LangGraph or the OpenAI Agents SDK, you can
  always answer "what actually went over the network?".
- ``content`` is ``str | None`` because an assistant turn that only calls tools
  has no text content.
- Tool arguments are a parsed ``dict``. On the wire they arrive as a JSON
  *string* (sometimes streamed in fragments) -- parsing and validation happen
  at the provider/tool boundary, which is exactly where you will implement it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]

FinishReason = Literal["stop", "length", "tool_calls", "content_filter", "error"]


@dataclass(slots=True)
class ToolCall:
    """A model's request to invoke a tool."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "arguments": self.arguments}


@dataclass(slots=True)
class Message:
    """One chat message.

    Exactly one of the following shapes is valid:

    - ``role="system"``    -> ``content`` is the system prompt
    - ``role="user"``      -> ``content`` is the user turn
    - ``role="assistant"`` -> ``content`` and/or ``tool_calls``
    - ``role="tool"``      -> ``content`` is the tool result, ``tool_call_id`` set
    """

    role: Role
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"role": self.role}
        if self.content is not None:
            out["content"] = self.content
        if self.tool_calls:
            out["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id is not None:
            out["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            out["name"] = self.name
        return out

    @classmethod
    def system(cls, content: str) -> Message:
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> Message:
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str | None = None, tool_calls: list[ToolCall] | None = None) -> Message:
        return cls(role="assistant", content=content, tool_calls=tool_calls or [])

    @classmethod
    def tool_result(cls, tool_call_id: str, content: str, name: str | None = None) -> Message:
        return cls(role="tool", content=content, tool_call_id=tool_call_id, name=name)


@dataclass(slots=True)
class ToolSpec:
    """The *declaration* of a tool, as sent to the model.

    ``parameters`` is a JSON Schema object describing the arguments. Modern
    providers can enforce this schema (strict mode / structured outputs), which
    removes a whole class of malformed tool calls -- but you still validate
    locally, because not every provider and not every model supports strict mode.
    """

    name: str
    description: str
    parameters: dict[str, Any]
    strict: bool = False

    def as_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "strict": self.strict,
            },
        }


@dataclass(slots=True)
class Usage:
    """Token accounting for one model call."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_input_tokens=self.cached_input_tokens + other.cached_input_tokens,
        )


@dataclass(slots=True)
class CompletionRequest:
    """A single model call.

    ``extra`` is an escape hatch for provider-specific knobs (reasoning effort,
    tool_choice, logprobs...). Keeping it explicit is better than a leaky
    ``**kwargs``: you can log exactly what non-portable features a lab used.
    """

    messages: list[Message]
    model: str
    tools: list[ToolSpec] = field(default_factory=list)
    temperature: float | None = None
    max_tokens: int | None = None
    response_format: dict[str, Any] | None = None
    stop: list[str] | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CompletionResponse:
    """The result of one model call."""

    message: Message
    usage: Usage = field(default_factory=Usage)
    finish_reason: str = "stop"
    model: str = ""
    raw: dict[str, Any] | None = None

    @property
    def text(self) -> str:
        return self.message.content or ""

    @property
    def tool_calls(self) -> list[ToolCall]:
        return self.message.tool_calls

    @property
    def wants_tools(self) -> bool:
        return bool(self.message.tool_calls)


@dataclass(slots=True)
class StreamEvent:
    """One event in a streamed completion.

    A single flexible event type keeps the learner's parser simple, while still
    modelling the real protocol: text arrives as deltas, tool calls arrive as
    fragments keyed by index, usage often arrives only at the end.

    ``type`` is one of: ``text`` | ``tool_call_delta`` | ``usage`` | ``done``.
    """

    type: Literal["text", "tool_call_delta", "usage", "done"]
    text: str | None = None
    index: int | None = None
    id: str | None = None
    name: str | None = None
    arguments_delta: str | None = None
    usage: Usage | None = None
    finish_reason: str | None = None
