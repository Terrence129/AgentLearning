"""MCP transports: in-memory and stdio framing (week 5).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Protocol, TextIO

from agentlab.errors import AgentError
from agentlab.mcp.jsonrpc import (
    INTERNAL_ERROR,
    JSONRPCError,
    make_error,
    parse_message,
)

PROTOCOL_VERSION = "2026-07-28"

MessageHandler = Callable[[dict[str, Any]], dict[str, Any] | None]


class TransportError(AgentError):
    """A transport-level failure (closed stream, timeout, framing error)."""


class TransportClosed(TransportError):
    """The peer closed the stream; no further messages can be read/written."""


class TransportTimeout(TransportError):
    """The request exceeded its deadline before a response arrived."""


class Transport(Protocol):
    """A bidirectional JSON-RPC channel."""

    def send(self, message: dict[str, Any]) -> dict[str, Any] | None: ...


class InMemoryTransport:
    """A synchronous in-process transport."""

    def __init__(self, handler: MessageHandler) -> None:
        self.handler = handler
        self.sent: list[dict[str, Any]] = []

    def send(self, message: dict[str, Any]) -> dict[str, Any] | None:
        self.sent.append(message)
        return self.handler(message)


class StdioServerTransport:
    """Newline-delimited JSON framing for a stdio MCP server."""

    def __init__(self, reader: TextIO, writer: TextIO) -> None:
        self.reader = reader
        self.writer = writer

    def read_message(self) -> dict[str, Any]:
        while True:
            line = self.reader.readline()
            if line == "":
                raise TransportClosed("stdio stream closed (EOF)")
            if not line.strip():
                continue
            return parse_message(line)

    def write_message(self, message: dict[str, Any]) -> None:
        try:
            text = encode_line(message)
        except (TypeError, ValueError) as exc:
            raise TransportError(f"message is not JSON-serialisable: {exc}") from exc
        self.writer.write(text)
        self.writer.flush()


def encode_line(message: dict[str, Any]) -> str:
    return json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n"


def decode_line(line: str) -> dict[str, Any]:
    return parse_message(line)


def serve_stdio(
    handler: MessageHandler,
    reader: TextIO,
    writer: TextIO,
    *,
    max_messages: int | None = None,
) -> int:
    transport = StdioServerTransport(reader, writer)
    processed = 0
    while max_messages is None or processed < max_messages:
        try:
            message = transport.read_message()
        except TransportClosed:
            break
        except JSONRPCError as exc:
            transport.write_message(make_error(None, exc.code, exc.message, exc.data))
            continue
        processed += 1
        try:
            response = handler(message)
        except JSONRPCError as exc:
            response = make_error(message.get("id"), exc.code, exc.message, exc.data)
        except Exception as exc:  # one bad request must not kill the server loop
            response = make_error(
                message.get("id"), INTERNAL_ERROR, f"internal error: {type(exc).__name__}: {exc}"
            )
        if response is not None:
            transport.write_message(response)
    return processed
