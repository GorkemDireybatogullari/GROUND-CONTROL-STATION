# GROUND-CONTROL-STATION — convenience targets.
# All real logic lives in scripts/; this is just a thin facade.

SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# ─── Help ───────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make \033[36m<target>\033[0m\n\nTargets:\n"} \
		/^[a-zA-Z0-9_.-]+:.*##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ─── Setup ──────────────────────────────────────────────────────────────────
.PHONY: install-system
install-system: ## Install OS-level deps (Ubuntu 22.04). Set INSTALL_ROS=1 for ROS2.
	./scripts/install-system-deps.sh

.PHONY: setup
setup: ## Bootstrap dev environment (npm + uv + hooks)
	./scripts/dev-setup.sh

# ─── Dev ────────────────────────────────────────────────────────────────────
.PHONY: dev
dev: ## Run Electron + backend together
	npm run dev:full

.PHONY: dev-frontend
dev-frontend: ## Run only the Electron/Vite dev stack
	npm run dev

.PHONY: dev-backend
dev-backend: ## Run only the FastAPI backend
	npm run backend

# ─── Quality ────────────────────────────────────────────────────────────────
.PHONY: format
format: ## Auto-format Python + JS/TS
	./scripts/format.sh

.PHONY: lint
lint: ## Run all linters (ruff, mypy, eslint, tsc)
	./scripts/lint.sh

.PHONY: test
test: ## Run pytest + vitest
	./scripts/test.sh

.PHONY: test-backend
test-backend: ## Run backend tests only
	cd backend && pytest

.PHONY: test-frontend
test-frontend: ## Run frontend tests only
	npm run test:run

.PHONY: test-e2e
test-e2e: ## Run Playwright e2e suite
	npm run test:e2e

.PHONY: typecheck
typecheck: ## Type-check JS/TS only
	npm run typecheck

# ─── Build ──────────────────────────────────────────────────────────────────
.PHONY: build
build: ## Build Electron app for current platform (override: PLATFORM=win|mac|linux)
	./scripts/build.sh $(or $(PLATFORM),linux)

# ─── Docker ─────────────────────────────────────────────────────────────────
.PHONY: docker-build
docker-build: ## Build backend Docker image
	docker compose build backend

.PHONY: docker-up
docker-up: ## Start backend container
	docker compose up backend

.PHONY: docker-down
docker-down: ## Stop containers
	docker compose down

# ─── Cleanup ────────────────────────────────────────────────────────────────
.PHONY: clean
clean: ## Remove build artefacts and caches
	./scripts/clean.sh

.PHONY: clean-deep
clean-deep: ## Same as clean, plus node_modules
	DEEP=1 ./scripts/clean.sh
