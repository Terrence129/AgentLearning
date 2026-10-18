"""Typed error hierarchy.

Why a hierarchy instead of bare ``Exception``? Because agent systems fail in
*taxonomic* ways, and each class needs a different recovery policy:

- ProviderError      -> retry with backoff, or fall back to another provider
- ToolError          -> feed the error back to the model as an observation
- SchemaValidationError -> repair loop (ask the model to fix its own output)
- BudgetExceeded     -> stop the run, never retry
- MaxStepsExceeded   -> stop the run, surface a partial result
- ConfigError        -> fail fast at startup, never retry

Getting this taxonomy right is half of making an agent reliable.
"""

from __future__ import annotations

from typing import Any


class AgentError(Exception):
    """Base class for every error raised by AgentLab."""


class ConfigError(AgentError):
    """Missing or invalid configuration (env var, file, provider name)."""


class ProviderError(AgentError):
    """A model provider call failed.

    Attributes:
        status: HTTP status code when there was one.
        retryable: whether retrying the identical request could plausibly succeed.
        retry_after: seconds the provider asked us to wait, if it said so.
        body: raw response body (truncated) for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        retryable: bool = False,
        retry_after: float | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.retryable = retryable
        self.retry_after = retry_after
        self.body = body


class ToolError(AgentError):
    """A tool raised or returned an invalid result.

    Tools should normally *not* let exceptions escape into the agent loop.
    The loop catches ``ToolError`` and converts it into a tool message so the
    model can see what went wrong and try something else. This is one of the
    highest-leverage reliability techniques in agent design.
    """


class SchemaValidationError(AgentError):
    """Model output did not validate against the declared schema.

    Attributes:
        raw: the raw text the model produced.
        errors: a list of human/model readable validation problems.
    """

    def __init__(self, message: str, *, raw: str = "", errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.raw = raw
        self.errors = errors or []


class BudgetExceeded(AgentError):
    """The run would exceed a hard cost/token/step budget."""


class MaxStepsExceeded(AgentError):
    """The agent loop hit its step ceiling without terminating.

    Carries whatever partial state exists so callers can still render a result.
    """

    def __init__(self, message: str, *, steps: int = 0, last_message: Any = None) -> None:
        super().__init__(message)
        self.steps = steps
        self.last_message = last_message
