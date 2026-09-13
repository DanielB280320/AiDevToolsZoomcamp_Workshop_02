from datetime import date

from app.db.memory import InMemoryRepository
from tests.builders import league, match, player, rating, team


def standings_row(client, league_id, team_name):
    teams = client.get(f"/api/leagues/{league_id}/standings").json()["teams"]
    return next(t for t in teams if t["name"] == team_name)


def test_returns_team_league_squad_and_last_five_results(client):
    liverpool = standings_row(client, "premier-league", "Liverpool")

    response = client.get(f"/api/teams/{liverpool['id']}")

    assert response.status_code == 200
    detail = response.json()
    assert detail["team"] == liverpool
    assert detail["league"]["id"] == "premier-league"
    assert {p["position"] for p in detail["squad"]} == {"GK", "DEF", "MID", "FWD"}
    assert all(p["teamId"] == liverpool["id"] for p in detail["squad"])

    matches = detail["recentMatches"]
    assert len(matches) == 5
    dates = [m["date"] for m in matches]
    assert dates == sorted(dates, reverse=True)
    for m in matches:
        assert m["homeTeam"]["id"] == m["homeTeamId"]
        assert m["awayTeam"]["id"] == m["awayTeamId"]
        assert liverpool["id"] in (m["homeTeamId"], m["awayTeamId"])


def test_player_goals_add_up_to_team_goals(client):
    for row in client.get("/api/leagues/bundesliga/standings").json()["teams"]:
        detail = client.get(f"/api/teams/{row['id']}").json()
        squad_ids = {p["id"] for p in detail["squad"]}

        assert sum(p["goals"] for p in detail["squad"]) == row["goalsFor"]
        for m in detail["recentMatches"]:
            team_goals = m["homeScore"] if m["homeTeamId"] == row["id"] else m["awayScore"]
            player_goals = sum(r["goals"] for r in m["playerRatings"] if r["playerId"] in squad_ids)
            assert player_goals == team_goals


def test_a_club_is_a_separate_team_in_each_competition(client):
    domestic = standings_row(client, "premier-league", "Liverpool")
    continental = standings_row(client, "champions-league", "Liverpool")

    assert domestic["id"] != continental["id"]
    assert client.get(f"/api/teams/{domestic['id']}").json()["league"]["id"] == "premier-league"
    assert client.get(f"/api/teams/{continental['id']}").json()["league"]["id"] == "champions-league"


def test_recent_matches_are_the_five_newest_with_team_summaries(client_for):
    fixtures = [
        match("alpha", "bravo", 1, 0, on=date(2026, 8, day), round=day)
        for day in (3, 1, 7, 5, 2, 6)  # stored out of order on purpose
    ]
    unrelated = match("bravo", "charlie", 4, 4, on=date(2026, 8, 9), round=9)
    repository = InMemoryRepository(
        leagues=[league()],
        teams=[team("alpha"), team("bravo", crest_logo=None), team("charlie")],
        matches=[*fixtures, unrelated],
    )

    matches = client_for(repository).get("/api/teams/alpha").json()["recentMatches"]

    assert [m["date"] for m in matches] == ["2026-08-07", "2026-08-06", "2026-08-05", "2026-08-03", "2026-08-02"]
    assert matches[0] == {
        "id": "alpha-v-bravo-2026-08-07",
        "leagueId": "test-league",
        "round": 7,
        "homeTeamId": "alpha",
        "awayTeamId": "bravo",
        "homeScore": 1,
        "awayScore": 0,
        "date": "2026-08-07",
        "playerRatings": [],
        "homeTeam": {
            "id": "alpha",
            "name": "Alpha",
            "crest": {"code": "ALP", "color": "#ABCDEF", "logo": "https://example.com/alpha.png"},
        },
        "awayTeam": {"id": "bravo", "name": "Bravo", "crest": {"code": "BRA", "color": "#ABCDEF"}},
    }


def test_squad_season_totals_are_summed_from_match_ratings(client_for):
    repository = InMemoryRepository(
        leagues=[league()],
        teams=[team("alpha"), team("bravo")],
        players=[
            player("striker", "alpha", "FWD", 9),
            player("keeper", "alpha", "GK", 1),
            player("benchwarmer", "alpha", "MID", 20),
            player("opponent", "bravo", "FWD", 9),
        ],
        matches=[
            match(
                "alpha", "bravo", 2, 1, on=date(2026, 8, 1),
                ratings=[rating("striker", goals=2, rating=8.9), rating("keeper", assists=1), rating("opponent", goals=1)],
            ),
            match(
                "bravo", "alpha", 0, 1, on=date(2026, 8, 8),
                ratings=[rating("striker", goals=1, assists=0, minutes_played=70), rating("keeper", rating=7.5)],
            ),
        ],
    )

    detail = client_for(repository).get("/api/teams/alpha").json()

    assert sorted(detail["squad"], key=lambda p: p["id"]) == [
        {"id": "benchwarmer", "teamId": "alpha", "name": "Benchwarmer", "position": "MID", "shirtNumber": 20, "goals": 0, "assists": 0},
        {"id": "keeper", "teamId": "alpha", "name": "Keeper", "position": "GK", "shirtNumber": 1, "goals": 0, "assists": 1},
        {"id": "striker", "teamId": "alpha", "name": "Striker", "position": "FWD", "shirtNumber": 9, "goals": 3, "assists": 0},
    ]
    assert detail["recentMatches"][0]["playerRatings"] == [
        {"playerId": "striker", "goals": 1, "assists": 0, "rating": 7.0, "minutesPlayed": 70},
        {"playerId": "keeper", "goals": 0, "assists": 0, "rating": 7.5, "minutesPlayed": 90},
    ]


def test_unknown_team_is_a_404(client):
    response = client.get("/api/teams/no-such-team")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}
