"""Attribute immutable native bytes to pinned inputs and correlate Windows observations."""

import argparse
import csv
import importlib.metadata
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path, PureWindowsPath

from distribution.payload import verify
from scripts.native_inventory import NATIVE_SUFFIXES, file_hash, inventory


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def classify(relative, origins):
    base = Path(relative).name.lower()
    names = {p["name"].lower() for p in origins}
    if relative == "AgroLinesPoC.exe":
        return "own", "AgroLines/PyInstaller bootloader"
    if "geos" in base:
        return "geos", "GEOS"
    if base.startswith("proj") and base.endswith(".dll"):
        return "proj", "PROJ"
    if "gdal" in base:
        return "gdal", "GDAL"
    if any(n.startswith(("pyside", "shiboken")) for n in names):
        return "qt", "Qt/PySide6/Shiboken"
    if "numpy" in names or "/numpy" in relative.lower():
        return "numpy", "OpenBLAS" if "openblas" in base else "NumPy/native runtime"
    if "pyproj" in names:
        return "proj", "pyproj bindings"
    if "fiona" in names:
        return "gdal", "Fiona/bundled dependency"
    if "shapely" in names:
        return "geos", "Shapely bindings"
    if any(n == "cpython" for n in names):
        return "python", "CPython/bundled runtime"
    return "other", "Other dependency/unconfirmed origin"


def input_index():
    index = defaultdict(list)
    for dist in importlib.metadata.distributions():
        for entry in dist.files or []:
            source = Path(dist.locate_file(entry))
            if source.suffix.lower() in NATIVE_SUFFIXES and source.is_file():
                index[file_hash(source)].append(
                    {
                        "name": dist.metadata["Name"],
                        "version": dist.version,
                        "input_relative": str(entry),
                    }
                )
    base = Path(sys.base_prefix)
    for parent in (base, base / "DLLs"):
        for source in parent.glob("*"):
            if source.is_file() and source.suffix.lower() in NATIVE_SUFFIXES:
                index[file_hash(source)].append(
                    {
                        "name": "CPython",
                        "version": sys.version.split()[0],
                        "input_relative": source.relative_to(base).as_posix(),
                    }
                )
    return index


def prepare(payload, output):
    payload = Path(payload).resolve()
    if not verify(payload, read_json(payload / "payload-manifest.json")):
        raise ValueError("Original frozen payload integrity failed")
    data = inventory([payload], distributions=[])
    if not data["inspection_complete"]:
        raise ValueError("Native inspection incomplete")
    index = input_index()
    for item in data["files"]:
        item["relative_path"] = Path(item["path"]).relative_to(payload).as_posix()
        item["packages"] = index.get(item["sha256"], [])
        item["group"], item["library"] = classify(item["relative_path"], item["packages"])
        item["origin_basis"] = (
            "exact_sha256_pinned_input"
            if item["packages"]
            else "entrypoint_manifest"
            if item["group"] == "own"
            else "unconfirmed_path_classification"
        )
    Path(output).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def reason(signature, tool):
    if signature["status"] == "NotSigned":
        return "No Authenticode signature; no signer chain to validate"
    flags = signature["chain_status"]
    if tool["exit_code"] == 0 and signature["status"] == "Valid":
        if not signature["chain_valid"]:
            return (
                "Windows Authenticode accepted; generic current-time chain differs: "
                + ", ".join(flags)
                + "; do not infer SAC rejection"
            )
        return "Authenticode and generic chain accepted in this runner; SAC unproven"
    return (
        "Authenticode failed/inconclusive; SignTool="
        + str(tool["exit_code"])
        + "; chain="
        + ", ".join(flags)
        + "; "
        + str(
            signature.get("status_message")
            or signature.get("inspection_error")
            or "See raw SignTool output"
        )
    )


def correlate(output, native, signatures, tools, loads, baseline, notices, package_sha):
    native, signatures, tools, loads, baseline = map(
        read_json, (native, signatures, tools, loads, baseline)
    )
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    by_path = {item["path"].casefold(): item for item in signatures["files"]}
    by_tool = {item["path"].casefold(): item for item in tools["files"]}
    old_root = PureWindowsPath(baseline["roots"][0])
    old = {
        PureWindowsPath(item["path"]).relative_to(old_root).as_posix(): item
        for item in baseline["files"]
    }
    observed = defaultdict(list)
    for phase in loads["phases"]:
        for item in phase["modules"]:
            if item.get("payload_relative"):
                observed[item["payload_relative"].casefold()].append(
                    {
                        "phase": phase["name"],
                        "process": item["process"],
                        "first_observed_ms": item["first_observed_ms"],
                    }
                )
    records = []
    for item in native["files"]:
        relative = item["relative_path"]
        if relative not in old or old[relative]["sha256"] != item["sha256"]:
            raise ValueError("Native bytes differ from original 453-file inventory")
        signature, tool = by_path[item["path"].casefold()], by_tool[item["path"].casefold()]
        if not signature["integrity_matches"] or not tool["integrity_matches"]:
            raise ValueError("Native file changed during audit")
        records.append(
            {
                **item,
                "baseline_signature": {
                    key: old[relative][key] for key in ("status", "chain_valid", "chain_status")
                },
                "authenticode": signature,
                "signtool": tool,
                "reason": reason(signature, tool),
                "loaded_observations": observed.get(relative.casefold(), []),
                "not_observed_is_not_unused": True,
            }
        )
    if len(records) != len(old):
        raise ValueError("Original inventory count mismatch")
    licenses = []
    for path in sorted(Path(notices).rglob("*")):
        if path.is_file():
            licenses.append(
                {
                    "path": path.relative_to(notices).as_posix(),
                    "sha256": file_hash(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    groups = {}
    for group in sorted({item["group"] for item in records}):
        subset = [item for item in records if item["group"] == group]
        groups[group] = {
            "files": len(subset),
            "unsigned": sum(r["authenticode"]["status"] == "NotSigned" for r in subset),
            "current_chain_false": sum(not r["authenticode"]["chain_valid"] for r in subset),
            "signtool_accepted": sum(r["signtool"]["exit_code"] == 0 for r in subset),
            "loaded": sum(bool(r["loaded_observations"]) for r in subset),
            "origin_unconfirmed": sum(
                r["origin_basis"] == "unconfirmed_path_classification" for r in subset
            ),
        }
    summary = {
        "package_sha256": package_sha,
        "files": len(records),
        "groups": groups,
        "chain_flags": dict(
            Counter(flag for r in records for flag in r["authenticode"]["chain_status"])
        ),
        "signtool_exit_codes": dict(Counter(str(r["signtool"]["exit_code"]) for r in records)),
        "observation_errors": loads["errors"],
        "sac_approved": False,
        "installed_msix_validated": False,
        "license_review_complete": False,
    }
    (output / "inventory.json").write_text(
        json.dumps({"summary": summary, "files": records, "licenses": licenses}, indent=2),
        encoding="utf-8",
    )
    fields = [
        "relative_path",
        "group",
        "library",
        "origin_basis",
        "origins",
        "sha256",
        "authenticode",
        "signer",
        "current_chain",
        "chain_flags",
        "signtool_exit",
        "observed_phases",
        "reason",
    ]
    with (output / "inventory.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for r in records:
            sig = r["authenticode"]
            writer.writerow(
                {
                    "relative_path": r["relative_path"],
                    "group": r["group"],
                    "library": r["library"],
                    "origin_basis": r["origin_basis"],
                    "origins": ";".join(p["name"] + "==" + p["version"] for p in r["packages"]),
                    "sha256": r["sha256"],
                    "authenticode": sig["status"],
                    "signer": sig["signer"],
                    "current_chain": sig["chain_valid"],
                    "chain_flags": ";".join(sig["chain_status"]),
                    "signtool_exit": r["signtool"]["exit_code"],
                    "observed_phases": ";".join(
                        sorted({v["phase"] for v in r["loaded_observations"]})
                    ),
                    "reason": r["reason"],
                }
            )
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("AGROLINES_NATIVE_AUDIT=" + json.dumps(summary))
    for r in records:
        print(
            "AGROLINES_NATIVE_FILE="
            + json.dumps(
                {
                    "path": r["relative_path"],
                    "group": r["group"],
                    "library": r["library"],
                    "origin": r["origin_basis"],
                    "packages": r["packages"],
                    "status": r["authenticode"]["status"],
                    "chain": r["authenticode"]["chain_status"],
                    "signtool": r["signtool"]["exit_code"],
                    "loaded": bool(r["loaded_observations"]),
                    "reason": r["reason"],
                }
            )
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--payload", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    for field in ("native", "signatures", "tools", "loads", "baseline", "notices", "package-sha"):
        parser.add_argument("--" + field)
    args = parser.parse_args()
    if args.prepare:
        prepare(args.payload, args.output)
    else:
        correlate(
            args.output,
            args.native,
            args.signatures,
            args.tools,
            args.loads,
            args.baseline,
            args.notices,
            args.package_sha,
        )


if __name__ == "__main__":
    main()
