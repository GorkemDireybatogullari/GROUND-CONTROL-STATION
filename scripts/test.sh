#!/usr/bin/env bash
# Run all test suites.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[test] pytest..."
if command -v pytest >/dev/null 2>&1; then
    (cd backend && pytest)
else
    (cd backend && uv run pytest)
fi

echo "[test] vitest..."
npm run test:run

echo "[test] Done."
