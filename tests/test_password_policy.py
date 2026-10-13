import pytest
from sqlalchemy.orm import Session

from server.models import Credential
from tests.conftest import account


@pytest.mark.parametrize(
    "password,status",
    [
        ("abcde", 422),
        ("abcdef", 201),
        ("abcdefghijkl", 201),
        ("Uma senha bem maior que doze!", 201),
    ],
)
def test_registration_password_boundaries(api, password, status, caplog):
    response = api.post(
        "/auth/register",
        json={"name": "Política de senha", "email": "policy@example.com", "password": password},
    )
    assert response.status_code == status
    assert password not in response.text
    assert password not in caplog.text
    if status == 201:
        login = api.post("/auth/login", json={"email": "policy@example.com", "password": password})
        assert login.status_code == 200
        with Session(api.app.state.engine) as db:
            assert db.get(Credential, response.json()["id"]).password_hash.startswith("$argon2id$")


@pytest.mark.parametrize(
    "password,status",
    [
        ("abcde", 422),
        ("abcdef", 204),
        ("abcdefghijkl", 204),
        ("Uma nova senha longa 123!", 204),
    ],
)
def test_reset_password_boundaries(api, monkeypatch, password, status):
    user, headers, _ = account(api)
    api.app.state.settings.smtp_host = "smtp.example.com"
    tokens = []
    monkeypatch.setattr(
        "server.auth.send_recovery", lambda settings, email, token: tokens.append(token)
    )
    assert api.post("/auth/recover", json={"email": user["email"]}).status_code == 202
    response = api.post("/auth/reset", json={"token": tokens[0], "password": password})
    assert response.status_code == status
    assert password not in response.text
    if status == 204:
        assert api.get("/auth/me", headers=headers).status_code == 401
        assert (
            api.post("/auth/login", json={"email": user["email"], "password": password}).status_code
            == 200
        )
    else:
        assert api.get("/auth/me", headers=headers).status_code == 200
        # Invalid new password does not consume the reset token or touch the old hash.
        assert (
            api.post("/auth/reset", json={"token": tokens[0], "password": "abcdef"}).status_code
            == 204
        )


def test_existing_hash_and_session_are_not_changed_by_new_policy(api):
    user, headers, _ = account(api)
    with Session(api.app.state.engine) as db:
        original_hash = db.get(Credential, user["id"]).password_hash
    assert (
        api.post(
            "/auth/register",
            json={"name": "Nova conta", "email": "new@example.com", "password": "abcdef"},
        ).status_code
        == 201
    )
    assert api.get("/auth/me", headers=headers).status_code == 200
    assert (
        api.post(
            "/auth/login", json={"email": user["email"], "password": "Senha sintetica 123!"}
        ).status_code
        == 200
    )
    with Session(api.app.state.engine) as db:
        assert db.get(Credential, user["id"]).password_hash == original_hash
