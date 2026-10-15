"""Builder measurements only, never distribution or SAC approval."""

import argparse
import json
from pathlib import Path

from scripts.native_inventory import file_hash


def report(payload, installer, commit):
    root, setup = Path(payload), Path(installer)
    files = [p for p in root.rglob("*") if p.is_file()]
    return {
        "source_commit": commit,
        "installer": setup.name,
        "installer_bytes": setup.stat().st_size,
        "installer_sha256": file_hash(setup),
        "onedir_bytes": sum(p.stat().st_size for p in files),
        "file_count": len(files),
        "dll_count": sum(p.suffix.lower() == ".dll" for p in files),
        "pyd_count": sum(p.suffix.lower() == ".pyd" for p in files),
        "exe_count": sum(p.suffix.lower() == ".exe" for p in files),
        "payload_manifest_sha256": file_hash(root / "payload-manifest.json"),
        "signed": False,
        "commercial_approved": False,
        "sac_approved": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True)
    parser.add_argument("--installer", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = report(args.payload, args.installer, args.commit)
    args.output.write_text(json.dumps(value, indent=2), encoding="utf-8")
    print("AGROLINES_FUNCTIONAL_ARTIFACT=" + json.dumps(value))
