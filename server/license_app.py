"""Separately deployed licensing API; no GIS/project/upload or collaboration routes."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr
from sqlalchemy import select, update

from server import security
from server.config import Settings
from server.dependencies import DB, bearer
from server.license_service import devices, extend, issue, locked_subscription, totp_counter
from server.models import (
    AuditEvent,
    Credential,
    LicenseActivation,
    LicenseAdministrator,
    LicenseAdminSession,
    LicenseSlot,
    LicenseSubscription,
    User,
)


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Activate(Input):
    email: EmailStr
    key: SecretStr = Field(min_length=30, max_length=100)
    installation_id: UUID
    label: str = Field(min_length=1, max_length=80)


class Device(Input):
    activation_id: UUID
    installation_id: UUID
    credential: SecretStr = Field(min_length=30, max_length=100)


class Login(Input):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=1024)
    code: SecretStr = Field(min_length=6, max_length=6)


class NewUser(Input):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class NewSubscription(Input):
    user_id: UUID
    plan: Literal["monthly", "annual"]
    edition: Literal["individual", "professional", "enterprise"] = "individual"


class Change(Input):
    action: Literal["renew", "suspend", "revoke", "resume"]
    plan: Literal["monthly", "annual"] | None = None


def admin(
    request: Request,
    db: DB,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if not credentials:
        raise HTTPException(401, "Administração exige senha e segundo fator.")
    session = db.get(LicenseAdminSession, security.digest(credentials.credentials))
    if not session or session.expires <= security.now():
        raise HTTPException(401, "Sessão administrativa expirada.")
    administrator = db.get(LicenseAdministrator, session.user_id)
    user = db.get(User, session.user_id)
    if not administrator or not user or not user.active:
        raise HTTPException(403, "Acesso administrativo indisponível.")
    return administrator


Admin = Annotated[LicenseAdministrator, Depends(admin)]


def write_access(actor):
    if actor.role not in ("manager", "owner"):
        raise HTTPException(403, "Perfil somente de leitura.")


def authenticated_device(db, body):
    activation = db.get(LicenseActivation, str(body.activation_id))
    if (
        not activation
        or not security.secrets.compare_digest(
            activation.credential_hash, security.digest(body.credential.get_secret_value())
        )
        or activation.installation_id != str(body.installation_id)
    ):
        raise HTTPException(401, "Credencial da instalação inválida.")
    slot = db.get(LicenseSlot, activation.slot_id)
    subscription = locked_subscription(db, slot.subscription_id)
    # Consistent lock order subscription -> activation; refresh after waiting for another request.
    db.refresh(activation, with_for_update=True)
    return activation, slot, subscription


def create_app(issuer, settings=None, engine=None):
    app = FastAPI(
        title="AgroLines — Licenciamento", docs_url=None, redoc_url=None, openapi_url=None
    )
    app.state.settings = settings or Settings()
    app.state.engine = engine
    app.state.issuer = issuer

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        # FastAPI's default error response can echo secret input fields.
        return JSONResponse({"detail": "Campos inválidos. Confira os dados informados."}, 422)

    @app.middleware("http")
    async def security_headers(request, call_next):
        if request.url.scheme != "https":
            return JSONResponse({"detail": "Este serviço exige HTTPS."}, 400)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 16384:
                return JSONResponse({"detail": "Requisição excede o limite."}, 413)
        request._body = bytes(body)
        response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; "
                "base-uri 'none'; form-action 'self'",
            }
        )
        return response

    def limited(db, request, category):
        security.rate_limit(
            db, category + ":" + (request.client.host if request.client else "unknown"), 20, 900
        )

    @app.post("/v1/activate")
    def activate(body: Activate, request: Request, db: DB):
        limited(db, request, "license-activate")
        user = db.scalar(
            select(User).where(User.email == str(body.email).lower(), User.active.is_(True))
        )
        slot = db.scalar(
            select(LicenseSlot).where(
                LicenseSlot.key_hash == security.digest(body.key.get_secret_value())
            )
        )
        if not user or not slot:
            raise HTTPException(403, "Usuário ou chave inválidos.")
        sub = locked_subscription(db, slot.subscription_id)
        db.refresh(slot, with_for_update=True)
        if sub.user_id != user.id or sub.status != "active" or sub.expires <= security.now():
            raise HTTPException(403, "Chave indisponível ou assinatura vencida.")
        existing = (
            db.get(LicenseActivation, slot.current_activation) if slot.current_activation else None
        )
        if existing and (existing.installation_id != str(body.installation_id) or existing.revoked):
            raise HTTPException(
                409, "Esta vaga já está ocupada ou revogada. Solicite substituição."
            )
        # One installation cannot consume both seats of the same subscription.
        for row in devices(db, sub):
            other = (
                db.get(LicenseActivation, row["activation_id"]) if row["activation_id"] else None
            )
            if (
                other
                and other.id != (existing.id if existing else None)
                and not other.revoked
                and other.installation_id == str(body.installation_id)
            ):
                raise HTTPException(409, "Esta instalação já ocupa uma vaga da assinatura.")
        credential = security.token()
        activation = existing or LicenseActivation(
            slot_id=slot.id,
            installation_id=str(body.installation_id),
            device_label=body.label,
            credential_hash=security.digest(credential),
            revoked=False,
            generation=0,
            created=security.now(),
            checked=security.now(),
        )
        activation.credential_hash = security.digest(credential)
        activation.device_label = body.label
        db.add(activation)
        db.flush()
        previous = slot.current_activation
        claimed = db.execute(
            update(LicenseSlot)
            .where(LicenseSlot.id == slot.id, LicenseSlot.current_activation == previous)
            .values(current_activation=activation.id)
            .execution_options(synchronize_session=False)
        )
        if claimed.rowcount != 1:
            raise HTTPException(409, "Vaga ocupada por outra ativação; tente novamente.")
        db.refresh(slot)
        security.audit(db, user.id, "license.activate", activation.id)
        return {
            "license": issue(db, issuer, activation, sub),
            "credential": credential,
            "devices": devices(db, sub),
        }

    @app.post("/v1/check")
    def check(body: Device, request: Request, db: DB):
        limited(db, request, "license-check")
        activation, slot, sub = authenticated_device(db, body)
        user = db.get(User, sub.user_id)
        if slot.current_activation != activation.id or not user or not user.active:
            activation.revoked = True
        return {
            "license": issue(db, issuer, activation, sub),
            "devices": devices(db, sub)
            if not activation.revoked and sub.status == "active"
            else [],
        }

    @app.post("/v1/deactivate")
    def deactivate(body: Device, request: Request, db: DB):
        limited(db, request, "license-deactivate")
        activation, slot, sub = authenticated_device(db, body)
        activation.revoked = True
        # Key rotation is performed by an authenticated administrator, returned once.
        if slot.current_activation == activation.id:
            slot.current_activation = None
            slot.key_hash = security.digest(security.token())
        security.audit(db, sub.user_id, "license.deactivate", activation.id)
        return {"license": issue(db, issuer, activation, sub), "devices": []}

    @app.post("/admin/login")
    def login(body: Login, request: Request, db: DB):
        limited(db, request, "license-admin")
        security.rate_limit(db, "license-admin-email:" + str(body.email).lower(), 10, 900)
        user = db.scalar(select(User).where(User.email == str(body.email).lower()))
        credential = db.get(Credential, user.id) if user else None
        valid = security.verify_password(
            credential.password_hash if credential else security.DUMMY_HASH,
            body.password.get_secret_value(),
        )
        actor = (
            db.scalar(
                select(LicenseAdministrator)
                .where(LicenseAdministrator.user_id == user.id)
                .with_for_update()
            )
            if user
            else None
        )
        counter = (
            totp_counter(
                issuer.unseal(actor.totp_sealed), body.code.get_secret_value(), security.now()
            )
            if actor
            else None
        )
        if (
            not valid
            or not user
            or not user.active
            or not actor
            or counter is None
            or counter <= actor.last_counter
        ):
            raise HTTPException(401, "Credenciais administrativas inválidas.")
        actor.last_counter = counter
        access = security.token()
        db.add(
            LicenseAdminSession(
                token_hash=security.digest(access), user_id=user.id, expires=security.now() + 600
            )
        )
        security.audit(db, user.id, "license.admin.login")
        return {"access_token": access, "expires_in": 600, "role": actor.role}

    @app.post("/admin/logout")
    def logout(
        actor: Admin, db: DB, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]
    ):
        db.delete(db.get(LicenseAdminSession, security.digest(credentials.credentials)))
        security.audit(db, actor.user_id, "license.admin.logout")
        return {"ok": True}

    @app.get("/admin/users")
    def users(actor: Admin, db: DB):
        return [
            {"id": u.id, "name": u.name, "email": u.email}
            for u in db.scalars(select(User).order_by(User.id).limit(200))
        ]

    @app.post("/admin/users", status_code=201)
    def new_user(body: NewUser, actor: Admin, db: DB):
        write_access(actor)
        email = str(body.email).lower()
        if db.scalar(select(User).where(User.email == email)):
            raise HTTPException(409, "Usuário já cadastrado.")
        user = User(name=body.name, email=email)
        db.add(user)
        db.flush()
        security.audit(db, actor.user_id, "license.user.create", user.id)
        return {"id": user.id}

    @app.put("/admin/users/{identifier}")
    def correct_user(identifier: UUID, body: NewUser, actor: Admin, db: DB):
        write_access(actor)
        user = db.scalar(select(User).where(User.id == str(identifier)).with_for_update())
        if not user:
            raise HTTPException(404, "Usuário não encontrado.")
        email = str(body.email).lower()
        other = db.scalar(select(User).where(User.email == email, User.id != user.id))
        if other:
            raise HTTPException(409, "E-mail pertence a outro cadastro.")
        if db.get(LicenseAdministrator, user.id):
            raise HTTPException(403, "Conta administrativa exige manutenção privilegiada própria.")
        user.name, user.email = body.name, email
        security.audit(db, actor.user_id, "license.user.correct", user.id)
        return {"id": user.id}

    @app.get("/admin/subscriptions")
    def subscriptions(actor: Admin, db: DB):
        return [
            {
                "id": s.id,
                "user_id": s.user_id,
                "plan": s.plan,
                "expires": s.expires,
                "status": s.status,
                "devices": devices(db, s),
            }
            for s in db.scalars(
                select(LicenseSubscription).order_by(LicenseSubscription.id).limit(200)
            )
        ]

    @app.post("/admin/subscriptions", status_code=201)
    def new_subscription(body: NewSubscription, actor: Admin, db: DB):
        write_access(actor)
        user = db.get(User, str(body.user_id))
        if not user or not user.active:
            raise HTTPException(404, "Usuário indisponível.")
        sub = LicenseSubscription(
            user_id=user.id,
            plan=body.plan,
            edition=body.edition,
            expires=extend(security.now(), body.plan),
        )
        db.add(sub)
        db.flush()
        keys = []
        for position in (1, 2):
            key = security.token()
            db.add(
                LicenseSlot(
                    subscription_id=sub.id, position=position, key_hash=security.digest(key)
                )
            )
            keys.append({"slot": position, "key": key})
        security.audit(db, actor.user_id, "license.subscription.create", sub.id)
        return {"id": sub.id, "expires": sub.expires, "keys": keys}

    @app.post("/admin/subscriptions/{identifier}")
    def change_subscription(identifier: UUID, body: Change, actor: Admin, db: DB):
        write_access(actor)
        sub = locked_subscription(db, str(identifier))
        if not sub:
            raise HTTPException(404, "Assinatura não encontrada.")
        if sub.status == "revoked" and body.action != "revoke":
            raise HTTPException(409, "Revogação definitiva: emita outra assinatura após revisão.")
        if body.action == "renew":
            sub.plan = body.plan or sub.plan
            sub.expires = extend(max(sub.expires, security.now()), sub.plan)
            sub.status = "active"
        else:
            sub.status = {"suspend": "suspended", "revoke": "revoked", "resume": "active"}[
                body.action
            ]
        security.audit(db, actor.user_id, "license.subscription." + body.action, sub.id)
        return {"id": sub.id, "expires": sub.expires, "status": sub.status}

    @app.post("/admin/subscriptions/{identifier}/slots/{position}/replace")
    def replace_slot(identifier: UUID, position: int, actor: Admin, db: DB):
        write_access(actor)
        sub = locked_subscription(db, str(identifier))
        if not sub or position not in (1, 2):
            raise HTTPException(404, "Vaga não encontrada.")
        slot = db.scalar(
            select(LicenseSlot)
            .where(LicenseSlot.subscription_id == sub.id, LicenseSlot.position == position)
            .with_for_update()
        )
        if slot.current_activation:
            activation = db.get(LicenseActivation, slot.current_activation)
            activation.revoked = True
        key = security.token()
        slot.key_hash, slot.current_activation = security.digest(key), None
        security.audit(db, actor.user_id, "license.slot.replace", slot.id)
        return {"slot": position, "key": key}

    @app.post("/admin/activations/{identifier}/revoke")
    def revoke_activation(identifier: UUID, actor: Admin, db: DB):
        write_access(actor)
        activation = db.get(LicenseActivation, str(identifier))
        if not activation:
            raise HTTPException(404, "Ativação não encontrada.")
        slot = db.get(LicenseSlot, activation.slot_id)
        locked_subscription(db, slot.subscription_id)
        db.refresh(activation, with_for_update=True)
        activation.revoked = True
        security.audit(db, actor.user_id, "license.activation.revoke", activation.id)
        return {"ok": True}

    @app.get("/admin/audit")
    def audit_log(actor: Admin, db: DB):
        return [
            {
                "action": event.action,
                "resource_id": event.resource_id,
                "occurred": event.occurred,
                "actor_id": event.actor_id,
            }
            for event in db.scalars(
                select(AuditEvent)
                .where(AuditEvent.action.like("license.%"))
                .order_by(AuditEvent.occurred.desc())
                .limit(200)
            )
        ]

    from pathlib import Path

    assets = Path(__file__).parent / "license_admin"

    @app.get("/admin", include_in_schema=False)
    def admin_page():
        return FileResponse(assets / "index.html")

    @app.get("/admin/app.js", include_in_schema=False)
    def admin_script():
        return FileResponse(assets / "app.js", media_type="text/javascript")

    @app.get("/admin/style.css", include_in_schema=False)
    def admin_style():
        return FileResponse(assets / "style.css", media_type="text/css")

    return app
