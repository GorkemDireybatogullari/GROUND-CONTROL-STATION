#!/usr/bin/env bash
# Auto-format the entire repo.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[format] ruff format (Python)..."
if command -v ruff >/dev/null 2>&1; then
    ruff format backend
    ruff check --fix backend
else
    (cd backend && uv run ruff format . && uv run ruff check --fix .)
fi

echo "[format] eslint --fix (JS/TS)..."
npm run lint:fix

echo "[format] Done."
