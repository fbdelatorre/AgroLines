"""Approved artwork provenance and verification of actual unpacked MSIX/PE icons."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

from distribution.icon import render

ROOT = Path(__file__).resolve().parent.parent
BRANDING = ROOT / "assets/branding"
MASTER_NAME = "AgroLines_Arte_Caixa_1080x1080.png"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def approved_source():
    originals = json.loads((BRANDING / "originals.json").read_text(encoding="utf-8"))
    for item in originals["files"]:
        if digest(BRANDING / item["name"]) != item["sha256"]:
            raise ValueError("Approved original artwork differs from recorded hash")
    return BRANDING / MASTER_NAME


def generate_assets(destination):
    source = approved_source()
    destination.mkdir()
    sizes = {"StoreLogo": 50, "Square44x44Logo": 44, "Square150x150Logo": 150}
    assets = {}
    for name, base in sizes.items():
        assets[f"{name}.png"] = base
        for scale in (100, 125, 150, 200, 400):
            assets[f"{name}.scale-{scale}.png"] = (base * scale + 50) // 100
    for size in (16, 24, 32, 48, 64, 96, 256):
        assets[f"Square44x44Logo.targetsize-{size}.png"] = size
        assets[f"Square44x44Logo.targetsize-{size}_altform-unplated.png"] = size
    for name, size in assets.items():
        if not render(source, size).save(str(destination / name), "PNG"):
            raise ValueError("Unable to generate Store assets")
    return {
        "source": MASTER_NAME,
        "source_sha256": digest(source),
        "assets": {
            name: {"size": size, "sha256": digest(destination / name)}
            for name, size in assets.items()
        },
    }


def ico_frames(path):
    content = Path(path).read_bytes()
    reserved, kind, count = struct.unpack_from("<HHH", content)
    if reserved or kind != 1 or not count:
        raise ValueError("Invalid ICO header")
    frames = []
    for index in range(count):
        entry = struct.unpack_from("<BBBBHHII", content, 6 + index * 16)
        size, offset = entry[-2:]
        frames.append(content[offset : offset + size])
    return frames


def verify_package(unpacked, staging_report, prepared):
    """Compare packaged bytes and PE RT_ICON resources, without installing MSIX."""
    import pefile

    source = approved_source()
    report = json.loads(Path(staging_report).read_text(encoding="utf-8"))
    branding = report["branding"]
    if branding["source_sha256"] != digest(source):
        raise ValueError("Staged artwork is not the approved original")
    for name, item in branding["assets"].items():
        if digest(Path(unpacked) / "Assets" / name) != item["sha256"]:
            raise ValueError("Unpacked Store icon differs from staged artwork")
    app = Path(unpacked) / "VFS/ProgramFilesX64/AgroLines"
    if digest(app / "_internal/assets/branding" / MASTER_NAME) != digest(source):
        raise ValueError("Packaged original differs from approved artwork")
    icon = Path(prepared) / "AgroLines.ico"
    if digest(app / "_internal/distribution/windows/AgroLines.ico") != digest(icon):
        raise ValueError("Runtime window/taskbar ICO differs from executable ICO")
    with pefile.PE(str(app / "AgroLinesPoC.exe")) as pe:
        embedded = []
        group_present = False
        for resource in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            group_present |= resource.id == 14  # RT_GROUP_ICON
            if resource.id == 3:  # RT_ICON: actual PNG frames, not a filename assertion
                for entry in resource.directory.entries:
                    for language in entry.directory.entries:
                        data = language.data.struct
                        embedded.append(pe.get_data(data.OffsetToData, data.Size))
        if not group_present or sorted(embedded) != sorted(ico_frames(icon)):
            raise ValueError("EXE embedded icons do not match the approved generated ICO")
    return {
        "source": MASTER_NAME,
        "source_sha256": digest(source),
        "store_assets_verified": len(branding["assets"]),
        "exe_icon_frames_verified": len(embedded),
        "runtime_ico_sha256": digest(icon),
        "unpacked_msix_verified": True,
        "installed_visual_validation": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unpacked", type=Path, required=True)
    parser.add_argument("--staging-report", type=Path, required=True)
    parser.add_argument("--prepared", type=Path, default=ROOT / "build/distribution")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = verify_package(args.unpacked, args.staging_report, args.prepared)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
