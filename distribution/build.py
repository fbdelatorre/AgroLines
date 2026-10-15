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


def privacy_assets(standalone=False, commercial=False):
    """Ship policy copies only, never internal audits or operational records."""
    folder = "docs/legal/standalone" if standalone else "docs/privacy/offline"
    if commercial:
        folder = "docs/legal/commercial"
    return [(str(ROOT / folder / name), "desktop/privacy_assets") for name in PRIVACY_FILES]


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


def prepare(output, version, manufacturer, store=False, standalone=False, commercial=False):
    if commercial and not standalone:
        raise ValueError("Commercial profile requires standalone layout")
    if store and standalone:
        raise ValueError("Choose one distribution profile")
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
    if standalone:
        metadata.update(
            name="AgroLines Experimental",
            distribution_channel="commercial-standalone" if commercial else "standalone-offline",
            offline_only=True,
            executable="AgroLines.exe",
            lgpl_python_external=True,
            agricultural_offline=True,
            licensing_online=commercial,
        )
    if commercial:
        metadata["offline_only"] = False
    (output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )
    generate(approved_source(), output / "AgroLines.ico")
    fields = {
        "CompanyName": manufacturer,
        "FileDescription": metadata["name"],
        "FileVersion": version,
        "InternalName": "AgroLines" if standalone else "AgroLinesPoC",
        "OriginalFilename": metadata.get("executable", "AgroLinesPoC.exe"),
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
    profile = parser.add_mutually_exclusive_group()
    profile.add_argument("--store", action="store_true")
    profile.add_argument("--standalone", action="store_true")
    profile.add_argument("--commercial", action="store_true")
    parser.add_argument("--license-origin")
    parser.add_argument("--public-keys", type=Path)
    parser.add_argument("--experimental-licensing", action="store_true")
    args = parser.parse_args()
    if args.commercial:
        if not args.license_origin or not args.public_keys:
            parser.error("Commercial build requires explicit HTTPS origin and public keys")
        from distribution.commercial_profile import prepare_trust

        trust = ROOT / "build/distribution/_agrolines_license_settings.py"
        trust.parent.mkdir(parents=True, exist_ok=True)
        prepare_trust(trust, args.license_origin, args.public_keys, args.experimental_licensing)
        args.standalone = True
    if sys.platform != "win32":
        raise SystemExit("Windows build requires a Windows builder")
    prepare(
        ROOT / "build/distribution",
        args.version,
        args.manufacturer,
        store=args.store,
        standalone=args.standalone,
        commercial=args.commercial,
    )
    offline = args.store or args.standalone
    builder_environment = store_builder_environment() if offline else os.environ.copy()
    if offline:
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
    payload = ROOT / ("dist/AgroLines" if args.standalone else "dist/AgroLinesPoC")
    if args.standalone:
        from distribution.libaec_build import stage as stage_codec

        stage_codec(payload)
        from distribution.geos_delivery import stage as stage_geos

        stage_geos(payload)
    collect_notices(payload, ROOT / "evidence/qt-minimal/build-inputs.json" if offline else None)
    if args.store:
        shutil.copyfile(
            ROOT / "distribution/windows/signing/native-policy.json",
            ROOT / "dist/AgroLinesPoC/native-signing-policy.json",
        )
    if args.standalone:
        from distribution.standalone_build import prepare_materials

        prepare_materials(payload)


if __name__ == "__main__":
    main()
