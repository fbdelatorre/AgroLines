"""Versioned signed licensing messages. No issuer secrets or network in this module."""

import base64
import json
import re
from uuid import UUID

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

ALGORITHM = "Ed25519"
FIELDS = {
    "format",
    "subscription_id",
    "activation_id",
    "installation_id",
    "user_id",
    "plan",
    "issued_at",
    "expires_at",
    "generation",
    "status",
    "edition",
    "modules",
}


def encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def decode(data):
    if not isinstance(data, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", data):
        raise ValueError("Codificação de licença inválida.")
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def claims(value):
    if not isinstance(value, dict) or set(value) != FIELDS or value["format"] != 1:
        raise ValueError("Formato de licença não suportado.")
    for field in ("subscription_id", "activation_id", "installation_id", "user_id"):
        if str(UUID(value[field])) != value[field]:
            raise ValueError("Identificador de licença inválido.")
    for field in ("issued_at", "expires_at", "generation"):
        if type(value[field]) is not int or value[field] <= 0:
            raise ValueError("Data ou revisão de licença inválida.")
    if value["plan"] not in ("monthly", "annual") or value["status"] not in (
        "active",
        "suspended",
        "revoked",
    ):
        raise ValueError("Situação de licença inválida.")
    if value["edition"] not in ("individual", "professional", "enterprise"):
        raise ValueError("Edição inválida.")
    if value["modules"] != ["projects", "geometry", "backup"]:
        raise ValueError("Módulos não suportados por este perfil.")
    return value


def sign(value, key, kid):
    data = canonical(claims(value))
    return {
        "alg": ALGORITHM,
        "kid": kid,
        "payload": encode(data),
        "signature": encode(key.sign(data)),
    }


def verify(envelope, keyring, installation_id):
    try:
        if not isinstance(envelope, dict) or set(envelope) != {
            "alg",
            "kid",
            "payload",
            "signature",
        }:
            raise ValueError("Envelope inválido.")
        if envelope["alg"] != ALGORITHM or envelope["kid"] not in keyring:
            raise ValueError("Emissor de licença desconhecido.")
        if len(envelope["payload"]) > 12000:
            raise ValueError("Licença excede o limite.")
        data = decode(envelope["payload"])
        key = VerifyKey(decode(keyring[envelope["kid"]]))
        key.verify(data, decode(envelope["signature"]))
        # Only after cryptographic verification; canonical form excludes duplicate JSON keys.
        value = claims(json.loads(data))
        if canonical(value) != data or value["installation_id"] != installation_id:
            raise ValueError("Licença pertence a outra instalação.")
        return value
    except (BadSignatureError, TypeError, KeyError, OverflowError) as exc:
        raise ValueError("Assinatura de licença inválida.") from exc
