import io
import json
from urllib.error import URLError
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from core.models import Farm, Field, Producer
from desktop.health import check_health
from server.config import Settings, get_settings
from server.db import make_engine
from server.main import create_app


def test_health_contract():
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agrolines", "version": "0.1.0"}


def test_environment_config_and_secret_redaction(monkeypatch):
    monkeypatch.setenv("AGROLINES_APP_NAME", "Teste")
    monkeypatch.setenv("AGROLINES_DATABASE_URL", "postgresql+psycopg://u:private@localhost/test")
    settings = Settings()
    assert settings.app_name == "Teste"
    assert "private" not in repr(settings)
    assert "private" not in settings.model_dump_json()
    engine = make_engine(settings)
    assert engine.url.database == "test"
    engine.dispose()
    get_settings.cache_clear()
    assert create_app().title == "Teste"
    get_settings.cache_clear()


def test_invalid_configuration(monkeypatch):
    monkeypatch.setenv("AGROLINES_APP_NAME", "Teste")
    with pytest.raises(ValidationError):
        Settings(database_url=None)


def test_domain_relationships():
    producer = Producer(uuid4(), "Produtor sintético")
    farm = Farm(uuid4(), producer.id, "Fazenda sintética")
    field = Field(uuid4(), farm.id, "Talhão sintético")
    assert field.farm_id == farm.id
    assert farm.producer_id == producer.id
    assert field.boundary_version == 1


class Response(io.BytesIO):
    status = 200


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"status": "ok", "service": "agrolines"}, True),
        ({"status": "ok", "service": "other"}, False),
        ({"status": "error", "service": "agrolines"}, False),
        ([], False),
    ],
)
def test_desktop_health_contract(monkeypatch, payload, expected):
    def open_url(url, timeout):
        assert url == "http://localhost:8000/health"
        assert timeout == 3.0
        return Response(json.dumps(payload).encode())

    monkeypatch.setattr("desktop.health.urlopen", open_url)
    assert check_health("http://localhost:8000/") is expected


@pytest.mark.parametrize("error", [URLError("offline"), TimeoutError(), ValueError("bad JSON")])
def test_desktop_health_failures(monkeypatch, error):
    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr("desktop.health.urlopen", fail)
    assert not check_health("http://localhost:8000")
