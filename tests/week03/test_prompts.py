"""Tests for prompt templates and the prompt registry.

A prompt is a versioned asset: render deterministically, hash its content, and
keep every version. These tests pin that contract, including the failure mode
that matters in production -- a missing placeholder must never render as an
empty string and ship a prompt that silently lost its instruction.
"""

from __future__ import annotations

import pytest
from agentlab.schemas.prompts import PromptRegistry, PromptRenderError, PromptTemplate

pytestmark = pytest.mark.week


def test_render_substitutes_named_placeholders() -> None:
    template = PromptTemplate(
        id="greeting",
        version="1.0.0",
        template="Hello {name}, you are {role}.",
    )

    assert template.render(name="Ada", role="engineer") == "Hello Ada, you are engineer."


def test_render_missing_value_raises_naming_placeholder() -> None:
    template = PromptTemplate(
        id="greeting",
        version="1.0.0",
        template="Hello {name}, you are {role}.",
    )

    with pytest.raises(PromptRenderError, match="role"):
        template.render(name="Ada")


def test_render_ignores_extra_values() -> None:
    template = PromptTemplate(id="greeting", version="1.0.0", template="Hi {name}")

    assert template.render(name="Ada", unused="context") == "Hi Ada"


def test_hash_is_stable_and_version_independent() -> None:
    first = PromptTemplate(id="greeting", version="1.0.0", template="Hi {name}")
    second = PromptTemplate(id="greeting", version="2.0.0", template="Hi {name}")

    assert first.hash == second.hash
    assert len(first.hash) == 64
    int(first.hash, 16)  # hexadecimal, not opaque text


def test_hash_changes_with_template_or_id() -> None:
    base = PromptTemplate(id="greeting", version="1.0.0", template="Hi {name}")
    different_text = PromptTemplate(id="greeting", version="1.0.0", template="Hello {name}")
    different_id = PromptTemplate(id="salutation", version="1.0.0", template="Hi {name}")

    assert len({base.hash, different_text.hash, different_id.hash}) == 3


def test_registry_rejects_duplicate_id_and_version() -> None:
    registry = PromptRegistry()
    template = PromptTemplate(id="greeting", version="1.0.0", template="Hi {name}")
    registry.register(template)

    with pytest.raises(ValueError):
        registry.register(template)


def test_registry_rejects_non_numeric_version() -> None:
    registry = PromptRegistry()

    with pytest.raises(ValueError):
        registry.register(PromptTemplate(id="greeting", version="one", template="Hi {name}"))


def test_registry_resolves_latest_by_numeric_version() -> None:
    registry = PromptRegistry()
    registry.register(PromptTemplate(id="greeting", version="1.0.0", template="Hello {name}"))
    registry.register(PromptTemplate(id="greeting", version="1.2.0", template="Hi {name}"))
    registry.register(PromptTemplate(id="greeting", version="1.10.0", template="Hey {name}"))

    assert registry.get("greeting").version == "1.10.0"
    assert registry.get("greeting", "1.2.0").version == "1.2.0"


def test_registry_versions_are_sorted_numerically() -> None:
    registry = PromptRegistry()
    for version in ("1.10.0", "1.2.0", "1.0.0"):
        registry.register(PromptTemplate(id="greeting", version=version, template="Hi {name}"))

    assert registry.versions("greeting") == ["1.0.0", "1.2.0", "1.10.0"]


def test_registry_render_uses_latest_version() -> None:
    registry = PromptRegistry()
    registry.register(PromptTemplate(id="greeting", version="1.0.0", template="Hello {name}"))
    registry.register(PromptTemplate(id="greeting", version="1.1.0", template="Hey {name}"))

    assert registry.render("greeting", name="Ada") == "Hey Ada"


def test_registry_unknown_prompt_raises_key_error() -> None:
    registry = PromptRegistry()

    with pytest.raises(KeyError):
        registry.get("missing")


def test_registry_unknown_version_raises_key_error() -> None:
    registry = PromptRegistry()
    registry.register(PromptTemplate(id="greeting", version="1.0.0", template="Hi {name}"))

    with pytest.raises(KeyError):
        registry.get("greeting", "9.9.9")


def test_registry_has_reports_registered_prompt() -> None:
    registry = PromptRegistry()
    registry.register(PromptTemplate(id="greeting", version="1.0.0", template="Hi {name}"))

    assert registry.has("greeting") is True
    assert registry.has("missing") is False
