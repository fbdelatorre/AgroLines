import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from distribution.offline_checks import run_offline_checks


def test_offline_desktop_edit_save_reopen():
    app = QApplication.instance() or QApplication([])
    result = run_offline_checks()
    assert result["passed"] and result["network_calls_denied"]
    app.processEvents()


def test_local_workspace_controls_without_remote_client(tmp_path, monkeypatch):
    import json

    from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

    from desktop.local_projects import LocalProjectsWindow

    app = QApplication.instance() or QApplication([])
    project_path = tmp_path / "local.agrolines"
    source = tmp_path / "source.geojson"
    source.write_text(
        json.dumps(
            {
                "type": "Feature",
                "properties": {"name": "Local"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[300000, 7500000], [300100, 7500000], [300100, 7500100], [300000, 7500000]]
                    ],
                },
                "crs": {"properties": {"name": "EPSG:32723"}},
            }
        )
    )
    answers = iter([("Local", True), ("EPSG:32723", True), ("", True)])
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: next(answers))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(project_path), ""))
    monkeypatch.setattr(QFileDialog, "getOpenFileNames", lambda *a, **k: ([str(source)], ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    monkeypatch.setenv("AGROLINES_TILE_URL", "invalid unused remote imagery")
    window = LocalProjectsWindow()
    try:
        window.create_project()
        window.import_files()
        assert len(window.project.features()) == 1
        assert window.layers.count() == 1
        assert window.map.imagery is None
        assert not window.map.interceptor.online
        assert window.remote_windows == []
    finally:
        window.close()
        app.processEvents()
