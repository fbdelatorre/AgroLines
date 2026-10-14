"""Desktop map workflow, separate from rendering and geometry processing."""

import json
from urllib.parse import urlencode

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QSlider,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.imports import import_polygons
from desktop.client import ApiError
from desktop.gis_map import WebMap
from desktop.icons import icon
from desktop.ui import RecordTable, action, input_field, label


class GeographyController(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.map = WebMap()
        self.map.featureSelected.connect(self.identify)
        self.map.readyChanged.connect(self.update_layers)
        self.map.set_online(window.online)
        self.preview = None
        self.features = []
        self.loaded_farm = None
        self.scope_generation = 0
        self.disposed = False
        self.editor_dialog = None
        self.build_panels()
        window.workspace.set_map_component(self.map)

    def build_panels(self):
        workspace = self.window.workspace
        layers = QWidget()
        body = QVBoxLayout(layers)
        body.setContentsMargins(10, 8, 10, 8)
        row = QHBoxLayout()
        action("Importar", self.choose_files, row, "plus", "primary")
        refresh = QToolButton()
        refresh.setIcon(icon("refresh"))
        refresh.setToolTip("Atualizar geometrias autorizadas")
        refresh.clicked.connect(self.refresh)
        row.addWidget(refresh)
        body.addLayout(row)
        self.layer_list = QListWidget()
        self.layer_list.setDragDropMode(QListWidget.InternalMove)
        self.layer_list.itemChanged.connect(self.update_layers)
        self.layer_list.model().rowsMoved.connect(self.update_layers)
        self.layer_list.currentRowChanged.connect(self.layer_selected)
        body.addWidget(self.layer_list, 1)
        body.addWidget(label("Visibilidade · arraste para ordenar", "Hint"))
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(100)
        self.opacity.setAccessibleName("Opacidade da camada selecionada")
        self.opacity.valueChanged.connect(self.style_selected)
        body.addWidget(label("Opacidade", "Hint"))
        body.addWidget(self.opacity)
        self.color = QComboBox()
        for title, color in (("Verde", "#39b980"), ("Amarelo", "#eac65b"), ("Azul", "#59afe0")):
            self.color.addItem(title, color)
        self.color.currentIndexChanged.connect(self.style_selected)
        body.addWidget(self.color)
        workspace.layers.widget().setWidget(layers)
        old_parameters = workspace.parameters.widget().takeWidget()
        tabs = QTabWidget()
        inspector = QWidget()
        column = QVBoxLayout(inspector)
        column.setContentsMargins(10, 8, 10, 8)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText(
            "Selecione um talhão no mapa para consultar seus atributos."
        )
        column.addWidget(self.details)
        self.edit_button = action(
            "Editar vértices numericamente", self.edit_numeric, column, "edit"
        )
        self.edit_button.setEnabled(False)
        self.fit_button = action(
            "Enquadrar seleção", lambda: self.map.run("fit", self.map.current_id), column, "frame"
        )
        self.fit_button.setEnabled(False)
        tabs.addTab(inspector, "Objeto")
        tabs.addTab(old_parameters, "Planejamento futuro")
        workspace.parameters.widget().setWidget(tabs)
        original_context = workspace.context.widget().takeWidget()
        context_tabs = QTabWidget()
        context_tabs.addTab(original_context, "Acesso")
        preview_panel = QWidget()
        body = QVBoxLayout(preview_panel)
        body.setContentsMargins(10, 8, 10, 8)
        self.preview_status = label("Nenhuma importação pendente.", "Hint")
        body.addWidget(self.preview_status)
        self.preview_table = RecordTable(["Talhão", "Área (ha)", "Perímetro (m)"])
        self.preview_table.setMinimumHeight(65)
        self.preview_table.currentRowChanged.connect(self.preview_selected)
        body.addWidget(self.preview_table, 1)
        self.confirm_overlaps = QCheckBox("Autorizar sobreposições conferidas")
        controls = QHBoxLayout()
        controls.addWidget(self.confirm_overlaps)
        self.save_button = action("Salvar importação", self.save, controls, "check", "primary")
        self.save_button.setEnabled(False)
        action("Descartar prévia", self.discard, controls, "close")
        body.addLayout(controls)
        context_tabs.addTab(preview_panel, "Prévia de importação")
        workspace.context.widget().setWidget(context_tabs)
        self.context_tabs = context_tabs
        self.import_options = QWidget()
        options = QVBoxLayout(self.import_options)
        options.setContentsMargins(0, 0, 0, 0)
        options.addWidget(label("SRC de origem (se ausente ou incorreto)", "Hint"))
        self.source_crs = input_field("Ex.: EPSG:31983")
        options.addWidget(self.source_crs)
        options.addWidget(label("SRC de trabalho da propriedade", "Hint"))
        self.work_crs = input_field("EPSG:32723")
        options.addWidget(self.work_crs)
        self.configure_button = action("Salvar SRC", self.configure_crs, options, "check")
        self.repair = QCheckBox("Corrigir inválidas (GEOS)")
        self.repair.setToolTip(
            "A prévia mostra a correção antes de gravar; originais são preservados."
        )
        options.addWidget(self.repair)
        body_layers = layers.layout()
        body_layers.insertWidget(1, self.import_options)

    def configure_crs(self):
        if self.preview:
            self.window.notice("Salve ou descarte a prévia antes de alterar o SRC.")
            return
        farm_id = self.window.context_property.currentData()
        value = self.work_crs.text().strip()
        if not farm_id:
            return

        def saved(result):
            for farm in self.window.farms:
                if farm["id"] == farm_id:
                    farm["work_crs"] = result["work_crs"]
            self.refresh()
            self.window.notice("SRC de trabalho atualizado; versões existentes preservadas.")

        self.window.call(
            lambda: self.window.client.request(
                "PATCH", f"/farms/{farm_id}/geography-settings", {"work_crs": value}
            ),
            saved,
        )

    def refresh(self, *_):
        if self.disposed or not self.window.workspace.map_active:
            return
        farm_id = self.window.context_property.currentData()
        if not farm_id:
            self.clear()
            return
        season_id = self.window.context_season.currentData()
        generation = self.scope_generation = self.scope_generation + 1
        self.map.set_collection({"type": "FeatureCollection", "features": []})
        self.details.clear()
        self.fit_button.setEnabled(False)
        farm = next(f for f in self.window.farms if f["id"] == farm_id)
        self.work_crs.setText(farm.get("work_crs", "EPSG:32723"))
        self.map.set_work_crs(self.work_crs.text())
        self.edit_button.setEnabled(False)
        permissions = farm["permissions"]
        self.configure_button.setEnabled(
            any("edit" in p["actions"] and p.get("season_id") is None for p in permissions)
        )
        whole = any(p.get("season_id") is None for p in permissions)

        def fetch():
            seasons = self.window.client.request("GET", f"/farms/{farm_id}/seasons")
            selected = next((s["id"] for s in seasons if s["id"] == season_id), None)
            if not whole and selected is None and seasons:
                selected = seasons[0]["id"]
            query = {}
            if selected:
                query["season_id"] = selected
                whole_season = whole or any(
                    p.get("season_id") == selected and p.get("operation_id") is None
                    for p in permissions
                )
                if not whole_season:
                    operation = next(
                        (
                            p.get("operation_id")
                            for p in permissions
                            if p.get("season_id") == selected and p.get("operation_id")
                        ),
                        None,
                    )
                    if operation:
                        query["operation_id"] = operation
            if not whole and not query:
                collection = {"type": "FeatureCollection", "features": []}
            else:
                suffix = "?" + urlencode(query) if query else ""
                collection = self.window.client.request("GET", f"/farms/{farm_id}/plots" + suffix)
            return seasons, selected, collection

        def loaded(result):
            if (
                generation != self.scope_generation
                or self.window.context_property.currentData() != farm_id
            ):
                return
            seasons, selected, collection = result
            selector = self.window.context_season
            selector.blockSignals(True)
            selector.clear()
            if whole:
                selector.addItem("Todas as safras", None)
            for season in seasons:
                selector.addItem(season["name"], season["id"])
            selector.setCurrentIndex(max(0, selector.findData(selected)))
            selector.blockSignals(False)
            self.features = collection["features"]
            self.map.set_collection(self.current_collection(), self.loaded_farm != farm_id)
            self.loaded_farm = farm_id
            self.fill_layers()
            plot_selector = self.window.context_plot
            plot_selector.blockSignals(True)
            plot_selector.clear()
            plot_selector.addItem("Todos os talhões", None)
            for feature in self.features:
                plot_selector.addItem(feature["properties"]["name"], feature["id"])
            plot_selector.setCurrentIndex(0)
            plot_selector.blockSignals(False)
            self.window.notice(f"{len(self.features)} talhão(ões) autorizado(s) carregado(s).")

        self.window.call(fetch, loaded, defer=True)

    def fill_layers(self):
        self.layer_list.blockSignals(True)
        self.layer_list.clear()
        for feature in self.map.collection["features"]:
            item = QListWidgetItem(feature["properties"]["name"])
            item.setFlags(
                item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            )
            item.setCheckState(Qt.Checked)
            item.setData(
                Qt.UserRole,
                {
                    "id": str(feature["id"]),
                    "visible": True,
                    "color": "#eac65b" if feature["properties"].get("preview") else "#39b980",
                    "opacity": 1,
                },
            )
            self.layer_list.addItem(item)
        self.layer_list.blockSignals(False)
        self.update_layers()

    def update_layers(self, *_):
        rows = []
        for index in range(self.layer_list.count()):
            item = self.layer_list.item(index)
            data = item.data(Qt.UserRole)
            rows.append({**data, "visible": item.checkState() == Qt.Checked})
        self.map.run("layers", rows)

    def layer_selected(self, row):
        item = self.layer_list.item(row) if row >= 0 else None
        if not item:
            return
        data = item.data(Qt.UserRole)
        self.opacity.blockSignals(True)
        self.color.blockSignals(True)
        self.opacity.setValue(round(data["opacity"] * 100))
        self.color.setCurrentIndex(max(0, self.color.findData(data["color"])))
        self.opacity.blockSignals(False)
        self.color.blockSignals(False)
        self.map.run("select", data["id"])

    def style_selected(self, *_):
        item = self.layer_list.currentItem()
        if item:
            self.layer_list.blockSignals(True)
            item.setData(
                Qt.UserRole,
                {
                    **item.data(Qt.UserRole),
                    "opacity": self.opacity.value() / 100,
                    "color": self.color.currentData(),
                },
            )
            self.layer_list.blockSignals(False)
            self.update_layers()

    def identify(self, feature):
        properties = feature["properties"]
        self.details.setPlainText(
            f"{properties['name']}\n\n"
            f"Área: {properties['area_m2'] / 10000:.4f} ha\n"
            f"Perímetro: {properties['perimeter_m']:.3f} m\n"
            f"SRC de cálculo: {properties['metric_crs']}\n"
            + (
                "\nPrévia local · ainda não gravada\n"
                if properties.get("preview")
                else f"\nVersão: {properties['revision']}\n"
            )
            + "\nAtributos:\n"
            + json.dumps(properties.get("attributes", {}), ensure_ascii=False, indent=2)
        )
        self.fit_button.setEnabled(True)
        farm = next(
            (f for f in self.window.farms if f["id"] == self.window.context_property.currentData()),
            None,
        )
        editable = farm and any(
            "edit" in p["actions"] and p.get("season_id") is None for p in farm["permissions"]
        )
        self.edit_button.setEnabled(bool(editable and not properties.get("preview")))
        report = properties.get("precision_report")
        if report:
            accuracy = report.get("display_transform_accuracy_m")
            summary = (
                "\nPrecisão de campo: não comprovada.\n"
                f"Datum original: {report.get('datum') or 'não informado'}\n"
                f"Consistência numérica: {report['roundtrip_consistency_m']:.6g} m\n"
                "Incerteza da transformação de visualização: "
                f"{accuracy if accuracy is not None else 'desconhecida'} m\n"
                "Distorção estimada da malha: "
                f"{report['estimated_grid_distortion_per_km_m']:.6f} m/km\n"
                f"Área geodésica: {report['geodesic_area_m2'] / 10000:.4f} ha\n"
                f"Perímetro geodésico: {report['geodesic_perimeter_m']:.3f} m\n"
                "Métricas da malha e geodésicas não incluem correção de altura do terreno."
            )
        else:
            summary = "\nDados legados: relatório de precisão ainda não disponível."
        self.details.setPlainText(self.details.toPlainText() + summary)
        from PySide6.QtGui import QTextCursor

        self.details.moveCursor(QTextCursor.Start)

    def choose_files(self):
        if self.preview:
            self.window.notice("Salve ou descarte a prévia atual antes de importar outro lote.")
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self.window,
            "Importar polígonos",
            "",
            "Dados geográficos (*.shp *.gpkg *.kml *.kmz *.geojson *.json)",
        )
        if paths:
            self.import_files(paths)

    def import_files(self, paths):
        farm_id = self.window.context_property.currentData()
        if not farm_id:
            self.window.notice("Selecione uma propriedade para preparar a importação.")
            return
        source_crs = self.source_crs.text().strip() or None
        repair = self.repair.isChecked()
        work_crs = self.work_crs.text().strip() or None

        def parse():
            try:
                return import_polygons(paths, source_crs, repair, work_crs)
            except Exception as exc:
                raise ApiError("Importação recusada: " + str(exc)) from None

        def loaded(preview):
            if self.window.context_property.currentData() != farm_id:
                return
            self.preview = preview
            self.preview_farm = farm_id
            self.preview_table.replace(
                [
                    (str(i), [p["name"], f"{p['area_m2'] / 10000:.4f}", f"{p['perimeter_m']:.3f}"])
                    for i, p in enumerate(preview.plots)
                ]
            )
            self.preview_status.setText(
                f"{len(preview.plots)} polígono(s) · {len(preview.warnings)} alerta(s). "
                "Confira a prévia e a propriedade antes de salvar."
            )
            import html

            self.preview_status.setToolTip(
                "<qt>" + html.escape("\n".join(preview.warnings)) + "</qt>"
            )
            self.map.set_collection(self.current_collection(), True)
            self.fill_layers()
            self.save_button.setEnabled(True)
            self.context_tabs.setCurrentIndex(1)
            self.window.workspace.toggles["context"].setChecked(True)
            self.window.workspace.context.show()
            self.window.workspace.resizeDocks([self.window.workspace.context], [205], Qt.Vertical)
            self.window.notice("Prévia local preparada; nenhum talhão foi gravado.")

        self.window.call(parse, loaded, protected=False)

    def save(self):
        if not self.preview or self.preview_farm != self.window.context_property.currentData():
            return
        farm_id = self.preview_farm
        payload = self.preview.payload(self.confirm_overlaps.isChecked())

        def saved(result):
            self.discard()
            self.refresh()
            self.window.notice(
                f"{len(result['created'])} talhão(ões) salvo(s); "
                f"{len(result['duplicates'])} duplicado(s) ignorado(s)."
            )

        self.window.call(
            lambda: self.window.client.request("POST", f"/farms/{farm_id}/plots/import", payload),
            saved,
        )

    def discard(self):
        self.preview = None
        self.preview_table.clear()
        self.preview_status.setText("Nenhuma importação pendente.")
        self.confirm_overlaps.setChecked(False)
        self.save_button.setEnabled(False)
        self.map.set_collection({"type": "FeatureCollection", "features": self.features})
        self.fill_layers()

    def clear(self):
        self.scope_generation += 1
        if self.editor_dialog:
            self.editor_dialog.invalidate()
        self.features = []
        self.loaded_farm = None
        self.map.clear()
        self.layer_list.clear()
        self.details.clear()
        self.fit_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.discard()

    def dispose(self):
        self.disposed = True
        self.map.dispose()

    def current_collection(self):
        previews = []
        if self.preview:
            for index, p in enumerate(self.preview.plots):
                properties = {
                    key: p[key]
                    for key in ("name", "area_m2", "perimeter_m", "metric_crs", "attributes")
                }
                previews.append(
                    {
                        "type": "Feature",
                        "id": f"preview-{index}",
                        "geometry": p["geometry"],
                        "properties": {**properties, "preview": True},
                    }
                )
        return {"type": "FeatureCollection", "features": self.features + previews}

    def pending_choice(self):
        box = QMessageBox(self.window)
        box.setWindowTitle("Importação ainda não salva")
        box.setTextFormat(Qt.PlainText)
        box.setText("Existe uma prévia local. Salve, descarte ou cancele para continuar.")
        box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        box.setDefaultButton(QMessageBox.Cancel)
        box.button(QMessageBox.Save).setText("Salvar")
        box.button(QMessageBox.Discard).setText("Descartar")
        box.button(QMessageBox.Cancel).setText("Cancelar")
        return box.exec()

    def allow_context_change(self, farm_id):
        if not self.preview or farm_id == self.preview_farm:
            return True
        choice = self.pending_choice()
        if choice == QMessageBox.Discard:
            self.discard()
            return True
        selector = self.window.context_property
        selector.blockSignals(True)
        selector.setCurrentIndex(selector.findData(self.preview_farm))
        selector.blockSignals(False)
        if choice == QMessageBox.Save:
            self.save()
        return False

    def allow_close(self):
        if not self.preview:
            return True
        choice = self.pending_choice()
        if choice == QMessageBox.Discard:
            self.discard()
            return True
        if choice == QMessageBox.Save:
            self.save()
        return False

    def preview_selected(self, row):
        if self.preview and row >= 0:
            self.map.run("select", f"preview-{row}")

    def edit_numeric(self):
        feature = next((f for f in self.features if f["id"] == self.map.current_id), None)
        if feature is None or self.preview:
            self.window.notice("Salve/descarte a prévia e selecione um talhão antes de editar.")
            return
        from desktop.vertex_editor import NumericVertexDialog

        try:
            dialog = NumericVertexDialog(self, feature)
        except ValueError as exc:
            self.window.notice(str(exc))
            return
        self.editor_dialog = dialog
        dialog.exec()
        self.editor_dialog = None
