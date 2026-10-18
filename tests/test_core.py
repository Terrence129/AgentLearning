"""Tests for the provided infrastructure (not a lab).

If these fail, the foundation is broken -- fix them before starting week 1.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agentlab.budget import Budget
from agentlab.config import ProviderConfig, Settings
from agentlab.errors import BudgetExceeded, ConfigError, ProviderError
from agentlab.pricing import estimate_cost, price_for
from agentlab.providers.base import assemble_stream, parse_tool_arguments
from agentlab.testing import MockProvider, text_turn, tool_turn
from agentlab.testing.cassettes import CassetteProvider
from agentlab.tools import Tool, ToolRegistry, schema_from_model
from agentlab.trace import JsonlSink, MemorySink, Tracer, load_trace
from agentlab.types import CompletionRequest, Message, ToolCall, ToolSpec, Usage
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# types
# ---------------------------------------------------------------------------


def test_message_to_dict_excludes_empty_fields() -> None:
    message = Message.user("hello")
    assert message.to_dict() == {"role": "user", "content": "hello"}


def test_assistant_message_with_tool_calls_roundtrips() -> None:
    message = Message.assistant(None, [ToolCall(id="call_1", name="add", arguments={"a": 1})])
    payload = message.to_dict()
    assert payload["role"] == "assistant"
    assert "content" not in payload
    assert payload["tool_calls"][0]["name"] == "add"


def test_usage_addition() -> None:
    total = Usage(10, 5, 3) + Usage(1, 2, 1)
    assert (total.input_tokens, total.output_tokens, total.cached_input_tokens) == (11, 7, 4)
    assert total.total_tokens == 18


def test_tool_spec_openai_shape() -> None:
    spec = ToolSpec(name="add", description="add numbers", parameters={"type": "object"}, strict=True)
    wire = spec.as_openai_tool()
    assert wire["type"] == "function"
    assert wire["function"]["name"] == "add"
    assert wire["function"]["strict"] is True


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


def test_settings_parses_providers_from_mapping() -> None:
    settings = Settings.from_env(
        env={
            "OPENAI_API_KEY": "sk-test-1234567890abcd",
            "DEEPSEEK_API_KEY": "sk-deepseek-1234567890",
            "DEFAULT_PROVIDER": "deepseek",
            "AGENTLAB_RUN_BUDGET_USD": "1.25",
        }
    )
    assert set(settings.providers) == {"openai", "deepseek"}
    assert settings.default_provider == "deepseek"
    assert settings.run_budget_usd == pytest.approx(1.25)
    assert settings.providers["openai"].base_url.startswith("https://")


def test_settings_provider_missing_raises_helpfully() -> None:
    settings = Settings.from_env(env={"DEFAULT_PROVIDER": "openai"})
    with pytest.raises(ConfigError, match="not configured"):
        settings.provider()


def test_provider_config_does_not_leak_key_in_repr() -> None:
    config = ProviderConfig(
        name="openai", api_key="sk-super-secret-value-123", base_url="https://x", model="m"
    )
    assert "super-secret" not in repr(config)


def test_mock_provider_name_is_not_a_real_provider() -> None:
    settings = Settings.from_env(env={"OPENAI_API_KEY": "sk-test-1234567890abcd"})
    with pytest.raises(ConfigError, match="only for tests"):
        settings.provider("mock")


# ---------------------------------------------------------------------------
# pricing & budgets
# ---------------------------------------------------------------------------


def test_price_lookup_uses_longest_prefix() -> None:
    assert price_for("gpt-4.1-mini-2026-01-01") is price_for("gpt-4.1-mini")
    assert price_for("gpt-4.1") is not price_for("gpt-4.1-mini")
    assert price_for("totally-unknown-model") is None


def test_estimate_cost_arithmetic() -> None:
    cost = estimate_cost("gpt-4.1-mini", Usage(input_tokens=1_000_000, output_tokens=1_000_000))
    assert cost == pytest.approx(0.40 + 1.60)
    assert estimate_cost("unknown", Usage(1000, 1000)) == 0.0


def test_budget_enforces_usd() -> None:
    budget = Budget(max_usd=0.001)
    budget.charge("gpt-4.1-mini", Usage(1_000_000, 0))
    with pytest.raises(BudgetExceeded, match="USD budget"):
        budget.assert_ok()


def test_budget_enforces_steps_and_tokens() -> None:
    budget = Budget(max_steps=2)
    budget.add_step()
    budget.add_step()
    with pytest.raises(BudgetExceeded, match="step budget"):
        budget.assert_ok()

    tokens = Budget(max_input_tokens=10)
    tokens.charge("mock-1", Usage(11, 0))
    with pytest.raises(BudgetExceeded, match="input-token"):
        tokens.assert_ok()


def test_budget_summary_reports_unknown_pricing() -> None:
    budget = Budget(max_usd=1.0)
    budget.charge("mystery-model", Usage(10, 10))
    assert budget.summary()["unknown_priced_models"] == ["mystery-model"]


# ---------------------------------------------------------------------------
# tracing
# ---------------------------------------------------------------------------


def test_tracer_sequences_and_scopes() -> None:
    sink = MemorySink()
    tracer = Tracer(run_id="run-1", sinks=[sink])
    tracer.emit("run_start", "demo")
    child = tracer.child("worker-1")
    child.emit("step", "inner")
    tracer.emit("run_end", "demo")

    assert [e.seq for e in sink.events] == [1, 2, 3]
    assert sink.events[1].data["scope"] == "worker-1"
    assert all(e.run_id == "run-1" for e in sink.events)


def test_tracer_span_records_duration_and_data() -> None:
    sink = MemorySink()
    tracer = Tracer(sinks=[sink])
    with tracer.span("model_call", "gpt", model="m") as box:
        box["data"]["output_tokens"] = 7
    event = sink.events[0]
    assert event.kind == "model_call"
    assert event.data["output_tokens"] == 7
    assert event.duration_ms is not None and event.duration_ms >= 0


def test_jsonl_trace_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    sink = JsonlSink(path)
    tracer = Tracer(run_id="r1", sinks=[sink])
    tracer.emit("step", "one", {"x": 1})
    tracer.emit("step", "two", {"x": 2})
    sink.close()

    loaded = load_trace(path)
    assert [e.name for e in loaded] == ["one", "two"]
    assert loaded[1].data == {"x": 2}
    assert json.loads(path.read_text(encoding="utf-8").splitlines()[0])["run_id"] == "r1"


# ---------------------------------------------------------------------------
# tool registry
# ---------------------------------------------------------------------------


class AddInput(BaseModel):
    a: int
    b: int


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="add",
            description="Add two integers",
            parameters=schema_from_model(AddInput),
            handler=lambda args: args.a + args.b,
            input_model=AddInput,
        )
    )
    return registry


def test_tool_registry_invokes_and_returns_text() -> None:
    registry = build_registry()
    result = registry.invoke("add", {"a": 2, "b": 3})
    assert result.ok
    assert result.output == "5"


def test_tool_registry_validation_failure_is_an_observation() -> None:
    registry = build_registry()
    result = registry.invoke("add", {"a": "not-a-number"})
    assert not result.ok
    assert "schema" in (result.error or "")


def test_tool_registry_unknown_tool_is_an_observation() -> None:
    result = build_registry().invoke("rm_rf", {})
    assert not result.ok
    assert "unknown tool" in result.output
    assert "add" in result.output  # tells the model what is available


def test_tool_errors_become_observations() -> None:
    def explode(_: dict) -> str:
        raise RuntimeError("boom")

    registry = ToolRegistry().register(
        Tool(name="explode", description="explodes", parameters={"type": "object"}, handler=explode)
    )
    result = registry.invoke("explode", {})
    assert not result.ok
    assert "RuntimeError" in (result.error or "")


def test_tool_output_is_truncated() -> None:
    tool = Tool(
        name="big",
        description="big output",
        parameters={"type": "object"},
        handler=lambda _: "x" * 500,
        max_output_chars=100,
    )
    result = tool.invoke({})
    assert result.truncated
    assert len(result.output) < 200
    assert "truncated" in result.output


def test_duplicate_tool_registration_rejected() -> None:
    registry = build_registry()
    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            Tool(name="add", description="dup", parameters={"type": "object"}, handler=lambda _: "")
        )


# ---------------------------------------------------------------------------
# mock provider & streaming
# ---------------------------------------------------------------------------


def test_mock_provider_scripts_turns_and_logs_calls() -> None:
    provider = MockProvider([text_turn("first"), text_turn("second")])
    request = CompletionRequest(messages=[Message.user("hi")], model="mock-1")

    assert provider.complete(request).text == "first"
    assert provider.complete(request).text == "second"
    assert len(provider.calls) == 2


def test_mock_provider_exhaustion_is_loud() -> None:
    provider = MockProvider([])
    with pytest.raises(ProviderError, match="script exhausted"):
        provider.complete(CompletionRequest(messages=[Message.user("hi")], model="mock-1"))


def test_stream_and_complete_are_equivalent() -> None:
    turns = [
        tool_turn("add", {"a": 1, "b": 2}, text="let me add"),
        text_turn("the answer is 3"),
    ]
    request = CompletionRequest(messages=[Message.user("1+2?")], model="mock-1")

    completed = MockProvider(list(turns)).complete(request)
    streamed = assemble_stream(list(MockProvider(list(turns)).stream(request)))

    assert completed.text == streamed.text
    assert [c.name for c in completed.tool_calls] == [c.name for c in streamed.tool_calls]
    assert completed.tool_calls[0].arguments == streamed.tool_calls[0].arguments


def test_assemble_stream_handles_empty_arguments() -> None:
    provider = MockProvider([tool_turn("noop", {})])
    response = assemble_stream(
        list(provider.stream(CompletionRequest(messages=[Message.user("x")], model="mock-1")))
    )
    assert response.tool_calls[0].arguments == {}


def test_parse_tool_arguments_rejects_bad_json() -> None:
    with pytest.raises(ProviderError, match="not valid JSON"):
        parse_tool_arguments("{not json")
    assert parse_tool_arguments("") == {}
    assert parse_tool_arguments('{"a": 1}') == {"a": 1}


# ---------------------------------------------------------------------------
# cassettes
# ---------------------------------------------------------------------------


def test_cassette_records_then_replays(tmp_path: Path) -> None:
    path = tmp_path / "cassette.json"
    request = CompletionRequest(messages=[Message.user("hi")], model="mock-1")

    with CassetteProvider(MockProvider([text_turn("recorded")]), path, mode="record") as recorder:
        assert recorder.complete(request).text == "recorded"

    replay = CassetteProvider(None, path, mode="replay")
    assert replay.complete(request).text == "recorded"


def test_cassette_replay_miss_is_explicit(tmp_path: Path) -> None:
    cassette = CassetteProvider(None, tmp_path / "empty.json", mode="replay")
    with pytest.raises(ProviderError, match="No cassette entry"):
        cassette.complete(CompletionRequest(messages=[Message.user("different")], model="mock-1"))
