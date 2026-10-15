"""Server-only initialization. Run interactively; never put passwords in command lines."""

import argparse
import getpass
import os
import secrets
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from server.config import Settings
from server.db import make_engine
from server.license_service import Issuer, enrollment_secret, export_public
from server.models import Credential, LicenseAdministrator, User
from server.security import hash_password


def secret_file(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(secrets.token_bytes(32))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["keys", "admin", "public"])
    parser.add_argument("--kid", required=True)
    parser.add_argument("--signing-file", required=True, type=Path)
    parser.add_argument("--wrapping-file", required=True, type=Path)
    parser.add_argument("--public-file", type=Path)
    args = parser.parse_args()
    if args.action == "keys":
        for path in (args.signing_file, args.wrapping_file):
            secret_file(path)
        print("Chaves criadas. Restrinja ACL e mantenha backup cifrado fora do aplicativo.")
        return
    issuer = Issuer.from_files(args.kid, args.signing_file, args.wrapping_file)
    if args.action == "public":
        if not args.public_file:
            parser.error("--public-file obrigatório")
        export_public(issuer, args.public_file)
        return
    email = input("E-mail administrativo: ").strip().lower()
    password = getpass.getpass("Senha exclusiva (mínimo 12 caracteres): ")
    if len(password) < 12 or password != getpass.getpass("Repita a senha: "):
        raise ValueError("Senha insuficiente ou divergente.")
    # This is enrollment, not public registration. Requires privileged server/DB access.
    secret, encoded = enrollment_secret()
    from server.license_service import totp_counter

    print("Cadastre este segredo TOTP em seu autenticador; não o envie ao suporte:", encoded)
    code = getpass.getpass("Código atual do autenticador: ")
    from server.security import now

    counter = totp_counter(secret, code, now())
    if counter is None:
        raise ValueError("Segundo fator não confirmado; nada foi cadastrado.")
    with Session(make_engine(Settings())) as db, db.begin():
        if db.scalar(select(User).where(User.email == email)):
            raise ValueError(
                "Conta existente: não sobrescrever credenciais. Revise com administrador."
            )
        user = User(name="Administração de licenças", email=email)
        db.add(user)
        db.flush()
        db.add(Credential(user_id=user.id, password_hash=hash_password(password)))
        db.add(
            LicenseAdministrator(
                user_id=user.id, role="owner", totp_sealed=issuer.seal(secret), last_counter=counter
            )
        )
    print("Administrador criado. Aguarde o próximo código para entrar.")


if __name__ == "__main__":
    main()
