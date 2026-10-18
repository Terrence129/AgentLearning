"""MCP server: discovery, tools and resources (week 5).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from agentlab.mcp.jsonrpc import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    META_PROTOCOL_VERSION,
    META_SERVER_INFO,
    METHOD_NOT_FOUND,
    RESULT_TYPE_COMPLETE,
    UNSUPPORTED_PROTOCOL_VERSION,
    JSONRPCError,
    is_notification,
    make_error,
    make_result,
)
from agentlab.mcp.transport import PROTOCOL_VERSION, serve_stdio

ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True, slots=True)
class MCPTool:
    """One capability advertised to clients."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler


@dataclass(frozen=True, slots=True)
class MCPResource:
    """One readable resource: a stable URI plus a reader."""

    uri: str
    name: str
    mime_type: str
    reader: Callable[[], str]


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


class MCPServer:
    """A stateless MCP server over a JSON-RPC message in / response out API."""

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
        if not name.strip():
            raise ValueError("tool name must not be blank")
        if name in self._tools:
            raise ValueError(f"tool {name!r} is already registered")
        tool = MCPTool(
            name=name,
            description=description,
            input_schema=dict(input_schema),
            handler=handler,
        )
        self._tools[name] = tool
        return tool

    def register_resource(
        self,
        uri: str,
        name: str,
        mime_type: str,
        reader: Callable[[], str],
    ) -> MCPResource:
        if not uri.strip():
            raise ValueError("resource uri must not be blank")
        if uri in self._resources:
            raise ValueError(f"resource {uri!r} is already registered")
        resource = MCPResource(uri=uri, name=name, mime_type=mime_type, reader=reader)
        self._resources[uri] = resource
        return resource

    def tool_names(self) -> list[str]:
        return sorted(self._tools)

    def resource_uris(self) -> list[str]:
        return sorted(self._resources)

    # -- dispatch ----------------------------------------------------------

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return make_error(None, INVALID_REQUEST, "message must be a JSON-RPC 2.0 object")
        request_id = message.get("id")
        method = message.get("method")
        if not isinstance(method, str):
            return make_error(request_id, INVALID_REQUEST, "request must include a string method")
        try:
            params = message.get("params") or {}
            if not isinstance(params, dict):
                raise JSONRPCError(INVALID_PARAMS, "params must be an object")
            self._check_protocol(params)
            if method == "server/discover":
                result = self._discover()
            elif method == "tools/list":
                result = self._tools_list()
            elif method == "tools/call":
                result = self._tools_call(params)
            elif method == "resources/list":
                result = self._resources_list()
            elif method == "resources/read":
                result = self._resources_read(params)
            else:
                raise JSONRPCError(METHOD_NOT_FOUND, f"unknown method {method!r}")
        except JSONRPCError as exc:
            if is_notification(message):
                return None
            return make_error(request_id, exc.code, exc.message, exc.data)
        if is_notification(message):
            return None
        return make_result(request_id, result)

    # -- internals ---------------------------------------------------------

    def _server_meta(self) -> dict[str, Any]:
        return {META_SERVER_INFO: {"name": self.name, "version": self.version}}

    def _check_protocol(self, params: dict[str, Any]) -> None:
        meta = params.get("_meta")
        if not isinstance(meta, dict):
            raise JSONRPCError(
                INVALID_PARAMS,
                "request params._meta must be an object carrying "
                f"{META_PROTOCOL_VERSION!r} (MCP 2026-07-28 is stateless)",
            )
        version = meta.get(META_PROTOCOL_VERSION)
        if not isinstance(version, str) or not version:
            raise JSONRPCError(
                INVALID_PARAMS,
                f"request params._meta must include {META_PROTOCOL_VERSION!r}",
            )
        if version not in self.supported_protocol_versions:
            raise JSONRPCError(
                UNSUPPORTED_PROTOCOL_VERSION,
                "Unsupported protocol version",
                {"supported": list(self.supported_protocol_versions), "requested": version},
            )

    def _discover(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "resultType": RESULT_TYPE_COMPLETE,
            "protocolVersions": list(self.supported_protocol_versions),
            "serverInfo": {"name": self.name, "version": self.version},
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False},
            },
            "ttlMs": 300_000,
            "cacheScope": "public",
            "_meta": self._server_meta(),
        }
        if self.instructions:
            result["instructions"] = self.instructions
        return result

    def _tools_list(self) -> dict[str, Any]:
        tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in sorted(self._tools.values(), key=lambda tool: tool.name)
        ]
        return {
            "resultType": RESULT_TYPE_COMPLETE,
            "tools": tools,
            "ttlMs": 60_000,
            "cacheScope": "private",
            "_meta": self._server_meta(),
        }

    def _tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        if not isinstance(name, str) or not name:
            raise JSONRPCError(INVALID_PARAMS, "tools/call requires a non-empty tool 'name'")
        tool = self._tools.get(name)
        if tool is None:
            raise JSONRPCError(
                INVALID_PARAMS,
                f"unknown tool {name!r}; available tools: {', '.join(self.tool_names()) or 'none'}",
            )
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            raise JSONRPCError(INVALID_PARAMS, "tools/call 'arguments' must be an object")
        try:
            output = tool.handler(arguments)
        except Exception as exc:  # tool bugs are results, not protocol failures
            return {
                "resultType": RESULT_TYPE_COMPLETE,
                "content": [
                    {"type": "text", "text": f"ERROR: tool {name!r} raised {type(exc).__name__}: {exc}"}
                ],
                "isError": True,
                "_meta": self._server_meta(),
            }
        result: dict[str, Any] = {
            "resultType": RESULT_TYPE_COMPLETE,
            "content": [{"type": "text", "text": _stringify(output)}],
            "isError": False,
            "_meta": self._server_meta(),
        }
        if isinstance(output, dict):
            result["structuredContent"] = output
        return result

    def _resources_list(self) -> dict[str, Any]:
        resources = [
            {"uri": resource.uri, "name": resource.name, "mimeType": resource.mime_type}
            for resource in sorted(self._resources.values(), key=lambda resource: resource.uri)
        ]
        return {
            "resultType": RESULT_TYPE_COMPLETE,
            "resources": resources,
            "ttlMs": 60_000,
            "cacheScope": "private",
            "_meta": self._server_meta(),
        }

    def _resources_read(self, params: dict[str, Any]) -> dict[str, Any]:
        uri = params.get("uri")
        if not isinstance(uri, str) or not uri:
            raise JSONRPCError(INVALID_PARAMS, "resources/read requires a non-empty 'uri'")
        resource = self._resources.get(uri)
        if resource is None:
            # 2026-07-28 aligned resource-not-found with JSON-RPC InvalidParams
            # (-32602); the old -32002 code is gone.
            raise JSONRPCError(
                INVALID_PARAMS,
                f"unknown resource {uri!r}; available resources: {', '.join(self.resource_uris()) or 'none'}",
            )
        try:
            text = resource.reader()
        except Exception as exc:
            raise JSONRPCError(
                INTERNAL_ERROR, f"resource {uri!r} reader failed: {type(exc).__name__}: {exc}"
            ) from exc
        return {
            "resultType": RESULT_TYPE_COMPLETE,
            "contents": [{"uri": resource.uri, "mimeType": resource.mime_type, "text": text}],
            "ttlMs": 60_000,
            "cacheScope": "private",
            "_meta": self._server_meta(),
        }


# -- demo server -------------------------------------------------------------

_KNOWLEDGE_BASE = (
    {
        "id": "kb-1",
        "title": "Refund policy",
        "text": "Refunds are available within 30 days of purchase for annual enterprise contracts.",
    },
    {
        "id": "kb-2",
        "title": "Discount policy",
        "text": "The maximum discount for enterprise deals is 10 percent without approval.",
    },
    {
        "id": "kb-3",
        "title": "Shipping",
        "text": "Shipping times depend on the destination country.",
    },
)

_FX_RATES = {
    ("USD", "SGD"): 1.35,
    ("SGD", "USD"): 1 / 1.35,
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1 / 0.92,
}


def build_demo_server() -> MCPServer:
    """Build the demo server: 3 tools + 1 resource, deterministic and offline."""

    def search_knowledge(arguments: dict[str, Any]) -> dict[str, Any]:
        query = str(arguments.get("query", "")).strip().lower()
        if query:
            results = [
                doc
                for doc in _KNOWLEDGE_BASE
                if query in doc["title"].lower() or query in doc["text"].lower()
            ]
        else:
            results = list(_KNOWLEDGE_BASE)
        return {"query": query, "results": results}

    def convert_currency(arguments: dict[str, Any]) -> dict[str, Any]:
        amount = float(arguments.get("amount", 0.0))
        from_currency = str(arguments.get("from_currency", "")).upper()
        to_currency = str(arguments.get("to_currency", "")).upper()
        rate = _FX_RATES.get((from_currency, to_currency))
        if rate is None:
            raise ValueError(f"unsupported currency pair {from_currency}->{to_currency}")
        return {
            "amount": round(amount * rate, 2),
            "from": from_currency,
            "to": to_currency,
            "rate": rate,
        }

    def check_refund_eligibility(arguments: dict[str, Any]) -> dict[str, Any]:
        days = int(arguments.get("days_since_purchase", 0))
        amount = float(arguments.get("amount_usd", 0.0))
        eligible = days <= 30 and amount <= 500.0
        return {
            "eligible": eligible,
            "reason": (
                "within the 30-day window and under the $500 cap"
                if eligible
                else "outside the 30-day window or above the $500 cap"
            ),
        }

    server = MCPServer(
        name="agentlab-demo",
        version="0.1.0",
        instructions="Read-only policy knowledge base. Prefer search_knowledge before answering.",
    )
    server.register_tool(
        "search_knowledge",
        "Search the internal knowledge base for policy documents matching a query.",
        {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Substring to search for"}},
            "required": ["query"],
        },
        search_knowledge,
    )
    server.register_tool(
        "convert_currency",
        "Convert an amount between two fixed currencies.",
        {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string", "description": "ISO currency code"},
                "to_currency": {"type": "string", "description": "ISO currency code"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
        convert_currency,
    )
    server.register_tool(
        "check_refund_eligibility",
        "Check whether a purchase is inside the refund window and amount cap.",
        {
            "type": "object",
            "properties": {
                "days_since_purchase": {"type": "integer"},
                "amount_usd": {"type": "number"},
            },
            "required": ["days_since_purchase", "amount_usd"],
        },
        check_refund_eligibility,
    )
    server.register_resource(
        "policy://refund",
        "Refund policy",
        "text/plain",
        lambda: (
            "Refunds are available within 30 days of purchase for annual enterprise contracts. "
            "The maximum discount for enterprise deals is 10 percent without approval."
        ),
    )
    return server


def main() -> int:
    """Run the demo server over stdio (``python -m agentlab.mcp.server``)."""
    server = build_demo_server()
    try:
        serve_stdio(server.handle, sys.stdin, sys.stdout)
    except KeyboardInterrupt:  # pragma: no cover - interactive shutdown
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
