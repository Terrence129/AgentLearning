"""Budgets: the cheapest reliability feature you will ever ship.

An unbounded agent loop is a denial-of-service attack on your own wallet. Every
production agent needs at least three ceilings:

- steps        (loop iterations)
- tokens       (context growth)
- money        (provider spend)

This module keeps the accumulation state and the enforcement separate: callers
``charge()`` for each model call, then call ``assert_ok()`` at the top of every
loop iteration. Enforcement belongs in the loop, not in the provider.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentlab.errors import BudgetExceeded
from agentlab.pricing import ModelPrice, estimate_cost, price_for
from agentlab.types import Usage


@dataclass(slots=True)
class Budget:
    max_usd: float | None = None
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    max_steps: int | None = None

    used_usd: float = 0.0
    used_input_tokens: int = 0
    used_output_tokens: int = 0
    steps: int = 0

    #: Models whose price we did not know. Reported at the end of a run.
    unknown_priced_models: set[str] | None = None

    def __post_init__(self) -> None:
        if self.unknown_priced_models is None:
            self.unknown_priced_models = set()

    # -- mutation ----------------------------------------------------------

    def charge(self, model: str, usage: Usage, prices: dict[str, ModelPrice] | None = None) -> float:
        """Account for one model call. Returns this call's estimated USD."""
        if price_for(model, prices) is None:
            assert self.unknown_priced_models is not None
            self.unknown_priced_models.add(model)
        cost = estimate_cost(model, usage, prices)
        self.used_usd += cost
        self.used_input_tokens += usage.input_tokens
        self.used_output_tokens += usage.output_tokens
        return cost

    def add_step(self, n: int = 1) -> None:
        self.steps += n

    # -- enforcement -------------------------------------------------------

    def assert_ok(self, *, what: str = "run", buffer_pct: float = 0.0) -> None:
        """Raise ``BudgetExceeded`` if any ceiling is reached.

        ``buffer_pct`` lets a caller stop slightly early: a planner that knows
        the next call costs ~10% of the ceiling should not spend 99.9% first.
        """
        if self.max_usd is not None and self.used_usd >= self.max_usd * (1 - buffer_pct):
            raise BudgetExceeded(
                f"{what} exceeded its USD budget: spent ${self.used_usd:.4f} of ${self.max_usd:.2f}"
            )
        if self.max_input_tokens is not None and self.used_input_tokens >= self.max_input_tokens:
            raise BudgetExceeded(
                f"{what} exceeded its input-token budget: {self.used_input_tokens} of {self.max_input_tokens}"
            )
        if self.max_output_tokens is not None and self.used_output_tokens >= self.max_output_tokens:
            raise BudgetExceeded(
                f"{what} exceeded its output-token budget: "
                f"{self.used_output_tokens} of {self.max_output_tokens}"
            )
        if self.max_steps is not None and self.steps >= self.max_steps:
            raise BudgetExceeded(f"{what} exceeded its step budget: {self.steps} of {self.max_steps}")

    @property
    def remaining_usd(self) -> float | None:
        if self.max_usd is None:
            return None
        return max(0.0, self.max_usd - self.used_usd)

    def summary(self) -> dict[str, float | int | list[str] | None]:
        return {
            "steps": self.steps,
            "used_usd": round(self.used_usd, 6),
            "used_input_tokens": self.used_input_tokens,
            "used_output_tokens": self.used_output_tokens,
            "max_usd": self.max_usd,
            "max_steps": self.max_steps,
            "unknown_priced_models": sorted(self.unknown_priced_models or ()),
        }
