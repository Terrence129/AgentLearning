"""Test infrastructure: deterministic, scripted model behaviour.

Everything in this module is *provided*, not a lab. You should never need to
edit it -- it exists so the whole curriculum can be tested offline, with no API
key, no network, and no flaky assertions.

The central idea: a ``Provider`` is just a function from request to response.
Replace it with a scripted one and the rest of your agent code can be tested
exactly like any other deterministic software.
"""

from __future__ import annotations

from agentlab.budget import Budget
from agentlab.testing.mock import MockProvider, MockTurn, text_turn, tool_turn
from agentlab.trace import MemorySink, Tracer

__all__ = [
    "Budget",
    "MemorySink",
    "MockProvider",
    "MockTurn",
    "Tracer",
    "text_turn",
    "tool_turn",
]
