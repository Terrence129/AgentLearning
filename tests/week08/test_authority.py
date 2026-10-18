"""Authority tests: deny-by-default intersection, no widening, no token passthrough."""

from __future__ import annotations

import pytest
from agentlab.guard.authority import (
    AuthorityBoundary,
    effective_authority,
    outbound_headers,
    reject_credential_passthrough,
)
from agentlab.guard.errors import AuthorizationError, TokenPassthroughError

pytestmark = pytest.mark.week


def _boundary(source: str, grants: set[str], *, tenant_id: str | None = "tenant-a") -> AuthorityBoundary:
    return AuthorityBoundary(source=source, tenant_id=tenant_id, grants=frozenset(grants))


def test_no_boundaries_grants_nothing():
    authority = effective_authority(tenant_id="tenant-a", boundaries=[])

    assert authority.grants == frozenset()
    assert authority.allows("orders:read") is False
    with pytest.raises(AuthorizationError):
        authority.require("orders:read")


def test_authority_is_the_intersection_of_boundaries():
    authority = effective_authority(
        tenant_id="tenant-a",
        boundaries=[
            _boundary("token", {"orders:read", "orders:write"}),
            _boundary("licence", {"orders:read"}),
        ],
    )

    assert authority.grants == frozenset({"orders:read"})
    assert authority.allows("orders:read") is True
    assert authority.allows("orders:write") is False


def test_model_claims_can_never_widen_authority():
    authority = effective_authority(
        tenant_id="tenant-a",
        boundaries=[_boundary("token", {"orders:read"})],
        model_claims=["orders:write", "orders:read"],
    )

    assert authority.allows("orders:write") is False
    assert authority.denied_claims == frozenset({"orders:write"})


def test_other_tenant_boundary_is_ignored():
    authority = effective_authority(
        tenant_id="tenant-a",
        boundaries=[
            _boundary("token", {"orders:read"}),
            _boundary("other-tenant", {"refund:write"}, tenant_id="tenant-b"),
        ],
    )

    assert authority.grants == frozenset({"orders:read"})
    assert authority.allows("refund:write") is False
    assert [boundary.source for boundary in authority.boundaries] == ["token"]


def test_platform_boundary_applies_to_every_tenant():
    authority = effective_authority(
        tenant_id="tenant-a",
        boundaries=[
            _boundary("platform", {"orders:read", "orders:write"}, tenant_id=None),
            _boundary("token", {"orders:read"}),
        ],
    )

    assert authority.grants == frozenset({"orders:read"})


def test_delegation_can_only_narrow():
    authority = effective_authority(
        tenant_id="tenant-a",
        boundaries=[_boundary("token", {"orders:read", "orders:write"})],
    )

    delegated = authority.delegate(["orders:read"])

    assert delegated.grants == frozenset({"orders:read"})
    assert delegated.tenant_id == "tenant-a"
    with pytest.raises(AuthorizationError):
        authority.delegate(["refund:write"])
    with pytest.raises(ValueError):
        authority.delegate([])


def test_tenant_id_is_required():
    with pytest.raises(ValueError):
        effective_authority(tenant_id="", boundaries=[])


def test_reject_credential_passthrough_detects_caller_credentials():
    with pytest.raises(TokenPassthroughError):
        reject_credential_passthrough({"authorization": "Bearer caller-token"})

    with pytest.raises(TokenPassthroughError):
        reject_credential_passthrough({"Accept": "application/json", "X-Api-Key": "caller-key"})

    assert reject_credential_passthrough({"Accept": "application/json"}) is None


def test_outbound_headers_never_forward_caller_credentials():
    outbound = outbound_headers(
        {"Authorization": "Bearer caller-token", "X-Api-Key": "caller-key", "Accept": "application/json"},
        upstream_token="upstream-token",
    )

    assert outbound["Authorization"] == "Bearer upstream-token"
    assert outbound["Accept"] == "application/json"
    flattened = " ".join(outbound.values())
    assert "caller-token" not in flattened
    assert "caller-key" not in flattened
    with pytest.raises(ValueError):
        outbound_headers({}, upstream_token="")
