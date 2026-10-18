"""Reference solution for ``agentlab.capstone.catalogue`` (week 9).

Copy into place with::

    Copy-Item solutions/week09/* . -Recurse -Force
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from agentlab.errors import AgentError

RiskLevel = Literal["low", "medium", "high"]
RISK_LEVELS: tuple[str, ...] = ("low", "medium", "high")

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    """One declared capability, from one declaration source."""

    id: str
    description: str
    input_schema: dict[str, Any]
    risk_level: RiskLevel
    is_write: bool
    approval_required: bool
    tenant_ids: frozenset[str] | None = None
    version: str = "1"
    source: str = "connector"


class CatalogueError(AgentError):
    """A declaration is invalid or ambiguous; the catalogue refuses to load it."""


class CapabilityNotAvailable(CatalogueError):
    """The capability is unknown *or* not available to this tenant."""


def _validate(definition: CapabilityDefinition) -> None:
    """Raise ``CatalogueError`` if a declaration violates the catalogue rules."""
    if not isinstance(definition.id, str) or not _ID_RE.match(definition.id):
        raise CatalogueError(f"capability id {definition.id!r} must be snake_case (^[a-z][a-z0-9_]*$)")
    if not isinstance(definition.description, str) or not definition.description.strip():
        raise CatalogueError(f"capability {definition.id!r} must have a non-empty description")
    if not isinstance(definition.input_schema, Mapping) or definition.input_schema.get("type") != "object":
        raise CatalogueError(
            f"capability {definition.id!r} input_schema must be a JSON Schema object (type: object)"
        )
    if definition.risk_level not in RISK_LEVELS:
        raise CatalogueError(
            f"capability {definition.id!r} risk_level must be one of: {', '.join(RISK_LEVELS)}"
        )
    if not isinstance(definition.is_write, bool) or not isinstance(definition.approval_required, bool):
        raise CatalogueError(f"capability {definition.id!r} is_write/approval_required must be booleans")
    if definition.is_write and not definition.approval_required:
        raise CatalogueError(
            f"write capability {definition.id!r} must set approval_required=True (fail closed)"
        )
    if definition.tenant_ids is not None:
        scoped = isinstance(definition.tenant_ids, (set, frozenset))
        if not scoped or not definition.tenant_ids:
            raise CatalogueError(
                f"capability {definition.id!r} tenant_ids must be None or a non-empty set of tenants"
            )
        if any(not isinstance(tenant, str) or not tenant.strip() for tenant in definition.tenant_ids):
            raise CatalogueError(
                f"capability {definition.id!r} tenant_ids must contain non-empty tenant strings"
            )
    if not isinstance(definition.version, str) or not definition.version.strip():
        raise CatalogueError(f"capability {definition.id!r} version must be a non-empty string")


class CapabilityCatalogue:
    """An immutable, validated view of the merged capability declarations."""

    def __init__(self, definitions: Mapping[str, CapabilityDefinition]) -> None:
        self._definitions: dict[str, CapabilityDefinition] = dict(definitions)

    @classmethod
    def merge(
        cls,
        connector_declarations: Iterable[CapabilityDefinition],
        published_assets: Iterable[CapabilityDefinition],
    ) -> CapabilityCatalogue:
        """Validate both sources and merge them, published-wins, into a catalogue."""
        merged: dict[str, CapabilityDefinition] = {}
        for label, definitions in (
            ("connector", connector_declarations),
            ("published", published_assets),
        ):
            seen: set[str] = set()
            for definition in definitions:
                _validate(definition)
                if definition.id in seen:
                    raise CatalogueError(f"duplicate capability id {definition.id!r} in {label} declarations")
                seen.add(definition.id)
                merged[definition.id] = definition  # published is processed second: it wins
        return cls(merged)

    def resolve(self, capability_id: str, tenant_id: str) -> CapabilityDefinition:
        """Return the definition if this tenant may use it, else raise."""
        definition = self._definitions.get(capability_id)
        available = (
            definition is not None
            and bool(tenant_id)
            and (definition.tenant_ids is None or tenant_id in definition.tenant_ids)
        )
        if not available:
            raise CapabilityNotAvailable(f"capability {capability_id!r} is not available")
        return definition

    def list_for_tenant(self, tenant_id: str) -> tuple[CapabilityDefinition, ...]:
        """Return this tenant's capabilities, sorted by ``id``."""
        if not tenant_id:
            return ()
        return tuple(
            definition
            for _, definition in sorted(self._definitions.items())
            if definition.tenant_ids is None or tenant_id in definition.tenant_ids
        )

    def ids(self) -> tuple[str, ...]:
        """Return every capability id in the catalogue, sorted."""
        return tuple(sorted(self._definitions))

    def __len__(self) -> int:
        """Number of capabilities in the merged catalogue."""
        return len(self._definitions)
