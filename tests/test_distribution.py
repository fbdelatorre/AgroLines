import json
from datetime import UTC, datetime

import pytest

from distribution.build import store_builder_environment, version_tuple
from distribution.checks import run_checks
from distribution.payload import manifest, verify
from distribution.windows_evidence import classify_events, collect


def test_payload_manifest_tamper_extra_files_and_path_escape(tmp_path):
    root = tmp_path / "payload"
    root.mkdir()
    file = root / "program.exe"
    file.write_bytes(b"actual payload bytes")
    data = manifest(root)
    assert verify(root, data)
    assert not data["approved_for_distribution"]
    (root / "extra.dll").write_bytes(b"unexpected")
    assert not verify(root, data)
    (root / "extra.dll").unlink()
    file.write_bytes(b"tampered")
    assert not verify(root, data)
    assert not verify(
        root, {"schema_version": 1, "files": [{"path": "../external", "sha256": "0" * 64}]}
    )


def test_manifest_covers_resources_as_well_as_native_code(tmp_path):
    (tmp_path / "map.js").write_text("const verified = true;")
    data = manifest(tmp_path)
    assert data["files"][0]["path"] == "map.js"
    assert verify(tmp_path, json.loads(json.dumps(data)))


def test_store_builder_does_not_inherit_incidental_tools_or_runtime_overrides(
    tmp_path, monkeypatch
):
    import os

    python = tmp_path / "python"
    windows = tmp_path / "windows"
    (python / "DLLs").mkdir(parents=True)
    (windows / "System32").mkdir(parents=True)
    monkeypatch.setattr("distribution.build.sys.prefix", str(python))
    monkeypatch.setattr("distribution.build.sys.base_prefix", str(python))
    monkeypatch.setenv("WINDIR", str(windows))
    monkeypatch.setenv("PATH", "INCIDENTAL_JAVA" + os.pathsep + "INCIDENTAL_GIS")
    monkeypatch.setenv("PYTHONPATH", "INCIDENTAL_PYTHON")
    monkeypatch.setenv("QT_PLUGIN_PATH", "INCIDENTAL_QT")
    monkeypatch.setenv("PROJ_DATA", "INCIDENTAL_PROJ")
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1234567890")
    environment = store_builder_environment()
    assert "INCIDENTAL" not in environment["PATH"]
    assert str(windows / "System32") in environment["PATH"].split(os.pathsep)
    assert all(key not in environment for key in ("PYTHONPATH", "QT_PLUGIN_PATH", "PROJ_DATA"))
    assert environment["SOURCE_DATE_EPOCH"] == "1234567890"
    assert "INCIDENTAL_JAVA" in os.environ["PATH"]  # Parent/system settings untouched.


@pytest.mark.parametrize("version", ["1.2.3", "1.2.3.65536", "1.2.3.x", "1.2.-3.4"])
def test_version_metadata_rejects_invalid_windows_versions(version):
    with pytest.raises(ValueError):
        version_tuple(version)


def test_event_evidence_preserves_raw_records_and_matches_nt_paths():
    xml = (
        "<Event><EventData><Data>\\Device\\HarddiskVolume3\\APP\\"
        "_MULTIARRAY_UMATH.cp312-win_amd64.pyd</Data></EventData></Event>"
        "<Event><EventData><Data>elsewhere.dll</Data></EventData></Event>"
    )
    events = classify_events(xml, ["_multiarray_umath.cp312-win_amd64.pyd"])
    assert len(events) == 2
    assert events[0]["associated_with_payload"] and not events[1]["associated_with_payload"]
    assert "HarddiskVolume3" in events[0]["xml"]


def test_real_native_checks_reuse_geometric_precision():
    result = run_checks()
    assert result["geospatial_checks_passed"]
    assert len(result["precision"]["checks"]) == 22
    assert result["precision"]["computational_tests_passed"]
    assert not result["precision"]["absolute_field_centimeter_accuracy_validated"]
    assert set(result["versions"]) == {"numpy", "shapely", "pyproj", "fiona", "gdal", "pyside6"}


def test_non_windows_never_claims_sac(monkeypatch):
    monkeypatch.setattr("distribution.windows_evidence.sys.platform", "linux")
    result = collect(datetime.now(UTC), ["example.exe"])
    assert not result["sac_active_confirmed"] and not result["code_integrity_readable"]
