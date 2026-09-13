import pytest
from fastapi.testclient import TestClient

from app.db import get_repository
from app.main import app
from app.sources import RepositorySource, get_data_source


@pytest.fixture(autouse=True, scope="session")
def in_memory_database():
    """Tests share one in-memory database with the mock data, never the configured DATABASE_URL."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", "sqlite://")
        yield


@pytest.fixture
def client():
    """Client backed by the mock database, even when an API_FOOTBALL_KEY is configured."""
    app.dependency_overrides[get_data_source] = lambda: RepositorySource(get_repository())
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client_for():
    """Factory for a client whose app reads from the given repository, for hand-built scenarios."""

    def make(repository):
        app.dependency_overrides[get_data_source] = lambda: RepositorySource(repository)
        return TestClient(app)

    yield make
    app.dependency_overrides.clear()
