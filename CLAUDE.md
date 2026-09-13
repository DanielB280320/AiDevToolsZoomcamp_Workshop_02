# AGENTS.md

Guidance for AI coding agents working on **Kickboard**, a football league scoreboard app.

## Source of truth
- The product spec lives in `_docs/specs.md`. Read it before making changes and keep it updated when requirements change.

## Project layout
- `frontend/` — React app (sidebar of leagues, standings table, team detail view)
- `backend/` — FastAPI backend, managed with `uv`
- `_docs/` — specifications and design docs

## Makefile (run at the repository root)
- `make install` — install backend and frontend dependencies
- `make dev` — run backend and frontend together (or `make backend` / `make frontend` separately)
- `make test` — run all tests
- `make help` — list every target

## Frontend commands (run in `frontend/`)
- `npm install` — install dependencies
- `npm run dev` — start the dev server (http://localhost:5173)
- `npm test` — run the test suite (Vitest + Testing Library)
- `npm run build` — production build

All backend calls live in `frontend/src/api/kickboardApi.js`, which `fetch`es the backend at `VITE_API_BASE_URL`
(default `http://localhost:8000`; see `frontend/.env.example`). Start the backend before `npm run dev`.
Tests don't need it: `src/test/setup.js` stubs `fetch` with the in-memory mock in `frontend/src/api/mock/`.

## Backend commands (run in `backend/`)
- `uv sync` — install dependencies
- `uv run uvicorn app.main:app --reload` — start the API (http://localhost:8000, docs at `/docs`)
- `uv run pytest` — run the test suite

The API contract is `openapi.yaml` at the repository root; `backend/tests/test_contract.py` checks responses against it.
Data access goes through the `Repository` protocol (`backend/app/db/repository.py`), provided by `get_repository` in
`backend/app/db/__init__.py`. It currently returns an in-memory mock database (`backend/app/db/mock/`).

Endpoints read from a `DataSource` (`backend/app/sources.py`, dependency `get_data_source`):
- `API_FOOTBALL_KEY` set (e.g. in `backend/.env`, see `backend/.env.example`) → live data from API-Football
  (`backend/app/api_football/`). League presentation still comes from the repository; responses are cached in memory.
- Not set → `RepositorySource`, which serves the repository (mock).
Tests never hit the network: `conftest.py` forces the mock, and `tests/test_api_football.py` uses a fake provider.

## Conventions
- All frontend calls to the backend go through a single API/data-service module, so mocks can be swapped for the real backend (and later a real sports data API) without touching UI components.
- Backend: use `uv` for dependencies (`uv add`, `uv run`). Write endpoint tests first, then implement.
- Keep the database layer database-agnostic (SQLAlchemy).
- Keep changes small and focused; don't add features listed as out of scope in the spec.

## Before finishing a task
- Run the relevant tests and make sure they pass.
- Do not commit secrets or `.env` files.
