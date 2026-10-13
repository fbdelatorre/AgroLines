import io
import json
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit

import pytest

from desktop.client import ApiClient, ApiError
from desktop.vault import WindowsVault
from tests.conftest import account


class MemoryVault:
    available = True

    def __init__(self):
        self.data = None

    def load(self):
        return self.data

    def save(self, data):
        self.data = json.loads(json.dumps(data))
        return True

    def clear(self):
        self.data = None


class Response(io.BytesIO):
    pass


class ApiOpener:
    def __init__(self, api):
        self.api = api

    def open(self, request, timeout):
        response = self.api.request(
            request.method,
            urlsplit(request.full_url).path,
            headers=dict(request.header_items()),
            content=request.data,
        )
        if response.status_code >= 400:
            raise HTTPError(
                request.full_url,
                response.status_code,
                "API error",
                {},
                io.BytesIO(response.content),
            )
        return Response(response.content)


def client_for(api):
    client = ApiClient("http://127.0.0.1:8000", MemoryVault())
    client.opener = ApiOpener(api)
    return client


def test_client_real_session_refresh_and_revocation(api):
    _, _, _ = account(api)
    client = client_for(api)
    assert (
        client.authenticate("owner@example.com", "Senha sintetica 123!")["user"]["email"]
        == "owner@example.com"
    )
    assert client.offline_snapshot()["user"]["email"] == "owner@example.com"
    client.state["access_expires"] = int(time.time()) - 1
    assert client.request("GET", "/auth/me")["email"] == "owner@example.com"
    assert "password" not in client.vault.data
    sessions = client.request("GET", "/auth/sessions")
    current = sessions[-1]
    client.request("DELETE", "/auth/sessions/" + current["id"])
    with pytest.raises(ApiError, match="inválida"):
        client.synchronize_access()
    assert client.offline_snapshot() is None
    assert client.vault.data is None


def test_offline_cache_expires_and_removed_grants_are_cleared(api, monkeypatch):
    owner, owner_headers, _ = account(api)
    invited, invited_headers, _ = account(api, "invited@example.com")
    farm = api.post("/farms", json={"name": "Sintética"}, headers=owner_headers).json()
    invite = api.post(
        "/farms/" + farm["id"] + "/invitations",
        headers=owner_headers,
        json={"user_id": invited["id"], "scopes": [{"role": "viewer"}]},
    ).json()
    api.post("/invitations/" + invite["id"] + "/accept", headers=invited_headers)
    client = client_for(api)
    client.authenticate(invited["email"], "Senha sintetica 123!")
    assert len(client.offline_snapshot()["farms"]) == 1
    api.post("/invitations/" + invite["id"] + "/revoke", headers=owner_headers)
    assert client.synchronize_access()["farms"] == []
    clock = client.state["offline_until"]
    monkeypatch.setattr("desktop.client.time.time", lambda: clock)
    assert client.offline_snapshot() is None
    assert owner["id"] != invited["id"]


def test_server_binding_and_https_required():
    with pytest.raises(ValueError, match="HTTPS"):
        ApiClient("http://example.com")
    vault = MemoryVault()
    vault.data = {"origin": "https://other.example.com", "access_token": "synthetic-token"}
    client = ApiClient("https://example.com", vault)
    assert not client.state.get("access_token")
    with pytest.raises(ValueError):
        ApiClient("https://user:password@example.com")


def test_nonwindows_vault_never_writes_plaintext(tmp_path):
    if sys.platform == "win32":
        pytest.skip("Coberto pelo teste real de DPAPI no Windows")
    vault = WindowsVault(tmp_path / "session")
    assert not vault.save({"refresh_token": "sensitive-synthetic-token"})
    assert not (tmp_path / "session").exists()
    assert vault.load() is None


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI exige Windows")
def test_windows_dpapi_roundtrip_and_tampering(tmp_path):
    vault = WindowsVault(tmp_path / "session.dpapi")
    data = {"refresh_token": "sensitive-synthetic-token", "user": {"name": "Pessoa sintética"}}
    assert vault.save(data)
    assert b"sensitive-synthetic-token" not in vault.path.read_bytes()
    assert vault.load() == data
    vault.path.write_bytes(b"corrupt encrypted blob")
    assert vault.load() is None
    vault.clear()
    assert not vault.path.exists()
