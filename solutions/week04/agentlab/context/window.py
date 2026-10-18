"""Context-window assembly: the budget ledger for a prompt (week 4).

Reference solution. See the starter docstring for the full contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from agentlab.errors import AgentError
from agentlab.types import Message, Role

CHARS_PER_TOKEN = 4
MESSAGE_OVERHEAD_TOKENS = 4


class ContextBudgetError(AgentError):
    """The context policy cannot be satisfied (invalid budget numbers, etc.)."""


class Priority(IntEnum):
    """How strong a claim an item has on the context window (lower = stronger)."""

    PINNED = 0
    TASK_STATE = 1
    RECENT_TURNS = 2
    OBSERVATIONS = 3
    HISTORY = 4


@dataclass(frozen=True, slots=True)
class ContextItem:
    """One candidate piece of context, with its eviction priority."""

    id: str
    content: str
    priority: Priority
    role: Role = "user"
    tool_call_id: str | None = None
    name: str | None = None

    @classmethod
    def pinned_constraint(cls, item_id: str, content: str) -> ContextItem:
        return cls(id=item_id, content=content, priority=Priority.PINNED, role="system")

    @classmethod
    def task_state(cls, item_id: str, content: str) -> ContextItem:
        return cls(id=item_id, content=content, priority=Priority.TASK_STATE, role="system")

    @classmethod
    def turn(cls, item_id: str, role: Role, content: str) -> ContextItem:
        return cls(id=item_id, content=content, priority=Priority.RECENT_TURNS, role=role)

    @classmethod
    def observation(
        cls, item_id: str, content: str, *, tool_call_id: str, name: str | None = None
    ) -> ContextItem:
        return cls(
            id=item_id,
            content=content,
            priority=Priority.OBSERVATIONS,
            role="tool",
            tool_call_id=tool_call_id,
            name=name,
        )

    @classmethod
    def history(cls, item_id: str, role: Role, content: str) -> ContextItem:
        return cls(id=item_id, content=content, priority=Priority.HISTORY, role=role)

    def to_message(self) -> Message:
        if self.role == "tool":
            return Message.tool_result(self.tool_call_id or "", self.content, self.name)
        return Message(role=self.role, content=self.content)


class TokenEstimator:
    """Cheap deterministic token estimate (see starter docstring)."""

    def estimate_text(self, text: str) -> int:
        if not text:
            return 0
        return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN

    def estimate_message(self, item: ContextItem) -> int:
        return self.estimate_text(item.content) + MESSAGE_OVERHEAD_TOKENS


@dataclass(frozen=True, slots=True)
class WindowPolicy:
    """The context budget for one agent call."""

    max_tokens: int
    reserve_output_tokens: int = 0

    @property
    def input_budget(self) -> int:
        if self.max_tokens <= 0:
            raise ContextBudgetError(f"context budget: max_tokens must be positive, got {self.max_tokens}")
        if self.reserve_output_tokens < 0:
            raise ContextBudgetError(
                f"context budget: reserve_output_tokens must be >= 0, got {self.reserve_output_tokens}"
            )
        budget = self.max_tokens - self.reserve_output_tokens
        if budget <= 0:
            raise ContextBudgetError(
                "context budget: reserve_output_tokens="
                f"{self.reserve_output_tokens} leaves no input budget out of "
                f"max_tokens={self.max_tokens}"
            )
        return budget


@dataclass(frozen=True, slots=True)
class AssembledContext:
    """The outcome of one assembly pass."""

    messages: tuple[Message, ...]
    used_tokens: int
    budget_tokens: int
    dropped: tuple[str, ...]
    dropped_tokens: int
    over_budget: bool
    included_ids: tuple[str, ...]


class ContextWindow:
    """Accumulates context items and assembles them under a token budget."""

    def __init__(self, policy: WindowPolicy, estimator: TokenEstimator | None = None) -> None:
        self.policy = policy
        self.estimator = estimator or TokenEstimator()
        self._items: list[ContextItem] = []
        self._ids: set[str] = set()

    def add(self, item: ContextItem) -> None:
        if item.id in self._ids:
            raise ValueError(f"context item id {item.id!r} already added")
        self._ids.add(item.id)
        self._items.append(item)

    def items(self) -> tuple[ContextItem, ...]:
        return tuple(self._items)

    def assemble(self) -> AssembledContext:
        budget = self.policy.input_budget
        costs = {item.id: self.estimator.estimate_message(item) for item in self._items}

        selected: set[str] = set()
        used = 0
        for item in self._items:
            if item.priority is Priority.PINNED:
                selected.add(item.id)
                used += costs[item.id]

        for priority in (
            Priority.TASK_STATE,
            Priority.RECENT_TURNS,
            Priority.OBSERVATIONS,
            Priority.HISTORY,
        ):
            group = [item for item in self._items if item.priority is priority]
            for item in reversed(group):
                if used + costs[item.id] <= budget:
                    selected.add(item.id)
                    used += costs[item.id]

        included = [item for item in self._items if item.id in selected]
        dropped_items = [item for item in self._items if item.id not in selected]
        return AssembledContext(
            messages=tuple(item.to_message() for item in included),
            used_tokens=used,
            budget_tokens=budget,
            dropped=tuple(item.id for item in dropped_items),
            dropped_tokens=sum(costs[item.id] for item in dropped_items),
            over_budget=used > budget,
            included_ids=tuple(item.id for item in included),
        )
