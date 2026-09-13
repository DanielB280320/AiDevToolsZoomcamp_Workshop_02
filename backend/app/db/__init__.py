from functools import cache

from app.db.mock import build_mock_repository
from app.db.repository import Repository


@cache
def _mock_repository() -> Repository:
    return build_mock_repository()


def get_repository() -> Repository:
    """FastAPI dependency providing the data store. Swap the mock for the real database here."""
    return _mock_repository()
