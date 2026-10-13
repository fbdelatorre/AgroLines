import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from server import security
from server.models import AuditEvent, AuthSession, Credential, ResetToken
from tests.conftest import account


def test_argon2id_and_invalid_hash():
    hashed = security.hash_password("Uma senha sintética longa")
    assert hashed.startswith("$argon2id$")
    assert security.verify_password(hashed, "Uma senha sintética longa")
    assert not security.verify_password(hashed, "senha incorreta")
    assert not security.verify_password("invalid", "senha")


def test_registration_email_unique_and_private_storage(api):
    user, headers, session = account(api, "OWNER@example.com")
    assert user["email"] == "owner@example.com"
    duplicate = api.post(
        "/auth/register",
        json={"name": "Outra pessoa", "email": "owner@example.com", "password": "Outra senha 123!"},
    )
    assert duplicate.status_code == 409
    assert api.get("/auth/me", headers=headers).json() == user
    with Session(api.app.state.engine) as db:
        credential = db.get(Credential, user["id"])
        stored = db.scalar(select(AuthSession))
        assert credential.password_hash.startswith("$argon2id$")
        assert session["access_token"] not in stored.access_hash
        assert session["refresh_token"] not in stored.refresh_hash
        assert stored.access_hash == security.digest(session["access_token"])
        assert db.scalar(select(AuditEvent).where(AuditEvent.action == "user.register"))
    assert "password" not in api.get("/auth/me", headers=headers).text
    assert api.get("/auth/me").status_code == 401


def test_login_errors_generic_and_persistent_limit(api, monkeypatch):
    _, _, _ = account(api)
    api.app.state.settings.login_limit = 2
    bad = {"email": "owner@example.com", "password": "incorreta"}
    assert api.post("/auth/login", json=bad).status_code == 401
    assert api.post("/auth/login", json=bad).status_code == 429
    # Window expiry actually permits a later attempt.
    clock = security.now()
    monkeypatch.setattr(security, "now", lambda: clock + 901)
    assert api.post("/auth/login", json=bad).status_code == 401
    unknown = api.post("/auth/login", json={"email": "unknown@example.com", "password": "errada"})
    assert unknown.status_code == 401
    assert unknown.json() == api.post("/auth/login", json=bad).json()


def test_access_expiration_and_secure_rotation(api, monkeypatch):
    _, headers, session = account(api)
    clock = session["access_expires"]
    monkeypatch.setattr(security, "now", lambda: clock)
    assert api.get("/auth/me", headers=headers).status_code == 401
    rotated = api.post("/auth/refresh", json={"token": session["refresh_token"]})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_expires"] == session["refresh_expires"]
    assert rotated.json()["refresh_token"] != session["refresh_token"]
    new_headers = {"Authorization": "Bearer " + rotated.json()["access_token"]}
    assert api.get("/auth/me", headers=new_headers).status_code == 200
    assert api.post("/auth/refresh", json={"token": session["refresh_token"]}).status_code == 401
    # Replay revokes the entire session, including newly issued tokens.
    assert api.get("/auth/me", headers=new_headers).status_code == 401
    assert (
        api.post("/auth/refresh", json={"token": rotated.json()["refresh_token"]}).status_code
        == 401
    )


def test_refresh_expiration_and_logout(api, monkeypatch):
    _, headers, tokens = account(api)
    assert api.post("/auth/logout", headers=headers).status_code == 204
    assert api.get("/auth/me", headers=headers).status_code == 401
    assert api.post("/auth/refresh", json={"token": tokens["refresh_token"]}).status_code == 401
    _, _, second = account(api, "second@example.com")
    monkeypatch.setattr(security, "now", lambda: second["refresh_expires"])
    assert api.post("/auth/refresh", json={"token": second["refresh_token"]}).status_code == 401


def test_sessions_are_user_scoped_and_revocable(api):
    _, owner, _ = account(api)
    _, outsider, _ = account(api, "outsider@example.com")
    session = api.get("/auth/sessions", headers=owner).json()[0]
    assert api.delete("/auth/sessions/" + session["id"], headers=outsider).status_code == 404
    assert len(api.get("/auth/sessions", headers=outsider).json()) == 1
    assert api.delete("/auth/sessions/" + session["id"], headers=owner).status_code == 204
    assert api.get("/auth/me", headers=owner).status_code == 401


def test_recovery_requires_mail_and_reset_invalidates_sessions(api, monkeypatch):
    user, headers, _ = account(api)
    assert api.post("/auth/recover", json={"email": user["email"]}).status_code == 503
    api.app.state.settings.smtp_host = "smtp.example.com"
    deliveries = []
    monkeypatch.setattr(
        "server.auth.send_recovery",
        lambda settings, email, token: deliveries.append((email, token)),
    )
    known = api.post("/auth/recover", json={"email": user["email"]})
    unknown = api.post("/auth/recover", json={"email": "absent@example.com"})
    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()
    raw = deliveries[0][1]
    assert raw not in known.text
    with Session(api.app.state.engine) as db:
        reset = db.scalar(select(ResetToken))
        assert reset.digest == security.digest(raw)
    body = {"token": raw, "password": "Nova senha segura 456!"}
    assert api.post("/auth/reset", json=body).status_code == 204
    assert api.post("/auth/reset", json=body).status_code == 400
    assert api.get("/auth/me", headers=headers).status_code == 401
    assert (
        api.post(
            "/auth/login", json={"email": user["email"], "password": body["password"]}
        ).status_code
        == 200
    )


def test_reset_expiration(api, monkeypatch):
    user, _, _ = account(api)
    api.app.state.settings.smtp_host = "smtp.example.com"
    tokens = []
    monkeypatch.setattr(
        "server.auth.send_recovery", lambda settings, email, token: tokens.append(token)
    )
    api.post("/auth/recover", json={"email": user["email"]})
    clock = security.now()
    monkeypatch.setattr(security, "now", lambda: clock + 901)
    assert (
        api.post(
            "/auth/reset", json={"token": tokens[0], "password": "Nova senha segura 456!"}
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    "body",
    [
        {"name": "", "email": "a@example.com", "password": "long enough password"},
        {"name": "Pessoa", "email": "not email", "password": "long enough password"},
        {"name": "Pessoa", "email": "a@example.com", "password": "short"},
    ],
)
def test_registration_validation(api, body):
    assert api.post("/auth/register", json=body).status_code == 422


def test_validation_does_not_echo_secrets(api):
    sensitive = "short-secret"
    response = api.post(
        "/auth/register", json={"name": "Pessoa", "email": "bad-email", "password": sensitive}
    )
    assert response.status_code == 422
    assert sensitive not in response.text
    assert "input" not in response.text


def test_mail_failure_does_not_leak_account_or_keep_usable_reset(api, monkeypatch, caplog):
    user, _, _ = account(api)
    api.app.state.settings.smtp_host = "smtp.example.com"

    def fail(*args):
        raise OSError("Synthetic delivery failure")

    monkeypatch.setattr("server.auth.send_recovery", fail)
    known = api.post("/auth/recover", json={"email": user["email"]})
    unknown = api.post("/auth/recover", json={"email": "absent@example.com"})
    assert known.json() == unknown.json()
    assert user["email"] not in caplog.text
    with Session(api.app.state.engine) as db:
        assert db.scalar(select(ResetToken)) is None


def test_invite_expiration(api, monkeypatch):
    user, owner, _ = account(api)
    recipient, invited, _ = account(api, "recipient@example.com")
    farm = api.post("/farms", headers=owner, json={"name": "Teste"}).json()
    invitation = api.post(
        "/farms/" + farm["id"] + "/invitations",
        headers=owner,
        json={"user_id": recipient["id"], "scopes": [{"role": "viewer"}]},
    ).json()
    clock = security.now()
    # Keep access valid while moving only the invitation's expiry into the past.
    from server.models import Invitation

    with Session(api.app.state.engine) as db:
        db.get(Invitation, invitation["id"]).expires = clock - 1
        db.commit()
    assert (
        api.post("/invitations/" + invitation["id"] + "/accept", headers=invited).status_code == 409
    )
    assert api.get("/invitations", headers=invited).json()[0]["status"] == "expired"
    assert user["id"] != recipient["id"]
