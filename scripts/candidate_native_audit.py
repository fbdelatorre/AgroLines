"""Compare the reduced candidate with immutable original evidence, without granting trust."""

import argparse
import csv
import importlib.metadata
import json
from collections import Counter
from pathlib import Path

from distribution.qt_payload import forbidden_family, inspect_tree
from scripts.native_inventory import file_hash
from scripts.signing_pipeline import read


def license_evidence(packages):
    result = []
    for package in packages:
        if package["name"] == "CPython":
            result.append(
                {
                    "package": package,
                    "evidence": "third-party-notices/Python-LICENSE.txt",
                    "scope": "CPython plus its separately licensed bundled components",
                }
            )
            continue
        metadata = importlib.metadata.distribution(package["name"]).metadata
        result.append(
            {
                "package": package,
                "declared_license": metadata.get("License-Expression")
                or metadata.get("License", "not declared"),
                "evidence": "third-party-notices/" + package["name"],
                "scope": "Package metadata; not a license grant for every vendored PE",
            }
        )
    return result


def inspect(root, native, signatures, tools, inputs, sources, loads=None):
    root = Path(root).resolve()
    original = {
        r["path"].casefold(): r
        for r in csv.DictReader(
            Path("docs/native-store-audit/inventario-arquivos.csv").open(encoding="utf-8")
        )
    }
    signed = {str(Path(r["path"]).resolve()).casefold(): r for r in signatures["files"]}
    verified = {str(Path(r["path"]).resolve()).casefold(): r for r in tools["files"]}
    source_map = {r["destination"].casefold(): r for r in inputs["files"]}
    source_meta = {r["source"].casefold(): r for r in sources["files"]}
    observations = {}
    for phase in (loads or {}).get("phases", []):
        for module in phase["modules"]:
            if module.get("payload_relative"):
                observations.setdefault(module["payload_relative"].casefold(), set()).add(
                    phase["name"]
                )
    qt = inspect_tree(root, inputs["python_modules"])
    rows = []
    for item in native["files"]:
        path = Path(item["path"]).resolve()
        relative = path.relative_to(root).as_posix()
        old = original.get(relative.casefold())
        source = source_map.get(relative.removeprefix("_internal/").casefold())
        meta = source_meta.get(source["source"].casefold()) if source else None
        exact_source = bool(
            source
            and source["source_sha256"] == item["sha256"]
            and meta
            and meta["sha256"] == item["sha256"]
        )
        sig, tool = signed[str(path).casefold()], verified[str(path).casefold()]
        if not sig["integrity_matches"] or not tool["integrity_matches"]:
            raise ValueError("Candidate bytes changed during verification")
        row = {
            "path": relative,
            "sha256": item["sha256"],
            "architecture": item["architecture"],
            "group": item["group"],
            "packages": item["packages"],
            "original_sha256": old["sha256"] if old else None,
            "change": "unchanged"
            if old and old["sha256"] == item["sha256"]
            else "changed"
            if old
            else "added",
            "signature": sig,
            "signtool": tool,
            "build_input": source,
            "build_input_metadata": meta,
            "exact_build_source_match": exact_source,
            "importers_by_dll_name": sorted(
                entry["destination"]
                for entry in inputs["files"]
                if any(
                    Path(name).name.casefold() == path.name.casefold() for name in entry["imports"]
                )
            ),
            "pinned_origin_confirmed": item["origin_basis"]
            in ("exact_sha256_pinned_input", "entrypoint_manifest"),
            "loaded_phases": sorted(observations.get(relative.casefold(), [])),
            "not_observed_is_not_unused": True,
            "license_review": "See docs/qt-minimal/licencas-e-homologacao.md; not approved",
            "package_license_evidence": license_evidence(item["packages"]),
            "re_signing_rights_confirmed": False,
            "trust_route": "Preserve accepted upstream signature"
            if sig["status"] == "Valid" and tool["exit_code"] == 0
            else "Embedded signing or real Store catalog trust not yet demonstrated",
        }
        if source and any(forbidden_family(name) for name in source["imports"]):
            raise ValueError("Retained PE depends on forbidden Qt family")
        rows.append(row)
    paths = {r["path"].casefold() for r in rows}
    removed = [
        {"path": r["path"], "sha256": r["sha256"], "family": forbidden_family(r["path"])}
        for key, r in original.items()
        if key not in paths
    ]
    summary = {
        "pe_files": len(rows),
        "accepted": sum(
            r["signature"]["status"] == "Valid" and r["signtool"]["exit_code"] == 0 for r in rows
        ),
        "unsigned": sum(r["signature"]["status"] == "NotSigned" for r in rows),
        "unsigned_observed": sum(
            r["signature"]["status"] == "NotSigned" and bool(r["loaded_phases"]) for r in rows
        )
        if loads
        else None,
        "origin_unconfirmed": sum(not r["pinned_origin_confirmed"] for r in rows),
        "exact_build_source_matches": sum(r["exact_build_source_match"] for r in rows),
        "changes": dict(Counter(r["change"] for r in rows)),
        "removed": len(removed),
        "qt_guard": qt,
        "sac_approved": False,
        "legal_compliance_approved": False,
    }
    return {
        "summary": summary,
        "files": rows,
        "removed": removed,
        "observations": loads,
        "source_file_sha256": file_hash(root / "AgroLinesPoC.exe"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "native", "signatures", "tools", "inputs", "sources", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--loads", type=Path)
    args = parser.parse_args()
    result = inspect(
        args.root,
        *[
            read(getattr(args, key))
            for key in ("native", "signatures", "tools", "inputs", "sources")
        ],
        read(args.loads) if args.loads else None,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    with args.output.with_suffix(".csv").open("w", encoding="utf-8", newline="") as stream:
        fields = [
            "path",
            "sha256",
            "architecture",
            "group",
            "change",
            "pinned_origin_confirmed",
            "exact_build_source_match",
            "build_input",
            "build_input_metadata",
            "importers_by_dll_name",
            "loaded_phases",
            "signature",
            "signtool",
            "package_license_evidence",
            "re_signing_rights_confirmed",
            "trust_route",
        ]
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for row in result["files"]:
            writer.writerow(
                {
                    key: json.dumps(row[key]) if isinstance(row[key], (list, dict)) else row[key]
                    for key in fields
                }
            )
    print("AGROLINES_MINIMAL_NATIVE=" + json.dumps(result["summary"]))
    print("AGROLINES_MINIMAL_REMOVED=" + json.dumps(result["removed"]))
    print("::group::Exact native dependency graph (metadata only)")
    print(
        "AGROLINES_MINIMAL_GRAPH="
        + json.dumps(
            [
                {
                    "path": row["path"],
                    "sha256": row["sha256"],
                    "group": row["group"],
                    "packages": row["packages"],
                    "imports": (row["build_input"] or {}).get("imports", []),
                    "source": (row["build_input"] or {}).get("source"),
                    "loaded_phases": row["loaded_phases"],
                }
                for row in result["files"]
            ]
        )
    )
    print("::endgroup::")
    for row in result["files"]:
        if not row["pinned_origin_confirmed"]:
            print("AGROLINES_PENDING_ORIGIN=" + json.dumps(row))
    print(
        "AGROLINES_MINIMAL_UNSIGNED="
        + json.dumps(
            [
                {
                    "path": r["path"],
                    "sha256": r["sha256"],
                    "group": r["group"],
                    "packages": r["packages"],
                    "loaded_phases": r["loaded_phases"],
                }
                for r in result["files"]
                if r["signature"]["status"] == "NotSigned"
            ]
        )
    )


if __name__ == "__main__":
    main()
