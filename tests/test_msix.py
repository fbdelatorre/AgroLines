import json
import sys

import pytest
from PySide6.QtGui import QImage

from distribution.build import prepare
from distribution.msix import CONFIG, NS, identity, stage, validate_manifest
from distribution.package_runtime import package_evidence
from distribution.payload import manifest, verify

OFFICIAL = {
    "name": "DelatorreCOrporation.AgroLines",
    "publisher": "CN=43189595-B928-4D57-90A4-24300E4D4976",
    "publisher_display_name": "Delatorre COrporation",
    "store_id": "9NRDJ3ZTM978",
    "package_family_name": "DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg",
    "url": "https://apps.microsoft.com/detail/9NRDJ3ZTM978",
    "application_id": "AgroLines",
}


@pytest.fixture
def payload(tmp_path):
    root = tmp_path / "payload"
    metadata_path = root / "_internal/distribution/windows"
    prepare(metadata_path, "1.0.0.0", OFFICIAL["publisher_display_name"], store=True)
    (root / "AgroLinesPoC.exe").write_bytes(b"MZsynthetic-integrity-test-only")
    (root / "_internal/native.pyd").write_bytes(b"native fixture, not executable")
    (root / "payload-manifest.json").write_text(json.dumps(manifest(root)))
    return root


def test_exact_case_sensitive_partner_center_identity():
    assert identity() == OFFICIAL
    tree = validate_manifest(CONFIG / "AppxManifest.xml")
    assert tree.getroot().find("f:Identity", NS).attrib["Version"] == "1.0.0.0"
    capabilities = [element.attrib["Name"] for element in tree.getroot().find("f:Capabilities", NS)]
    assert set(capabilities) == {"runFullTrust", "unvirtualizedResources"}
    assert "$(KnownFolder:LocalAppData)\\AgroLines" in (CONFIG / "AppxManifest.xml").read_text()


def test_stage_complete_payload_assets_and_roundtrip_hashes(payload, tmp_path):
    output = tmp_path / "stage"
    result = stage(payload, output, "1.0.0.0")
    assert not result["installed_msix_validated"] and not result["sac_approved"]
    assert verify(
        output / "VFS/ProgramFilesX64/AgroLines",
        json.loads((payload / "payload-manifest.json").read_text()),
    )
    for name, size in (
        ("StoreLogo.png", 50),
        ("Square44x44Logo.png", 44),
        ("Square150x150Logo.png", 150),
    ):
        image = QImage(str(output / "Assets" / name))
        assert not image.isNull() and image.width() == image.height() == size
    with pytest.raises(FileExistsError):
        stage(payload, output, "1.0.0.0")


@pytest.mark.parametrize("version", ["0.1.0.0", "1.0.0.1", "1.0.0", "1.0.65536.0"])
def test_reject_store_version_rules(payload, tmp_path, version):
    with pytest.raises(ValueError):
        stage(payload, tmp_path / "stage", version)


def test_reject_changed_publisher_and_tampered_runtime(payload, tmp_path):
    candidate = tmp_path / "AppxManifest.xml"
    candidate.write_text(
        (CONFIG / "AppxManifest.xml")
        .read_text()
        .replace(OFFICIAL["publisher"], "CN=another-identity")
    )
    with pytest.raises(ValueError, match="official Store identity"):
        validate_manifest(candidate)
    (payload / "_internal/native.pyd").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash verification"):
        stage(payload, tmp_path / "stage", "1.0.0.0")


def test_store_metadata_retains_official_display_name(tmp_path):
    metadata = prepare(
        tmp_path / "build", "1.0.0.0", OFFICIAL["publisher_display_name"], store=True
    )
    assert metadata["store_identity"] == OFFICIAL and metadata["name"] == "AgroLines"
    with pytest.raises(ValueError):
        prepare(tmp_path / "other", "1.0.0.0", "Delatorre Corporation", store=True)


def test_unpacked_process_never_attests_official_msix_installation():
    result = package_evidence()
    assert not result["packaged"] and not result["official_identity_matches"]
    assert sys.platform != "win32" or result["errors"] == []


def test_fixture_reopen_survives_package_version_changes(tmp_path):
    from PySide6.QtWidgets import QApplication

    from distribution.offline_checks import run_offline_checks

    app = QApplication.instance() or QApplication([])
    first = run_offline_checks(tmp_path)
    second = run_offline_checks(tmp_path)
    assert first["project_sha256"] == second["project_sha256"]
    assert second["existing_project_preserved"] and second["network_calls_denied"]
    app.processEvents()


def test_project_default_is_outside_installation_and_package_cache(tmp_path, monkeypatch):
    from desktop.storage import project_directory

    monkeypatch.setattr("desktop.storage.local_app_data", lambda: tmp_path)
    assert project_directory() == tmp_path / "AgroLines/Projects"
    assert "WindowsApps" not in project_directory().parts
    assert "Packages" not in project_directory().parts
