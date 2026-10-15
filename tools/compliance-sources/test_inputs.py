"""Input guard: wrong wheel cannot trigger downloads or be treated as evidence."""

import sys

import pytest
import verify_gdal


def test_wrong_fiona_wheel_refused_before_network_or_directory_creation(tmp_path, monkeypatch):
    wheel = tmp_path / "fake.whl"
    wheel.write_bytes(b"not-the-approved-wheel")
    output = tmp_path / "new"
    monkeypatch.setattr(
        sys, "argv", ["verify_gdal", "--wheel", str(wheel), "--output", str(output)]
    )

    def forbidden(*args):
        raise AssertionError("Network request before provenance check")

    monkeypatch.setattr(verify_gdal, "api", forbidden)
    monkeypatch.setattr(verify_gdal.urllib.request, "urlopen", forbidden)
    with pytest.raises(SystemExit, match="Wrong Fiona wheel"):
        verify_gdal.main()
    assert not output.exists()
