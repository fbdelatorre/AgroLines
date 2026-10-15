"""Profile and real archive gates; fixtures contain no executable native code."""

import json
from pathlib import Path

import pytest

from distribution.build import prepare
from distribution.msix import identity
from distribution.standalone_build import inspect_layout, validate_installer_input

OWN = {"core.local_projects", "desktop.local_projects", "distribution.poc"}


def test_standalone_is_offline_and_independent_from_store(tmp_path):
    data = prepare(tmp_path / "standalone", "1.0.0.1", "Delatorre Corporation", standalone=True)
    assert data["offline_only"] and data["lgpl_python_external"]
    assert data["distribution_channel"] == "standalone-offline"
    assert data["executable"] == "AgroLines.exe" and "store_identity" not in data
    assert not data["approved_for_distribution"]
    store = prepare(tmp_path / "store", "1.0.0.0", identity()["publisher_display_name"], store=True)
    assert store["store_identity"] == identity() and store["offline_only"]
    assert "lgpl_python_external" not in store  # Existing MSIX contract is preserved.
    with pytest.raises(ValueError, match="one distribution"):
        prepare(
            tmp_path / "invalid", "1.0.0.1", "Delatorre Corporation", store=True, standalone=True
        )


@pytest.fixture
def layout(tmp_path):
    metadata = tmp_path / "_internal/distribution/windows"
    metadata.mkdir(parents=True)
    (metadata / "metadata.json").write_text(
        json.dumps(
            {
                "distribution_channel": "standalone-offline",
                "offline_only": True,
                "version": "1.0.0.1",
                "manufacturer": "Delatorre Corporation",
            }
        )
    )
    for name in (
        "AgroLines.exe",
        "_internal/python312.dll",
        "_internal/PySide6/QtCore.pyd",
        "_internal/PySide6/Qt6Core.dll",
        "_internal/PySide6/Qt6WebEngineCore.dll",
        "_internal/PySide6/QtWebEngineProcess.exe",
        "_internal/PySide6/plugins/platforms/qwindows.dll",
        "_internal/PySide6/__init__.py",
        "_internal/shiboken6/__init__.py",
        "_internal/desktop/map_assets/map-offline.html",
        "_internal/desktop/map_assets/leaflet.js",
        "_internal/desktop/map_assets/leaflet.css",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("inert layout fixture")
    return tmp_path


def test_external_bindings_without_embedded_shadow_or_own_source(layout):
    report = inspect_layout(layout, OWN)
    assert report["layout_passed"] and not report["legal_approval"]
    with pytest.raises(ValueError, match="shadowed"):
        inspect_layout(layout, OWN | {"PySide6.support.deprecated"})
    own = layout / "_internal/core/precision.py"
    own.parent.mkdir()
    own.write_text("inert private source fixture")
    with pytest.raises(ValueError, match="Own source"):
        inspect_layout(layout, OWN)


def test_layout_rejects_missing_binding_or_runtime(layout):
    (layout / "_internal/shiboken6/__init__.py").unlink()
    with pytest.raises(ValueError, match="Missing external"):
        inspect_layout(layout, OWN)


def test_layout_rejects_online_or_missing_application(layout):
    with pytest.raises(ValueError, match="Missing own"):
        inspect_layout(layout, set())
    path = layout / "_internal/distribution/windows/metadata.json"
    path.write_text(
        json.dumps({"distribution_channel": "standalone-offline", "offline_only": False})
    )
    with pytest.raises(ValueError, match="offline profile"):
        inspect_layout(layout, OWN)


def test_installer_rejects_version_mismatch_and_tampered_payload_before_archive_read(layout):
    with pytest.raises(ValueError, match="metadata/profile"):
        validate_installer_input(layout, "1.0.0.2", "Delatorre Corporation")
    (layout / "payload-manifest.json").write_text(json.dumps({"schema_version": 1, "files": []}))
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_installer_input(layout, "1.0.0.1", "Delatorre Corporation")


def test_standalone_installer_has_no_user_data_delete_or_automatic_launch():
    # Compile-time guard is independent from the PowerShell wrapper.
    installer = Path("distribution/windows/installer.iss").read_text()
    assert "#error Standalone commercial distribution is blocked" in installer
    assert "[UninstallDelete]" not in installer and "[InstallDelete]" not in installer
    assert "#ifndef Standalone\nFilename:" in installer
