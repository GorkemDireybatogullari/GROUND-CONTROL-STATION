#!/usr/bin/env bash
# Lint the entire repo. Exits non-zero on any failure.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

failed=0

run_step() {
    local name="$1"; shift
    echo "[lint] $name..."
    if ! "$@"; then
        echo "[lint] FAILED: $name"
        failed=1
    fi
}

if command -v ruff >/dev/null 2>&1; then
    run_step "ruff check" ruff check backend
    run_step "ruff format --check" ruff format --check backend
else
    run_step "ruff check (via uv)" sh -c "cd backend && uv run ruff check ."
    run_step "ruff format --check (via uv)" sh -c "cd backend && uv run ruff format --check ."
fi

if command -v mypy >/dev/null 2>&1; then
    run_step "mypy" mypy --config-file backend/pyproject.toml backend
else
    run_step "mypy (via uv)" sh -c "cd backend && uv run mypy --config-file pyproject.toml ."
fi

run_step "eslint" npm run lint
run_step "tsc --noEmit" npm run typecheck

if [[ $failed -ne 0 ]]; then
    echo "[lint] One or more checks failed."
    exit 1
fi
echo "[lint] All checks passed."
