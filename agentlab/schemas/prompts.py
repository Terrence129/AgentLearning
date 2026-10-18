"""Versioned prompt templates -- YOUR WEEK 3 BUILD.

Why this exists: a prompt is code, but it usually lives as a string literal with
no identity. When behaviour regresses you cannot answer "which prompt changed?",
cannot roll back one asset, and cannot review a prompt edit as a diff. A prompt
asset fixes that with three cheap pieces of metadata -- ``id``, ``version`` and a
content ``hash`` -- and a registry that keeps every version instead of silently
overwriting the previous one.

This module is deliberately dumb: string formatting plus a stable hash. No
templating language, no vendor SDK, no prompt-caching magic.

Read first: ``docs/research/01-agent-architecture-sota.md`` §3.2 (system prompt
"altitude") and ``docs/research/05-sendos-concept-map.md`` §2.5 (versioned asset
registry / prompt versioning).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

#: Valid versions are dot-separated integers: ``"1"``, ``"1.0"``, ``"2.10.3"``.
_VERSION_RE = re.compile(r"^\d+(\.\d+)*$")


class PromptRenderError(ValueError):
    """A prompt template was rendered before all of its placeholders had values."""


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """One immutable, versioned prompt asset.

    ``id`` names the asset (``"structured-output"``); ``version`` is a
    dot-separated integer sequence; ``template`` is a ``str.format``-style string
    whose placeholders are named fields (``{schema_name}``). Editing history is
    forbidden by design: change the ``version`` instead of the old object.
    """

    id: str
    version: str
    template: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("prompt id must not be empty")
        if not self.template.strip():
            raise ValueError("prompt template must not be empty")

    def render(self, **values: Any) -> str:
        """Render the template with ``values``.

        Uses ``str.format`` semantics: ``{name}`` is replaced by ``values["name"]``
        and literal braces are written ``{{`` / ``}}``.

        Policy:
        - every placeholder must be supplied: a missing name raises
          ``PromptRenderError`` naming it (a silently empty prompt is a bug);
        - extra values are ignored, so a caller can pass a shared context dict;
        - two versions with the same ``id`` and ``template`` render identically.
        """
        raise NotImplementedError("Week 3 lab: implement PromptTemplate.render")

    @property
    def hash(self) -> str:
        """Stable content hash of this asset as 64 lowercase hex characters.

        ``sha256(id + "\\x00" + template)``. ``version`` is excluded on purpose:
        an identical template under a new version has identical behaviour, and
        detecting a no-op version bump is useful. Two different ids must never
        share a hash for the same text.
        """
        raise NotImplementedError("Week 3 lab: implement PromptTemplate.hash")


class PromptRegistry:
    """An in-memory, append-only collection of prompt versions keyed by ``id``.

    The registry is the reviewable history: old versions stay fetchable, the
    latest is resolved deterministically by numeric version order, and a
    same-``id``/same-``version`` re-registration is rejected rather than
    silently replacing history.
    """

    def __init__(self) -> None:
        self._templates: dict[str, dict[str, PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> PromptTemplate:
        """Add ``template`` and return it.

        Policy:
        - ``template.version`` must match ``_VERSION_RE`` (dot-separated
          integers); otherwise raise ``ValueError``;
        - registering the same ``id`` + ``version`` twice raises ``ValueError``
          (append a new version instead of overwriting);
        - registration is otherwise append-only.
        """
        raise NotImplementedError("Week 3 lab: implement PromptRegistry.register")

    def get(self, prompt_id: str, version: str | None = None) -> PromptTemplate:
        """Return the requested version, or the latest version when ``version`` is None.

        Latest means the greatest numeric version tuple (so ``"1.10"`` beats
        ``"1.9"``). Unknown ``prompt_id`` or unknown ``version`` raises
        ``KeyError`` whose message lists what is available.
        """
        raise NotImplementedError("Week 3 lab: implement PromptRegistry.get")

    def versions(self, prompt_id: str) -> list[str]:
        """All registered versions for ``prompt_id``, ascending numerically.

        Unknown ``prompt_id`` raises ``KeyError``.
        """
        raise NotImplementedError("Week 3 lab: implement PromptRegistry.versions")

    def render(self, prompt_id: str, *, version: str | None = None, **values: Any) -> str:
        """Render (the latest by default) ``prompt_id`` with ``values``."""
        raise NotImplementedError("Week 3 lab: implement PromptRegistry.render")

    def has(self, prompt_id: str) -> bool:
        """True when at least one version of ``prompt_id`` is registered."""
        raise NotImplementedError("Week 3 lab: implement PromptRegistry.has")


def version_key(version: str) -> tuple[int, ...]:
    """Numeric sort key for a dot-separated version string (e.g. ``"1.10" -> (1, 10)``)."""
    return tuple(int(part) for part in version.split("."))
