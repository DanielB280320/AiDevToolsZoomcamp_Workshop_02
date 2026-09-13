# Kickboard — Football League Scoreboard

Kickboard is a full-stack web app for following the standings of the world's major football competitions and
drilling into any team to see its season details. It was built for Homework 2 of the AI Dev Tools Zoomcamp
("Build and Ship an AI-Assisted Full-Stack App").

## What the app does

- **Sidebar of competitions**, grouped by region:
  - Europe: Premier League, La Liga, Serie A, Bundesliga
  - Americas: Brasileirão Série A, Liga MX, MLS, Primera División (Argentina)
  - Continental: UEFA Champions League
- **Standings table** for the selected league: position, crest, team, games played, W / D / L, goal difference
  and points.
- **Team detail view** (click a team row):
  - Top scorer of the season
  - Best player in the last match, ranked by a composite score:
    `goals × 4 + assists × 3 + rating × 2 + minutesPlayed / 90`
  - Full squad grouped by position (GK / DEF / MID / FWD)
  - Last 5 results with score, opponent and W/D/L
- **Shareable URLs**: the selected league and team are kept in the URL hash
  (`#/leagues/:leagueId/teams/:teamId`), so the browser Back button and links work.

The full product spec is in [`_docs/specs.md`](_docs/specs.md), and the API contract is in
[`openapi.yaml`](openapi.yaml).

## Architecture

```
┌──────────────────────┐   fetch (JSON)   ┌───────────────────────────┐
│ frontend/  (React)   │ ───────────────▶ │ backend/  (FastAPI)       │
│ Vite, port 5173      │                  │ port 8000, /api/*         │
│ src/api/kickboardApi │                  │                           │
└──────────────────────┘                  │  DataSource               │
                                          │   ├─ RepositorySource ──▶ SQL database (SQLAlchemy)
                                          │   │   (default)            SQLite file by default
                                          │   └─ ApiFootballSource ─▶ API-Football v3 (optional,
                                          │       (API_FOOTBALL_KEY)    needs an API key)
                                          └───────────────────────────┘
```

| Layer    | Tech                                                        | Location    |
|----------|-------------------------------------------------------------|-------------|
| Frontend | React 19, Vite 8, plain CSS; tests with Vitest + Testing Library | `frontend/` |
| Backend  | Python 3.13, FastAPI, managed with `uv`; tests with pytest  | `backend/`  |
| Database | SQLAlchemy 2 (database-agnostic), SQLite by default         | `backend/app/db/` |
| Contract | OpenAPI 3 spec, checked by the backend tests                | `openapi.yaml` |

API endpoints (read-only; interactive docs at http://localhost:8000/docs):

| Method | Path                                  | Returns                                    |
|--------|---------------------------------------|--------------------------------------------|
| GET    | `/api/leagues`                        | All competitions                           |
| GET    | `/api/leagues/{leagueId}/standings`   | League info + standings table              |
| GET    | `/api/teams/{teamId}`                 | Team, league, squad and last 5 matches     |

Key design points:

- Every frontend call to the backend goes through **one module**, `frontend/src/api/kickboardApi.js`, so the
  data source can change without touching the UI components.
- The backend reads data through a **`DataSource`** (`backend/app/sources.py`). Without an API key it serves the
  database, and with `API_FOOTBALL_KEY` set it serves live data from API-Football, mapped onto the same API
  contract. The frontend works the same way in both modes.
- Database access goes through a **`Repository`** protocol (`backend/app/db/repository.py`). It is implemented
  with SQLAlchemy and uses only portable column types, so switching databases only needs a driver and a
  `DATABASE_URL`.

## Running the project locally

### Prerequisites

- **Git**
- **Python 3.13+** and **[uv](https://docs.astral.sh/uv/getting-started/installation/)**. uv can install
  Python 3.13 for you.
- **Node.js 20.19+ or 22.12+** (required by Vite 8) and npm
- **make** (optional): the Makefile is a shortcut. Without `make` (for example on Windows without WSL), run the
  commands shown in the "Without make" column below.
- An internet connection in the browser, because club and league logos load from external image hosts (see
  Limitations).

### 1. Clone

```bash
git clone https://github.com/DanielB280320/AiDevToolsZoomcamp_Workshop_02.git
cd AiDevToolsZoomcamp_Workshop_02
```

### 2. Install, run and test

| Step                 | With make (repo root) | Without make                                                           |
|----------------------|-----------------------|------------------------------------------------------------------------|
| Install dependencies | `make install`        | `cd backend && uv sync` and `cd frontend && npm install`               |
| Start the backend    | `make backend`        | `cd backend && uv run uvicorn app.main:app --reload`                   |
| Start the frontend   | `make frontend`       | `cd frontend && npm run dev`                                           |
| Start both together  | `make dev`            | Run the two commands above in separate terminals                       |
| Run all tests        | `make test`           | `cd backend && uv run pytest` and `cd frontend && npm test`            |
| Production build     | `make build`          | `cd frontend && npm run build`                                         |
| List targets         | `make help`           |                                                                        |

Then open **http://localhost:5173**.

- **Start the backend before (or together with) the frontend.** The frontend has no data of its own at
  runtime. If the backend is down, it shows "Could not reach the Kickboard server."
- On first start, the backend creates `backend/kickboard.db` and fills it with the generated mock season. You
  don't need a separate database setup step.
- API docs (Swagger UI): http://localhost:8000/docs

### 3. Configuration (optional)

The app runs with no configuration. To change the defaults, copy the example files. **Never commit the real
`.env` files**; they are git-ignored.

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

| Variable                 | File            | Default                              | Purpose |
|--------------------------|-----------------|--------------------------------------|---------|
| `API_FOOTBALL_KEY`       | `backend/.env`  | *(empty)*                            | If set, serves live API-Football data instead of the database |
| `DATABASE_URL`           | `backend/.env`  | `sqlite:///backend/kickboard.db`     | Any SQLAlchemy URL (for example Postgres after `uv add psycopg`) |
| `KICKBOARD_CORS_ORIGINS` | `backend/.env`  | `http://localhost:5173`              | Comma-separated browser origins allowed to call the API |
| `VITE_API_BASE_URL`      | `frontend/.env` | `http://localhost:8000`              | Where the frontend sends its API calls |

`make backend` loads `backend/.env` automatically. If you start uvicorn yourself, export the variables first or
use `uv run --env-file .env uvicorn app.main:app --reload`.

### 4. Tests

- **Backend:** 42 pytest tests covering endpoints, the SQL repository, the API-Football adapter (with a fake
  provider) and an OpenAPI contract check. They use an in-memory SQLite database and never touch the network or
  your `kickboard.db`.
- **Frontend:** 64 Vitest tests. `fetch` is stubbed with an in-memory mock backend, so they don't need the
  backend running.
- Both suites pass at the time of writing. pytest prints 2 deprecation warnings that come from FastAPI/Starlette
  dependencies, not from project code.

## Limitations and things to know

### The data is mocked, not real

- **It wasn't possible to get real, current-season data during development, so the app serves generated mock
  data by default.** Club names and logos are real, but **players, squads, results, ratings and standings are fictional**
  and don't reflect any real season.
- The mock data is **deterministic** (seeded random generation in `backend/app/db/mock/generate.py`). Everyone
  who runs the project sees the same tables and players.
- The mock data is **static**. The simulated season ends on a fixed last matchday (2026-09-12), and nothing
  changes over time.
- The mock is **smaller than the real competitions**:
  - Each league has **10 teams** (real leagues have 18–20+). Domestic leagues have played 12 rounds.
  - The Champions League is simplified to one 10-team table after 8 rounds. Real knockout rounds and the
    36-team league phase are not modelled.
- Player names come from per-country name pools, so they sound plausible but are made up.

### Live data (API-Football) is implemented but effectively unavailable

- The integration in `backend/app/api_football/` runs when `API_FOOTBALL_KEY` is set. It is covered by tests
  against a fake provider, but it has **not been confirmed end-to-end with real current-season data**.
- The **free API-Football plan allows 100 requests/day and restricts which seasons you can access**, so current
  seasons are usually not available on it. Serving all 9 competitions with current data would likely need a paid
  plan.
- Even in live mode the app is **not real-time**. Responses are cached in memory (standings/results 30 min,
  player stats 6 h, seasons/squads/finished matches 24 h), and live match scores are out of scope. If the
  provider fails, the last cached copy is served; with nothing cached, the API returns `503`. The cache is lost
  when the backend restarts.
- The provider has no club colours, so in live mode the league colour is used as the accent. Players without a
  match rating are left out of "best player".

### Database

- There are **no migrations yet**. Tables are created with `create_all` at startup, and existing tables are not
  altered. If the schema or the mock generator changes, **delete `backend/kickboard.db`** so it is regenerated
  on the next start.
- Seeding only happens when the database is **empty**, so an existing database keeps its old data.
- Only SQLite has been used. Other databases (Postgres and others) should work through `DATABASE_URL` plus the
  matching driver, but they haven't been tested.

### Scope and other considerations

- **Read-only app:** there are only `GET` endpoints, and no way to add or edit teams, matches or results from
  the UI.
- **Out of scope** (per the spec): live score updates, user accounts, favourites, notifications, historical
  seasons and betting odds/predictions.
- The "best player" formula weights are **placeholders** and haven't been tuned.
- **Logos are hotlinked** from external hosts (`r2.thesportsdb.com`, `media.api-sports.io`). Offline, or if a
  host blocks the request, the UI falls back to a coloured badge with the club/league code.
- **CORS:** by default the backend only accepts requests from `http://localhost:5173`. If Vite starts on another
  port (for example 5174 because 5173 is busy), or you open the app through a different host, add that origin
  to `KICKBOARD_CORS_ORIGINS`, or the browser will block the API calls.
- `VITE_API_BASE_URL` is read when the frontend is built or started, so restart `npm run dev` (or rebuild) after
  changing it.
- The frontend has its own copy of the mock generator (`frontend/src/api/mock/`), used **only by the tests**. It
  mirrors the backend mock, so changes to one should be reflected in the other.
- **Not deployed:** there is no Dockerfile, CI pipeline or hosting setup. The project is meant to run locally,
  and the backend has no authentication or rate limiting.

## Project layout

```
.
├── _docs/specs.md          Product specification (source of truth)
├── openapi.yaml            API contract
├── Makefile                install / dev / test / build shortcuts
├── backend/
│   ├── app/
│   │   ├── main.py         FastAPI app, CORS, error handlers
│   │   ├── api.py          Routes (/api/...)
│   │   ├── sources.py      DataSource selection (database vs API-Football)
│   │   ├── services.py     Standings / team-detail logic
│   │   ├── api_football/   Live data client + adapter
│   │   └── db/             Repository, SQLAlchemy tables, mock data generator
│   └── tests/              pytest suite (in-memory SQLite, fake provider)
└── frontend/
    └── src/
        ├── api/            kickboardApi.js (only backend client) + test-only mock
        ├── components/     Sidebar, StandingsTable, TeamDetail, Crest, ...
        ├── hooks/          Async loading, hash routing
        └── lib/            Formatting, colours, team stats
```
