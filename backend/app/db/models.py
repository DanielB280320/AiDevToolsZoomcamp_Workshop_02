"""Stored records. Derived values (standings, season totals) are computed in app/services.py, not stored."""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class League:
    id: str
    name: str
    country: str
    region: str
    code: str
    logo: str
    season: str
    color: str
    logo_background: str = "#ffffff"


@dataclass(frozen=True)
class Team:
    """A club's entry in one competition; the same club gets a separate Team per league."""

    id: str
    name: str
    league_id: str
    crest_code: str
    crest_color: str
    crest_logo: str | None = None


@dataclass(frozen=True)
class Player:
    id: str
    team_id: str
    name: str
    position: str
    shirt_number: int


@dataclass(frozen=True)
class PlayerRating:
    player_id: str
    goals: int
    assists: int
    rating: float
    minutes_played: int


@dataclass(frozen=True)
class Match:
    id: str
    league_id: str
    round: int
    home_team_id: str
    away_team_id: str
    home_score: int
    away_score: int
    date: date
    player_ratings: list[PlayerRating] = field(default_factory=list)
