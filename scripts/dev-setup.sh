#!/usr/bin/env bash
# One-shot dev environment bootstrap.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[dev-setup] Repo: $REPO_ROOT"

# 1. .env
if [[ ! -f .env ]]; then
    cp .env.example .env
    echo "[dev-setup] Created .env from .env.example (edit as needed)."
fi

# 2. Frontend deps
echo "[dev-setup] Installing npm dependencies..."
npm install

# 3. Backend deps via uv (creates .venv automatically)
if command -v uv >/dev/null 2>&1; then
    echo "[dev-setup] Installing backend Python deps via uv..."
    (cd backend && uv venv --python 3.10 && uv pip install -e ".[dev]")
else
    echo "[dev-setup] uv not found. Falling back to python3.10 + pip..."
    if [[ ! -d backend/.venv ]]; then
        python3.10 -m venv backend/.venv
    fi
    # shellcheck disable=SC1091
    source backend/.venv/bin/activate
    pip install --upgrade pip
    pip install -e "backend[dev]"
fi

# 4. Pre-commit hooks
if command -v pre-commit >/dev/null 2>&1; then
    echo "[dev-setup] Installing pre-commit hooks..."
    pre-commit install
else
    echo "[dev-setup] pre-commit not installed (optional). 'pip install pre-commit' to enable."
fi

# 5. simple-git-hooks (already configured in package.json)
npx simple-git-hooks || true

echo
echo "[dev-setup] Done. Try:"
echo "  npm run dev:full      # Electron + backend"
echo "  make test             # all tests"
