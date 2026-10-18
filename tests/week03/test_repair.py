"""Tests for validation-error formatting, repair messages and failure metrics.

The repair loop is only as good as the feedback it sends: an error message the
model can act on, attached to the output it must fix, under a bounded retry
budget that the metrics make visible.
"""

from __future__ import annotations

import pytest
from agentlab.schemas.repair import (
    REPAIR_PROMPT,
    RepairStats,
    build_repair_messages,
    format_validation_errors,
)

pytestmark = pytest.mark.week


def test_format_validation_errors_joins_location_and_message() -> None:
    errors = [
        {"loc": ("headline",), "msg": "String should have at most 12 words"},
        {"loc": ("items", 0, "name"), "msg": "Field required"},
    ]

    assert format_validation_errors(errors) == [
        "headline: String should have at most 12 words",
        "items.0.name: Field required",
    ]


def test_format_validation_errors_maps_empty_location_to_root() -> None:
    assert format_validation_errors([{"loc": (), "msg": "Invalid value"}]) == ["<root>: Invalid value"]


def test_repair_prompt_is_a_versioned_asset() -> None:
    assert REPAIR_PROMPT.id == "structured-repair"
    # the prompt must be renderable and mention the two things the model needs
    rendered = REPAIR_PROMPT.render(schema_name="Answer", errors="- answer: bad")
    assert "Answer" in rendered
    assert "answer: bad" in rendered


def test_build_repair_messages_keeps_invalid_output_and_errors() -> None:
    messages = build_repair_messages(
        '{"answer": 1}',
        ["answer: Input should be a valid string"],
        schema_name="Answer",
    )

    assert [message.role for message in messages] == ["assistant", "user"]
    assert messages[0].content == '{"answer": 1}'
    instruction = messages[1].content or ""
    assert "Answer" in instruction
    assert "answer: Input should be a valid string" in instruction
    assert "JSON" in instruction


def test_repair_stats_track_clean_repaired_and_failed() -> None:
    stats = RepairStats()

    stats.record(repairs=0, valid=True)
    stats.record(repairs=1, valid=True)
    stats.record(repairs=1, valid=False)

    assert (stats.total, stats.clean, stats.repaired, stats.failed) == (3, 1, 1, 1)
    assert stats.repair_rate == pytest.approx(1 / 3)
    assert stats.failure_rate == pytest.approx(1 / 3)


def test_repair_stats_rates_are_zero_when_empty() -> None:
    stats = RepairStats()

    assert stats.repair_rate == 0.0
    assert stats.failure_rate == 0.0
