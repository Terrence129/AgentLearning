"""Typed failures for the guard layer.

Guard failures are not bugs in the agent -- they are the *system working*. A
blocked injection, a denied path, a rejected replayed approval and an exhausted
quota are all expected outcomes, and each one needs a distinct name so that:

- the agent loop can convert it into a safe observation for the model;
- the audit log can record a decision instead of a crash;
- an incident review can count them by category.

They all derive from ``agentlab.errors.AgentError`` so a caller that already
handles agent errors treats a guard decision as an agent error rather than a
programming bug. Nothing here is retryable except by changing the request.
"""

from __future__ import annotations

from agentlab.errors import AgentError


class GuardError(AgentError):
    """Base class for every guard-layer decision and refusal."""


class InjectionBlocked(GuardError):
    """Untrusted content was rejected as a prompt-injection attempt."""


class SandboxViolation(GuardError):
    """A sandboxed action was refused before it could run."""


class PathNotAllowed(SandboxViolation):
    """A model-supplied path escaped (or tried to escape) the allowed roots."""


class ToolNotAllowed(SandboxViolation):
    """The tool is not on the sandbox's allowlist for this run."""


class SandboxLimitExceeded(SandboxViolation):
    """A size/output/time limit was exceeded."""


class SandboxTimeout(SandboxViolation):
    """A subprocess outlived its time limit and was killed."""


class ApprovalRequired(SandboxViolation):
    """A write action was attempted without a valid, unused approval."""


class AuthorizationError(GuardError):
    """The effective authority does not grant the requested capability."""


class TokenPassthroughError(GuardError):
    """Caller credentials were about to be forwarded to an upstream service."""


class QuotaExceeded(GuardError):
    """A tenant's rate limit or budget is exhausted."""


class RoutingError(GuardError):
    """No model candidate satisfies the request (cost, latency, reliability)."""


class RequestCancelled(GuardError):
    """The caller cancelled; routing must never retry a cancelled request."""


class AuditViolation(GuardError):
    """An attempt to mutate an append-only audit log was rejected."""
