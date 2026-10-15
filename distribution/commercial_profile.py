"""Build-time public trust configuration; never accepts a private issuer key."""

import json
from pathlib import Path

from core.license_network import validate_origin
from core.license_protocol import decode


def prepare_trust(output, origin, keyfile, experimental=False):
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
    Path(output).write_text(
        "ORIGIN = "
        + repr(origin)
        + "\nKEYRING = "
        + repr(data)
        + "\nTEST_PROFILE = "
        + repr(bool(experimental))
        + "\n",
        encoding="utf-8",
    )
    return {"origin": origin, "key_ids": sorted(data), "experimental": bool(experimental)}
