"""Real HTTP/DB workflow against a migrated disposable or development server.

Creates only synthetic accounts/properties; never deletes or resets the database.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

BASE = os.getenv("AGROLINES_API_URL", "http://127.0.0.1:8000").rstrip("/")


def request(method, path, body=None, token=None, expected=200):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(
        BASE + path,
        method=method,
        headers=headers,
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urlopen(req, timeout=10) as response:
            status, raw = response.status, response.read()
    except HTTPError as error:
        status, raw = error.code, error.read()
    allowed = expected if isinstance(expected, tuple) else (expected,)
    assert status in allowed, f"{method} {path}: status {status}, expected {expected}"
    return json.loads(raw) if raw else None


def main():
    suffix = uuid4().hex
    password = "Synthetic integration password 123!"
    accounts = []
    for label in ("owner", "recipient", "outsider"):
        email = f"{label}-{suffix}@example.com"
        user = request(
            "POST",
            "/auth/register",
            {"name": "Integração sintética", "email": email, "password": password},
            expected=201,
        )
        login = request("POST", "/auth/login", {"email": email, "password": password})
        accounts.append((user, login))
    owner, recipient, outsider = accounts
    access = owner[1]["access_token"]
    farm = request("POST", "/farms", {"name": "Integração sintética"}, access, 201)
    farm_id = farm["id"]
    season_path = f"/farms/{farm_id}/seasons"
    season = request("POST", season_path, {"name": "2026/2027"}, access, 201)
    other_season = request("POST", season_path, {"name": "Privada"}, access, 201)
    op_path = f"{season_path}/{season['id']}/operations"
    operation = request("POST", op_path, {"name": "Plantio"}, access, 201)
    request("POST", op_path, {"name": "Colheita privada"}, access, 201)
    invite = request(
        "POST",
        f"/farms/{farm_id}/invitations",
        {
            "user_id": recipient[0]["id"],
            "scopes": [
                {"role": "operator", "season_id": season["id"], "operation_id": operation["id"]}
            ],
        },
        access,
        201,
    )
    invited_access = recipient[1]["access_token"]
    request(
        "POST",
        f"/invitations/{invite['id']}/accept",
        token=outsider[1]["access_token"],
        expected=404,
    )
    request("POST", f"/invitations/{invite['id']}/accept", token=invited_access)
    assert request("GET", season_path, token=invited_access) == [season]
    assert request("GET", op_path, token=invited_access) == [operation]
    request(
        "GET", f"{season_path}/{other_season['id']}/operations", token=invited_access, expected=404
    )
    request("PATCH", f"{op_path}/{operation['id']}", {"name": "Forbidden"}, invited_access, 404)
    request("GET", f"/farms/{farm_id}", token=outsider[1]["access_token"], expected=404)
    request("POST", f"/invitations/{invite['id']}/revoke", token=access)
    request("GET", f"/farms/{farm_id}", token=invited_access, expected=404)
    competing = request(
        "POST",
        f"/farms/{farm_id}/invitations",
        {"user_id": recipient[0]["id"], "scopes": [{"role": "viewer"}]},
        access,
        201,
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        accept = pool.submit(
            request,
            "POST",
            f"/invitations/{competing['id']}/accept",
            None,
            invited_access,
            (200, 409),
        )
        revoke = pool.submit(
            request, "POST", f"/invitations/{competing['id']}/revoke", None, access, 200
        )
        accept.result()
        revoke.result()
    request("GET", f"/farms/{farm_id}", token=invited_access, expected=404)
    # Competing refresh requests must yield exactly one rotation and a family revocation.
    concurrent_session = request(
        "POST", "/auth/login", {"email": owner[0]["email"], "password": password}
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: request(
                    "POST",
                    "/auth/refresh",
                    {"token": concurrent_session["refresh_token"]},
                    expected=(200, 401),
                ),
                range(2),
            )
        )
    rotations = [result for result in results if "access_token" in result]
    assert len(rotations) == 1
    request("GET", "/auth/me", token=rotations[0]["access_token"], expected=401)
    rotated = request("POST", "/auth/refresh", {"token": owner[1]["refresh_token"]})
    request("GET", "/auth/me", token=access, expected=401)
    request("GET", "/auth/me", token=rotated["access_token"])
    request("POST", "/auth/refresh", {"token": owner[1]["refresh_token"]}, expected=401)
    request("GET", "/auth/me", token=rotated["access_token"], expected=401)
    request("POST", "/auth/logout", token=outsider[1]["access_token"], expected=204)
    request("GET", "/auth/me", token=outsider[1]["access_token"], expected=401)
    print(
        "HTTP/PostgreSQL: cadastro, sessão, escopos, isolamento, "
        "revogação, replay e concorrência aprovados."
    )


if __name__ == "__main__":
    main()
