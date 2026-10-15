"""Fail-closed authorization and minimal private installer handoff. No external writes."""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def authorize(metadata, repository, confirmation, enabled, event):
    if (
        metadata.get("private") is not True
        or metadata.get("visibility") != "private"
        or metadata.get("full_name") != repository
        or confirmation != repository
        or enabled != "true"
        or event != "workflow_dispatch"
    ):
        raise PermissionError(
            "Private delivery requires verified private repository, "
            "exact owner confirmation and manual authorization"
        )
    return {"repository": repository, "private_verified": True, "binary_upload_authorized": True}


def lab_inputs(directory):
    root = Path(directory)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Public laboratory build inputs directory required")
    expected = {"public.json", "origin.json", "tls-ca.pem", "fixture.json"}
    if {path.name for path in root.iterdir()} != expected or any(
        path.is_symlink() or not path.is_file() for path in root.iterdir()
    ):
        raise ValueError(
            "Only the four public build inputs are allowed; never provide server secrets"
        )
    origin = json.loads((root / "origin.json").read_text())
    if origin.get("test_profile") is not True:
        raise ValueError("Explicit TESTE laboratory inputs required")
    from core.license_network import validate_origin
    from core.license_protocol import decode, verify

    endpoint = validate_origin(origin["origin"])
    keys = json.loads((root / "public.json").read_text())
    if set(keys) != {"synthetic-lab-only"}:
        raise ValueError("Dedicated synthetic key required")
    fixtures = json.loads((root / "fixture.json").read_text())
    for name in ("active", "revoked"):
        value = fixtures[name]
        installation = json.loads(decode(value["payload"]))["installation_id"]
        verified = verify(value, keys, installation)
        if verified["status"] != name:
            raise ValueError("Signed fixture state mismatch")
    if "PRIVATE KEY" in (root / "tls-ca.pem").read_text():
        raise ValueError("Private TLS key forbidden in client inputs")
    return endpoint


def stage(root, destination, versions):
    root, destination = Path(root).resolve(), Path(destination)
    for version in versions:
        if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version):
            raise ValueError("Invalid candidate version")
    destination.mkdir(parents=True, exist_ok=False)
    sources = [
        "dist/AgroLines/payload-manifest.json",
        "dist/AgroLines/standalone-layout.json",
        "docs/testing/windows11-vm-checklist.md",
        "docs/testing/private-installer.md",
        "docs/testing/test-license-lab.md",
        "evidence/functional/installed/result.json",
        "evidence/functional/signing/native.json",
    ]
    for version in versions:
        sources.extend(
            (
                f"dist/installers/AgroLines-Setup-{version}-TESTE-x64.exe",
                f"evidence/functional/artifact-{version}.json",
                f"evidence/functional/inno-{version}.log",
                f"evidence/functional/payload-{version}.json",
            )
        )
    fixture_root = root / "build/vm-fixtures"
    fixtures = json.loads((fixture_root / "fixture-manifest.json").read_text())
    allowed = {
        "TESTE.shp",
        "TESTE.shx",
        "TESTE.dbf",
        "TESTE.prj",
        "TESTE.cpg",
        "TESTE.gpkg",
        "TESTE.kml",
        "TESTE.kmz",
        "TESTE.geojson",
        "LINHA-NAO-SUPORTADA.geojson",
    }
    for row in fixtures["files"]:
        if row["name"] not in allowed:
            raise ValueError("Unexpected manual fixture file")
        path = fixture_root / row["name"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("Manual fixture hash mismatch")
        sources.append("build/vm-fixtures/" + row["name"])
    sources.append("build/vm-fixtures/fixture-manifest.json")
    manifest = []
    for name in sources:
        source = root / name
        if source.is_symlink() or not source.resolve().is_relative_to(root) or not source.is_file():
            raise ValueError("Missing/untrusted handoff input: " + name)
        relative = "synthetic-gis/" + source.name if name.startswith("build/vm-fixtures/") else name
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        with target.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        manifest.append({"path": relative, "sha256": digest, "bytes": target.stat().st_size})
        if target.suffix == ".exe":
            target.with_suffix(".exe.sha256").write_text(digest + "  " + target.name + "\n")
    (destination / "handoff-manifest.json").write_text(json.dumps(manifest, indent=2))
    (destination / "LEIA-ME.txt").write_text(
        "AgroLines TESTE, experimental e não assinado. Entrega privada autorizada.\n"
        "Leia docs/testing/. Não é homologação SAC nem distribuição comercial.\n"
        "Chaves de ativação e chaves privadas permanecem no servidor do titular.\n",
        encoding="utf-8",
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    gate = sub.add_parser("authorize")
    for name in ("metadata", "repository", "confirmation", "enabled", "event"):
        gate.add_argument("--" + name, required=True)
    inputs = sub.add_parser("lab-inputs")
    inputs.add_argument("directory", type=Path)
    pack = sub.add_parser("stage")
    pack.add_argument("--root", type=Path, default=Path("."))
    pack.add_argument("--destination", type=Path, required=True)
    pack.add_argument("--versions", nargs=2, required=True)
    args = parser.parse_args()
    if args.action == "authorize":
        print(
            json.dumps(
                authorize(
                    json.loads(Path(args.metadata).read_text(encoding="utf-8-sig")),
                    args.repository,
                    args.confirmation,
                    args.enabled,
                    args.event,
                )
            )
        )
    elif args.action == "lab-inputs":
        print(lab_inputs(args.directory))
    else:
        stage(args.root, args.destination, args.versions)


if __name__ == "__main__":
    main()
