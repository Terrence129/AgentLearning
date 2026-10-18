"""MCP client: discover, map remote tools into a ToolRegistry, invoke (week 5).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from agentlab.errors import AgentError, ToolError
from agentlab.mcp.jsonrpc import (
    JSONRPC_VERSION,
    META_CLIENT_CAPABILITIES,
    META_CLIENT_INFO,
    META_PROTOCOL_VERSION,
    RESULT_TYPE_COMPLETE,
    RESULT_TYPE_INPUT_REQUIRED,
    UNSUPPORTED_PROTOCOL_VERSION,
    make_request,
)
from agentlab.mcp.security import MCPClientSecurity, tool_digest
from agentlab.mcp.transport import (
    PROTOCOL_VERSION,
    Transport,
    TransportClosed,
    TransportTimeout,
)
from agentlab.tools.registry import Tool, ToolRegistry, ToolResult


class MCPError(AgentError):
    """A protocol or transport failure while talking to an MCP server."""

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
    """One discovered tool with its security digest."""

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
    """Discover an MCP server, map its tools, and call them."""

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

    # -- wire layer --------------------------------------------------------

    def _next_request_id(self) -> int:
        self._next_id += 1
        return self._next_id

    def _meta(self) -> dict[str, Any]:
        return {
            META_PROTOCOL_VERSION: self.protocol_version,
            META_CLIENT_INFO: {"name": self.client_name, "version": self.client_version},
            META_CLIENT_CAPABILITIES: {},
        }

    def _request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = self._next_request_id()
        message = make_request(request_id, method, params, meta=self._meta())
        try:
            response = self.transport.send(message)
        except TransportTimeout as exc:
            raise MCPError(f"{method} timed out waiting for the server: {exc}") from exc
        except TransportClosed as exc:
            raise MCPError(f"transport closed during {method}: {exc}") from exc
        if response is None:
            raise MCPError(f"no response for {method} request {request_id}")
        if response.get("jsonrpc") != JSONRPC_VERSION:
            raise MCPError(f"response to {method} is not JSON-RPC 2.0")
        if response.get("id") != request_id:
            raise MCPError(f"response id {response.get('id')!r} does not match request id {request_id!r}")
        if "error" in response:
            error = response.get("error") or {}
            raise MCPError(
                str(error.get("message", f"{method} failed")),
                code=error.get("code"),
                data=error.get("data"),
            )
        result = response.get("result")
        if not isinstance(result, dict):
            raise MCPError(f"response to {method} has no result object")
        result_type = result.get("resultType", RESULT_TYPE_COMPLETE)
        if result_type == RESULT_TYPE_INPUT_REQUIRED:
            raise MCPError(
                "server returned resultType='input_required' (Multi Round-Trip Request); "
                "MRTR is not implemented in this lab subset"
            )
        if result_type != RESULT_TYPE_COMPLETE:
            raise MCPError(f"unknown resultType {result_type!r} in response to {method}")
        return result

    # -- public operations -------------------------------------------------

    def discover(self) -> DiscoverResult:
        result = self._request("server/discover")
        server_info = result.get("serverInfo")
        if not isinstance(server_info, dict) or not server_info.get("name"):
            raise MCPError("server/discover result is missing the required serverInfo object")
        server = ServerInfo(name=str(server_info["name"]), version=str(server_info.get("version", "")))
        versions = tuple(str(version) for version in result.get("protocolVersions") or ())
        if versions and self.protocol_version not in versions:
            raise MCPError(
                f"server does not support protocol version {self.protocol_version!r}; "
                f"supported: {list(versions)}",
                code=UNSUPPORTED_PROTOCOL_VERSION,
            )
        if self.security is not None:
            self.security.check_server(server.name)
        discovered = DiscoverResult(
            server=server,
            protocol_versions=versions,
            capabilities=dict(result.get("capabilities") or {}),
            ttl_ms=result.get("ttlMs"),
            cache_scope=result.get("cacheScope"),
        )
        self._discovered = discovered
        return discovered

    def list_tools(self) -> list[RemoteTool]:
        if self.security is not None and self.security.pins is not None and self._discovered is None:
            raise MCPError(
                "discover() must be called before list_tools() when pinning is configured: "
                "tool pins are keyed by server identity"
            )
        result = self._request("tools/list")
        raw_tools = result.get("tools") or []
        tools: list[RemoteTool] = []
        for raw in raw_tools:
            if not isinstance(raw, dict) or not raw.get("name"):
                raise MCPError("tools/list returned a tool declaration without a name")
            tool = RemoteTool(
                name=str(raw["name"]),
                description=str(raw.get("description", "")),
                input_schema=dict(raw.get("inputSchema") or {}),
                digest="",
                output_schema=raw.get("outputSchema"),
            )
            tools.append(replace(tool, digest=tool_digest(tool)))
        if self.security is not None:
            server_name = self._discovered.server.name if self._discovered is not None else ""
            self.security.check_tools(server_name, tools)
        return tools

    def call_tool(self, name: str, arguments: Mapping[str, Any] | None = None) -> ToolResult:
        arguments_payload = dict(arguments or {})
        if self.security is not None:
            self.security.check_call(name, arguments_payload)
        try:
            result = self._request("tools/call", {"name": name, "arguments": arguments_payload})
        except MCPError as exc:
            return ToolResult.failure(f"MCP tool call failed: {exc}")
        blocks = result.get("content") or []
        texts = [
            str(block.get("text", ""))
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        text = "\n".join(texts)
        if result.get("isError"):
            return ToolResult.failure(text or f"remote tool {name!r} returned an error")
        meta: dict[str, Any] = {}
        if isinstance(result.get("structuredContent"), dict):
            meta["structuredContent"] = result["structuredContent"]
        return ToolResult(ok=True, output=text, meta=meta)

    def read_resource(self, uri: str) -> ResourceContents:
        result = self._request("resources/read", {"uri": uri})
        contents = result.get("contents") or []
        if not contents:
            raise MCPError(f"resources/read returned no contents for {uri!r}")
        first = contents[0]
        if not isinstance(first, dict):
            raise MCPError(f"resources/read returned malformed contents for {uri!r}")
        return ResourceContents(
            uri=str(first.get("uri", uri)),
            mime_type=str(first.get("mimeType", "text/plain")),
            text=str(first.get("text", "")),
        )

    def as_tool_registry(self) -> ToolRegistry:
        registry = ToolRegistry()
        for remote in self.list_tools():

            def handler(arguments: dict[str, Any], _name: str = remote.name) -> str:
                result = self.call_tool(_name, arguments)
                if not result.ok:
                    raise ToolError(result.error or f"remote tool {_name!r} failed")
                return result.output

            registry.register(
                Tool(
                    name=remote.name,
                    description=remote.description,
                    parameters=remote.input_schema,
                    handler=handler,
                )
            )
        return registry
