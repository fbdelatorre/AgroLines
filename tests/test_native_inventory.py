import hashlib
import json
import struct
from pathlib import Path

import pytest

from scripts.native_inventory import inventory
from scripts.windows_probe import probe


def native_file(path):
    content = bytearray(128)
    content[:2] = b"MZ"
    struct.pack_into("<I", content, 60, 64)
    content[64:70] = b"PE\0\0\x64\x86"
    path.write_bytes(content)
    return content


def test_inventory_native_files_hashes_ownership_and_runtime(tmp_path):
    binary = tmp_path / "blocked.pyd"
    content = native_file(binary)
    runtime = tmp_path / "python.exe"
    native_file(runtime)
    (tmp_path / "not-native.txt").write_text("ignored")

    class Distribution:
        metadata = {"Name": "SyntheticGIS"}
        version = "1.2"
        files = [Path("blocked.pyd")]

        def locate_file(self, path):
            return tmp_path / path

    result = inventory([tmp_path, tmp_path], [Distribution()])
    assert result["inspection_complete"]
    assert len(result["files"]) == 2
    item = next(f for f in result["files"] if f["path"] == str(binary))
    assert item["sha256"] == hashlib.sha256(content).hexdigest()
    assert item["architecture"] == "x64"
    assert item["packages"] == [{"name": "SyntheticGIS", "version": "1.2"}]
    assert not result["smart_app_control_compatibility_proven"]
    json.dumps(result)


def test_partial_inventory_never_approves(tmp_path):
    native_file(tmp_path / "example.dll")
    result = inventory([tmp_path, tmp_path / "missing"], [])
    assert not result["inspection_complete"]
    assert result["errors"][0]["error"] == "root_missing"


def test_empty_inventory_never_approves(tmp_path):
    assert not inventory([tmp_path], [])["inspection_complete"]


def test_symlink_does_not_escape_inventory(tmp_path):
    target = tmp_path / "external"
    target.mkdir()
    native_file(target / "external.dll")
    root = tmp_path / "root"
    root.mkdir()
    try:
        (root / "link").symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Creating symlinks is unavailable to this test account")
    result = inventory([root], [])
    assert not result["inspection_complete"] and not result["files"]
    assert result["errors"][0]["error"] == "symlink_directory_not_scanned"


@pytest.mark.parametrize("case", ["numpy", "shapely", "fiona", "pyproj", "shapefile"])
def test_native_functional_probes(case):
    probe(case)


def test_probe_error_output_does_not_disclose_secrets(monkeypatch, capsys):
    from scripts import windows_probe

    def failing(_):
        raise RuntimeError("postgresql://private-password@host/db")

    monkeypatch.setattr(windows_probe, "probe", failing)
    monkeypatch.setattr("sys.argv", ["windows_probe", "server-import"])
    with pytest.raises(SystemExit) as error:
        windows_probe.main()
    assert error.value.code == 1
    output = capsys.readouterr().err
    assert "private-password" not in output and "FAILED (RuntimeError)" in output
