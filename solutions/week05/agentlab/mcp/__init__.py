"""Model Context Protocol, built from scratch (week 5).

MCP is the interoperability layer: instead of writing a bespoke integration for
every system, you expose/consume a standard one. The lab builds both sides of
the **2026-07-28 stateless revision** so the protocol stops being magic. There
is no dependency on the official ``mcp`` package.

Modules:
    jsonrpc.py    JSON-RPC 2.0 framing, error codes, MCP ``_meta`` metadata
    transport.py  in-memory transport and newline-delimited stdio framing
    server.py     discovery, tools and resources, plus the demo server
    client.py     discover -> map into ToolRegistry -> invoke
    security.py   trust list, tool-description digest pinning, token policy
"""

from __future__ import annotations

from agentlab.mcp.client import (
    DiscoverResult,
    MCPClient,
    MCPError,
    RemoteTool,
    ResourceContents,
    ServerInfo,
)
from agentlab.mcp.jsonrpc import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    JSONRPC_VERSION,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    RESULT_TYPE_COMPLETE,
    RESULT_TYPE_INPUT_REQUIRED,
    UNSUPPORTED_PROTOCOL_VERSION,
    JSONRPCError,
    is_notification,
    make_error,
    make_notification,
    make_request,
    make_result,
    parse_message,
)
from agentlab.mcp.security import (
    MCPClientSecurity,
    SecurityPolicyError,
    ServerTrustPolicy,
    TokenPassthroughBlocked,
    TokenPassthroughPolicy,
    ToolNotAllowedError,
    ToolPinStore,
    ToolPoisoningError,
    UntrustedServerError,
    tool_digest,
)
from agentlab.mcp.server import MCPResource, MCPServer, MCPTool, build_demo_server
from agentlab.mcp.transport import (
    PROTOCOL_VERSION,
    InMemoryTransport,
    StdioServerTransport,
    Transport,
    TransportClosed,
    TransportError,
    TransportTimeout,
    decode_line,
    encode_line,
    serve_stdio,
)

__all__ = [
    "INTERNAL_ERROR",
    "INVALID_PARAMS",
    "INVALID_REQUEST",
    "JSONRPC_VERSION",
    "METHOD_NOT_FOUND",
    "PARSE_ERROR",
    "PROTOCOL_VERSION",
    "RESULT_TYPE_COMPLETE",
    "RESULT_TYPE_INPUT_REQUIRED",
    "UNSUPPORTED_PROTOCOL_VERSION",
    "DiscoverResult",
    "InMemoryTransport",
    "JSONRPCError",
    "MCPClient",
    "MCPClientSecurity",
    "MCPError",
    "MCPResource",
    "MCPServer",
    "MCPTool",
    "RemoteTool",
    "ResourceContents",
    "SecurityPolicyError",
    "ServerInfo",
    "ServerTrustPolicy",
    "StdioServerTransport",
    "TokenPassthroughBlocked",
    "TokenPassthroughPolicy",
    "ToolNotAllowedError",
    "ToolPinStore",
    "ToolPoisoningError",
    "Transport",
    "TransportClosed",
    "TransportError",
    "TransportTimeout",
    "UntrustedServerError",
    "build_demo_server",
    "decode_line",
    "encode_line",
    "is_notification",
    "make_error",
    "make_notification",
    "make_request",
    "make_result",
    "parse_message",
    "serve_stdio",
    "tool_digest",
]
