from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from server import security
from server.db import make_engine
from server.models import AuthSession, User

bearer = HTTPBearer(auto_error=False)


def database(request: Request):
    if request.app.state.engine is None:
        request.app.state.engine = make_engine(request.app.state.settings)
    with Session(request.app.state.engine, expire_on_commit=False) as db:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise


DB = Annotated[Session, Depends(database, scope="function")]


def authenticated(
    db: DB,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    unauthorized = HTTPException(
        401, "Sessão inválida ou expirada.", headers={"WWW-Authenticate": "Bearer"}
    )
    if credentials is None:
        raise unauthorized
    session = db.scalar(
        select(AuthSession)
        .where(
            AuthSession.access_hash == security.digest(credentials.credentials),
            AuthSession.revoked.is_(False),
            AuthSession.access_expires > security.now(),
            AuthSession.refresh_expires > security.now(),
        )
        .with_for_update()
    )
    if session is None:
        raise unauthorized
    user = db.get(User, session.user_id)
    if user is None or not user.active:
        raise unauthorized
    return user, session


Actor = Annotated[tuple[User, AuthSession], Depends(authenticated)]
