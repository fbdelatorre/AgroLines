"""Reject misleading full-app native evidence without executing any DLL."""

import importlib.util
import json
from pathlib import Path

import pytest

path = Path(__file__).parents[1] / "tools/standalone-native-lab/run.py"
spec = importlib.util.spec_from_file_location("full_native_lab", path)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


@pytest.fixture
def observed(tmp_path):
    source = tmp_path / "Qt6Core.dll"
    source.write_bytes(b"inert fixture; never loaded")
    snapshots = {
        "errors": [],
        "frozen": True,
        "qt_version": "6.12.0-agrolines-synthetic",
        "modules": [{"path": str(source), "sha256": lab.lab.sha(source)}],
    }
    for number in range(3):
        (tmp_path / f"loaded-{number}.json").write_text(json.dumps(snapshots))
    (tmp_path / "smoke-startup-and-gis-probe.json").write_text(
        json.dumps(
            {
                "checks_passed": True,
                "precision": {"checks": [True] * 22},
            }
        )
    )
    (tmp_path / "offline-import-edit-backup-probe.json").write_text(
        json.dumps(
            {
                "passed": True,
                "webengine_ready": True,
                "local_formats": ["SHP", "GPKG", "KML", "KMZ", "GeoJSON"],
            }
        )
    )
    return tmp_path, source


def test_validator_rejects_unmodified_version_and_wrong_loaded_bytes(observed):
    directory, source = observed
    result = lab.validate_reports(directory, "modified", "qtbase-6.12.0", {source: source})
    assert result["computational_precision"] == "22/22"
    with pytest.raises(ValueError, match="version not observed"):
        lab.validate_reports(directory, "upstream-original", "qtbase-6.12.0", {source: source})
    source.write_bytes(b"different bytes than the process observation")
    with pytest.raises(ValueError, match="not loaded"):
        lab.validate_reports(directory, "modified", "qtbase-6.12.0", {source: source})


def test_incomplete_capture_and_precision_regression_cannot_approve(observed):
    directory, source = observed
    path = directory / "smoke-startup-and-gis-probe.json"
    data = json.loads(path.read_text())
    data["precision"]["checks"].pop()
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="regression"):
        lab.validate_reports(directory, "modified", "qtbase-6.12.0", {source: source})
    (directory / "loaded-2.json").unlink()
    with pytest.raises(ValueError, match="all three"):
        lab.validate_reports(directory, "modified", "qtbase-6.12.0", {source: source})


def test_signing_example_has_no_approval_or_credentials():
    cfg = json.loads(
        Path("distribution/windows/standalone/signing-configuration.example.json").read_text()
    )
    assert cfg["authorized"] is False
    assert all(r["authorized"] is False for r in cfg["roles"].values())
    assert all(r["approved"] is False for r in cfg["reviews"].values())
    assert cfg["certificate"]["thumbprint"] is None
    assert cfg["certificate"]["approved_public_roots"] == []
