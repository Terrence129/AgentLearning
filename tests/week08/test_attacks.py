"""Red-team corpus tests: every checked-in attack must be blocked or detected.

The corpus is data (``agentlab/guard/attacks.py``); this file maps each ``target``
to the guard entry point that must stop it. Adding an attack to the corpus
automatically adds a test case here -- that is the point of keeping them apart.
"""

from __future__ import annotations

import pytest
from agentlab.budget import Budget
from agentlab.guard.attacks import ATTACKS, REQUIRED_CATEGORIES, Attack
from agentlab.guard.authority import AuthorityBoundary, effective_authority, reject_credential_passthrough
from agentlab.guard.errors import (
    ApprovalRequired,
    PathNotAllowed,
    QuotaExceeded,
    RoutingError,
    TokenPassthroughError,
)
from agentlab.guard.injection import screen_untrusted, vet_output
from agentlab.guard.ratelimit import QuotaPolicy, TenantQuotaLimiter
from agentlab.guard.routing import CostAwareRouter, ModelCandidate, RouteRequest
from agentlab.guard.sandbox import (
    ApprovalLedger,
    ApprovalToken,
    action_hash,
    require_approval,
    resolve_sandbox_path,
)
from agentlab.pricing import DEFAULT_PRICES
from agentlab.tools.registry import Tool

pytestmark = pytest.mark.week


# ---------------------------------------------------------------------------
# probe dispatch: target -> "was this attack blocked or detected?"
# ---------------------------------------------------------------------------


def _probe_injection(attack: Attack, tmp_path) -> bool:
    decision = screen_untrusted(attack.payload, source="tool")
    return (not decision.allowed) and bool(decision.findings)


def _probe_output(attack: Attack, tmp_path) -> bool:
    result = vet_output(attack.payload, secrets=attack.args.get("secrets", ()))
    return (not result.safe) and bool(result.reasons)


def _probe_path(attack: Attack, tmp_path) -> bool:
    root = tmp_path / "fight"
    root.mkdir(exist_ok=True)
    try:
        resolve_sandbox_path(attack.payload, allowed_roots=[root])
    except PathNotAllowed:
        return True
    return False


def _probe_token(attack: Attack, tmp_path) -> bool:
    name, _, value = attack.payload.partition(":")
    try:
        reject_credential_passthrough({name.strip(): value.strip()})
    except TokenPassthroughError:
        return True
    return False


def _probe_approval(attack: Attack, tmp_path) -> bool:
    args = attack.args
    tool = Tool(
        name=args["tool"],
        description="write tool under attack",
        parameters={},
        handler=lambda arguments: None,
        is_write=True,
    )
    arguments = args["arguments"]
    ledger = ApprovalLedger()
    token = ApprovalToken(
        ticket_id="ticket-1",
        action_hash=action_hash(tool.name, arguments),
        tenant_id=args["tenant_id"],
        approver=args["approver"],
        expires_at=1_060.0,
    )
    require_approval(tool, arguments, token, tenant_id=args["tenant_id"], ledger=ledger, now=1_000.0)
    try:
        require_approval(tool, arguments, token, tenant_id=args["tenant_id"], ledger=ledger, now=1_000.0)
    except ApprovalRequired:
        return True
    return False


def _probe_authority(attack: Attack, tmp_path) -> bool:
    args = attack.args
    boundaries = [
        AuthorityBoundary(
            source=boundary["source"],
            tenant_id=boundary["tenant_id"],
            grants=frozenset(boundary["grants"]),
        )
        for boundary in args["boundaries"]
    ]
    authority = effective_authority(
        tenant_id=args["caller_tenant"],
        boundaries=boundaries,
        model_claims=args["model_claims"],
    )
    return (not authority.allows(attack.payload)) and attack.payload in authority.denied_claims


def _probe_routing(attack: Attack, tmp_path) -> bool:
    args = attack.args
    candidate = ModelCandidate(
        name="premium",
        model=attack.payload,
        price=DEFAULT_PRICES[attack.payload],
        p95_latency_ms=1_500.0,
    )
    router = CostAwareRouter([candidate], budget=Budget(max_usd=args["budget_usd"]))
    request = RouteRequest(
        expected_input_tokens=args["input_tokens"],
        expected_output_tokens=args["output_tokens"],
    )
    try:
        router.select(request)
    except RoutingError:
        return True
    return False


def _probe_quota(attack: Attack, tmp_path) -> bool:
    args = attack.args
    limiter = TenantQuotaLimiter(
        QuotaPolicy(max_requests=args["max_requests"], window_s=60.0), clock=lambda: 0.0
    )
    for _ in range(args["max_requests"]):
        limiter.charge(attack.payload)
    try:
        limiter.charge(attack.payload)
    except QuotaExceeded:
        return True
    return False


_PROBES = {
    "injection": _probe_injection,
    "output": _probe_output,
    "path": _probe_path,
    "token": _probe_token,
    "approval": _probe_approval,
    "authority": _probe_authority,
    "routing": _probe_routing,
    "quota": _probe_quota,
}


def _guard_blocks(attack: Attack, tmp_path) -> bool:
    probe = _PROBES.get(attack.target)
    assert probe is not None, f"{attack.id} targets unknown guard {attack.target!r}"
    return probe(attack, tmp_path)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("attack", ATTACKS, ids=[attack.id for attack in ATTACKS])
def test_attack_is_blocked_or_detected(attack, tmp_path):
    assert _guard_blocks(attack, tmp_path) is True, (
        f"{attack.id} ({attack.title}) was not blocked by the {attack.target} guard"
    )


def test_corpus_has_minimum_size_categories_and_full_coverage(tmp_path):
    assert len(ATTACKS) >= 10
    assert len({attack.id for attack in ATTACKS}) == len(ATTACKS)
    assert {attack.category for attack in ATTACKS} >= REQUIRED_CATEGORIES
    assert {attack.target for attack in ATTACKS} <= set(_PROBES)
    for attack in ATTACKS:
        assert attack.payload, f"{attack.id} has an empty payload"
    assert all(_guard_blocks(attack, tmp_path) for attack in ATTACKS)
