"""Inspect immutable PR18 dependencies in a disposable copy. SPDX-License-Identifier: 0BSD."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    subprocess.run(
        ["pwsh", "-File", str(REPO / "distribution/windows/standalone/Assert-Laboratory.ps1")],
        check=True,
    )
    from distribution.payload import verify

    manifest = json.loads((args.payload / "payload-manifest.json").read_text())
    if not verify(args.payload, manifest) or args.work.exists():
        raise ValueError("Verified input and fresh laboratory required")
    copy = args.work / "app"
    evidence = args.work / "evidence"
    evidence.mkdir(parents=True)
    shutil.copytree(args.payload, copy)
    with (copy / "_internal/PySide6/__init__.py").open("a", encoding="utf-8") as output:
        output.write("\n" + (Path(__file__).parent / "hook.py").read_text())
    environment = os.environ.copy()
    environment["AGROLINES_LICENSE_PROBE"] = str(evidence.resolve())
    subprocess.run(
        [
            "pwsh",
            "-File",
            str(Path(__file__).parent / "Run-Probe.ps1"),
            "-Executable",
            str((copy / "AgroLines.exe").resolve()),
            "-Report",
            str((evidence / "offline.json").resolve()),
        ],
        check=True,
        env=environment,
        cwd=REPO,
    )
    report = json.loads((evidence / "configuration.json").read_text())
    if report["errors"]:
        raise ValueError("Incomplete license configuration probe: " + str(report))
    if not verify(args.payload, manifest):
        raise ValueError("Original modified")
    report["own_exe_sha256"] = hashlib.sha256((copy / "AgroLines.exe").read_bytes()).hexdigest()
    print("AGROLINES_LICENSE_CONFIGURATION=" + json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
