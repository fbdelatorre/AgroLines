"""Synthetic Ed25519 consumer only; no AgroLines code, issuer or installation."""

import hashlib
import json
import sys
from pathlib import Path

from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey

signer = SigningKey.generate()  # ephemeral test key, never written, printed or trusted by AgroLines
message = b"synthetic Ed25519 frozen dependency control"
signature = signer.sign(message).signature
signer.verify_key.verify(message, signature)
try:
    signer.verify_key.verify(message + b"tamper", signature)
except BadSignatureError:
    pass
else:
    raise AssertionError("Modified message accepted")
files = []
for name in ("nacl._sodium", "_cffi_backend"):
    path = Path(sys.modules[name].__file__).resolve()
    files.append(
        {"module": name, "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    )
result = {
    "frozen": bool(getattr(sys, "frozen", False)),
    "signature_verified": True,
    "tampering_refused": True,
    "native_files": files,
    "component_only": True,
    "agrolines_license_issued": False,
    "sac_approved": False,
}
Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
