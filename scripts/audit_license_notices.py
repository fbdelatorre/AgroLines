"""Read notices from the immutable candidate; metadata is evidence, not legal approval."""

import argparse
import json
import re
import shutil
from pathlib import Path

from scripts.native_inventory import file_hash


def inspect(notices, output):
    notices, output = Path(notices), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    packages = json.loads((notices / "packages.json").read_text(encoding="utf-8"))
    files = []
    for path in sorted(notices.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(notices).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        evidence = {
            "path": relative,
            "sha256": file_hash(path),
            "size_bytes": path.stat().st_size,
            "spdx": sorted(set(re.findall(r"SPDX-License-Identifier:\s*([^\r\n]+)", text))),
            "lgpl_mentions": len(re.findall(r"LGPL|Lesser General Public License", text)),
            "gpl_mentions": len(re.findall(r"GNU GENERAL PUBLIC LICENSE|GPL-[23]", text)),
            "excerpt": text[:1800],
        }
        files.append(evidence)
        destination = output / "original-notices" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        print("AGROLINES_LICENSE_FILE=" + json.dumps(evidence))
    for package in packages:
        print("AGROLINES_LICENSE_PACKAGE=" + json.dumps(package))
    report = {
        "packages": packages,
        "files": files,
        "metadata_scope": "Original builder environment; presence here is not proof of runtime use",
        "complete_source_offer_or_relinking_verified": False,
        "legal_compliance_approved": False,
        "limitations": [
            "Collector matches license/copyright filenames, not every COPYING/NOTICE file",
            "Metadata cannot license all vendored DLLs or replace full-text review",
            "These are original package notices; no license text is generated or adopted",
        ],
    }
    (output / "notices-evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notices", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inspect(args.notices, args.output)


if __name__ == "__main__":
    main()
