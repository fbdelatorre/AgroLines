"""Persistent synthetic installed-state exercise, disposable Server lab ONLY."""

import json
import os
import sys
from pathlib import Path
from uuid import UUID


def run(phase, fixture, directory, output):
    from _agrolines_license_settings import KEYRING, TEST_PROFILE

    if (
        not TEST_PROFILE
        or sys.platform != "win32"
        or os.getenv("GITHUB_ACTIONS") != "true"
        or os.getenv("RUNNER_ENVIRONMENT") != "github-hosted"
    ):
        raise PermissionError("Installed probe is restricted to the authorized disposable builder")
    root = Path(directory).resolve()
    identifier = str(UUID(root.name))
    if root.name != identifier or not root.is_relative_to(
        Path(os.environ["RUNNER_TEMP"]).resolve()
    ):
        raise ValueError("Fresh canonical UUID state inside runner temp required")
    from core.license_protocol import decode, verify
    from desktop.license_client import LicenseManager
    from desktop.license_storage import RegistryAnchor
    from desktop.protected_storage import WindowsVault

    anchor = RegistryAnchor()
    anchor.path += "Lab\\" + identifier
    if phase == "cleanup":
        import winreg

        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, anchor.path)
        return 0
    if phase not in ("initialize", "verify"):
        raise ValueError("Unknown installed-state phase")
    data = json.loads(Path(fixture).read_text())
    install = json.loads(decode(data["active"]["payload"]))["installation_id"]
    verify(data["active"], KEYRING, install)
    root.mkdir(parents=True, exist_ok=True)
    vault = WindowsVault(root / "license.dpapi")

    class Offline:
        def post(self, *args):
            raise OSError("Synthetic server unavailable; valid offline state must survive")

    if phase == "initialize":
        if vault.path.exists():
            raise ValueError("Initial state must be fresh")
        vault.save({"installation_id": install, "license": None, "credential": None})
    manager = LicenseManager(vault, anchor, KEYRING, Offline())
    if phase == "initialize":
        manager.accept({"license": data["active"], "credential": "synthetic-laboratory-token-only"})
    assert manager.state["installation_id"] == install and not manager.verify().read_only
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from desktop.commercial import CommercialWindow
    from distribution.offline_checks import run_offline_checks

    app = QApplication.instance() or QApplication([])
    projects = run_offline_checks(root / "projects", manager)
    window = CommercialWindow(manager)
    window.setWindowTitle("AgroLines · TESTE · homologação instalada")
    window.show()
    ready = []

    def loaded():
        ready.append(window.map.is_ready and window.isVisible())
        QTimer.singleShot(250, window.close)

    window.map.readyChanged.connect(loaded)
    QTimer.singleShot(30000, window.close)
    app.exec()
    assert ready and all(ready), "Installed Qt/Leaflet GUI did not become ready"
    result = {
        "phase": phase,
        "frozen": bool(getattr(sys, "frozen", False)),
        "license_preserved": not manager.verify().read_only,
        "installation_identity_preserved": manager.state["installation_id"] == install,
        "projects": projects,
        "gui_and_leaflet_ready": True,
        "test_profile": True,
        "real_https_activation_proven": False,
        "sac_approved": False,
    }
    from desktop.storage import data_directory

    assert not data_directory().resolve().is_relative_to(Path(sys.executable).resolve().parent)
    result["default_data_outside_runtime"] = True
    result["local_diagnostic_present"] = (data_directory() / "Diagnostics/desktop.log").is_file()
    assert result["local_diagnostic_present"]
    Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0
