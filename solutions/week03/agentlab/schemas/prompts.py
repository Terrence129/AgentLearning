"""Reference solution -- week 3: prompt templates as versioned assets.

The two design choices worth noting:

- rendering is strict about *missing* placeholders (a missing instruction is a
  silent outage) and ignores extra values (callers routinely pass a context
  dict), which matches how template systems behave in production;
- the hash deliberately excludes the version, so a no-op version bump has the
  same hash and a real content change is detectable as a diff.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

_VERSION_RE = re.compile(r"^\d+(\.\d+)*$")


class PromptRenderError(ValueError):
    """A prompt template was rendered before all of its placeholders had values."""


class _StrictFormatMap(dict[str, Any]):
    """``str.format_map`` mapping that fails loudly on a missing placeholder."""

    def __missing__(self, key: str) -> str:
        raise PromptRenderError(f"missing value for placeholder {key!r}")


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """One immutable, versioned prompt asset."""

    id: str
    version: str
    template: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("prompt id must not be empty")
        if not self.template.strip():
            raise ValueError("prompt template must not be empty")

    def render(self, **values: Any) -> str:
        """Render the template with ``values`` (strict about missing names)."""
        try:
            return self.template.format_map(_StrictFormatMap(values))
        except (IndexError, KeyError) as exc:
            raise PromptRenderError(
                f"prompt {self.id!r} v{self.version} must use named placeholders, not positional ones"
            ) from exc

    @property
    def hash(self) -> str:
        """``sha256(id + NUL + template)`` as 64 lowercase hex characters."""
        payload = f"{self.id}\x00{self.template}".encode()
        return hashlib.sha256(payload).hexdigest()


class PromptRegistry:
    """An in-memory, append-only collection of prompt versions keyed by ``id``."""

    def __init__(self) -> None:
        self._templates: dict[str, dict[str, PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> PromptTemplate:
        """Add ``template``; reject duplicate id+version and non-numeric versions."""
        if not _VERSION_RE.match(template.version):
            raise ValueError(
                f"prompt version {template.version!r} must be dot-separated integers (e.g. '1.0.0')"
            )
        versions = self._templates.setdefault(template.id, {})
        if template.version in versions:
            raise ValueError(
                f"prompt {template.id!r} version {template.version!r} is already registered; "
                "bump the version instead of overwriting history"
            )
        versions[template.version] = template
        return template

    def get(self, prompt_id: str, version: str | None = None) -> PromptTemplate:
        """Return a specific version, or the numerically greatest when ``version`` is None."""
        if prompt_id not in self._templates:
            available = ", ".join(sorted(self._templates)) or "none"
            raise KeyError(f"unknown prompt id {prompt_id!r}; registered ids: {available}")
        versions = self._templates[prompt_id]
        if version is None:
            version = max(versions, key=version_key)
        if version not in versions:
            available = ", ".join(sorted(versions, key=version_key)) or "none"
            raise KeyError(f"unknown version {version!r} for prompt {prompt_id!r}; available: {available}")
        return versions[version]

    def versions(self, prompt_id: str) -> list[str]:
        """All versions for ``prompt_id``, ascending numerically."""
        if prompt_id not in self._templates:
            raise KeyError(f"unknown prompt id {prompt_id!r}")
        return sorted(self._templates[prompt_id], key=version_key)

    def render(self, prompt_id: str, *, version: str | None = None, **values: Any) -> str:
        """Render (the latest by default) ``prompt_id`` with ``values``."""
        return self.get(prompt_id, version).render(**values)

    def has(self, prompt_id: str) -> bool:
        """True when at least one version of ``prompt_id`` is registered."""
        return prompt_id in self._templates


def version_key(version: str) -> tuple[int, ...]:
    """Numeric sort key for a dot-separated version string."""
    return tuple(int(part) for part in version.split("."))
