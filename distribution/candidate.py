"""Inspect the generated MSIX, correlate probes, and report limits without approval."""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from distribution.build import PRIVACY_FILES, ROOT
from distribution.msix import NS, identity, package_family_name

PREFIX = "VFS/ProgramFilesX64/AgroLines/"
COMPONENTS = {
    "python": "python312.dll",
    "sqlite": "_sqlite3.pyd",
    "numpy": "_multiarray_umath",
    "gdal": "gdal",
    "proj": "proj",
    "geos": "geos",
    "qt_webengine": "qt6webenginecore.dll",
    "qt_helper": "qtwebengineprocess.exe",
}


def inspect_package(path):
    official = identity()
    with ZipFile(path) as archive:
        names = archive.namelist()
        if "AppxSignature.p7x" in names:
            raise ValueError("Expected unsigned Store submission candidate")
        package = ET.fromstring(archive.read("AppxManifest.xml"))
        declared = package.find("f:Identity", NS).attrib
        if (
            declared["Name"] != official["name"]
            or declared["Publisher"] != official["publisher"]
            or declared["ProcessorArchitecture"] != "x64"
            or declared["Version"] != "1.0.0.0"
            or package_family_name(declared["Name"], declared["Publisher"])
            != official["package_family_name"]
            or package.find("f:Properties/f:PublisherDisplayName", NS).text
            != official["publisher_display_name"]
        ):
            raise ValueError("Archive identity/version does not match candidate")
        windows = package.find("f:Dependencies/f:TargetDeviceFamily", NS).attrib
        if windows != {
            "Name": "Windows.Desktop",
            "MinVersion": "10.0.22000.0",
            "MaxVersionTested": "10.0.26100.0",
        }:
            raise ValueError("Unexpected Windows target requirements")
        capabilities = [entry.attrib["Name"] for entry in package.find("f:Capabilities", NS)]
        if set(capabilities) != {"runFullTrust", "unvirtualizedResources"}:
            raise ValueError("Unexpected capabilities require separate review")
        payload = [name for name in names if name.startswith(PREFIX)]
        native = [name for name in payload if name.lower().endswith((".dll", ".pyd", ".exe"))]
        components = {}
        for key, token in COMPONENTS.items():
            paths = []
            for name in native:
                basename = Path(name).name.lower()
                matches = (
                    basename == token
                    if key not in {"numpy", "gdal", "proj", "geos"}
                    else token in basename
                    and basename.endswith(".pyd" if key == "numpy" else ".dll")
                )
                if matches:
                    paths.append(name)
            components[key] = paths
        if any(not paths for paths in components.values()):
            raise ValueError("Native component missing from MSIX")
        for suffix in (
            "/proj.db",
            "/icudtl.dat",
            "/qtwebengine_resources.pak",
            "/desktop/map_assets/map-offline.html",
            "/desktop/map_assets/leaflet.js",
            "/desktop/map_assets/leaflet.css",
            "/desktop/map_assets/map.js",
            "/desktop/map_assets/map.css",
        ):
            if not any(name.lower().endswith(suffix) for name in payload):
                raise ValueError("Required local resource missing: " + suffix)
        if not any("/translations/qtwebengine_locales/" in name.lower() for name in payload):
            raise ValueError("WebEngine locales missing")
        privacy_prefix = PREFIX + "_internal/desktop/privacy_assets/"
        policy_names = {
            name.removeprefix(privacy_prefix)
            for name in names
            if name.startswith(privacy_prefix) and not name.endswith("/")
        }
        if policy_names != set(PRIVACY_FILES):
            raise ValueError("Policy payload contains missing or internal documents")
        for name in PRIVACY_FILES:
            if (
                archive.read(privacy_prefix + name)
                != (ROOT / "docs/privacy/offline" / name).read_bytes()
            ):
                raise ValueError("Packaged policy differs from reviewed source")
    with Path(path).open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {
        "file": Path(path).name,
        "sha256": digest,
        "size_bytes": Path(path).stat().st_size,
        "identity": official,
        "version": declared["Version"],
        "architecture": "x64",
        "windows": windows,
        "capabilities": capabilities,
        "signature": "unsigned-store-submission",
        "components": components,
        "privacy_files": sorted(policy_names),
        "privacy_policy_approved": False,
        "installed_msix_validated": False,
        "sac_approved": False,
        "native_network_trace_validated": False,
        "automatic_store_publication": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("package", "runtime", "offline", "signatures", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--run-url", required=True)
    args = parser.parse_args()
    report = inspect_package(args.package)
    runtime, offline, signatures = (
        json.loads(path.read_text(encoding="utf-8-sig"))
        for path in (args.runtime, args.offline, args.signatures)
    )
    if not (
        runtime["frozen"]
        and runtime["checks_passed"]
        and runtime["payload_integrity_verified"]
        and runtime["qt_webengine_map_ready"]
        and offline["passed"]
        and offline["projects"]["backup_restored"]
    ):
        raise ValueError("Frozen runtime/offline probes incomplete")
    if (
        runtime["msix_validation_passed"]
        or offline["sac_approved"]
        or offline["native_network_trace_validated"]
    ):
        raise ValueError("Hosted extraction cannot claim installed/SAC approval")
    native_files = signatures["files"]
    if (
        not native_files
        or len(native_files) != signatures["inspected_pe_files"]
        or any(
            entry["status"] == "InspectionError" or not entry["integrity_matches"]
            for entry in native_files
        )
    ):
        raise ValueError("Native inventory inspection/integrity incomplete")
    report.update(
        source_commit=args.source_commit,
        run_url=args.run_url,
        runtime_versions=runtime["versions"],
        native_signatures={
            "inspected_pe_files": len(native_files),
            "statuses": dict(Counter(entry["status"] for entry in native_files)),
            "valid_chains": sum(bool(entry["chain_valid"]) for entry in native_files),
            "unverified_files": signatures["unverified_files"],
            "sac_approved": False,
        },
        offline_formats=offline["local_formats"],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = {key: value for key, value in report.items() if key != "components"}
    summary["component_counts"] = {key: len(paths) for key, paths in report["components"].items()}
    print("AGROLINES_CANDIDATE_EVIDENCE=" + json.dumps(summary))


if __name__ == "__main__":
    main()
