#!/usr/bin/env bash
# Build production artifacts (Vite renderer + Electron app).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PLATFORM="${1:-linux}"

echo "[build] Building Vite + main process..."
npm run build

case "$PLATFORM" in
    linux) npm run package:electron-app:linux ;;
    win|windows) npm run package:electron-app:win ;;
    mac|darwin) npm run package:electron-app:mac ;;
    *) echo "[build] Unknown platform: $PLATFORM (use linux|win|mac)"; exit 1 ;;
esac

echo "[build] Artifacts in dist/."
