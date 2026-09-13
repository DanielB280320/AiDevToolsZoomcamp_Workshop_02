"""Maps API-Football data onto the Kickboard API's response shapes.

League presentation (name, region, colours) comes from the repository; standings, squads and results come
from the provider. Ids are scoped like the mock's: `{leagueId}--{providerTeamId}` for teams,
`{teamId}--{providerPlayerId}` for players and `{leagueId}--{providerFixtureId}` for matches.
"""

import re
import unicodedata
from dataclasses import asdict
from datetime import datetime

from app import schemas
from app.api_football.client import ApiFootballClient
from app.db import models
from app.db.repository import Repository
from app.services import RECENT_MATCHES, NotFoundError, ProviderError

# Kickboard league id -> API-Football league id.
LEAGUE_IDS = {
    "premier-league": 39,
    "la-liga": 140,
    "serie-a": 135,
    "bundesliga": 78,
    "brasileirao": 71,
    "liga-mx": 262,
    "mls": 253,
    "primera-division": 128,
    "champions-league": 2,
}

# Cache lifetimes in seconds, balancing freshness against the plan's daily request quota.
RESULTS_TTL = 30 * 60  # standings and fixtures
SEASON_STATS_TTL = 6 * 60 * 60  # player goals and assists
STATIC_TTL = 24 * 60 * 60  # current season, squads, finished match details

FINISHED = {"FT", "AET", "PEN"}
POSITIONS = {"Goalkeeper": "GK", "Defender": "DEF", "Midfielder": "MID", "Attacker": "FWD"}
MAX_MINUTES = 120
ROUND_NUMBER = re.compile(r" - (\d+)$")  # "Regular Season - 12"


class ApiFootballSource:
    def __init__(self, repository: Repository, client: ApiFootballClient):
        self._repository = repository
        self._client = client

    def list_leagues(self) -> list[schemas.League]:
        leagues = []
        for league in self._repository.list_leagues():
            if league.id not in LEAGUE_IDS:
                continue
            try:
                season = self._season(league)
            except ProviderError:
                season = None  # keep the sidebar usable; the standings request reports the error
            leagues.append(_league(league, season))
        return leagues

    def get_standings(self, league_id: str) -> schemas.Standings:
        league = self._league_record(league_id)
        if league is None:
            raise NotFoundError("League not found")
        season = self._season(league)
        return schemas.Standings(league=_league(league, season), teams=self._table(league, season))

    def get_team_detail(self, team_id: str) -> schemas.TeamDetail:
        league_id, _, club_id = team_id.partition("--")
        league = self._league_record(league_id)
        if league is None or not club_id.isdigit():
            raise NotFoundError("Team not found")
        season = self._season(league)
        team = next((row for row in self._table(league, season) if row.id == team_id), None)
        if team is None:
            raise NotFoundError("Team not found")

        return schemas.TeamDetail(
            team=team,
            league=_league(league, season),
            squad=self._squad(league, season, team_id, int(club_id)),
            recent_matches=self._recent_matches(league, season, int(club_id)),
        )

    def _league_record(self, league_id: str) -> models.League | None:
        return self._repository.get_league(league_id) if league_id in LEAGUE_IDS else None

    def _season(self, league: models.League) -> dict:
        items = self._client.get("/leagues", {"id": LEAGUE_IDS[league.id], "current": "true"}, STATIC_TTL)
        season = next((s for item in items for s in item["seasons"] if s.get("current")), None)
        if season is None:
            raise ProviderError(f"Sports data provider has no current season for {league.name}")
        return season

    def _table(self, league: models.League, season: dict) -> list[schemas.Team]:
        params = {"league": LEAGUE_IDS[league.id], "season": season["year"]}
        items = self._client.get("/standings", params, RESULTS_TTL)
        groups = [group for item in items for group in item["league"]["standings"]]
        teams = []
        for position, row in enumerate(pick_table(groups), start=1):
            record = row["all"]
            goals_for, goals_against = record["goals"]["for"] or 0, record["goals"]["against"] or 0
            teams.append(
                schemas.Team(
                    id=_team_id(league, row["team"]["id"]),
                    name=row["team"]["name"],
                    league_id=league.id,
                    crest=_crest(league, row["team"]),
                    position=position,
                    played=record["played"] or 0,
                    wins=record["win"] or 0,
                    draws=record["draw"] or 0,
                    losses=record["lose"] or 0,
                    goals_for=goals_for,
                    goals_against=goals_against,
                    goal_difference=goals_for - goals_against,
                    points=row["points"] or 0,
                )
            )
        return teams

    def _squad(self, league: models.League, season: dict, team_id: str, club_id: int) -> list[schemas.Player]:
        provider_league_id = LEAGUE_IDS[league.id]
        totals: dict[int, tuple[int, int]] = {}
        stats_params = {"team": club_id, "league": provider_league_id, "season": season["year"]}
        for item in self._client.get("/players", stats_params, SEASON_STATS_TTL):
            goals, assists = totals.get(item["player"]["id"], (0, 0))
            for stats in item["statistics"]:
                if stats["team"]["id"] == club_id and stats["league"]["id"] == provider_league_id:
                    goals += stats["goals"]["total"] or 0
                    assists += stats["goals"]["assists"] or 0
            totals[item["player"]["id"]] = (goals, assists)

        return [
            schemas.Player(
                id=f"{team_id}--{player['id']}",
                team_id=team_id,
                name=player["name"],
                position=POSITIONS[player["position"]],
                shirt_number=player.get("number") or None,
                goals=totals.get(player["id"], (0, 0))[0],
                assists=totals.get(player["id"], (0, 0))[1],
            )
            for squad in self._client.get("/players/squads", {"team": club_id}, STATIC_TTL)
            for player in squad["players"]
            if player.get("position") in POSITIONS
        ]

    def _recent_matches(self, league: models.League, season: dict, club_id: int) -> list[schemas.Match]:
        # One request for the whole league's season, shared by every team in it.
        params = {"league": LEAGUE_IDS[league.id], "season": season["year"]}
        played = [
            item
            for item in self._client.get("/fixtures", params, RESULTS_TTL)
            if item["fixture"]["status"]["short"] in FINISHED
            and club_id in (item["teams"]["home"]["id"], item["teams"]["away"]["id"])
        ]
        recent = sorted(played, key=lambda item: item["fixture"]["timestamp"], reverse=True)[:RECENT_MATCHES]
        if not recent:
            return []

        # Player statistics are only included when fixtures are requested by id.
        ids = "-".join(str(item["fixture"]["id"]) for item in recent)
        players = {item["fixture"]["id"]: item.get("players") or [] for item in self._client.get("/fixtures", {"ids": ids}, STATIC_TTL)}
        return [_match(league, item, players.get(item["fixture"]["id"], [])) for item in recent]


def pick_table(groups: list[list[dict]]) -> list[dict]:
    """Chooses the single table to show from the provider's groups (conferences, zones, Apertura/Clausura).

    A group containing every team is an overall table; the latest one with games played wins. Otherwise the
    groups split the teams between them (e.g. MLS conferences) and are merged into one ranking, ordered like
    services.compute_standings.
    """
    team_ids = {row["team"]["id"] for group in groups for row in group}
    overall = [group for group in groups if {row["team"]["id"] for row in group} == team_ids]
    if overall:
        started = [group for group in overall if any(row["all"]["played"] for row in group)]
        return sorted((started or overall)[-1], key=lambda row: row["rank"])

    rows = {row["team"]["id"]: row for group in groups for row in group}
    return sorted(
        rows.values(),
        key=lambda row: (-row["points"], -row["goalsDiff"], -(row["all"]["goals"]["for"] or 0), row["team"]["name"]),
    )


def _league(league: models.League, season: dict | None) -> schemas.League:
    fields = asdict(league)
    if season:
        start, end = season["start"][:4], season["end"][:4]
        fields["season"] = start if start == end else f"{start}–{end[2:]}"
    return schemas.League.model_validate(fields)


def _team_id(league: models.League, club_id: int) -> str:
    return f"{league.id}--{club_id}"


def _crest(league: models.League, team: dict) -> schemas.Crest:
    # The provider has no club colours, so the league's accent colour stands in.
    return schemas.Crest(code=_club_code(team["name"]), color=league.color, logo=team.get("logo") or None)


def _club_code(name: str) -> str:
    letters = "".join(c for c in unicodedata.normalize("NFKD", name) if c.isascii() and c.isalpha())
    return (letters or name)[:3].upper()


def _team_summary(league: models.League, team: dict) -> schemas.TeamSummary:
    return schemas.TeamSummary(id=_team_id(league, team["id"]), name=team["name"], crest=_crest(league, team))


def _match(league: models.League, item: dict, players: list[dict]) -> schemas.Match:
    home, away = item["teams"]["home"], item["teams"]["away"]
    round_number = ROUND_NUMBER.search(item["league"].get("round") or "")
    return schemas.Match(
        id=f"{league.id}--{item['fixture']['id']}",
        league_id=league.id,
        round=int(round_number[1]) if round_number else None,
        home_team_id=_team_id(league, home["id"]),
        away_team_id=_team_id(league, away["id"]),
        home_score=item["goals"]["home"],
        away_score=item["goals"]["away"],
        date=datetime.fromisoformat(item["fixture"]["date"]).date(),
        player_ratings=_player_ratings(league, players),
        home_team=_team_summary(league, home),
        away_team=_team_summary(league, away),
    )


def _player_ratings(league: models.League, players: list[dict]) -> list[schemas.PlayerRating]:
    ratings = []
    for side in players:
        team_id = _team_id(league, side["team"]["id"])
        for entry in side["players"]:
            for stats in entry["statistics"]:
                minutes, rating = stats["games"].get("minutes"), stats["games"].get("rating")
                if not minutes or rating is None:
                    continue  # didn't play, or too briefly to be rated
                ratings.append(
                    schemas.PlayerRating(
                        player_id=f"{team_id}--{entry['player']['id']}",
                        goals=stats["goals"].get("total") or 0,
                        assists=stats["goals"].get("assists") or 0,
                        rating=round(float(rating), 1),
                        minutes_played=min(minutes, MAX_MINUTES),
                    )
                )
    return ratings
