"""Owner-run private TLS/SQLite laboratory; never imported or shipped by the client."""

import argparse
import ipaddress
import json
import secrets
import time
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from core.license_network import validate_origin
from core.license_protocol import sign
from distribution.lab_tls import create_tls, write_private
from server.license_service import Issuer, extend, public_key
from server.models import Base, LicenseSlot, LicenseSubscription, User
from server.security import digest, token

KID = "synthetic-lab-only"
ROOT = Path(__file__).resolve().parent.parent


def lab_host(origin):
    from urllib.parse import urlsplit

    host = urlsplit(validate_origin(origin)).hostname
    if host == "localhost":
        return "127.0.0.1"
    address = ipaddress.IPv4Address(host)
    if not any(
        address in ipaddress.ip_network(net)
        for net in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8")
    ):
        raise ValueError("Laboratory requires localhost or an authorized private IPv4 address")
    return str(address)


def engine_for(directory):
    from sqlalchemy.engine import URL

    return create_engine(URL.create("sqlite", database=str(directory / "license-lab.sqlite")))


def initialize(directory, origin):
    directory = Path(directory).resolve()
    if directory.is_relative_to(ROOT):
        raise ValueError("Server state/secrets must remain outside the repository")
    origin = validate_origin(origin)
    host = lab_host(origin)
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    (directory / "LABORATORY-ONLY").write_text("Synthetic TLS/SQLite, no commercial validity\n")
    write_private(directory / "issuer.private-key", secrets.token_bytes(32))
    write_private(directory / "wrapping.private-key", secrets.token_bytes(32))
    issuer = load_issuer(directory)
    public = directory / "client-build-inputs"
    public.mkdir()
    (public / "public.json").write_text(json.dumps(public_key(issuer)))
    (public / "tls-ca.pem").write_bytes(create_tls(directory, origin))
    (public / "origin.json").write_text(json.dumps({"origin": origin, "test_profile": True}))
    (directory / "server.json").write_text(json.dumps({"origin": origin, "bind_host": host}))
    value = dict(
        format=1,
        subscription_id=str(uuid4()),
        activation_id=str(uuid4()),
        installation_id=str(uuid4()),
        user_id=str(uuid4()),
        plan="monthly",
        issued_at=int(time.time()),
        expires_at=int(time.time()) + 7 * 86400,
        generation=1,
        status="active",
        edition="individual",
        modules=["projects", "geometry", "backup"],
    )
    active = sign(value, issuer.signing_key, KID)
    value.update(generation=2, status="revoked")
    (public / "fixture.json").write_text(
        json.dumps({"active": active, "revoked": sign(value, issuer.signing_key, KID)})
    )
    engine = engine_for(directory)
    Base.metadata.create_all(engine)
    accounts = []
    try:
        with Session(engine) as db, db.begin():
            for plan in ("monthly", "annual"):
                email = plan + "@example.com"
                user = User(name="TESTE " + plan, email=email)
                db.add(user)
                db.flush()
                sub = LicenseSubscription(
                    user_id=user.id,
                    plan=plan,
                    expires=extend(int(time.time()), plan),
                    edition="individual",
                )
                db.add(sub)
                db.flush()
                keys = []
                for position in (1, 2):
                    key = token()
                    db.add(
                        LicenseSlot(subscription_id=sub.id, position=position, key_hash=digest(key))
                    )
                    keys.append({"slot": position, "key": key})
                accounts.append(
                    {"email": email, "subscription_id": sub.id, "plan": plan, "keys": keys}
                )
        write_private(directory / "test-accounts.json", json.dumps(accounts, indent=2).encode())
    finally:
        engine.dispose()
    return public


def load_issuer(directory):
    if not (directory / "LABORATORY-ONLY").is_file():
        raise ValueError("Explicit laboratory marker required")
    return Issuer.from_files(
        KID, directory / "issuer.private-key", directory / "wrapping.private-key"
    )


def application(directory):
    from server.config import Settings
    from server.license_app import create_app

    issuer = load_issuer(directory)
    return create_app(issuer, Settings(database_url="sqlite://"), engine_for(directory))


def change(directory, plan, action, seconds=120):
    load_issuer(directory)
    engine = engine_for(directory)
    try:
        with Session(engine) as db, db.begin():
            sub = db.scalar(
                select(LicenseSubscription).join(User).where(User.email == plan + "@example.com")
            )
            if sub is None or sub.status == "revoked":
                raise ValueError(
                    "Unknown or finally revoked synthetic subscription; use a fresh lab"
                )
            if action == "renew":
                sub.expires = extend(max(sub.expires, int(time.time())), sub.plan)
            elif action == "expire":
                sub.expires = int(time.time()) - 60
            elif action == "short-expiry":
                if not 60 <= seconds <= 3600:
                    raise ValueError("Synthetic expiry must be between 60 and 3600 seconds")
                sub.expires = int(time.time()) + seconds
            elif action == "revoke":
                sub.status = "revoked"
            else:
                raise ValueError("Unknown laboratory action")
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("init", "serve", "renew", "expire", "short-expiry", "revoke")
    )
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--origin")
    parser.add_argument("--plan", choices=("monthly", "annual"), default="monthly")
    parser.add_argument("--authorize-private-listener", action="store_true")
    parser.add_argument("--seconds", type=int, default=120)
    args = parser.parse_args()
    if args.action == "init":
        if not args.origin:
            parser.error("Explicit private HTTPS origin required")
        initialize(args.directory, args.origin)
        print(
            "TESTE: public build inputs prepared; restrict server ACL; "
            "do not upload server files or account keys."
        )
    elif args.action == "serve":
        if not args.authorize_private_listener:
            parser.error("Explicit authorization required to listen in the private laboratory")
        import uvicorn

        config = json.loads((args.directory / "server.json").read_text())
        host = lab_host(config["origin"])
        uvicorn.run(
            application(args.directory),
            host=host,
            port=443,
            ssl_certfile=str(args.directory / "tls-server.pem"),
            ssl_keyfile=str(args.directory / "tls-server.key"),
            proxy_headers=False,
            access_log=False,
        )
    else:
        change(args.directory, args.plan, args.action, args.seconds)
        print("Synthetic state updated. Reconnect the client and explicitly check its license.")


if __name__ == "__main__":
    main()
