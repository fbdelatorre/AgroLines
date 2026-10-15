"""Create synthetic public trust and signed fixtures; no real activation or secrets emitted."""

import argparse
import json
import time
from pathlib import Path
from uuid import uuid4

from nacl.signing import SigningKey

from core.license_protocol import encode, sign


class LabSigner:
    def __init__(self):
        self.key = SigningKey.generate()

    def sign(self, data):
        return self.key.sign(data).signature


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tls-origin")
    parser.add_argument("--tls-private-directory", type=Path)
    args = parser.parse_args()
    if bool(args.tls_origin) != bool(args.tls_private_directory):
        parser.error("TLS laboratory requires explicit origin and separate private directory")
    args.output.mkdir(parents=True, exist_ok=True)
    signer = LabSigner()
    keyring = {"synthetic-lab-only": encode(bytes(signer.key.verify_key))}
    (args.output / "public.json").write_text(json.dumps(keyring) + "\n")
    value = dict(
        format=1,
        subscription_id=str(uuid4()),
        activation_id=str(uuid4()),
        installation_id=str(uuid4()),
        user_id=str(uuid4()),
        plan="monthly",
        issued_at=int(time.time()),
        expires_at=int(time.time()) + 86400,
        generation=1,
        status="active",
        edition="individual",
        modules=["projects", "geometry", "backup"],
    )
    active = sign(value, signer, "synthetic-lab-only")
    value.update(generation=2, status="revoked")
    revoked = sign(value, signer, "synthetic-lab-only")
    (args.output / "fixture.json").write_text(
        json.dumps({"active": active, "revoked": revoked}) + "\n"
    )
    if args.tls_origin:
        from core.license_network import validate_origin
        from distribution.lab_tls import create_tls

        origin = validate_origin(args.tls_origin)
        private = args.tls_private_directory.resolve()
        if private.is_relative_to(Path(__file__).resolve().parent.parent) or private.is_relative_to(
            args.output.resolve()
        ):
            raise ValueError(
                "Private TLS server material must be outside checkout/public build inputs"
            )
        private.mkdir(mode=0o700, parents=True, exist_ok=False)
        (args.output / "tls-ca.pem").write_bytes(create_tls(private, origin))
        (args.output / "origin.json").write_text(
            json.dumps({"origin": origin, "test_profile": True})
        )
    # Private synthetic signer exists only in process memory. No private-key file or logging.


if __name__ == "__main__":
    main()
