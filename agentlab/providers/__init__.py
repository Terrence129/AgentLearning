"""Provider construction.

One factory so the rest of the code never imports a concrete provider class
directly. That indirection is what makes swapping DeepSeek for OpenAI (or a
cassette, or a mock) a one-line change in tests.
"""

from __future__ import annotations

from typing import Any

import httpx

from agentlab.config import ProviderConfig, Settings
from agentlab.errors import ConfigError
from agentlab.providers.base import Provider, assemble_stream, parse_tool_arguments
from agentlab.providers.openai_compat import OpenAICompatibleProvider

__all__ = [
    "OpenAICompatibleProvider",
    "Provider",
    "assemble_stream",
    "build_provider",
    "parse_tool_arguments",
    "provider_from_settings",
]


def build_provider(
    config: ProviderConfig,
    *,
    transport: httpx.BaseTransport | None = None,
    timeout: float = 60.0,
    max_retries: int = 3,
) -> Provider:
    """Build a provider for ``config``.

    ``transport`` exists so tests can inject ``httpx.MockTransport`` -- no
    network, no API key, full control over every byte on the wire.
    """
    if config.api_style != "openai-compatible":
        raise ConfigError(
            f"api_style {config.api_style!r} is not implemented yet. "
            "Anthropic/Gemini adapters are an optional stretch exercise; their wire "
            "formats differ (system prompt placement, content blocks, tool schema)."
        )
    return OpenAICompatibleProvider(config, transport=transport, timeout=timeout, max_retries=max_retries)


def provider_from_settings(settings: Settings, name: str | None = None, **kwargs: Any) -> Provider:
    return build_provider(settings.provider(name), **kwargs)
