"""MCP server: discovery, tools and resources (week 5).

Why this module exists
----------------------
An MCP server is a small, well-defined host for capability: it advertises what
it can do and executes requests. The 2026-07-28 revision made it *stateless*
(docs/research/01-agent-architecture-sota.md §10): there is no ``initialize``
handshake and no protocol session, so every request must carry its protocol
version and client identity in ``params._meta``, and servers MUST implement
``server/discover`` so clients can learn supported versions, capabilities and
identity up front. All results carry a required ``resultType`` field, list/read
results carry ``ttlMs`` and ``cacheScope`` caching hints, and ``tools/list``
should be deterministically ordered so prompt caches actually hit.

This lab implements a documented subset: ``server/discover``, ``tools/list``,
``tools/call``, ``resources/list`` and ``resources/read``. Prompts, MRTR
(``input_required``), subscriptions and OAuth are out of scope -- see
labs/week05-mcp/README.md for the exact divergence list.

What breaks without it
----------------------
- The server exposes tools with descriptions that do not match what it runs, so
  the model asks for the wrong thing (tool/implementation drift).
- A version mismatch produces a random downstream failure instead of
  ``UnsupportedProtocolVersionError`` with the supported list.
- A tool exception kills the session instead of becoming an ``isError`` result
  the client can reason about.
- Listings shuffle between calls, defeating client caching and making tests (and
  prompt caching) unreliable.

Read first: docs/research/02-frameworks-protocols.md §1.1 and the MCP tools /
resources spec pages.

Public surface
--------------
``MCPTool``          name + description + JSON Schema + handler
``MCPResource``      uri + name + mime type + reader
``MCPServer``        registry + JSON-RPC dispatcher
``build_demo_server`` three tools and one resource, deterministic and offline
``main``             run the demo server over stdio (``python -m agentlab.mcp.server``)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from agentlab.mcp.transport import PROTOCOL_VERSION

#: A tool handler receives the JSON arguments object and returns any JSON-able
#: value. Raising is allowed: the server converts it into a tool-level error
#: result (``isError: true``) rather than a protocol error.
ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True, slots=True)
class MCPTool:
    """One capability advertised to clients.

    ``input_schema`` is a JSON Schema object (2020-12 by default per the spec).
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler


@dataclass(frozen=True, slots=True)
class MCPResource:
    """One readable resource: a stable URI plus a reader.

    Resources are application-controlled (the client decides when to read);
    tools are model-controlled. That distinction is the main design question
    when exposing data over MCP.
    """

    uri: str
    name: str
    mime_type: str
    reader: Callable[[], str]


class MCPServer:
    """A stateless MCP server over a JSON-RPC message in / response out API.

    Dispatch contract (``handle``):
        - validate the request has ``params._meta[protocolVersion]``; missing ->
          ``InvalidParams`` (-32602); unsupported -> ``UnsupportedProtocolVersion``
          (-32022) whose ``data`` is ``{"supported": [...], "requested": ...}``;
        - ``server/discover`` returns supported versions, server identity,
          capabilities and caching hints;
        - ``tools/list`` returns tools sorted by name;
        - ``tools/call`` executes one tool; unknown tool or missing name is a
          protocol ``InvalidParams`` error; a handler exception becomes a
          successful JSON-RPC result with ``isError: true``;
        - ``resources/list`` returns resources sorted by URI;
        - ``resources/read`` returns the resource text; unknown URI is
          ``InvalidParams`` (-32602, NOT the old -32002 -- the 2026 revision
          aligned resource-not-found with the JSON-RPC spec);
        - an unknown method returns ``MethodNotFound`` (-32601);
        - notifications (no ``id``) return ``None`` and are never answered;
        - every result includes ``resultType: "complete"`` and
          ``_meta[serverInfo]``.
    """

    def __init__(
        self,
        *,
        name: str = "agentlab-demo",
        version: str = "0.1.0",
        instructions: str | None = None,
        supported_protocol_versions: tuple[str, ...] = (PROTOCOL_VERSION,),
    ) -> None:
        self.name = name
        self.version = version
        self.instructions = instructions
        self.supported_protocol_versions = tuple(supported_protocol_versions)
        self._tools: dict[str, MCPTool] = {}
        self._resources: dict[str, MCPResource] = {}

    # -- registration ------------------------------------------------------

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: ToolHandler,
    ) -> MCPTool:
        """Register a tool.

        Raises:
            ValueError: if ``name`` is blank or already registered.
        """
        raise NotImplementedError("Week 5 lab: implement MCPServer.register_tool")

    def register_resource(
        self,
        uri: str,
        name: str,
        mime_type: str,
        reader: Callable[[], str],
    ) -> MCPResource:
        """Register a resource.

        Raises:
            ValueError: if ``uri`` is blank or already registered.
        """
        raise NotImplementedError("Week 5 lab: implement MCPServer.register_resource")

    def tool_names(self) -> list[str]:
        """Registered tool names, sorted."""
        raise NotImplementedError("Week 5 lab: implement MCPServer.tool_names")

    def resource_uris(self) -> list[str]:
        """Registered resource URIs, sorted."""
        raise NotImplementedError("Week 5 lab: implement MCPServer.resource_uris")

    # -- dispatch ----------------------------------------------------------

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Handle one decoded JSON-RPC message; return a response or ``None``."""
        raise NotImplementedError("Week 5 lab: implement MCPServer.handle")


def build_demo_server() -> MCPServer:
    """Build the demo server: 3 tools + 1 resource, deterministic and offline.

    Tools (all read-only, no network):
        - ``search_knowledge(query)`` -- substring search over a tiny knowledge base
        - ``convert_currency(amount, from_currency, to_currency)`` -- fixed rates
        - ``check_refund_eligibility(days_since_purchase, amount_usd)`` --
          deterministic policy check
    Resource:
        - ``policy://refund`` -- the refund policy text (``text/plain``)
    """
    raise NotImplementedError("Week 5 lab: implement build_demo_server")


def main() -> int:
    """Run the demo server over stdio (``python -m agentlab.mcp.server``).

    This is the deliverable entry point; tests exercise the same server through
    an in-memory or StringIO transport instead of spawning a process.
    """
    raise NotImplementedError("Week 5 lab: implement main")


if __name__ == "__main__":
    raise SystemExit(main())
