#!/usr/bin/env python
"""Mini-SendOS capstone demo: the whole governed lifecycle, offline (week 9).

What it demonstrates
--------------------
One authenticated goal flows through the four seams you built:

    goal -> typed decision -> persisted proposal -> bound human approval
         -> at-most-once execution -> append-only audit trail

No network, no API key, no FastAPI: the model is ``agentlab.testing.MockProvider``
and the tools are local simulations, so the demo is deterministic and free.

How to run it
-------------
::

    # Windows (PowerShell)
    .\\.venv\\Scripts\\python.exe scripts\\demo_capstone.py

    # macOS / Linux
    uv run python scripts/demo_capstone.py

Before the capstone is implemented the script stops at the first unimplemented
seam and prints exactly what is missing. That is expected: the demo is a
prerequisite check, not a test. Build in this order and re-run it after each step:

1. ``agentlab/capstone/decisions.py`` -- ``parse_decision``,
   ``decision_to_wire``, ``enforce_presentation_budgets``.
2. ``agentlab/capstone/catalogue.py`` -- ``CapabilityCatalogue.merge``,
   ``resolve``, ``list_for_tenant``, ``ids``, ``__len__``.
3. ``agentlab/capstone/platform.py``  -- ``action_digest`` and the five lifecycle
   methods.

The script exits ``0`` only when the whole demo completes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Allow ``python scripts/demo_capstone.py`` from the repo root without installing.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentlab.capstone import (  # noqa: E402
    CapabilityCatalogue,
    CapabilityDefinition,
    CapstonePlatform,
    GoalRequest,
)
from agentlab.testing import MockProvider, text_turn  # noqa: E402
from agentlab.tools.registry import ToolRegistry  # noqa: E402

TENANT = "acme"
ACTOR = "analyst-1"
APPROVER = "manager-1"
ORDER_ID = "ORD-1"
DISCOUNT_PERCENT = 10

#: The decision the scripted model returns for ``submit_goal``. It is a valid
#: wire payload for the decision union -- the platform may parse or re-emit it,
#: but it must never invent free text.
SCRIPTED_DECISION: dict[str, Any] = {
    "kind": "action_proposal",
    "headline": "Offer a 10% discount on ORD-1",
    "capability_id": "apply_discount",
    "arguments": {"order_id": ORDER_ID, "percent": DISCOUNT_PERCENT},
}

PREREQUISITES_MESSAGE = """\
DEMO BLOCKED: prerequisites not implemented.
  First gap: {gap}

The capstone is built in three stages; this demo completes when all three exist:
  1. agentlab/capstone/decisions.py  parse_decision / decision_to_wire / enforce_presentation_budgets
  2. agentlab/capstone/catalogue.py  CapabilityCatalogue.merge / resolve / list_for_tenant
  3. agentlab/capstone/platform.py   action_digest + submit_goal / propose_action / approve / execute

Check your progress:  .\\.venv\\Scripts\\python.exe -m pytest tests/week09 -m week -q
                      (macOS / Linux: uv run pytest tests/week09 -m week -q)
Lab brief:            labs/week09-capstone/README.md
"""


def build_catalogue() -> CapabilityCatalogue:
    """Two declaration sources: connectors first, published assets second (they win)."""
    connector_declarations = [
        CapabilityDefinition(
            id="search_orders",
            description="Search orders by customer or status.",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
            risk_level="low",
            is_write=False,
            approval_required=False,
            source="connector:orders",
        ),
        CapabilityDefinition(
            id="apply_discount",
            description="Apply a discount to an order (connector draft).",
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "percent": {"type": "number"},
                },
                "required": ["order_id", "percent"],
                "additionalProperties": False,
            },
            risk_level="high",
            is_write=True,
            approval_required=True,
            source="connector:orders",
        ),
    ]
    published_assets = [
        CapabilityDefinition(
            id="apply_discount",
            description="Apply a discount to an order. Maximum 15%, manager approval above 10%.",
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "percent": {"type": "number"},
                },
                "required": ["order_id", "percent"],
                "additionalProperties": False,
            },
            risk_level="high",
            is_write=True,
            approval_required=True,
            tenant_ids=None,
            version="3",
            source="published",
        )
    ]
    return CapabilityCatalogue.merge(connector_declarations, published_assets)


def build_tools() -> ToolRegistry:
    """Local simulations; the platform executes capabilities through this registry."""
    registry = ToolRegistry()

    @registry.add(
        name="search_orders",
        description="Search orders by customer or status.",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    )
    def search_orders(arguments: dict[str, Any]) -> dict[str, Any]:
        return {"query": arguments["query"], "orders": [{"order_id": ORDER_ID, "total": 1200}]}

    @registry.add(
        name="apply_discount",
        description="Apply a discount to an order (simulated write).",
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}, "percent": {"type": "number"}},
            "required": ["order_id", "percent"],
            "additionalProperties": False,
        },
        is_write=True,
    )
    def apply_discount(arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "order_id": arguments["order_id"],
            "percent": arguments["percent"],
            "status": "applied",
        }

    return registry


def run(platform: CapstonePlatform) -> None:
    """Drive the lifecycle, printing each stage as it completes."""
    request = GoalRequest(
        goal="Discount order ORD-1 by 10% to close the deal", tenant_id=TENANT, actor_id=ACTOR
    )

    print("0. catalogue")
    for definition in platform.catalogue.list_for_tenant(TENANT):
        approval = "approval required" if definition.approval_required else "no approval"
        print(
            f"   - {definition.id:<16} risk={definition.risk_level:<6} write={definition.is_write!s:<5} {approval}"
        )

    decision = platform.submit_goal(request)
    print(f"\n1. decision    kind={decision.kind!r}  headline={decision.headline!r}")
    print(f"   next_moves={list(decision.next_moves)}")
    if decision.kind != "action_proposal":
        raise SystemExit(
            f"demo expected an action_proposal, got {decision.kind!r}; "
            "check submit_goal's mock-provider handling"
        )

    proposal = platform.propose_action(
        request, capability_id="apply_discount", arguments={"order_id": ORDER_ID, "percent": DISCOUNT_PERCENT}
    )
    print(f"\n2. proposal    id={proposal.proposal_id}  status={proposal.status}")
    print(f"   action_hash={proposal.action_hash[:16]}...  expires_at={proposal.expires_at.isoformat()}")

    approval = platform.approve(proposal.proposal_id, approver_id=APPROVER, approved=True)
    print(
        f"\n3. approval    id={approval.approval_id}  approver={approval.approver_id}  approved={approval.approved}"
    )

    receipt = platform.execute(proposal.proposal_id, approval_id=approval.approval_id)
    print(
        f"\n4. execution   status={receipt.status}  capability={receipt.capability_id}  audit_seq={receipt.audit_seq}"
    )
    print(f"   detail={receipt.detail}")

    rows = platform.audit_trail()
    print(f"\n5. audit trail ({len(rows)} append-only rows)")
    for row in rows:
        print(f"   {row.seq:>3}  {row.event:<18} actor={row.actor_id:<12} tenant={row.tenant_id}")

    print("\nDEMO COMPLETE: goal -> decision -> proposal -> approval -> execution -> audit, offline.")


def main() -> int:
    print("Mini-SendOS capstone demo -- offline, mock provider\n")
    try:
        catalogue = build_catalogue()
        registry = build_tools()
        provider = MockProvider([text_turn(json.dumps(SCRIPTED_DECISION))])
        platform = CapstonePlatform(provider=provider, tools=registry, catalogue=catalogue)
        run(platform)
    except NotImplementedError as exc:
        print(PREREQUISITES_MESSAGE.format(gap=exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
