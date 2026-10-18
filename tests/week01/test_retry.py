"""Retry-policy tests: the adapter's error taxonomy and backoff.

These are the tests that justify putting retries *behind* the provider seam. If
they pass, a 429, a flaky gateway and a malformed request produce three
different, testable outcomes -- and the agent loop never sees an ``httpx`` type.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from agentlab.errors import ProviderError
from agentlab.types import CompletionRequest, Message

pytestmark = pytest.mark.week


def _ok_body() -> dict[str, Any]:
    return {
        "model": "test-model",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }


def _request() -> CompletionRequest:
    return CompletionRequest(messages=[Message.user("hi")], model="test-model")


def test_success_on_first_attempt_makes_one_request_and_does_not_sleep(
    make_provider, sleeps: list[float]
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler)
    response = provider.complete(_request())

    assert response.text == "ok"
    assert len(calls) == 1
    assert sleeps == []


def test_retries_5xx_then_succeeds(make_provider) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(503, text="gateway down")
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler, max_retries=2)
    response = provider.complete(_request())

    assert response.text == "ok"
    assert len(calls) == 2


def test_gives_up_after_max_retries_with_typed_error(make_provider) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(500, text="x" * 500)

    provider = make_provider(handler, max_retries=2)

    with pytest.raises(ProviderError) as info:
        provider.complete(_request())

    error = info.value
    assert len(calls) == 3  # max_retries + 1 attempts
    assert error.status == 500
    assert error.retryable is True
    assert error.body is not None
    assert 0 < len(error.body) <= 200  # bodies are truncated, not dumped


def test_does_not_retry_bad_request(make_provider) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(400, text="invalid tool schema")

    provider = make_provider(handler, max_retries=3)

    with pytest.raises(ProviderError) as info:
        provider.complete(_request())

    assert len(calls) == 1
    assert info.value.status == 400
    assert info.value.retryable is False


def test_honours_retry_after_header(make_provider, sleeps: list[float]) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(429, headers={"retry-after": "2.5"}, text="slow down")
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler, max_retries=1)
    response = provider.complete(_request())

    assert response.text == "ok"
    assert len(calls) == 2
    assert sleeps == [2.5]  # the server said 2.5 s: obey it exactly


def test_uses_exponential_backoff_with_jitter_without_retry_after(make_provider, sleeps: list[float]) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) <= 2:
            return httpx.Response(500, text="boom")
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler, max_retries=2, backoff_base=0.1)
    response = provider.complete(_request())

    assert response.text == "ok"
    assert len(calls) == 3
    assert len(sleeps) == 2
    assert 0.1 <= sleeps[0] <= 0.1 + 0.05 + 1e-9  # base * 2**0 + jitter
    assert 0.2 <= sleeps[1] <= 0.2 + 0.05 + 1e-9  # base * 2**1 + jitter


def test_retries_transport_errors_then_succeeds(make_provider) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) <= 2:
            raise httpx.ConnectError("connection reset by peer")
        return httpx.Response(200, json=_ok_body())

    provider = make_provider(handler, max_retries=3)
    response = provider.complete(_request())

    assert response.text == "ok"
    assert len(calls) == 3


def test_transport_error_becomes_provider_error(make_provider) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        raise httpx.ReadTimeout("timed out")

    provider = make_provider(handler, max_retries=1)

    with pytest.raises(ProviderError) as info:
        provider.complete(_request())

    assert len(calls) == 2
    assert info.value.status is None
    assert info.value.retryable is True


def test_max_retries_zero_means_single_attempt(make_provider) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(500, text="boom")

    provider = make_provider(handler, max_retries=0)

    with pytest.raises(ProviderError):
        provider.complete(_request())

    assert len(calls) == 1
