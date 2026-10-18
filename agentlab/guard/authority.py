"""Deny-by-default authority: the model proposes, the system disposes.

Every agent request carries independent claims about who the caller is and what
they may do: the authenticated token, the tenant licence, the capability
catalogue entry, the user's role binding, the run's scope. None of them is
trusted alone, and **none of them can be widened by model output** (research 05
§4.2, research 03 §3.2 "excessive agency"):

- Authority is the **intersection** over all applicable boundaries. Adding a
  boundary can only narrow. An empty boundary set grants nothing.
- A **tenant mismatch is not an authority**: a grant from tenant B never
  intersects into tenant A. The platform binds the tenant; the model never
  supplies it.
- What the model *claims* (``model_claims``) is a **request**, recorded as
  ``denied_claims`` when outside the effective grants, never a permission.
- ``delegate`` can only narrow: a sub-agent never inherits more than its parent.
- **No token passthrough** (MCP authorization, 2025-11-25): caller credentials are
  stripped from outbound requests; the agent obtains its own audience-bound
  upstream credential instead. Forwarding the caller's token makes the agent a
  confused deputy.

Read first: research 05 §4.2 (fail-closed authority intersection) and research
03 §3.3 (MCP hardening: audience-bound tokens, no passthrough).

Hints:
- ``frozenset.intersection(*grants)`` over the matching boundaries is the whole
  computation; getting "no matching boundaries" right is the deny-by-default part.
- Do header matching case-insensitively; HTTP header names are not case sensitive.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

#: Header names that carry caller credentials and must never be forwarded.
SENSITIVE_HEADERS: frozenset[str] = frozenset(
    {"authorization", "proxy-authorization", "cookie", "x-api-key", "x-auth-token"}
)


@dataclass(frozen=True, slots=True)
class AuthorityBoundary:
    """One independent source of grants (token, role, licence, catalogue...).

    Attributes:
        source: which system this boundary came from (for audit evidence).
        tenant_id: the tenant this boundary applies to; ``None`` means a
            platform-wide boundary that applies to every tenant.
        grants: capability names granted by this source, e.g. ``"orders:read"``.
    """

    source: str
    tenant_id: str | None
    grants: frozenset[str]


@dataclass(frozen=True, slots=True)
class EffectiveAuthority:
    """The intersection of every applicable boundary.

    Attributes:
        tenant_id: the platform-bound tenant this authority belongs to.
        grants: capabilities that every matching boundary granted.
        denied_claims: capabilities the model asked for but was not granted
            (recorded for audit; never permissions).
        boundaries: the boundaries that actually participated, for evidence.
    """

    tenant_id: str
    grants: frozenset[str]
    denied_claims: frozenset[str] = frozenset()
    boundaries: tuple[AuthorityBoundary, ...] = ()

    def allows(self, capability: str) -> bool:
        """Return whether ``capability`` is in the effective grants."""
        raise NotImplementedError("Week 8 lab: implement EffectiveAuthority.allows")

    def require(self, capability: str) -> None:
        """Raise ``AuthorizationError`` unless ``capability`` is granted."""
        raise NotImplementedError("Week 8 lab: implement EffectiveAuthority.require")

    def delegate(self, requested: Sequence[str]) -> EffectiveAuthority:
        """Return a strictly narrower authority for a sub-agent.

        Contract:
            - ``requested`` must be a subset of ``self.grants``; asking for more
              raises ``AuthorizationError`` (delegation narrows, never widens);
            - raises ``ValueError`` when ``requested`` is empty (delegate nothing
              rather than delegate everything implicitly);
            - the result keeps the tenant, boundaries, and denied claims.
        """
        raise NotImplementedError("Week 8 lab: implement EffectiveAuthority.delegate")


def effective_authority(
    *,
    tenant_id: str,
    boundaries: Sequence[AuthorityBoundary],
    model_claims: Sequence[str] = (),
) -> EffectiveAuthority:
    """Compute the effective authority by fail-closed intersection.

    Contract:
        - ``tenant_id`` must be a non-empty string (``ValueError`` otherwise); it
          is bound by the platform, never by the model;
        - applicable boundaries are those with ``tenant_id`` equal to the caller's
          or ``None`` (platform-wide); boundaries for other tenants are dropped;
        - with no applicable boundaries the grants are empty (deny by default);
        - grants are the intersection of the applicable boundaries' grants;
        - ``model_claims`` never add grants; claims outside the grants are
          recorded in ``denied_claims``.
    """
    raise NotImplementedError("Week 8 lab: implement effective_authority")


def reject_credential_passthrough(headers: Mapping[str, str]) -> None:
    """Raise ``TokenPassthroughError`` if ``headers`` carry caller credentials.

    Contract: header names are matched case-insensitively against
    ``SENSITIVE_HEADERS``; the error message names the offending headers. Safe
    headers return ``None``.
    """
    raise NotImplementedError("Week 8 lab: implement reject_credential_passthrough")


def outbound_headers(
    caller_headers: Mapping[str, str],
    *,
    upstream_token: str,
) -> dict[str, str]:
    """Build headers for an upstream call without forwarding caller credentials.

    Contract:
        - every ``SENSITIVE_HEADERS`` entry from ``caller_headers`` is dropped;
        - ``Authorization: Bearer <upstream_token>`` is set from the agent's own
          audience-bound credential;
        - other caller headers are preserved verbatim;
        - an empty ``upstream_token`` raises ``ValueError``: the agent must never
          call upstream unauthenticated just because the caller token was dropped.
    """
    raise NotImplementedError("Week 8 lab: implement outbound_headers")
