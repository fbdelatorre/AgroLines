import hashlib
import secrets
import time
from contextlib import contextmanager
from threading import BoundedSemaphore

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import HTTPException
from sqlalchemy import select

from server.models import AuditEvent, RateBucket

hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
DUMMY_HASH = hasher.hash(secrets.token_urlsafe(32))
password_slots = BoundedSemaphore(4)


@contextmanager
def password_work():
    if not password_slots.acquire(blocking=False):
        raise HTTPException(429, "Servidor ocupado. Tente novamente.", headers={"Retry-After": "1"})
    try:
        yield
    finally:
        password_slots.release()


def now() -> int:
    return int(time.time())


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def token() -> str:
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    with password_work():
        return hasher.hash(password)


def verify_password(encoded: str, password: str) -> bool:
    with password_work():
        try:
            return hasher.verify(encoded, password)
        except (VerificationError, InvalidHashError):
            return False


def audit(db, actor_id, action, resource_id=None, farm_id=None):
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            resource_id=resource_id,
            farm_id=farm_id,
            occurred=now(),
        )
    )


def rate_limit(db, key: str, limit: int, window: int):
    # Persistent, atomic bucket creation and row lock: works across API workers.
    if db.bind.dialect.name == "postgresql":
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    key = digest(key)
    db.execute(
        insert(RateBucket)
        .values(key=key, started=now(), attempts=0)
        .on_conflict_do_nothing(index_elements=["key"])
    )
    bucket = db.scalar(select(RateBucket).where(RateBucket.key == key).with_for_update())
    if now() - bucket.started >= window:
        bucket.started, bucket.attempts = now(), 0
    bucket.attempts += 1
    blocked = bucket.attempts > limit
    # Keep attempts even if subsequent authentication fails.
    db.commit()
    if blocked:
        raise HTTPException(
            429,
            "Muitas tentativas. Aguarde e tente novamente.",
            headers={"Retry-After": str(window)},
        )
