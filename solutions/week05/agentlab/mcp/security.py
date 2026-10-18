"""MCP client-side security controls (week 5).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from agentlab.errors import AgentError


class SecurityPolicyError(AgentError):
    """A client-side MCP security policy refused an operation."""


class UntrustedServerError(SecurityPolicyError):
    """The server identity is not in the client's trust list."""


class ToolPoisoningError(SecurityPolicyError):
    """A tool declaration changed after pinning, or an unpinned tool appeared."""


class TokenPassthroughBlocked(SecurityPolicyError):
    """A credential-like value was about to be forwarded to an MCP server."""


class ToolNotAllowedError(SecurityPolicyError):
    """The tool is outside the configured allowlist."""


class RemoteToolLike(Protocol):
    """Anything that looks like a discovered remote tool (structurally typed)."""

    name: str
    description: str
    input_schema: dict[str, Any]


def tool_digest(tool: RemoteToolLike) -> str:
    payload = {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.input_schema,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ServerTrustPolicy:
    """An allowlist of trusted server identities."""

    allowed_servers: frozenset[str]

    def check(self, server_name: str) -> None:
        if server_name not in self.allowed_servers:
            raise UntrustedServerError(f"server {server_name!r} is not in the trust list; refusing to use it")


class ToolPinStore:
    """Pins tool declarations on first contact and verifies them afterwards."""

    def __init__(self, *, allow_new_tools: bool = False) -> None:
        self.allow_new_tools = allow_new_tools
        self._pins: dict[str, dict[str, str]] = {}

    def pin(self, server_name: str, tools: Sequence[RemoteToolLike]) -> tuple[str, ...]:
        if server_name in self._pins:
            raise ValueError(f"server {server_name!r} is already pinned")
        pins = {tool.name: tool_digest(tool) for tool in tools}
        self._pins[server_name] = pins
        return tuple(pins)

    def is_pinned(self, server_name: str) -> bool:
        return server_name in self._pins

    def verify(self, server_name: str, tools: Sequence[RemoteToolLike]) -> None:
        pins = self._pins.get(server_name)
        if pins is None:
            raise ToolPoisoningError(
                f"server {server_name!r} has no pins; pin it on first contact before verifying"
            )
        for tool in tools:
            digest = tool_digest(tool)
            pinned = pins.get(tool.name)
            if pinned is None:
                if not self.allow_new_tools:
                    raise ToolPoisoningError(
                        f"new tool {tool.name!r} appeared after pinning server "
                        f"{server_name!r}; refusing an unpinned capability"
                    )
                continue
            if pinned != digest:
                raise ToolPoisoningError(
                    f"tool {tool.name!r} declaration changed after pinning server "
                    f"{server_name!r} (digest mismatch)"
                )

    def pinned_digests(self, server_name: str) -> dict[str, str]:
        return dict(self._pins.get(server_name, {}))


DEFAULT_FORBIDDEN_ARGUMENT_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "client_secret",
        "password",
        "refresh_token",
        "secret",
        "token",
    }
)


@dataclass(frozen=True, slots=True)
class TokenPassthroughPolicy:
    """Refuse to forward credential-like tool arguments to a remote server."""

    forbidden_keys: frozenset[str] = DEFAULT_FORBIDDEN_ARGUMENT_KEYS

    def check(self, arguments: Mapping[str, Any]) -> None:
        for key in arguments:
            if str(key).lower() in self.forbidden_keys:
                raise TokenPassthroughBlocked(
                    f"refusing to forward credential-like argument {key!r} to an MCP server; "
                    "authenticate via the transport (OAuth resource server), never via tool "
                    "arguments"
                )


@dataclass(frozen=True, slots=True)
class MCPClientSecurity:
    """The facade an MCP client consults at each boundary."""

    trust: ServerTrustPolicy | None = None
    pins: ToolPinStore | None = None
    tokens: TokenPassthroughPolicy | None = None
    allowed_tools: frozenset[str] | None = None

    def check_server(self, server_name: str) -> None:
        if self.trust is not None:
            self.trust.check(server_name)

    def check_tools(self, server_name: str, tools: Sequence[RemoteToolLike]) -> None:
        if self.allowed_tools is not None:
            for tool in tools:
                if tool.name not in self.allowed_tools:
                    raise ToolNotAllowedError(f"tool {tool.name!r} is not in the client allowlist")
        if self.pins is not None:
            if not self.pins.is_pinned(server_name):
                self.pins.pin(server_name, tools)
            else:
                self.pins.verify(server_name, tools)

    def check_call(self, tool_name: str, arguments: Mapping[str, Any]) -> None:
        if self.tokens is not None:
            self.tokens.check(arguments)
        if self.allowed_tools is not None and tool_name not in self.allowed_tools:
            raise ToolNotAllowedError(f"tool {tool_name!r} is not in the client allowlist")
