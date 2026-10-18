"""Tests for the MCP client: discovery, registry mapping, failures (week 5 lab)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from agentlab.mcp.client import MCPClient, MCPError
from agentlab.mcp.jsonrpc import (
    INVALID_PARAMS,
    META_CLIENT_CAPABILITIES,
    META_CLIENT_INFO,
    META_PROTOCOL_VERSION,
)
from agentlab.mcp.server import MCPServer, build_demo_server
from agentlab.mcp.transport import (
    PROTOCOL_VERSION,
    InMemoryTransport,
    TransportTimeout,
)

pytestmark = pytest.mark.week


class TimeoutTransport:
    """A transport whose deadline always expires."""

    def send(self, message: dict) -> dict | None:
        raise TransportTimeout("deadline exceeded while waiting for the server")


class NoResponseTransport:
    """A transport that swallows notifications and returns nothing for requests."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, message: dict) -> dict | None:
        self.sent.append(message)
        return None


class WrongIdTransport:
    """Responds, but with an id that does not match the request."""

    def send(self, message: dict) -> dict:
        return {"jsonrpc": "2.0", "id": "someone-else", "result": {"resultType": "complete"}}


class FixedResultTransport:
    """Always answers with one fixed result payload."""

    def __init__(self, result: dict) -> None:
        self.result = result
        self.sent: list[dict] = []

    def send(self, message: dict) -> dict:
        self.sent.append(message)
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": self.result}


def make_client_with_demo_server() -> tuple[MCPClient, InMemoryTransport]:
    server = build_demo_server()
    transport = InMemoryTransport(server.handle)
    return MCPClient(transport), transport


def test_discover_parses_identity_versions_and_capabilities() -> None:
    client, transport = make_client_with_demo_server()

    discovery = client.discover()

    assert discovery.server.name == "agentlab-demo"
    assert discovery.server.version
    assert PROTOCOL_VERSION in discovery.protocol_versions
    assert "tools" in discovery.capabilities
    assert isinstance(discovery.ttl_ms, int)
    assert transport.sent[0]["method"] == "server/discover"


def test_every_request_carries_stateless_protocol_metadata() -> None:
    client, transport = make_client_with_demo_server()
    client.discover()
    client.list_tools()

    assert len(transport.sent) == 2
    for message in transport.sent:
        meta = message["params"]["_meta"]
        assert meta[META_PROTOCOL_VERSION] == PROTOCOL_VERSION
        assert meta[META_CLIENT_INFO]["name"] == "agentlab-client"
        assert meta[META_CLIENT_INFO]["version"]
        assert meta[META_CLIENT_CAPABILITIES] == {}
        assert "_meta" not in message


def test_list_tools_returns_declarations_and_security_digests() -> None:
    client, _ = make_client_with_demo_server()

    tools = client.list_tools()

    assert [tool.name for tool in tools] == [
        "check_refund_eligibility",
        "convert_currency",
        "search_knowledge",
    ]
    for tool in tools:
        assert len(tool.digest) == 64
        assert tool.input_schema["type"] == "object"
        assert tool.description


def test_call_tool_returns_a_success_result_with_structured_content() -> None:
    client, _ = make_client_with_demo_server()

    result = client.call_tool("search_knowledge", {"query": "refund"})

    assert result.ok
    assert "refund" in result.output.lower()
    assert isinstance(result.meta.get("structuredContent"), dict)


def test_call_tool_unknown_tool_becomes_an_observation() -> None:
    client, _ = make_client_with_demo_server()

    result = client.call_tool("delete_everything", {})

    assert not result.ok
    assert "unknown tool" in (result.error or "").lower()


def test_call_tool_timeout_becomes_an_observation() -> None:
    client = MCPClient(TimeoutTransport())

    result = client.call_tool("search_knowledge", {"query": "refund"})

    assert not result.ok
    assert "timed out" in (result.error or "").lower()


def test_discover_timeout_raises_mcp_error() -> None:
    client = MCPClient(TimeoutTransport())
    with pytest.raises(MCPError, match="timed out"):
        client.discover()


def test_missing_response_is_an_mcp_error() -> None:
    client = MCPClient(NoResponseTransport())
    with pytest.raises(MCPError, match="no response"):
        client.discover()


def test_mismatched_response_id_is_an_mcp_error() -> None:
    client = MCPClient(WrongIdTransport())
    with pytest.raises(MCPError, match="id"):
        client.discover()


def test_malformed_discover_result_is_an_mcp_error() -> None:
    transport = FixedResultTransport({"resultType": "complete"})
    client = MCPClient(transport)
    # A result that is missing the required serverInfo is a protocol error, not a crash.
    with pytest.raises(MCPError, match="serverInfo"):
        client.discover()


def test_input_required_result_is_rejected_as_unsupported() -> None:
    client = MCPClient(FixedResultTransport({"resultType": "input_required", "inputRequests": []}))
    with pytest.raises(MCPError, match="input_required"):
        client.discover()


def test_protocol_error_response_raises_mcp_error_with_code() -> None:
    class ErrorTransport:
        def send(self, message: dict) -> dict:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {"code": INVALID_PARAMS, "message": "bad arguments"},
            }

    client = MCPClient(ErrorTransport())
    with pytest.raises(MCPError) as caught:
        client.discover()
    assert caught.value.code == INVALID_PARAMS
    assert "bad arguments" in str(caught.value)


def test_read_resource_returns_contents() -> None:
    client, _ = make_client_with_demo_server()

    contents = client.read_resource("policy://refund")

    assert contents.uri == "policy://refund"
    assert contents.mime_type == "text/plain"
    assert "30 days" in contents.text


def test_read_resource_unknown_uri_raises_mcp_error() -> None:
    client, _ = make_client_with_demo_server()
    with pytest.raises(MCPError):
        client.read_resource("policy://missing")


def test_as_tool_registry_maps_remote_tools_into_the_local_registry() -> None:
    client, _ = make_client_with_demo_server()

    registry = client.as_tool_registry()

    assert registry.names() == [
        "check_refund_eligibility",
        "convert_currency",
        "search_knowledge",
    ]
    result = registry.invoke(
        "convert_currency", {"amount": 100, "from_currency": "USD", "to_currency": "SGD"}
    )
    assert result.ok
    assert json.loads(result.output)["amount"] == pytest.approx(135.0)


def test_remote_tool_failure_is_an_observation_through_the_registry() -> None:
    client, _ = make_client_with_demo_server()
    registry = client.as_tool_registry()

    result = registry.invoke("convert_currency", {"amount": 10, "from_currency": "XYZ", "to_currency": "SGD"})

    assert not result.ok
    assert "unsupported" in (result.error or "").lower()


def test_list_tools_requires_discovery_when_security_is_configured() -> None:
    from agentlab.mcp.security import MCPClientSecurity, ToolPinStore

    server = build_demo_server()
    client = MCPClient(InMemoryTransport(server.handle), security=MCPClientSecurity(pins=ToolPinStore()))
    with pytest.raises(MCPError, match="discover"):
        client.list_tools()


def test_custom_server_is_usable_through_the_same_client() -> None:
    server = MCPServer(name="custom", version="9.9.9")
    server.register_tool(
        "add",
        "Add two integers",
        {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
        lambda arguments: {"sum": int(arguments.get("a", 0)) + int(arguments.get("b", 0))},
    )
    client = MCPClient(InMemoryTransport(server.handle))

    result = client.call_tool("add", {"a": 2, "b": 3})

    assert result.ok
    assert json.loads(result.output)["sum"] == 5


def test_client_metadata_is_configurable_and_used_on_every_call() -> None:
    sent: list[dict[str, Any]] = []

    class EchoTransport:
        def send(self, message: dict) -> dict:
            sent.append(message)
            if message["method"] == "server/discover":
                return {
                    "jsonrpc": "2.0",
                    "id": message["id"],
                    "result": {
                        "resultType": "complete",
                        "protocolVersions": [PROTOCOL_VERSION],
                        "serverInfo": {"name": "echo", "version": "1.0.0"},
                        "capabilities": {},
                        "ttlMs": 1000,
                        "cacheScope": "private",
                    },
                }
            return {
                "jsonrpc": "2.0",
                "id": message["id"],
                "result": {"resultType": "complete", "tools": []},
            }

    client = MCPClient(EchoTransport(), client_name="my-agent", client_version="3.1.4")
    client.discover()
    client.list_tools()

    meta = sent[1]["params"]["_meta"]
    assert meta[META_CLIENT_INFO] == {"name": "my-agent", "version": "3.1.4"}
    assert meta[META_PROTOCOL_VERSION] == PROTOCOL_VERSION
