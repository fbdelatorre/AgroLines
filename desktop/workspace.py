"""Dockable visual shell; deliberately contains no GIS engine or imagery provider."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from desktop.icons import icon
from desktop.labels import ROLE_NAMES, scope_text
from desktop.ui import RecordTable, action, form_layout, label


class MapViewport(QFrame):
    """Replaceable central component, not a pretend map or licensed basemap."""

    def __init__(self):
        super().__init__()
        self.setObjectName("MapViewport")
        self.setMinimumSize(180, 140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body = QVBoxLayout(self)
        body.setContentsMargins(12, 12, 12, 12)
        tools = QToolBar("Ferramentas cartográficas")
        tools.setMovable(False)
        tools.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        for title, image in (
            ("Selecionar", "select"),
            ("Desenhar", "edit"),
            ("Editar", "edit"),
            ("Medir", "measure"),
            ("Curvas", "lines"),
            ("Paralelas", "layers"),
            ("Ampliar", "plus"),
            ("Reduzir", "minus"),
            ("Enquadrar", "frame"),
        ):
            tool = tools.addAction(icon(image), title)
            tool.setToolTip(title + " — não implementado")
            tool.setEnabled(False)
        body.addWidget(tools)
        body.addWidget(label("Ferramentas cartográficas · etapa futura", "Hint"))
        body.addStretch(2)
        mark = label("Mapa", "MapTitle")
        mark.setAlignment(Qt.AlignCenter)
        body.addWidget(mark)
        description = label(
            "Visualização cartográfica ainda não implementada.\n"
            "Esta área está reservada para o mapa e suas camadas.",
            "Description",
        )
        description.setAlignment(Qt.AlignCenter)
        body.addWidget(description)
        body.addStretch(2)
        body.addWidget(label("Sem imagem, geometria ou sistema de coordenadas carregado.", "Hint"))


class VisualWorkspace(QMainWindow):
    """Nested dock host keeps navigation outside the GIS panel layout.

    Future map renderers replace map_viewport through set_map_component(). Forms
    continue to use the central page stack without spending space on empty docks.
    """

    openProperty = Signal(str)

    def __init__(self, pages):
        super().__init__()
        self.setObjectName("VisualWorkspace")
        self.setDockOptions(QMainWindow.AllowNestedDocks)
        self.setCentralWidget(pages)
        self.map_viewport = MapViewport()
        self.map_index = pages.addWidget(self.map_viewport)
        self.map_active = False
        self.compact = False
        self.context_farm = None
        self.panel_visibility = {"layers": True, "parameters": True, "context": True}
        self.compact_visibility = {name: False for name in self.panel_visibility}
        self.docks = {}
        self.toggles = {}
        self.layers = self._dock("layers", "Camadas", Qt.LeftDockWidgetArea, self._layers())
        self.parameters = self._dock(
            "parameters", "Parâmetros", Qt.RightDockWidgetArea, self._parameters()
        )
        self.context = self._dock(
            "context", "Informações da propriedade", Qt.BottomDockWidgetArea, self._context()
        )
        # Horizontal docks stay narrow; the replaceable map receives the surplus.
        self.resizeDocks([self.layers, self.parameters], [190, 245], Qt.Horizontal)
        self.resizeDocks([self.context], [145], Qt.Vertical)
        for dock in self.docks.values():
            dock.hide()

    def _dock(self, name, title, area, content):
        dock = QDockWidget(title, self)
        dock.setObjectName("Panel_" + name)
        dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumSize(140, 70)
        scroll.setWidget(content)
        dock.setWidget(scroll)
        self.addDockWidget(area, dock)
        self.docks[name] = dock
        toggle = dock.toggleViewAction()
        toggle.setText(title)
        toggle.setIcon(
            icon({"layers": "layers", "parameters": "settings", "context": "farm"}[name])
        )
        toggle.triggered.connect(lambda visible, key=name: self._remember(key, visible))
        dock.visibilityChanged.connect(lambda visible, key=name: self._visibility(key, visible))
        self.toggles[name] = toggle
        return dock

    def _remember(self, name, visible):
        if self.map_active:
            preferences = self.compact_visibility if self.compact else self.panel_visibility
            preferences[name] = visible

    def _visibility(self, name, visible):
        # Closing a dock and using its toolbar toggle share the same preference.
        if self.map_active and self.docks[name].isHidden():
            preferences = self.compact_visibility if self.compact else self.panel_visibility
            preferences[name] = False

    def _layers(self):
        panel = QFrame()
        body = QVBoxLayout(panel)
        body.setContentsMargins(12, 10, 12, 10)
        body.addWidget(label("Em desenvolvimento", "Unavailable"))
        body.addWidget(label("Nenhuma camada cartográfica carregada.", "Description"))
        for group, description in (
            ("Limites", "Propriedades e talhões"),
            ("Linhas", "Curvas e linhas operacionais"),
            ("Imagens", "Fontes sob licença adequada"),
        ):
            body.addWidget(label(group, "PanelHeading"))
            body.addWidget(label(description + " · etapa futura", "Hint"))
        body.addStretch()
        return panel

    def _parameters(self):
        panel = QFrame()
        body = QVBoxLayout(panel)
        body.setContentsMargins(10, 10, 10, 10)
        tabs = QTabWidget()
        tabs.setObjectName("ParameterTabs")
        for title in ("Linhas operacionais", "Curvas de nível"):
            tab = QWidget()
            content = QVBoxLayout(tab)
            content.addWidget(label("Em desenvolvimento", "Unavailable"))
            content.addWidget(
                label(
                    "Os parâmetros geométricos serão disponibilizados com o motor GIS. "
                    "Nenhum cálculo está disponível nesta etapa.",
                    "Description",
                )
            )
            fields = QWidget()
            form = form_layout(fields)
            names = (
                ("Largura de trabalho (m)", "Azimute (°)", "Raio mínimo (m)")
                if title == "Linhas operacionais"
                else (
                    "Intervalo vertical (m)",
                    "Raio mínimo (m)",
                    "Desvio horizontal (m)",
                    "Variação vertical (m)",
                    "Comprimento mínimo (m)",
                    "Suavização",
                )
            )
            for name in names:
                control = QLineEdit()
                control.setPlaceholderText("—")
                control.setEnabled(False)
                control.setAccessibleName(name + " — não implementado")
                control.setToolTip("Parâmetro cartográfico ainda não implementado")
                control.setMinimumWidth(50)
                form.addRow(label(name), control)
            content.addWidget(fields)
            generate = QPushButton(
                "Gerar linhas" if title == "Linhas operacionais" else "Gerar curvas"
            )
            generate.setProperty("variant", "primary")
            generate.setEnabled(False)
            generate.setToolTip("Geração cartográfica ainda não implementada")
            content.addWidget(generate)
            content.addStretch()
            tabs.addTab(tab, title)
        body.addWidget(tabs, 1)
        body.addWidget(label("Visualização e métricas", "PanelHeading"))
        body.addWidget(label("Sem resultados cartográficos.", "Hint"))
        return panel

    def _context(self):
        panel = QFrame()
        body = QVBoxLayout(panel)
        body.setContentsMargins(10, 8, 10, 8)
        heading = QHBoxLayout()
        self.context_title = label("Selecione uma propriedade", "PanelHeading")
        heading.addWidget(self.context_title, 1)
        self.open_button = action("Abrir propriedade", self._open, heading, "farm")
        self.open_button.setEnabled(False)
        body.addLayout(heading)
        self.context_table = RecordTable(["Perfil", "Escopo autorizado"])
        self.context_table.setMinimumHeight(65)
        body.addWidget(self.context_table)
        return panel

    def _open(self):
        if self.context_farm:
            self.openProperty.emit(self.context_farm["id"])

    def set_context(self, farm):
        self.context_farm = farm
        self.context_title.setText(farm["name"] if farm else "Selecione uma propriedade")
        self.open_button.setEnabled(bool(farm))
        self.context_table.replace(
            [(p, [ROLE_NAMES[p["role"]], scope_text(p)]) for p in farm["permissions"]]
            if farm
            else []
        )

    def set_map_component(self, component):
        """Explicit extension point; actual GIS integration belongs to a later stage."""
        pages = self.centralWidget()
        old = self.map_viewport
        index = pages.indexOf(old)
        pages.insertWidget(index, component)
        pages.removeWidget(old)
        self.map_viewport = component
        self.map_index = index
        if self.map_active:
            pages.setCurrentIndex(self.map_index)
        old.deleteLater()

    def activate_map(self, active):
        self.map_active = False  # Do not overwrite user preferences while switching pages.
        preferences = self.compact_visibility if self.compact else self.panel_visibility
        for name, dock in self.docks.items():
            dock.setVisible(active and preferences[name])
            self.toggles[name].setEnabled(active)
        self.map_active = active

    def adapt(self, compact):
        if compact == self.compact:
            return
        self.compact = compact
        # Wide and compact layouts remember separate user choices. Optional
        # panels start collapsed on small monitors, but may be reopened there.
        if self.map_active:
            self.activate_map(True)
