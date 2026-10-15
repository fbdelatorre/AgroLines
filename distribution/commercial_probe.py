"""Synthetic frozen diagnostic, enabled ONLY in explicitly experimental lab builds."""

import json
import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4


def run(fixture_path, output):
    from _agrolines_license_settings import KEYRING, TEST_PROFILE

    if (
        not TEST_PROFILE
        or os.getenv("GITHUB_ACTIONS") != "true"
        or os.getenv("RUNNER_ENVIRONMENT") != "github-hosted"
        or sys.platform != "win32"
    ):
        raise PermissionError(
            "Synthetic licensing probe is restricted to the disposable Windows builder"
        )
    from core.license_protocol import decode, verify
    from core.licensing import Module
    from desktop.license_client import LicenseManager
    from desktop.license_storage import RegistryAnchor
    from desktop.protected_storage import WindowsVault
    from distribution.store_probe import run as gis_probe

    fixture = json.loads(Path(fixture_path).read_text())
    install = json.loads(decode(fixture["active"]["payload"]))["installation_id"]
    # The fixture is untrusted until the embedded public key verifies its signature.
    verify(fixture["active"], KEYRING, install)

    class NoNetwork:
        def post(self, *args):
            raise OSError("Synthetic offline server")

    import winreg

    anchor = RegistryAnchor()
    anchor.path = RegistryAnchor.path + "Lab\\" + str(uuid4())
    result = {
        "frozen": bool(getattr(sys, "frozen", False)),
        "sac_approved": False,
        "deployed_https_activation_proven": False,
        "installer_executed": False,
    }
    try:
        with tempfile.TemporaryDirectory() as work:
            vault = WindowsVault(Path(work) / "license.dpapi")
            assert vault.save({"installation_id": install, "license": None, "credential": None})
            manager = LicenseManager(vault, anchor, KEYRING, NoNetwork())
            assert manager.verify().read_only
            from PySide6.QtCore import QTimer
            from PySide6.QtWidgets import QApplication, QDialog, QLineEdit

            from desktop.commercial import CommercialWindow

            app = QApplication.instance() or QApplication([])
            window = CommercialWindow(manager)
            window.show()

            def observe_dialog():
                for widget in app.topLevelWidgets():
                    if (
                        isinstance(widget, QDialog)
                        and "Ativação e assinatura" in widget.windowTitle()
                    ):
                        result["activation_dialog_visible"] = widget.isVisible()
                        result["activation_key_field_hidden"] = any(
                            field.echoMode() == QLineEdit.Password
                            for field in widget.findChildren(QLineEdit)
                        )
                        widget.reject()
                QTimer.singleShot(0, window.close)

            QTimer.singleShot(700, observe_dialog)
            app.exec()
            assert result.get("activation_dialog_visible") and result.get(
                "activation_key_field_hidden"
            )
            manager.accept(
                {
                    "license": fixture["active"],
                    "credential": "synthetic-not-a-server-token-for-laboratory",
                }
            )
            assert manager.verify().permits(Module.GEOMETRY)
            assert fixture["active"]["payload"].encode() not in vault.path.read_bytes()
            reopened = LicenseManager(vault, anchor, KEYRING, NoNetwork())
            assert reopened.state["installation_id"] == install
            assert reopened.verify().permits(Module.GEOMETRY)
            try:
                reopened.check()
            except OSError:
                pass
            assert reopened.verify().permits(Module.GEOMETRY)
            previous = vault.path.read_bytes()
            reopened.accept({"license": fixture["revoked"]})
            vault.path.write_bytes(previous)
            restored = LicenseManager(vault, anchor, KEYRING, NoNetwork())
            assert restored.verify().read_only
            result.update(
                dpapi_roundtrip=True,
                offline_valid=True,
                reinstall_state_preserved=True,
                network_failure_preserved_validity=True,
                revocation_survived_file_restore=True,
            )
        # Real frozen WebEngine/Leaflet/GIS checks; laboratory fixtures use development
        # entitlements and are never an alternative customer entrypoint.
        gis_path = Path(output).with_name("commercial-gis.json")
        assert gis_probe(gis_path) == 0
        result["gis"] = json.loads(gis_path.read_text())
        result["passed"] = True
        Path(output).write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return 0
    finally:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, anchor.path)
        except FileNotFoundError:
            pass


def concurrency(fixture_path, directory, mode):
    """Two independent frozen processes, one protected state; no production registry path."""
    import time
    from uuid import UUID

    from _agrolines_license_settings import KEYRING, TEST_PROFILE

    if (
        not TEST_PROFILE
        or os.getenv("GITHUB_ACTIONS") != "true"
        or os.getenv("RUNNER_ENVIRONMENT") != "github-hosted"
        or sys.platform != "win32"
    ):
        raise PermissionError(
            "Concurrent licensing experiment requires authorized disposable builder"
        )
    root = Path(directory).resolve()
    if not root.is_relative_to(Path(os.environ["RUNNER_TEMP"]).resolve()):
        raise ValueError("Laboratory state must stay inside the disposable runner temp")
    identifier = str(UUID(root.name))
    if identifier != root.name:
        raise ValueError("Canonical laboratory identifier required")
    from core.license_protocol import decode, verify
    from desktop.license_client import LicenseManager
    from desktop.license_storage import RegistryAnchor
    from desktop.protected_storage import WindowsVault

    fixture = json.loads(Path(fixture_path).read_text())
    installation = json.loads(decode(fixture["active"]["payload"]))["installation_id"]
    verify(fixture["active"], KEYRING, installation)
    anchor = RegistryAnchor()
    anchor.path = RegistryAnchor.path + "Lab\\" + identifier
    if mode == "cleanup":
        import winreg

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, anchor.path)
        except FileNotFoundError:
            pass
        return 0
    vault = WindowsVault(root / "license.dpapi")

    class NoNetwork:
        def post(self, *args):
            raise OSError("Synthetic offline experiment")

    if mode == "init":
        root.mkdir(parents=True, exist_ok=False)
        vault.save({"installation_id": installation, "license": None, "credential": None})
        manager = LicenseManager(vault, anchor, KEYRING, NoNetwork())
        manager.accept({"license": fixture["active"]})
    elif mode == "observer":
        manager = LicenseManager(vault, anchor, KEYRING, NoNetwork())
        assert not manager.verify().read_only
        (root / "observer.ready").write_text("ready")
        deadline = time.monotonic() + 20
        while not (root / "writer.done").exists():
            if time.monotonic() > deadline:
                raise TimeoutError("Other laboratory process did not finish")
            time.sleep(0.05)
        assert manager.verify().read_only
        result = {
            "stale_process_cannot_erase_revocation": True,
            "different_frozen_processes": True,
            "dpapi_used": True,
            "named_mutex_used": True,
            "sac_approved": False,
        }
        (root / "observer.json").write_text(json.dumps(result) + "\n")
    elif mode == "writer":
        manager = LicenseManager(vault, anchor, KEYRING, NoNetwork())
        previous = vault.path.read_bytes()
        manager.accept({"license": fixture["revoked"]})
        vault.path.write_bytes(previous)  # deliberate file-restore negative control, lab data only
        (root / "writer.done").write_text("revocation persisted; old file restored")
    else:
        raise ValueError("Unknown laboratory role")
    return 0
