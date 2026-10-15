"""Negative controls: synthetic archives/headers/databases; never load native code."""

import importlib.util
import sqlite3
import struct
from pathlib import Path
from zipfile import ZipFile, ZipInfo

import pytest


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load("audit")
project = load("project_snapshot")


def record(status="Valid", flags=None, timestamp=True, exit_code=0):
    return {
        "signature": {
            "status": status,
            "chain_valid": False,
            "chain_status": flags or [],
            "integrity_matches": True,
            "timestamp_signer": "historical signer" if timestamp else None,
        },
        "signtool": {
            "exit_code": exit_code,
            "integrity_matches": True,
            "timeout": False,
            "stdout": "The signature is timestamped: time\nTimestamp Verified by:"
            if timestamp
            else "",
        },
    }


def test_overlap_classification_requires_timestamp_and_signtool():
    row = record(flags=["NotTimeValid"])
    assert audit.chain_class(row) == "current_time_expiry_historical_signtool_accepted"
    row["signtool"]["exit_code"] = 1
    with pytest.raises(ValueError, match="Unaccepted"):
        audit.chain_class(row)


@pytest.mark.parametrize("flags,timestamp", [(["Revoked"], True), (["NotTimeValid"], False)])
def test_no_expiry_exception_for_other_failure(flags, timestamp):
    with pytest.raises(ValueError):
        audit.chain_class(record(flags=flags, timestamp=timestamp))


def test_unsigned_is_not_expired_signed():
    assert audit.chain_class(record("NotSigned", exit_code=1)) == "unsigned_no_signer_chain"
    with pytest.raises(ValueError):
        audit.chain_class(record("NotSigned", flags=["NotTimeValid"], exit_code=1))


@pytest.mark.parametrize("names", [("a", "A"), ("../a",), ("C:/a",), ("a\\b",)])
def test_unsafe_archive_refused(tmp_path, names):
    target = tmp_path / "unsafe.zip"
    with ZipFile(target, "w") as archive:
        for name in names:
            archive.writestr(name, b"synthetic")
    if any("\\" in name for name in names):
        # ZipInfo normalizes the Windows OS separator while writing. Patch both
        # synthetic filename headers, never payload/CRC, to exercise the reader.
        target.write_bytes(target.read_bytes().replace(b"a/b", b"a\\b"))
    with ZipFile(target) as archive, pytest.raises(ValueError):
        audit.safe_entries(archive)


def test_same_entries_do_not_mean_same_container_bytes(tmp_path):
    first, second = tmp_path / "a.zip", tmp_path / "b.zip"
    for path, year in ((first, 2025), (second, 2026)):
        with ZipFile(path, "w") as archive:
            archive.writestr(ZipInfo("payload.txt", (year, 1, 1, 0, 0, 0)), b"same bytes")
    report = audit.compare_containers(first, second)
    assert report["entry_content_identical"]
    assert not report["container_bytes_identical"]
    assert report["metadata_differences"] == ["payload.txt"]


def test_modified_member_detected(tmp_path):
    first, second = tmp_path / "a.zip", tmp_path / "b.zip"
    for path, data in ((first, b"before"), (second, b"after")):
        with ZipFile(path, "w") as archive:
            archive.writestr("payload", data)
    assert not audit.compare_containers(first, second)["entry_content_identical"]


def test_header_certificate_bounds():
    data = bytearray(512)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 64)
    data[64:68] = b"PE\0\0"
    struct.pack_into("<H", data, 68, 0x8664)
    struct.pack_into("<H", data, 88, 0x20B)
    assert not audit.pe_header(data)
    struct.pack_into("<II", data, 88 + 112 + 32, 500, 64)
    with pytest.raises(ValueError, match="outside"):
        audit.pe_header(data)


def test_unpinned_artifact_refused_before_reading_zip(tmp_path):
    path = tmp_path / "fake.zip"
    path.write_bytes(b"not the authorized archive")
    with pytest.raises(ValueError, match="SHA256"):
        audit.audit(path, tmp_path)


def synthetic_project(tmp_path):
    path = tmp_path / "synthetic.agrolines"
    with sqlite3.connect(path) as db:
        for table in sorted(project.TABLES):
            db.execute(f'CREATE TABLE "{table}" (id TEXT)')
            db.execute(f'INSERT INTO "{table}" VALUES (?)', ("synthetic",))
        db.execute("PRAGMA user_version=1")
    return path


def test_readonly_snapshot_detects_content_change(tmp_path):
    path = synthetic_project(tmp_path)
    before = path.read_bytes()
    original = project.snapshot(path)
    assert path.read_bytes() == before
    with sqlite3.connect(path) as db:
        db.execute("UPDATE revision SET id='modified'")
    updated = project.snapshot(path)
    assert original["tables"]["revision"] != updated["tables"]["revision"]
    assert original["tables"]["project"] == updated["tables"]["project"]


def test_snapshot_refuses_hot_or_unknown_project(tmp_path):
    path = synthetic_project(tmp_path)
    wal = Path(str(path) + "-wal")
    wal.touch()
    with pytest.raises(ValueError, match="settle"):
        project.snapshot(path)
    wal.unlink()
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version=2")
    with pytest.raises(ValueError, match="Unknown schema"):
        project.snapshot(path)


def test_actual_application_schema_snapshot(tmp_path):
    from core.local_projects import LocalProject

    path = tmp_path / "actual-synthetic.agrolines"
    local = LocalProject.create(path, "Synthetic audit fixture")
    local.close()
    before = path.read_bytes()
    report = project.snapshot(path)
    assert report["tables"]["project"]["rows"] == 1
    assert report["tables"]["revision"]["rows"] == 0
    assert path.read_bytes() == before
