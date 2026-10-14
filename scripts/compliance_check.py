"""Check material evidence; report legal/contractual issues without approving them."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

from distribution.qt_payload import external_qml, forbidden_family, qml_debug_tool

REFERENCE_SHA = "75fe75bd8d7097b826d46c4cd50576162f99aede3eb2db9def34d21a3b25ac90"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local(root, relative):
    name = PurePosixPath(relative)
    path = root / relative
    if name.is_absolute() or ".." in name.parts or "\\" in relative or path.is_symlink():
        raise ValueError("Unsafe compliance evidence path")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence escaped dossier")
    return path


def verify(root, payload_manifest=None):
    root = Path(root)
    registry = read(root / "inventory.json")
    reference = read(root / "evidence/payload.json")
    natives = read(root / "evidence/native.json")
    result = {
        key: []
        for key in (
            "technical_failure",
            "documentary_pending",
            "legal_pending",
            "contractual_pending",
        )
    }
    fail = result["technical_failure"].append
    components = {r["id"]: r for r in registry["components"]}
    if len(components) != len(registry["components"]):
        fail("Duplicate component")
    if registry["reference_msix_sha256"] != REFERENCE_SHA:
        fail("Reference MSIX changed")
    expected = {r["path"]: r["sha256"] for r in reference}
    actual = {r["path"]: r for r in registry["files"]}
    if len(actual) != len(registry["files"]) or set(actual) != set(expected):
        fail("Distributed file missing, duplicated or unauthorized")
    for path, row in actual.items():
        if expected.get(path) != row["sha256"]:
            fail("Unexpected hash: " + path)
        if row["component"] not in components:
            fail("Unregistered distributed dependency: " + path)
        if forbidden_family(path) or external_qml(path) or qml_debug_tool(path):
            fail("Forbidden Qt component: " + path)
    for native in natives:
        row = actual.get(native["path"], {})
        if row.get("owner_packages") != native["packages"]:
            fail("Owner/version drift: " + native["path"])
        version = (native["build_input_metadata"] or {}).get("product_version")
        if row.get("binary_product_version") != version:
            fail("PE version drift: " + native["path"])
        if row.get("sha256") != native["sha256"]:
            fail("Native hash drift: " + native["path"])
    for document in read(root / "documents.json")["files"]:
        path = local(root, document["path"])
        if not path.is_file() or sha(path) != document["sha256"]:
            fail("Document absent or changed: " + document["path"])
    for notice in read(root / "evidence/notices.json"):
        path = local(root, "notices/reference/" + notice["path"])
        if not path.is_file() or sha(path) != notice["sha256"]:
            fail("Original distributed notice missing/changed: " + notice["path"])
    for component in components.values():
        for notice in component["notice_files"]:
            if not local(root, notice).is_file():
                fail("Required license absent: " + notice)
        for copyright_row in component["copyright_evidence"]:
            path = local(root, copyright_row["file"])
            text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
            if any(line not in text for line in copyright_row["excerpt"]):
                fail("Copyright absent: " + component["id"])
        if (
            not component["notice_files"]
            or not component["copyright_evidence"]
            or not component.get("copyright_scope_confirmed")
        ):
            result["documentary_pending"].append(
                component["id"] + ": exact notices/copyright scope"
            )
        if not component["version"]:
            result["documentary_pending"].append(component["id"] + ": exact version not proven")
        if not component["corresponding_source_proven"] and component.get("source_requirement") != (
            "no_general_binary_source_requirement_identified"
        ):
            result["documentary_pending"].append(component["id"] + ": source/build correspondence")
    sources = read(root / "sources-index.json")
    for source in sources["sources"]:
        if not source.get("sha256") or not (source.get("url") or source.get("commit")):
            result["documentary_pending"].append(source["component"] + ": source integrity/origin")
    if payload_manifest is not None:
        supplied = read(payload_manifest)
        rows = supplied["files"]
        if (
            len(rows) != len({r["path"] for r in rows})
            or {r["path"]: r["sha256"] for r in rows} != expected
        ):
            fail(
                "Payload changed: separate candidate, inventory and legal-document review required"
            )
    result["legal_pending"].extend(
        [
            "LGPL Qt/GEOS/libiconv and other copyleft obligations, MSIX mechanism and EULA",
            "Privacy legal bases, transfers, Store security/privacy/account requirements",
        ]
    )
    result["contractual_pending"].extend(
        [
            "Exact Qt/Chromium/wheel supplier SBOM, patches, build recipes "
            "and redistribution evidence",
            "Microsoft Individual account/publisher, capabilities and Store-delivered trust",
        ]
    )
    result["technical_checks_passed"] = not result["technical_failure"]
    result["distribution_approved"] = False
    result["legal_compliance_approved"] = False
    return result


def manifest(root):
    root = Path(root)
    records = [
        {"path": p.relative_to(root).as_posix(), "sha256": sha(p), "size_bytes": p.stat().st_size}
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name not in ("documents.json", "verification.json")
    ]
    (root / "documents.json").write_text(
        json.dumps({"schema_version": 1, "files": records}, indent=2) + "\n", encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("docs/compliance"))
    parser.add_argument("--payload-manifest", type=Path)
    parser.add_argument("--submission", action="store_true")
    parser.add_argument("--refresh-documents", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.refresh_documents:
        manifest(args.root)
    result = verify(args.root, args.payload_manifest)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["technical_failure"]:
        raise SystemExit(1)
    if args.submission:
        # No automated test or editable approval boolean can clear legal/contractual gates.
        raise SystemExit(2)


if __name__ == "__main__":
    main()
