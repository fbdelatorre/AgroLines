"""Exact additional commercial-profile inputs, independent of the old candidate."""

import json
from pathlib import Path

from distribution.legal_materials import digest, safe_file

ROOT = Path(__file__).resolve().parent.parent
MATERIALS = ROOT / "distribution/legal/commercial"


def records():
    return json.loads((MATERIALS / "materials.json").read_text())["packages"]


def additions(payload):
    metadata = Path(payload) / "_internal/distribution/windows/metadata.json"
    if (
        not metadata.exists()
        or json.loads(metadata.read_text()).get("distribution_channel") != "commercial-standalone"
    ):
        return {}, []
    natives, components = {}, []
    for package in records():
        paths = []
        for row in package["natives"]:
            source = safe_file(payload, row["path"])
            if digest(source) != row["sha256"]:
                raise ValueError("Commercial crypto input differs from pinned official wheel")
            natives[row["path"]] = {"component": package["name"], "sha256": row["sha256"]}
            paths.append(row["path"])
        for notice in package["notices"]:
            if digest(safe_file(MATERIALS, notice["file"])) != notice["sha256"]:
                raise ValueError("Changed commercial dependency notice")
        components.append(
            {
                "id": package["name"],
                "version": package["version"],
                "license_evidence": {
                    "PyNaCl": "Apache-2.0; embedded libsodium ISC notice included",
                    "cffi": "MIT-0; embedded libffi separately documented",
                    "pycparser": "BSD-3-Clause",
                }[package["name"]],
                "notice_files": [],
                "wheel_origin": package,
                "native_paths": paths,
            }
        )
    return natives, components
