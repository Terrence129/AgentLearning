"""Sandbox tests: path allowlist, size/time limits, approval binding."""

from __future__ import annotations

import sys

import pytest
from agentlab.guard.errors import (
    ApprovalRequired,
    PathNotAllowed,
    SandboxLimitExceeded,
    SandboxTimeout,
    ToolNotAllowed,
)
from agentlab.guard.sandbox import (
    ApprovalLedger,
    ApprovalToken,
    action_hash,
    read_text_limited,
    require_allowed_tool,
    require_approval,
    resolve_sandbox_path,
    run_command,
)
from agentlab.tools.registry import Tool

pytestmark = pytest.mark.week


def _tool(name: str = "write_file", *, is_write: bool = True) -> Tool:
    return Tool(
        name=name, description="test tool", parameters={}, handler=lambda args: None, is_write=is_write
    )


def _token(**overrides: object) -> ApprovalToken:
    values: dict[str, object] = {
        "ticket_id": "ticket-1",
        "action_hash": action_hash("write_file", {"path": "notes.txt"}),
        "tenant_id": "tenant-a",
        "approver": "alice",
        "expires_at": 1_060.0,
    }
    values.update(overrides)
    return ApprovalToken(**values)  # type: ignore[arg-type]


def _root(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    return root


# ---------------------------------------------------------------------------
# path allowlist
# ---------------------------------------------------------------------------


def test_resolve_rejects_parent_traversal(tmp_path):
    with pytest.raises(PathNotAllowed):
        resolve_sandbox_path("../escape.txt", allowed_roots=[_root(tmp_path)])


def test_resolve_rejects_encoded_traversal(tmp_path):
    with pytest.raises(PathNotAllowed):
        resolve_sandbox_path("..%2F..%2Fwindows%2Fwin.ini", allowed_roots=[_root(tmp_path)])


def test_resolve_rejects_absolute_paths(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(PathNotAllowed):
        resolve_sandbox_path(str(root / "notes.txt"), allowed_roots=[root])


def test_resolve_rejects_empty_path(tmp_path):
    with pytest.raises(PathNotAllowed):
        resolve_sandbox_path("", allowed_roots=[_root(tmp_path)])


def test_resolve_accepts_relative_path_inside_root(tmp_path):
    root = _root(tmp_path)
    (root / "notes.txt").write_text("inside", encoding="utf-8")

    resolved = resolve_sandbox_path("notes.txt", allowed_roots=[root])

    assert resolved == (root / "notes.txt").resolve()
    assert resolved.parent == root.resolve()


# ---------------------------------------------------------------------------
# size and command limits
# ---------------------------------------------------------------------------


def test_read_text_limited_returns_small_file(tmp_path):
    path = tmp_path / "small.txt"
    path.write_text("hello sandbox", encoding="utf-8")

    assert read_text_limited(path, max_bytes=64) == "hello sandbox"


def test_read_text_limited_rejects_oversized_file(tmp_path):
    path = tmp_path / "big.txt"
    path.write_text("x" * 200, encoding="utf-8")

    with pytest.raises(SandboxLimitExceeded):
        read_text_limited(path, max_bytes=16)

    with pytest.raises(ValueError):
        read_text_limited(path, max_bytes=0)


def test_run_command_rejects_unlisted_command(tmp_path):
    with pytest.raises(ToolNotAllowed):
        run_command(["cmd", "/c", "echo hi"], allowed_commands=["python"], cwd=tmp_path)


def test_run_command_runs_allowed_command(tmp_path):
    result = run_command(
        [sys.executable, "-c", "print('sandbox-ok')"],
        allowed_commands=["python"],
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "sandbox-ok" in result.stdout


def test_run_command_times_out(tmp_path):
    with pytest.raises(SandboxTimeout):
        run_command(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            allowed_commands=["python"],
            cwd=tmp_path,
            timeout_s=0.1,
        )


# ---------------------------------------------------------------------------
# approval binding
# ---------------------------------------------------------------------------


def test_action_hash_is_canonical_and_sensitive():
    first = action_hash("write_file", {"b": 2, "a": 1})
    reordered = action_hash("write_file", {"a": 1, "b": 2})
    different = action_hash("write_file", {"a": 1, "b": 3})

    assert first == reordered
    assert first != different
    assert len(first) == 64
    assert all(char in "0123456789abcdef" for char in first)


def test_write_tool_requires_approval():
    with pytest.raises(ApprovalRequired):
        require_approval(
            _tool(),
            {"path": "notes.txt"},
            None,
            tenant_id="tenant-a",
            ledger=ApprovalLedger(),
            now=1_000.0,
        )


def test_read_tool_needs_no_approval():
    result = require_approval(
        _tool(is_write=False),
        {"query": "invoice"},
        None,
        tenant_id="tenant-a",
        ledger=ApprovalLedger(),
        now=1_000.0,
    )

    assert result is None


def test_approval_must_match_the_exact_action():
    with pytest.raises(ApprovalRequired):
        require_approval(
            _tool(),
            {"path": "other.txt"},
            _token(),
            tenant_id="tenant-a",
            ledger=ApprovalLedger(),
            now=1_000.0,
        )


def test_expired_approval_is_rejected():
    with pytest.raises(ApprovalRequired):
        require_approval(
            _tool(),
            {"path": "notes.txt"},
            _token(expires_at=900.0),
            tenant_id="tenant-a",
            ledger=ApprovalLedger(),
            now=1_000.0,
        )


def test_approval_for_another_tenant_is_rejected():
    with pytest.raises(ApprovalRequired):
        require_approval(
            _tool(),
            {"path": "notes.txt"},
            _token(tenant_id="tenant-b"),
            tenant_id="tenant-a",
            ledger=ApprovalLedger(),
            now=1_000.0,
        )


def test_replayed_approval_is_rejected():
    ledger = ApprovalLedger()
    arguments = {"path": "notes.txt"}

    require_approval(_tool(), arguments, _token(), tenant_id="tenant-a", ledger=ledger, now=1_000.0)
    with pytest.raises(ApprovalRequired):
        require_approval(_tool(), arguments, _token(), tenant_id="tenant-a", ledger=ledger, now=1_000.0)


def test_require_allowed_tool_rejects_unlisted_tool():
    with pytest.raises(ToolNotAllowed):
        require_allowed_tool(_tool("shell"), allowed_tools=["search"])

    assert require_allowed_tool(_tool("search"), allowed_tools=["search"]) is None
