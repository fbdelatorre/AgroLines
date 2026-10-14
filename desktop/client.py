import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from core.offline_policy import require_remote
from desktop.vault import WindowsVault


class ApiError(Exception):
    def __init__(self, message, status=0, field_errors=None):
        super().__init__(message)
        self.status = status
        self.field_errors = field_errors or {}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ApiClient:
    def __init__(self, url, vault=None):
        require_remote()
        parsed = urlsplit(url)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Endereço da API inválido.")
        if parsed.scheme == "http" and parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("Use HTTPS para servidores fora do computador local.")
        self.url = url.rstrip("/")
        self.vault = vault or WindowsVault()
        self.opener = build_opener(NoRedirect())
        self.state = self.vault.load() or {}
        if self.state.get("origin") != self.url:
            self.state = {}
        self.state["origin"] = self.url

    def raw(self, method, path, body=None, access=None):
        require_remote()
        headers = {"Accept": "application/json"}
        if access:
            headers["Authorization"] = "Bearer " + access
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        request = Request(self.url + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=5) as response:
                data = response.read()
                return json.loads(data) if data else None
        except HTTPError as exc:
            try:
                detail = json.loads(exc.read()).get("detail")
            except (ValueError, AttributeError):
                detail = None
            message = detail if isinstance(detail, str) else "Confira os dados informados."
            fields = {}
            if isinstance(detail, list):
                for error in detail:
                    location = error.get("loc", [])
                    if len(location) >= 2 and location[0] == "body":
                        key = location[1]
                        kind = error.get("type", "")
                        if key == "password" and kind == "string_too_short":
                            fields[key] = "Use pelo menos 6 caracteres."
                        elif key == "password" and kind == "string_too_long":
                            fields[key] = "Use até 128 caracteres."
                        elif key == "email":
                            fields[key] = "Informe um e-mail válido."
                        else:
                            fields[key] = "Confira este campo."
            raise ApiError(message, exc.code, fields) from None
        except (URLError, OSError, ValueError):
            raise ApiError("Servidor indisponível. Nenhuma alteração foi confirmada.") from None

    def persist(self):
        self.vault.save(self.state)

    def authenticate(self, email, password):
        tokens = self.raw("POST", "/auth/login", {"email": email, "password": password})
        self.state = {"origin": self.url, **tokens}
        self.persist()
        return self.synchronize_access()

    def request(self, method, path, body=None):
        if not self.state.get("access_token"):
            raise ApiError("Entre na sua conta.", 401)
        if time.time() >= self.state["access_expires"] - 30:
            try:
                tokens = self.raw("POST", "/auth/refresh", {"token": self.state["refresh_token"]})
                self.state.update(tokens)
                self.persist()
            except ApiError as exc:
                if exc.status == 401:
                    self.clear()
                raise
        try:
            return self.raw(method, path, body, self.state["access_token"])
        except ApiError as exc:
            if exc.status == 401:
                self.clear()
            raise

    def synchronize_access(self):
        # Invalidate cached grants before revalidation: never retain a removed farm.
        self.state.pop("farms", None)
        self.state.pop("offline_until", None)
        self.persist()
        user = self.request("GET", "/auth/me")
        farms = self.request("GET", "/farms")
        self.state.update(
            user=user,
            farms=farms,
            offline_until=min(int(time.time()) + 900, self.state["access_expires"]),
        )
        self.persist()
        return {"user": user, "farms": farms}

    def offline_snapshot(self):
        if time.time() < self.state.get("offline_until", 0) and time.time() < self.state.get(
            "access_expires", 0
        ):
            return {"user": self.state.get("user"), "farms": self.state.get("farms", [])}
        return None

    def clear(self):
        self.state = {"origin": self.url}
        self.vault.clear()

    def logout(self):
        try:
            self.request("POST", "/auth/logout")
            return "Sessão encerrada no servidor e neste computador."
        except ApiError:
            return "Sessão local removida. Sem conexão, a sessão remota expira no prazo original."
        finally:
            self.clear()
