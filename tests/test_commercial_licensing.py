"""Synthetic complete commercial flow, negative controls and durable local state."""

import copy
import os
import time
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from core.license_protocol import decode, encode, verify
from core.licensing import Module
from core.local_projects import LocalProject
from desktop.license_client import LicenseManager
from server import security
from server.config import Settings
from server.license_app import create_app
from server.license_service import Issuer, extend, public_key, totp
from server.models import (
    Base,
    Credential,
    LicenseActivation,
    LicenseAdministrator,
    LicenseSlot,
    LicenseSubscription,
    User,
)


class MemoryVault:
    """Test-only storage. Production has no plaintext fallback."""

    def __init__(self):
        self.value = None

    def load(self):
        return copy.deepcopy(self.value)

    def save(self, value):
        self.value = copy.deepcopy(value)
        return True


class ASGITransport:
    """In-process HTTPS URL, not evidence of a deployed TLS server or Windows SAC."""

    def __init__(self, api):
        self.api = api
        self.failed = False

    def post(self, operation, body):
        if self.failed:
            raise OSError("Synthetic unavailable network")
        result = self.api.post("/v1/" + operation, json=body)
        if result.status_code != 200:
            raise OSError(str(result.status_code))
        return result.json()


@pytest.fixture
def licensed():
    test_database = os.getenv("AGROLINES_LICENSE_TEST_DATABASE_URL")
    schema = None
    if test_database:
        from sqlalchemy import text

        engine = create_engine(test_database)
        schema = "license_test_" + uuid4().hex
        with engine.begin() as connection:
            connection.execute(text("CREATE SCHEMA " + schema))
        engine = engine.execution_options(schema_translate_map={None: schema})
    else:
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    Base.metadata.create_all(engine)
    issuer = Issuer("synthetic-1", Ed25519PrivateKey.generate(), b"x" * 32)
    secret = b"synthetic-test-only!!"
    with Session(engine) as db, db.begin():
        user = User(name="Admin sintético", email="admin@example.com")
        db.add(user)
        db.flush()
        db.add(
            Credential(
                user_id=user.id, password_hash=security.hash_password("Synthetic admin password!")
            )
        )
        db.add(
            LicenseAdministrator(
                user_id=user.id, role="owner", totp_sealed=issuer.seal(secret), last_counter=-1
            )
        )
    with TestClient(
        create_app(issuer, Settings(database_url="sqlite://"), engine),
        base_url="https://licenses.example.test",
    ) as api:
        login = api.post(
            "/admin/login",
            json={
                "email": "admin@example.com",
                "password": "Synthetic admin password!",
                "code": totp(secret, security.now() // 30),
            },
        )
        assert login.status_code == 200, login.text
        headers = {"Authorization": "Bearer " + login.json()["access_token"]}
        user = api.post(
            "/admin/users",
            headers=headers,
            json={"email": "tester@example.com", "name": "Titular sintético"},
        )
        assert user.status_code == 201, user.text
        subscription = api.post(
            "/admin/subscriptions",
            headers=headers,
            json={"user_id": user.json()["id"], "plan": "monthly"},
        )
        assert subscription.status_code == 201, subscription.text
        yield api, headers, subscription.json(), public_key(issuer), engine, issuer, secret
    if schema:
        from sqlalchemy import text

        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA " + schema + " CASCADE"))
    engine.dispose()


def manager(api, keyring):
    return LicenseManager(MemoryVault(), MemoryVault(), keyring, ASGITransport(api))


def activate(manager, subscription, slot=0):
    return manager.activate("tester@example.com", subscription["keys"][slot]["key"], "PC fictício")


def test_full_lifecycle_two_seats_offline_renewal_revocation(licensed, tmp_path):
    api, admin, sub, keyring, engine, issuer, secret = licensed
    first, second, third = (manager(api, keyring) for _ in range(3))
    assert first.verify().read_only  # first offline activation cannot silently create entitlement
    first.transport.failed = True
    with pytest.raises(OSError):
        activate(first, sub)
    assert first.verify().read_only
    first.transport.failed = False
    a, b = activate(first, sub), activate(second, sub, 1)
    assert a["subscription_id"] == b["subscription_id"] == sub["id"]
    assert a["activation_id"] != b["activation_id"]
    with pytest.raises(OSError, match="409"):
        activate(third, sub)
    with pytest.raises(OSError, match="409"):
        activate(third, sub, 1)
    first.transport.failed = True
    assert first.verify().permits(Module.GEOMETRY)
    with pytest.raises(OSError):
        first.check()
    assert first.verify().permits(Module.GEOMETRY)  # network outage never revokes
    project = LocalProject.create(
        tmp_path / "agricultura.agrolines", "Projeto sintético", license_verifier=first
    )
    project.backup(tmp_path / "before.agrolines")
    first.transport.failed = False
    old_expiry = first.parsed()["expires_at"]
    assert (
        api.post(
            "/admin/subscriptions/" + sub["id"],
            headers=admin,
            json={"action": "renew", "plan": "annual"},
        ).status_code
        == 200
    )
    first.check()
    assert first.parsed()["expires_at"] > old_expiry
    assert first.parsed()["plan"] == "annual"
    assert (
        api.post(
            "/admin/subscriptions/" + sub["id"], headers=admin, json={"action": "revoke"}
        ).status_code
        == 200
    )
    # Offline copies cannot learn an unreceived server decision.
    assert second.verify().permits(Module.GEOMETRY)
    previous = copy.deepcopy(first.vault.value)
    first.check()
    assert first.verify().read_only
    first.transport.failed = True
    first.vault.value = previous  # restoring license file alone cannot remove persisted revocation
    recovered = LicenseManager(first.vault, first.anchor, keyring, first.transport)
    assert recovered.verify().read_only
    project.backup(tmp_path / "after.agrolines")  # user data stays recoverable
    assert project.features() == []
    with pytest.raises(PermissionError):
        LocalProject.create(tmp_path / "blocked.agrolines", "Blocked", license_verifier=recovered)
    project.close()
    with Session(engine) as db:
        assert len(db.scalars(select(LicenseSlot)).all()) == 2
        assert len(db.scalars(select(LicenseActivation)).all()) == 2
        for slot in db.scalars(select(LicenseSlot)):
            assert slot.key_hash not in [key["key"] for key in sub["keys"]]


def test_bad_key_owner_expiry_tampering_and_copy(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    client = manager(api, keys)
    original_key = sub["keys"][0]["key"]
    for email, key in [("other@example.com", original_key), ("tester@example.com", "x" * 43)]:
        with pytest.raises(OSError, match="403"):
            client.activate(email, key, "Synthetic")
    activate(client, sub)
    envelope = copy.deepcopy(client.state["license"])
    changed = copy.deepcopy(envelope)
    changed["payload"] = encode(decode(changed["payload"]).replace(b"monthly", b"annual"))
    with pytest.raises(ValueError):
        verify(changed, keys, client.state["installation_id"])
    with pytest.raises(ValueError):
        verify(envelope, keys, str(uuid4()))
    changed["alg"] = "none"
    with pytest.raises(ValueError):
        verify(changed, keys, client.state["installation_id"])
    assert client.verify().permits(Module.GEOMETRY)
    with Session(engine) as db, db.begin():
        db.get(LicenseSubscription, sub["id"]).expires = security.now() - 1
    client.check()
    assert client.verify().read_only
    another = manager(api, keys)
    with pytest.raises(OSError, match="403"):
        activate(another, sub, 1)
    assert (
        api.post(
            "/admin/subscriptions/" + sub["id"], headers=admin, json={"action": "renew"}
        ).status_code
        == 200
    )
    client.check()
    assert client.verify().permits(Module.GEOMETRY)


def test_device_replacement_deactivation_reinstall_and_clock(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    client = manager(api, keys)
    activate(client, sub)
    restored = LicenseManager(client.vault, client.anchor, keys, ASGITransport(api))
    assert restored.state["installation_id"] == client.state["installation_id"]
    assert restored.verify().permits(Module.GEOMETRY)
    restored.clock = lambda: time.time() - 3600
    assert restored.verify().read_only
    restored.clock = time.time
    assert restored.verify().permits(Module.GEOMETRY)
    replacement = api.post(
        "/admin/subscriptions/" + sub["id"] + "/slots/1/replace", headers=admin, json={}
    )
    assert replacement.status_code == 200
    client.check()
    assert client.verify().read_only
    new = manager(api, keys)
    new.activate("tester@example.com", replacement.json()["key"], "PC substituto")
    assert new.verify().permits(Module.GEOMETRY)
    new.check(deactivate=True)
    assert new.verify().read_only
    with pytest.raises(OSError, match="403"):
        manager(api, keys).activate("tester@example.com", replacement.json()["key"], "PC terceiro")


def test_admin_strong_auth_and_no_secret_echo(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    assert api.post("/admin/users", json={"email": "a@example.com", "name": "A"}).status_code == 401
    repeated = api.post(
        "/admin/login",
        json={
            "email": "admin@example.com",
            "password": "Synthetic admin password!",
            "code": totp(secret, security.now() // 30),
        },
    )
    assert repeated.status_code == 401  # TOTP replay cannot grant another session
    broken = api.post("/v1/activate", json={"key": "DO-NOT-ECHO-SECRET", "email": "invalid"})
    assert broken.status_code == 422
    assert "DO-NOT-ECHO-SECRET" not in broken.text
    assert api.get("/admin/audit", headers=admin).status_code == 200
    assert api.get("/admin").headers["content-security-policy"].startswith("default-src 'self'")
    assert api.post("/admin/logout", headers=admin, json={}).status_code == 200
    assert api.get("/admin/users", headers=admin).status_code == 401
    assert api.get("http://licenses.example.test/admin").status_code == 400


def test_calendar_renewal_not_arbitrary_thirty_day_offline_grace():
    from datetime import UTC, datetime

    jan = int(datetime(2028, 1, 31, 10, tzinfo=UTC).timestamp())
    assert datetime.fromtimestamp(extend(jan, "monthly"), UTC).day == 29
    assert datetime.fromtimestamp(extend(jan, "annual"), UTC).year == 2029


def test_postgres_concurrent_activation_cannot_overbook_a_seat(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrent row locks require the dedicated PostgreSQL CI database")
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    barrier = Barrier(3)

    def attempt():
        barrier.wait()
        response = api.post(
            "/v1/activate",
            json={
                "email": "tester@example.com",
                "key": sub["keys"][0]["key"],
                "installation_id": str(uuid4()),
                "label": "Concurrent synthetic PC",
            },
        )
        return response.status_code

    with ThreadPoolExecutor(max_workers=3) as pool:
        outcomes = list(pool.map(lambda i: attempt(), range(3)))
    assert sorted(outcomes) == [200, 409, 409]
    with Session(engine) as db:
        assert len(db.scalars(select(LicenseActivation)).all()) == 1


def test_temporary_suspension_and_individual_revocation(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    client = manager(api, keys)
    value = activate(client, sub)
    assert (
        api.post(
            "/admin/subscriptions/" + sub["id"], headers=admin, json={"action": "suspend"}
        ).status_code
        == 200
    )
    client.check()
    assert client.verify().read_only
    assert (
        api.post(
            "/admin/subscriptions/" + sub["id"], headers=admin, json={"action": "resume"}
        ).status_code
        == 200
    )
    client.check()
    assert client.verify().permits(Module.GEOMETRY)
    assert (
        api.post(
            "/admin/activations/" + value["activation_id"] + "/revoke", headers=admin, json={}
        ).status_code
        == 200
    )
    client.check()
    assert client.verify().read_only


def test_viewer_cannot_write_and_activation_rate_limit(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    with Session(engine) as db, db.begin():
        administrator = db.scalar(select(LicenseAdministrator))
        administrator.role = "viewer"
    assert api.get("/admin/subscriptions", headers=admin).status_code == 200
    assert (
        api.post(
            "/admin/subscriptions/" + sub["id"], headers=admin, json={"action": "revoke"}
        ).status_code
        == 403
    )
    for _ in range(20):
        assert (
            api.post(
                "/v1/activate",
                json={
                    "email": "tester@example.com",
                    "key": "x" * 43,
                    "installation_id": str(uuid4()),
                    "label": "Synthetic",
                },
            ).status_code
            == 403
        )
    response = api.post(
        "/v1/activate",
        json={
            "email": "tester@example.com",
            "key": "x" * 43,
            "installation_id": str(uuid4()),
            "label": "Synthetic",
        },
    )
    assert response.status_code == 429
    assert response.headers["retry-after"]


def test_clock_correction_requires_fresh_server_response(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    client = manager(api, keys)
    activate(client, sub)
    client.clock = lambda: time.time() + 86400 * 10
    client.verify()
    client.clock = time.time
    assert client.verify().read_only
    client.transport.failed = True
    with pytest.raises(OSError):
        client.check()
    assert client.verify().read_only
    client.transport.failed = False
    client.check()
    assert client.verify().permits(Module.GEOMETRY)


def test_administrative_correction_is_authenticated_audited_and_not_a_transfer_to_admin(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    with Session(engine) as db:
        user_id = db.get(LicenseSubscription, sub["id"]).user_id
        owner = db.scalar(select(LicenseAdministrator)).user_id
    corrected = {"name": "Titular corrigido sintético", "email": "corrected@example.com"}
    assert api.put("/admin/users/" + user_id, json=corrected).status_code == 401
    assert api.put("/admin/users/" + user_id, json=corrected, headers=admin).status_code == 200
    assert api.put("/admin/users/" + owner, json=corrected, headers=admin).status_code == 409
    assert any(
        row["action"] == "license.user.correct"
        for row in api.get("/admin/audit", headers=admin).json()
    )
    client = manager(api, keys)
    client.activate("corrected@example.com", sub["keys"][0]["key"], "Synthetic corrected owner")
    assert client.verify().permits(Module.GEOMETRY)


def test_corrupt_local_guard_and_untrusted_response_fail_closed(licensed, tmp_path):
    api, admin, sub, keys, engine, issuer, secret = licensed
    client = manager(api, keys)
    activate(client, sub)
    old = copy.deepcopy(client.state)
    with pytest.raises(ValueError):
        client.accept({"license": client.state["license"], "devices": "invalid-list"})
    assert client.state == old
    client.anchor.value = {"installation_id": client.state["installation_id"]}
    with pytest.raises(ValueError, match="Registro protegido"):
        LicenseManager(client.vault, client.anchor, keys, client.transport)


def test_server_maintenance_does_not_revoke_a_valid_local_license(licensed, monkeypatch):
    api, admin, sub, keys, engine, issuer, secret = licensed
    client = manager(api, keys)
    activate(client, sub)
    from fastapi import HTTPException

    from server import license_service

    def maintenance(*args):
        raise HTTPException(503, "Synthetic maintenance")

    monkeypatch.setattr(license_service, "sign", maintenance)
    with pytest.raises(OSError):
        client.check()
    assert client.verify().permits(Module.GEOMETRY)


def test_client_cannot_choose_expiry_and_revoked_seat_cannot_list_other_devices(licensed):
    api, admin, sub, keys, engine, issuer, secret = licensed
    first, second = manager(api, keys), manager(api, keys)
    bad = {
        "email": "tester@example.com",
        "key": sub["keys"][0]["key"],
        "installation_id": first.state["installation_id"],
        "label": "Synthetic",
        "expires_at": 9999999999,
    }
    assert api.post("/v1/activate", json=bad).status_code == 422
    value = activate(first, sub)
    activate(second, sub, 1)
    assert len(first.state["devices"]) == 2
    api.post("/admin/activations/" + value["activation_id"] + "/revoke", headers=admin, json={})
    first.check()
    assert first.state["devices"] == []
    assert first.verify().read_only
