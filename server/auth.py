import logging
import smtplib

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from server import security
from server.dependencies import DB, Actor
from server.mail import send_recovery
from server.models import AuthSession, Credential, RefreshToken, ResetToken, User
from server.schemas import Login, Named, Recovery, Registration, Reset, TokenInput

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def public_user(user):
    return {"id": user.id, "name": user.name, "email": user.email}


def issue(db, user, settings, session=None):
    access, refresh = security.token(), security.token()
    if session is None:
        session = AuthSession(
            user_id=user.id, refresh_expires=security.now() + settings.refresh_ttl
        )
        db.add(session)
    session.access_hash = security.digest(access)
    session.refresh_hash = security.digest(refresh)
    session.access_expires = min(security.now() + settings.access_ttl, session.refresh_expires)
    db.flush()
    db.add(RefreshToken(digest=session.refresh_hash, session_id=session.id))
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "access_expires": session.access_expires,
        "refresh_expires": session.refresh_expires,
        "user": public_user(user),
    }


@router.post("/register", status_code=201)
def register(body: Registration, request: Request, db: DB):
    security.rate_limit(db, "register:" + request.client.host, 20, 3600)
    user = User(name=body.name, email=str(body.email).casefold())
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "E-mail já cadastrado.") from None
    db.add(Credential(user_id=user.id, password_hash=security.hash_password(body.password)))
    security.audit(db, user.id, "user.register", user.id)
    return public_user(user)


@router.post("/login")
def login(body: Login, request: Request, db: DB):
    settings = request.app.state.settings
    email = str(body.email).casefold()
    security.rate_limit(
        db, "login-ip:" + request.client.host, settings.login_limit * 10, settings.login_window
    )
    security.rate_limit(db, "login-email:" + email, settings.login_limit, settings.login_window)
    user = db.scalar(select(User).where(User.email == email))
    credential = db.get(Credential, user.id) if user else None
    valid = security.verify_password(
        credential.password_hash if credential else security.DUMMY_HASH, body.password
    )
    if not valid or user is None or not user.active:
        security.audit(db, None, "login.failed")
        db.commit()
        raise HTTPException(401, "E-mail ou senha inválidos.")
    if security.hasher.check_needs_rehash(credential.password_hash):
        credential.password_hash = security.hash_password(body.password)
    security.audit(db, user.id, "login.success")
    return issue(db, user, settings)


@router.post("/refresh")
def refresh(body: TokenInput, request: Request, db: DB):
    historical = db.get(RefreshToken, security.digest(body.token))
    session = (
        db.scalar(
            select(AuthSession).where(AuthSession.id == historical.session_id).with_for_update()
        )
        if historical
        else None
    )
    if session is None or session.revoked or session.refresh_expires <= security.now():
        raise HTTPException(401, "Renovação inválida ou expirada.")
    if session.refresh_hash != security.digest(body.token):
        session.revoked = True
        security.audit(db, session.user_id, "refresh.replay", session.id)
        db.commit()
        raise HTTPException(401, "Reutilização de token; sessão revogada.")
    user = db.get(User, session.user_id)
    if not user.active:
        raise HTTPException(401, "Conta indisponível.")
    security.audit(db, user.id, "session.refresh", session.id)
    return issue(db, user, request.app.state.settings, session)


@router.post("/logout", status_code=204)
def logout(actor: Actor, db: DB):
    user, session = actor
    session.revoked = True
    security.audit(db, user.id, "session.logout", session.id)


@router.get("/me")
def me(actor: Actor):
    return public_user(actor[0])


@router.patch("/me")
def change_name(body: Named, actor: Actor, db: DB):
    actor[0].name = body.name
    security.audit(db, actor[0].id, "user.name", actor[0].id)
    return public_user(actor[0])


@router.get("/sessions")
def sessions(actor: Actor, db: DB):
    return [
        {
            "id": s.id,
            "access_expires": s.access_expires,
            "refresh_expires": s.refresh_expires,
            "revoked": s.revoked,
        }
        for s in db.scalars(select(AuthSession).where(AuthSession.user_id == actor[0].id))
    ]


@router.delete("/sessions/{session_id}", status_code=204)
def revoke_session(session_id: str, actor: Actor, db: DB):
    session = db.scalar(
        select(AuthSession)
        .where(AuthSession.id == session_id, AuthSession.user_id == actor[0].id)
        .with_for_update()
    )
    if session is None:
        raise HTTPException(404, "Sessão não encontrada.")
    session.revoked = True
    security.audit(db, actor[0].id, "session.revoke", session.id)


@router.post("/recover", status_code=202)
def recover(body: Recovery, request: Request, db: DB):
    settings = request.app.state.settings
    if not settings.smtp_host:
        raise HTTPException(503, "Recuperação por e-mail não configurada.")
    security.rate_limit(db, "recover-ip:" + request.client.host, 10, 900)
    security.rate_limit(db, "recover-email:" + str(body.email).casefold(), 3, 900)
    user = db.scalar(select(User).where(User.email == str(body.email).casefold()))
    if user and user.active:
        raw = security.token()
        reset = ResetToken(
            digest=security.digest(raw), user_id=user.id, expires=security.now() + 900
        )
        db.add(reset)
        security.audit(db, user.id, "password.recovery")
        try:
            send_recovery(settings, user.email, raw)
        except (OSError, smtplib.SMTPException):
            db.rollback()
            logging.getLogger(__name__).error(
                "Falha no envio de recuperação; verificar serviço SMTP"
            )
            # Same response for existing and unknown users, even on delivery failure.
    return {"message": "Se a conta existir, receberá instruções por e-mail."}


@router.post("/reset", status_code=204)
def reset_password(body: Reset, db: DB):
    reset = db.scalar(
        select(ResetToken).where(ResetToken.digest == security.digest(body.token)).with_for_update()
    )
    if reset is None or reset.used or reset.expires <= security.now():
        raise HTTPException(400, "Código inválido ou expirado.")
    credential = db.scalar(
        select(Credential).where(Credential.user_id == reset.user_id).with_for_update()
    )
    credential.password_hash = security.hash_password(body.password)
    db.execute(update(ResetToken).where(ResetToken.user_id == reset.user_id).values(used=True))
    db.execute(update(AuthSession).where(AuthSession.user_id == reset.user_id).values(revoked=True))
    security.audit(db, reset.user_id, "password.reset")
