"""MCP client-side security controls (week 5).

Why this module exists
----------------------
Connecting an agent to a third-party MCP server is a *supply-chain* decision.
The protocol can tell you what a server claims; it cannot tell you whether the
claims are honest, stable, or safe to act on. The failure modes are concrete
(docs/research/02-frameworks-protocols.md §1.1, "Security posture"):

- **Tool poisoning / rug pull.** A server advertises a benign tool description,
  the human approves it, then the description changes to include malicious
  instructions or a destructive default. Clients must pin the description.
- **Untrusted servers.** An agent that connects to whatever server a tool output
  or a user message names has handed an attacker a capability channel. Keep a
  trust list.
- **Confused deputy / token passthrough.** Passing the user's OAuth token or API
  key through to a remote tool lets the server act as the user. MCP servers are
  OAuth *resource servers*; the client should never forward user credentials as
  ordinary tool arguments.

What breaks without it
----------------------
- A malicious server quietly changes ``search`` into ``delete`` between runs and
  the agent executes it.
- A prompt-injected message points the client at ``http://attacker/mcp`` and the
  agent starts calling it.
- The user's bearer token ends up in a third-party server's logs.

Read first: docs/research/02-frameworks-protocols.md §1.1 (Security posture) and
the MCP authorization spec page.

Public surface
--------------
``RemoteToolLike``            structural view of a discovered tool (name etc.)
``tool_digest``               canonical sha-256 fingerprint of a tool declaration
``ServerTrustPolicy``         allowlist of trusted server identities
``ToolPinStore``              first-contact pinning + digest verification
``TokenPassthroughPolicy``    refuse credential-like tool arguments
``MCPClientSecurity``         facade the client calls at each boundary
``SecurityPolicyError``       base class for the checks below
``UntrustedServerError``      server is not in the trust list
``ToolPoisoningError``        tool declaration changed or an unpinned tool appeared
``TokenPassthroughBlocked``   a credential-like argument would cross the boundary
``ToolNotAllowedError``       tool is outside the client's allowlist
"""

from __future__ import annotations

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
    """Canonical sha-256 digest of a tool declaration.

    Contract:
        - hashes ``{"name", "description", "inputSchema"}`` with sorted keys and
          compact separators, so dict insertion order does not change the digest;
        - stable across processes and runs;
        - changes when the name, the description, or the schema changes.
    """
    raise NotImplementedError("Week 5 lab: implement tool_digest")


@dataclass(frozen=True, slots=True)
class ServerTrustPolicy:
    """An allowlist of trusted server identities.

    Identity comes from the server's self-declared ``serverInfo.name`` in
    ``server/discover``. Self-declared identity is only a weak signal on its own
    (a hostile server can claim any name), which is why MCP also layers OAuth
    resource indicators and DNS/registry verification -- this lab teaches the
    policy seam, not transport authentication.
    """

    allowed_servers: frozenset[str]

    def check(self, server_name: str) -> None:
        """Raise :class:`UntrustedServerError` when the server is not trusted."""
        raise NotImplementedError("Week 5 lab: implement ServerTrustPolicy.check")


class ToolPinStore:
    """Pins tool declarations on first contact and verifies them afterwards.

    Contract:
        - ``pin(server_name, tools)`` records each tool's digest; re-pinning an
          already-pinned server raises ``ValueError`` (pins are loaded once);
        - ``verify(server_name, tools)`` raises :class:`ToolPoisoningError` when a
          known tool's digest changed, or when a tool appears that was never
          pinned (``allow_new_tools=False``);
        - removing a tool is allowed (servers evolve); only *silent extension* and
          *mutation* are dangerous;
        - ``pinned_digests(server_name)`` returns a copy of the pins.
    """

    def __init__(self, *, allow_new_tools: bool = False) -> None:
        self.allow_new_tools = allow_new_tools
        self._pins: dict[str, dict[str, str]] = {}

    def pin(self, server_name: str, tools: Sequence[RemoteToolLike]) -> tuple[str, ...]:
        """Pin the current declarations; return the newly pinned tool names."""
        raise NotImplementedError("Week 5 lab: implement ToolPinStore.pin")

    def is_pinned(self, server_name: str) -> bool:
        """True when this server has already been pinned."""
        raise NotImplementedError("Week 5 lab: implement ToolPinStore.is_pinned")

    def verify(self, server_name: str, tools: Sequence[RemoteToolLike]) -> None:
        """Verify declarations against the pins (see class contract)."""
        raise NotImplementedError("Week 5 lab: implement ToolPinStore.verify")

    def pinned_digests(self, server_name: str) -> dict[str, str]:
        """A copy of the pinned ``{tool_name: digest}`` mapping."""
        raise NotImplementedError("Week 5 lab: implement ToolPinStore.pinned_digests")


#: Argument names that strongly suggest a credential. MCP servers authenticate
#: the *client* via the transport's OAuth layer; a credential in tool arguments
#: is either a design smell or an exfiltration attempt.
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
        """Raise :class:`TokenPassthroughBlocked` for any forbidden top-level key.

        Matching is case-insensitive. Nested objects are the caller's
        responsibility in this subset; a production policy should walk the whole
        argument tree.
        """
        raise NotImplementedError("Week 5 lab: implement TokenPassthroughPolicy.check")


@dataclass(frozen=True, slots=True)
class MCPClientSecurity:
    """The facade an :class:`agentlab.mcp.client.MCPClient` consults at each step.

    Ordering contract:
        1. ``check_server``  -- after ``server/discover``, before listing tools;
        2. ``check_tools``   -- after ``tools/list``; pins on first contact;
        3. ``check_call``    -- before sending ``tools/call``: token passthrough
           first, then the tool allowlist (so a blocked credential never leaves
           the process, even for an allowed tool).
    """

    trust: ServerTrustPolicy | None = None
    pins: ToolPinStore | None = None
    tokens: TokenPassthroughPolicy | None = None
    allowed_tools: frozenset[str] | None = None

    def check_server(self, server_name: str) -> None:
        """Apply the trust list, if configured."""
        raise NotImplementedError("Week 5 lab: implement MCPClientSecurity.check_server")

    def check_tools(self, server_name: str, tools: Sequence[RemoteToolLike]) -> None:
        """Pin on first contact, verify afterwards; enforce the allowlist."""
        raise NotImplementedError("Week 5 lab: implement MCPClientSecurity.check_tools")

    def check_call(self, tool_name: str, arguments: Mapping[str, Any]) -> None:
        """Block credential passthrough, then enforce the tool allowlist."""
        raise NotImplementedError("Week 5 lab: implement MCPClientSecurity.check_call")
