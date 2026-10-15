"""Independent license service. Issuer key material is server-only, never frozen."""

import base64
import calendar
import hashlib
import hmac
import json
import secrets
import struct
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select

from core.license_protocol import sign
from server import security
from server.models import LicenseActivation, LicenseSlot, LicenseSubscription


@dataclass(frozen=True)
class Issuer:
    kid: str
    signing_key: Ed25519PrivateKey
    wrapping_key: bytes

    @classmethod
    def from_files(cls, kid, signing_file, wrapping_file):
        values = []
        for filename in (signing_file, wrapping_file):
            path = Path(filename)
            if path.stat().st_mode & 0o077 and __import__("os").name != "nt":
                raise ValueError("Chave de servidor acessível a outros usuários.")
            data = path.read_bytes()
            if len(data) != 32:
                raise ValueError("Chave de servidor deve conter exatamente 32 bytes.")
            values.append(data)
        if not kid or len(kid) > 80:
            raise ValueError("Identificador público de chave inválido.")
        return cls(kid, Ed25519PrivateKey.from_private_bytes(values[0]), values[1])

    def seal(self, value):
        nonce = secrets.token_bytes(12)
        return nonce + AESGCM(self.wrapping_key).encrypt(nonce, value, b"agrolines-admin-totp-v1")

    def unseal(self, value):
        return AESGCM(self.wrapping_key).decrypt(value[:12], value[12:], b"agrolines-admin-totp-v1")


def extend(timestamp, plan):
    start = datetime.fromtimestamp(timestamp, UTC)
    month = start.month - 1 + (12 if plan == "annual" else 1)
    year, month = start.year + month // 12, month % 12 + 1
    return int(
        start.replace(
            year=year, month=month, day=min(start.day, calendar.monthrange(year, month)[1])
        ).timestamp()
    )


def totp(secret, counter):
    digest = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 15
    code = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % 1000000
    return f"{code:06d}"


def totp_counter(secret, code, timestamp):
    if not isinstance(code, str) or len(code) != 6 or not code.isascii() or not code.isdigit():
        return None
    for counter in range(timestamp // 30 - 1, timestamp // 30 + 2):
        if counter >= 0 and hmac.compare_digest(totp(secret, counter), code):
            return counter
    return None


def issue(db, issuer, activation, subscription):
    activation.generation += 1
    activation.checked = security.now()
    db.flush()
    return sign(
        {
            "format": 1,
            "subscription_id": subscription.id,
            "activation_id": activation.id,
            "installation_id": activation.installation_id,
            "user_id": subscription.user_id,
            "plan": subscription.plan,
            "issued_at": security.now(),
            "expires_at": subscription.expires,
            "generation": activation.generation,
            "status": "revoked"
            if activation.revoked or subscription.status == "revoked"
            else subscription.status,
            "edition": subscription.edition,
            "modules": ["projects", "geometry", "backup"],
        },
        issuer.signing_key,
        issuer.kid,
    )


def locked_subscription(db, identifier):
    return db.scalar(
        select(LicenseSubscription).where(LicenseSubscription.id == identifier).with_for_update()
    )


def devices(db, subscription):
    slots = db.scalars(select(LicenseSlot).where(LicenseSlot.subscription_id == subscription.id))
    result = []
    for slot in slots:
        active = (
            db.get(LicenseActivation, slot.current_activation) if slot.current_activation else None
        )
        result.append(
            {
                "slot": slot.position,
                "activation_id": active.id if active else None,
                "label": active.device_label if active else None,
                "revoked": active.revoked if active else False,
            }
        )
    return sorted(result, key=lambda row: row["slot"])


def public_key(issuer):
    from core.license_protocol import encode

    return {issuer.kid: encode(issuer.signing_key.public_key().public_bytes_raw())}


def export_public(issuer, path):
    Path(path).write_text(json.dumps(public_key(issuer), indent=2) + "\n")


def enrollment_secret():
    value = secrets.token_bytes(20)
    return value, base64.b32encode(value).decode().rstrip("=")
