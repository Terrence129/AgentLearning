"""Tool declaration, validation and invocation.

Design decisions worth studying, because they recur in every framework:

1. **One object owns both halves of a tool** -- the JSON Schema shown to the
   model and the Python handler that runs. Keeping them together is the only
   way to stop schema/implementation drift.
2. **Validation happens before execution.** A model can and will emit arguments
   that violate the schema; fail at the boundary, not halfway through a side
   effect.
3. **Errors become data.** ``invoke`` never raises for a tool-level problem; it
   returns ``ToolResult(ok=False, ...)`` which the loop feeds back to the model
   as an observation. That single decision is one of the biggest reliability
   differences between a demo and an agent that recovers from mistakes.
4. **Outputs are truncated.** Tool output is context; unbounded tool output is
   how agents die at 90% of the context window.
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ValidationError

from agentlab.types import ToolSpec

JSONSchema = dict[str, Any]

DEFAULT_MAX_OUTPUT_CHARS = 8_000


@dataclass(slots=True)
class ToolResult:
    """The outcome of invoking a tool, in a form that is safe to show the model."""

    ok: bool
    output: str
    error: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    truncated: bool = False

    @classmethod
    def success(cls, output: Any, *, meta: dict[str, Any] | None = None) -> ToolResult:
        return cls(ok=True, output=_stringify(output), meta=meta or {})

    @classmethod
    def failure(cls, error: str, *, meta: dict[str, Any] | None = None) -> ToolResult:
        return cls(ok=False, output=f"ERROR: {error}", error=error, meta=meta or {})

    def as_observation(self) -> str:
        """What the model sees as the tool message content."""
        return self.output


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)


@dataclass(slots=True)
class Tool:
    """A callable capability exposed to the model."""

    name: str
    description: str
    parameters: JSONSchema
    handler: Callable[[Any], Any]
    input_model: type[BaseModel] | None = None
    is_write: bool = False
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS

    def spec(self) -> ToolSpec:
        return ToolSpec(name=self.name, description=self.description, parameters=self.parameters)

    def invoke(self, arguments: Mapping[str, Any] | None) -> ToolResult:
        args = dict(arguments or {})
        try:
            if self.input_model is not None:
                validated = self.input_model.model_validate(args)
                result = self.handler(validated)
            else:
                result = self.handler(args)
        except ValidationError as exc:
            return ToolResult.failure(
                f"arguments for tool {self.name!r} do not match its schema: {exc.errors()}"
            )
        except Exception as exc:  # tool bugs are observations, not crashes
            return ToolResult.failure(f"tool {self.name!r} raised {type(exc).__name__}: {exc}")

        text = _stringify(result)
        truncated = len(text) > self.max_output_chars
        if truncated:
            text = (
                text[: self.max_output_chars] + f"\n...[truncated {len(text) - self.max_output_chars} chars]"
            )
        return ToolResult(ok=True, output=text, truncated=truncated)


class ToolRegistry:
    """A named collection of tools plus the glue to expose them to a model."""

    def __init__(self, tools: Iterable[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools or ():
            self.register(tool)

    # -- registration ------------------------------------------------------

    def register(self, tool: Tool) -> ToolRegistry:
        if tool.name in self._tools:
            raise ValueError(f"tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool
        return self

    def add(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        input_model: type[BaseModel] | None = None,
        parameters: JSONSchema | None = None,
        is_write: bool = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator form::

        @registry.add(description="Add two integers", input_model=AddInput)
        def add(args: AddInput) -> int:
            return args.a + args.b
        """

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            model = input_model or _model_from_callable(fn)
            schema = parameters or (model.model_json_schema() if model is not None else _empty_schema())
            self.register(
                Tool(
                    name=name or fn.__name__,
                    description=description or (inspect.getdoc(fn) or fn.__name__),
                    parameters=schema,
                    handler=fn,
                    input_model=model,
                    is_write=is_write,
                )
            )
            return fn

        return decorator

    # -- access ------------------------------------------------------------

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def tools(self) -> list[Tool]:
        return list(self._tools.values())

    def specs(self) -> list[ToolSpec]:
        return [tool.spec() for tool in self._tools.values()]

    def openai_tools(self) -> list[dict[str, Any]]:
        return [tool.spec().as_openai_tool() for tool in self._tools.values()]

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)

    # -- invocation --------------------------------------------------------

    def invoke(self, name: str, arguments: Mapping[str, Any] | None = None) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult.failure(
                f"unknown tool {name!r}; available tools: {', '.join(self.names()) or 'none'}"
            )
        return tool.invoke(arguments)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _empty_schema() -> JSONSchema:
    return {"type": "object", "properties": {}, "additionalProperties": False}


def _model_from_callable(fn: Callable[..., Any]) -> type[BaseModel] | None:
    """Best-effort inference of a single pydantic-model parameter."""
    try:
        hints = inspect.get_annotations(fn, eval_str=True)
    except Exception:
        return None
    candidates = [h for h in hints.values() if inspect.isclass(h) and issubclass(h, BaseModel)]
    return candidates[0] if len(candidates) == 1 else None


def schema_from_model(model: type[BaseModel]) -> JSONSchema:
    """JSON Schema for a pydantic model, with the provider-friendly extras."""
    schema = model.model_json_schema()
    schema.setdefault("additionalProperties", False)
    return schema
