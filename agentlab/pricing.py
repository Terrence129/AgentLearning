"""Token pricing, so cost is a first-class number instead of a surprise invoice.

IMPORTANT: the table below is a *snapshot for learning*. Providers change prices
frequently. Treat these numbers as editable defaults -- override them per run and
record the price source/date when you report cost results.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentlab.types import Usage


@dataclass(frozen=True, slots=True)
class ModelPrice:
    """USD per 1,000,000 tokens."""

    input_per_mtok: float
    output_per_mtok: float
    cached_input_per_mtok: float | None = None


#: Keyed by model-name *prefix*; the longest matching prefix wins.
#: Snapshot taken 2026-10 -- verify at the provider's pricing page before quoting.
DEFAULT_PRICES: dict[str, ModelPrice] = {
    "gpt-4.1-nano": ModelPrice(0.10, 0.40, 0.025),
    "gpt-4.1-mini": ModelPrice(0.40, 1.60, 0.10),
    "gpt-4.1": ModelPrice(2.00, 8.00, 0.50),
    "gpt-4o-mini": ModelPrice(0.15, 0.60, 0.075),
    "gpt-4o": ModelPrice(2.50, 10.00, 1.25),
    "deepseek-chat": ModelPrice(0.27, 1.10, 0.07),
    "deepseek-reasoner": ModelPrice(0.55, 2.19, 0.14),
    "qwen-plus": ModelPrice(0.40, 1.20, None),
    "qwen-turbo": ModelPrice(0.05, 0.20, None),
    "mock-1": ModelPrice(0.0, 0.0, 0.0),
}


def price_for(model: str, prices: dict[str, ModelPrice] | None = None) -> ModelPrice | None:
    """Longest-prefix lookup. Returns ``None`` for unknown models."""
    table = prices or DEFAULT_PRICES
    best: ModelPrice | None = None
    best_len = -1
    for key, price in table.items():
        if model.startswith(key) and len(key) > best_len:
            best, best_len = price, len(key)
    return best


def estimate_cost(model: str, usage: Usage, prices: dict[str, ModelPrice] | None = None) -> float:
    """Estimate USD for one call. Unknown models cost 0.0 (and are reported as unknown)."""
    price = price_for(model, prices)
    if price is None:
        return 0.0
    cached = min(usage.cached_input_tokens, usage.input_tokens)
    uncached = usage.input_tokens - cached
    cost = (uncached / 1_000_000) * price.input_per_mtok
    if price.cached_input_per_mtok is not None:
        cost += (cached / 1_000_000) * price.cached_input_per_mtok
    else:
        cost += (cached / 1_000_000) * price.input_per_mtok
    cost += (usage.output_tokens / 1_000_000) * price.output_per_mtok
    return cost
