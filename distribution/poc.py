"""Frozen Windows distribution proof. Approval always requires external real-machine review."""

import argparse
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

STARTED = datetime.now(UTC)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-report", type=Path, help="Maintainer CI output; auto closes")
    parser.add_argument("--local", action="store_true", help="Open offline projects without login")
    parser.add_argument(
        "--require-msix", action="store_true", help="Fail without official package identity"
    )
    parser.add_argument(
        "--offline-project-root", type=Path, help="Maintainer durable synthetic fixture"
    )
    args = parser.parse_args()
    initial_assets = (
        Path(sys._MEIPASS) / "distribution/windows"
        if getattr(sys, "frozen", False)
        else Path(__file__).parent / "windows"
    )
    initial_metadata = json.loads((initial_assets / "metadata.json").read_text(encoding="utf-8"))
    from core.offline_policy import is_offline_only, require_local_path

    if is_offline_only() and not args.smoke_report:
        args.local = True
    if initial_metadata.get("distribution_channel") == "microsoft-store" and not args.smoke_report:
        args.local = True
    if (
        args.local
        and sys.platform == "win32"
        and (
            os.getenv("QTWEBENGINE_DISABLE_SANDBOX") == "1"
            or "--no-sandbox" in os.getenv("QTWEBENGINE_CHROMIUM_FLAGS", "")
        )
    ):
        return 1
    if args.local:
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication

        from desktop.local_projects import LocalProjectsWindow

        assets = (
            Path(sys._MEIPASS) / "distribution/windows"
            if getattr(sys, "frozen", False)
            else Path(__file__).parent / "windows"
        )
        metadata = json.loads((assets / "metadata.json").read_text(encoding="utf-8"))
        local_app = QApplication(sys.argv[:1])
        local_app.setApplicationName(metadata["name"])
        local_app.setApplicationVersion(metadata["version"])
        local_app.setOrganizationName(metadata["manufacturer"])
        local_app.setWindowIcon(
            QIcon(
                str(
                    assets / "AgroLines.ico"
                    if getattr(sys, "frozen", False)
                    else Path(__file__).parent.parent
                    / "assets/branding/AgroLines_Arte_Caixa_1080x1080.png"
                )
            )
        )
        local_window = LocalProjectsWindow()
        local_window.show()
        return local_app.exec()
    from desktop.storage import data_directory

    directory = data_directory() / "Evidence"
    output = args.smoke_report or directory / (uuid.uuid4().hex + ".json")
    require_local_path(output)
    if args.offline_project_root:
        require_local_path(args.offline_project_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "offline_only": is_offline_only(),
        "frozen": bool(getattr(sys, "frozen", False)),
        "started_utc": STARTED.isoformat(),
        "approved_for_distribution": False,
        "checks_passed": False,
        "sac_compatibility_proven": False,
    }
    app = window = web_map = local_window = None
    exit_code = 1

    def save():
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    try:
        if sys.platform == "win32" and (
            os.getenv("QTWEBENGINE_DISABLE_SANDBOX") == "1"
            or "--no-sandbox" in os.getenv("QTWEBENGINE_CHROMIUM_FLAGS", "")
        ):
            raise RuntimeError("Chromium sandbox must remain active")
        from PySide6.QtCore import QTimer, QUrl
        from PySide6.QtGui import QDesktopServices, QIcon
        from PySide6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        from desktop.gis_map import WebMap
        from desktop.ui import THEME
        from distribution.checks import run_checks
        from distribution.payload import verify
        from distribution.windows_evidence import collect

        assets = (
            Path(sys._MEIPASS) / "distribution/windows"
            if report["frozen"]
            else Path(__file__).parent / "windows"
        )
        metadata = json.loads((assets / "metadata.json").read_text(encoding="utf-8"))
        report["metadata"] = metadata
        report["python_version"] = sys.version.split()[0]
        app = QApplication(sys.argv[:1])
        app.setApplicationName(metadata["name"])
        app.setApplicationVersion(metadata["version"])
        app.setOrganizationName(metadata["manufacturer"])
        app.setStyleSheet(THEME)
        app.setWindowIcon(
            QIcon(
                str(
                    assets / "AgroLines.ico"
                    if getattr(sys, "frozen", False)
                    else Path(__file__).parent.parent
                    / "assets/branding/AgroLines_Arte_Caixa_1080x1080.png"
                )
            )
        )
        window = QMainWindow()
        window.setWindowTitle(f"AgroLines · Prova de distribuição {metadata['version']}")
        window.resize(1000, 720)
        panel = QWidget()
        layout = QVBoxLayout(panel)
        title = QLabel(
            f"{metadata['name']} · {metadata['version']}\n{metadata['manufacturer']}"
            " · marca informada, identidade jurídica não verificada"
        )
        title.setWordWrap(True)
        layout.addWidget(title)
        status = QLabel("Verificando componentes… Homologação Windows/SAC pendente.")
        status.setWordWrap(True)
        layout.addWidget(status)
        result = run_checks()
        from distribution.offline_checks import run_offline_checks

        report["offline_projects"] = run_offline_checks(args.offline_project_root)
        report.update(result)
        report["evidence_before"] = collect(STARTED, ["AgroLinesPoC.exe"])
        web_map = WebMap(offline=bool(metadata.get("store_identity")) or args.require_msix)
        layout.addWidget(web_map, 1)
        web_map.set_collection(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "poc",
                        "geometry": result["geometry"],
                        "properties": {"name": "Polígono sintético de verificação"},
                    }
                ],
            },
            fit=True,
        )
        button = QPushButton("Abrir pasta de evidências")
        button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(output.parent)))
        )
        layout.addWidget(button)
        from desktop.local_projects import LocalProjectsWindow

        local_window = []

        def open_local():
            project_window = LocalProjectsWindow()
            local_window.append(project_window)
            project_window.show()

        local_button = QPushButton("Projetos locais · sem conexão ou login")
        local_button.clicked.connect(open_local)
        layout.addWidget(local_button)
        window.setCentralWidget(panel)
        window.show()
        finished = False

        def complete():
            nonlocal exit_code, finished
            if finished:
                return
            finished = True
            try:
                payload = Path(sys.executable).parent if report["frozen"] else None
                names = (
                    [
                        p.name
                        for p in payload.rglob("*")
                        if p.suffix.lower() in {".dll", ".pyd", ".exe"}
                    ]
                    if payload
                    else ["AgroLinesPoC.exe"]
                )
                report["evidence_after"] = collect(STARTED, names)
                manifest_path = payload / "payload-manifest.json" if payload else None
                report["payload_integrity_verified"] = bool(
                    manifest_path
                    and manifest_path.exists()
                    and verify(payload, json.loads(manifest_path.read_text()))
                )
                report["checks_passed"] = (
                    report["geospatial_checks_passed"]
                    and web_map.is_ready
                    and report["offline_projects"]["passed"]
                )
                from distribution.package_runtime import package_evidence, qt_helper_evidence

                package = package_evidence()
                report["package_identity"] = package
                report["qt_helpers"] = qt_helper_evidence(package.get("install_path"))
                project_external = bool(
                    args.offline_project_root
                    and package.get("install_path")
                    and not args.offline_project_root.resolve().is_relative_to(
                        Path(package["install_path"]).resolve()
                    )
                    and "packages" not in [p.casefold() for p in args.offline_project_root.parts]
                )
                report["project_directory_external"] = project_external
                report["msix_validation_passed"] = bool(
                    report["checks_passed"]
                    and package["official_identity_matches"]
                    and report["qt_helpers"]
                    and all(h["inside_package"] for h in report["qt_helpers"])
                    and project_external
                )
                if args.require_msix:
                    report["checks_passed"] = (
                        report["checks_passed"] and report["msix_validation_passed"]
                    )
                report["qt_webengine_map_ready"] = web_map.is_ready
                after = report["evidence_after"]
                report["sac_run_observed"] = (
                    report["evidence_before"]["sac_active_confirmed"]
                    and after["sac_active_confirmed"]
                    and after["code_integrity_readable"]
                    and not any(e["associated_with_payload"] for e in after["events"])
                    and report["checks_passed"]
                )
                save()
                status.setText(
                    "Componentes e mapa verificados. Homologação Windows/SAC pendente.\n"
                    + " · ".join(f"{k} {v}" for k, v in report["versions"].items())
                    + f"\nEvidência: {output}"
                    if report["checks_passed"]
                    else "Verificação falhou. Consulte as evidências."
                )
                exit_code = 0 if report["checks_passed"] else 1
                if args.smoke_report:
                    app.quit()
            except Exception as error:
                report["error_type"] = type(error).__name__
                report["checks_passed"] = False
                save()
                status.setText("Não foi possível verificar as evidências. Homologação pendente.")
                if args.smoke_report:
                    app.quit()

        web_map.readyChanged.connect(lambda: QTimer.singleShot(2200, complete))
        QTimer.singleShot(30000, complete)
        app.aboutToQuit.connect(complete)
        app.exec()
    except Exception as error:
        report["error_type"] = type(error).__name__
        report["failed_module"] = getattr(error, "name", None)
        report["error"] = (
            "Não foi possível carregar ou verificar os componentes. "
            "Não desative proteções do Windows."
        )
        try:
            from distribution.windows_evidence import collect

            names = [
                "_multiarray_umath",
                "shapely",
                "pyproj",
                "fiona",
                "PySide6",
                "QtWebEngineProcess",
                "AgroLinesPoC",
            ]
            report["evidence_after"] = collect(STARTED, names)
        except Exception:
            report["evidence_error"] = "Windows evidence unavailable"
        save()
        if not args.smoke_report and sys.platform == "win32":
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                None, report["error"] + f"\nEvidência: {output}", "AgroLines", 0x10
            )
    finally:
        if local_window:
            for project_window in local_window:
                project_window.close()
        if web_map:
            web_map.dispose()
        if window:
            window.close()
        if app:
            app.processEvents()
        save()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
