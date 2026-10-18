"""Structured tracing: the backbone of debugging, evals and observability.

An agent that fails silently is worthless. From week 2 onward every lab emits
trace events through this module, so by week 7 the eval harness already has a
rich data source. The format is a deliberately boring append-only JSONL file:
one event per line, monotonically sequenced, easy to grep, easy to load into
pandas or OpenTelemetry later.

Event kinds used across the course (strings, not enums -- extensibility wins):

    run_start, run_end, step, model_call, model_stream, tool_call, tool_result,
    context_compaction, approval_requested, approval_granted, approval_denied,
    subagent_start, subagent_end, eval_case, guardrail_block, error
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol


def utc_now() -> str:
    """ISO-8601 UTC timestamp with a ``Z`` suffix."""
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def new_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


@dataclass(slots=True)
class TraceEvent:
    run_id: str
    seq: int
    ts: str
    kind: str
    name: str
    data: dict[str, Any] = field(default_factory=dict)
    duration_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "run_id": self.run_id,
            "seq": self.seq,
            "ts": self.ts,
            "kind": self.kind,
            "name": self.name,
            "data": self.data,
        }
        if self.duration_ms is not None:
            out["duration_ms"] = round(self.duration_ms, 3)
        return out

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> TraceEvent:
        return cls(
            run_id=payload["run_id"],
            seq=payload["seq"],
            ts=payload["ts"],
            kind=payload["kind"],
            name=payload["name"],
            data=payload.get("data", {}),
            duration_ms=payload.get("duration_ms"),
        )


class TraceSink(Protocol):
    """Anything that can persist trace events."""

    def write(self, event: TraceEvent) -> None: ...


class MemorySink:
    """Keeps events in memory. Tests assert on this; apps may inspect it live."""

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def write(self, event: TraceEvent) -> None:
        self.events.append(event)

    def of_kind(self, kind: str) -> list[TraceEvent]:
        return [e for e in self.events if e.kind == kind]

    def close(self) -> None:  # symmetry with JsonlSink
        pass


class JsonlSink:
    """Append-only JSONL writer. Flushes every line so crashes lose nothing."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")

    def write(self, event: TraceEvent) -> None:
        self._fh.write(json.dumps(event.to_dict(), ensure_ascii=False, default=str) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> JsonlSink:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class _SeqState:
    """Shared monotonic counter so child tracers keep one total order."""

    __slots__ = ("value",)

    def __init__(self) -> None:
        self.value = 0

    def next(self) -> int:
        self.value += 1
        return self.value


class Tracer:
    """Emits trace events to one or more sinks.

    Usage::

        tracer = Tracer()
        tracer.emit("run_start", "demo", {"goal": "hello"})
        with tracer.span("model_call", "gpt-4.1-mini", model="gpt-4.1-mini") as span:
            span["data"]["input_tokens"] = 42

    A child tracer shares the run id and sinks but tags every event with a
    scope, which is how multi-agent runs stay readable (week 6).
    """

    def __init__(
        self,
        run_id: str | None = None,
        sinks: tuple[TraceSink, ...] | list[TraceSink] = (),
        *,
        scope: str | None = None,
        _seq: _SeqState | None = None,
    ) -> None:
        self.run_id = run_id or new_run_id()
        self.sinks: list[TraceSink] = list(sinks)
        self.scope = scope
        self._seq = _seq or _SeqState()

    # -- emitting ----------------------------------------------------------

    def emit(
        self,
        kind: str,
        name: str,
        data: dict[str, Any] | None = None,
        *,
        duration_ms: float | None = None,
    ) -> TraceEvent:
        payload = dict(data or {})
        if self.scope:
            payload.setdefault("scope", self.scope)
        event = TraceEvent(
            run_id=self.run_id,
            seq=self._seq.next(),
            ts=utc_now(),
            kind=kind,
            name=name,
            data=payload,
            duration_ms=duration_ms,
        )
        for sink in self.sinks:
            sink.write(event)
        return event

    @contextmanager
    def span(self, kind: str, name: str, **attrs: Any) -> Iterator[dict[str, Any]]:
        """Time a block and emit one event when it exits (even on error).

        Yields a mutable dict: write into ``box["data"]`` to add attributes that
        are only known once the block finishes.
        """
        started = time.perf_counter()
        box: dict[str, Any] = {"data": dict(attrs)}
        try:
            yield box
        finally:
            self.emit(kind, name, box["data"], duration_ms=(time.perf_counter() - started) * 1000)

    # -- composition -------------------------------------------------------

    def child(self, scope: str) -> Tracer:
        """A tracer for a sub-agent / sub-task, sharing sinks and sequence."""
        return Tracer(run_id=self.run_id, sinks=self.sinks, scope=scope, _seq=self._seq)

    def add_sink(self, sink: TraceSink) -> None:
        self.sinks.append(sink)

    def close(self) -> None:
        for sink in self.sinks:
            close = getattr(sink, "close", None)
            if callable(close):
                close()

    def __enter__(self) -> Tracer:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def load_trace(path: str | Path) -> list[TraceEvent]:
    """Read a JSONL trace file back into events (used by the week 7 evals)."""
    events: list[TraceEvent] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(TraceEvent.from_dict(json.loads(line)))
    return events
