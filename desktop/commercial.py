"""Commercial shell reuses the offline GIS workspace, never collaboration clients."""

from datetime import UTC, datetime

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from core.licensing import Module
from core.local_projects import LocalProject
from desktop.local_projects import LocalProjectsWindow, LocalVertexDialog


class Completed(QObject):
    result = Signal(object, str)


class LicenseWork(QRunnable):
    def __init__(self, work):
        super().__init__()
        self.work = work
        self.signals = Completed()

    def run(self):
        try:
            self.signals.result.emit(self.work(), "")
        except Exception as exc:
            self.signals.result.emit(None, str(exc))


class CapturedPermission:
    """One already-started edit may save even if a network check changes entitlements."""

    def __init__(self, value):
        self.value = value

    def verify(self):
        return self.value


class CommercialWindow(LocalProjectsWindow):
    from pathlib import Path

    privacy_source = (
        Path(__file__).parent.parent / "docs/legal/commercial/politica-privacidade.html"
    )

    def __init__(self, manager):
        self.manager = manager
        super().__init__(manager)
        self.setWindowTitle("AgroLines · Projetos locais")
        toolbar = self.addToolBar("Licença")
        toolbar.setMovable(False)
        toolbar.addAction("Minha licença", self.license_dialog)
        toolbar.addAction("Exportar dados", self.export_data)
        self.license_status = QLabel()
        self.statusBar().addPermanentWidget(self.license_status)
        self.busy = False
        self.pending = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.background_check)
        self.timer.start(
            15 * 60 * 1000
        )  # Online opportunity, never an offline expiry/grace period.
        self.update_status()
        QTimer.singleShot(0, self.first_run)

    def first_run(self):
        if self.manager.verify().read_only:
            self.license_dialog()
        else:
            self.background_check()

    def update_status(self):
        state = self.manager.verify()
        try:
            value = self.manager.parsed() if self.manager.state.get("license") else None
        except ValueError:
            value = None
        suffix = ""
        if value:
            suffix = " · vence " + datetime.fromtimestamp(value["expires_at"], UTC).strftime(
                "%d/%m/%Y %H:%M UTC"
            )
        self.license_status.setToolTip(state.reason + suffix)
        self.license_status.setMaximumWidth(380)
        self.license_status.setText(
            "Licença ativa" + suffix
            if not state.read_only
            else "Licença pendente · recuperação de dados disponível"
        )

    def async_work(self, work, done=None):
        if self.busy:
            return
        self.busy = True
        task = LicenseWork(work)
        self.pending.append(task)

        def complete(value, error):
            self.busy = False
            self.pending.remove(task)
            self.update_status()
            if done:
                done(value, error)

        task.signals.result.connect(complete)
        QThreadPool.globalInstance().start(task)

    def background_check(self):
        if self.manager.state.get("credential"):
            self.async_work(self.manager.check)

    def license_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("AgroLines · Ativação e assinatura")
        dialog.resize(650, 530)
        layout = QVBoxLayout(dialog)
        status = QLabel(self.manager.verify().reason)
        status.setWordWrap(True)
        layout.addWidget(status)
        form = QFormLayout()
        email, key, label = QLineEdit(), QLineEdit(), QLineEdit("Meu computador")
        key.setEchoMode(QLineEdit.Password)
        form.addRow("E-mail do titular", email)
        form.addRow("Chave desta vaga", key)
        form.addRow("Nome do computador (sem dados pessoais)", label)
        layout.addLayout(form)
        info = QTextBrowser()
        info.setOpenExternalLinks(False)
        layout.addWidget(info)

        def details():
            try:
                value = self.manager.parsed()
            except ValueError:
                value = None
            text = "Primeira ativação exige HTTPS. Depois, uso offline até o vencimento.\n"
            if value:
                text += (
                    "Plano: "
                    + {"monthly": "Mensal", "annual": "Anual"}[value["plan"]]
                    + "\nVencimento: "
                    + datetime.fromtimestamp(value["expires_at"], UTC).isoformat()
                    + "\nSituação: "
                    + self.manager.verify().reason
                    + "\n"
                )
            for device in self.manager.state.get("devices", []):
                text += f"Vaga {device['slot']}: {device.get('label') or 'disponível'}\n"
            text += "\nFalha de rede preserva licença válida. Salvar trabalho em andamento, abrir, "
            text += "exportar e recuperar seus dados continuam disponíveis após vencimento.\n"
            text += "Suporte e privacidade: fabricio.grupodelatorre@gmail.com\n"
            text += "Não envie chaves, senhas ou projetos completos sem necessidade."
            info.setPlainText(text)

        def finished(value, error):
            status.setText(error or self.manager.verify().reason)
            details()

        def activate():
            values = email.text().strip(), key.text().strip(), label.text().strip()
            key.clear()
            self.async_work(lambda: self.manager.activate(*values), finished)

        for title, callback in (
            ("Ativar esta vaga", activate),
            ("Verificar licença agora", lambda: self.async_work(self.manager.check, finished)),
            ("Desativar este computador", lambda: self.deactivate(finished)),
        ):
            button = QPushButton(title)
            button.clicked.connect(callback)
            layout.addWidget(button)
        close = QDialogButtonBox(QDialogButtonBox.Close)
        close.rejected.connect(dialog.reject)
        layout.addWidget(close)
        details()
        dialog.exec()

    def deactivate(self, done):
        if (
            QMessageBox.question(
                self, "Desativar", "Desativar este computador? Seus projetos serão preservados."
            )
            == QMessageBox.Yes
        ):
            self.async_work(lambda: self.manager.check(deactivate=True), done)

    def create_project(self):
        if self.manager.verify().read_only:
            self.license_dialog()
            return
        super().create_project()

    def import_files(self):
        if self.manager.verify().read_only:
            self.license_dialog()
            return
        super().import_files()

    def edit(self):
        index = self.layers.currentRow()
        permission = self.manager.verify()
        if not permission.permits(Module.GEOMETRY):
            self.license_dialog()
            return
        if self.project and index >= 0:
            # Separate short-lived connection, permissions captured for this dialog only.
            project = LocalProject(self.project.path, CapturedPermission(permission))
            try:
                if (
                    LocalVertexDialog(project, self.features[index], self).exec()
                    == QDialog.Accepted
                ):
                    self.refresh()
            finally:
                project.close()

    def export_data(self):
        """Export canonical WGS84 GeoJSON already stored by the existing GIS engine."""
        if not self.project:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar dados locais", "", "GeoJSON (*.geojson)"
        )
        if not path:
            return

        def export():
            import json
            from pathlib import Path

            from core.offline_policy import require_local_path

            require_local_path(path)
            rows = self.project.features()
            value = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": row["geometry"],
                        "properties": {"name": row["name"], "revision": row["revision"]},
                    }
                    for row in rows
                ],
            }
            with Path(path).open("x", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, allow_nan=False)

        self.run(export)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
