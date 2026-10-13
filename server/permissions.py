from fastapi import HTTPException
from sqlalchemy import select

from server.models import Farm, Operation, Permission, Season

ACTIONS = {
    "owner": {"read", "edit", "export", "manage", "transfer"},
    "administrator": {"read", "edit", "export", "manage"},
    "editor": {"read", "edit", "export"},
    "operator": {"read", "export"},
    "viewer": {"read"},
}


def grants(db, farm_id, user_id):
    return list(
        db.scalars(
            select(Permission).where(Permission.farm_id == farm_id, Permission.user_id == user_id)
        )
    )


def can(db, user_id, farm, action, season_id=None, operation_id=None):
    if farm.owner_id == user_id:
        return True
    for grant in grants(db, farm.id, user_id):
        if action not in ACTIONS[grant.role]:
            continue
        if grant.season_id is not None and grant.season_id != season_id:
            continue
        if grant.operation_id is not None and grant.operation_id != operation_id:
            continue
        return True
    return False


def visible(db, user_id, farm, season_id=None):
    if can(db, user_id, farm, "read", season_id):
        return True
    # Parent header only, no siblings/children outside granted operation.
    return any(season_id is None or g.season_id == season_id for g in grants(db, farm.id, user_id))


def farm_for(db, user_id, farm_id, action="read", lock=False):
    stmt = select(Farm).where(Farm.id == farm_id)
    farm = db.scalar(stmt.with_for_update() if lock else stmt)
    allowed = farm and (
        visible(db, user_id, farm) if action == "read" else can(db, user_id, farm, action)
    )
    if not allowed:
        raise HTTPException(404, "Propriedade não encontrada ou acesso não autorizado.")
    return farm


def validate_scope(db, farm, scope):
    if scope.season_id:
        season = db.get(Season, scope.season_id)
        if not season or season.farm_id != farm.id:
            raise HTTPException(404, "Safra não pertence à propriedade.")
    if scope.operation_id:
        operation = db.get(Operation, scope.operation_id)
        if not operation or operation.season_id != scope.season_id:
            raise HTTPException(404, "Operação não pertence à safra.")
