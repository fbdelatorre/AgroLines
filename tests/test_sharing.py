import pytest
from sqlalchemy.orm import Session

from server.models import Farm
from server.permissions import ACTIONS, can
from tests.conftest import account


def prepare(api):
    owner, h1, _ = account(api)
    recipient, h2, _ = account(api, "recipient@example.com")
    _, h3, _ = account(api, "outsider@example.com")
    farm = api.post("/farms", headers=h1, json={"name": "São João"}).json()
    other = api.post("/farms", headers=h3, json={"name": "Propriedade privada"}).json()
    s1 = api.post(f"/farms/{farm['id']}/seasons", headers=h1, json={"name": "2026/2027"}).json()
    s2 = api.post(f"/farms/{farm['id']}/seasons", headers=h1, json={"name": "2027/2028"}).json()
    o1 = api.post(
        f"/farms/{farm['id']}/seasons/{s1['id']}/operations", headers=h1, json={"name": "Plantio"}
    ).json()
    o2 = api.post(
        f"/farms/{farm['id']}/seasons/{s1['id']}/operations", headers=h1, json={"name": "Colheita"}
    ).json()
    return owner, recipient, h1, h2, h3, farm, other, s1, s2, o1, o2


def share(api, farm, recipient, owner_headers, recipient_headers, scopes):
    invite = api.post(
        f"/farms/{farm['id']}/invitations",
        headers=owner_headers,
        json={"user_id": recipient["id"], "scopes": scopes},
    )
    assert invite.status_code == 201, invite.text
    accepted = api.post(
        "/invitations/" + invite.json()["id"] + "/accept", headers=recipient_headers
    )
    assert accepted.status_code == 200, accepted.text
    return invite.json()["id"]


@pytest.mark.parametrize("role", ["administrator", "editor", "operator", "viewer"])
def test_roles_and_farm_sharing(api, role):
    _, recipient, owner, invited, _, farm, other, *_ = prepare(api)
    share(api, farm, recipient, owner, invited, [{"role": role}])
    assert [f["id"] for f in api.get("/farms", headers=invited).json()] == [farm["id"]]
    assert api.get("/farms/" + other["id"], headers=invited).status_code == 404
    changed = api.patch("/farms/" + farm["id"], headers=invited, json={"name": "Alterada"})
    assert changed.status_code == (200 if "edit" in ACTIONS[role] else 404)
    members = api.get("/farms/" + farm["id"] + "/members", headers=invited)
    assert members.status_code == (200 if role == "administrator" else 404)
    assert (
        api.post(
            "/farms/" + farm["id"] + "/transfer", headers=invited, json={"user_id": recipient["id"]}
        ).status_code
        == 404
    )
    with Session(api.app.state.engine) as db:
        persisted = db.get(Farm, farm["id"])
        assert can(db, recipient["id"], persisted, "export") == ("export" in ACTIONS[role])
        assert not can(db, recipient["id"], persisted, "transfer")


def test_operation_scope_hides_siblings_and_prevents_parent_edits(api):
    _, recipient, owner, invited, outsider, farm, other, s1, s2, o1, o2 = prepare(api)
    share(
        api,
        farm,
        recipient,
        owner,
        invited,
        [{"role": "editor", "season_id": s1["id"], "operation_id": o1["id"]}],
    )
    base = "/farms/" + farm["id"] + "/seasons"
    assert api.get(base, headers=invited).json() == [s1]
    ops = base + "/" + s1["id"] + "/operations"
    assert api.get(ops, headers=invited).json() == [o1]
    assert api.get(base + "/" + s2["id"] + "/operations", headers=invited).status_code == 404
    assert api.patch(base + "/" + s1["id"], headers=invited, json={"name": "NO"}).status_code == 404
    assert api.post(ops, headers=invited, json={"name": "NO"}).status_code == 404
    assert api.patch(ops + "/" + o2["id"], headers=invited, json={"name": "NO"}).status_code == 404
    assert (
        api.patch(
            ops + "/" + o1["id"], headers=invited, json={"name": "Plantio autorizado"}
        ).status_code
        == 200
    )
    assert api.get("/farms/" + farm["id"] + "/audit", headers=invited).status_code == 404
    assert api.get("/farms/" + farm["id"], headers=outsider).status_code == 404
    assert api.get("/farms/" + other["id"], headers=invited).status_code == 404


def test_multiple_scopes_and_revocation_immediate(api):
    _, recipient, owner, invited, _, farm, _, s1, s2, o1, _ = prepare(api)
    invite_id = share(
        api,
        farm,
        recipient,
        owner,
        invited,
        [
            {"role": "viewer", "season_id": s2["id"]},
            {"role": "operator", "season_id": s1["id"], "operation_id": o1["id"]},
        ],
    )
    assert len(api.get("/farms/" + farm["id"] + "/seasons", headers=invited).json()) == 2
    assert api.post("/invitations/" + invite_id + "/revoke", headers=owner).status_code == 200
    assert api.get("/farms", headers=invited).json() == []
    assert api.get("/farms/" + farm["id"], headers=invited).status_code == 404
    assert api.post("/invitations/" + invite_id + "/accept", headers=invited).status_code == 409


def test_change_permission_and_individual_revocation(api):
    _, recipient, owner, invited, _, farm, _, s1, _, o1, _ = prepare(api)
    share(api, farm, recipient, owner, invited, [{"role": "editor"}])
    grant_id = api.get("/farms/" + farm["id"] + "/members", headers=owner).json()[1]["id"]
    assert (
        api.patch(
            "/permissions/" + grant_id, headers=invited, json={"role": "administrator"}
        ).status_code
        == 404
    )
    assert (
        api.patch(
            "/permissions/" + grant_id,
            headers=owner,
            json={"role": "viewer", "season_id": s1["id"], "operation_id": o1["id"]},
        ).status_code
        == 200
    )
    assert (
        api.patch("/farms/" + farm["id"], headers=invited, json={"name": "NO"}).status_code == 404
    )
    assert api.delete("/permissions/" + grant_id, headers=owner).status_code == 204
    assert api.get("/farms", headers=invited).json() == []


def test_invitation_is_account_bound_and_cannot_be_stolen(api):
    _, recipient, owner, invited, outsider, farm, _, _, _, _, _ = prepare(api)
    response = api.post(
        "/farms/" + farm["id"] + "/invitations",
        headers=owner,
        json={"email": recipient["email"], "scopes": [{"role": "viewer"}]},
    )
    invitation_id = response.json()["id"]
    assert response.json()["recipient_id"] == recipient["id"]
    assert (
        api.post("/invitations/" + invitation_id + "/accept", headers=outsider).status_code == 404
    )
    assert api.get("/invitations", headers=outsider).json() == []
    assert len(api.get("/invitations", headers=invited).json()) == 1
    assert (
        api.post("/invitations/" + invitation_id + "/decline", headers=invited).status_code == 200
    )
    assert api.post("/invitations/" + invitation_id + "/accept", headers=invited).status_code == 409
    assert api.get("/farms", headers=invited).json() == []


def test_scope_validation_and_owner_cannot_be_granted(api):
    _, recipient, owner, _, _, farm, other, s1, s2, o1, _ = prepare(api)
    invalid = [
        {"role": "owner"},
        {"role": "viewer", "operation_id": o1["id"]},
        {"role": "administrator", "season_id": s1["id"]},
    ]
    for scope in invalid:
        assert (
            api.post(
                "/farms/" + farm["id"] + "/invitations",
                headers=owner,
                json={"user_id": recipient["id"], "scopes": [scope]},
            ).status_code
            == 422
        )
    assert (
        api.post(
            "/farms/" + other["id"] + "/invitations",
            headers=owner,
            json={"user_id": recipient["id"], "scopes": [{"role": "viewer"}]},
        ).status_code
        == 404
    )
    assert (
        api.post(
            "/farms/" + farm["id"] + "/invitations",
            headers=owner,
            json={
                "user_id": recipient["id"],
                "scopes": [{"role": "viewer", "season_id": s2["id"], "operation_id": o1["id"]}],
            },
        ).status_code
        == 404
    )
    assert api.get("/invitations", headers=owner).json() == []


def test_transfer_owner_and_pending_invites_recheck_authority(api):
    owner_user, recipient, owner, invited, outsider, farm, _, *_ = prepare(api)
    share(api, farm, recipient, owner, invited, [{"role": "administrator"}])
    third_user = api.get("/auth/me", headers=outsider).json()
    pending = api.post(
        "/farms/" + farm["id"] + "/invitations",
        headers=owner,
        json={"user_id": third_user["id"], "scopes": [{"role": "viewer"}]},
    ).json()
    assert (
        api.post(
            "/farms/" + farm["id"] + "/transfer", headers=owner, json={"user_id": recipient["id"]}
        ).status_code
        == 200
    )
    assert api.get("/farms/" + farm["id"], headers=owner).status_code == 404
    assert api.get("/farms/" + farm["id"], headers=invited).json()["owned"] is True
    assert (
        api.post("/invitations/" + pending["id"] + "/accept", headers=outsider).status_code == 409
    )
    assert api.get("/farms", headers=owner).json() == []
    assert (
        api.get("/farms/" + farm["id"] + "/members", headers=invited).json()[0]["user"]["id"]
        == recipient["id"]
    )
    assert owner_user["id"] != recipient["id"]


def test_revoked_invitation_does_not_leak_updated_resource_names(api):
    _, recipient, owner, invited, _, farm, _, s1, _, o1, _ = prepare(api)
    invitation_id = share(
        api,
        farm,
        recipient,
        owner,
        invited,
        [{"role": "viewer", "season_id": s1["id"], "operation_id": o1["id"]}],
    )
    api.post("/invitations/" + invitation_id + "/revoke", headers=owner)
    api.patch("/farms/" + farm["id"], headers=owner, json={"name": "Nome privado atualizado"})
    api.patch(
        f"/farms/{farm['id']}/seasons/{s1['id']}",
        headers=owner,
        json={"name": "Safra privada atualizada"},
    )
    api.patch(
        f"/farms/{farm['id']}/seasons/{s1['id']}/operations/{o1['id']}",
        headers=owner,
        json={"name": "Operação privada atualizada"},
    )
    history = api.get("/invitations", headers=invited)
    assert "privad" not in history.text
    assert history.json()[0]["farm_name"] == "Propriedade indisponível"
    assert history.json()[0]["scopes"][0]["season_name"] is None
    assert history.json()[0]["scopes"][0]["operation_name"] is None
    assert "Operação privada atualizada" in api.get("/invitations", headers=owner).text
