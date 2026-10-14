"""Temporary numeric vertex edits; only explicit server save creates a revision."""

from copy import deepcopy

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.geography import inspect_polygon
from core.precision import VertexEditor
from desktop.client import ApiError
from desktop.ui import action, field, form_layout, label


class NumericVertexDialog(QDialog):
    def __init__(self, controller, feature):
        super().__init__(controller.window)
        self.controller = controller
        self.feature = feature
        self.properties = feature["properties"]
        farm = next(
            f
            for f in controller.window.farms
            if f["id"] == controller.window.context_property.currentData()
        )
        self.editor = VertexEditor(
            self.properties["original_geometry"],
            self.properties["source_crs"],
            farm.get("work_crs", "EPSG:32723"),
        )
        self.locations = [location for location, _ in self.editor.vertices()]
        self.saved = False
        self.busy = False
        self.invalidated = False
        self.setWindowTitle("Editar vértices numericamente")
        self.setMinimumWidth(420)
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        body = QVBoxLayout(content)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
        body.addWidget(label(self.properties["name"], "CardTitle"))
        body.addWidget(
            label(
                "Coordenadas em metros no SRC de trabalho. Edição temporária; "
                "exatidão centimétrica de campo não comprovada.",
                "Description",
            )
        )
        form_widget = QWidget()
        form = form_layout(form_widget)
        self.vertex = QSpinBox()
        self.vertex.setRange(1, len(self.locations))
        self.vertex.valueChanged.connect(self.populate)
        form.addRow(label("Vértice"), self.vertex)
        self.x = field(form, "X / Leste (m)")
        self.y = field(form, "Y / Norte (m)")
        self.distance = field(form, "Deslocamento (m)", "Ex.: 0,001")
        self.distance.setText("0.01")
        self.azimuth = field(form, "Azimute (°)", "0 = Norte; 90 = Leste")
        self.azimuth.setText("90")
        body.addWidget(form_widget)
        row = QHBoxLayout()
        self.apply_button = action("Aplicar coordenadas", self.apply, row, "check")
        self.move_button = action("Deslocar", self.move, row, "transfer")
        body.addLayout(row)
        row = QHBoxLayout()
        self.undo_button = action("Desfazer · Ctrl+Z", self.undo, row)
        self.redo_button = action("Refazer · Ctrl+Y", self.redo, row)
        body.addLayout(row)
        self.confirm_overlaps = QCheckBox("Autorizar sobreposições conferidas")
        body.addWidget(self.confirm_overlaps)
        self.status = label("Nenhuma alteração gravada.", "Hint")
        body.addWidget(self.status)
        row = QHBoxLayout()
        self.save_button = action("Salvar nova versão", self.save, row, "check", "primary")
        self.discard_button = action("Descartar", self.reject, row, "close")
        action("Cancelar", self.reject, row)
        outer.addLayout(row)
        available = QApplication.primaryScreen().availableGeometry()
        self.setMinimumHeight(260)
        self.resize(
            max(420, min(520, available.width() - 40)), max(260, min(600, available.height() - 40))
        )
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.undo)
        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redo_shortcut.activated.connect(self.redo)
        self.populate()

    def coordinate(self):
        location = self.locations[self.vertex.value() - 1]
        return location, self.editor._ring(location)[location[2]]

    def populate(self, *_):
        _, coordinate = self.coordinate()
        self.x.setText(format(coordinate[0], ".17g"))
        self.y.setText(format(coordinate[1], ".17g"))
        self.undo_button.setEnabled(bool(self.editor.undo_stack))
        self.redo_button.setEnabled(bool(self.editor.redo_stack))

    @staticmethod
    def number(widget):
        return float(widget.text().strip().replace(",", "."))

    def apply(self):
        if self.busy:
            return
        try:
            location, _ = self.coordinate()
            self.editor.set_vertex(location, self.number(self.x), self.number(self.y))
            self.populate()
            self.status.setText("Alteração temporária; salve para criar uma nova versão.")
        except (ValueError, IndexError) as exc:
            self.status.setText(str(exc))

    def move(self):
        if self.busy:
            return
        try:
            location, _ = self.coordinate()
            self.editor.move_vertex(location, self.number(self.distance), self.number(self.azimuth))
            self.populate()
            self.status.setText("Deslocamento aplicado matematicamente, sem usar pixels.")
        except (ValueError, IndexError) as exc:
            self.status.setText(str(exc))

    def undo(self):
        if not self.busy:
            self.editor.undo()
            self.populate()

    def redo(self):
        if not self.busy:
            self.editor.redo()
            self.populate()

    def save(self):
        if self.invalidated:
            return
        if self.busy or self.controller.window.job is not None:
            self.status.setText("Aguarde a solicitação em andamento.")
            return
        if not self.controller.window.online:
            self.status.setText("Salvar exige conexão com o servidor.")
            return
        source = deepcopy(self.editor.source_geometry())
        farm_id = self.controller.window.context_property.currentData()
        plot_id = self.feature["id"]
        self.busy = True
        self.save_button.setEnabled(False)
        self.status.setText("Validando precisão, topologia e versão no servidor…")
        acknowledge_overlaps = self.confirm_overlaps.isChecked()

        def submit():
            try:
                result = inspect_polygon(
                    source,
                    self.editor.source_crs,
                    work_crs=self.editor.work_crs,
                    metadata=(self.properties.get("precision_report") or {}).get(
                        "source_metadata", {}
                    ),
                )
            except ValueError as exc:
                raise ApiError(str(exc)) from None
            body = {
                "name": self.properties["name"],
                "original_geometry": source,
                "source_crs": self.editor.source_crs,
                "geometry": result.geometry,
                "work_crs": self.editor.work_crs,
                "metadata": result.precision_report["source_metadata"],
                "attributes": self.properties["attributes"],
                "expected_revision": self.properties["revision"],
                "acknowledge_overlaps": acknowledge_overlaps,
            }
            return self.controller.window.client.request(
                "PUT", f"/farms/{farm_id}/plots/{plot_id}/geometry", body
            )

        def saved(_):
            self.busy = False
            self.saved = True
            self.accept()
            self.controller.refresh()

        def failed(error):
            self.busy = False
            self.save_button.setEnabled(True)
            self.status.setText(str(error))

        self.controller.window.call(submit, saved, on_error=failed)

    def reject(self):
        if self.busy:
            self.status.setText("Aguarde o resultado do salvamento antes de fechar.")
            return
        super().reject()

    def closeEvent(self, event):
        if self.busy:
            event.ignore()
        else:
            event.accept()

    def invalidate(self):
        self.invalidated = True
        self.x.clear()
        self.y.clear()
        self.editor = None
        super().reject()
