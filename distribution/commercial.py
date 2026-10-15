"""Explicit commercial standalone entry point, distinct from the closed offline editions."""

from _agrolines_license_settings import KEYRING, ORIGIN, TEST_PROFILE

from core.offline_policy import enforce

enforce(licensing_endpoint=ORIGIN)


def main():
    import sys

    if TEST_PROFILE and len(sys.argv) == 4 and sys.argv[1] == "--licensing-probe":
        from distribution.commercial_probe import run

        return run(sys.argv[2], sys.argv[3])

    from PySide6.QtWidgets import QApplication, QMessageBox

    from desktop.commercial import CommercialWindow
    from desktop.license_storage import make_manager
    from desktop.license_transport import LicenseTransport
    from distribution.standalone_support import taskbar_identity

    taskbar_identity()
    app = QApplication(sys.argv)
    from pathlib import Path

    from PySide6.QtGui import QIcon

    assets = Path(sys._MEIPASS) / "distribution/windows"
    app.setApplicationName("AgroLines")
    app.setWindowIcon(QIcon(str(assets / "AgroLines.ico")))
    try:
        manager = make_manager(KEYRING, LicenseTransport(ORIGIN))
        window = CommercialWindow(manager)
    except (ValueError, OSError) as exc:
        QMessageBox.critical(None, "Ativação protegida", str(exc))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
