import os
import sys
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from PySide6.QtCore import QSize, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
)

from core.offline_policy import require_remote
from core.passwords import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from desktop.client import ApiClient, ApiError
from desktop.geography import GeographyController
from desktop.health import check_health
from desktop.icons import icon
from desktop.labels import ROLE_DESCRIPTIONS, ROLE_NAMES, SECTIONS, STATUSES, scope_text
from desktop.pages import PageBuilders
from desktop.ui import THEME, Card, Page, apply_theme, error_for, field, form_layout, label
from desktop.workspace import VisualWorkspace


class HealthWorker(QThread):
    checked = Signal(bool)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        self.checked.emit(check_health(self.url))


class Job(QThread):
    def __init__(self, function, parent=None):
        super().__init__(parent)
        self.function = function
        self.result = None
        self.error = None

    def run(self):
        try:
            self.result = self.function()
        except ApiError as exc:
            self.error = exc
        except Exception:
            self.error = ApiError(
                "Não foi possível executar a solicitação. Confira a configuração."
            )
        finally:
            self.function = None


class MainWindow(PageBuilders, QMainWindow):
    def __init__(self, client=None):
        require_remote()
        super().__init__()
        apply_theme()
        self.client = client or ApiClient(os.getenv("AGROLINES_API_URL", "http://127.0.0.1:8000"))
        self.online = None
        self.job = None
        self.pending_read = None
        self.geo = None
        self.farms = []
        self.invite_records = []
        self._populating = False
        self.responsive_splits = []
        self.farm_selectors = []
        self.page_indices = {}
        self.nav_rows = {}
        self.setWindowTitle("AgroLines")
        self.setMinimumSize(640, 480)
        self.setStyleSheet(THEME)
        self.pages = QStackedWidget()
        self.workspace = VisualWorkspace(self.pages)
        self.workspace.openProperty.connect(self.open_context_property)
        self._menu_collapsed = False
        self.navigation = QListWidget()
        self.navigation.setObjectName("Navigation")
        self.navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.navigation.setIconSize(QSize(19, 19))
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        aside = QVBoxLayout(self.sidebar)
        aside.setContentsMargins(3, 10, 3, 8)
        aside.setSpacing(6)
        aside.addWidget(self.navigation, 1)
        self.collapse_menu = QToolButton()
        self.collapse_menu.setIcon(icon("collapse"))
        self.collapse_menu.setToolTip("Recolher ou expandir menu")
        self.collapse_menu.clicked.connect(self.toggle_menu)
        aside.addWidget(self.collapse_menu)
        self.add_page("Entrar / Cadastro", self.auth_page(), "Entrar", "lock")
        dashboard = Page("Painel", "Esta seção faz parte das próximas etapas do AgroLines.")
        dashboard.body.addWidget(Card("Em desenvolvimento"))
        dashboard.body.addStretch()
        self.add_page("Painel", dashboard, image="home", future=True)
        self.add_page("Mapa", self.workspace.map_viewport, image="map", future=True)
        self.add_page("Minhas propriedades", self.farms_page(False), "Propriedades", "farm")
        self.add_page("Compartilhadas comigo", self.farms_page(True), "Compartilhadas", "share")
        self.add_page("Usuários e permissões", self.members_page(), "Permissões", "users")
        self.add_page("Compartilhar propriedade", self.sharing_page(), "Compartilhar", "share")
        self.add_page("Convites recebidos e enviados", self.invites_page(), "Convites", "mail")
        for section in SECTIONS:
            if section == "Painel":
                continue
            page = Page(section, "Esta seção faz parte das próximas etapas do AgroLines.")
            card = Card(
                "Em desenvolvimento",
                "Os cadastros mínimos de safras e operações estão na tela Propriedades.",
            )
            page.body.addWidget(card)
            page.body.addStretch()
            image = {
                "Painel": "home",
                "Fazendas": "farm",
                "Safras": "calendar",
                "Operações": "lines",
                "Configurações": "settings",
                "Produtores": "users",
            }.get(section, "layers")
            self.add_page(section, page, image=image, future=True)
        self.add_page("Minha conta", self.account_page(), image="user")
        self.navigation.currentRowChanged.connect(self.navigate_row)
        self.navigation.setCurrentRow(0)
        shell = QFrame()
        shell.setObjectName("Shell")
        column = QVBoxLayout(shell)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(self.sidebar)
        row.addWidget(self.workspace, 1)
        column.addWidget(self.top_bar())
        column.addLayout(row, 1)
        footer = QFrame()
        footer.setObjectName("Footer")
        row = QHBoxLayout(footer)
        row.setContentsMargins(14, 7, 14, 7)
        self.connection = label("● Verificando servidor", "Hint")
        self.connection.setWordWrap(False)
        self.message = label("", "Notice")
        self.message.setWordWrap(False)
        self.message.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.sync_status = label("Sincronização não implementada", "Hint")
        self.sync_status.setWordWrap(False)
        self.sync_status.setToolTip(
            "Não há sincronização completa ou fila de alterações offline nesta etapa."
        )
        row.addWidget(self.connection)
        row.addWidget(self.message, 1)
        row.addWidget(self.sync_status)
        column.addWidget(footer)
        self.setCentralWidget(shell)
        available = QApplication.primaryScreen().availableGeometry()
        self.resize(
            max(640, min(1180, int(available.width() * 0.94))),
            max(480, min(780, int(available.height() * 0.92))),
        )
        self.adapt_layout()
        self.worker = HealthWorker(self.client.url, self)
        self.worker.checked.connect(self.show_health)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(10000)
        self.refresh()

    def add_page(self, title, page, caption=None, image="layers", future=False):
        index = (
            self.workspace.map_index if page is self.workspace.map_viewport else self.pages.count()
        )
        self.page_indices[title] = index
        self.nav_rows[title] = self.navigation.count()
        item = QListWidgetItem(icon(image), caption or title)
        item.setData(Qt.UserRole, {"page": index, "title": title, "image": image})
        item.setToolTip(title + (" — Em desenvolvimento" if future else ""))
        self.navigation.addItem(item)
        if page is not self.workspace.map_viewport:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            self.pages.addWidget(scroll)

    def navigate_row(self, row):
        if row < 0:
            return
        for index in range(self.navigation.count()):
            item = self.navigation.item(index)
            item.setIcon(
                icon(item.data(Qt.UserRole)["image"], "#8fe1af" if index == row else "#91a6b2")
            )
        self.pages.setCurrentIndex(self.navigation.item(row).data(Qt.UserRole)["page"])
        title = self.navigation.item(row).data(Qt.UserRole)["title"]
        self.workspace.activate_map(title == "Mapa")
        if hasattr(self, "section_title"):
            self.section_title.setText(title + (" · Em desenvolvimento" if title == "Mapa" else ""))
        if title == "Mapa":
            if self.geo is None:
                try:
                    self.geo = GeographyController(self)
                except ValueError as exc:
                    self.notice(str(exc))
                    return
            self.geo.refresh()
        if title == "Convites recebidos e enviados" and self.client.state.get("access_token"):
            self.load_invites()
        elif title == "Usuários e permissões" and self.member_farm.currentData():
            self.load_members()

    def navigate_to(self, title):
        self.navigation.setCurrentRow(self.nav_rows[title])

    def top_bar(self):
        bar = QFrame()
        bar.setObjectName("TopBar")
        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 7, 12, 7)
        row.setSpacing(10)
        self.brand_box = QFrame()
        brand_row = QHBoxLayout(self.brand_box)
        brand_row.setContentsMargins(0, 0, 0, 0)
        logo = label()
        logo.setPixmap(icon("leaf", "#30b579").pixmap(24, 24))
        self.brand = label("AgroLines", "Brand")
        self.brand.setWordWrap(False)
        brand_row.addWidget(logo)
        brand_row.addWidget(self.brand, 1)
        row.addWidget(self.brand_box)
        self.context_property = QComboBox()
        self.context_property.setMinimumWidth(100)
        self.context_property.setPlaceholderText("Propriedade")
        self.context_property.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.context_property.setToolTip("Contexto da propriedade · somente acessos autorizados")
        self.context_property.setAccessibleName("Contexto da propriedade")
        self.context_property.currentIndexChanged.connect(self.context_changed)
        row.addWidget(self.context_property, 1)
        self.context_season = QComboBox()
        self.context_season.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.context_season.setMinimumWidth(75)
        self.context_season.setPlaceholderText("Safra")
        self.context_season.setAccessibleName("Safra do mapa")
        self.context_season.currentIndexChanged.connect(self.geo_scope_changed)
        row.addWidget(self.context_season, 1)
        self.context_plot = QComboBox()
        self.context_plot.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.context_plot.setMinimumWidth(75)
        self.context_plot.setPlaceholderText("Talhão")
        self.context_plot.setAccessibleName("Talhão do mapa")
        self.context_plot.currentIndexChanged.connect(self.geo_plot_changed)
        row.addWidget(self.context_plot, 1)
        self.section_title = label("Entrar / Cadastro", "Hint")
        self.section_title.setWordWrap(False)
        row.addWidget(self.section_title)
        for toggle in self.workspace.toggles.values():
            button = QToolButton()
            button.setDefaultAction(toggle)
            button.setToolTip(toggle.text() + " · mostrar ou recolher painel")
            row.addWidget(button)
        self.account_button = QToolButton()
        self.account_button.setIcon(icon("user", "#72d6a3"))
        self.account_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.account_button.setText("Minha conta")
        self.account_button.setMaximumWidth(150)
        self.account_button.clicked.connect(lambda: self.navigate_to("Minha conta"))
        row.addWidget(self.account_button)
        return bar

    def context_changed(self, *_):
        farm_id = self.context_property.currentData()
        if self.geo and not self._populating and not self.geo.allow_context_change(farm_id):
            return
        farm = next((f for f in self.farms if f["id"] == farm_id), None)
        self.workspace.set_context(farm)
        if self.geo and not self._populating:
            self.context_season.blockSignals(True)
            self.context_season.clear()
            self.context_season.blockSignals(False)
            self.context_plot.clear()
            self.geo.refresh()

    def geo_scope_changed(self, *_):
        if self.geo and not self._populating:
            self.geo.refresh()

    def geo_plot_changed(self, *_):
        if self.geo and self.context_plot.currentData():
            self.geo.map.run("select", self.context_plot.currentData())
            self.geo.map.run("fit", self.context_plot.currentData())

    def open_context_property(self, farm_id):
        farm = next((f for f in self.farms if f["id"] == farm_id), None)
        if not farm:
            return
        table = self.owned_list if farm["owned"] else self.shared_list
        self.navigate_to("Minhas propriedades" if farm["owned"] else "Compartilhadas comigo")
        for row in range(table.count()):
            if table.item(row).data(Qt.UserRole)["id"] == farm_id:
                table.setCurrentRow(row)
                break

    def toggle_menu(self):
        self._menu_collapsed = not self._menu_collapsed
        self.adapt_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "context_property"):
            self.adapt_layout()

    def adapt_layout(self):
        compact = self.width() < 900 or self._menu_collapsed
        self.sidebar.setFixedWidth(56 if compact else 176)
        self.brand_box.setFixedWidth(56 if compact else 176)
        self.brand.setVisible(not compact)
        self.collapse_menu.setText("" if compact else "Recolher menu")
        self.collapse_menu.setToolButtonStyle(
            Qt.ToolButtonIconOnly if compact else Qt.ToolButtonTextBesideIcon
        )
        for index in range(self.navigation.count()):
            item = self.navigation.item(index)
            item.setText(
                ""
                if compact
                else {
                    "Entrar / Cadastro": "Entrar",
                    "Minhas propriedades": "Propriedades",
                    "Compartilhadas comigo": "Compartilhadas",
                    "Usuários e permissões": "Permissões",
                    "Compartilhar propriedade": "Compartilhar",
                    "Convites recebidos e enviados": "Convites",
                }.get(item.data(Qt.UserRole)["title"], item.data(Qt.UserRole)["title"])
            )
        for split in self.responsive_splits:
            split.setOrientation(Qt.Horizontal if self.width() >= 1100 else Qt.Vertical)
        self.workspace.adapt(self.width() < 1050)
        self.section_title.setVisible(self.width() >= 1400)
        self.context_plot.setVisible(self.width() >= 1000)
        self.context_season.setVisible(self.width() >= 800)
        self.account_button.setToolButtonStyle(
            Qt.ToolButtonIconOnly if self.width() < 900 else Qt.ToolButtonTextBesideIcon
        )
        if hasattr(self, "sync_status"):
            self.sync_status.setVisible(self.width() >= 900)

    def notice(self, text):
        self.message.setText(text)
        self.message.setToolTip(text)

    def call(
        self, function, callback=None, protected=True, fields=None, defer=False, on_error=None
    ):
        if self.job is not None:
            if defer:
                self.pending_read = (function, callback, protected, fields, on_error)
            else:
                self.notice("Aguarde a solicitação em andamento.")
            return
        if protected and not self.online:
            self.notice("Esta ação exige conexão com o servidor.")
            return
        self.job = Job(function, self)
        current = self.job
        self.notice("Consultando servidor…")

        def completed():
            self.job = None
            if current.error:
                self.notice(str(current.error))
                for key, message in getattr(current.error, "field_errors", {}).items():
                    if fields and key in fields:
                        error_for(fields[key], message)
                if current.error.status == 401:
                    self.pending_read = None
                    self.clear_views()
                    self.navigate_to("Entrar / Cadastro")
                elif on_error:
                    on_error(current.error)
            else:
                self.notice("Solicitação concluída.")
                if callback:
                    callback(current.result)
            current.deleteLater()
            if self.job is None and self.pending_read:
                pending = self.pending_read
                self.pending_read = None
                self.call(pending[0], pending[1], pending[2], pending[3], on_error=pending[4])

        current.finished.connect(completed)
        current.start()

    def public_request(self, method, path, body, callback=None, fields=None, on_error=None):
        self.call(
            lambda: self.client.raw(method, path, body), callback, False, fields, on_error=on_error
        )

    def private_request(self, method, path, body=None, callback=None, fields=None):
        self.call(lambda: self.client.request(method, path, body), callback, fields=fields)

    def valid_name(self, widget):
        text = widget.text().strip()
        return error_for(
            widget,
            "Informe um nome."
            if not text
            else "Use até 120 caracteres."
            if len(text) > 120
            else "",
        )

    def valid_email(self, widget):
        try:
            validate_email(widget.text().strip(), check_deliverability=False)
        except EmailNotValidError:
            return error_for(widget, "Informe um e-mail válido.")
        return error_for(widget)

    def valid_password(self, widget):
        length = len(widget.text())
        return error_for(
            widget,
            f"Use pelo menos {MIN_PASSWORD_LENGTH} caracteres."
            if length < MIN_PASSWORD_LENGTH
            else f"Use até {MAX_PASSWORD_LENGTH} caracteres."
            if length > MAX_PASSWORD_LENGTH
            else "",
        )

    def sign_in(self):
        if not self.valid_email(self.login_email):
            return
        if not error_for(
            self.login_password, "Informe sua senha." if not self.login_password.text() else ""
        ):
            return
        email, password = self.login_email.text().strip(), self.login_password.text()
        self.login_password.clear()
        self.call(
            lambda: self.client.authenticate(email, password),
            self.apply_snapshot,
            False,
            {"email": self.login_email, "password": self.login_password},
        )

    def sign_up(self):
        checks = (
            self.valid_name(self.register_name),
            self.valid_email(self.register_email),
            self.valid_password(self.register_password),
        )
        if not all(checks):
            return
        body = {
            "name": self.register_name.text().strip(),
            "email": self.register_email.text().strip(),
            "password": self.register_password.text(),
        }
        self.register_password.clear()

        def created(user):
            self.login_email.setText(user["email"])
            self.auth_tabs.setCurrentIndex(0)
            self.notice("Conta criada. Entre com sua senha.")

        self.public_request(
            "POST",
            "/auth/register",
            body,
            created,
            {
                "name": self.register_name,
                "email": self.register_email,
                "password": self.register_password,
            },
            lambda error: error_for(self.register_email, str(error))
            if error.status == 409
            else None,
        )

    def recover_password(self):
        if self.valid_email(self.recovery_email):
            self.public_request(
                "POST",
                "/auth/recover",
                {"email": self.recovery_email.text().strip()},
                lambda result: self.notice(result["message"]),
                {"email": self.recovery_email},
            )

    def reset_password_now(self):
        if not self.valid_password(self.reset_password):
            return
        if not error_for(
            self.reset_token,
            "Informe o código recebido." if len(self.reset_token.text()) < 20 else "",
        ):
            return
        body = {"token": self.reset_token.text(), "password": self.reset_password.text()}
        self.reset_token.clear()
        self.reset_password.clear()
        self.public_request(
            "POST",
            "/auth/reset",
            body,
            lambda _: self.notice("Senha redefinida. Entre novamente."),
            {"token": self.reset_token, "password": self.reset_password},
        )

    def save_account(self):
        if self.valid_name(self.account_name):
            self.private_request(
                "PATCH",
                "/auth/me",
                {"name": self.account_name.text().strip()},
                lambda _: self.reload_access(),
                {"name": self.account_name},
            )

    def copy_identifier(self):
        QApplication.clipboard().setText(self.account_id.text())
        self.notice("Identificador copiado.")

    def logout(self):
        def done(text):
            self.clear_views()
            self.notice(text)
            self.navigate_to("Entrar / Cadastro")

        self.call(self.client.logout, done, False)

    def create_farm(self):
        if self.valid_name(self.farm_name):

            def created(farm):
                self._select_after_refresh = farm["id"]
                self.farm_name.clear()
                self.reload_access()

            self.private_request(
                "POST",
                "/farms",
                {"name": self.farm_name.text().strip()},
                created,
                {"name": self.farm_name},
            )

    def rename_farm(self):
        item = self.owned_list.currentItem()
        if item and self.valid_name(self.farm_name):
            farm_id = item.data(Qt.UserRole)["id"]
            self.private_request(
                "PATCH",
                "/farms/" + farm_id,
                {"name": self.farm_name.text().strip()},
                lambda _: self.reload_access(),
                {"name": self.farm_name},
            )
        elif not item:
            self.notice("Selecione uma propriedade para renomear.")

    def share_selected_property(self):
        item = self.owned_list.currentItem()
        if item:
            self.navigate_to("Compartilhar propriedade")
            self.share_farm.setCurrentIndex(self.share_farm.findData(item.data(Qt.UserRole)["id"]))
            self.sharing_flow.show_step(0)
        else:
            self.notice("Selecione uma propriedade para compartilhar.")

    def transfer_farm(self):
        item = self.owned_list.currentItem()
        if not item:
            self.notice("Selecione uma propriedade para transferir.")
            return
        farm = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("Transferir titularidade")
        body = QVBoxLayout(dialog)
        body.addWidget(label(f"Propriedade: {farm['name']}", "CardTitle"))
        body.addWidget(
            label(
                (
                    "O novo proprietário terá controle total. Seu acesso de "
                    "proprietário será removido."
                ),
                "Description",
            )
        )
        holder = QFrame()
        form = form_layout(holder)
        self.transfer_user = field(form, "Novo proprietário", "Identificador da conta")
        body.addWidget(holder)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Transferir titularidade")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancelar")

        def confirm():
            try:
                UUID(self.transfer_user.text().strip())
            except ValueError:
                error_for(self.transfer_user, "Informe um identificador válido.")
                return
            dialog.accept()

        buttons.accepted.connect(confirm)
        buttons.rejected.connect(dialog.reject)
        body.addWidget(buttons)
        if dialog.exec() == QDialog.Accepted:
            user_id = str(UUID(self.transfer_user.text().strip()))
            self.private_request(
                "POST",
                "/farms/" + farm["id"] + "/transfer",
                {"user_id": user_id},
                lambda _: self.reload_access(),
            )

    def farm_selector(self, layout):
        selector = QComboBox()
        self.farm_selectors.append(selector)
        layout.addWidget(selector)
        return selector

    def select_owned_property(self, *_):
        if self._populating:
            return
        item = self.owned_list.currentItem()
        if item:
            self.property_farm.setCurrentIndex(
                self.property_farm.findData(item.data(Qt.UserRole)["id"])
            )

    def load_property_seasons(self, *_):
        if self._populating:
            return
        farm_id = self.property_farm.currentData()
        self.property_seasons.clear()
        self.property_operations.clear()
        if not farm_id:
            self.property_season.clear()
            return

        def loaded(data):
            if self.property_farm.currentData() != farm_id:
                return
            selected = self.property_season.currentData()
            self.property_seasons.replace([(s, [s["name"]]) for s in data])
            self.property_season.blockSignals(True)
            self.property_season.clear()
            for season in data:
                self.property_season.addItem(season["name"], season["id"])
            index = self.property_season.findData(selected)
            if index >= 0:
                self.property_season.setCurrentIndex(index)
            self.property_season.blockSignals(False)
            self.load_property_operations()

        self.call(
            lambda: self.client.request("GET", f"/farms/{farm_id}/seasons"), loaded, defer=True
        )

    def select_property_season(self, *_):
        item = self.property_seasons.currentItem()
        if item:
            self.property_season.setCurrentIndex(
                self.property_season.findData(item.data(Qt.UserRole)["id"])
            )
            self.property_tabs.setCurrentIndex(1)

    def load_property_operations(self, *_):
        if self._populating:
            return
        farm_id, season_id = self.property_farm.currentData(), self.property_season.currentData()
        self.property_operations.clear()
        if farm_id and season_id:

            def loaded(data):
                if (self.property_farm.currentData(), self.property_season.currentData()) == (
                    farm_id,
                    season_id,
                ):
                    self.property_operations.replace([(o, [o["name"]]) for o in data])

            self.call(
                lambda: self.client.request(
                    "GET", f"/farms/{farm_id}/seasons/{season_id}/operations"
                ),
                loaded,
                defer=True,
            )

    def create_scope_season(self):
        farm_id = self.property_farm.currentData()
        if farm_id and self.valid_name(self.new_season_name):
            self.private_request(
                "POST",
                f"/farms/{farm_id}/seasons",
                {"name": self.new_season_name.text().strip()},
                lambda _: (self.new_season_name.clear(), self.load_property_seasons()),
                {"name": self.new_season_name},
            )

    def create_scope_operation(self):
        farm_id, season_id = self.property_farm.currentData(), self.property_season.currentData()
        if farm_id and season_id and self.valid_name(self.new_operation_name):
            self.private_request(
                "POST",
                f"/farms/{farm_id}/seasons/{season_id}/operations",
                {"name": self.new_operation_name.text().strip()},
                lambda _: (self.new_operation_name.clear(), self.load_property_operations()),
                {"name": self.new_operation_name},
            )
        elif not season_id:
            self.notice("Cadastre e selecione uma safra antes de criar a operação.")

    def read_shared_seasons(self, *_):
        if self._populating:
            return
        self.authorized_seasons.clear()
        self.authorized_operations.clear()
        item = self.shared_list.currentItem()
        if item:
            farm_id = item.data(Qt.UserRole)["id"]

            def loaded(data):
                current = self.shared_list.currentItem()
                if current and current.data(Qt.UserRole)["id"] == farm_id:
                    self.authorized_seasons.replace([(s, [s["name"]]) for s in data])

            self.call(
                lambda: self.client.request("GET", f"/farms/{farm_id}/seasons"), loaded, defer=True
            )

    def read_shared_operations(self, *_):
        if self._populating:
            return
        self.authorized_operations.clear()
        farm, season = self.shared_list.currentItem(), self.authorized_seasons.currentItem()
        if farm and season:
            farm_id, season_id = farm.data(Qt.UserRole)["id"], season.data(Qt.UserRole)["id"]

            def loaded(data):
                current_farm, current_season = (
                    self.shared_list.currentItem(),
                    self.authorized_seasons.currentItem(),
                )
                if (
                    current_farm
                    and current_season
                    and current_farm.data(Qt.UserRole)["id"] == farm_id
                    and current_season.data(Qt.UserRole)["id"] == season_id
                ):
                    self.authorized_operations.replace([(o, [o["name"]]) for o in data])

            self.call(
                lambda: self.client.request(
                    "GET", f"/farms/{farm_id}/seasons/{season_id}/operations"
                ),
                loaded,
                defer=True,
            )

    def load_members(self, *_):
        if self._populating:
            return
        farm_id = self.member_farm.currentData()
        if getattr(self, "_member_source", None) != farm_id:
            self.member_list.clear()
        self._member_source = farm_id
        if farm_id:

            def loaded(data):
                if self.member_farm.currentData() == farm_id:
                    self.member_list.replace(
                        [
                            (
                                entry,
                                [
                                    entry["user"]["name"],
                                    ROLE_NAMES[entry["role"]],
                                    scope_text(entry),
                                ],
                            )
                            for entry in data
                        ]
                    )
                    self.select_member()

            self.call(
                lambda: self.client.request("GET", f"/farms/{farm_id}/members"), loaded, defer=True
            )

    def select_member(self, *_):
        item = self.member_list.currentItem()
        if item and item.data(Qt.UserRole).get("id"):
            self.member_role.setCurrentIndex(
                self.member_role.findData(item.data(Qt.UserRole)["role"])
            )

    def change_member(self):
        item = self.member_list.currentItem()
        if item and item.data(Qt.UserRole).get("id"):
            data = item.data(Qt.UserRole)
            body = {
                "role": self.member_role.currentData(),
                "season_id": data["season_id"],
                "operation_id": data["operation_id"],
            }
            if body["role"] == "administrator" and body["season_id"]:
                self.notice(
                    "Administrador exige acesso à propriedade inteira. Use outro "
                    "perfil neste escopo."
                )
                return
            self.private_request(
                "PATCH", "/permissions/" + data["id"], body, lambda _: self.load_members()
            )
        else:
            self.notice(
                "Selecione uma concessão de acesso; titularidade é "
                "transferida na tela Propriedades."
            )

    def revoke_member(self):
        item = self.member_list.currentItem()
        if item and item.data(Qt.UserRole).get("id"):
            data = item.data(Qt.UserRole)
            confirmation = QMessageBox(self)
            confirmation.setWindowTitle("Revogar acesso")
            confirmation.setIcon(QMessageBox.Question)
            confirmation.setTextFormat(Qt.PlainText)
            confirmation.setText(
                f"Revogar a concessão de {data['user']['name']} para {scope_text(data)}?"
            )
            confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            confirmation.setDefaultButton(QMessageBox.Cancel)
            answer = confirmation.exec()
            if answer == QMessageBox.Yes:
                self.private_request(
                    "DELETE", "/permissions/" + data["id"], callback=lambda _: self.load_members()
                )
        else:
            self.notice("Selecione uma concessão de acesso para revogar.")

    def reset_share_scopes(self, *_):
        self.season_list.clear()
        self.operation_list.clear()
        self.operation_season.blockSignals(True)
        self.operation_season.clear()
        self.operation_season.blockSignals(False)
        self.share_confirmed.setChecked(False)
        self.scope_notice.clear()

    def update_share_role(self, *_):
        role = self.share_role.currentData()
        self.role_description.setText(ROLE_DESCRIPTIONS[role])
        self.share_scope.setEnabled(role != "administrator")
        if role == "administrator":
            self.share_scope.setCurrentIndex(0)

    def selected_scopes(self):
        role = self.share_role.currentData()
        kind = self.share_scope.currentIndex()
        if kind == 1:
            return [
                {"role": role, "season_id": i.data(Qt.UserRole)}
                for i in self.season_list.selectedItems()
            ]
        if kind == 2:
            return [
                {
                    "role": role,
                    "season_id": self.operation_season.currentData(),
                    "operation_id": i.data(Qt.UserRole),
                }
                for i in self.operation_list.selectedItems()
            ]
        return [{"role": role}]

    def validate_share_step(self, step):
        if step == 0 and not self.share_farm.currentData():
            self.notice("Selecione uma propriedade sob sua gestão.")
            return False
        if step == 1:
            text = self.recipient.text().strip()
            if "@" in text:
                return self.valid_email(self.recipient)
            try:
                UUID(text)
            except ValueError:
                return error_for(self.recipient, "Informe um e-mail ou identificador válido.")
            return error_for(self.recipient)
        if step == 3 and not self.selected_scopes():
            self.scope_notice.setText("Selecione ao menos uma safra ou operação.")
            return False
        return True

    def enter_share_step(self, step):
        if step == 3:
            self.scope_notice.clear()
            self.load_seasons()
        elif step == 4:
            self.share_confirmed.setChecked(False)
            kind = self.share_scope.currentIndex()
            names = (
                "Propriedade inteira"
                if kind == 0
                else ", ".join(
                    i.text()
                    for i in (
                        self.season_list.selectedItems()
                        if kind == 1
                        else self.operation_list.selectedItems()
                    )
                )
            )
            if kind == 2:
                names = f"{self.operation_season.currentText()} — {names}"
            self.share_review.setText(
                f"Propriedade: {self.share_farm.currentText()}\n\n"
                f"Destinatário: {self.recipient.text().strip()}\n\n"
                f"Perfil: {self.share_role.currentText()}\n\nEscopo: {names}"
            )

    def load_seasons(self, *_):
        if self._populating:
            return
        farm_id = self.share_farm.currentData()
        if farm_id:
            selected_seasons = {i.data(Qt.UserRole) for i in self.season_list.selectedItems()}
            selected_season = self.operation_season.currentData()
            selected_operations = {i.data(Qt.UserRole) for i in self.operation_list.selectedItems()}

            def loaded(data):
                if self.share_farm.currentData() != farm_id:
                    return
                self.season_list.clear()
                self.operation_season.blockSignals(True)
                self.operation_season.clear()
                for season in data:
                    self.season_list.addItem(season["name"])
                    self.season_list.item(self.season_list.count() - 1).setData(
                        Qt.UserRole, season["id"]
                    )
                    self.season_list.item(self.season_list.count() - 1).setSelected(
                        season["id"] in selected_seasons
                    )
                    self.operation_season.addItem(season["name"], season["id"])
                index = self.operation_season.findData(selected_season)
                if index >= 0:
                    self.operation_season.setCurrentIndex(index)
                self.operation_season.blockSignals(False)
                self.load_operations(selected=selected_operations)
                if not data:
                    self.scope_notice.setText(
                        "Nenhuma safra cadastrada. Crie a safra na tela Propriedades "
                        "ou compartilhe a propriedade inteira."
                    )

            self.call(
                lambda: self.client.request("GET", f"/farms/{farm_id}/seasons"), loaded, defer=True
            )

    def load_operations(self, *_, selected=None):
        if self._populating:
            return
        selected = (
            {i.data(Qt.UserRole) for i in self.operation_list.selectedItems()}
            if selected is None
            else selected
        )
        self.operation_list.clear()
        farm_id, season_id = self.share_farm.currentData(), self.operation_season.currentData()
        if farm_id and season_id:

            def loaded(data):
                if (self.share_farm.currentData(), self.operation_season.currentData()) != (
                    farm_id,
                    season_id,
                ):
                    return
                self.operation_list.clear()
                for operation in data:
                    self.operation_list.addItem(operation["name"])
                    self.operation_list.item(self.operation_list.count() - 1).setData(
                        Qt.UserRole, operation["id"]
                    )
                    self.operation_list.item(self.operation_list.count() - 1).setSelected(
                        operation["id"] in selected
                    )

            self.call(
                lambda: self.client.request(
                    "GET", f"/farms/{farm_id}/seasons/{season_id}/operations"
                ),
                loaded,
                defer=True,
            )

    def send_invite(self):
        if not all(self.validate_share_step(step) for step in (0, 1, 3)):
            return
        if self.sharing_flow.currentIndex() != 4 or not self.share_confirmed.isChecked():
            self.notice("Revise e confirme o convite antes de enviar.")
            return
        recipient = self.recipient.text().strip()
        body = {
            "email" if "@" in recipient else "user_id": recipient
            if "@" in recipient
            else str(UUID(recipient)),
            "scopes": self.selected_scopes(),
        }
        farm_id = self.share_farm.currentData()

        def done(_):
            self.recipient.clear()
            self.sharing_flow.show_step(0)
            self.notice("Convite criado. Ele fica disponível na conta do destinatário.")

        def failed(error):
            if error.status == 400:
                self.sharing_flow.show_step(1)
                error_for(self.recipient, str(error))

        self.call(
            lambda: self.client.request("POST", f"/farms/{farm_id}/invitations", body),
            done,
            on_error=failed,
        )

    def load_invites(self, *_):
        self.call(
            lambda: self.client.request("GET", "/invitations"), self.received_invites, defer=True
        )

    def received_invites(self, data):
        self.invite_records = data
        self.render_invites()

    def render_invites(self, *_):
        user_id = self.client.state.get("user", {}).get("id")
        received = self.invite_direction.currentIndex() == 0
        status = self.invite_status.currentData()
        rows = []
        for entry in self.invite_records:
            if (entry["recipient_id"] == user_id) != received or (
                status and entry["status"] != status
            ):
                continue
            rows.append(
                (
                    entry,
                    [
                        entry["farm_name"],
                        entry["inviter_name"] if received else entry["recipient_name"],
                        STATUSES[entry["status"]],
                    ],
                )
            )
        self.invite_list.replace(rows)
        self.select_invite()

    def select_invite(self, *_):
        item = self.invite_list.currentItem()
        entry = item.data(Qt.UserRole) if item else None
        received = (
            entry["recipient_id"] == self.client.state.get("user", {}).get("id")
            if entry
            else self.invite_direction.currentIndex() == 0
        )
        pending = bool(entry and entry["status"] == "pending")
        self.accept_invite_button.setVisible(received)
        self.decline_invite_button.setVisible(received)
        self.revoke_invite_button.setVisible(not received)
        self.accept_invite_button.setEnabled(pending)
        self.decline_invite_button.setEnabled(pending)
        self.revoke_invite_button.setEnabled(
            bool(entry and entry["status"] in ("pending", "accepted"))
        )
        self.invite_details.setText(
            "\n".join(ROLE_NAMES[s["role"]] + " · " + scope_text(s) for s in entry["scopes"])
            if entry
            else "Selecione um convite para consultar o perfil e o escopo."
        )

    def decide_invite(self, decision):
        item = self.invite_list.currentItem()
        if item:
            invitation_id = item.data(Qt.UserRole)["id"]

            def done(_):
                self.reload_access()
                self.pending_read = (
                    lambda: self.client.request("GET", "/invitations"),
                    self.received_invites,
                    True,
                    None,
                    None,
                )

            self.private_request("POST", f"/invitations/{invitation_id}/{decision}", callback=done)

    def apply_snapshot(self, data):
        if not data or not data.get("user"):
            self.clear_views()
            return
        changed = self.farms != data["farms"]
        context_selected = self.context_property.currentData()
        chosen = getattr(self, "_select_after_refresh", None) or self.property_farm.currentData()
        if changed:
            self.clear_views()
        user = data["user"]
        if not self.account_name.isModified() or self.account_id.text() != user["id"]:
            self.account_name.setText(user["name"])
        self.account_email.setText(user["email"])
        self.account_id.setText(user["id"])
        self.farms = data["farms"]
        self.account_button.setText(user["name"])
        self.account_button.setToolTip("Minha conta · " + user["name"])
        if changed:
            self.context_property.blockSignals(True)
            self.context_property.clear()
            for farm in self.farms:
                self.context_property.addItem(farm["name"], farm["id"])
            index = self.context_property.findData(context_selected)
            self.context_property.setCurrentIndex(index if index >= 0 else 0)
            self.context_property.blockSignals(False)
            self.context_changed()
        if changed:
            self._populating = True
            owned, shared = [], []
            for farm in self.farms:
                roles = ", ".join(ROLE_NAMES[p["role"]] for p in farm["permissions"])
                if farm["owned"]:
                    owned.append((farm, [farm["name"], roles]))
                else:
                    shared.append(
                        (
                            farm,
                            [
                                farm["name"],
                                roles,
                                ", ".join(scope_text(p) for p in farm["permissions"]),
                            ],
                        )
                    )
            self.owned_list.replace(owned)
            self.shared_list.replace(shared)
            for selector in self.farm_selectors:
                selected = chosen if selector is self.property_farm else selector.currentData()
                selector.clear()
                for farm in self.farms:
                    if any("manage" in p["actions"] for p in farm["permissions"]):
                        selector.addItem(farm["name"], farm["id"])
                index = selector.findData(selected)
                if index >= 0:
                    selector.setCurrentIndex(index)
            if chosen:
                for row in range(self.owned_list.count()):
                    if self.owned_list.item(row).data(Qt.UserRole)["id"] == chosen:
                        self.owned_list.setCurrentRow(row)
                        break
            self._populating = False
            self._select_after_refresh = None
            self.load_property_seasons()
        if not self.client.vault.available:
            self.notice(
                "Sessão somente em memória neste sistema. Persistência "
                "protegida disponível no Windows."
            )
        if self.navigation.currentRow() == 0:
            self.navigate_to("Minha conta")

    def clear_views(self):
        self._populating = True
        self.pending_read = None
        self.farms = []
        self.invite_records = []
        if self.geo:
            self.geo.clear()
        for listing in (
            self.owned_list,
            self.shared_list,
            self.member_list,
            self.invite_list,
            self.season_list,
            self.operation_list,
            self.authorized_seasons,
            self.authorized_operations,
            self.property_seasons,
            self.property_operations,
        ):
            listing.clear()
        for selector in self.farm_selectors:
            selector.clear()
        self.operation_season.clear()
        self.property_season.clear()
        self.account_name.clear()
        self.account_email.clear()
        self.account_id.clear()
        self.context_property.clear()
        self.context_season.clear()
        self.context_plot.clear()
        self.workspace.set_context(None)
        self.account_button.setText("Minha conta")
        self.account_button.setToolTip("Minha conta")
        self.invite_details.setText("Selecione um convite para consultar o perfil e o escopo.")
        self.share_confirmed.setChecked(False)
        self._populating = False

    def reload_access(self):
        self.clear_views()
        self.call(self.client.synchronize_access, self.apply_snapshot, defer=True)

    def refresh(self):
        if not self.worker.isRunning():
            self.worker.start()
        if self.online is False and not self.client.offline_snapshot():
            self.clear_views()

    def show_health(self, online):
        was_online = self.online
        self.online = online
        if self.geo:
            self.geo.map.set_online(online)
        self.connection.setText("● Servidor online" if online else "● Servidor offline")
        self.connection.setStyleSheet("color: #7dda9f" if online else "color: #ecaa80")
        self.connection.setToolTip(
            "Servidor disponível. Sincronização completa ainda não implementada."
            if online
            else "Alterações bloqueadas. Resumo local disponível por até 15 minutos."
        )
        if online and self.client.state.get("access_token") and self.job is None:
            if was_online is not True:
                self.reload_access()
            else:
                self.call(self.client.synchronize_access, self.apply_snapshot)
        elif not online and was_online is not False:
            self.clear_views()
            snapshot = self.client.offline_snapshot()
            if snapshot:
                self.apply_snapshot(snapshot)
            else:
                self.notice("Sem autorização local válida. O login inicial exige conexão.")

    def closeEvent(self, event):
        self.timer.stop()
        self.worker.wait()
        if self.geo and not self.geo.allow_close():
            event.ignore()
            self.timer.start(10000)
            return
        if self.job:
            self.job.wait()
        if self.geo:
            self.geo.dispose()
        event.accept()


def main():
    app = QApplication(sys.argv)
    try:
        if "--remote" not in sys.argv:
            from desktop.local_projects import LocalProjectsWindow

            window = LocalProjectsWindow()
        else:
            window = MainWindow()
    except ValueError as exc:
        QMessageBox.critical(None, "Configuração inválida", str(exc))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
