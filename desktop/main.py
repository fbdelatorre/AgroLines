import os
import sys

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from desktop.client import ApiClient, ApiError
from desktop.health import check_health

SECTIONS = (
    "Painel",
    "Produtores",
    "Fazendas",
    "Talhões",
    "Safras",
    "Operações",
    "Máquinas",
    "Implementos",
    "Planejamentos",
    "Exportações",
    "Configurações",
)


class HealthWorker(QThread):
    checked = Signal(bool)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        self.checked.emit(check_health(self.url))


ROLE_NAMES = {
    "owner": "Proprietário",
    "administrator": "Administrador",
    "editor": "Editor",
    "operator": "Operador",
    "viewer": "Visualizador",
}
STATUSES = {
    "pending": "Pendente",
    "accepted": "Aceito",
    "declined": "Recusado",
    "revoked": "Revogado",
    "expired": "Expirado",
}


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


def button(text, action, layout):
    widget = QPushButton(text)
    widget.clicked.connect(action)
    layout.addWidget(widget)
    return widget


def field(layout, label, secret=False):
    widget = QLineEdit()
    if secret:
        widget.setEchoMode(QLineEdit.Password)
    layout.addRow(label, widget)
    return widget


class MainWindow(QMainWindow):
    def __init__(self, client=None):
        super().__init__()
        self.client = client or ApiClient(os.getenv("AGROLINES_API_URL", "http://127.0.0.1:8000"))
        self.online = None
        self.job = None
        self.farms = []
        self.setWindowTitle("AgroLines")
        self.resize(1120, 720)
        self.setStyleSheet(
            "QWidget { background:#18212b; color:#e7edf4; font-size:14px; }"
            "QLineEdit,QListWidget,QComboBox { background:#253443; padding:8px;"
            "border:1px solid #465867; }"
            "QPushButton { background:#256b4d; padding:9px; border-radius:4px; }"
            "QPushButton:disabled { background:#39434c; color:#89939e; }"
            "QTabBar::tab { padding:10px; }"
        )
        self.connection = QLabel("Verificando servidor…")
        self.message = QLabel("Sincronização completa não implementada.")
        self.message.setWordWrap(True)
        self.pages = QStackedWidget()
        self.navigation = QListWidget()
        self.page_indices = {}
        self.farm_selectors = []
        self.add_page("Entrar / Cadastro", self.auth_page())
        self.add_page("Minha conta", self.account_page())
        self.add_page("Minhas propriedades", self.farms_page(False))
        self.add_page("Compartilhadas comigo", self.farms_page(True))
        self.add_page("Usuários e permissões", self.members_page())
        self.add_page("Compartilhar propriedade", self.sharing_page())
        self.add_page("Convites recebidos e enviados", self.invites_page())
        for section in SECTIONS:
            self.add_page(section, QLabel(f"{section} — Em desenvolvimento"))
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)
        row = QHBoxLayout()
        row.addWidget(self.navigation, 1)
        row.addWidget(self.pages, 4)
        layout = QVBoxLayout()
        layout.addWidget(self.connection)
        layout.addWidget(self.message)
        layout.addLayout(row)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.worker = HealthWorker(self.client.url, self)
        self.worker.checked.connect(self.show_health)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(10000)
        self.refresh()

    def add_page(self, title, page):
        self.page_indices[title] = self.pages.count()
        self.navigation.addItem(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        self.pages.addWidget(scroll)

    def call(self, function, callback=None, protected=True):
        if self.job is not None:
            self.message.setText("Aguarde a solicitação em andamento.")
            return
        if protected and not self.online:
            self.message.setText("Esta ação exige conexão com o servidor.")
            return
        self.job = Job(function, self)
        current = self.job
        self.message.setText("Consultando servidor…")

        def completed():
            self.job = None
            if current.error:
                self.message.setText(str(current.error))
                if current.error.status == 401:
                    self.clear_views()
                    self.navigation.setCurrentRow(0)
            else:
                self.message.setText(
                    "Solicitação concluída. Sincronização completa não implementada."
                )
                if callback:
                    callback(current.result)
            current.deleteLater()

        current.finished.connect(completed)
        current.start()

    def public_request(self, method, path, body, callback=None):
        self.call(lambda: self.client.raw(method, path, body), callback, False)

    def private_request(self, method, path, body=None, callback=None):
        self.call(lambda: self.client.request(method, path, body), callback)

    def auth_page(self):
        tabs = QTabWidget()
        login = QWidget()
        form = QFormLayout(login)
        self.login_email = field(form, "E-mail")
        self.login_password = field(form, "Senha", True)
        sign_in = QPushButton("Entrar")
        form.addRow(sign_in)
        sign_in.clicked.connect(self.sign_in)
        tabs.addTab(login, "Login")
        register = QWidget()
        form = QFormLayout(register)
        self.register_name = field(form, "Nome")
        self.register_email = field(form, "E-mail")
        self.register_password = field(form, "Senha (mínimo 12 caracteres)", True)
        sign_up = QPushButton("Criar conta")
        form.addRow(sign_up)
        sign_up.clicked.connect(self.sign_up)
        tabs.addTab(register, "Cadastro")
        recovery = QWidget()
        form = QFormLayout(recovery)
        self.recovery_email = field(form, "E-mail da conta")
        send = QPushButton("Solicitar código por e-mail")
        form.addRow(send)
        send.clicked.connect(
            lambda: self.public_request(
                "POST",
                "/auth/recover",
                {"email": self.recovery_email.text()},
                lambda data: self.message.setText(data["message"]),
            )
        )
        self.reset_token = field(form, "Código recebido", True)
        self.reset_password = field(form, "Nova senha (mínimo 12 caracteres)", True)
        reset = QPushButton("Redefinir senha")
        form.addRow(reset)
        reset.clicked.connect(self.reset_password_now)
        tabs.addTab(recovery, "Recuperar senha")
        return tabs

    def sign_in(self):
        email, password = self.login_email.text(), self.login_password.text()
        self.login_password.clear()
        self.call(lambda: self.client.authenticate(email, password), self.apply_snapshot, False)

    def sign_up(self):
        body = {
            "name": self.register_name.text(),
            "email": self.register_email.text(),
            "password": self.register_password.text(),
        }
        self.register_password.clear()

        def created(user):
            self.login_email.setText(user["email"])
            self.message.setText("Conta criada. Entre com sua senha na aba Login.")

        self.call(lambda: self.client.raw("POST", "/auth/register", body), created, False)

    def reset_password_now(self):
        body = {"token": self.reset_token.text(), "password": self.reset_password.text()}
        self.reset_token.clear()
        self.reset_password.clear()
        self.call(
            lambda: self.client.raw("POST", "/auth/reset", body),
            lambda _: self.message.setText("Senha redefinida. Entre novamente."),
            False,
        )

    def account_page(self):
        page = QWidget()
        form = QFormLayout(page)
        self.account_name = field(form, "Nome")
        self.account_email = field(form, "E-mail")
        self.account_email.setReadOnly(True)
        self.account_id = field(form, "Seu identificador para convites")
        self.account_id.setReadOnly(True)
        save = QPushButton("Salvar nome")
        form.addRow(save)
        save.clicked.connect(
            lambda: self.private_request(
                "PATCH",
                "/auth/me",
                {"name": self.account_name.text()},
                lambda _: self.reload_access(),
            )
        )
        leave = QPushButton("Sair da conta")
        form.addRow(leave)

        def logout():
            self.call(
                self.client.logout,
                lambda text: (
                    self.clear_views(),
                    self.message.setText(text),
                    self.navigation.setCurrentRow(0),
                ),
                False,
            )

        leave.clicked.connect(logout)
        return page

    def farms_page(self, shared):
        page = QWidget()
        layout = QVBoxLayout(page)
        listing = QListWidget()
        if shared:
            self.shared_list = listing
            layout.addWidget(QLabel("Propriedades e escopos atualmente autorizados pelo servidor."))
        else:
            self.owned_list = listing
            self.farm_name = QLineEdit()
            self.farm_name.setPlaceholderText("Nome da propriedade")
            layout.addWidget(self.farm_name)
            button(
                "Cadastrar propriedade",
                lambda: self.private_request(
                    "POST",
                    "/farms",
                    {"name": self.farm_name.text()},
                    lambda _: self.reload_access(),
                ),
                layout,
            )
            button("Renomear propriedade selecionada", self.rename_farm, layout)
            self.transfer_user = QLineEdit()
            self.transfer_user.setPlaceholderText("Identificador do novo proprietário")
            layout.addWidget(self.transfer_user)
            button("Transferir titularidade da propriedade selecionada", self.transfer_farm, layout)
        layout.addWidget(listing)
        if shared:
            self.authorized_seasons = QListWidget()
            self.authorized_operations = QListWidget()
            listing.currentRowChanged.connect(
                lambda _: (self.authorized_seasons.clear(), self.authorized_operations.clear())
            )
            button("Consultar safras autorizadas", self.read_shared_seasons, layout)
            layout.addWidget(self.authorized_seasons)
            button("Consultar operações autorizadas", self.read_shared_operations, layout)
            layout.addWidget(self.authorized_operations)
        button("Atualizar acesso", self.reload_access, layout)
        return page

    def read_shared_seasons(self):
        item = self.shared_list.currentItem()
        if item:
            farm_id = item.data(Qt.UserRole)["id"]

            def loaded(data):
                current = self.shared_list.currentItem()
                if not current or current.data(Qt.UserRole)["id"] != farm_id:
                    return
                self.authorized_seasons.clear()
                self.authorized_operations.clear()
                for season in data:
                    self.authorized_seasons.addItem(season["name"])
                    self.authorized_seasons.item(self.authorized_seasons.count() - 1).setData(
                        Qt.UserRole, season["id"]
                    )

            self.call(lambda: self.client.request("GET", f"/farms/{farm_id}/seasons"), loaded)

    def read_shared_operations(self):
        farm, season = self.shared_list.currentItem(), self.authorized_seasons.currentItem()
        if farm and season:
            farm_id, season_id = farm.data(Qt.UserRole)["id"], season.data(Qt.UserRole)

            def loaded(data):
                self.authorized_operations.clear()
                for operation in data:
                    self.authorized_operations.addItem(operation["name"])

            self.call(
                lambda: self.client.request(
                    "GET", f"/farms/{farm_id}/seasons/{season_id}/operations"
                ),
                loaded,
            )

    def rename_farm(self):
        item = self.owned_list.currentItem()
        if item:
            farm_id = item.data(Qt.UserRole)["id"]
            self.private_request(
                "PATCH",
                "/farms/" + farm_id,
                {"name": self.farm_name.text()},
                lambda _: self.reload_access(),
            )

    def transfer_farm(self):
        from PySide6.QtWidgets import QMessageBox

        item = self.owned_list.currentItem()
        if (
            item
            and QMessageBox.question(
                self,
                "Transferir titularidade",
                "Você perderá o acesso de proprietário. Confirma a transferência?",
            )
            == QMessageBox.Yes
        ):
            farm_id = item.data(Qt.UserRole)["id"]
            user_id = self.transfer_user.text()
            self.call(
                lambda: self.client.request(
                    "POST", "/farms/" + farm_id + "/transfer", {"user_id": user_id}
                ),
                lambda _: self.reload_access(),
            )

    def farm_selector(self, layout):
        selector = QComboBox()
        self.farm_selectors.append(selector)
        layout.addWidget(selector)
        return selector

    def members_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.member_farm = self.farm_selector(layout)
        button("Carregar usuários e permissões", self.load_members, layout)
        self.member_list = QListWidget()
        self.member_farm.currentIndexChanged.connect(lambda _: self.member_list.clear())
        layout.addWidget(self.member_list)
        self.member_role = QComboBox()
        for role in ("administrator", "editor", "operator", "viewer"):
            self.member_role.addItem(ROLE_NAMES[role], role)
        layout.addWidget(self.member_role)
        button("Alterar perfil da permissão selecionada", self.change_member, layout)
        button("Revogar permissão selecionada", self.revoke_member, layout)
        return page

    def load_members(self):
        farm_id = self.member_farm.currentData()
        if farm_id:

            def loaded(data):
                if self.member_farm.currentData() != farm_id:
                    return
                self.member_list.clear()
                for entry in data:
                    scope = (
                        "operação"
                        if entry["operation_id"]
                        else "safra"
                        if entry["season_id"]
                        else "fazenda inteira"
                    )
                    self.member_list.addItem(
                        f"{entry['user']['name']} — {ROLE_NAMES[entry['role']]} — {scope}"
                    )
                    self.member_list.item(self.member_list.count() - 1).setData(Qt.UserRole, entry)

            self.call(lambda: self.client.request("GET", "/farms/" + farm_id + "/members"), loaded)

    def change_member(self):
        item = self.member_list.currentItem()
        if item and item.data(Qt.UserRole).get("id"):
            data = item.data(Qt.UserRole)
            body = {
                "role": self.member_role.currentData(),
                "season_id": data["season_id"],
                "operation_id": data["operation_id"],
            }
            self.call(
                lambda: self.client.request("PATCH", "/permissions/" + data["id"], body),
                lambda _: self.load_members(),
            )

    def revoke_member(self):
        item = self.member_list.currentItem()
        if item and item.data(Qt.UserRole).get("id"):
            grant_id = item.data(Qt.UserRole)["id"]
            self.call(
                lambda: self.client.request("DELETE", "/permissions/" + grant_id),
                lambda _: self.load_members(),
            )

    def sharing_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.share_farm = self.farm_selector(layout)
        self.recipient = QLineEdit()
        self.recipient.setPlaceholderText("E-mail de conta existente ou identificador do usuário")
        layout.addWidget(self.recipient)
        self.share_role = QComboBox()
        for role in ("viewer", "operator", "editor", "administrator"):
            self.share_role.addItem(ROLE_NAMES[role], role)
        layout.addWidget(self.share_role)
        self.new_season_name = QLineEdit()
        self.new_season_name.setPlaceholderText("Nome da nova safra")
        layout.addWidget(self.new_season_name)
        button("Cadastrar safra nesta propriedade", self.create_scope_season, layout)
        self.new_operation_name = QLineEdit()
        self.new_operation_name.setPlaceholderText("Nome da nova operação na safra selecionada")
        layout.addWidget(self.new_operation_name)
        button("Cadastrar operação na safra selecionada", self.create_scope_operation, layout)
        self.share_scope = QComboBox()
        self.share_scope.addItems(
            ["Fazenda inteira", "Safras selecionadas", "Operações selecionadas"]
        )
        layout.addWidget(self.share_scope)
        button("Carregar safras para selecionar escopos", self.load_seasons, layout)
        self.season_list = QListWidget()
        self.season_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.season_list)
        self.operation_season = QComboBox()
        layout.addWidget(self.operation_season)
        button("Carregar operações da safra selecionada", self.load_operations, layout)
        self.operation_list = QListWidget()
        self.operation_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.operation_list)
        self.share_farm.currentIndexChanged.connect(
            lambda _: (
                self.season_list.clear(),
                self.operation_season.clear(),
                self.operation_list.clear(),
            )
        )
        self.operation_season.currentIndexChanged.connect(lambda _: self.operation_list.clear())
        button("Enviar convite", self.send_invite, layout)
        return page

    def create_scope_season(self):
        farm_id = self.share_farm.currentData()
        if farm_id:
            self.private_request(
                "POST",
                f"/farms/{farm_id}/seasons",
                {"name": self.new_season_name.text()},
                lambda _: self.load_seasons(),
            )

    def create_scope_operation(self):
        farm_id, season_id = self.share_farm.currentData(), self.operation_season.currentData()
        if farm_id and season_id:
            self.private_request(
                "POST",
                f"/farms/{farm_id}/seasons/{season_id}/operations",
                {"name": self.new_operation_name.text()},
                lambda _: self.load_operations(),
            )

    def load_seasons(self):
        farm_id = self.share_farm.currentData()
        if farm_id:

            def loaded(data):
                if self.share_farm.currentData() != farm_id:
                    return
                self.season_list.clear()
                self.operation_season.clear()
                for season in data:
                    self.season_list.addItem(season["name"])
                    self.season_list.item(self.season_list.count() - 1).setData(
                        Qt.UserRole, season["id"]
                    )
                    self.operation_season.addItem(season["name"], season["id"])

            self.call(lambda: self.client.request("GET", "/farms/" + farm_id + "/seasons"), loaded)

    def load_operations(self):
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

            self.call(
                lambda: self.client.request(
                    "GET", f"/farms/{farm_id}/seasons/{season_id}/operations"
                ),
                loaded,
            )

    def send_invite(self):
        farm_id = self.share_farm.currentData()
        role = self.share_role.currentData()
        kind = self.share_scope.currentIndex()
        scopes = [{"role": role}]
        if kind == 1:
            scopes = [
                {"role": role, "season_id": i.data(Qt.UserRole)}
                for i in self.season_list.selectedItems()
            ]
        elif kind == 2:
            scopes = [
                {
                    "role": role,
                    "season_id": self.operation_season.currentData(),
                    "operation_id": i.data(Qt.UserRole),
                }
                for i in self.operation_list.selectedItems()
            ]
        if not farm_id or not scopes:
            self.message.setText("Selecione propriedade e escopos do convite.")
            return
        recipient = self.recipient.text().strip()
        body = {"email" if "@" in recipient else "user_id": recipient, "scopes": scopes}
        self.call(
            lambda: self.client.request("POST", "/farms/" + farm_id + "/invitations", body),
            lambda _: self.message.setText(
                "Convite criado. O destinatário pode aceitar na própria conta."
            ),
        )

    def invites_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        button("Atualizar convites", self.load_invites, layout)
        self.invite_list = QListWidget()
        layout.addWidget(self.invite_list)
        for label, decision in (
            ("Aceitar", "accept"),
            ("Recusar", "decline"),
            ("Revogar", "revoke"),
        ):
            button(label, lambda checked=False, d=decision: self.decide_invite(d), layout)
        return page

    def load_invites(self):
        def loaded(data):
            self.invite_list.clear()
            user_id = self.client.state.get("user", {}).get("id")
            for invite in data:
                direction = "Recebido" if invite["recipient_id"] == user_id else "Enviado"
                scopes = ", ".join(
                    ROLE_NAMES[scope["role"]]
                    + " / "
                    + (
                        f"{scope['season_name']} — {scope['operation_name']}"
                        if scope["operation_id"]
                        else scope["season_name"]
                        if scope["season_id"]
                        else "fazenda inteira"
                    )
                    for scope in invite["scopes"]
                )
                contact = (
                    invite["inviter_name"] if direction == "Recebido" else invite["recipient_name"]
                )
                self.invite_list.addItem(
                    f"{direction} • {contact} • {invite['farm_name']} • "
                    f"{STATUSES[invite['status']]} • {scopes}"
                )
                self.invite_list.item(self.invite_list.count() - 1).setData(Qt.UserRole, invite)

        self.call(lambda: self.client.request("GET", "/invitations"), loaded)

    def decide_invite(self, decision):
        item = self.invite_list.currentItem()
        if item:
            invitation_id = item.data(Qt.UserRole)["id"]
            self.call(
                lambda: self.client.request("POST", f"/invitations/{invitation_id}/{decision}"),
                lambda _: self.reload_access(),
            )

    def apply_snapshot(self, data):
        if not data or not data.get("user"):
            self.clear_views()
            return
        changed = self.farms != data["farms"]
        if changed:
            self.clear_views()
        user = data["user"]
        self.account_name.setText(user["name"])
        self.account_email.setText(user["email"])
        self.account_id.setText(user["id"])
        self.farms = data["farms"]
        self.owned_list.clear()
        self.shared_list.clear()
        for farm in self.farms:
            listing = self.owned_list if farm["owned"] else self.shared_list
            roles = ", ".join(ROLE_NAMES[p["role"]] for p in farm["permissions"])
            listing.addItem(f"{farm['name']} — {roles}")
            listing.item(listing.count() - 1).setData(Qt.UserRole, farm)
        if changed:
            for selector in self.farm_selectors:
                selected = selector.currentData()
                selector.clear()
                for farm in self.farms:
                    if any("manage" in p["actions"] for p in farm["permissions"]):
                        selector.addItem(farm["name"], farm["id"])
                index = selector.findData(selected)
                if index >= 0:
                    selector.setCurrentIndex(index)
        if not self.client.vault.available:
            self.message.setText(
                "Sessão somente em memória: proteção Windows indisponível. "
                "Sincronização não implementada."
            )
        if self.navigation.currentRow() == 0:
            self.navigation.setCurrentRow(self.page_indices["Minha conta"])

    def clear_views(self):
        self.farms = []
        for listing in (
            self.owned_list,
            self.shared_list,
            self.member_list,
            self.invite_list,
            self.season_list,
            self.operation_list,
            self.authorized_seasons,
            self.authorized_operations,
        ):
            listing.clear()
        for selector in self.farm_selectors:
            selector.clear()
        self.operation_season.clear()
        self.account_name.clear()
        self.account_email.clear()
        self.account_id.clear()

    def reload_access(self):
        self.clear_views()
        self.call(self.client.synchronize_access, self.apply_snapshot)

    def refresh(self):
        if not self.worker.isRunning():
            self.worker.start()
        if self.online is False and not self.client.offline_snapshot():
            self.clear_views()

    def show_health(self, online: bool):
        was_online = self.online
        self.online = online
        self.connection.setText(
            "Servidor online — sincronização completa não implementada"
            if online
            else "Servidor offline — resumo local por até 15 minutos; alterações bloqueadas"
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
                self.message.setText("Sem autorização local válida. O login inicial exige conexão.")

    def closeEvent(self, event):
        self.timer.stop()
        self.worker.wait()
        if self.job:
            self.job.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
    except ValueError as exc:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(None, "Configuração inválida", str(exc))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
