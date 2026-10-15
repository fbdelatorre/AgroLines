"""Prepare exact metadata/version/icon then build a Windows onedir PoC."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from distribution.branding import approved_source
from distribution.icon import generate

ROOT = Path(__file__).resolve().parent.parent
PRIVACY_FILES = ("politica-privacidade.html", "politica-privacidade.md", "politica-privacidade.txt")


def privacy_assets():
    """Ship policy copies only, never internal audits or operational records."""
    return [
        (str(ROOT / "docs/privacy/offline" / name), "desktop/privacy_assets")
        for name in PRIVACY_FILES
    ]


def store_builder_environment():
    """Build from pinned Python/wheels and Windows, never unrelated JDK/MySQL/GIS on PATH."""
    environment = os.environ.copy()
    windows = Path(environment["WINDIR"]).resolve()
    paths = [
        Path(sys.prefix),
        Path(sys.prefix) / "Scripts",
        Path(sys.base_prefix),
        Path(sys.base_prefix) / "DLLs",
        windows / "System32",
        windows,
    ]
    environment["PATH"] = os.pathsep.join(str(p.resolve()) for p in paths if p.is_dir())
    for key in (
        "PYTHONHOME",
        "PYTHONPATH",
        "GDAL_DATA",
        "PROJ_LIB",
        "PROJ_DATA",
        "QT_PLUGIN_PATH",
        "QTWEBENGINEPROCESS_PATH",
        "QTWEBENGINE_RESOURCES_PATH",
        "QTWEBENGINE_LOCALES_PATH",
        "QML2_IMPORT_PATH",
        "QML_IMPORT_PATH",
    ):
        environment.pop(key, None)
    return environment


def version_tuple(value):
    pieces = value.split(".")
    if len(pieces) != 4 or any(not p.isdigit() or not 0 <= int(p) <= 65535 for p in pieces):
        raise ValueError("Version must have four numeric components in [0,65535]")
    return tuple(int(p) for p in pieces)


def prepare(output, version, manufacturer, store=False):
    parts = version_tuple(version)
    if not manufacturer or len(manufacturer) > 120 or any(c in manufacturer for c in '\r\n"'):
        raise ValueError("Manufacturer must be a plain single-line name")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((ROOT / "distribution/windows/metadata.json").read_text())
    metadata.update(version=version, manufacturer=manufacturer)
    if store:
        from distribution.msix import identity

        official = identity()
        if manufacturer != official["publisher_display_name"] or parts[3] != 0 or parts[0] == 0:
            raise ValueError(
                "Store build requires official publisher display name and revision zero"
            )
        metadata.update(
            name="AgroLines",
            distribution_channel="microsoft-store",
            store_identity=official,
            offline_only=True,
        )
    (output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )
    generate(approved_source(), output / "AgroLines.ico")
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


def collect_notices(payload, analysis_path=None):
    notices = Path(payload) / "third-party-notices"
    from distribution.notices import collect

    modules = json.loads(Path(analysis_path).read_text())["python_modules"] if analysis_path else []
    collect(payload, modules)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copyfile(python_license, notices / "Python-LICENSE.txt")
    supplement = ROOT / "distribution/windows/third-party"
    if supplement.is_dir():
        shutil.copytree(supplement, notices / "reviewed-texts", dirs_exist_ok=True)
    (notices / "README.txt").write_text(
        "Dependency notices collected for internal PoC. Commercial redistribution "
        "requires review of Qt/Chromium notices, LGPL/source obligations, "
        "runtime redistribution rights and the AgroLines license. Not legal approval.\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="0.1.0.1")
    parser.add_argument("--manufacturer", default="Delatorre Corporation")
    parser.add_argument("--store", action="store_true")
    args = parser.parse_args()
    if sys.platform != "win32":
        raise SystemExit("Windows build requires a Windows builder")
    prepare(ROOT / "build/distribution", args.version, args.manufacturer, store=args.store)
    builder_environment = store_builder_environment() if args.store else os.environ.copy()
    if args.store:
        report = ROOT / "evidence/qt-minimal/builder-environment.json"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(
                {
                    "external_tools_path_inherited": False,
                    "path": builder_environment["PATH"].split(os.pathsep),
                    "source_date_epoch": builder_environment.get("SOURCE_DATE_EPOCH"),
                    "python_hash_seed": builder_environment.get("PYTHONHASHSEED"),
                    "scope": (
                        "Isolated PyInstaller child environment; "
                        "no Windows security setting changed"
                    ),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
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
        env=builder_environment,
    )
    collect_notices(
        ROOT / "dist/AgroLinesPoC",
        ROOT / "evidence/qt-minimal/build-inputs.json" if args.store else None,
    )
    if args.store:
        shutil.copyfile(
            ROOT / "distribution/windows/signing/native-policy.json",
            ROOT / "dist/AgroLinesPoC/native-signing-policy.json",
        )


if __name__ == "__main__":
    main()
