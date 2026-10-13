from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, or_, select

from server import security
from server.auth import public_user
from server.dependencies import DB, Actor
from server.models import (
    AuditEvent,
    Farm,
    Invitation,
    InvitationScope,
    Operation,
    Permission,
    Season,
    User,
)
from server.permissions import ACTIONS, can, farm_for, grants, validate_scope, visible
from server.schemas import InviteInput, Named, Scope, Transfer

router = APIRouter(tags=["Propriedades e compartilhamento"])


def farm_json(db, farm, user_id):
    permissions = [
        {
            "id": g.id,
            "role": g.role,
            "season_id": g.season_id,
            "operation_id": g.operation_id,
            "season_name": db.get(Season, g.season_id).name if g.season_id else None,
            "operation_name": db.get(Operation, g.operation_id).name if g.operation_id else None,
            "actions": sorted(ACTIONS[g.role]),
        }
        for g in grants(db, farm.id, user_id)
    ]
    if farm.owner_id == user_id:
        permissions = [
            {
                "role": "owner",
                "season_id": None,
                "operation_id": None,
                "actions": sorted(ACTIONS["owner"]),
            }
        ]
    return {
        "id": farm.id,
        "name": farm.name,
        "owned": farm.owner_id == user_id,
        "permissions": permissions,
    }


@router.post("/farms", status_code=201)
def create_farm(body: Named, actor: Actor, db: DB):
    farm = Farm(owner_id=actor[0].id, name=body.name)
    db.add(farm)
    db.flush()
    security.audit(db, actor[0].id, "farm.create", farm.id, farm.id)
    return farm_json(db, farm, actor[0].id)


@router.get("/farms")
def list_farms(actor: Actor, db: DB):
    user_id = actor[0].id
    shared = select(Permission.farm_id).where(Permission.user_id == user_id)
    return [
        farm_json(db, f, user_id)
        for f in db.scalars(
            select(Farm)
            .where(or_(Farm.owner_id == user_id, Farm.id.in_(shared)))
            .order_by(Farm.name)
        )
    ]


@router.get("/farms/{farm_id}")
def get_farm(farm_id: str, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id)
    return farm_json(db, farm, actor[0].id)


@router.patch("/farms/{farm_id}")
def edit_farm(farm_id: str, body: Named, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "edit", lock=True)
    farm.name = body.name
    security.audit(db, actor[0].id, "farm.edit", farm.id, farm.id)
    return farm_json(db, farm, actor[0].id)


@router.post("/farms/{farm_id}/transfer")
def transfer(farm_id: str, body: Transfer, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "transfer", lock=True)
    recipient = db.get(User, body.user_id)
    if not recipient or not recipient.active or recipient.id == farm.owner_id:
        raise HTTPException(400, "Destinatário inválido.")
    previous = farm.owner_id
    farm.owner_id = recipient.id
    db.execute(
        delete(Permission).where(
            Permission.farm_id == farm.id, Permission.user_id.in_([previous, recipient.id])
        )
    )
    security.audit(db, previous, "farm.transfer", recipient.id, farm.id)
    return {"id": farm.id, "owner_id": recipient.id}


@router.get("/farms/{farm_id}/seasons")
def list_seasons(farm_id: str, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id)
    return [
        {"id": s.id, "name": s.name}
        for s in db.scalars(select(Season).where(Season.farm_id == farm.id).order_by(Season.name))
        if visible(db, actor[0].id, farm, s.id)
    ]


@router.post("/farms/{farm_id}/seasons", status_code=201)
def create_season(farm_id: str, body: Named, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "edit", lock=True)
    season = Season(farm_id=farm.id, name=body.name)
    db.add(season)
    db.flush()
    security.audit(db, actor[0].id, "season.create", season.id, farm.id)
    return {"id": season.id, "name": season.name}


def season_for(db, user_id, farm_id, season_id, action="read", lock=False):
    farm = farm_for(db, user_id, farm_id, lock=lock)
    season = db.get(Season, season_id)
    allowed = (
        visible(db, user_id, farm, season_id)
        if action == "read"
        else can(db, user_id, farm, action, season_id)
    )
    if not season or season.farm_id != farm.id or not allowed:
        raise HTTPException(404, "Safra não encontrada ou acesso não autorizado.")
    return farm, season


@router.patch("/farms/{farm_id}/seasons/{season_id}")
def edit_season(
    farm_id: str,
    season_id: str,
    body: Named,
    actor: Actor,
    db: DB,
):
    farm, season = season_for(db, actor[0].id, farm_id, season_id, "edit", lock=True)
    season.name = body.name
    security.audit(db, actor[0].id, "season.edit", season.id, farm.id)
    return {"id": season.id, "name": season.name}


@router.get("/farms/{farm_id}/seasons/{season_id}/operations")
def list_operations(farm_id: str, season_id: str, actor: Actor, db: DB):
    farm, season = season_for(db, actor[0].id, farm_id, season_id)
    return [
        {"id": o.id, "name": o.name}
        for o in db.scalars(
            select(Operation).where(Operation.season_id == season.id).order_by(Operation.name)
        )
        if can(db, actor[0].id, farm, "read", season.id, o.id)
    ]


@router.post("/farms/{farm_id}/seasons/{season_id}/operations", status_code=201)
def create_operation(
    farm_id: str,
    season_id: str,
    body: Named,
    actor: Actor,
    db: DB,
):
    farm, season = season_for(db, actor[0].id, farm_id, season_id, "edit", lock=True)
    operation = Operation(season_id=season.id, name=body.name)
    db.add(operation)
    db.flush()
    security.audit(db, actor[0].id, "operation.create", operation.id, farm.id)
    return {"id": operation.id, "name": operation.name}


@router.patch("/farms/{farm_id}/seasons/{season_id}/operations/{operation_id}")
def edit_operation(
    farm_id: str,
    season_id: str,
    operation_id: str,
    body: Named,
    actor: Actor,
    db: DB,
):
    farm, season = season_for(db, actor[0].id, farm_id, season_id, lock=True)
    operation = db.get(Operation, operation_id)
    if (
        not operation
        or operation.season_id != season.id
        or not can(db, actor[0].id, farm, "edit", season.id, operation.id)
    ):
        raise HTTPException(404, "Operação não encontrada ou acesso não autorizado.")
    operation.name = body.name
    security.audit(db, actor[0].id, "operation.edit", operation.id, farm.id)
    return {"id": operation.id, "name": operation.name}


@router.get("/farms/{farm_id}/members")
def members(farm_id: str, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "manage")
    entries = [
        {
            "role": "owner",
            "user": public_user(db.get(User, farm.owner_id)),
            "season_id": None,
            "operation_id": None,
        }
    ]
    for p in db.scalars(select(Permission).where(Permission.farm_id == farm.id)):
        entries.append(
            {
                "id": p.id,
                "role": p.role,
                "user": public_user(db.get(User, p.user_id)),
                "season_id": p.season_id,
                "operation_id": p.operation_id,
            }
        )
    return entries


@router.post("/farms/{farm_id}/invitations", status_code=201)
def invite(farm_id: str, body: InviteInput, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "manage", lock=True)
    recipient = (
        db.get(User, body.user_id)
        if body.user_id
        else db.scalar(select(User).where(User.email == str(body.email).casefold()))
    )
    # Bind invitations to an existing immutable account ID, not a future claimant of an email.
    if not recipient or not recipient.active or recipient.id in (farm.owner_id, actor[0].id):
        raise HTTPException(400, "Destinatário deve ter uma conta válida no AgroLines.")
    invitation = Invitation(
        farm_id=farm.id,
        inviter_id=actor[0].id,
        recipient_id=recipient.id,
        expires=security.now() + 7 * 86400,
    )
    db.add(invitation)
    db.flush()
    for scope in body.scopes:
        validate_scope(db, farm, scope)
        db.add(InvitationScope(invitation_id=invitation.id, **scope.model_dump()))
    security.audit(db, actor[0].id, "invitation.create", invitation.id, farm.id)
    return {"id": invitation.id, "status": invitation.status, "recipient_id": recipient.id}


def invitation_json(db, i):
    return {
        "id": i.id,
        "farm_id": i.farm_id,
        "farm_name": db.get(Farm, i.farm_id).name,
        "inviter_id": i.inviter_id,
        "inviter_name": db.get(User, i.inviter_id).name,
        "recipient_id": i.recipient_id,
        "recipient_name": db.get(User, i.recipient_id).name,
        "status": "expired" if i.status == "pending" and i.expires <= security.now() else i.status,
        "expires": i.expires,
        "scopes": [
            {
                "role": s.role,
                "season_id": s.season_id,
                "operation_id": s.operation_id,
                "season_name": db.get(Season, s.season_id).name if s.season_id else None,
                "operation_name": db.get(Operation, s.operation_id).name
                if s.operation_id
                else None,
            }
            for s in db.scalars(
                select(InvitationScope).where(InvitationScope.invitation_id == i.id)
            )
        ],
    }


@router.get("/invitations")
def list_invitations(actor: Actor, db: DB):
    return [
        invitation_json(db, i)
        for i in db.scalars(
            select(Invitation).where(
                or_(Invitation.recipient_id == actor[0].id, Invitation.inviter_id == actor[0].id)
            )
        )
    ]


@router.post("/invitations/{invitation_id}/{decision}")
def decide_invitation(invitation_id: str, decision: str, actor: Actor, db: DB):
    invitation = db.get(Invitation, invitation_id)
    if not invitation:
        raise HTTPException(404, "Convite não encontrado.")
    # Serialize acceptance/revocation/transfer/grant updates on the farm row.
    farm = db.scalar(select(Farm).where(Farm.id == invitation.farm_id).with_for_update())
    db.refresh(invitation)
    if decision == "revoke":
        if not can(db, actor[0].id, farm, "manage"):
            raise HTTPException(404, "Convite não encontrado.")
        invitation.status = "revoked"
        db.execute(delete(Permission).where(Permission.invitation_id == invitation.id))
    elif decision in ("accept", "decline"):
        if invitation.recipient_id != actor[0].id:
            raise HTTPException(404, "Convite não encontrado.")
        if invitation.status != "pending" or invitation.expires <= security.now():
            raise HTTPException(409, "Convite não está disponível.")
        if not can(db, invitation.inviter_id, farm, "manage"):
            raise HTTPException(409, "Responsável pelo convite perdeu autorização.")
        invitation.status = "accepted" if decision == "accept" else "declined"
        if decision == "accept":
            for scope in db.scalars(
                select(InvitationScope).where(InvitationScope.invitation_id == invitation.id)
            ):
                validate_scope(db, farm, scope)
                db.add(
                    Permission(
                        farm_id=farm.id,
                        user_id=actor[0].id,
                        invitation_id=invitation.id,
                        role=scope.role,
                        season_id=scope.season_id,
                        operation_id=scope.operation_id,
                    )
                )
    else:
        raise HTTPException(400, "Ação inválida.")
    security.audit(db, actor[0].id, "invitation." + decision, invitation.id, farm.id)
    return invitation_json(db, invitation)


@router.patch("/permissions/{permission_id}")
def change_permission(permission_id: str, body: Scope, actor: Actor, db: DB):
    permission = db.get(Permission, permission_id)
    if not permission:
        raise HTTPException(404, "Permissão não encontrada.")
    farm = farm_for(db, actor[0].id, permission.farm_id, "manage", lock=True)
    permission = db.scalar(
        select(Permission)
        .where(Permission.id == permission_id)
        .execution_options(populate_existing=True)
    )
    if permission is None:
        raise HTTPException(404, "Permissão não encontrada.")
    validate_scope(db, farm, body)
    for key, value in body.model_dump().items():
        setattr(permission, key, value)
    security.audit(db, actor[0].id, "permission.change", permission.id, farm.id)
    return {"id": permission.id, **body.model_dump()}


@router.delete("/permissions/{permission_id}", status_code=204)
def revoke_permission(permission_id: str, actor: Actor, db: DB):
    permission = db.get(Permission, permission_id)
    if not permission:
        raise HTTPException(404, "Permissão não encontrada.")
    farm = farm_for(db, actor[0].id, permission.farm_id, "manage", lock=True)
    permission = db.scalar(
        select(Permission)
        .where(Permission.id == permission_id)
        .execution_options(populate_existing=True)
    )
    if permission is None:
        raise HTTPException(404, "Permissão não encontrada.")
    security.audit(db, actor[0].id, "permission.revoke", permission.id, farm.id)
    db.delete(permission)


@router.get("/farms/{farm_id}/audit")
def audit_events(farm_id: str, actor: Actor, db: DB):
    farm_for(db, actor[0].id, farm_id, "manage")
    return [
        {
            "id": a.id,
            "actor_id": a.actor_id,
            "action": a.action,
            "resource_id": a.resource_id,
            "occurred": a.occurred,
        }
        for a in db.scalars(
            select(AuditEvent)
            .where(AuditEvent.farm_id == farm_id)
            .order_by(AuditEvent.occurred.desc())
            .limit(200)
        )
    ]
