"""Tests for JSON-RPC 2.0 framing and MCP metadata (week 5 lab)."""

from __future__ import annotations

import json

import pytest
from agentlab.mcp.jsonrpc import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    RESULT_TYPE_COMPLETE,
    RESULT_TYPE_INPUT_REQUIRED,
    UNSUPPORTED_PROTOCOL_VERSION,
    JSONRPCError,
    encode_message,
    is_notification,
    make_error,
    make_notification,
    make_request,
    make_result,
    parse_message,
)

pytestmark = pytest.mark.week


def test_make_request_merges_meta_into_params() -> None:
    request = make_request(
        7,
        "tools/list",
        {"cursor": "abc"},
        meta={"io.modelcontextprotocol/protocolVersion": "2026-07-28"},
    )

    assert request["jsonrpc"] == "2.0"
    assert request["id"] == 7
    assert request["method"] == "tools/list"
    assert request["params"]["cursor"] == "abc"
    assert request["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] == "2026-07-28"
    assert "_meta" not in request


def test_make_request_without_params_still_carries_meta() -> None:
    request = make_request(1, "server/discover", meta={"x": "y"})
    assert request["params"] == {"_meta": {"x": "y"}}


def test_make_notification_has_no_id_field() -> None:
    notification = make_notification(
        "notifications/tools/list_changed",
        meta={"io.modelcontextprotocol/protocolVersion": "2026-07-28"},
    )
    assert "id" not in notification
    assert is_notification(notification) is True


def test_make_result_and_error_shapes() -> None:
    result = make_result("req-1", {"resultType": RESULT_TYPE_COMPLETE, "tools": []})
    assert result == {
        "jsonrpc": "2.0",
        "id": "req-1",
        "result": {"resultType": RESULT_TYPE_COMPLETE, "tools": []},
    }

    error = make_error("req-1", INVALID_PARAMS, "bad arguments", {"field": "name"})
    assert error["jsonrpc"] == "2.0"
    assert error["id"] == "req-1"
    assert error["error"] == {
        "code": INVALID_PARAMS,
        "message": "bad arguments",
        "data": {"field": "name"},
    }

    parse_error = make_error(None, PARSE_ERROR, "could not parse JSON")
    assert parse_error["id"] is None
    assert parse_error["error"]["code"] == -32700


def test_jsonrpc_error_to_dict_carries_code_and_data() -> None:
    error = JSONRPCError(
        UNSUPPORTED_PROTOCOL_VERSION,
        "Unsupported protocol version",
        {"supported": ["2026-07-28"], "requested": "1900-01-01"},
    )

    payload = error.to_dict()

    assert payload["code"] == -32022
    assert payload["message"] == "Unsupported protocol version"
    assert payload["data"]["supported"] == ["2026-07-28"]
    assert payload["data"]["requested"] == "1900-01-01"


def test_standard_error_codes_are_stable() -> None:
    assert make_error(1, INVALID_REQUEST, "x")["error"]["code"] == -32600
    assert make_error(1, METHOD_NOT_FOUND, "x")["error"]["code"] == -32601
    assert make_error(1, INTERNAL_ERROR, "x")["error"]["code"] == -32603


def test_parse_message_accepts_json_text_bytes_and_dicts() -> None:
    message = make_request(1, "tools/list", meta={"k": "v"})
    assert parse_message(message) == message
    assert parse_message(json.dumps(message)) == message
    assert parse_message(json.dumps(message).encode("utf-8")) == message


def test_parse_message_reports_parse_errors() -> None:
    with pytest.raises(JSONRPCError) as caught:
        parse_message("{not json")
    assert caught.value.code == PARSE_ERROR


def test_parse_message_rejects_non_objects_and_wrong_versions() -> None:
    with pytest.raises(JSONRPCError) as non_object:
        parse_message("[1, 2, 3]")
    assert non_object.value.code == INVALID_REQUEST

    with pytest.raises(JSONRPCError) as wrong_version:
        parse_message({"jsonrpc": "1.0", "id": 1, "method": "tools/list"})
    assert wrong_version.value.code == INVALID_REQUEST

    with pytest.raises(JSONRPCError) as neither_request_nor_response:
        parse_message({"jsonrpc": "2.0", "id": 1})
    assert neither_request_nor_response.value.code == INVALID_REQUEST

    with pytest.raises(JSONRPCError) as bad_params:
        parse_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": [1]})
    assert bad_params.value.code == INVALID_REQUEST


def test_parse_message_rejects_invalid_id_types() -> None:
    with pytest.raises(JSONRPCError):
        parse_message({"jsonrpc": "2.0", "id": 1.5, "method": "tools/list"})
    with pytest.raises(JSONRPCError):
        parse_message({"jsonrpc": "2.0", "id": True, "method": "tools/list"})


def test_is_notification_distinguishes_absent_id_from_null_id() -> None:
    assert is_notification({"jsonrpc": "2.0", "method": "x"}) is True
    assert is_notification({"jsonrpc": "2.0", "id": None, "method": "x"}) is False
    assert is_notification({"jsonrpc": "2.0", "id": 3, "method": "x"}) is False


def test_encode_message_is_compact_and_single_line() -> None:
    text = encode_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"a": "b"}})
    assert "\n" not in text
    assert json.loads(text)["method"] == "tools/list"


def test_result_type_constants_match_the_2026_spec() -> None:
    result = make_result(1, {"resultType": RESULT_TYPE_INPUT_REQUIRED})
    assert result["result"]["resultType"] == "input_required"
    assert RESULT_TYPE_COMPLETE == "complete"
