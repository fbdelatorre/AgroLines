"""Negative controls for isolated lab evidence, never substitutes native execution."""

import struct

import pytest
from run import apply_marker, validate, x64


def test_marker_refuses_unknown_or_duplicate_source(tmp_path):
    source = tmp_path / "capi/geos_ts_c.cpp"
    source.parent.mkdir()
    source.write_text('"%s", GEOS_CAPI_VERSION\n"%s", GEOS_CAPI_VERSION')
    with pytest.raises(ValueError, match="Unexpected source"):
        apply_marker(tmp_path, "geos-3.14.1")
    source.write_text('snprintf(version, 256, "%s", GEOS_CAPI_VERSION);')
    apply_marker(tmp_path, "geos-3.14.1")
    assert source.read_text() == (
        'snprintf(version, 256, "%s-agrolines-synthetic", GEOS_CAPI_VERSION);'
    )


def test_wrong_phase_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="version"):
        validate({"version": "3.14.1"}, "modified", tmp_path)


def test_outside_selected_directory_is_rejected(tmp_path):
    outside = tmp_path / "outside.dll"
    outside.write_bytes(b"MZ")
    with pytest.raises(ValueError, match="outside"):
        validate({"version": "3.14.1", "loaded_path": str(outside)}, "original", tmp_path / "lab")


def test_x86_rejected(tmp_path):
    dll = tmp_path / "bad.dll"
    dll.write_bytes(b"MZ" + b"\0" * 58 + struct.pack("<I", 64) + b"PE\0\0\x4c\x01")
    with pytest.raises(ValueError, match="x64"):
        x64(dll)
