"""MCP client: discover, map remote tools into a ToolRegistry, invoke (week 5).

Why this module exists
----------------------
Writing a bespoke integration per tool does not scale; MCP turns every remote
capability into the same three operations: discover, list, call. The client is
where the protocol becomes useful to *your* agent:

1. it speaks the stateless 2026-07-28 dialect -- every request carries
   ``params._meta`` with the protocol version, client identity and capabilities
   (there is no ``initialize`` handshake to carry them);
2. it maps remote tool declarations onto the local ``ToolRegistry`` the agent
   loop already uses, so a remote tool is indistinguishable from a local one;
3. it converts protocol failures into ``ToolResult`` observations (the model can
   see and recover from them), while security refusals fail loudly.

What breaks without it
----------------------
- Every remote tool needs its own adapter, and the adapters drift.
- Protocol errors crash the loop instead of becoming an observation.
- Remote tools are missing from ``registry.specs()``, so the model never sees
  them (or sees stale descriptions after the server changes).
- Timeouts hang the run instead of failing a single tool call.

Documented divergences (see labs/week05-mcp/README.md): the transport is
synchronous, so "timeout" here means the transport raised
:class:`agentlab.mcp.transport.TransportTimeout` -- a real client implements a
deadline with async cancellation. MRTR (``resultType: "input_required"``) is
detected and rejected as unsupported rather than implemented.

Read first: docs/research/02-frameworks-protocols.md §1.1 and the MCP tools /
discovery spec pages.

Public surface
--------------
``ServerInfo``       identity reported by ``server/discover``
``RemoteTool``       a discovered tool declaration plus its security digest
``DiscoverResult``   supported versions, capabilities, identity, caching hints
``ResourceContents`` the text of one resource
``MCPError``         protocol/transport failure (not a tool-level error)
``MCPClient``        the discover -> list -> call client
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from agentlab.errors import AgentError
from agentlab.mcp.security import MCPClientSecurity
from agentlab.mcp.transport import PROTOCOL_VERSION, Transport
from agentlab.tools.registry import ToolRegistry, ToolResult


class MCPError(AgentError):
    """A protocol or transport failure while talking to an MCP server.

    Attributes:
        code: the JSON-RPC error code, when the server returned one.
        data: the JSON-RPC error ``data`` payload, when present.
    """

    def __init__(self, message: str, *, code: int | None = None, data: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.data = data


@dataclass(frozen=True, slots=True)
class ServerInfo:
    """Server identity from ``server/discover``."""

    name: str
    version: str


@dataclass(frozen=True, slots=True)
class RemoteTool:
    """One discovered tool.

    ``digest`` is the canonical fingerprint used by tool-description pinning
    (:func:`agentlab.mcp.security.tool_digest`).
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    digest: str
    output_schema: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class DiscoverResult:
    """What ``server/discover`` told the client."""

    server: ServerInfo
    protocol_versions: tuple[str, ...]
    capabilities: dict[str, Any] = field(default_factory=dict)
    ttl_ms: int | None = None
    cache_scope: str | None = None


@dataclass(frozen=True, slots=True)
class ResourceContents:
    """The text payload of one resource read."""

    uri: str
    mime_type: str
    text: str


class MCPClient:
    """Discover an MCP server, map its tools, and call them.

    Contract:
        - ``discover`` calls ``server/discover``, verifies the negotiated protocol
          version, applies the trust policy, and returns :class:`DiscoverResult`;
        - ``list_tools`` calls ``tools/list`` and returns :class:`RemoteTool`
          declarations carrying their security digest; when a security policy is
          configured, ``discover`` must have been called first so pins can be
          keyed by server identity;
        - ``call_tool`` sends ``tools/call`` and returns a ``ToolResult``;
          protocol/transport failures become ``ToolResult.failure`` (observations
          the model can recover from), while security refusals raise;
        - ``read_resource`` reads one resource, raising :class:`MCPError` on
          failure;
        - ``as_tool_registry`` returns a local ``ToolRegistry`` whose tools invoke
          the remote server -- the bridge into the week-2 agent loop;
        - every request includes ``params._meta`` with the protocol version and
          client identity (stateless design -- there is no handshake).
    """

    def __init__(
        self,
        transport: Transport,
        *,
        client_name: str = "agentlab-client",
        client_version: str = "0.1.0",
        protocol_version: str = PROTOCOL_VERSION,
        security: MCPClientSecurity | None = None,
    ) -> None:
        self.transport = transport
        self.client_name = client_name
        self.client_version = client_version
        self.protocol_version = protocol_version
        self.security = security
        self._next_id = 0
        self._discovered: DiscoverResult | None = None

    def _meta(self) -> dict[str, Any]:
        """Request metadata attached to every call (stateless MCP)."""
        raise NotImplementedError("Week 5 lab: implement MCPClient._meta")

    def discover(self) -> DiscoverResult:
        """Call ``server/discover`` and return the server's declaration."""
        raise NotImplementedError("Week 5 lab: implement MCPClient.discover")

    def list_tools(self) -> list[RemoteTool]:
        """List the server's tools with digests for pinning."""
        raise NotImplementedError("Week 5 lab: implement MCPClient.list_tools")

    def call_tool(self, name: str, arguments: Mapping[str, Any] | None = None) -> ToolResult:
        """Invoke one remote tool; failures become observations."""
        raise NotImplementedError("Week 5 lab: implement MCPClient.call_tool")

    def read_resource(self, uri: str) -> ResourceContents:
        """Read one resource by URI."""
        raise NotImplementedError("Week 5 lab: implement MCPClient.read_resource")

    def as_tool_registry(self) -> ToolRegistry:
        """Map every discovered tool into a local ``ToolRegistry``."""
        raise NotImplementedError("Week 5 lab: implement MCPClient.as_tool_registry")
