"""Tests for the governed capability catalogue (week 9)."""

from __future__ import annotations

from typing import Any, cast

import pytest
from agentlab.capstone.catalogue import (
    CapabilityCatalogue,
    CapabilityDefinition,
    CapabilityNotAvailable,
    CatalogueError,
)
from agentlab.errors import AgentError

pytestmark = pytest.mark.week


def cap(capability_id: str = "search_orders", **overrides: Any) -> CapabilityDefinition:
    """A valid low-risk read capability, with overrides."""
    fields: dict[str, Any] = {
        "id": capability_id,
        "description": "Search orders by customer or status",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
        "risk_level": "low",
        "is_write": False,
        "approval_required": False,
    }
    fields.update(overrides)
    return CapabilityDefinition(**fields)


def merged(
    connectors: list[CapabilityDefinition] | None = None,
    published: list[CapabilityDefinition] | None = None,
) -> CapabilityCatalogue:
    return CapabilityCatalogue.merge(connectors or [], published or [])


def test_merge_combines_both_sources_in_sorted_order() -> None:
    catalogue = merged([cap("zebra_report"), cap("alpha_report")], [cap("middle_report")])
    assert len(catalogue) == 3
    assert catalogue.ids() == ("alpha_report", "middle_report", "zebra_report")


def test_published_definition_wins_on_id_conflict() -> None:
    connector = cap("apply_discount", description="Connector copy", risk_level="low")
    published = cap(
        "apply_discount",
        description="Published, approved copy",
        risk_level="high",
        is_write=True,
        approval_required=True,
        source="published",
    )
    catalogue = merged([connector], [published])
    resolved = catalogue.resolve("apply_discount", "acme")
    assert resolved.description == "Published, approved copy"
    assert resolved.risk_level == "high"
    assert resolved.is_write is True
    assert resolved.source == "published"


def test_duplicate_id_within_connector_source_is_rejected() -> None:
    with pytest.raises(CatalogueError) as caught:
        merged([cap("search_orders"), cap("search_orders")])
    assert "search_orders" in str(caught.value)


def test_duplicate_id_within_published_source_is_rejected() -> None:
    with pytest.raises(CatalogueError):
        merged(published=[cap("search_orders"), cap("search_orders")])


def test_write_capability_without_approval_fails_closed() -> None:
    with pytest.raises(CatalogueError) as caught:
        merged([cap("apply_discount", is_write=True, approval_required=False)])
    assert "approval" in str(caught.value).lower()


def test_write_capability_with_approval_is_accepted() -> None:
    catalogue = merged([cap("apply_discount", is_write=True, approval_required=True)])
    assert catalogue.resolve("apply_discount", "acme").approval_required is True


def test_invalid_capability_id_is_rejected() -> None:
    for bad_id in ("Search Orders", "", "search-orders", "1search"):
        with pytest.raises(CatalogueError):
            merged([cap(bad_id)])


def test_input_schema_must_be_an_object_schema() -> None:
    with pytest.raises(CatalogueError):
        merged([cap("search_orders", input_schema={"type": "array"})])


def test_invalid_risk_level_is_rejected() -> None:
    with pytest.raises(CatalogueError):
        merged([cap("search_orders", risk_level=cast(Any, "critical"))])


def test_empty_tenant_scope_is_rejected() -> None:
    with pytest.raises(CatalogueError):
        merged([cap("search_orders", tenant_ids=frozenset())])


def test_resolve_returns_a_universal_capability_for_any_tenant() -> None:
    catalogue = merged([cap("search_orders")])
    assert catalogue.resolve("search_orders", "acme").id == "search_orders"
    assert catalogue.resolve("search_orders", "globex").id == "search_orders"


def test_resolve_honours_tenant_scope() -> None:
    catalogue = merged(published=[cap("beta_pricing", tenant_ids=frozenset({"beta"}))])
    assert catalogue.resolve("beta_pricing", "beta").id == "beta_pricing"
    with pytest.raises(CapabilityNotAvailable):
        catalogue.resolve("beta_pricing", "acme")


def test_denied_and_unknown_share_the_same_error_shape() -> None:
    catalogue = merged(published=[cap("beta_pricing", tenant_ids=frozenset({"beta"}))])
    with pytest.raises(CapabilityNotAvailable) as denied:
        catalogue.resolve("beta_pricing", "acme")
    with pytest.raises(CapabilityNotAvailable) as unknown:
        catalogue.resolve("ghost_capability", "acme")
    assert isinstance(denied.value, AgentError)
    assert str(denied.value).replace("beta_pricing", "ghost_capability") == str(unknown.value)


def test_resolve_with_empty_tenant_id_fails_closed() -> None:
    catalogue = merged([cap("search_orders")])
    with pytest.raises(CapabilityNotAvailable):
        catalogue.resolve("search_orders", "")


def test_list_for_tenant_is_sorted_and_tenant_filtered() -> None:
    catalogue = merged(
        [cap("zebra_report"), cap("alpha_report"), cap("beta_pricing", tenant_ids=frozenset({"beta"}))]
    )
    assert [definition.id for definition in catalogue.list_for_tenant("acme")] == [
        "alpha_report",
        "zebra_report",
    ]
    assert [definition.id for definition in catalogue.list_for_tenant("beta")] == [
        "alpha_report",
        "beta_pricing",
        "zebra_report",
    ]
    assert catalogue.list_for_tenant("") == ()


def test_merge_is_order_independent() -> None:
    connector = [cap("a_read"), cap("b_read")]
    published = [cap("c_read")]
    first = merged(connector, published)
    second = merged(list(reversed(connector)), list(reversed(published)))
    assert first.ids() == second.ids()
    assert len(first) == len(second) == 3
