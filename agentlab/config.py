"""Configuration loaded from environment variables (and ``.env``).

Deliberately hand-rolled instead of pydantic-settings: you should be able to
read this file and know exactly where every value comes from. The same
principle as the rest of the course -- understand the abstraction before you
adopt one.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from agentlab.errors import ConfigError

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"

#: Provider names that use the OpenAI-compatible chat-completions wire format.
OPENAI_COMPATIBLE = frozenset({"openai", "deepseek", "qwen", "moonshot", "compat"})


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Everything needed to call one provider."""

    name: str
    api_key: str
    base_url: str
    model: str
    api_style: str = "openai-compatible"

    def __repr__(self) -> str:  # never print secrets into logs or trace files
        masked = f"{self.api_key[:6]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
        return f"ProviderConfig(name={self.name!r}, model={self.model!r}, base_url={self.base_url!r}, api_key={masked!r})"


def _get(env: Mapping[str, str], *names: str, default: str | None = None) -> str | None:
    for name in names:
        value = env.get(name)
        if value is not None and value.strip():
            return value.strip()
    return default


#: Markers that appear in sample keys (``sk-...``, ``<your-key>``, ...) but never
#: in a real key. Accepting them silently produces a confusing 401 instead of a
#: clear "you have not added your key yet" error.
_PLACEHOLDER_MARKERS = ("...", "<", "your-", "changeme", "replace-me", "xxxx")


def is_placeholder_secret(value: str) -> bool:
    """True when a configured secret is obviously a sample value, not a real key."""
    text = value.strip()
    if not text:
        return True
    if len(text) < 12:
        return True
    lowered = text.lower()
    return any(marker in lowered for marker in _PLACEHOLDER_MARKERS)


@dataclass(frozen=True, slots=True)
class Settings:
    """Resolved process configuration."""

    default_provider: str
    providers: Mapping[str, ProviderConfig]
    data_dir: Path
    trace_dir: Path
    run_budget_usd: float
    allow_network: bool
    env_file: Path | None = field(default=None, compare=False)
    #: Providers whose key was present but looked like a sample value.
    skipped_providers: tuple[str, ...] = ()

    # -- construction ------------------------------------------------------

    @classmethod
    def from_env(
        cls,
        env_file: str | Path = ".env",
        env: Mapping[str, str] | None = None,
    ) -> Settings:
        """Load settings from ``env`` (defaults to ``os.environ``).

        ``.env`` is loaded first without overriding real environment variables,
        so CI secrets always win over a developer's local file.
        """
        path = Path(env_file)
        loaded_from: Path | None = None
        if env is None:
            if path.exists():
                load_dotenv(path, override=False)
                loaded_from = path
            env = os.environ

        providers: dict[str, ProviderConfig] = {}
        skipped: list[str] = []
        openai_key = _get(env, "OPENAI_API_KEY")
        if openai_key:
            if is_placeholder_secret(openai_key):
                skipped.append("openai")
            else:
                providers["openai"] = ProviderConfig(
                    name="openai",
                    api_key=openai_key,
                    base_url=_get(env, "OPENAI_BASE_URL", default=DEFAULT_OPENAI_BASE_URL)
                    or DEFAULT_OPENAI_BASE_URL,
                    model=_get(env, "OPENAI_MODEL", default="gpt-4.1-mini") or "gpt-4.1-mini",
                )

        deepseek_key = _get(env, "DEEPSEEK_API_KEY")
        if deepseek_key:
            if is_placeholder_secret(deepseek_key):
                skipped.append("deepseek")
            else:
                providers["deepseek"] = ProviderConfig(
                    name="deepseek",
                    api_key=deepseek_key,
                    base_url=_get(env, "DEEPSEEK_BASE_URL", default=DEFAULT_DEEPSEEK_BASE_URL)
                    or DEFAULT_DEEPSEEK_BASE_URL,
                    model=_get(env, "DEEPSEEK_MODEL", default="deepseek-chat") or "deepseek-chat",
                )

        compat_key = _get(env, "COMPAT_API_KEY")
        if compat_key:
            name = (_get(env, "COMPAT_NAME", default="compat") or "compat").lower()
            if is_placeholder_secret(compat_key):
                skipped.append(name)
            else:
                providers[name] = ProviderConfig(
                    name=name,
                    api_key=compat_key,
                    base_url=_get(env, "COMPAT_BASE_URL", default="") or "",
                    model=_get(env, "COMPAT_MODEL", default="") or "",
                )

        return cls(
            default_provider=(_get(env, "DEFAULT_PROVIDER", default="deepseek") or "deepseek").lower(),
            providers=providers,
            data_dir=Path(_get(env, "AGENTLAB_DATA_DIR", default="./data") or "./data"),
            trace_dir=Path(_get(env, "AGENTLAB_TRACE_DIR", default="./traces") or "./traces"),
            run_budget_usd=float(_get(env, "AGENTLAB_RUN_BUDGET_USD", default="0.50") or "0.50"),
            allow_network=(_get(env, "AGENTLAB_ALLOW_NETWORK", default="0") or "0").lower()
            in {"1", "true", "yes"},
            env_file=loaded_from,
            skipped_providers=tuple(skipped),
        )

    # -- access ------------------------------------------------------------

    def provider(self, name: str | None = None) -> ProviderConfig:
        """Return a provider config or raise a helpful ``ConfigError``."""
        target = (name or self.default_provider).lower()
        if target == "mock":
            raise ConfigError(
                "The 'mock' provider is only for tests. Construct agentlab.testing.MockProvider directly."
            )
        if target not in self.providers:
            available = ", ".join(sorted(self.providers)) or "none"
            if target in self.skipped_providers:
                raise ConfigError(
                    f"Provider {target!r} still has a placeholder key in .env "
                    "(for example 'sk-...'). Replace it with a real API key, then retry."
                )
            raise ConfigError(
                f"Provider {target!r} is not configured. Available: {available}. "
                "Copy .env.example to .env and add the key for the provider you want."
            )
        return self.providers[target]

    @property
    def has_any_provider(self) -> bool:
        return bool(self.providers)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.trace_dir.mkdir(parents=True, exist_ok=True)
