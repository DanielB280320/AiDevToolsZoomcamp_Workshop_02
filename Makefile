.PHONY: help install install-backend install-frontend dev backend frontend test test-backend test-frontend build

help: ## Show available commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-18s %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies (uv)
	cd backend && uv sync

install-frontend: ## Install frontend dependencies (npm)
	cd frontend && npm install

dev: ## Run backend and frontend together (Ctrl+C stops both)
	$(MAKE) -j2 backend frontend

backend: ## Run the API at http://localhost:8000 (docs at /docs); loads backend/.env if present
	cd backend && uv run $(if $(wildcard backend/.env),--env-file .env) uvicorn app.main:app --reload

frontend: ## Run the dev server at http://localhost:5173
	cd frontend && npm run dev

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && uv run pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

build: ## Build the frontend for production
	cd frontend && npm run build
