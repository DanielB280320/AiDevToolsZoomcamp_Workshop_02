"""The SQL repository: records round-trip through the database that DATABASE_URL selects."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import get_repository, open_repository
from app.db.mock import generate_mock_data
from tests.builders import database, league, match, player, rating, team


def test_records_are_read_back_as_they_were_stored():
    leagues = [league(logo_background="#0B1F63"), league("other-league")]
    teams = [team("alpha"), team("bravo", crest_logo=None)]
    players = [player("striker", "alpha"), player("keeper", "bravo", "GK", 1)]
    matches = [
        match(
            "alpha", "bravo", 2, 1, on=date(2026, 8, 1), round=3,
            ratings=[rating("striker", goals=2, rating=8.9, minutes_played=84), rating("keeper", assists=1, rating=6.1)],
        )
    ]
    repository = database(leagues=leagues, teams=teams, players=players, matches=matches)

    assert repository.list_leagues() == leagues
    assert repository.get_league("other-league") == leagues[1]
    assert repository.list_teams("test-league") == teams
    assert repository.get_team("bravo") == teams[1]
    assert repository.list_players("alpha") == [players[0]]
    assert repository.list_matches("test-league") == matches


def test_missing_records_are_none_or_empty():
    repository = database(leagues=[league()])

    assert repository.get_league("nope") is None
    assert repository.get_team("nope") is None
    assert repository.list_teams("nope") == []
    assert repository.list_players("nope") == []
    assert repository.list_matches("test-league") == []


def test_records_are_listed_in_the_order_they_were_added():
    repository = database(leagues=[league()], teams=[team("zulu"), team("alpha")])

    repository.add(teams=[team("mike")])

    assert [t.id for t in repository.list_teams("test-league")] == ["zulu", "alpha", "mike"]


def test_references_to_missing_records_are_rejected():
    repository = database(leagues=[league()])

    with pytest.raises(IntegrityError):
        repository.add(teams=[team("alpha", league_id="no-such-league")])
    assert repository.list_teams("no-such-league") == []


def test_database_url_selects_the_database_and_an_empty_one_gets_the_mock_data(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'kickboard.db'}")

    assert get_repository().list_leagues() == generate_mock_data().leagues
    assert (tmp_path / "kickboard.db").exists()


def test_stored_data_persists_and_is_not_seeded_again(tmp_path):
    url = f"sqlite:///{tmp_path / 'kickboard.db'}"
    open_repository(url).add(leagues=[league("extra")])

    leagues = open_repository(url).list_leagues()

    assert [l.id for l in leagues] == [l.id for l in generate_mock_data().leagues] + ["extra"]
