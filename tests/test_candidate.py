"""Archive omissions and disclosure boundaries, using inert synthetic ZIP fixtures."""

from pathlib import Path
from zipfile import ZipFile

import pytest

from distribution.build import PRIVACY_FILES, ROOT, privacy_assets
from distribution.candidate import COMPONENTS, PREFIX, inspect_package
from distribution.msix import CONFIG


def fixture_package(path, omit=None, extra=None, publisher=None):
    """No fixture here is an executable, signed MSIX or SAC evidence."""
    files = {
        "AppxManifest.xml": (CONFIG / "AppxManifest.xml").read_bytes(),
        **{
            PREFIX
            + "_internal/"
            + (
                token if "." in token else token + (".pyd" if key == "numpy" else ".dll")
            ): b"inert fixture"
            for key, token in COMPONENTS.items()
        },
    }
    for suffix in (
        "proj.db",
        "icudtl.dat",
        "qtwebengine_resources.pak",
        "desktop/map_assets/map-offline.html",
        "desktop/map_assets/leaflet.js",
        "desktop/map_assets/leaflet.css",
        "desktop/map_assets/map.js",
        "desktop/map_assets/map.css",
        "translations/qtwebengine_locales/pt-BR.pak",
    ):
        files[PREFIX + "_internal/" + suffix] = b"inert local fixture"
    for name in PRIVACY_FILES:
        files[PREFIX + "_internal/desktop/privacy_assets/" + name] = (
            ROOT / "docs/privacy/offline" / name
        ).read_bytes()
    if omit:
        files = {name: content for name, content in files.items() if omit not in name}
    if extra:
        files[extra] = b"inert unexpected document"
    if publisher:
        files["AppxManifest.xml"] = files["AppxManifest.xml"].replace(
            b"CN=43189595-B928-4D57-90A4-24300E4D4976", publisher.encode()
        )
    with ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_policy_asset_selection_excludes_operational_and_internal_documents():
    assert {Path(source).name for source, _ in privacy_assets()} == set(PRIVACY_FILES)
    assert all(destination == "desktop/privacy_assets" for _, destination in privacy_assets())


def test_candidate_archive_preserves_limits_and_exact_policy(tmp_path):
    file = tmp_path / "synthetic.msix"
    fixture_package(file)
    result = inspect_package(file)
    assert result["signature"] == "unsigned-store-submission"
    assert not result["privacy_policy_approved"]
    assert not result["installed_msix_validated"] and not result["sac_approved"]
    assert result["identity"]["store_id"] == "9NRDJ3ZTM978"
    assert set(result["components"]) == set(COMPONENTS)


@pytest.mark.parametrize(
    "omit", ["qtwebengineprocess.exe", "proj.db", "leaflet.js", "qtwebengine_locales"]
)
def test_candidate_rejects_missing_native_or_local_resources(tmp_path, omit):
    file = tmp_path / "synthetic.msix"
    fixture_package(file, omit=omit)
    with pytest.raises(ValueError, match="missing"):
        inspect_package(file)


def test_candidate_rejects_internal_document_leak(tmp_path):
    file = tmp_path / "synthetic.msix"
    fixture_package(file, extra=PREFIX + "_internal/desktop/privacy_assets/private-records.csv")
    with pytest.raises(ValueError, match="internal documents"):
        inspect_package(file)


def test_candidate_rejects_replaced_publisher(tmp_path):
    file = tmp_path / "synthetic.msix"
    fixture_package(file, publisher="CN=Different")
    with pytest.raises(ValueError, match="identity"):
        inspect_package(file)


@pytest.mark.parametrize(
    "extra",
    [
        "PySide6/QtCharts.pyd",
        "PySide6/qml/QtQuick3D/qmldir",
        "PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll",
    ],
)
def test_final_archive_rejects_unused_qt_components(tmp_path, extra):
    file = tmp_path / "synthetic.msix"
    fixture_package(file, extra=PREFIX + "_internal/" + extra)
    with pytest.raises(ValueError, match="Forbidden Qt"):
        inspect_package(file)
