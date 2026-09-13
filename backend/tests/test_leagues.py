import re
from collections import Counter

from tests.builders import database, league

HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")
LEAGUE_KEYS = {"id", "name", "country", "region", "code", "logo", "logoBackground", "season", "color"}


def test_lists_the_nine_competitions_grouped_by_region(client):
    response = client.get("/api/leagues")

    assert response.status_code == 200
    leagues = response.json()
    assert len(leagues) == 9
    assert Counter(l["region"] for l in leagues) == {"Europe": 4, "Americas": 4, "Continental": 1}
    assert [l["name"] for l in leagues if l["region"] == "Continental"] == ["UEFA Champions League"]


def test_league_fields_follow_the_contract(client):
    for item in client.get("/api/leagues").json():
        assert set(item) == LEAGUE_KEYS
        assert re.fullmatch(r"[A-Z]{3}", item["code"])
        assert HEX_COLOR.fullmatch(item["color"])
        assert HEX_COLOR.fullmatch(item["logoBackground"])
        assert item["logo"].startswith("https://")


def test_serialises_leagues_in_repository_order_with_camel_case_keys(client_for):
    repository = database(
        leagues=[
            league("second", name="Second"),
            league("first", name="First", region="Continental", logo_background="#0B1F63"),
        ]
    )

    response = client_for(repository).get("/api/leagues")

    assert response.json() == [
        {
            "id": "second",
            "name": "Second",
            "country": "Testland",
            "region": "Europe",
            "code": "TST",
            "logo": "https://example.com/league.png/small",
            "logoBackground": "#ffffff",
            "season": "2026",
            "color": "#123456",
        },
        {
            "id": "first",
            "name": "First",
            "country": "Testland",
            "region": "Continental",
            "code": "TST",
            "logo": "https://example.com/league.png/small",
            "logoBackground": "#0B1F63",
            "season": "2026",
            "color": "#123456",
        },
    ]
