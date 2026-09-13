from collections.abc import Iterable

from app.db.models import League, Match, Player, Team


class InMemoryRepository:
    """Mock database: holds records in lists and returns them in insertion order."""

    def __init__(
        self,
        leagues: Iterable[League] = (),
        teams: Iterable[Team] = (),
        players: Iterable[Player] = (),
        matches: Iterable[Match] = (),
    ):
        self._leagues = {league.id: league for league in leagues}
        self._teams = {team.id: team for team in teams}
        self._players = list(players)
        self._matches = list(matches)

    def list_leagues(self) -> list[League]:
        return list(self._leagues.values())

    def get_league(self, league_id: str) -> League | None:
        return self._leagues.get(league_id)

    def list_teams(self, league_id: str) -> list[Team]:
        return [team for team in self._teams.values() if team.league_id == league_id]

    def get_team(self, team_id: str) -> Team | None:
        return self._teams.get(team_id)

    def list_players(self, team_id: str) -> list[Player]:
        return [player for player in self._players if player.team_id == team_id]

    def list_matches(self, league_id: str) -> list[Match]:
        return [match for match in self._matches if match.league_id == league_id]
