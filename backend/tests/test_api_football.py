"""The API served from live API-Football data, against a fake provider (no network, no API key)."""

from datetime import datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api_football import ApiFootballClient, ApiFootballSource
from app.db.memory import InMemoryRepository
from app.main import app
from app.sources import RepositorySource, get_data_source
from tests.builders import league
from tests.test_contract import assert_matches_schema

PREMIER_LEAGUE, MLS, ARGENTINA, LIGA_MX = 39, 253, 128, 262
LIVERPOOL, ARSENAL, CHELSEA = 40, 42, 49


class FakeApiFootball:
    """Answers API-Football v3 requests from canned responses, on a clock the test controls."""

    def __init__(self):
        self.responses = {}
        self.requests = []
        self.now = 0.0

    def on(self, path, response, **params):
        """`response` is the list of `response` items, a whole body (errors, paging), an httpx.Response or an exception."""
        self.responses[(path, frozenset((key, str(value)) for key, value in params.items()))] = response

    def handle(self, request):
        self.requests.append(request)
        key = (request.url.path, frozenset(request.url.params.items()))
        if key not in self.responses:
            raise AssertionError(f"Unexpected request: {request.url}")
        response = self.responses[key]
        if isinstance(response, Exception):
            raise response
        if isinstance(response, httpx.Response):
            return response
        if isinstance(response, list):
            response = {"errors": [], "paging": {"current": 1, "total": 1}, "response": response}
        return httpx.Response(200, json=response)

    def paths(self):
        return [request.url.path for request in self.requests]


@pytest.fixture
def provider():
    return FakeApiFootball()


@pytest.fixture
def api(provider):
    repository = InMemoryRepository(
        leagues=[
            league("premier-league", name="Premier League", season="2025–26", color="#3D1159"),
            league("mls", name="MLS", region="Americas", season="2025"),
            league("primera-division", name="Primera División", region="Americas"),
            league("liga-mx", name="Liga MX", region="Americas"),
        ]
    )
    client = ApiFootballClient("secret-key", transport=httpx.MockTransport(provider.handle), clock=lambda: provider.now)
    app.dependency_overrides[get_data_source] = lambda: ApiFootballSource(repository, client)
    yield TestClient(app)
    app.dependency_overrides.clear()


def serve_season(provider, league_id, start, end):
    seasons = [{"year": int(start[:4]), "start": start, "end": end, "current": True}]
    provider.on("/leagues", [{"league": {"id": league_id}, "seasons": seasons}], id=league_id, current="true")


def row(rank, club, name, win, draw, lose, goals_for, goals_against, *, points=None, group="League"):
    return {
        "rank": rank,
        "team": team(club, name),
        "points": win * 3 + draw if points is None else points,
        "goalsDiff": goals_for - goals_against,
        "group": group,
        "all": {
            "played": win + draw + lose,
            "win": win,
            "draw": draw,
            "lose": lose,
            "goals": {"for": goals_for, "against": goals_against},
        },
    }


def standings(league_id, *groups):
    return [{"league": {"id": league_id, "season": 2026, "standings": list(groups)}}]


def team(club, name):
    return {"id": club, "name": name, "logo": f"https://media.api-sports.io/football/teams/{club}.png"}


def fixture(id, home, away, score, day, *, status="FT", round="Regular Season - 1"):
    kickoff = datetime.fromisoformat(f"{day}T19:30:00+00:00")
    return {
        "fixture": {"id": id, "date": kickoff.isoformat(), "timestamp": int(kickoff.timestamp()), "status": {"short": status}},
        "league": {"id": PREMIER_LEAGUE, "season": 2026, "round": round},
        "teams": {"home": home, "away": away},
        "goals": {"home": score[0], "away": score[1]},
    }


def lineup(club, *players):
    return {"team": {"id": club}, "players": list(players)}


def played(player_id, name, *, minutes=90, rating="7.0", goals=None, assists=None):
    games = {"minutes": minutes, "rating": rating}
    return {"player": {"id": player_id, "name": name}, "statistics": [{"games": games, "goals": {"total": goals, "assists": assists}}]}


def season_stats(player_id, *, goals=None, assists=None):
    stats = {"team": {"id": LIVERPOOL}, "league": {"id": PREMIER_LEAGUE}, "goals": {"total": goals, "assists": assists}}
    return {"player": {"id": player_id}, "statistics": [stats]}


def serve_premier_league(provider):
    serve_season(provider, PREMIER_LEAGUE, "2026-08-15", "2027-05-23")
    table = [
        row(1, LIVERPOOL, "Liverpool", 3, 1, 0, 9, 2),
        row(2, ARSENAL, "Arsenal", 3, 0, 1, 7, 3),
        row(3, CHELSEA, "Chelsea", 1, 1, 2, 4, 6, points=1),  # after a points deduction
    ]
    provider.on("/standings", standings(PREMIER_LEAGUE, table), league=PREMIER_LEAGUE, season=2026)


def test_leagues_show_the_providers_current_season(api, provider):
    serve_season(provider, PREMIER_LEAGUE, "2026-08-15", "2027-05-23")
    serve_season(provider, MLS, "2026-02-21", "2026-11-07")
    serve_season(provider, ARGENTINA, "2026-01-23", "2026-12-14")
    serve_season(provider, LIGA_MX, "2026-07-10", "2027-05-25")

    response = api.get("/api/leagues")

    assert response.status_code == 200
    leagues = response.json()
    assert [(item["id"], item["season"]) for item in leagues] == [
        ("premier-league", "2026–27"),
        ("mls", "2026"),
        ("primera-division", "2026"),
        ("liga-mx", "2026–27"),
    ]
    assert leagues[0]["color"] == "#3D1159"
    for item in leagues:
        assert_matches_schema("League", item)
    assert {request.headers["x-apisports-key"] for request in provider.requests} == {"secret-key"}


def test_leagues_fall_back_to_the_stored_season_when_the_provider_fails(api, provider):
    for league_id in (PREMIER_LEAGUE, MLS, ARGENTINA, LIGA_MX):
        provider.on("/leagues", httpx.ConnectError("unreachable"), id=league_id, current="true")

    response = api.get("/api/leagues")

    assert response.status_code == 200
    assert response.json()[0]["season"] == "2025–26"


def test_standings_are_the_providers_table(api, provider):
    serve_premier_league(provider)

    body = api.get("/api/leagues/premier-league/standings").json()

    assert_matches_schema("Standings", body)
    assert body["league"]["season"] == "2026–27"
    assert body["teams"][0] == {
        "id": "premier-league--40",
        "name": "Liverpool",
        "leagueId": "premier-league",
        "crest": {"code": "LIV", "color": "#3D1159", "logo": "https://media.api-sports.io/football/teams/40.png"},
        "position": 1,
        "played": 4,
        "wins": 3,
        "draws": 1,
        "losses": 0,
        "goalsFor": 9,
        "goalsAgainst": 2,
        "goalDifference": 7,
        "points": 10,
    }
    assert [(t["position"], t["name"], t["points"]) for t in body["teams"]] == [
        (1, "Liverpool", 10),
        (2, "Arsenal", 9),
        (3, "Chelsea", 1),
    ]


def test_conference_tables_are_merged_into_one_ranking(api, provider):
    serve_season(provider, MLS, "2026-02-21", "2026-11-07")
    east = [
        row(1, 1601, "Columbus Crew", 5, 0, 1, 12, 5, group="Eastern Conference"),
        row(2, 1602, "Orlando City", 3, 1, 2, 8, 8, group="Eastern Conference"),
    ]
    west = [
        row(1, 1603, "LAFC", 5, 0, 1, 11, 4, group="Western Conference"),
        row(2, 1604, "LA Galaxy", 4, 1, 1, 9, 6, group="Western Conference"),
    ]
    provider.on("/standings", standings(MLS, east, west), league=MLS, season=2026)

    teams = api.get("/api/leagues/mls/standings").json()["teams"]

    assert [(t["position"], t["name"]) for t in teams] == [
        (1, "Columbus Crew"),  # level with LAFC on points and goal difference, more goals scored
        (2, "LAFC"),
        (3, "LA Galaxy"),
        (4, "Orlando City"),
    ]


def test_a_table_of_every_team_is_preferred_over_zones(api, provider):
    serve_season(provider, ARGENTINA, "2026-01-23", "2026-12-14")
    zone_a = [row(1, 435, "River Plate", 4, 0, 0, 10, 2, group="Zona A")]
    zone_b = [row(1, 451, "Boca Juniors", 3, 1, 0, 8, 3, group="Zona B")]
    annual = [
        row(1, 451, "Boca Juniors", 9, 3, 1, 22, 9, group="Tabla Anual"),
        row(2, 435, "River Plate", 8, 2, 3, 20, 12, group="Tabla Anual"),
    ]
    provider.on("/standings", standings(ARGENTINA, zone_a, zone_b, annual), league=ARGENTINA, season=2026)

    teams = api.get("/api/leagues/primera-division/standings").json()["teams"]

    assert [(t["name"], t["played"]) for t in teams] == [("Boca Juniors", 13), ("River Plate", 13)]


def test_the_latest_phase_with_games_played_is_shown(api, provider):
    serve_season(provider, LIGA_MX, "2026-07-10", "2027-05-25")
    apertura = [
        row(1, 2287, "Toluca", 5, 1, 0, 14, 4, group="Apertura"),
        row(2, 2283, "Club América", 4, 1, 1, 11, 6, group="Apertura"),
    ]
    clausura = [
        row(1, 2283, "Club América", 0, 0, 0, 0, 0, group="Clausura"),
        row(2, 2287, "Toluca", 0, 0, 0, 0, 0, group="Clausura"),
    ]
    provider.on("/standings", standings(LIGA_MX, apertura, clausura), league=LIGA_MX, season=2026)

    teams = api.get("/api/leagues/liga-mx/standings").json()["teams"]

    assert [(t["name"], t["points"]) for t in teams] == [("Toluca", 16), ("Club América", 13)]


def test_team_detail_combines_squad_season_stats_and_rated_recent_matches(api, provider):
    serve_premier_league(provider)
    liverpool, arsenal, chelsea = team(LIVERPOOL, "Liverpool"), team(ARSENAL, "Arsenal"), team(CHELSEA, "Chelsea")
    season = [
        fixture(1, liverpool, arsenal, (2, 0), "2026-08-16"),
        fixture(3, liverpool, chelsea, (3, 1), "2026-08-30", round="Regular Season - 3"),
        fixture(4, arsenal, chelsea, (2, 1), "2026-08-30", round="Regular Season - 3"),  # not Liverpool's
        fixture(5, arsenal, liverpool, (0, 1), "2026-09-13", round="Regular Season - 5"),
        fixture(6, liverpool, arsenal, (None, None), "2026-09-20", status="NS", round="Regular Season - 6"),
        fixture(2, chelsea, liverpool, (1, 1), "2026-08-23", round="Regular Season - 2"),
        fixture(7, liverpool, chelsea, (2, 2), "2026-09-06", round="Regular Season - 4"),
        fixture(8, arsenal, liverpool, (1, 3), "2026-08-20", round="Play-offs"),
    ]
    provider.on("/fixtures", season, league=PREMIER_LEAGUE, season=2026)
    by_id = {f["fixture"]["id"]: f for f in season}
    last_match_players = [
        lineup(ARSENAL, played(1100, "Bukayo Saka", rating="6.4")),
        lineup(
            LIVERPOOL,
            played(306, "Mohamed Salah", goals=1, rating="8.1"),
            played(1600, "Alisson Becker", minutes=120, rating="7.2"),
            played(2000, "Late Sub", minutes=4, rating=None),  # too brief to be rated
            played(2001, "Unused Sub", minutes=None, rating=None),
        ),
    ]
    details = [by_id[5] | {"players": last_match_players}, *(by_id[i] | {"players": []} for i in (7, 3, 2, 8))]
    provider.on("/fixtures", details, ids="5-7-3-2-8")
    squad = [
        {"id": 1600, "name": "Alisson Becker", "number": 1, "position": "Goalkeeper"},
        {"id": 306, "name": "Mohamed Salah", "number": 11, "position": "Attacker"},
        {"id": 2000, "name": "Late Sub", "number": None, "position": "Midfielder"},
        {"id": 2002, "name": "Virgil van Dijk", "number": 4, "position": "Defender"},
    ]
    provider.on("/players/squads", [{"team": liverpool, "players": squad}], team=LIVERPOOL)
    params = {"team": LIVERPOOL, "league": PREMIER_LEAGUE, "season": 2026}
    first_page = [season_stats(306, goals=4, assists=2), season_stats(1600)]
    provider.on("/players", {"errors": [], "paging": {"current": 1, "total": 2}, "response": first_page}, **params)
    second_page = [season_stats(2002, goals=1)]
    provider.on("/players", {"errors": [], "paging": {"current": 2, "total": 2}, "response": second_page}, **params, page=2)

    response = api.get("/api/teams/premier-league--40")

    assert response.status_code == 200
    detail = response.json()
    assert_matches_schema("TeamDetail", detail)
    assert detail["team"]["name"] == "Liverpool"
    assert detail["league"]["id"] == "premier-league"
    player = {"teamId": "premier-league--40"}
    assert detail["squad"] == [
        player | {"id": "premier-league--40--1600", "name": "Alisson Becker", "position": "GK", "shirtNumber": 1, "goals": 0, "assists": 0},
        player | {"id": "premier-league--40--306", "name": "Mohamed Salah", "position": "FWD", "shirtNumber": 11, "goals": 4, "assists": 2},
        player | {"id": "premier-league--40--2000", "name": "Late Sub", "position": "MID", "goals": 0, "assists": 0},
        player | {"id": "premier-league--40--2002", "name": "Virgil van Dijk", "position": "DEF", "shirtNumber": 4, "goals": 1, "assists": 0},
    ]

    matches = detail["recentMatches"]
    assert [m["id"] for m in matches] == [f"premier-league--{i}" for i in (5, 7, 3, 2, 8)]
    assert matches[0] == {
        "id": "premier-league--5",
        "leagueId": "premier-league",
        "round": 5,
        "homeTeamId": "premier-league--42",
        "awayTeamId": "premier-league--40",
        "homeScore": 0,
        "awayScore": 1,
        "date": "2026-09-13",
        "playerRatings": [
            {"playerId": "premier-league--42--1100", "goals": 0, "assists": 0, "rating": 6.4, "minutesPlayed": 90},
            {"playerId": "premier-league--40--306", "goals": 1, "assists": 0, "rating": 8.1, "minutesPlayed": 90},
            {"playerId": "premier-league--40--1600", "goals": 0, "assists": 0, "rating": 7.2, "minutesPlayed": 120},
        ],
        "homeTeam": {
            "id": "premier-league--42",
            "name": "Arsenal",
            "crest": {"code": "ARS", "color": "#3D1159", "logo": "https://media.api-sports.io/football/teams/42.png"},
        },
        "awayTeam": {
            "id": "premier-league--40",
            "name": "Liverpool",
            "crest": {"code": "LIV", "color": "#3D1159", "logo": "https://media.api-sports.io/football/teams/40.png"},
        },
    }
    assert "round" not in matches[4]  # "Play-offs" has no round number


@pytest.mark.parametrize("team_id", ["premier-league--99", "premier-league--liverpool", "liverpool", "serie-x--40"])
def test_unknown_team_is_a_404(api, provider, team_id):
    serve_premier_league(provider)

    response = api.get(f"/api/teams/{team_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


def test_unknown_league_is_a_404(api):
    response = api.get("/api/leagues/serie-x/standings")

    assert response.status_code == 404
    assert response.json() == {"detail": "League not found"}


def test_provider_errors_are_a_503_with_the_providers_message(api, provider):
    serve_premier_league(provider)
    limit_reached = {"errors": {"requests": "You have reached the request limit for the day"}, "response": []}
    provider.on("/standings", limit_reached, league=PREMIER_LEAGUE, season=2026)

    response = api.get("/api/leagues/premier-league/standings")

    assert response.status_code == 503
    assert response.json() == {"detail": "Sports data provider error: You have reached the request limit for the day"}
    assert_matches_schema("Error", response.json())


def test_an_invalid_api_key_is_a_503_explaining_why(api, provider):
    rejected = {"errors": {"token": "Invalid API key, please check your request and credentials.", "error": "4xSe"}}
    provider.on("/leagues", httpx.Response(403, json=rejected), id=PREMIER_LEAGUE, current="true")

    response = api.get("/api/leagues/premier-league/standings")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Sports data provider error: Invalid API key, please check your request and credentials."
    }


def test_a_provider_server_error_is_a_503(api, provider):
    provider.on("/leagues", httpx.Response(500, text="Internal Server Error"), id=PREMIER_LEAGUE, current="true")

    response = api.get("/api/leagues/premier-league/standings")

    assert response.status_code == 503
    assert response.json() == {"detail": "Sports data provider is unavailable"}


def test_an_unreachable_provider_is_a_503(api, provider):
    provider.on("/leagues", httpx.ConnectError("unreachable"), id=PREMIER_LEAGUE, current="true")

    response = api.get("/api/leagues/premier-league/standings")

    assert response.status_code == 503
    assert response.json() == {"detail": "Sports data provider is unavailable"}


def test_responses_are_cached_until_they_expire(api, provider):
    serve_premier_league(provider)

    for _ in range(3):
        api.get("/api/leagues/premier-league/standings")
    assert provider.paths() == ["/leagues", "/standings"]

    provider.now += 60 * 60  # an hour later the table is refreshed; the season isn't
    api.get("/api/leagues/premier-league/standings")
    assert provider.paths() == ["/leagues", "/standings", "/standings"]


def test_a_stale_copy_is_served_when_the_provider_fails(api, provider):
    serve_premier_league(provider)
    fresh = api.get("/api/leagues/premier-league/standings").json()

    provider.now += 60 * 60
    provider.on("/standings", httpx.ReadTimeout("slow"), league=PREMIER_LEAGUE, season=2026)
    response = api.get("/api/leagues/premier-league/standings")

    assert response.status_code == 200
    assert response.json() == fresh


def test_live_data_is_used_only_when_an_api_key_is_configured(monkeypatch):
    monkeypatch.delenv("API_FOOTBALL_KEY", raising=False)
    assert isinstance(get_data_source(), RepositorySource)

    monkeypatch.setenv("API_FOOTBALL_KEY", "secret-key")
    assert isinstance(get_data_source(), ApiFootballSource)
