"""MCP transports: in-memory and stdio framing (week 5).

Why this module exists
----------------------
The protocol is transport-agnostic, and that is the point. The 2026-07-28 spec
defines two transports: ``stdio`` (a local child process; one JSON message per
line) and *Streamable HTTP* (one POST endpoint answering with JSON or a
request-scoped SSE stream). Because the message layer is separate, the same
server logic can run over either -- and the same tests can run with no process
and no network.

This module gives you both shapes in a testable form:

- :class:`InMemoryTransport` -- a synchronous request/response channel. It is
  what the week's tests use and the right default for an agent that talks to a
  server in-process.
- :class:`StdioServerTransport` -- newline-delimited JSON framing over two text
  streams. The lab tests it with ``io.StringIO`` (no subprocess, no stdio
  spawning); a production host would wire it to ``sys.stdin.buffer`` /
  ``sys.stdout.buffer``.
- :func:`serve_stdio` -- the read/handle/write loop a stdio server runs.

Documented divergences from the real spec (see labs/week05-mcp/README.md):
this is a **synchronous** subset. Real MCP clients multiplex request ids over
async streams, implement deadline cancellation, handle server-to-client
notifications and ``subscriptions/listen``; none of that is required to learn
the framing, and all of it would make the week's tests flaky.

What breaks without it
----------------------
- Messages get concatenated or split because framing is done by ad-hoc
  ``print``/``read`` rather than one message per line.
- A malformed request kills the server loop instead of producing a parse error
  the client can see.
- The transport leaks into business logic, so the server can only run one way.

Read first: the MCP transport documentation for stdio, then the JSON-RPC
framing module in this package.

Public surface
--------------
``PROTOCOL_VERSION``       the MCP revision this subset implements
``Transport``              protocol: ``send(message) -> response | None``
``TransportError``         base transport failure
``TransportClosed``        the stream ended (EOF)
``TransportTimeout``       the request deadline expired
``InMemoryTransport``      in-process transport with a message log
``StdioServerTransport``   newline-delimited JSON over two text streams
``encode_line``            message -> one line of JSON
``decode_line``            one line of JSON -> validated message
``serve_stdio``            stdio read/handle/write loop
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TextIO

from agentlab.errors import AgentError

#: MCP revision whose stateless design this lab subset implements. Note that
#: 2026-07-28 removed the `initialize` handshake, sessions, `ping`,
#: `logging/setLevel` and the HTTP GET stream; see the README conformance notes.
PROTOCOL_VERSION = "2026-07-28"

#: A handler takes one decoded message and returns a response dict (or None for
#: notifications). Both the in-memory transport and the stdio loop use it, so a
#: server can be exercised without any transport-specific code.
MessageHandler = Callable[[dict[str, Any]], dict[str, Any] | None]


class TransportError(AgentError):
    """A transport-level failure (closed stream, timeout, framing error)."""


class TransportClosed(TransportError):
    """The peer closed the stream; no further messages can be read/written."""


class TransportTimeout(TransportError):
    """The request exceeded its deadline before a response arrived."""


class Transport(Protocol):
    """A bidirectional JSON-RPC channel.

    ``send`` writes one message and returns the matching response, or ``None``
    for a notification. Asynchronous transports would return a future instead;
    the synchronous contract is what keeps week 5 deterministic.
    """

    def send(self, message: dict[str, Any]) -> dict[str, Any] | None: ...


class InMemoryTransport:
    """A synchronous in-process transport.

    ``handler`` is usually ``MCPServer.handle``. Every outgoing message is
    recorded in ``self.sent`` so tests can assert exactly what crossed the
    "wire" (``_meta`` fields included).
    """

    def __init__(self, handler: MessageHandler) -> None:
        self.handler = handler
        self.sent: list[dict[str, Any]] = []

    def send(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Record the message, invoke the handler, return its response."""
        raise NotImplementedError("Week 5 lab: implement InMemoryTransport.send")


class StdioServerTransport:
    """Newline-delimited JSON framing for a stdio MCP *server*.

    MCP stdio framing is deliberately boring: each message is exactly one line
    of UTF-8 JSON, with escaped newlines inside strings. No ``Content-Length``
    headers (that is LSP), no BOM, no blank lines.
    """

    def __init__(self, reader: TextIO, writer: TextIO) -> None:
        self.reader = reader
        self.writer = writer

    def read_message(self) -> dict[str, Any]:
        """Read and validate one line.

        Raises:
            TransportClosed: on EOF (blank lines are skipped).
            JSONRPCError: when the line is not valid JSON-RPC (the caller can
                turn this into a parse-error response).
        """
        raise NotImplementedError("Week 5 lab: implement StdioServerTransport.read_message")

    def write_message(self, message: dict[str, Any]) -> None:
        """Write one message followed by exactly one newline, then flush."""
        raise NotImplementedError("Week 5 lab: implement StdioServerTransport.write_message")


def encode_line(message: dict[str, Any]) -> str:
    """Serialise one message as a single JSON line (including ``\\n``).

    Raises:
        ValueError: if the JSON text could contain a raw newline (it cannot with
            ``json.dumps`` default escaping -- this is a guard for custom
            encoders learners may add).
    """
    raise NotImplementedError("Week 5 lab: implement encode_line")


def decode_line(line: str) -> dict[str, Any]:
    """Parse one JSON line into a validated JSON-RPC message."""
    raise NotImplementedError("Week 5 lab: implement decode_line")


def serve_stdio(
    handler: MessageHandler,
    reader: TextIO,
    writer: TextIO,
    *,
    max_messages: int | None = None,
) -> int:
    """Run the stdio server loop until EOF or ``max_messages`` requests.

    Contract:
        - read one line at a time; skip blank lines;
        - on a parse error, write a JSON-RPC error response with ``id=None`` and
          continue (one bad message must not kill the server);
        - call ``handler`` for valid messages; write a response when the handler
          returns one (``None`` means notification);
        - a handler raising ``JSONRPCError`` becomes an error response;
        - return the number of *valid* messages processed.

    ``max_messages`` exists so tests can drive a finite loop against
    ``io.StringIO``; production hosts leave it ``None``.
    """
    raise NotImplementedError("Week 5 lab: implement serve_stdio")
