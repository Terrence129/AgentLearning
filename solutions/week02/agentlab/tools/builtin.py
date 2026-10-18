"""Reference solution -- week 2: built-in tools.

The two non-obvious choices:

- The calculator walks a whitelisted AST instead of calling ``eval``: safety is
  structural (there is no code path from a model argument to the interpreter),
  not a blocklist that the next clever payload defeats.
- The filesystem is a *sandbox object*, not a set of path joins. Every single
  operation goes through ``resolve``, so traversal and absolute paths are
  rejected once, in one place, and the error becomes an observation.
"""

from __future__ import annotations

import ast
import operator
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agentlab.errors import ToolError
from agentlab.tools.registry import ToolRegistry
from pydantic import BaseModel, Field

DEFAULT_MAX_READ_CHARS = 64_000
MAX_SEARCH_RESULTS = 50
MAX_EXPRESSION_CHARS = 200
MAX_EXPONENT = 1000
SEARCH_MAX_FILE_BYTES = 1_000_000
SKIP_DIRS = frozenset({".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "traces"})

Number = int | float

_BINARY_OPS: dict[type[ast.operator], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type[ast.unaryop], Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorInput(BaseModel):
    """Arguments for ``calculator``; the expression is arithmetic, not Python."""

    expression: str = Field(description="Arithmetic expression, e.g. '(12 + 8) * 3'")


class ReadFileInput(BaseModel):
    """Arguments for ``read_file``; ``path`` is relative to the workspace root."""

    path: str = Field(description="Path relative to the workspace root, e.g. 'notes/todo.md'")


class ListDirInput(BaseModel):
    """Arguments for ``list_dir``."""

    path: str = Field(default=".", description="Directory path relative to the workspace root")


class WriteFileInput(BaseModel):
    """Arguments for ``write_file`` (a write action: ``is_write=True``)."""

    path: str = Field(description="Path relative to the workspace root; parents are created")
    content: str = Field(description="Full UTF-8 content to write (overwrites the file)")


class SearchTextInput(BaseModel):
    """Arguments for ``search_text``; literal substring search, not a regex."""

    pattern: str = Field(description="Literal text to find (case-sensitive)")
    path: str = Field(default=".", description="File or directory relative to the workspace root")
    max_results: int = Field(
        default=MAX_SEARCH_RESULTS,
        ge=1,
        le=200,
        description="Maximum number of matches to return",
    )


def safe_eval(expression: str) -> int | float:
    """Evaluate a plain arithmetic expression without ``eval``."""
    if not isinstance(expression, str):
        raise ValueError("expression must be a string")
    text = expression.strip()
    if not text:
        raise ValueError("expression is empty")
    if len(text) > MAX_EXPRESSION_CHARS:
        raise ValueError(f"expression is longer than {MAX_EXPRESSION_CHARS} characters")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"invalid arithmetic expression: {exc.msg}") from exc
    try:
        return _eval_node(tree.body)
    except ZeroDivisionError as exc:
        raise ValueError("division by zero") from exc


def _eval_node(node: ast.AST) -> Number:
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"unsupported literal: {value!r}")
        return value
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BINARY_OPS:
            raise ValueError(f"unsupported binary operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if op_type is ast.Pow and abs(right) > MAX_EXPONENT:
            raise ValueError(f"exponent is larger than {MAX_EXPONENT}")
        return _BINARY_OPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f"unsupported unary operator: {op_type.__name__}")
        return _UNARY_OPS[op_type](_eval_node(node.operand))
    raise ValueError(f"unsupported expression element: {type(node).__name__}")


class FileSandbox:
    """A filesystem view rooted at one directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    # -- path policy -------------------------------------------------------

    def resolve(self, path: str) -> Path:
        """Resolve a workspace-relative path, refusing anything that escapes ``root``."""
        text = (path or "").strip()
        if text in {"", "."}:
            return self.root
        candidate = Path(text)
        if candidate.is_absolute():
            raise ToolError("absolute paths are not allowed; use a path relative to the workspace root")
        resolved = (self.root / candidate).resolve()
        if not resolved.is_relative_to(self.root):
            raise ToolError(f"path {text!r} escapes the workspace root")
        return resolved

    def _relative(self, resolved: Path) -> str:
        return resolved.relative_to(self.root).as_posix()

    # -- operations --------------------------------------------------------

    def read_text(self, path: str, *, max_chars: int = DEFAULT_MAX_READ_CHARS) -> str:
        """Return the UTF-8 text of a file under the root."""
        resolved = self.resolve(path)
        if not resolved.is_file():
            raise ToolError(f"not a file: {path!r}")
        try:
            text = resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ToolError(f"not a UTF-8 text file: {path!r}") from exc
        except OSError as exc:
            raise ToolError(f"cannot read {path!r}: {exc}") from exc
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"

    def list_dir(self, path: str = ".") -> list[str]:
        """Return the sorted entries of a directory under the root."""
        resolved = self.resolve(path)
        if not resolved.is_dir():
            raise ToolError(f"not a directory: {path!r}")
        entries = [f"{entry.name}/" if entry.is_dir() else entry.name for entry in resolved.iterdir()]
        return sorted(entries)

    def write_text(self, path: str, content: str) -> str:
        """Write UTF-8 ``content`` to a file under the root, creating parents."""
        resolved = self.resolve(path)
        if resolved.is_dir():
            raise ToolError(f"cannot write to a directory: {path!r}")
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise ToolError(f"cannot write {path!r}: {exc}") from exc
        return f"wrote {len(content)} characters to {self._relative(resolved)}"

    def search_text(
        self,
        pattern: str,
        path: str = ".",
        *,
        max_results: int = MAX_SEARCH_RESULTS,
    ) -> list[str]:
        """Literal substring search across the workspace (or one file)."""
        if not pattern:
            raise ToolError("pattern must not be empty")
        resolved = self.resolve(path)
        if resolved.is_file():
            files = [resolved]
        elif resolved.is_dir():
            files = sorted(
                candidate
                for candidate in resolved.rglob("*")
                if candidate.is_file()
                and not any(part in SKIP_DIRS for part in candidate.relative_to(self.root).parts[:-1])
            )
        else:
            raise ToolError(f"not a file or directory: {path!r}")

        matches: list[str] = []
        for file_path in files:
            if len(matches) >= max_results:
                break
            try:
                if file_path.stat().st_size > SEARCH_MAX_FILE_BYTES:
                    continue
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue  # binary or unreadable files are skipped, not errors
            relative = self._relative(file_path)
            for line_number, line in enumerate(content.splitlines(), start=1):
                if pattern in line:
                    matches.append(f"{relative}:{line_number}: {line.strip()}")
                    if len(matches) >= max_results:
                        break
        return matches


def build_builtin_tools(root: str | Path, *, registry: ToolRegistry | None = None) -> ToolRegistry:
    """Register the five built-in tools in a registry and return it."""
    sandbox = FileSandbox(root)
    reg = ToolRegistry() if registry is None else registry

    @reg.add(
        name="calculator",
        description=(
            "Evaluate one arithmetic expression. Supports numbers, parentheses and "
            "the operators + - * / // % **. No variables, no functions."
        ),
        input_model=CalculatorInput,
    )
    def calculator(args: CalculatorInput) -> int | float:
        return safe_eval(args.expression)

    @reg.add(
        name="read_file",
        description="Read a UTF-8 text file. The path must be relative to the workspace root.",
        input_model=ReadFileInput,
    )
    def read_file(args: ReadFileInput) -> str:
        return sandbox.read_text(args.path)

    @reg.add(
        name="list_dir",
        description=(
            "List a directory relative to the workspace root. One entry per line; directories end with '/'."
        ),
        input_model=ListDirInput,
    )
    def list_dir(args: ListDirInput) -> str:
        return "\n".join(sandbox.list_dir(args.path))

    @reg.add(
        name="write_file",
        description=(
            "Write UTF-8 content to a file relative to the workspace root, creating "
            "parent directories. Overwrites an existing file."
        ),
        input_model=WriteFileInput,
        is_write=True,
    )
    def write_file(args: WriteFileInput) -> str:
        return sandbox.write_text(args.path, args.content)

    @reg.add(
        name="search_text",
        description=(
            "Search workspace text files for a literal, case-sensitive substring. "
            "Returns 'path:line_number: line_text' matches."
        ),
        input_model=SearchTextInput,
    )
    def search_text(args: SearchTextInput) -> str:
        return "\n".join(sandbox.search_text(args.pattern, args.path, max_results=args.max_results))

    return reg
