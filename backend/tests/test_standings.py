from tests.builders import database, league, match, team


def test_every_league_has_a_consistent_ordered_table(client):
    for item in client.get("/api/leagues").json():
        response = client.get(f"/api/leagues/{item['id']}/standings")

        assert response.status_code == 200
        body = response.json()
        assert body["league"] == item
        teams = body["teams"]
        assert len(teams) == 10
        assert [t["position"] for t in teams] == list(range(1, len(teams) + 1))
        assert [t["points"] for t in teams] == sorted((t["points"] for t in teams), reverse=True)
        for row in teams:
            assert row["leagueId"] == item["id"]
            assert row["played"] > 0
            assert row["wins"] + row["draws"] + row["losses"] == row["played"]
            assert row["points"] == row["wins"] * 3 + row["draws"]
            assert row["goalDifference"] == row["goalsFor"] - row["goalsAgainst"]


def test_ranks_by_points_then_goal_difference_then_goals_scored_then_name(client_for):
    names = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel"]
    repository = database(
        leagues=[league()],
        teams=[team(name) for name in names],
        matches=[
            match("alpha", "echo", 2, 0),  # alpha: 3 pts, GD +2, GF 2
            match("bravo", "foxtrot", 3, 1),  # bravo: 3 pts, GD +2, GF 3 -> above alpha on goals scored
            match("charlie", "delta", 1, 1),  # level on everything -> charlie above delta by name
            match("golf", "hotel", 1, 0),  # golf: 3 pts, GD +1 -> below alpha on goal difference
        ],
    )

    teams = client_for(repository).get("/api/leagues/test-league/standings").json()["teams"]

    assert [t["id"] for t in teams] == ["bravo", "alpha", "golf", "charlie", "delta", "hotel", "foxtrot", "echo"]


def test_rows_are_computed_from_this_leagues_matches_only(client_for):
    repository = database(
        leagues=[league(), league("other-league")],
        teams=[
            team("alpha"),
            team("bravo"),
            team("idle"),
            team("outsider", league_id="other-league"),
            team("rival", league_id="other-league"),
        ],
        matches=[
            match("alpha", "bravo", 3, 1),
            match("bravo", "alpha", 2, 2),
            match("outsider", "rival", 5, 0, league_id="other-league"),
        ],
    )

    body = client_for(repository).get("/api/leagues/test-league/standings").json()

    assert body["league"]["id"] == "test-league"
    assert body["teams"] == [
        {
            "id": "alpha",
            "name": "Alpha",
            "leagueId": "test-league",
            "crest": {"code": "ALP", "color": "#ABCDEF", "logo": "https://example.com/alpha.png"},
            "position": 1,
            "played": 2,
            "wins": 1,
            "draws": 1,
            "losses": 0,
            "goalsFor": 5,
            "goalsAgainst": 3,
            "goalDifference": 2,
            "points": 4,
        },
        {
            "id": "bravo",
            "name": "Bravo",
            "leagueId": "test-league",
            "crest": {"code": "BRA", "color": "#ABCDEF", "logo": "https://example.com/bravo.png"},
            "position": 2,
            "played": 2,
            "wins": 0,
            "draws": 1,
            "losses": 1,
            "goalsFor": 3,
            "goalsAgainst": 5,
            "goalDifference": -2,
            "points": 1,
        },
        {
            "id": "idle",
            "name": "Idle",
            "leagueId": "test-league",
            "crest": {"code": "IDL", "color": "#ABCDEF", "logo": "https://example.com/idle.png"},
            "position": 3,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goalsFor": 0,
            "goalsAgainst": 0,
            "goalDifference": 0,
            "points": 0,
        },
    ]


def test_crest_logo_is_omitted_when_missing(client_for):
    repository = database(leagues=[league()], teams=[team("alpha", crest_logo=None)])

    teams = client_for(repository).get("/api/leagues/test-league/standings").json()["teams"]

    assert teams[0]["crest"] == {"code": "ALP", "color": "#ABCDEF"}


def test_unknown_league_is_a_404(client):
    response = client.get("/api/leagues/no-such-league/standings")

    assert response.status_code == 404
    assert response.json() == {"detail": "League not found"}
