"""Database access. DATABASE_URL (any SQLAlchemy URL) selects the database; the default is a SQLite file in backend/."""

import os
from functools import cache
from pathlib import Path

from app.db.mock import generate_mock_data
from app.db.repository import Repository
from app.db.sql import SqlRepository, create_database_engine

DEFAULT_DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[2] / 'kickboard.db'}"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", "").strip() or DEFAULT_DATABASE_URL


def open_repository(url: str) -> SqlRepository:
    """Connects to the database, creating missing tables and loading the mock data into an empty database."""
    repository = SqlRepository(create_database_engine(url))
    repository.create_schema()
    if repository.is_empty():
        repository.add(**generate_mock_data()._asdict())
    return repository


@cache
def _repository(url: str) -> SqlRepository:
    # Cached so the engine's connection pool lives as long as the app.
    return open_repository(url)


def get_repository() -> Repository:
    """FastAPI dependency providing the database configured by DATABASE_URL."""
    return _repository(database_url())
