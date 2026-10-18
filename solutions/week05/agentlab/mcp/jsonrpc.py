"""JSON-RPC 2.0 message framing for MCP (week 5).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

JSONRPC_VERSION = "2.0"

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

HEADER_MISMATCH = -32020
MISSING_REQUIRED_CLIENT_CAPABILITY = -32021
UNSUPPORTED_PROTOCOL_VERSION = -32022

META_PROTOCOL_VERSION = "io.modelcontextprotocol/protocolVersion"
META_CLIENT_INFO = "io.modelcontextprotocol/clientInfo"
META_CLIENT_CAPABILITIES = "io.modelcontextprotocol/clientCapabilities"
META_SERVER_INFO = "io.modelcontextprotocol/serverInfo"

RESULT_TYPE_COMPLETE = "complete"
RESULT_TYPE_INPUT_REQUIRED = "input_required"


@dataclass(slots=True)
class JSONRPCError(Exception):
    """A JSON-RPC protocol error."""

    code: int
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            payload["data"] = self.data
        return payload


def _with_meta(params: dict[str, Any] | None, meta: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(params or {})
    if meta:
        merged = dict(payload.get("_meta") or {})
        merged.update(meta)
        payload["_meta"] = merged
    return payload


def make_request(
    request_id: str | int,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "id": request_id, "method": method}
    params_payload = _with_meta(params, meta)
    if params_payload or params is not None or meta is not None:
        payload["params"] = params_payload
    return payload


def make_notification(
    method: str, params: dict[str, Any] | None = None, *, meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "method": method}
    params_payload = _with_meta(params, meta)
    if params_payload or params is not None or meta is not None:
        payload["params"] = params_payload
    return payload


def make_result(request_id: str | int, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def make_error(
    request_id: str | int | None,
    code: int,
    message: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
        "error": JSONRPCError(code, message, data).to_dict(),
    }
    return response


def _valid_id(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, (str, int)) and not isinstance(value, bool)


def parse_message(payload: str | bytes | dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, (str, bytes, bytearray)):
        try:
            decoded = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise JSONRPCError(PARSE_ERROR, f"could not parse JSON: {exc}") from exc
    else:
        decoded = payload

    if not isinstance(decoded, dict):
        raise JSONRPCError(INVALID_REQUEST, "message must be a JSON object")
    if decoded.get("jsonrpc") != JSONRPC_VERSION:
        raise JSONRPCError(INVALID_REQUEST, "message must declare jsonrpc '2.0'")

    if "method" in decoded:
        if not isinstance(decoded["method"], str):
            raise JSONRPCError(INVALID_REQUEST, "method must be a string")
        if "params" in decoded and not isinstance(decoded["params"], dict):
            raise JSONRPCError(INVALID_REQUEST, "params must be an object")
    elif "result" not in decoded and "error" not in decoded:
        raise JSONRPCError(INVALID_REQUEST, "message must contain method, result or error")

    if "id" in decoded and not _valid_id(decoded["id"]):
        raise JSONRPCError(INVALID_REQUEST, "id must be a string, an integer or null")
    return decoded


def is_notification(message: dict[str, Any]) -> bool:
    return "id" not in message


def encode_message(message: dict[str, Any]) -> str:
    return json.dumps(message, ensure_ascii=False, separators=(",", ":"))
