"""Capture four real Windows desktop views of the PR #10 offline application."""

import argparse
import hashlib
import json
import os
import platform
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

TITLES = {
    "01-tela-principal.png": "Projeto fictício, limite e três talhões no mapa vetorial local",
    "02-camadas-importadas.png": "Camadas realmente importadas de GeoJSON, SHP e GPKG",
    "03-edicao-de-vertices.png": "Diálogo real de edição, com coordenadas métricas numéricas",
    "04-projetos-e-backups.png": "Diálogo real de abertura de projetos e cópias de backup",
}


def capture(output, revision, configure_hosted_display=False):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "started_utc": datetime.now(UTC).isoformat(),
        "platform": platform.system(),
        "os_version": platform.version(),
        "source_revision": revision,
        "images": {},
        "completed": False,
        "synthetic_only": True,
        "store_installed": False,
        "sac_approved": False,
    }
    window = app = native = original_mode = None
    error = None
    try:
        if sys.platform != "win32":
            raise RuntimeError("Este ambiente não é Windows; nenhuma imagem será gerada.")
        if os.getenv("QT_QPA_PLATFORM", "windows") != "windows":
            raise RuntimeError("Capturas exigem QPA windows; offscreen/minimal não são aceitos.")
        from core.offline_policy import enforce, require_local_path

        enforce()
        require_local_path(output)
        from scripts.windows_screen_capture import NativeDesktop

        native = NativeDesktop()
        report["desktop"] = native.readiness()
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QIcon
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication

        import desktop.local_projects as local_ui
        from core.local_projects import LocalProject
        from scripts.store_demo import prepare

        app = QApplication(sys.argv[:1])
        if configure_hosted_display:
            original_mode, report["display_mode"] = native.configure_hosted_display()
            QTest.qWait(1000)
        app.setApplicationName("AgroLines")
        app.setWindowIcon(
            QIcon(str(Path("assets/branding/AgroLines_Arte_Caixa_1080x1080.png").resolve()))
        )
        project_path = prepare(output / "dados-ficticios")
        window = local_ui.LocalProjectsWindow()
        window.load(project_path)
        assert not window.remote_windows and window.map.imagery is None
        window.showFullScreen()
        window.raise_()
        window.activateWindow()
        handle = int(window.winId())
        deadline = time.monotonic() + 30
        while not window.map.is_ready:
            if time.monotonic() > deadline:
                raise RuntimeError("Qt WebEngine/Leaflet não concluíram a inicialização.")
            QTest.qWait(100)
        QTest.qWait(1500)

        def record(name):
            item = native.capture(handle, output / name)
            item["sha256"] = hashlib.sha256((output / name).read_bytes()).hexdigest()
            item["description"] = TITLES[name]
            report["images"][name] = item

        report["qt_webengine_ready"] = window.map.is_ready
        report["feature_count"] = len(window.project.features())
        assert report["feature_count"] == 4
        window.centralWidget().setSizes([400, max(window.width() - 400, 1)])
        QTest.qWait(500)
        record("01-tela-principal.png")
        window.layers.setCurrentRow(1)
        window.centralWidget().setSizes([400, max(window.width() - 400, 1)])
        feature = window.features[1]
        window.map.run("select", feature["id"])
        QTest.qWait(1000)
        record("02-camadas-importadas.png")
        errors = []

        def vertex_capture():
            dialog = app.activeModalWidget()
            try:
                if not isinstance(dialog, local_ui.LocalVertexDialog):
                    raise RuntimeError("Diálogo de vértices não está em execução.")
                dialog.x.setText(format(float(dialog.x.text()) + 0.001, ".17g"))
                dialog.apply()
                QTest.qWait(300)
                record("03-edicao-de-vertices.png")
                dialog.save()
            except Exception as exc:
                errors.append(str(exc))
                if dialog:
                    dialog.reject()

        QTimer.singleShot(1500, vertex_capture)
        window.edit()  # Actual application's modal dialog and save/refresh path.
        if errors:
            raise RuntimeError(errors[0])
        assert window.project.features()[1]["revision"] == 2
        backup = project_path.parent / "Backup-apos-edicao-ficticia.agrolines"
        window.project.backup(backup)
        restored = LocalProject.restore(
            backup, project_path.parent / "Restaurado-ficticio.agrolines"
        )
        try:
            assert restored.features()[1]["revision"] == 2
            report["history_revisions"] = len(restored.history(feature["id"]))
        finally:
            restored.close()
        report["backup_restored"] = True
        # Only choose the initial folder of the existing file picker. No new UI,
        # fake services, replacement dialog, or altered controls are introduced.
        original_directory = local_ui.project_directory
        local_ui.project_directory = lambda: project_path.parent

        def file_capture():
            dialog_handle = None
            try:
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    candidate, owner, title = native.foreground()
                    if owner == os.getpid() and candidate != handle and title == "Abrir projeto":
                        dialog_handle = candidate
                        time.sleep(2)
                        record("04-projetos-e-backups.png")
                        return
                    time.sleep(0.1)
                raise RuntimeError("Diálogo nativo de abertura não observável.")
            except Exception as exc:
                errors.append(str(exc))
            finally:
                if dialog_handle:
                    native.user.PostMessageW(
                        dialog_handle, 0x0010, 0, 0
                    )  # Cancel only this dialog.
                else:
                    current, owner, title = native.foreground()
                    if owner == os.getpid() and title == "Abrir projeto":
                        native.user.PostMessageW(current, 0x0010, 0, 0)

        worker = threading.Thread(target=file_capture, daemon=True)
        worker.start()
        try:
            window.open_project()  # Native modal event loop does not dispatch QTimers on Windows.
        finally:
            local_ui.project_directory = original_directory
        worker.join(timeout=5)
        if worker.is_alive() or errors:
            raise RuntimeError(errors[0] if errors else "Captura nativa não terminou.")
        assert set(report["images"]) == set(TITLES)
        report["completed"] = True
        report["manual_visual_review_required"] = True
    except Exception as exc:
        error = str(exc)
        report["unavailable_reason"] = error
        # Never deliver a partial or unverified set as Store screenshots.
        for name in TITLES:
            (output / name).unlink(missing_ok=True)
        report["images"] = {}
    finally:
        if window:
            window.close()
        if app:
            app.processEvents()
        if original_mode is not None:
            report["display_mode"]["restored"] = native.restore_display(original_mode)
        (output / "capture-evidence.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        lines = [
            "# Capturas reais da edição offline",
            "",
            "Estado: " + ("quatro capturas produzidas" if report["completed"] else "indisponível"),
            "",
            "Dados exclusivamente sintéticos. Sem instalação de MSIX ou comprovação SAC.",
            "",
        ]
        lines.extend(f"- `{name}`: {description}." for name, description in TITLES.items())
        lines += [
            "",
            "Evidência: capture-evidence.json. Método: pixels do desktop Windows via GDI;",
            "nenhum QWidget.grab, render offscreen, composição, redimensionamento de PNG ou IA.",
            "Revisão humana de legibilidade, recortes, idiomas e sobreposições ainda obrigatória.",
        ]
        if error:
            lines += ["", "Nenhum PNG entregue. Motivo: " + error]
        (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if report["completed"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--revision", default="não informado")
    parser.add_argument("--configure-hosted-display", action="store_true")
    args = parser.parse_args()
    raise SystemExit(capture(args.output, args.revision, args.configure_hosted_display))
