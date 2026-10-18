"""Quota tests: fixed windows, per-tenant isolation, token and USD budgets."""

from __future__ import annotations

import pytest
from agentlab.guard.errors import QuotaExceeded
from agentlab.guard.ratelimit import QuotaPolicy, TenantQuotaLimiter

pytestmark = pytest.mark.week


class _Clock:
    def __init__(self, value: float = 100.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _limiter(**policy: object) -> tuple[TenantQuotaLimiter, _Clock]:
    clock = _Clock()
    return TenantQuotaLimiter(QuotaPolicy(**policy), clock=clock), clock  # type: ignore[arg-type]


def test_allows_requests_up_to_quota_then_rejects():
    limiter, _ = _limiter(max_requests=3)

    for _ in range(3):
        limiter.charge("tenant-a")

    with pytest.raises(QuotaExceeded, match="tenant-a"):
        limiter.charge("tenant-a")


def test_window_resets_after_window_seconds():
    limiter, clock = _limiter(max_requests=2, window_s=60.0)

    limiter.charge("tenant-a")
    limiter.charge("tenant-a")
    with pytest.raises(QuotaExceeded):
        limiter.charge("tenant-a")

    clock.advance(60.0)
    limiter.charge("tenant-a")


def test_tenant_quotas_are_isolated():
    limiter, _ = _limiter(max_requests=2)

    limiter.charge("tenant-a")
    limiter.charge("tenant-a")
    limiter.charge("tenant-b")
    limiter.charge("tenant-b")

    with pytest.raises(QuotaExceeded):
        limiter.charge("tenant-a")
    assert limiter.status("tenant-b").used_requests == 2


def test_token_budget_is_enforced():
    limiter, _ = _limiter(max_requests=10, max_tokens=100)

    limiter.charge("tenant-a", tokens=60)
    with pytest.raises(QuotaExceeded, match="token"):
        limiter.charge("tenant-a", tokens=60)

    # the refused request did not consume budget
    assert limiter.status("tenant-a").used_tokens == 60


def test_cost_budget_is_enforced():
    limiter, _ = _limiter(max_requests=10, max_usd=0.01)

    limiter.charge("tenant-a", usd=0.004)
    with pytest.raises(QuotaExceeded, match="usd"):
        limiter.charge("tenant-a", usd=0.02)

    assert limiter.status("tenant-a").used_usd == pytest.approx(0.004)


def test_check_does_not_consume():
    limiter, _ = _limiter(max_requests=1)

    limiter.check("tenant-a")
    limiter.check("tenant-a")
    limiter.charge("tenant-a")
    with pytest.raises(QuotaExceeded):
        limiter.check("tenant-a")


def test_tenant_id_is_required():
    limiter, _ = _limiter(max_requests=2)

    with pytest.raises(ValueError, match="tenant"):
        limiter.charge("")


def test_status_reports_usage_and_reset_time():
    limiter, _ = _limiter(max_requests=5, max_tokens=100, max_usd=1.0, window_s=60.0)

    limiter.charge("tenant-a", tokens=10, usd=0.002)
    limiter.charge("tenant-a", tokens=5, usd=0.001)
    status = limiter.status("tenant-a")

    assert status.tenant_id == "tenant-a"
    assert status.used_requests == 2
    assert status.used_tokens == 15
    assert status.used_usd == pytest.approx(0.003)
    assert status.resets_at == pytest.approx(160.0)
