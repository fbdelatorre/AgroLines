import json
import subprocess
import sys

import pytest

from core.local_projects import LocalProject
from scripts.store_demo import prepare


def test_demo_is_local_synthetic_and_backup_reopens_exactly(tmp_path):
    path = prepare(tmp_path / "synthetic")
    evidence = json.loads((path.parent / "origem-dos-dados.json").read_text())
    assert evidence["synthetic_only"] and evidence["work_crs"] == "EPSG:32723"
    project = LocalProject(path)
    backup = LocalProject(path.parent / "Backup-demonstracao-ficticia.agrolines")
    try:
        features = project.features()
        assert len(features) == 4 and all(feature["revision"] == 1 for feature in features)
        assert backup.features() == features
        assert all("Fictícia" in f["name"] or "fictíc" in f["name"] for f in features)
        assert project.db.execute("SELECT COUNT(*) FROM source").fetchone()[0] >= 6
    finally:
        project.close()
        backup.close()
    with pytest.raises(FileExistsError):
        prepare(path.parent)


@pytest.mark.skipif(sys.platform == "win32", reason="Only non-Windows refusal is tested here")
def test_capture_refuses_non_windows_without_substitute_images(tmp_path):
    output = tmp_path / "not-windows"
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.capture_store_windows", "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert completed.returncode == 2
    report = json.loads((output / "capture-evidence.json").read_text())
    assert not report["completed"] and not report["images"]
    assert not list(output.glob("*.png"))
    assert (output / "README.md").is_file()
