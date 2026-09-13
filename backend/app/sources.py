"""Where the API's data comes from: live API-Football data when a key is configured, the repository otherwise."""

import os
from functools import cache
from typing import Protocol

from app import schemas, services
from app.api_football import ApiFootballClient, ApiFootballSource
from app.db import get_repository
from app.db.repository import Repository


class DataSource(Protocol):
    def list_leagues(self) -> list[schemas.League]: ...

    def get_standings(self, league_id: str) -> schemas.Standings: ...

    def get_team_detail(self, team_id: str) -> schemas.TeamDetail: ...


class RepositorySource:
    """Serves stored records, deriving standings and season totals from the stored matches."""

    def __init__(self, repository: Repository):
        self._repository = repository

    def list_leagues(self) -> list[schemas.League]:
        return services.list_leagues(self._repository)

    def get_standings(self, league_id: str) -> schemas.Standings:
        return services.get_standings(self._repository, league_id)

    def get_team_detail(self, team_id: str) -> schemas.TeamDetail:
        return services.get_team_detail(self._repository, team_id)


@cache
def _api_football_source(api_key: str) -> ApiFootballSource:
    # Cached so the HTTP connection pool and response cache live as long as the app.
    return ApiFootballSource(get_repository(), ApiFootballClient(api_key))


def get_data_source() -> DataSource:
    """FastAPI dependency. Set API_FOOTBALL_KEY for live data; without it the mock database is served."""
    api_key = os.environ.get("API_FOOTBALL_KEY", "").strip()
    return _api_football_source(api_key) if api_key else RepositorySource(get_repository())
