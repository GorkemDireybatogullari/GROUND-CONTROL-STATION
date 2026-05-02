#!/usr/bin/env bash
# Wipe build artefacts, caches, and virtualenvs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[clean] Removing build/ dist/ release/ caches..."
rm -rf \
    dist \
    build \
    release \
    coverage \
    htmlcov \
    test-results \
    playwright-report \
    node_modules/.vite \
    backend/.venv \
    backend/.pytest_cache \
    backend/.mypy_cache \
    backend/.ruff_cache \
    backend/.coverage

find . -type d -name __pycache__ -not -path "./node_modules/*" -prune -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./node_modules/*" -delete 2>/dev/null || true

if [[ "${DEEP:-0}" == "1" ]]; then
    echo "[clean] DEEP=1 set — removing node_modules/..."
    rm -rf node_modules
fi

echo "[clean] Done."
