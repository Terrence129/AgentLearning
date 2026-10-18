"""JSON-RPC 2.0 message framing for MCP (week 5).

Why this module exists
----------------------
MCP is JSON-RPC 2.0 all the way down. Every feature -- discovery, tool listing,
tool calls, resource reads, errors -- is one of three shapes: a *request*
(``id`` + ``method`` + ``params``), a *result* (``id`` + ``result``), or an
*error* (``id`` + ``error``). Notifications are requests without an ``id``.
Getting the framing right is the difference between "the protocol works" and
"sometimes a message is silently dropped because the id was a string on one side
and an int on the other".

The 2026-07-28 MCP revision (docs/research/01-agent-architecture-sota.md §10,
docs/research/02-frameworks-protocols.md §1.1) is **stateless**: there is no
``initialize`` handshake and no session id. Every request carries its protocol
version, client identity and client capabilities in ``params._meta``. All
results carry a required ``resultType`` field (``"complete"`` or
``"input_required"``). A server that receives an unsupported version answers
with a JSON-RPC error whose code is ``-32022`` and whose ``data.supported``
lists the versions it does speak.

What breaks without it
----------------------
- A response with the wrong ``id`` gets matched to the wrong request (worst in
  an async client with several in-flight calls).
- Client and server disagree about the protocol revision and spend a debugging
  session on a mismatch that should have been one error.
- Malformed JSON crashes the server loop instead of returning a parse error.
- Error codes get invented ad hoc, so callers cannot distinguish "bad
  arguments" (fix the call) from "internal error" (retry/report).

Read first: the JSON-RPC 2.0 specification, then the MCP 2026-07-28 changelog.

Public surface
--------------
``JSONRPC_VERSION``      the only valid protocol marker ("2.0")
``JSONRPCError``         typed protocol error: code, message, data
``make_request``         build a request dict (merges ``_meta`` into params)
``make_notification``    build a notification (request without id)
``make_result``          build a result response
``make_error``           build an error response
``parse_message``        validate/parse one message from text or dict
``is_notification``      True for requests without an id
``encode_message``       canonical JSON text for one message (no newline)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

JSONRPC_VERSION = "2.0"

# -- standard JSON-RPC 2.0 error codes ---------------------------------------
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# -- MCP-reserved codes (2026-07-28 error code allocation policy) ------------
# The JSON-RPC server-error range is partitioned: -32000..-32019 remains
# implementation-defined; -32020..-32099 is reserved for the MCP specification.
HEADER_MISMATCH = -32020
MISSING_REQUIRED_CLIENT_CAPABILITY = -32021
UNSUPPORTED_PROTOCOL_VERSION = -32022

#: MCP request metadata keys. The protocol version and client capabilities are
#: sent on *every* request because there is no session to carry them.
META_PROTOCOL_VERSION = "io.modelcontextprotocol/protocolVersion"
META_CLIENT_INFO = "io.modelcontextprotocol/clientInfo"
META_CLIENT_CAPABILITIES = "io.modelcontextprotocol/clientCapabilities"
META_SERVER_INFO = "io.modelcontextprotocol/serverInfo"

#: Allowed values of the required ``resultType`` field on results.
RESULT_TYPE_COMPLETE = "complete"
RESULT_TYPE_INPUT_REQUIRED = "input_required"


@dataclass(slots=True)
class JSONRPCError(Exception):
    """A JSON-RPC protocol error.

    ``code`` follows the JSON-RPC / MCP allocation; ``data`` is optional and
    must be JSON-serialisable (MCP uses it, e.g. ``{"supported": [...]}`` for
    ``UnsupportedProtocolVersionError``). ``message`` is human-readable and
    safe to log.
    """

    code: int
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """The ``error`` object of a JSON-RPC error response."""
        raise NotImplementedError("Week 5 lab: implement JSONRPCError.to_dict")


def make_request(
    request_id: str | int,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a JSON-RPC 2.0 request.

    Contract:
        - result is ``{"jsonrpc": "2.0", "id": ..., "method": ...}``;
        - ``params`` is included when ``params`` or ``meta`` is supplied;
        - ``meta`` entries are merged into ``params["_meta"]`` (MCP convention),
          never into the top level.
    """
    raise NotImplementedError("Week 5 lab: implement make_request")


def make_notification(
    method: str, params: dict[str, Any] | None = None, *, meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build a notification: a request without an ``id``."""
    raise NotImplementedError("Week 5 lab: implement make_notification")


def make_result(request_id: str | int, result: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON-RPC result response.

    Contract: ``{"jsonrpc": "2.0", "id": request_id, "result": result}``.
    Callers are responsible for the MCP-required ``resultType`` inside
    ``result``.
    """
    raise NotImplementedError("Week 5 lab: implement make_result")


def make_error(
    request_id: str | int | None,
    code: int,
    message: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a JSON-RPC error response (``id`` may be ``None`` for parse errors)."""
    raise NotImplementedError("Week 5 lab: implement make_error")


def parse_message(payload: str | bytes | dict[str, Any]) -> dict[str, Any]:
    """Parse and validate one JSON-RPC message.

    Contract:
        - accepts a JSON string/bytes or an already-decoded dict;
        - raises ``JSONRPCError(PARSE_ERROR)`` for invalid JSON or non-object JSON;
        - raises ``JSONRPCError(INVALID_REQUEST)`` when ``jsonrpc`` is not
          ``"2.0"``, when a message has neither ``method`` nor ``result``/
          ``error``, when ``method`` is not a string, or when ``params`` is not
          an object;
        - ``id`` may be a string, an int, or absent (notification) -- but not a
          bool/float/object.
    """
    raise NotImplementedError("Week 5 lab: implement parse_message")


def is_notification(message: dict[str, Any]) -> bool:
    """True when a request has no ``id`` key at all (notifications never answer)."""
    raise NotImplementedError("Week 5 lab: implement is_notification")


def encode_message(message: dict[str, Any]) -> str:
    """Serialise one message to compact JSON text (no trailing newline).

    Deterministic key order is not required by JSON-RPC, but compact output
    keeps stdio framing predictable: one line per message.
    """
    raise NotImplementedError("Week 5 lab: implement encode_message")
