"""Capability catalogue: governed tool declarations (week 9).

Why this exists
---------------
A tool the model can see is a permission the business granted. The catalogue is
the single place that decides which capabilities exist, which tenant may see
them, whether they are reads or writes, and whether a write needs a human. It is
SendOS's ``CapabilityCatalogueAssembler`` in miniature: three declaration
sources merged with **published-wins** (here two: connector manifests and
published assets), because "the platform said so" must beat "a connector claimed
so".

The rules (encoded in the tests, not just here)
-----------------------------------------------
1. **Merge by id, published wins.** The two sources are merged by ``id``. On a
   conflict the *published* definition is used as a whole -- fields are never
   mixed between sources.
2. **Fail closed on ambiguity.** Duplicate ids *within one source* are an error:
   if two declarations claim the same id, neither can be trusted.
3. **Validate at the boundary.** Ids are snake_case; ``input_schema`` is a JSON
   Schema object; ``risk_level`` is one of ``RISK_LEVELS``.
4. **Writes require approval.** A definition with ``is_write=True`` and
   ``approval_required=False`` is rejected: a write capability may never be
   auto-approved by omission. (Low-risk writes may still require approval; the
   rule only forbids accidentally forgetting it.)
5. **Tenant scope is explicit.** ``tenant_ids=None`` means every tenant may use
   it; a ``frozenset`` limits it to those tenants; an *empty* set is rejected
   because it can never be used intentionally.
6. **No cross-tenant oracle.** Asking for a capability that exists for another
   tenant must fail with the *same* error and message as asking for one that does
   not exist. The error must not reveal whether the id exists elsewhere.
7. **Deterministic order.** ``ids()`` and ``list_for_tenant()`` return sorted
   tuples so prompts, diffs and tests are stable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Literal

from agentlab.errors import AgentError

#: Risk levels a capability may declare. ``high`` always needs a human.
RiskLevel = Literal["low", "medium", "high"]
RISK_LEVELS: tuple[str, ...] = ("low", "medium", "high")


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    """One declared capability, from one declaration source.

    Fields
    ------
    id: snake_case identifier (``^[a-z][a-z0-9_]*$``), unique per source.
    description: what the capability does, shown to the model; non-empty.
    input_schema: JSON Schema object for the arguments (``type: object``).
    risk_level: one of ``RISK_LEVELS``.
    is_write: True when invoking it changes state outside the run.
    approval_required: True when a human must approve before execution. Must be
        True whenever ``is_write`` is True (fail closed).
    tenant_ids: ``None`` = all tenants; otherwise the tenants allowed to use it.
    version: published asset version; useful in audit rows and pins.
    source: free-form origin label (``"connector"``, ``"published"``, a connector
        name). Carried for diagnostics; not part of merge precedence.
    """

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
    """The capability is unknown *or* not available to this tenant.

    The two cases deliberately share one error type and one message shape; see
    rule 6 in the module docstring.
    """


class CapabilityCatalogue:
    """An immutable, validated view of the merged capability declarations."""

    @classmethod
    def merge(
        cls,
        connector_declarations: Iterable[CapabilityDefinition],
        published_assets: Iterable[CapabilityDefinition],
    ) -> CapabilityCatalogue:
        """Validate both sources and merge them, published-wins, into a catalogue.

        Contract
        --------
        - Validate every definition in both sources (rules 3, 4, 5).
        - Duplicate ids within one source raise ``CatalogueError`` naming the id
          and the source (rule 2).
        - A published definition wins over a connector definition with the same
          id (rule 1); the connector copy is discarded entirely.
        - The result is independent of input order: same inputs => same catalogue.
        - Never mutates the definitions; ``CapabilityDefinition`` is frozen.
        """
        raise NotImplementedError("Week 9 capstone: implement CapabilityCatalogue.merge")

    def resolve(self, capability_id: str, tenant_id: str) -> CapabilityDefinition:
        """Return the definition if this tenant may use it, else raise.

        Contract
        --------
        - Unknown ``capability_id`` and "exists but not for this tenant" both
          raise ``CapabilityNotAvailable(f"capability {capability_id!r} is not available")``
          -- same type, same message shape, no cross-tenant oracle (rule 6).
        - An empty ``tenant_id`` is treated as unavailable (fail closed).
        """
        raise NotImplementedError("Week 9 capstone: implement CapabilityCatalogue.resolve")

    def list_for_tenant(self, tenant_id: str) -> tuple[CapabilityDefinition, ...]:
        """Return this tenant's capabilities, sorted by ``id`` (rule 7).

        Universal capabilities (``tenant_ids is None``) and tenant-scoped ones
        both appear. An empty tenant gets an empty tuple.
        """
        raise NotImplementedError("Week 9 capstone: implement CapabilityCatalogue.list_for_tenant")

    def ids(self) -> tuple[str, ...]:
        """Return every capability id in the catalogue, sorted (rule 7)."""
        raise NotImplementedError("Week 9 capstone: implement CapabilityCatalogue.ids")

    def __len__(self) -> int:
        """Number of capabilities in the merged catalogue."""
        raise NotImplementedError("Week 9 capstone: implement CapabilityCatalogue.__len__")
