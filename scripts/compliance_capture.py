"""Read the fixed reference MSIX without installing, executing or changing it."""

import argparse
import base64
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

REFERENCE_SHA = "75fe75bd8d7097b826d46c4cd50576162f99aede3eb2db9def34d21a3b25ac90"
PREFIX = "VFS/ProgramFilesX64/AgroLines/"


def capture(package, evidence, output):
    package, evidence, output = Path(package), Path(evidence), Path(output)
    digest = hashlib.file_digest(package.open("rb"), "sha256").hexdigest()
    if digest != REFERENCE_SHA:
        raise ValueError("Immutable reference MSIX mismatch")
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entry")
        for name in names:
            parts = PurePosixPath(name).parts
            if name.startswith("/") or ".." in parts or "\\" in name:
                raise ValueError("Unsafe ZIP path")
        manifest = json.loads(archive.read(PREFIX + "payload-manifest.json"))
        expected = {r["path"]: r["sha256"] for r in manifest["files"]}
        actual = {
            name.removeprefix(PREFIX)
            for name in names
            if name.startswith(PREFIX) and not name.endswith("/")
        } - {"payload-manifest.json"}
        if actual != set(expected):
            raise ValueError("Payload coverage mismatch")
        records = []
        for path in sorted(actual):
            raw = archive.read(PREFIX + path)
            sha = hashlib.sha256(raw).hexdigest()
            if sha != expected[path]:
                raise ValueError("Payload hash mismatch: " + path)
            records.append({"path": path, "sha256": sha, "size_bytes": len(raw)})
            # Only legal documents are copied. No application source, bytecode or binaries.
            if path.startswith("third-party-notices/"):
                target = output / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                print(
                    "AGROLINES_COMPLIANCE_NOTICE="
                    + json.dumps(
                        {
                            "path": path,
                            "sha256": sha,
                            "base64": base64.b64encode(raw).decode("ascii"),
                        }
                    )
                )
        reports = {
            "reference": {"msix_sha256": digest, "size_bytes": package.stat().st_size},
            "payload": records,
            "native": json.loads((evidence / "qt-minimal/native-current.json").read_text()),
            "analysis": json.loads((evidence / "qt-minimal/build-inputs.json").read_text()),
        }
        for key, value in reports.items():
            (output / (key + ".json")).write_text(json.dumps(value, indent=2), encoding="utf-8")
            if key == "native":
                for row in value["files"]:
                    print("AGROLINES_COMPLIANCE_NATIVE=" + json.dumps(row))
            elif key == "payload":
                for row in value:
                    print("AGROLINES_COMPLIANCE_PAYLOAD=" + json.dumps(row))
            else:
                print("AGROLINES_COMPLIANCE_" + key.upper() + "=" + json.dumps(value))
    if hashlib.file_digest(package.open("rb"), "sha256").hexdigest() != digest:
        raise ValueError("Reference changed")
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    capture(args.package, args.evidence, args.output)


if __name__ == "__main__":
    main()
