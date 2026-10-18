"""Check that every relative markdown link in the repository resolves to a real file.

This exists because a learning repository is mostly links, and a dead internal link
is a broken exercise. Run it after editing docs:

    .\\.venv\\Scripts\\python.exe scripts/check_links.py

Exit code 1 when any link is broken. External links are not fetched (see
``--external`` for a best-effort check, which is slow and rate-limited).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# [text](target) and [text](<target with spaces>) -- skip images and external links.
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "bin",
    "obj",
    "data",
    "traces",
    "PersonalInfo",
    "_research",
}


def iter_markdown(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return sorted(files)


def check_file(path: Path) -> list[tuple[int, str, str]]:
    """Return (line_number, link, reason) for broken links in one file."""
    problems: list[tuple[int, str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in LINK_RE.finditer(line):
            target = match.group(1).strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            if target.startswith("app://"):
                continue
            anchor = ""
            if "#" in target:
                target, anchor = target.split("#", 1)
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(REPO_ROOT)
            except ValueError:
                problems.append((line_no, match.group(0), "points outside the repository"))
                continue
            if not resolved.exists():
                problems.append((line_no, match.group(0), f"missing target: {target}"))
            elif anchor and resolved.suffix == ".md":
                section = resolved.read_text(encoding="utf-8", errors="replace")
                if anchor.lower() not in _slugify(section):
                    problems.append((line_no, match.group(0), f"missing anchor: #{anchor}"))
    return problems


def _slugify(markdown: str) -> str:
    """Rough GitHub heading slug set, enough to catch obvious anchor typos."""
    slugs: set[str] = set()
    for line in markdown.splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            slug = re.sub(r"[^\w\s-]", "", heading).strip().replace(" ", "-")
            slugs.add(slug)
    return " ".join(slugs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--quiet", action="store_true", help="Only print problems")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = iter_markdown(root)
    failures = 0
    for path in files:
        problems = check_file(path)
        if not problems:
            continue
        failures += len(problems)
        rel = path.relative_to(root)
        for line_no, link, reason in problems:
            print(f"{rel}:{line_no}: {link} -> {reason}")

    if not args.quiet:
        print(f"\nChecked {len(files)} markdown files; {failures} broken link(s).")
    if failures:
        print("Fix the links above, or update the doc that references them.")
        return 1
    if not args.quiet:
        print("All internal links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
