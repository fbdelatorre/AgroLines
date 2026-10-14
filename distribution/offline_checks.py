"""Reproducible frozen client exercise; not physical-disconnection/SAC acceptance."""

import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QDialog

from core.local_projects import LocalProject
from desktop.local_projects import LocalVertexDialog


def run_offline_checks():
    def forbidden(*args, **kwargs):
        raise RuntimeError("Network prohibited during offline project probe")

    with (
        patch.object(socket.socket, "connect", forbidden),
        patch.object(socket, "create_connection", forbidden),
        patch.object(socket, "getaddrinfo", forbidden),
        tempfile.TemporaryDirectory() as directory,
    ):
        root = Path(directory)
        source = root / "synthetic.geojson"
        geometry = {
            "type": "Polygon",
            "coordinates": [
                [
                    [300000.000123, 7500000.000123],
                    [300100.000123, 7500000.000123],
                    [300100.000123, 7500100.000123],
                    [300000.000123, 7500000.000123],
                ]
            ],
        }
        source.write_text(
            json.dumps(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {"name": "Offline synthetic"},
                    "crs": {"properties": {"name": "EPSG:32723"}},
                }
            )
        )
        project = LocalProject.create(root / "project.agrolines", "Offline")
        try:
            project.import_files([source], acknowledge_warnings=True)
            feature = project.features()[0]
            dialog = LocalVertexDialog(project, feature)
            before = float(dialog.x.text())
            dialog.x.setText(format(before + 0.001, ".17g"))
            dialog.apply()
            dialog.undo()
            assert float(dialog.x.text()) == before
            dialog.redo()
            dialog.save()
            assert dialog.result() == QDialog.Accepted, dialog.status.text()
            dialog.close()
            edited = project.features()[0]["original_geometry"]
            assert abs(edited["coordinates"][0][0][0] - before - 0.001) < 1e-9
            project.backup(root / "backup.agrolines")
        finally:
            project.close()
        reopened = LocalProject(root / "project.agrolines")
        try:
            assert reopened.features()[0]["original_geometry"] == edited
            assert len(reopened.history(feature["id"])) == 2
        finally:
            reopened.close()
        restored = LocalProject.restore(root / "backup.agrolines", root / "restored.agrolines")
        try:
            assert restored.features()[0]["original_geometry"] == edited
        finally:
            restored.close()
    return {
        "passed": True,
        "network_calls_denied": True,
        "numeric_edit_m": 0.001,
        "reopened_exact": True,
        "backup_restored": True,
        "physical_disconnection_validated": False,
    }
