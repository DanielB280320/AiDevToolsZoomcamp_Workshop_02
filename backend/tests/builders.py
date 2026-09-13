"""Small constructors for hand-built test data, with sensible defaults."""

from datetime import date

from app.db.models import League, Match, Player, PlayerRating, Team
from app.db.sql import SqlRepository, create_database_engine

LEAGUE_ID = "test-league"


def database(leagues=(), teams=(), players=(), matches=()):
    """A fresh in-memory database holding just the given records."""
    repository = SqlRepository(create_database_engine("sqlite://"))
    repository.create_schema()
    repository.add(leagues=leagues, teams=teams, players=players, matches=matches)
    return repository


def league(id=LEAGUE_ID, **overrides):
    fields = {
        "id": id,
        "name": "Test League",
        "country": "Testland",
        "region": "Europe",
        "code": "TST",
        "logo": "https://example.com/league.png/small",
        "season": "2026",
        "color": "#123456",
    }
    return League(**(fields | overrides))


def team(id, league_id=LEAGUE_ID, **overrides):
    fields = {
        "id": id,
        "name": id.title(),
        "league_id": league_id,
        "crest_code": id[:3].upper(),
        "crest_color": "#ABCDEF",
        "crest_logo": f"https://example.com/{id}.png",
    }
    return Team(**(fields | overrides))


def player(id, team_id, position="FWD", shirt_number=9, name=None):
    return Player(id=id, team_id=team_id, name=name or id.title(), position=position, shirt_number=shirt_number)


def rating(player_id, goals=0, assists=0, rating=7.0, minutes_played=90):
    return PlayerRating(
        player_id=player_id, goals=goals, assists=assists, rating=rating, minutes_played=minutes_played
    )


def match(home, away, home_score, away_score, *, on=date(2026, 9, 1), league_id=LEAGUE_ID, round=1, ratings=()):
    return Match(
        id=f"{home}-v-{away}-{on.isoformat()}",
        league_id=league_id,
        round=round,
        home_team_id=home,
        away_team_id=away,
        home_score=home_score,
        away_score=away_score,
        date=on,
        player_ratings=list(ratings),
    )
