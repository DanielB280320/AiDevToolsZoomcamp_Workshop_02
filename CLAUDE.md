# AGENTS.md

Guidance for AI coding agents working on **Kickboard**, a football league scoreboard app.

## Source of truth
- The product spec lives in `_docs/specs.md`. Read it before making changes and keep it updated when requirements change.

## Project layout
- `frontend/` — React app (sidebar of leagues, standings table, team detail view)
- `backend/` — FastAPI backend, managed with `uv`
- `_docs/` — specifications and design docs

## Frontend commands (run in `frontend/`)
- `npm install` — install dependencies
- `npm run dev` — start the dev server (http://localhost:5173)
- `npm test` — run the test suite (Vitest + Testing Library)
- `npm run build` — production build

All backend calls live in `frontend/src/api/kickboardApi.js`, currently backed by the mock in `frontend/src/api/mock/`.

## Conventions
- All frontend calls to the backend go through a single API/data-service module, so mocks can be swapped for the real backend (and later a real sports data API) without touching UI components.
- Backend: use `uv` for dependencies (`uv add`, `uv run`). Write endpoint tests first, then implement.
- Keep the database layer database-agnostic (SQLAlchemy).
- Keep changes small and focused; don't add features listed as out of scope in the spec.

## Before finishing a task
- Run the relevant tests and make sure they pass.
- Do not commit secrets or `.env` files.
