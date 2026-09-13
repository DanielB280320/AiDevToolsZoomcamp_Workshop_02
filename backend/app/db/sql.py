"""Repository backed by a SQL database through SQLAlchemy. The database URL decides which database that is."""

from collections.abc import Callable, Iterable
from dataclasses import fields

from sqlalchemy import Engine, create_engine, event, func, make_url, select
from sqlalchemy.orm import Session, selectinload, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import League, Match, Player, PlayerRating, Team
from app.db.tables import Base, LeagueRow, MatchRow, PlayerRatingRow, PlayerRow, TeamRow


def create_database_engine(url: str) -> Engine:
    """Engine for any SQLAlchemy URL, e.g. `sqlite:///kickboard.db` or `postgresql+psycopg://user:pass@host/db`."""
    parsed = make_url(url)
    if parsed.get_backend_name() != "sqlite":
        return create_engine(parsed, pool_pre_ping=True)

    options = {}
    if parsed.database in (None, "", ":memory:"):
        # Share one connection, or every thread would get its own empty in-memory database.
        options = {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
    engine = create_engine(parsed, **options)
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    # SQLite only enforces foreign keys when asked to, per connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class SqlRepository:
    def __init__(self, engine: Engine):
        self._engine = engine
        self._sessions = sessionmaker(engine)

    def create_schema(self) -> None:
        """Creates missing tables. Existing tables aren't altered; schema changes will need migrations."""
        Base.metadata.create_all(self._engine)

    def is_empty(self) -> bool:
        with self._sessions() as session:
            return session.scalar(select(LeagueRow.id).limit(1)) is None

    def add(
        self,
        leagues: Iterable[League] = (),
        teams: Iterable[Team] = (),
        players: Iterable[Player] = (),
        matches: Iterable[Match] = (),
    ) -> None:
        """Stores records in one transaction; they are listed after the records already stored."""
        with self._sessions.begin() as session:
            # Parents first, so every flush satisfies the foreign keys.
            _insert(session, LeagueRow, leagues, _values)
            _insert(session, TeamRow, teams, _values)
            _insert(session, PlayerRow, players, _values)
            _insert(session, MatchRow, matches, _match_values)

    def list_leagues(self) -> list[League]:
        with self._sessions() as session:
            rows = session.scalars(select(LeagueRow).order_by(LeagueRow.sort_order))
            return [_record(League, row) for row in rows]

    def get_league(self, league_id: str) -> League | None:
        with self._sessions() as session:
            row = session.get(LeagueRow, league_id)
            return _record(League, row) if row else None

    def list_teams(self, league_id: str) -> list[Team]:
        with self._sessions() as session:
            rows = session.scalars(select(TeamRow).where(TeamRow.league_id == league_id).order_by(TeamRow.sort_order))
            return [_record(Team, row) for row in rows]

    def get_team(self, team_id: str) -> Team | None:
        with self._sessions() as session:
            row = session.get(TeamRow, team_id)
            return _record(Team, row) if row else None

    def list_players(self, team_id: str) -> list[Player]:
        with self._sessions() as session:
            rows = session.scalars(
                select(PlayerRow).where(PlayerRow.team_id == team_id).order_by(PlayerRow.sort_order)
            )
            return [_record(Player, row) for row in rows]

    def list_matches(self, league_id: str) -> list[Match]:
        statement = (
            select(MatchRow)
            .where(MatchRow.league_id == league_id)
            .options(selectinload(MatchRow.player_ratings))
            .order_by(MatchRow.sort_order)
        )
        with self._sessions() as session:
            return [
                _record(Match, row, player_ratings=[_record(PlayerRating, r) for r in row.player_ratings])
                for row in session.scalars(statement).all()
            ]


def _insert(session: Session, row_type: type[Base], records: Iterable, values: Callable[[object], dict]) -> None:
    start = session.scalar(select(func.coalesce(func.max(row_type.sort_order) + 1, 0)))
    session.add_all(row_type(sort_order=order, **values(record)) for order, record in enumerate(records, start))
    session.flush()


def _values(record) -> dict:
    return {field.name: getattr(record, field.name) for field in fields(record)}


def _match_values(match: Match) -> dict:
    ratings = [PlayerRatingRow(sort_order=order, **_values(r)) for order, r in enumerate(match.player_ratings)]
    return _values(match) | {"player_ratings": ratings}


def _record(model_type, row, **overrides):
    return model_type(**{field.name: getattr(row, field.name) for field in fields(model_type)} | overrides)
