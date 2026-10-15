"""Maintainer-only standalone layout gate; never imported by the application."""

import argparse
import json
import shutil
from pathlib import Path

from distribution.payload import manifest, verify
from distribution.qt_payload import inspect_tree
from scripts.native_inventory import file_hash

ROOT = Path(__file__).resolve().parent.parent
BINDINGS = ("PySide6", "shiboken6")


def inspect_layout(root, embedded_modules):
    root = Path(root)
    internal = root / "_internal"
    metadata = json.loads((internal / "distribution/windows/metadata.json").read_text())
    if (
        metadata.get("distribution_channel") != "standalone-offline"
        or metadata.get("offline_only") is not True
        or metadata.get("store_identity")
    ):
        raise ValueError("Explicit standalone offline profile required")
    inspect_tree(root, embedded_modules)
    if not {"core.local_projects", "desktop.local_projects", "distribution.poc"}.issubset(
        embedded_modules
    ):
        raise ValueError("Missing own application modules in PYZ")
    for name in embedded_modules:
        if any(name == p or name.startswith(p + ".") for p in BINDINGS):
            raise ValueError("LGPL Python binding shadowed by embedded PYZ: " + name)
    for package in BINDINGS:
        if not (internal / package / "__init__.py").is_file():
            raise ValueError("Missing external LGPL Python package: " + package)
    for package in ("core", "desktop", "distribution"):
        if any((internal / package).rglob("*.py")) or any((internal / package).rglob("*.pyc")):
            raise ValueError("Own source/bytecode unexpectedly collected outside PYZ")
    forbidden = ("python.exe", "pip.exe", "psql.exe", "postgres.exe")
    if any(p.name.casefold() in forbidden for p in root.rglob("*")):
        raise ValueError("Unexpected external runtime installer/client")
    required = (
        "AgroLines.exe",
        "_internal/python312.dll",
        "_internal/PySide6/QtCore.pyd",
        "_internal/PySide6/Qt6Core.dll",
        "_internal/PySide6/Qt6WebEngineCore.dll",
        "_internal/PySide6/QtWebEngineProcess.exe",
        "_internal/PySide6/plugins/platforms/qwindows.dll",
        "_internal/desktop/map_assets/map-offline.html",
        "_internal/desktop/map_assets/leaflet.js",
        "_internal/desktop/map_assets/leaflet.css",
    )
    for name in required:
        if not (root / name).is_file():
            raise ValueError("Missing standalone runtime input: " + name)
    return {
        "external_bindings": list(BINDINGS),
        "own_modules_kept_in_pyz": True,
        "offline_only": True,
        "layout_passed": True,
        "legal_approval": False,
    }


def prepare_materials(root):
    # Import is confined to build time, not collected into the executable.
    from PyInstaller.archive.readers import CArchiveReader

    root = Path(root)
    embedded = CArchiveReader(str(root / "AgroLines.exe")).open_embedded_archive("PYZ.pyz")
    report = inspect_layout(root, embedded.toc)
    policy_path = ROOT / "distribution/windows/signing/native-policy.json"
    policy = json.loads(policy_path.read_text())
    for record in policy["files"]:
        if record["path"] == "AgroLinesPoC.exe" and record["group"] == "own":
            record["path"] = "AgroLines.exe"
    policy["profile"] = "standalone-offline"
    from distribution.libaec_build import SLOT
    from distribution.libaec_build import evidence as codec_evidence

    codec = codec_evidence(root)
    for record in policy["files"]:
        if record["path"] == SLOT:
            record.update(
                baseline_sha256=codec["binary_sha256"],
                group="libaec",
                packages=[],
                source_build_provenance="libaec-provenance.json",
                origin_confirmed=True,
                blocker="BSD source/build proven; signature/distribution review pending",
            )
    policy["inherited_store_policy_sha256"] = file_hash(policy_path)
    (root / "native-signing-policy.json").write_text(json.dumps(policy, indent=2), encoding="utf-8")
    docs = root / "standalone-docs"
    shutil.copytree(ROOT / "docs/distribution/standalone", docs)
    from distribution.legal_materials import prepare as prepare_legal

    prepare_legal(root)
    report["external_python_sources"] = [
        {"path": p.relative_to(root).as_posix(), "sha256": file_hash(p)}
        for package in BINDINGS
        for p in sorted((root / "_internal" / package).rglob("*.py"))
    ]
    (root / "standalone-layout.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (root / "payload-manifest.json").write_text(
        json.dumps(manifest(root), indent=2), encoding="utf-8"
    )


def validate_installer_input(root, version, manufacturer):
    root = Path(root)
    metadata = json.loads((root / "_internal/distribution/windows/metadata.json").read_text())
    if (
        metadata.get("distribution_channel") != "standalone-offline"
        or metadata.get("offline_only") is not True
        or metadata.get("store_identity")
        or metadata["version"] != version
        or metadata["manufacturer"] != manufacturer
    ):
        raise ValueError("Installer metadata/profile mismatch")
    if not verify(root, json.loads((root / "payload-manifest.json").read_text())):
        raise ValueError("Installer input hash mismatch")
    from distribution.legal_materials import verify as verify_legal

    verify_legal(root)
    from PyInstaller.archive.readers import CArchiveReader

    embedded = CArchiveReader(str(root / "AgroLines.exe")).open_embedded_archive("PYZ.pyz")
    return inspect_layout(root, embedded.toc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--manufacturer", required=True)
    arguments = parser.parse_args()
    validate_installer_input(arguments.root, arguments.version, arguments.manufacturer)
