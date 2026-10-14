"""Offline project workspace: deliberately never constructs an API client."""

from pathlib import Path

from pyproj import CRS
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
)

from core.local_projects import LocalProject
from core.offline_policy import is_offline_only, require_local_path, require_remote
from core.precision import VertexEditor
from desktop.gis_map import WebMap
from desktop.storage import project_directory
from desktop.ui import THEME


class LocalVertexDialog(QDialog):
    def __init__(self, project, feature, parent=None):
        super().__init__(parent)
        self.project, self.feature = project, feature
        self.editor = VertexEditor(
            feature["original_geometry"], feature["source_crs"], project.work_crs
        )
        self.locations = [location for location, _ in self.editor.vertices()]
        self.setWindowTitle("Vértices · coordenadas métricas")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.vertex = QSpinBox()
        self.vertex.setRange(1, len(self.locations))
        self.x, self.y = QLineEdit(), QLineEdit()
        form.addRow("Vértice", self.vertex)
        form.addRow("Leste (m)", self.x)
        form.addRow("Norte (m)", self.y)
        layout.addLayout(form)
        self.status = QLabel("Alterações temporárias. Salvar cria uma nova versão local.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        for text, callback in (
            ("Aplicar", self.apply),
            ("Desfazer", self.undo),
            ("Refazer", self.redo),
        ):
            button = QPushButton(text)
            button.clicked.connect(callback)
            layout.addWidget(button)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.vertex.valueChanged.connect(self.populate)
        self.populate()

    def populate(self):
        coordinate = dict(self.editor.vertices())[self.locations[self.vertex.value() - 1]]
        self.x.setText(format(coordinate[0], ".17g"))
        self.y.setText(format(coordinate[1], ".17g"))

    def apply(self):
        try:
            self.editor.set_vertex(
                self.locations[self.vertex.value() - 1],
                float(self.x.text().replace(",", ".")),
                float(self.y.text().replace(",", ".")),
            )
            self.populate()
            self.status.setText("Alteração temporária aplicada.")
        except ValueError as exc:
            self.status.setText(str(exc))

    def undo(self):
        self.editor.undo()
        self.populate()

    def redo(self):
        self.editor.redo()
        self.populate()

    def save(self):
        try:
            self.project.save_geometry(
                self.feature["id"], self.editor.source_geometry(), self.feature["revision"]
            )
            self.accept()
        except (ValueError, PermissionError) as exc:
            self.status.setText(str(exc))


class LocalProjectsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = None
        self._closed = False
        self.setWindowTitle("AgroLines · Projetos locais")
        self.resize(1100, 750)
        self.setStyleSheet(THEME)
        toolbar = self.addToolBar("Projeto local")
        toolbar.setMovable(False)
        if not is_offline_only():
            toolbar.addAction("Colaboração online", self.open_remote)
        if is_offline_only():
            toolbar.addAction("Privacidade", self.show_privacy)
        self.remote_windows = []
        for title, callback in (
            ("Novo", self.create_project),
            ("Abrir", self.open_project),
            ("Importar", self.import_files),
            ("Editar vértices", self.edit),
            ("Backup", self.backup),
            ("Restaurar", self.restore),
        ):
            toolbar.addAction(title, callback)
        self.layers = QListWidget()
        self.map = WebMap(offline=True)
        self.map.set_online(False)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.layers)
        splitter.addWidget(self.map)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 880])
        self.setCentralWidget(splitter)
        self.statusBar().showMessage(
            "Offline · Abra ou crie um projeto. Sincronização não habilitada."
        )

    def show_privacy(self):
        bundled = Path(__file__).parent / "privacy_assets/politica-privacidade.html"
        source = Path(__file__).parent.parent / "docs/privacy/offline/politica-privacidade.html"
        content = bundled if bundled.is_file() else source
        dialog = QDialog(self)
        dialog.setWindowTitle("Privacidade · AgroLines offline")
        dialog.resize(760, 600)
        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setOpenLinks(False)
        browser.setHtml(content.read_text(encoding="utf-8"))
        layout.addWidget(browser)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def open_remote(self):
        require_remote()

        def open_window():
            from desktop.main import MainWindow

            window = MainWindow()
            self.remote_windows.append(window)
            window.show()

        self.run(open_window)

    def run(self, callback):
        try:
            callback()
        except Exception as exc:
            QMessageBox.warning(self, "Projeto local", str(exc))

    def load(self, path):
        require_local_path(path)
        project = LocalProject(path)
        if self.project:
            self.project.close()
        self.project = project
        self.refresh()

    def refresh(self):
        self.features = self.project.features()
        self.layers.clear()
        for feature in self.features:
            self.layers.addItem(f"{feature['name']} · versão {feature['revision']}")
        self.map.set_work_crs(CRS.from_user_input(self.project.work_crs).to_string())
        self.map.set_collection(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": f["id"],
                        "geometry": f["geometry"],
                        "properties": {"name": f["name"]},
                    }
                    for f in self.features
                ],
            },
            fit=True,
        )
        self.statusBar().showMessage(f"Offline · {self.project.name} · dados gravados localmente")

    def create_project(self):
        name, ok = QInputDialog.getText(self, "Novo projeto", "Nome")
        if not ok:
            return
        crs, ok = QInputDialog.getText(
            self, "SRC de trabalho", "SRC projetado em metros", text="EPSG:32723"
        )
        if not ok:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Criar projeto", str(project_directory()), "AgroLines (*.agrolines)"
        )
        if path:

            def create():
                project = LocalProject.create(path, name, crs)
                project.close()
                self.load(path)

            self.run(create)

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir projeto", str(project_directory()), "AgroLines (*.agrolines)"
        )
        if path:
            self.run(lambda: self.load(path))

    def import_files(self):
        if not self.project:
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Importar polígonos", "", "Vetores (*.shp *.gpkg *.kml *.kmz *.geojson)"
        )
        if not paths:
            return
        crs, ok = QInputDialog.getText(
            self, "SRC de origem", "Vazio usa o SRC informado no arquivo"
        )
        if not ok:
            return

        def perform():
            try:
                self.project.import_files(paths, crs or None)
            except ValueError as exc:
                if not str(exc).startswith("Confirme os avisos"):
                    raise
                if QMessageBox.question(self, "Avisos da importação", str(exc)) != QMessageBox.Yes:
                    return
                self.project.import_files(paths, crs or None, acknowledge_warnings=True)
            self.refresh()

        self.run(perform)

    def edit(self):
        index = self.layers.currentRow()
        if self.project and index >= 0:
            dialog = LocalVertexDialog(self.project, self.features[index], self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh()

    def backup(self):
        if self.project:
            path, _ = QFileDialog.getSaveFileName(
                self, "Backup", str(project_directory()), "AgroLines (*.agrolines)"
            )
            if path:
                self.run(lambda: self.project.backup(path))

    def restore(self):
        source, _ = QFileDialog.getOpenFileName(
            self, "Escolher backup", str(project_directory()), "AgroLines (*.agrolines)"
        )
        if not source:
            return
        target, _ = QFileDialog.getSaveFileName(
            self, "Restaurar em novo arquivo", str(project_directory()), "AgroLines (*.agrolines)"
        )
        if target:

            def restore():
                restored = LocalProject.restore(source, target)
                restored.close()
                self.load(target)

            self.run(restore)

    def closeEvent(self, event):
        if self._closed:
            event.accept()
            return
        self._closed = True
        for window in self.remote_windows:
            window.close()
        self.map.dispose()
        if self.project:
            self.project.close()
        event.accept()
