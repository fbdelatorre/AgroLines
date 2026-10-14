"""Inventory native files without importing blocked NumPy/Qt/GIS modules.

Hashes identify the inspected bytes; they are not signatures or proof of SAC acceptance.
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import struct
import sys
from datetime import UTC, datetime
from pathlib import Path

NATIVE_SUFFIXES = {".dll", ".pyd", ".exe", ".so", ".dylib"}


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binary_kind(path):
    with Path(path).open("rb") as source:
        header = source.read(64)
        if header.startswith(b"MZ") and len(header) >= 64:
            source.seek(struct.unpack_from("<I", header, 60)[0])
            pe = source.read(6)
            if pe[:4] == b"PE\0\0" and len(pe) == 6:
                machine = struct.unpack_from("<H", pe, 4)[0]
                return "PE", {0x8664: "x64", 0xAA64: "arm64", 0x14C: "x86"}.get(
                    machine, f"machine:{machine}"
                )
            return "invalid_PE", None
        if header.startswith(b"\x7fELF"):
            return "ELF", None
        return "other", None


def inventory(roots, distributions=None):
    distributions = list(
        importlib.metadata.distributions() if distributions is None else distributions
    )
    owners, packages, errors = {}, [], []
    for distribution in distributions:
        name, version = distribution.metadata["Name"], distribution.version
        packages.append({"name": name, "version": version})
        for entry in distribution.files or []:
            if Path(entry).suffix.lower() in NATIVE_SUFFIXES:
                path = str(Path(distribution.locate_file(entry)).absolute()).casefold()
                owners.setdefault(path, []).append({"name": name, "version": version})
    paths = set()
    resolved_roots = sorted({str(Path(root).resolve()) for root in roots})
    for root in resolved_roots:
        if not Path(root).is_dir():
            errors.append({"path": root, "error": "root_missing"})
            continue

        def on_error(error):
            errors.append({"path": error.filename, "error": type(error).__name__})

        for directory, directories, files in os.walk(root, onerror=on_error, followlinks=False):
            for name in list(directories):
                child = Path(directory) / name
                if child.is_symlink():
                    errors.append({"path": str(child), "error": "symlink_directory_not_scanned"})
                    directories.remove(name)
            for name in files:
                path = Path(directory) / name
                if path.suffix.lower() in NATIVE_SUFFIXES:
                    if path.is_symlink():
                        errors.append({"path": str(path), "error": "symlink_not_scanned"})
                    else:
                        paths.add(path.absolute())
    records = []
    for path in sorted(paths):
        try:
            kind, architecture = binary_kind(path)
            records.append(
                {
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "sha256": file_hash(path),
                    "format": kind,
                    "architecture": architecture,
                    "packages": owners.get(str(path).casefold(), []),
                }
            )
        except OSError as error:
            errors.append({"path": str(path), "error": type(error).__name__})
    return {
        "schema_version": 1,
        "generated_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "roots": resolved_roots,
        "packages": sorted(packages, key=lambda p: p["name"].casefold()),
        "files": records,
        "errors": errors,
        "inspection_complete": not errors and bool(records),
        "smart_app_control_compatibility_proven": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", help="Repeat for runtime and installer roots")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.root or [sys.prefix, sys.base_prefix])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Native inventory: {len(report['files'])} files; {len(report['errors'])} errors.")
    raise SystemExit(0 if report["inspection_complete"] else 1)


if __name__ == "__main__":
    main()
