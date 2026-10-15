"""Adversarial evidence checks; matching source metadata must never approve a release."""

import io
import tarfile

import pytest

from tools.webengine_legal.audit import (
    assessment,
    checked_download,
    digest,
    inspect_archive,
    inspect_wheel,
    returned_literal,
)


def archive_fixture(tmp_path, members):
    path = tmp_path / "synthetic-source.tar.xz"
    with tarfile.open(path, "w:xz") as package:
        for name, value in members.items():
            data = value.encode()
            member = tarfile.TarInfo(name)
            member.size = len(data)
            package.addfile(member, io.BytesIO(data))
    return path, {"sha256": digest(path)}


def test_effective_snapshot_not_summary_determines_source_version(tmp_path):
    path, record = archive_fixture(
        tmp_path,
        {
            "qt/CHROMIUM_VERSION": "Based on Chromium version: 140.0.7339.264",
            "qt/src/3rdparty/chromium/chrome/VERSION": (
                "MAJOR=140\nMINOR=0\nBUILD=7339\nPATCH=225\n"
            ),
            "qt/src/3rdparty/chromium/LICENSE": "INERT synthetic notice, no legal grant",
        },
    )
    result = inspect_archive(path, record)
    assert result["chromium"] == "140.0.7339.225"
    assert len(result["source_notice_inventory"]) == 1
    assert result["source_notice_inventory_is_not_a_binary_target_bom"]


def test_identical_versions_and_source_never_approve_exact_build_or_legal_status():
    wheel = {
        "qt_webengine": "6.140.0",
        "chromium": "140.0.7339.225",
        "security_patch": "152.0.7977.83",
    }
    result = assessment(wheel, dict(wheel), {"chromium": wheel["chromium"]})
    assert result["versions_match_candidate"] and result["effective_source_chromium_matches"]
    for name in (
        "exact_wheel_source_correspondence_proven",
        "actual_target_generated_credits_proven",
        "legal_approved",
        "distribution_approved",
    ):
        assert result[name] is False
    assert not assessment(wheel, {})["versions_match_candidate"]


def test_wheel_drift_is_rejected_before_parsing_or_native_loading(tmp_path):
    path = tmp_path / "inert.whl"
    path.write_bytes(b"not executable, not a real wheel")
    with pytest.raises(ValueError, match="audited official input"):
        inspect_wheel(path, {"sha256": "0" * 64})


def test_changed_archive_rejected_before_inspection(tmp_path):
    path, _ = archive_fixture(tmp_path, {"source/LICENSE": "INERT"})
    with pytest.raises(ValueError, match="checksum mismatch"):
        inspect_archive(path, {"sha256": "0" * 64})


def test_archive_traversal_rejected_without_extracting(tmp_path):
    path, record = archive_fixture(tmp_path, {"../untrusted/LICENSE": "INERT"})
    with pytest.raises(ValueError, match="Unsafe archive"):
        inspect_archive(path, record)
    assert not (tmp_path.parent / "untrusted").exists()


def test_source_summary_cannot_replace_missing_actual_chrome_version(tmp_path):
    path, record = archive_fixture(tmp_path, {"source/CHROMIUM_VERSION": "140.0.7339.225"})
    with pytest.raises(ValueError, match="effective Chromium"):
        inspect_archive(path, record)


def test_download_does_not_overwrite_unknown_existing_input(tmp_path):
    path = tmp_path / "preserve.bin"
    path.write_bytes(b"preserve this original")
    with pytest.raises(ValueError, match="original file preserved"):
        checked_download("https://example.invalid/source", path, "0" * 64, 100)
    assert path.read_bytes() == b"preserve this original"


def test_unsupported_export_never_falls_back_to_unrelated_string():
    class InertPE:
        def get_data(self, address, size):
            return b"\x90" * size

        def get_string_at_rva(self, address, size):
            raise AssertionError("Must reject the unsupported instruction first")

    with pytest.raises(ValueError, match="Unsupported exported function"):
        returned_literal(InertPE(), 100)
