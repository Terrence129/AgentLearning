"""Context-window assembly: the budget ledger for a prompt (week 4).

Why this module exists
----------------------
A language model has no memory; the *only* thing it sees is what you put in the
prompt this turn. Performance degrades as the prompt grows -- Chroma's
context-rot study found focused ~300-token inputs beating full ~113k-token
inputs across model families, and one distractor is enough to hurt
(docs/research/01-agent-architecture-sota.md §3.1). So "the context window is
big, just append everything" is not a strategy; it is how an agent loses the
instruction that mattered.

What breaks without it
----------------------
- A pinned safety constraint ("never refund above $500") scrolls out of the
  window and the model confidently violates it.
- Tool output from 40 turns ago crowds out the current task state, so the agent
  loops or re-does work.
- Unbounded growth hits the provider limit mid-task and the run dies with no
  recoverable partial result.

Your job in this module is a **priority-aware budget**: every candidate piece of
context declares how strong its claim on the window is, the window fills the
highest claims first, and pinned constraints are *never* evicted.

Read first: docs/research/01-agent-architecture-sota.md §3.1-§3.4 and §3.8.

Public surface
--------------
``Priority``          priority classes, lower integer = stronger claim
``ContextItem``       one candidate message plus its priority
``TokenEstimator``    cheap deterministic token estimate (no tokenizer needed)
``WindowPolicy``      the token budget and output reservation
``AssembledContext``  the selected messages plus accounting
``ContextWindow``     accumulates items, assembles a budgeted message list
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from agentlab.errors import AgentError
from agentlab.types import Message, Role

#: Rough characters-per-token ratio for mixed English text. Deliberately
#: crude: the point is a *relative* budget, not exact billing (providers report
#: true usage; ``Budget`` in agentlab/budget.py accounts for that).
CHARS_PER_TOKEN = 4

#: Fixed per-message overhead of role markers, separators and formatting. Real
#: chat templates add a handful of tokens per message even for empty content.
MESSAGE_OVERHEAD_TOKENS = 4


class ContextBudgetError(AgentError):
    """The context policy cannot be satisfied (invalid budget numbers, etc.)."""


class Priority(IntEnum):
    """How strong a claim an item has on the context window.

    Lower integer = stronger claim. The hierarchy mirrors the budget policy in
    research §3.8: pinned constraints > task state > recent turns > observations
    > history.
    """

    PINNED = 0
    TASK_STATE = 1
    RECENT_TURNS = 2
    OBSERVATIONS = 3
    HISTORY = 4


@dataclass(frozen=True, slots=True)
class ContextItem:
    """One candidate piece of context, with its eviction priority.

    Attributes:
        id: unique, stable identifier (used for deduplication and reporting).
        content: the text that will be placed in the prompt.
        priority: claim strength; see :class:`Priority`.
        role: chat role for the assembled message.
        tool_call_id: required when ``role == "tool"`` (links the result to the
            assistant tool call); ignored otherwise.
        name: optional tool name for ``role == "tool"``.
    """

    id: str
    content: str
    priority: Priority
    role: Role = "user"
    tool_call_id: str | None = None
    name: str | None = None

    # -- constructors ------------------------------------------------------
    #
    # HINTS
    # - Every constructor is a one-liner that fixes the role/priority pair.
    # - Pinned constraints are normally system messages.
    # - Observations are tool messages and must carry a tool_call_id.

    @classmethod
    def pinned_constraint(cls, item_id: str, content: str) -> ContextItem:
        """A policy/constraint item that must never be evicted (system role)."""
        raise NotImplementedError("Week 4 lab: implement ContextItem.pinned_constraint")

    @classmethod
    def task_state(cls, item_id: str, content: str) -> ContextItem:
        """Current plan / decisions / open questions (system role)."""
        raise NotImplementedError("Week 4 lab: implement ContextItem.task_state")

    @classmethod
    def turn(cls, item_id: str, role: Role, content: str) -> ContextItem:
        """A recent conversation turn that should be kept verbatim if possible."""
        raise NotImplementedError("Week 4 lab: implement ContextItem.turn")

    @classmethod
    def observation(
        cls, item_id: str, content: str, *, tool_call_id: str, name: str | None = None
    ) -> ContextItem:
        """A tool result (low priority: the cheapest thing to compress away)."""
        raise NotImplementedError("Week 4 lab: implement ContextItem.observation")

    @classmethod
    def history(cls, item_id: str, role: Role, content: str) -> ContextItem:
        """Old conversation content: first to be evicted."""
        raise NotImplementedError("Week 4 lab: implement ContextItem.history")

    # -- conversion --------------------------------------------------------

    def to_message(self) -> Message:
        """Convert to the wire ``Message`` type used by providers.

        Contract:
            - ``role`` is preserved.
            - For tool items use ``Message.tool_result(tool_call_id, content, name)``.
            - For every other role use ``Message(role=..., content=...)``.
        """
        raise NotImplementedError("Week 4 lab: implement ContextItem.to_message")


class TokenEstimator:
    """Cheap deterministic token estimate.

    A real implementation might use tiktoken or the provider's counter. This one
    uses a ratio so the labs stay dependency-free and deterministic; that is
    enough because the window only needs *relative* costs.

    Contract:
        - ``estimate_text("") == 0``.
        - ``estimate_text(text)`` is ``ceil(len(text) / CHARS_PER_TOKEN)``.
        - ``estimate_message(item)`` adds ``MESSAGE_OVERHEAD_TOKENS`` to the text
          estimate (every message pays the chat-template overhead).
    """

    def estimate_text(self, text: str) -> int:
        """Estimated tokens for a bare string."""
        raise NotImplementedError("Week 4 lab: implement TokenEstimator.estimate_text")

    def estimate_message(self, item: ContextItem) -> int:
        """Estimated tokens for one item once rendered as a chat message."""
        raise NotImplementedError("Week 4 lab: implement TokenEstimator.estimate_message")


@dataclass(frozen=True, slots=True)
class WindowPolicy:
    """The context budget for one agent call.

    Attributes:
        max_tokens: total context-window budget.
        reserve_output_tokens: tokens reserved for the model's reply; the input
            budget is ``max_tokens - reserve_output_tokens``.
    """

    max_tokens: int
    reserve_output_tokens: int = 0

    @property
    def input_budget(self) -> int:
        """Tokens available for input messages.

        Raises:
            ContextBudgetError: if ``max_tokens <= 0``, ``reserve_output_tokens
                < 0``, or the reservation leaves no input budget.
        """
        raise NotImplementedError("Week 4 lab: implement WindowPolicy.input_budget")


@dataclass(frozen=True, slots=True)
class AssembledContext:
    """The outcome of one assembly pass.

    Attributes:
        messages: selected messages, in original insertion order.
        used_tokens: estimated tokens of the selected messages.
        budget_tokens: the input budget the assembly targeted.
        dropped: ids of items that did not fit, in insertion order.
        dropped_tokens: estimated tokens of the dropped items.
        over_budget: True when pinned items alone exceed the budget (the
            assembler still includes them; reporting beats silent eviction).
        included_ids: ids of selected items, in insertion order.
    """

    messages: tuple[Message, ...]
    used_tokens: int
    budget_tokens: int
    dropped: tuple[str, ...]
    dropped_tokens: int
    over_budget: bool
    included_ids: tuple[str, ...]


class ContextWindow:
    """Accumulates context items and assembles them under a token budget.

    Assembly contract:
        1. Items are selected by priority class, strongest first:
           PINNED, TASK_STATE, RECENT_TURNS, OBSERVATIONS, HISTORY.
        2. PINNED items are always included, even when they alone exceed the
           budget (``over_budget`` is then True).
        3. Within a class, newer items win when the class does not fully fit.
        4. Selected messages are emitted in original insertion order, not
           priority order, so the prompt reads like a conversation.
        5. ``dropped`` reports every item that did not fit, in insertion order.
    """

    def __init__(self, policy: WindowPolicy, estimator: TokenEstimator | None = None) -> None:
        self.policy = policy
        self.estimator = estimator or TokenEstimator()
        self._items: list[ContextItem] = []
        self._ids: set[str] = set()

    def add(self, item: ContextItem) -> None:
        """Add one item.

        Raises:
            ValueError: if an item with the same ``id`` was already added.
        """
        raise NotImplementedError("Week 4 lab: implement ContextWindow.add")

    def items(self) -> tuple[ContextItem, ...]:
        """The items added so far, in insertion order."""
        raise NotImplementedError("Week 4 lab: implement ContextWindow.items")

    def assemble(self) -> AssembledContext:
        """Select items under the policy and return the assembled context.

        Raises:
            ContextBudgetError: if :attr:`WindowPolicy.input_budget` is invalid.
        """
        raise NotImplementedError("Week 4 lab: implement ContextWindow.assemble")
