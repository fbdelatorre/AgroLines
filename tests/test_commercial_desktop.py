"""Permission transitions preserve data and already-started edits; no fake UI approvals."""

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.licensing import Entitlements, Module  # noqa: E402
from core.local_projects import LocalProject  # noqa: E402
from desktop.commercial import CapturedPermission, CommercialWindow  # noqa: E402
from desktop.license_client import RecoveryManager  # noqa: E402
from desktop.local_projects import LocalVertexDialog  # noqa: E402


class ChangingLicense:
    state = {"license": None, "credential": None}
    active = True

    def verify(self):
        modules = frozenset(
            {Module.PROJECTS, Module.BACKUP} | ({Module.GEOMETRY} if self.active else set())
        )
        return Entitlements(
            "individual",
            modules,
            True,
            "Ativa" if self.active else "Vencida",
            read_only=not self.active,
        )

    def parsed(self):
        return None


def test_already_started_vertex_edit_can_save_after_license_expires(tmp_path):
    app = QApplication.instance() or QApplication([])
    license = ChangingLicense()
    project = LocalProject.create(
        tmp_path / "synthetic.agrolines", "Synthetic", license_verifier=license
    )
    source = tmp_path / "synthetic.geojson"
    source.write_text(
        json.dumps(
            {
                "type": "Polygon",
                "coordinates": [[[-45, -22], [-44.999, -22], [-44.999, -21.999], [-45, -22]]],
            }
        )
    )
    project.import_files([source], source_crs="EPSG:4326", acknowledge_warnings=True)
    feature = project.features()[0]
    operation = LocalProject(project.path, CapturedPermission(license.verify()))
    dialog = LocalVertexDialog(operation, feature)
    location, coordinate = next(dialog.editor.vertices())
    dialog.editor.set_vertex(location, coordinate[0] + 0.02, coordinate[1])
    license.active = False
    # Existing operation retains only its captured permission; future project edits are denied.
    dialog.save()
    assert len(project.history(feature["id"])) == 2
    import pytest

    with pytest.raises(PermissionError):
        project.save_geometry(feature["id"], feature["original_geometry"], 2)
    project.backup(tmp_path / "recovery.agrolines")
    operation.close()
    project.close()
    dialog.close()
    app.processEvents()


def test_recovery_shell_can_open_existing_project_without_activation(tmp_path):
    app = QApplication.instance() or QApplication([])
    project = LocalProject.create(tmp_path / "synthetic.agrolines", "Synthetic")
    project.close()

    class QuietWindow(CommercialWindow):
        def first_run(self):
            pass

    window = QuietWindow(RecoveryManager("Synthetic corrupted licensing state"))
    window.load(tmp_path / "synthetic.agrolines")
    assert window.project.features() == []
    assert window.manager.verify().read_only
    assert (
        "recuper" in window.manager.verify().reason.lower()
        or "suporte" in window.manager.verify().reason
    )
    window.close()
    app.processEvents()


def test_background_work_does_not_block_the_gui_event_loop():
    from threading import Event

    from PySide6.QtCore import QEventLoop, QTimer

    app = QApplication.instance() or QApplication([])

    class QuietWindow(CommercialWindow):
        def first_run(self):
            pass

    window = QuietWindow(ChangingLicense())
    release = Event()
    ticks = []

    def slow_service():
        if not release.wait(10):
            raise OSError("Synthetic timeout")
        return True

    completed = QEventLoop()
    window.async_work(slow_service, lambda value, error: completed.quit())
    loop = QEventLoop()
    QTimer.singleShot(20, lambda: ticks.append("GUI alive while service waits"))
    QTimer.singleShot(80, loop.quit)
    loop.exec()
    assert ticks and window.busy
    assert window.manager.verify().permits(Module.GEOMETRY)
    release.set()
    QTimer.singleShot(3000, completed.quit)
    completed.exec()
    assert not window.busy
    window.close()
    app.processEvents()
