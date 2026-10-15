"""Explicit commercial standalone entry point, distinct from the closed offline editions."""

from _agrolines_license_settings import KEYRING, ORIGIN, TEST_PROFILE

from core.offline_policy import enforce

enforce(licensing_endpoint=ORIGIN)


def main():
    import sys

    if TEST_PROFILE and len(sys.argv) == 5 and sys.argv[1] == "--license-concurrency":
        from distribution.commercial_probe import concurrency

        try:
            return concurrency(sys.argv[3], sys.argv[4], sys.argv[2])
        except Exception as exc:
            import json
            import os
            from pathlib import Path

            mode = (
                sys.argv[2]
                if sys.argv[2] in ("init", "observer", "writer", "cleanup")
                else "unknown"
            )
            if (
                os.getenv("GITHUB_ACTIONS") == "true"
                and os.getenv("RUNNER_ENVIRONMENT") == "github-hosted"
            ):
                target = Path(os.environ["RUNNER_TEMP"]) / (
                    "license-concurrency-" + mode + "-error.json"
                )
                target.write_text(
                    json.dumps({"error_type": type(exc).__name__, "message": str(exc)})
                )
            return 1
    if TEST_PROFILE and len(sys.argv) == 3 and sys.argv[1] == "--binding-report":
        import os

        if (
            os.getenv("GITHUB_ACTIONS") != "true"
            or os.getenv("RUNNER_ENVIRONMENT") != "github-hosted"
        ):
            raise PermissionError(
                "Laboratory diagnostics unavailable outside the authorized builder"
            )
        from distribution.standalone_support import binding_report

        binding_report(sys.argv[2])
        return 0
    if TEST_PROFILE and len(sys.argv) == 4 and sys.argv[1] == "--licensing-probe":
        from distribution.commercial_probe import run

        try:
            return run(sys.argv[2], sys.argv[3])
        except Exception as exc:
            import json
            import traceback
            from pathlib import Path

            frames = [
                {"file": row.filename, "line": row.lineno, "function": row.name}
                for row in traceback.extract_tb(exc.__traceback__)
            ]
            Path(sys.argv[3]).write_text(
                json.dumps(
                    {
                        "passed": False,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                        "frames": frames,
                    },
                    indent=2,
                )
            )
            return 1

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
    except (ValueError, OSError) as exc:
        from desktop.license_client import RecoveryManager

        manager = RecoveryManager(exc)
        QMessageBox.warning(None, "Ativação protegida", manager.reason)
    window = CommercialWindow(manager)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
