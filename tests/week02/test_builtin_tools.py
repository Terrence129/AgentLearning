"""Tests for the built-in tools: safe calculator + workspace-scoped filesystem.

Two themes: the calculator must be *structurally* unable to run code, and the
filesystem tools must refuse every path that escapes their root -- because the
model's arguments are untrusted input, not trustworthy function calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agentlab.tools.builtin import build_builtin_tools, safe_eval

pytestmark = pytest.mark.week


# ---------------------------------------------------------------------------
# calculator
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("(12 + 8) * 3", 60),
        ("2 ** 10", 1024),
        ("7 / 2", 3.5),
        ("-3 + +5", 2),
        ("10 // 3", 3),
        ("10 % 3", 1),
        ("1.5 * 2", 3.0),
    ],
)
def test_safe_eval_evaluates_arithmetic(expression: str, expected: float) -> None:
    assert safe_eval(expression) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "open('/etc/passwd')",
        "x + 1",
        "True",
        "[1, 2][0]",
        "lambda: 1",
        "1 if 2 else 3",
        "{'x': 1}",
        "f'{1}'",
    ],
)
def test_safe_eval_rejects_non_arithmetic(expression: str) -> None:
    with pytest.raises(ValueError):
        safe_eval(expression)


@pytest.mark.parametrize("expression", ["", "   ", "1; 2", "1 +", "9 ** 5000"])
def test_safe_eval_rejects_invalid_or_abusive_expressions(expression: str) -> None:
    with pytest.raises(ValueError):
        safe_eval(expression)


@pytest.mark.parametrize("expression", ["1 / 0", "1 // 0", "1 % 0"])
def test_safe_eval_reports_division_by_zero(expression: str) -> None:
    with pytest.raises(ValueError, match="division by zero"):
        safe_eval(expression)


def test_calculator_tool_returns_observation(tmp_path: Path) -> None:
    registry = build_builtin_tools(tmp_path)

    result = registry.invoke("calculator", {"expression": "(12 + 8) * 3"})

    assert result.ok
    assert result.output == "60"


def test_calculator_tool_reports_bad_expression_as_observation(tmp_path: Path) -> None:
    registry = build_builtin_tools(tmp_path)

    result = registry.invoke("calculator", {"expression": "__import__('os').system('dir')"})

    assert result.ok is False
    assert "ValueError" in (result.error or "")


# ---------------------------------------------------------------------------
# read_file / list_dir / write_file
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "workspace"
    root.mkdir()
    return root


def test_read_file_returns_content_inside_root(workspace: Path) -> None:
    (workspace / "notes.txt").write_text("hello workspace", encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("read_file", {"path": "notes.txt"})

    assert result.ok
    assert result.output == "hello workspace"


def test_read_file_rejects_path_traversal(workspace: Path) -> None:
    (workspace.parent / "secret.txt").write_text("TOP SECRET", encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("read_file", {"path": "../secret.txt"})

    assert result.ok is False
    assert "TOP SECRET" not in result.output


def test_read_file_rejects_absolute_path(workspace: Path) -> None:
    outside = workspace.parent / "outside.txt"
    outside.write_text("not yours", encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("read_file", {"path": str(outside)})

    assert result.ok is False
    assert "absolute" in (result.error or "").lower()


def test_read_file_missing_file_is_an_observation(workspace: Path) -> None:
    registry = build_builtin_tools(workspace)

    result = registry.invoke("read_file", {"path": "nope.txt"})

    assert result.ok is False
    assert "nope.txt" in (result.error or "")


def test_list_dir_marks_directories_and_sorts(workspace: Path) -> None:
    (workspace / "b.txt").write_text("b", encoding="utf-8")
    (workspace / "a.txt").write_text("a", encoding="utf-8")
    (workspace / "sub").mkdir()
    registry = build_builtin_tools(workspace)

    result = registry.invoke("list_dir", {"path": "."})

    assert result.ok
    assert result.output.splitlines() == ["a.txt", "b.txt", "sub/"]


def test_list_dir_rejects_a_file_path(workspace: Path) -> None:
    (workspace / "a.txt").write_text("a", encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("list_dir", {"path": "a.txt"})

    assert result.ok is False


def test_write_file_creates_parent_directories(workspace: Path) -> None:
    registry = build_builtin_tools(workspace)

    result = registry.invoke("write_file", {"path": "notes/deep/todo.md", "content": "hello"})

    assert result.ok
    assert (workspace / "notes" / "deep" / "todo.md").read_text(encoding="utf-8") == "hello"
    assert "notes/deep/todo.md" in result.output
    assert registry.get("write_file") is not None
    assert registry.get("write_file").is_write is True


def test_write_file_rejects_path_outside_root(workspace: Path) -> None:
    outside = workspace.parent / "escape.txt"
    registry = build_builtin_tools(workspace)

    result = registry.invoke("write_file", {"path": "../escape.txt", "content": "bad"})

    assert result.ok is False
    assert not outside.exists()


# ---------------------------------------------------------------------------
# search_text
# ---------------------------------------------------------------------------


def test_search_text_returns_path_line_matches(workspace: Path) -> None:
    (workspace / "a.txt").write_text("needle alpha\nsecond needle here\n", encoding="utf-8")
    (workspace / "sub").mkdir()
    (workspace / "sub" / "c.txt").write_text("needle in sub\n", encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("search_text", {"pattern": "needle"})

    assert result.ok
    assert result.output.splitlines() == [
        "a.txt:1: needle alpha",
        "a.txt:2: second needle here",
        "sub/c.txt:1: needle in sub",
    ]


def test_search_text_respects_max_results(workspace: Path) -> None:
    (workspace / "many.txt").write_text("x\n" * 5, encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("search_text", {"pattern": "x", "max_results": 2})

    assert result.ok
    assert len(result.output.splitlines()) == 2


def test_search_text_skips_binaries_and_ignored_directories(workspace: Path) -> None:
    (workspace / "a.txt").write_text("needle\n", encoding="utf-8")
    (workspace / "blob.bin").write_bytes(b"\xff\xfe needle")
    (workspace / ".git").mkdir()
    (workspace / ".git" / "secret.txt").write_text("needle\n", encoding="utf-8")
    registry = build_builtin_tools(workspace)

    result = registry.invoke("search_text", {"pattern": "needle"})

    assert result.ok
    assert result.output.splitlines() == ["a.txt:1: needle"]


def test_search_text_rejects_empty_pattern(workspace: Path) -> None:
    registry = build_builtin_tools(workspace)

    result = registry.invoke("search_text", {"pattern": ""})

    assert result.ok is False
    assert "pattern" in (result.error or "").lower()


# ---------------------------------------------------------------------------
# registry surface
# ---------------------------------------------------------------------------


def test_builtin_tools_declare_schemas_and_write_flag(tmp_path: Path) -> None:
    registry = build_builtin_tools(tmp_path)

    assert registry.names() == ["calculator", "list_dir", "read_file", "search_text", "write_file"]
    for spec in registry.specs():
        assert spec.parameters.get("type") == "object"
    calculator = registry.get("calculator")
    assert calculator is not None
    assert "expression" in calculator.parameters["properties"]
    assert calculator.parameters["required"] == ["expression"]
    assert registry.get("write_file") is not None
    assert registry.get("write_file").is_write is True
    for read_tool in ("calculator", "read_file", "list_dir", "search_text"):
        tool = registry.get(read_tool)
        assert tool is not None
        assert tool.is_write is False
