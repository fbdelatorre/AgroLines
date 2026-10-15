"""Build-time public trust configuration; never accepts a private issuer key."""

import json
from pathlib import Path

from core.license_network import validate_origin
from core.license_protocol import decode


def prepare_trust(output, origin, keyfile, experimental=False, lab_ca_file=None):
    origin = validate_origin(origin)
    data = json.loads(Path(keyfile).read_text())
    if not isinstance(data, dict) or not 1 <= len(data) <= 8:
        raise ValueError("Public keyring required")
    if any(
        not isinstance(k, str) or not k or len(k) > 80 or len(decode(v)) != 32
        for k, v in data.items()
    ):
        raise ValueError("Only raw Ed25519 PUBLIC keys are accepted")
    if origin.endswith((".test", ".invalid", ".localhost")) and not experimental:
        raise ValueError("Synthetic licensing endpoint requires explicit experimental profile")
    if not experimental and any(k == "synthetic-lab-only" for k in data):
        raise ValueError("Synthetic licensing trust cannot be compiled into production")
    ca = None
    if lab_ca_file:
        if not experimental:
            raise ValueError("Laboratory TLS trust is forbidden in production")
        import ssl

        ca = Path(lab_ca_file).read_text(encoding="ascii")
        if len(ca) > 12000 or "PRIVATE KEY" in ca:
            raise ValueError("Only a public laboratory CA certificate is accepted")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cadata=ca)
        if (
            ca.count("-----BEGIN CERTIFICATE-----") != 1
            or context.cert_store_stats()["x509_ca"] != 1
        ):
            raise ValueError("Laboratory trust must identify a CA certificate")
    Path(output).write_text(
        "ORIGIN = "
        + repr(origin)
        + "\nKEYRING = "
        + repr(data)
        + "\nTEST_PROFILE = "
        + repr(bool(experimental))
        + "\nLAB_TLS_CA_PEM = "
        + repr(ca)
        + "\n",
        encoding="utf-8",
    )
    return {"origin": origin, "key_ids": sorted(data), "experimental": bool(experimental)}
