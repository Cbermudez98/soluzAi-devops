import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import db


@pytest.fixture(autouse=True)
def seeded_db():
    db.reset()
    db.seed()
    yield db
    db.reset()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
