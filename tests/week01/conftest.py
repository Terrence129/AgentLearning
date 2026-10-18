"""Shared fixtures for the week 1 provider lab.

Every test here uses ``httpx.MockTransport``: no network, no API key, and the
test controls every byte that crosses the provider seam -- including HTTP status
codes, headers and SSE chunk boundaries.
"""

from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest
from agentlab.config import ProviderConfig
from agentlab.providers.openai_compat import OpenAICompatibleProvider

BASE_URL = "https://api.example.test/v1"
MODEL = "test-model"
API_KEY = "sk-test-0123456789abcdef"

Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def config() -> ProviderConfig:
    """A provider config pointed at a fake base URL."""
    return ProviderConfig(
        name="test-provider",
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL,
    )


@pytest.fixture
def make_provider(config: ProviderConfig) -> Callable[..., OpenAICompatibleProvider]:
    """Build a provider wired to a scripted transport.

    ``backoff_base`` defaults to 0 so retry tests stay under the 10 s suite
    budget; the tests that assert on delay values patch ``time.sleep``.
    """

    def _make(
        handler: Handler,
        *,
        max_retries: int = 3,
        backoff_base: float = 0.0,
    ) -> OpenAICompatibleProvider:
        return OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            max_retries=max_retries,
            backoff_base=backoff_base,
        )

    return _make


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record requested retry delays instead of really sleeping."""
    recorded: list[float] = []
    monkeypatch.setattr("time.sleep", recorded.append)
    return recorded
