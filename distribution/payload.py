"""Payload-only inventory and integrity manifest, never a substitute for signatures."""

import argparse
import json
from pathlib import Path

from scripts.native_inventory import file_hash, inventory


def manifest(root):
    root = Path(root).resolve()
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Payload cannot contain symlinks")
        if path.is_file() and path.name != "payload-manifest.json":
            files.append({"path": path.relative_to(root).as_posix(), "sha256": file_hash(path)})
    if not files:
        raise ValueError("Empty payload")
    return {"schema_version": 1, "files": files, "approved_for_distribution": False}


def verify(root, data):
    root = Path(root).resolve()
    if data.get("schema_version") != 1 or not data.get("files"):
        return False
    expected = set()
    for item in data["files"]:
        path = root / item["path"]
        if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
            return False
        if item["path"] in expected or file_hash(path) != item["sha256"]:
            return False
        expected.add(item["path"])
    entries = list(root.rglob("*"))
    if any(p.is_symlink() for p in entries):
        return False
    actual = {p.relative_to(root).as_posix() for p in entries if p.is_file()}
    return actual - {"payload-manifest.json"} == expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", action="store_true")
    args = parser.parse_args()
    data = manifest(args.root) if args.manifest else inventory([args.root], distributions=[])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if not args.manifest and not data["inspection_complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
