"""Prepare exact metadata/version/icon then build a Windows onedir PoC."""

import argparse
import importlib.metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path

from distribution.icon import generate

ROOT = Path(__file__).resolve().parent.parent


def version_tuple(value):
    pieces = value.split(".")
    if len(pieces) != 4 or any(not p.isdigit() or not 0 <= int(p) <= 65535 for p in pieces):
        raise ValueError("Version must have four numeric components in [0,65535]")
    return tuple(int(p) for p in pieces)


def prepare(output, version, manufacturer):
    parts = version_tuple(version)
    if not manufacturer or len(manufacturer) > 120 or any(c in manufacturer for c in '\r\n"'):
        raise ValueError("Manufacturer must be a plain single-line name")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((ROOT / "distribution/windows/metadata.json").read_text())
    metadata.update(version=version, manufacturer=manufacturer)
    (output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )
    generate(ROOT / "distribution/windows/brand.svg", output / "AgroLines.ico")
    fields = {
        "CompanyName": manufacturer,
        "FileDescription": metadata["name"],
        "FileVersion": version,
        "InternalName": "AgroLinesPoC",
        "OriginalFilename": "AgroLinesPoC.exe",
        "ProductName": metadata["name"],
        "ProductVersion": version,
    }
    strings = ",".join(f"StringStruct({k!r}, {v!r})" for k, v in fields.items())
    info = (
        f"VSVersionInfo(ffi=FixedFileInfo(filevers={parts!r},prodvers={parts!r},"
        "mask=0x3f,flags=0,OS=0x40004,fileType=1,subtype=0,date=(0,0)),"
        f"kids=[StringFileInfo([StringTable('041604b0',[{strings}])]),"
        "VarFileInfo([VarStruct('Translation',[1046,1200])])])"
    )
    (output / "version.txt").write_text(info, encoding="utf-8")
    return metadata


def collect_notices(payload):
    notices = Path(payload) / "third-party-notices"
    notices.mkdir(parents=True, exist_ok=True)
    packages = []
    for package in importlib.metadata.distributions():
        name = package.metadata["Name"]
        packages.append(
            {
                "name": name,
                "version": package.version,
                "license": package.metadata.get("License-Expression")
                or package.metadata.get("License", "not declared"),
            }
        )
        for entry in package.files or []:
            if "license" not in str(entry).casefold() and "copyright" not in str(entry).casefold():
                continue
            source = Path(package.locate_file(entry))
            if source.is_file():
                safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(entry))
                target = notices / name / safe
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    (notices / "packages.json").write_text(json.dumps(packages, indent=2), encoding="utf-8")
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copyfile(python_license, notices / "Python-LICENSE.txt")
    (notices / "README.txt").write_text(
        "Dependency notices collected for internal PoC. Commercial redistribution "
        "requires review of Qt/Chromium notices, LGPL/source obligations, "
        "runtime redistribution rights and the AgroLines license. Not legal approval.\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="0.1.0.1")
    parser.add_argument("--manufacturer", default="AgroLines - identidade juridica pendente")
    args = parser.parse_args()
    if sys.platform != "win32":
        raise SystemExit("Windows build requires a Windows builder")
    prepare(ROOT / "build/distribution", args.version, args.manufacturer)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            str(ROOT / "distribution/windows/poc.spec"),
        ],
        check=True,
        cwd=ROOT,
    )
    collect_notices(ROOT / "dist/AgroLinesPoC")


if __name__ == "__main__":
    main()
