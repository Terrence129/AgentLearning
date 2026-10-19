#!/usr/bin/env bash
# AgentLab task runner (macOS / Linux)
#
# Usage:
#   ./tasks.sh setup
#   ./tasks.sh test
#   ./tasks.sh week 2
#   ./tasks.sh doctor
#   ./tasks.sh fmt
#   ./tasks.sh solution 1      # copies the reference solution for week 1 (last resort!)
#
# Windows: use .\tasks.ps1 - it exposes the same subcommands.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

require_uv() {
    command -v uv >/dev/null 2>&1 || die "uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
}

format_week() {
    local value="${1:-}"
    [[ -n "$value" ]] || die "This command needs a week number, e.g. ./tasks.sh week 2"
    [[ "$value" =~ ^[0-9]+$ ]] || die "Week must be a number, got: $value"
    printf '%02d' "$((10#$value))"
}

run_allow_failure() {
    set +e
    "$@"
    local code=$?
    set -e
    return "$code"
}

cmd="${1:-help}"

case "$cmd" in
    help)
        cat <<'EOF'
AgentLab tasks (macOS / Linux)

  ./tasks.sh setup          Create the Python 3.12 env, install dev deps, copy .env if missing
  ./tasks.sh sync           Re-sync dependencies (pass --all-extras for all optional extras)
  ./tasks.sh doctor         Check toolchain, keys and directories
  ./tasks.sh test           Run the whole test suite
  ./tasks.sh week 2         Run only that week's tests
  ./tasks.sh fmt            Format with ruff
  ./tasks.sh lint           Lint with ruff
  ./tasks.sh check          Lint + format check + full tests (what CI runs)
  ./tasks.sh chat           Start the terminal chat (week 1 deliverable)
  ./tasks.sh solution 1     Copy the reference solution for week 1 into place
  ./tasks.sh clean          Remove caches and local runtime artifacts

First time here? Read START-HERE.md, then run: ./tasks.sh setup
EOF
        ;;
    setup)
        require_uv
        echo "[1/4] Installing Python 3.12 via uv..."
        uv python install 3.12
        echo "[2/4] Creating .venv and syncing dependencies..."
        uv sync --extra dev
        if [[ ! -f .env ]]; then
            cp .env.example .env
            echo "[3/4] Created .env from .env.example -- add your API keys."
        else
            echo "[3/4] .env already exists, leaving it alone."
        fi
        echo "[4/4] Running doctor..."
        if ! run_allow_failure uv run python -m agentlab.cli doctor; then
            echo
            echo "Doctor reported issues (expected until you add an API key)."
            echo "Edit .env, then run: ./tasks.sh doctor"
        fi
        echo
        echo "Setup done. Next: read START-HERE.md"
        ;;
    sync)
        require_uv
        if [[ "${2:-}" == "--all-extras" ]]; then
            uv sync --all-extras
        else
            uv sync --extra dev
        fi
        ;;
    doctor)
        require_uv
        run_allow_failure uv run python -m agentlab.cli doctor
        ;;
    test)
        require_uv
        run_allow_failure uv run pytest -q
        ;;
    labs)
        require_uv
        run_allow_failure uv run pytest -m week -v
        ;;
    week)
        require_uv
        week="$(format_week "${2:-}")"
        run_allow_failure uv run pytest "tests/week${week}" -m week -v
        ;;
    fmt)
        require_uv
        uv run ruff format .
        ;;
    lint)
        require_uv
        uv run ruff check --fix .
        ;;
    check)
        require_uv
        uv run ruff check .
        uv run ruff format --check .
        uv run pytest -q
        ;;
    chat)
        require_uv
        run_allow_failure uv run python -m agentlab.cli chat
        ;;
    solution)
        week="$(format_week "${2:-}")"
        src="solutions/week${week}"
        [[ -d "$src" ]] || die "No solution directory for week ${week} (${src})"
        if [[ "${3:-}" != "--force" ]]; then
            read -r -p "This copies the week ${week} reference solution over your code. Type 'yes' to continue: " answer
            [[ "$answer" == "yes" ]] || {
                echo "Cancelled."
                exit 0
            }
        fi
        cp -R "${src}/." "$ROOT/"
        echo "Copied week ${week} solution over the repo. Re-run the tests to confirm."
        ;;
    clean)
        rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage .pytest_tmp data traces
        find agentlab tests solutions scripts -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
        echo "Clean."
        ;;
    *)
        die "Unknown task: ${cmd}. Run ./tasks.sh help for the list."
        ;;
esac
