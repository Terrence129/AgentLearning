"""Tests for the MCP server (discovery, tools, resources) (week 5 lab)."""

from __future__ import annotations

import pytest
from agentlab.mcp.jsonrpc import (
    INVALID_PARAMS,
    META_PROTOCOL_VERSION,
    META_SERVER_INFO,
    METHOD_NOT_FOUND,
    RESULT_TYPE_COMPLETE,
    UNSUPPORTED_PROTOCOL_VERSION,
)
from agentlab.mcp.server import MCPServer, build_demo_server
from agentlab.mcp.transport import PROTOCOL_VERSION

pytestmark = pytest.mark.week


def request(
    method: str,
    params: dict | None = None,
    *,
    request_id: int = 1,
    version: str = PROTOCOL_VERSION,
    include_meta: bool = True,
) -> dict:
    payload = dict(params or {})
    if include_meta:
        payload["_meta"] = {META_PROTOCOL_VERSION: version}
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": payload}


def tool_call(name: str, arguments: dict | None = None) -> dict:
    return request("tools/call", {"name": name, "arguments": arguments or {}})


def make_echo_server() -> MCPServer:
    server = MCPServer(name="echo", version="2.0.0")

    def echo(arguments: dict) -> dict:
        return {"echo": arguments.get("text", "")}

    server.register_tool(
        "echo",
        "Echo the provided text back",
        {"type": "object", "properties": {"text": {"type": "string"}}},
        echo,
    )
    server.register_tool(
        "ping_tool",
        "Return pong",
        {"type": "object", "properties": {}},
        lambda arguments: {"pong": True},
    )
    return server


def test_demo_server_exposes_three_tools_and_one_resource() -> None:
    server = build_demo_server()

    assert server.tool_names() == [
        "check_refund_eligibility",
        "convert_currency",
        "search_knowledge",
    ]
    assert server.resource_uris() == ["policy://refund"]


def test_discover_reports_versions_identity_capabilities_and_caching() -> None:
    server = MCPServer(name="demo", version="1.2.3", instructions="Use the tools.")
    response = server.handle(request("server/discover"))
    assert response is not None
    result = response["result"]

    assert result["resultType"] == RESULT_TYPE_COMPLETE
    assert result["protocolVersions"] == [PROTOCOL_VERSION]
    assert result["serverInfo"] == {"name": "demo", "version": "1.2.3"}
    assert set(result["capabilities"]) >= {"tools", "resources"}
    assert isinstance(result["ttlMs"], int) and result["ttlMs"] > 0
    assert result["cacheScope"] in {"public", "private"}
    assert result["_meta"][META_SERVER_INFO] == {"name": "demo", "version": "1.2.3"}


def test_requests_without_protocol_meta_are_invalid_params() -> None:
    server = make_echo_server()
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    assert response is not None
    assert response["error"]["code"] == INVALID_PARAMS
    assert "protocolVersion" in response["error"]["message"]


def test_unsupported_protocol_version_returns_32022_with_supported_list() -> None:
    server = make_echo_server()
    response = server.handle(request("tools/list", version="1900-01-01"))
    assert response is not None

    error = response["error"]
    assert error["code"] == UNSUPPORTED_PROTOCOL_VERSION == -32022
    assert error["data"]["requested"] == "1900-01-01"
    assert PROTOCOL_VERSION in error["data"]["supported"]


def test_tools_list_is_deterministic_sorted_and_cacheable() -> None:
    server = MCPServer(name="listing", version="1.0.0")

    def noop(arguments: dict) -> str:
        return "ok"

    server.register_tool("zeta", "Last tool", {"type": "object"}, noop)
    server.register_tool("alpha", "First tool", {"type": "object"}, noop)

    first = server.handle(request("tools/list"))
    second = server.handle(request("tools/list"))
    assert first is not None and second is not None
    result = first["result"]

    assert [tool["name"] for tool in result["tools"]] == ["alpha", "zeta"]
    assert result["tools"][0]["description"] == "First tool"
    assert result["tools"][0]["inputSchema"] == {"type": "object"}
    assert isinstance(result["ttlMs"], int)
    assert result["cacheScope"] == "private"
    assert first["result"] == second["result"]


def test_tools_call_executes_the_tool_and_returns_text_and_structured_content() -> None:
    server = build_demo_server()
    response = server.handle(tool_call("search_knowledge", {"query": "refund"}))
    assert response is not None
    result = response["result"]

    assert result["resultType"] == RESULT_TYPE_COMPLETE
    assert result["isError"] is False
    assert result["content"][0]["type"] == "text"
    assert "refund" in result["content"][0]["text"].lower()
    assert isinstance(result["structuredContent"], dict)


def test_tools_call_unknown_tool_is_a_protocol_error() -> None:
    server = build_demo_server()
    response = server.handle(tool_call("delete_everything"))
    assert response is not None
    assert response["error"]["code"] == INVALID_PARAMS
    assert "delete_everything" in response["error"]["message"]


def test_tools_call_missing_name_is_a_protocol_error() -> None:
    server = build_demo_server()
    response = server.handle(request("tools/call", {"arguments": {}}))
    assert response is not None
    assert response["error"]["code"] == INVALID_PARAMS


def test_tool_exception_becomes_an_iserror_result_not_a_crash() -> None:
    server = MCPServer(name="boom", version="1.0.0")

    def explode(arguments: dict) -> str:
        raise RuntimeError("boom")

    server.register_tool("explode", "Always fails", {"type": "object"}, explode)
    response = server.handle(tool_call("explode"))
    assert response is not None

    assert "error" not in response
    result = response["result"]
    assert result["isError"] is True
    assert "RuntimeError" in result["content"][0]["text"]


def test_resources_list_and_read_return_expected_shapes() -> None:
    server = build_demo_server()

    listing = server.handle(request("resources/list"))
    assert listing is not None
    resource = listing["result"]["resources"][0]
    assert resource["uri"] == "policy://refund"
    assert resource["name"]
    assert resource["mimeType"] == "text/plain"

    read = server.handle(request("resources/read", {"uri": "policy://refund"}))
    assert read is not None
    contents = read["result"]["contents"][0]
    assert contents["uri"] == "policy://refund"
    assert contents["mimeType"] == "text/plain"
    assert "30 days" in contents["text"]


def test_unknown_resource_uri_is_invalid_params_not_32002() -> None:
    server = build_demo_server()
    response = server.handle(request("resources/read", {"uri": "policy://missing"}))
    assert response is not None
    assert response["error"]["code"] == INVALID_PARAMS == -32602


def test_unknown_method_returns_method_not_found() -> None:
    server = make_echo_server()
    response = server.handle(request("tools/delete"))
    assert response is not None
    assert response["error"]["code"] == METHOD_NOT_FOUND


def test_notifications_are_never_answered() -> None:
    server = make_echo_server()
    notification = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {"_meta": {META_PROTOCOL_VERSION: PROTOCOL_VERSION}},
    }
    assert server.handle(notification) is None
