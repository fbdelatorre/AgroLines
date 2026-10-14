"""Stage the complete PyInstaller payload; official Store identity is never substituted."""

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from distribution.build import version_tuple
from distribution.payload import verify

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "distribution/windows/msix"
FOUNDATION = "http://schemas.microsoft.com/appx/manifest/foundation/windows10"
NS = {"f": FOUNDATION}


def identity():
    return json.loads((CONFIG / "identity.json").read_text(encoding="utf-8"))


def validate_manifest(path):
    tree = ET.parse(path)
    package = tree.getroot()
    expected = identity()
    declared = package.find("f:Identity", NS)
    properties = package.find("f:Properties", NS)
    application = package.find("f:Applications/f:Application", NS)
    if (
        declared.attrib["Name"] != expected["name"]
        or declared.attrib["Publisher"] != expected["publisher"]
        or declared.attrib["ProcessorArchitecture"] != "x64"
        or properties.find("f:PublisherDisplayName", NS).text != expected["publisher_display_name"]
        or application.attrib["Id"] != expected["application_id"]
        or application.attrib["Executable"] != r"VFS\ProgramFilesX64\AgroLines\AgroLinesPoC.exe"
        or application.attrib["EntryPoint"] != "Windows.FullTrustApplication"
    ):
        raise ValueError("MSIX must retain the exact official Store identity and executable")
    parts = version_tuple(declared.attrib["Version"])
    if parts[0] == 0 or parts[3] != 0:
        raise ValueError("Store version must be nonzero and its fourth component must be zero")
    return tree


def generate_assets(destination):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer

    destination.mkdir()
    renderer = QSvgRenderer(str(ROOT / "distribution/windows/brand.svg"))
    if not renderer.isValid():
        raise ValueError("Invalid brand SVG")
    for name, size in (
        ("StoreLogo.png", 50),
        ("Square44x44Logo.png", 44),
        ("Square150x150Logo.png", 150),
    ):
        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        if not image.save(str(destination / name), "PNG"):
            raise ValueError("Unable to generate Store assets")


def stage(payload, output, version):
    payload, output = Path(payload).resolve(), Path(output).resolve()
    validate_manifest(CONFIG / "AppxManifest.xml")
    parts = version_tuple(version)
    if parts[3] != 0 or parts[0] == 0:
        raise ValueError("Store versions reserve the fourth component: use e.g. 1.0.0.0")
    data = json.loads((payload / "payload-manifest.json").read_text(encoding="utf-8"))
    if not verify(payload, data):
        raise ValueError("Payload hash verification failed before MSIX staging")
    executable = payload / "AgroLinesPoC.exe"
    if not executable.is_file() or executable.read_bytes()[:2] != b"MZ":
        raise ValueError("Expected Windows PyInstaller executable")
    metadata = json.loads((payload / "_internal/distribution/windows/metadata.json").read_text())
    if (
        metadata.get("store_identity") != identity()
        or metadata["version"] != version
        or metadata.get("offline_only") is not True
    ):
        raise ValueError("Build the Store payload with matching metadata/version first")
    if output == payload or output.is_relative_to(payload) or payload.is_relative_to(output):
        raise ValueError("MSIX staging must be separate from the payload")
    output.mkdir(parents=True, exist_ok=False)
    try:
        app = output / "VFS/ProgramFilesX64/AgroLines"
        shutil.copytree(payload, app)
        if not verify(app, data):
            raise ValueError("Copied payload differs from audited runtime")
        generate_assets(output / "Assets")
        # Preserve namespace prefixes, including prefixes used in IgnorableNamespaces.
        template = (CONFIG / "AppxManifest.xml").read_text(encoding="utf-8")
        template = template.replace('Version="1.0.0.0"', f'Version="{version}"', 1)
        (output / "AppxManifest.xml").write_text(template, encoding="utf-8")
        validate_manifest(output / "AppxManifest.xml")
    except Exception:
        shutil.rmtree(output)
        raise
    return {
        "identity": identity(),
        "version": version,
        "architecture": "x64",
        "signature": "unsigned-store-submission",
        "sac_approved": False,
        "installed_msix_validated": False,
        "files": len(data["files"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", default="1.0.0.0")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = stage(args.payload, args.output, args.version)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
