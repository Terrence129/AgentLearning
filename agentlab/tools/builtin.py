"""Built-in tools: a calculator and a workspace-scoped filesystem -- YOUR WEEK 2 BUILD.

Two lessons live in this file, and neither is "write a file helper":

1. **A tool is a contract, not a function.** Each tool declares a pydantic input
   model; the registry turns it into JSON Schema for the model and validates the
   model's arguments before anything executes. Bad arguments become observations,
   not crashes.

2. **Safety is a property of the tool definition.** The filesystem tools are
   confined to one workspace root: relative paths only, traversal rejected,
   writes flagged ``is_write=True`` so later weeks can require approval. A model
   that can write anywhere can rewrite its own instructions.

The calculator is deliberately not ``eval``: a safe AST walker that accepts
numbers, parentheses, unary ``+``/``-`` and ``+ - * / // % **`` is enough for
arithmetic and structurally unable to import ``os`` -- which is what makes it
safe to hand to a model.

Read first: ``docs/research/01-agent-architecture-sota.md`` §1.4 (tools are the
action surface) and §3.3 (tool schema checklist).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from agentlab.tools.registry import ToolRegistry

#: Files are read up to this many characters; longer files are truncated with a marker.
DEFAULT_MAX_READ_CHARS = 64_000

#: Default cap on ``search_text`` matches, so grep-like tools cannot flood context.
MAX_SEARCH_RESULTS = 50

#: Expressions longer than this are rejected before parsing.
MAX_EXPRESSION_CHARS = 200

#: ``**`` with an enormous exponent is a denial-of-service attack on your process.
MAX_EXPONENT = 1000

#: Directory names never traversed by ``search_text`` (cheap recursive walk).
SKIP_DIRS = frozenset({".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "traces"})


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
    """Evaluate a plain arithmetic expression without ``eval``.

    Accepted grammar: integer/float literals, parentheses, unary ``+``/``-``,
    and the binary operators ``+ - * / // % **``. Everything else -- names,
    calls, attribute access, comprehensions, comparisons, boolean literals --
    raises ``ValueError``.

    Additional policy:
    - an empty expression, a non-str input, or one longer than
      ``MAX_EXPRESSION_CHARS`` raises ``ValueError``;
    - a ``SyntaxError`` is re-raised as ``ValueError`` with a useful message;
    - ``**`` with ``abs(exponent) > MAX_EXPONENT`` raises ``ValueError``;
    - division by zero raises ``ValueError`` mentioning ``division by zero``.

    Returns ``int`` when the arithmetic is integral, ``float`` otherwise.
    """
    raise NotImplementedError("Week 2 lab: implement safe_eval")


class FileSandbox:
    """A filesystem view rooted at one directory.

    Every path is relative to ``root``; absolute paths and paths that escape the
    root (``..``, symlink tricks) raise ``agentlab.errors.ToolError``. The
    registry converts that into a failed ``ToolResult``, which the loop feeds
    back to the model more safely than a traceback.

    The class contains no model-facing policy: JSON Schemas and the
    read/write/approval flags live in ``build_builtin_tools``.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str) -> Path:
        """Resolve a workspace-relative path, refusing anything that escapes ``root``.

        ``"."`` resolves to the root itself. Raises ``ToolError`` for absolute
        paths and for paths that resolve outside the root (check with
        ``Path.is_relative_to`` *after* ``resolve()``, which also catches symlinks).
        """
        raise NotImplementedError("Week 2 lab: implement FileSandbox.resolve")

    def read_text(self, path: str, *, max_chars: int = DEFAULT_MAX_READ_CHARS) -> str:
        """Return the UTF-8 text of a file under the root.

        Raises ``ToolError`` when the path is not an existing regular file, is
        not UTF-8, or escapes the root. Text longer than ``max_chars`` is
        truncated and a ``"...[truncated N chars]"`` marker is appended.
        """
        raise NotImplementedError("Week 2 lab: implement FileSandbox.read_text")

    def list_dir(self, path: str = ".") -> list[str]:
        """Return the sorted entries of a directory under the root.

        Directories are suffixed with ``"/"`` so the model can tell them apart
        (``["a.txt", "sub/"]``). Raises ``ToolError`` when ``path`` is not an
        existing directory. Hidden files are included; the caller (the tool
        handler) decides how to render the list.
        """
        raise NotImplementedError("Week 2 lab: implement FileSandbox.list_dir")

    def write_text(self, path: str, content: str) -> str:
        """Write UTF-8 ``content`` to a file under the root, creating parents.

        Raises ``ToolError`` when the path escapes the root or points at an
        existing directory. Returns a short human/model-readable summary that
        includes the workspace-relative path and the number of characters
        written (e.g. ``"wrote 42 characters to notes/todo.md"``).
        """
        raise NotImplementedError("Week 2 lab: implement FileSandbox.write_text")

    def search_text(
        self,
        pattern: str,
        path: str = ".",
        *,
        max_results: int = MAX_SEARCH_RESULTS,
    ) -> list[str]:
        """Literal substring search across the workspace (or one file).

        Behaviour:
        - returns ``"relative/path:line_number: line_text"`` strings, sorted by
          path then line number;
        - ``pattern`` is a literal substring, case-sensitive; empty patterns
          raise ``ToolError``;
        - files that are not UTF-8 decodable are skipped silently (binaries are
          not errors);
        - directories named in ``SKIP_DIRS`` are never traversed;
        - stops after ``max_results`` matches.
        """
        raise NotImplementedError("Week 2 lab: implement FileSandbox.search_text")


def build_builtin_tools(root: str | Path, *, registry: ToolRegistry | None = None) -> ToolRegistry:
    """Register the five built-in tools in a registry and return it.

    Tools (exact names, because the trace and the model both see them):

    ==============  =======================  ===============  ===========================
    name            input model              ``is_write``     output rendering
    ==============  =======================  ===============  ===========================
    ``calculator``  ``CalculatorInput``      ``False``        numeric result as text
    ``read_file``   ``ReadFileInput``        ``False``        file content
    ``list_dir``    ``ListDirInput``         ``False``        one entry per line
    ``write_file``  ``WriteFileInput``       ``True``         summary line
    ``search_text`` ``SearchTextInput``      ``False``        one match per line
    ==============  =======================  ===============  ===========================

    ``registry=None`` creates a new registry; pass one in to add these tools to
    an existing agent. Write tools must declare ``is_write=True`` even though
    this lab does not yet enforce approvals -- week 8 will, and it reads the flag.
    """
    raise NotImplementedError("Week 2 lab: implement build_builtin_tools")


__all__ = [
    "DEFAULT_MAX_READ_CHARS",
    "MAX_EXPRESSION_CHARS",
    "MAX_EXPONENT",
    "MAX_SEARCH_RESULTS",
    "SKIP_DIRS",
    "CalculatorInput",
    "FileSandbox",
    "ListDirInput",
    "ReadFileInput",
    "SearchTextInput",
    "WriteFileInput",
    "build_builtin_tools",
    "safe_eval",
]
