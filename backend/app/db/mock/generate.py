"""Generates the mock database: a fictional but deterministic season for every league in fixtures.py."""

import math
import random
from datetime import date, timedelta

from app.db.memory import InMemoryRepository
from app.db.mock.fixtures import CLUBS, LEAGUES, NAME_POOLS, LeagueFixture
from app.db.models import League, Match, Player, PlayerRating, Team

SQUAD_SHIRTS = {
    "GK": (1, 13),
    "DEF": (2, 3, 4, 5, 15, 22),
    "MID": (6, 8, 10, 14, 16, 18),
    "FWD": (7, 9, 11, 19),
}
LINEUP = {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3}
SUBSTITUTIONS = 3
SCORER_WEIGHT = {"GK": 0, "DEF": 1, "MID": 3, "FWD": 6}
ASSIST_WEIGHT = {"GK": 0, "DEF": 2, "MID": 4, "FWD": 3}
ASSIST_CHANCE = 0.75

LAST_MATCHDAY = date(2026, 9, 12)
DAYS_BETWEEN_ROUNDS = 5


def club_roster(club_id: str) -> list[tuple[str, str, int]]:
    """(name, position, shirt number) per player. Seeded by club, so names match across competitions."""
    pool = NAME_POOLS[CLUBS[club_id].name_pool]
    rng = random.Random(f"roster:{club_id}")
    used_names: set[str] = set()
    roster = []
    for position, shirts in SQUAD_SHIRTS.items():
        for shirt_number in shirts:
            while (name := f"{rng.choice(pool['first'])} {rng.choice(pool['last'])}") in used_names:
                pass
            used_names.add(name)
            roster.append((name, position, shirt_number))
    return roster


def round_robin(team_ids: list[str]) -> list[list[tuple[str, str]]]:
    """Circle method: every team plays once per round and meets every other team once."""
    ids: list[str | None] = [*team_ids, None] if len(team_ids) % 2 else list(team_ids)
    rounds = []
    for round_index in range(len(ids) - 1):
        pairs = []
        for i in range(len(ids) // 2):
            a, b = ids[i], ids[-1 - i]
            if a and b:
                pairs.append((a, b) if round_index % 2 == 0 else (b, a))
        rounds.append(pairs)
        ids.insert(1, ids.pop())
    return rounds


def schedule(team_ids: list[str], double_round_robin: bool) -> list[list[tuple[str, str]]]:
    first_leg = round_robin(team_ids)
    if not double_round_robin:
        return first_leg
    return first_leg + [[(away, home) for home, away in pairs] for pairs in first_leg]


def poisson(rng: random.Random, mean: float) -> int:
    limit = math.exp(-mean)
    goals, p = 0, rng.random()
    while p > limit:
        goals += 1
        p *= rng.random()
    return goals


def simulate_performance(
    rng: random.Random, squad: list[Player], goals_for: int, goals_against: int
) -> list[PlayerRating]:
    starters = [
        player
        for position, count in LINEUP.items()
        for player in rng.sample([p for p in squad if p.position == position], count)
    ]
    bench = [p for p in squad if p.position != "GK" and p not in starters]
    rng.shuffle(bench)
    subbed_off = rng.sample([p for p in starters if p.position != "GK"], SUBSTITUTIONS)

    minutes = {player.id: 90 for player in starters}
    for off, on in zip(subbed_off, bench):
        minute = rng.randint(55, 85)
        minutes[off.id] = minute
        minutes[on.id] = 90 - minute

    on_pitch = [p for p in squad if p.id in minutes]
    goals = dict.fromkeys(minutes, 0)
    assists = dict.fromkeys(minutes, 0)
    for _ in range(goals_for):
        scorer = rng.choices(on_pitch, weights=[SCORER_WEIGHT[p.position] * minutes[p.id] for p in on_pitch])[0]
        goals[scorer.id] += 1
        if rng.random() < ASSIST_CHANCE:
            candidates = [p for p in on_pitch if p is not scorer]
            assister = rng.choices(
                candidates, weights=[ASSIST_WEIGHT[p.position] * minutes[p.id] for p in candidates]
            )[0]
            assists[assister.id] += 1

    result_bonus = 0.3 if goals_for > goals_against else -0.3 if goals_for < goals_against else 0
    ratings = []
    for player in on_pitch:
        clean_sheet = 0.5 if goals_against == 0 and player.position in ("GK", "DEF") else 0
        cameo = -0.4 if minutes[player.id] < 30 else 0
        raw = (
            6 + rng.random() * 1.2 + goals[player.id] * 0.9 + assists[player.id] * 0.5
            + result_bonus + clean_sheet + cameo
        )
        ratings.append(
            PlayerRating(
                player_id=player.id,
                goals=goals[player.id],
                assists=assists[player.id],
                rating=round(min(10, max(4.5, raw)), 1),
                minutes_played=minutes[player.id],
            )
        )
    return ratings


def generate_league(fixture: LeagueFixture) -> tuple[list[Team], list[Player], list[Match]]:
    rng = random.Random(f"league:{fixture.id}")

    teams = []
    squads: dict[str, list[Player]] = {}
    for club_id in fixture.club_ids:
        club = CLUBS[club_id]
        team = Team(
            id=f"{fixture.id}--{club_id}",
            name=club.name,
            league_id=fixture.id,
            crest_code=club.code,
            crest_color=club.color,
            crest_logo=club.logo,
        )
        teams.append(team)
        squads[team.id] = [
            Player(id=f"{team.id}--{shirt}", team_id=team.id, name=name, position=position, shirt_number=shirt)
            for name, position, shirt in club_roster(club_id)
        ]
    strength = {team.id: 1 - (i / len(teams)) * 0.6 for i, team in enumerate(teams)}

    rounds = schedule([t.id for t in teams], fixture.double_round_robin)[: fixture.rounds_played]
    matches = []
    for round_index, pairs in enumerate(rounds):
        played_on = LAST_MATCHDAY - timedelta(days=(len(rounds) - 1 - round_index) * DAYS_BETWEEN_ROUNDS)
        for match_index, (home, away) in enumerate(pairs):
            edge = strength[home] - strength[away]
            home_score = poisson(rng, max(0.25, 1.55 + edge * 1.6))
            away_score = poisson(rng, max(0.25, 1.15 - edge * 1.6))
            matches.append(
                Match(
                    id=f"{fixture.id}--r{round_index + 1}-m{match_index + 1}",
                    league_id=fixture.id,
                    round=round_index + 1,
                    home_team_id=home,
                    away_team_id=away,
                    home_score=home_score,
                    away_score=away_score,
                    date=played_on,
                    player_ratings=[
                        *simulate_performance(rng, squads[home], home_score, away_score),
                        *simulate_performance(rng, squads[away], away_score, home_score),
                    ],
                )
            )

    players = [player for squad in squads.values() for player in squad]
    return teams, players, matches


def build_mock_repository() -> InMemoryRepository:
    leagues, teams, players, matches = [], [], [], []
    for fixture in LEAGUES:
        leagues.append(
            League(
                id=fixture.id,
                name=fixture.name,
                country=fixture.country,
                region=fixture.region,
                code=fixture.code,
                logo=fixture.logo,
                season=fixture.season,
                color=fixture.color,
                logo_background=fixture.logo_background,
            )
        )
        league_teams, league_players, league_matches = generate_league(fixture)
        teams += league_teams
        players += league_players
        matches += league_matches
    return InMemoryRepository(leagues=leagues, teams=teams, players=players, matches=matches)
