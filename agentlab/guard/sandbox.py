"""Sandboxed tool execution: confine what the model can touch.

Week 2 taught you to validate tool *arguments*. That is not enough when the
model chooses the arguments: an argument that passes the JSON schema can still
say ``../../etc/passwd``, a 2 GB file, or ``rm -rf /``. The sandbox is the layer
where a syntactically valid request is checked against what this run is actually
allowed to do (research 03 §3.2, §3.4):

- **Path allowlist**: model-supplied paths are relative to one of the allowed
  roots; traversal, absolute paths and encoded traversal are rejected after
  decoding. Symlink escapes are caught by resolving before comparing.
- **Size limits**: reading a huge file is an unbounded-cost incident; read at
  most ``max_bytes`` and refuse bigger files loudly.
- **Command boundary**: subprocesses may only run allowlisted commands, with a
  hard timeout and truncated output. Anything else is a refusal, not a warning.
- **Approval for writes**: tools declare ``is_write`` (``agentlab.tools``), and a
  write requires an approval token bound to the exact action (tool + canonical
  arguments), the tenant, and an expiry, consumed **at most once**. A replayed
  token is an unbounded execution licence; the ledger is what makes replay
  impossible.

Read first: ``agentlab/tools/registry.py`` (``Tool.is_write``) and research 03
§3.2 (sandbox escape / RCE row) and §4.4 (multi-tenant isolation).

Hints:
- Decode before validating: ``urllib.parse.unquote`` turns ``%2e%2e%2f`` into
  ``../`` and makes the traversal visible.
- Compare resolved paths with ``Path.is_relative_to`` against resolved roots,
  never raw strings.
- Bind approvals to a canonical hash of the action, not to a tool name.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentlab.tools.registry import Tool

#: Default maximum number of bytes a sandboxed read may return.
DEFAULT_MAX_READ_BYTES = 256_000
#: Default subprocess timeout, in seconds.
DEFAULT_TIMEOUT_S = 2.0
#: Default maximum characters of subprocess output kept.
DEFAULT_MAX_OUTPUT_CHARS = 8_000


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Outcome of a sandboxed command. A non-zero exit is data, not an exception.

    Attributes:
        argv: the executed argv, for the audit record.
        returncode: process exit code.
        stdout: captured stdout, truncated to the output limit.
        stderr: captured stderr, truncated to the output limit.
    """

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True, slots=True)
class ApprovalToken:
    """Human approval bound to one concrete action.

    Attributes:
        ticket_id: unique id for this approval (the at-most-once key).
        action_hash: ``action_hash(tool_name, arguments)`` of the approved call.
        tenant_id: tenant the approval was granted to.
        approver: human principal who approved.
        expires_at: epoch seconds after which the token is dead.
    """

    ticket_id: str
    action_hash: str
    tenant_id: str
    approver: str
    expires_at: float


class ApprovalLedger:
    """Remembers consumed approval tickets, making execution at-most-once.

    This is intentionally tiny: one set of ticket ids. In production the ledger
    is durable (a row with a unique constraint per ticket), because an in-memory
    ledger resets on restart and re-opens the replay window.
    """

    def __init__(self) -> None:
        self._consumed: set[str] = set()

    def consume(self, token: ApprovalToken, *, now: float | None = None) -> None:
        """Mark ``token`` as used; refuse a second use or an expired token.

        Contract:
            - expired token (``now >= token.expires_at``) raises
              ``ApprovalRequired``; ``now`` defaults to ``time.time()``;
            - an already-consumed ``ticket_id`` raises ``ApprovalRequired``;
            - on success the ticket id is recorded and the call returns ``None``.
        """
        raise NotImplementedError("Week 8 lab: implement ApprovalLedger.consume")


def resolve_sandbox_path(raw_path: str, *, allowed_roots: Sequence[str | Path]) -> Path:
    """Resolve a model-supplied relative path inside an allowed root.

    Contract:
        - ``raw_path`` is URL-decoded once before validation;
        - empty paths, absolute paths (POSIX or Windows), NUL bytes and any
          ``..`` path segment raise ``PathNotAllowed``;
        - the candidate is joined to a root and resolved; if the resolved path
          is outside every allowed root, raise ``PathNotAllowed``;
        - returns the resolved ``Path`` of the first existing candidate, else the
          resolved candidate under the first allowed root;
        - raises ``ValueError`` when ``allowed_roots`` is empty.

    Hints: normalise separators first (a Windows host accepts both), then use
    ``Path.resolve(strict=False)`` so symlinked parents are followed before the
    containment check.
    """
    raise NotImplementedError("Week 8 lab: implement resolve_sandbox_path")


def read_text_limited(path: str | Path, *, max_bytes: int = DEFAULT_MAX_READ_BYTES) -> str:
    """Read a UTF-8 text file, refusing files larger than ``max_bytes``.

    Contract:
        - returns decoded text (invalid bytes replaced, never raised);
        - files larger than ``max_bytes`` raise ``SandboxLimitExceeded`` *before*
          loading the whole file;
        - ``max_bytes <= 0`` raises ``ValueError``.
    """
    raise NotImplementedError("Week 8 lab: implement read_text_limited")


def run_command(
    argv: Sequence[str],
    *,
    allowed_commands: Sequence[str],
    cwd: str | Path | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
) -> CommandResult:
    """Run one subprocess inside the sandbox boundary.

    Contract:
        - an empty argv raises ``ValueError``;
        - the command (``Path(argv[0]).name``, extension stripped) must be in
          ``allowed_commands`` or ``ToolNotAllowed`` is raised;
        - the process runs without a shell, with captured output and the given
          cwd; exceeding ``timeout_s`` raises ``SandboxTimeout``;
        - a non-zero exit is returned as ``CommandResult`` (the model decides
          what to do next); stdout/stderr are truncated to ``max_output_chars``.
    """
    raise NotImplementedError("Week 8 lab: implement run_command")


def action_hash(tool_name: str, arguments: Mapping[str, Any]) -> str:
    """Stable SHA-256 hex digest of one concrete tool action.

    The hash binds an approval to the *action*, not to the tool name: approving
    ``issue_refund`` for $10 must not authorise ``issue_refund`` for $10,000.
    Canonical form: JSON of ``{"tool": ..., "arguments": ...}`` with sorted keys,
    compact separators, ``ensure_ascii=False`` and ``default=str``.
    """
    raise NotImplementedError("Week 8 lab: implement action_hash")


def require_allowed_tool(tool: Tool, allowed_tools: Sequence[str]) -> None:
    """Raise ``ToolNotAllowed`` when ``tool`` is not on the run's allowlist."""
    raise NotImplementedError("Week 8 lab: implement require_allowed_tool")


def require_approval(
    tool: Tool,
    arguments: Mapping[str, Any],
    token: ApprovalToken | None,
    *,
    tenant_id: str,
    ledger: ApprovalLedger,
    now: float | None = None,
) -> None:
    """Require a valid, unused approval for a write tool; no-op for reads.

    Contract:
        - ``tool.is_write`` false => returns without touching the ledger;
        - write tool with ``token is None`` => ``ApprovalRequired``;
        - token tenant must equal ``tenant_id`` => otherwise ``ApprovalRequired``;
        - token ``action_hash`` must equal ``action_hash(tool.name, arguments)``;
        - the token is then consumed through ``ledger.consume(token, now=now)``,
          which enforces expiry and at-most-once use.
    """
    raise NotImplementedError("Week 8 lab: implement require_approval")
