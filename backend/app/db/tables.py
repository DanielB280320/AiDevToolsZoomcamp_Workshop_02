"""SQLAlchemy table mappings for the records in models.py.

Only portable column types are used, so the same schema works on SQLite, Postgres and other databases.
`sort_order` keeps the order records were added in, which is the order they are listed in.
"""

import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

ID = String(128)
COLOR = String(16)
URL = String(500)


class Base(DeclarativeBase):
    pass


class LeagueRow(Base):
    __tablename__ = "leagues"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    sort_order: Mapped[int]
    name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(32))
    code: Mapped[str] = mapped_column(String(8))
    logo: Mapped[str] = mapped_column(URL)
    season: Mapped[str] = mapped_column(String(16))
    color: Mapped[str] = mapped_column(COLOR)
    logo_background: Mapped[str] = mapped_column(COLOR)


class TeamRow(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    sort_order: Mapped[int]
    name: Mapped[str] = mapped_column(String(100))
    league_id: Mapped[str] = mapped_column(ForeignKey("leagues.id"), index=True)
    crest_code: Mapped[str] = mapped_column(String(8))
    crest_color: Mapped[str] = mapped_column(COLOR)
    crest_logo: Mapped[str | None] = mapped_column(URL)


class PlayerRow(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    sort_order: Mapped[int]
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(3))
    shirt_number: Mapped[int]


class MatchRow(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    sort_order: Mapped[int]
    league_id: Mapped[str] = mapped_column(ForeignKey("leagues.id"), index=True)
    round: Mapped[int]
    home_team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"))
    home_score: Mapped[int]
    away_score: Mapped[int]
    date: Mapped[datetime.date]
    player_ratings: Mapped[list["PlayerRatingRow"]] = relationship(
        order_by="PlayerRatingRow.sort_order", cascade="all, delete-orphan"
    )


class PlayerRatingRow(Base):
    __tablename__ = "player_ratings"

    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), primary_key=True)
    sort_order: Mapped[int]
    goals: Mapped[int]
    assists: Mapped[int]
    rating: Mapped[float]
    minutes_played: Mapped[int]
