"""Verify public PyPI publisher attestations; never executes downloaded wheels."""

import base64
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

TARGETS = [
    ("shapely", "2.2.0", "shapely-2.2.0-cp312-cp312-win_amd64.whl", "shapely/shapely"),
    (
        "scipy-openblas64",
        "0.3.34.106.0",
        "scipy_openblas64-0.3.34.106.0-py3-none-win_amd64.whl",
        "MacPython/openblas-libs",
    ),
    ("numpy", "2.5.4", "numpy-2.5.4-cp312-cp312-win_amd64.whl", "numpy/numpy-release"),
]


def get(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        return response.read()


def main():
    root = Path("build/publication-verification")
    root.mkdir(parents=True)
    rows = []
    for project, version, filename, repository in TARGETS:
        metadata = json.loads(get(f"https://pypi.org/pypi/{project}/{version}/json"))
        info = next(f for f in metadata["urls"] if f["filename"] == filename)
        raw = get(info["url"])
        digest = hashlib.sha256(raw).hexdigest()
        if digest != info["digests"]["sha256"]:
            raise ValueError("PyPI file digest mismatch")
        artifact = root / filename
        artifact.write_bytes(raw)
        provenance = get(f"https://pypi.org/integrity/{project}/{version}/{filename}/provenance")
        p = root / (filename + ".provenance.json")
        p.write_bytes(provenance)
        command = [
            "pypi-attestations",
            "verify",
            "pypi",
            "--repository",
            "https://github.com/" + repository,
            "--provenance-file",
            str(p),
            str(artifact),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        (root / (project + "-verification.txt")).write_text(result.stdout + result.stderr)
        verified = result.returncode == 0
        row = {
            "project": project,
            "version": version,
            "wheel": filename,
            "sha256": digest,
            "expected_repository": repository,
            "attestation_verified": verified,
            "exit_code": result.returncode,
            "tool": "pypi-attestations 0.0.30",
            "scope": "Publisher and artifact integrity, not license/source-binary equivalence",
            "tool_output": result.stdout + result.stderr,
        }
        if verified:
            # The verified statement binds this wheel; certificate identity/source
            # details remain in the original provenance, not an inferred rebuild.
            bundles = json.loads(provenance)["attestation_bundles"]
            row["publisher"] = [b["publisher"] for b in bundles]
            row["subjects"] = [
                json.loads(base64.b64decode(a["envelope"]["statement"]))["subject"]
                for b in bundles
                for a in b["attestations"]
            ]
        rows.append(row)
        print("AGROLINES_PUBLICATION_VERIFIED=" + json.dumps(row))
        artifact.unlink()  # Evidence artifact contains no wheel/native binary.
    (root / "verification.json").write_text(json.dumps(rows, indent=2) + "\n")
    if not all(r["attestation_verified"] for r in rows):
        raise SystemExit("Public attestations not all verified; no approval inferred")


if __name__ == "__main__":
    main()
