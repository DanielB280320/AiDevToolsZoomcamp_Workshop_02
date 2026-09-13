"""Response models; they mirror components/schemas in the repository-root openapi.yaml."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Region = Literal["Europe", "Americas", "Continental"]
Position = Literal["GK", "DEF", "MID", "FWD"]


class Schema(BaseModel):
    """snake_case in Python, camelCase on the wire."""

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)


class League(Schema):
    id: str
    name: str
    country: str
    region: Region
    code: str
    logo: str
    logo_background: str
    season: str
    color: str


class Crest(Schema):
    code: str
    color: str
    logo: str | None = None


class TeamSummary(Schema):
    id: str
    name: str
    crest: Crest


class Team(Schema):
    id: str
    name: str
    league_id: str
    crest: Crest
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class Standings(Schema):
    league: League
    teams: list[Team]


class Player(Schema):
    id: str
    team_id: str
    name: str
    position: Position
    shirt_number: int | None = None
    goals: int
    assists: int


class PlayerRating(Schema):
    player_id: str
    goals: int
    assists: int
    rating: float
    minutes_played: int


class Match(Schema):
    id: str
    league_id: str
    round: int | None = None
    home_team_id: str
    away_team_id: str
    home_score: int
    away_score: int
    date: date
    player_ratings: list[PlayerRating]
    home_team: TeamSummary
    away_team: TeamSummary


class TeamDetail(Schema):
    team: Team
    league: League
    squad: list[Player]
    recent_matches: list[Match]


class Error(BaseModel):
    detail: str
