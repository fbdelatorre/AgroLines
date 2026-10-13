import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from server.config import Settings
from server.main import create_app
from server.models import Base


@pytest.fixture
def api():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    settings = Settings(database_url="sqlite://")
    with TestClient(create_app(settings, engine)) as client:
        yield client
    engine.dispose()


def account(api, email="owner@example.com"):
    response = api.post(
        "/auth/register",
        json={"name": "Pessoa sintética", "email": email, "password": "Senha sintetica 123!"},
    )
    assert response.status_code == 201, response.text
    login = api.post("/auth/login", json={"email": email, "password": "Senha sintetica 123!"})
    assert login.status_code == 200, login.text
    session = login.json()
    return session["user"], {"Authorization": "Bearer " + session["access_token"]}, session
