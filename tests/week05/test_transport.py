"""Tests for MCP in-memory and stdio transports (week 5 lab)."""

from __future__ import annotations

import io
import json

import pytest
from agentlab.mcp.jsonrpc import INVALID_PARAMS, PARSE_ERROR, JSONRPCError
from agentlab.mcp.transport import (
    InMemoryTransport,
    StdioServerTransport,
    TransportClosed,
    decode_line,
    encode_line,
    serve_stdio,
)

pytestmark = pytest.mark.week


def raw_request(request_id: int, method: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": {"_meta": {"v": 1}}}


def raw_result(request_id: int, payload: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": payload}


def test_in_memory_transport_routes_messages_and_records_them() -> None:
    def handler(message: dict) -> dict:
        return raw_result(message["id"], {"echo": message["method"]})

    transport = InMemoryTransport(handler)
    response = transport.send(raw_request(1, "tools/list"))

    assert response is not None
    assert response["result"] == {"echo": "tools/list"}
    assert len(transport.sent) == 1
    assert transport.sent[0]["method"] == "tools/list"


def test_in_memory_transport_passes_notifications_through() -> None:
    calls: list[str] = []

    def handler(message: dict) -> None:
        calls.append(message["method"])

    transport = InMemoryTransport(handler)
    notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert transport.send(notification) is None
    assert calls == ["notifications/initialized"]
    assert len(transport.sent) == 1


def test_stdio_write_message_emits_exactly_one_newline_terminated_line() -> None:
    writer = io.StringIO()
    transport = StdioServerTransport(io.StringIO(), writer)

    transport.write_message(raw_result(1, {"resultType": "complete"}))

    output = writer.getvalue()
    assert output.endswith("\n")
    assert output.count("\n") == 1
    assert json.loads(output)["result"] == {"resultType": "complete"}


def test_stdio_read_message_parses_and_skips_blank_lines() -> None:
    payload = raw_request(9, "tools/list")
    reader = io.StringIO("\n\n" + json.dumps(payload) + "\n")
    transport = StdioServerTransport(reader, io.StringIO())

    assert transport.read_message() == payload


def test_stdio_read_message_at_eof_raises_transport_closed() -> None:
    transport = StdioServerTransport(io.StringIO(""), io.StringIO())
    with pytest.raises(TransportClosed):
        transport.read_message()


def test_encode_and_decode_line_roundtrip() -> None:
    message = raw_request(3, "resources/list")
    line = encode_line(message)
    assert line == json.dumps(message, separators=(",", ":")) + "\n"
    assert decode_line(line) == message


def test_decode_line_rejects_invalid_json() -> None:
    with pytest.raises(JSONRPCError) as caught:
        decode_line("{nope}\n")
    assert caught.value.code == PARSE_ERROR


def test_serve_stdio_processes_requests_and_survives_parse_errors() -> None:
    lines = [
        json.dumps(raw_request(1, "tools/list")),
        "{this is not json}",
        json.dumps(raw_request(2, "resources/list")),
    ]
    reader = io.StringIO("\n".join(lines) + "\n")
    writer = io.StringIO()

    def handler(message: dict) -> dict:
        return raw_result(message["id"], {"ok": True})

    processed = serve_stdio(handler, reader, writer, max_messages=3)

    responses = [json.loads(line) for line in writer.getvalue().splitlines()]
    assert processed == 2
    assert len(responses) == 3
    assert responses[0]["id"] == 1
    assert responses[1]["id"] is None
    assert responses[1]["error"]["code"] == PARSE_ERROR
    assert responses[2]["id"] == 2


def test_serve_stdio_turns_handler_protocol_errors_into_error_responses() -> None:
    reader = io.StringIO(json.dumps(raw_request(4, "tools/call")) + "\n")
    writer = io.StringIO()

    def handler(message: dict) -> dict:
        raise JSONRPCError(INVALID_PARAMS, "unknown tool 'nope'")

    processed = serve_stdio(handler, reader, writer, max_messages=1)

    response = json.loads(writer.getvalue())
    assert processed == 1
    assert response["id"] == 4
    assert response["error"]["code"] == INVALID_PARAMS
