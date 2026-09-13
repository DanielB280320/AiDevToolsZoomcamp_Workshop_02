"""Business logic: turns stored records into the API's response shapes."""

from collections import Counter
from dataclasses import asdict, dataclass

from app import schemas
from app.db import models
from app.db.repository import Repository

POINTS_FOR_WIN = 3
RECENT_MATCHES = 5


class NotFoundError(Exception):
    """Raised when a requested resource doesn't exist; the API maps it to a 404."""


class ProviderError(Exception):
    """Raised when the external sports data provider fails and nothing is cached; the API maps it to a 503."""


@dataclass
class _Record:
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0

    def add(self, scored: int, conceded: int) -> None:
        self.played += 1
        self.goals_for += scored
        self.goals_against += conceded
        if scored > conceded:
            self.wins += 1
        elif scored < conceded:
            self.losses += 1
        else:
            self.draws += 1

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.wins * POINTS_FOR_WIN + self.draws


def list_leagues(repository: Repository) -> list[schemas.League]:
    return [_league(league) for league in repository.list_leagues()]


def get_standings(repository: Repository, league_id: str) -> schemas.Standings:
    league = repository.get_league(league_id)
    if league is None:
        raise NotFoundError("League not found")
    table = compute_standings(repository.list_teams(league_id), repository.list_matches(league_id))
    return schemas.Standings(league=_league(league), teams=table)


def get_team_detail(repository: Repository, team_id: str) -> schemas.TeamDetail:
    team = repository.get_team(team_id)
    if team is None:
        raise NotFoundError("Team not found")

    league = repository.get_league(team.league_id)
    league_teams = repository.list_teams(team.league_id)
    league_matches = repository.list_matches(team.league_id)
    team_matches = [m for m in league_matches if team_id in (m.home_team_id, m.away_team_id)]

    goals, assists = Counter(), Counter()
    for match in team_matches:
        for entry in match.player_ratings:
            goals[entry.player_id] += entry.goals
            assists[entry.player_id] += entry.assists
    squad = [
        schemas.Player.model_validate(asdict(player) | {"goals": goals[player.id], "assists": assists[player.id]})
        for player in repository.list_players(team_id)
    ]

    teams_by_id = {t.id: t for t in league_teams}
    recent = sorted(team_matches, key=lambda m: m.date, reverse=True)[:RECENT_MATCHES]

    return schemas.TeamDetail(
        team=next(row for row in compute_standings(league_teams, league_matches) if row.id == team_id),
        league=_league(league),
        squad=squad,
        recent_matches=[
            schemas.Match.model_validate(
                asdict(match)
                | {
                    "home_team": _team_summary(teams_by_id[match.home_team_id]),
                    "away_team": _team_summary(teams_by_id[match.away_team_id]),
                }
            )
            for match in recent
        ],
    )


def compute_standings(teams: list[models.Team], matches: list[models.Match]) -> list[schemas.Team]:
    """League table ranked by points, then goal difference, then goals scored, then name."""
    records = {team.id: _Record() for team in teams}
    for match in matches:
        records[match.home_team_id].add(match.home_score, match.away_score)
        records[match.away_team_id].add(match.away_score, match.home_score)

    def rank(team: models.Team):
        record = records[team.id]
        return -record.points, -record.goal_difference, -record.goals_for, team.name

    return [
        schemas.Team(
            id=team.id,
            name=team.name,
            league_id=team.league_id,
            crest=_crest(team),
            position=position,
            played=records[team.id].played,
            wins=records[team.id].wins,
            draws=records[team.id].draws,
            losses=records[team.id].losses,
            goals_for=records[team.id].goals_for,
            goals_against=records[team.id].goals_against,
            goal_difference=records[team.id].goal_difference,
            points=records[team.id].points,
        )
        for position, team in enumerate(sorted(teams, key=rank), start=1)
    ]


def _league(league: models.League) -> schemas.League:
    return schemas.League.model_validate(asdict(league))


def _crest(team: models.Team) -> schemas.Crest:
    return schemas.Crest(code=team.crest_code, color=team.crest_color, logo=team.crest_logo)


def _team_summary(team: models.Team) -> schemas.TeamSummary:
    return schemas.TeamSummary(id=team.id, name=team.name, crest=_crest(team))
