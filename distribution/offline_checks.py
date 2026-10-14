"""Reproducible frozen client exercise; not physical-disconnection/SAC acceptance."""

import hashlib
import json
import socket
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QDialog

from core.local_projects import LocalProject
from desktop.local_projects import LocalVertexDialog


def existing_project(root):
    project = LocalProject(root / "project.agrolines")
    try:
        assert project.name == "Offline"
        feature = project.features()[0]
        assert len(project.features()) == 1 and len(project.history(feature["id"])) == 2
        assert abs(feature["original_geometry"]["coordinates"][0][0][0] - 300000.001123) < 1e-9
    finally:
        project.close()
    digest = hashlib.sha256((root / "project.agrolines").read_bytes()).hexdigest()
    for name in ("backup.agrolines", "restored.agrolines"):
        copied = LocalProject(root / name)
        try:
            assert copied.features()[0]["original_geometry"] == feature["original_geometry"]
        finally:
            copied.close()
    return digest


def run_offline_checks(project_directory=None):
    def forbidden(*args, **kwargs):
        raise RuntimeError("Network prohibited during offline project probe")

    with (
        patch.object(socket.socket, "connect", forbidden),
        patch.object(socket, "create_connection", forbidden),
        patch.object(socket, "getaddrinfo", forbidden),
        ExitStack() as contexts,
    ):
        directory = project_directory or contexts.enter_context(tempfile.TemporaryDirectory())
        root = Path(directory)
        root.mkdir(parents=True, exist_ok=True)
        if (root / "project.agrolines").exists():
            return {
                "passed": True,
                "network_calls_denied": True,
                "reopened_exact": True,
                "existing_project_preserved": True,
                "project_sha256": existing_project(root),
                "physical_disconnection_validated": False,
            }
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
        "existing_project_preserved": False,
        "project_sha256": existing_project(root) if project_directory else None,
    }
