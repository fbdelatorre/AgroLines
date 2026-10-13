"""View construction; business calls and access checks remain in MainWindow."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QListWidget,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QWidget,
)

from core.passwords import MIN_PASSWORD_LENGTH
from desktop.labels import ROLE_DESCRIPTIONS, ROLE_NAMES
from desktop.sharing import SharingFlow
from desktop.ui import (
    Card,
    FlowLayout,
    Page,
    RecordTable,
    action,
    field,
    form_layout,
    inline_input,
    label,
)


class PageBuilders:
    def auth_page(self):
        page = Page(
            "Bem-vindo ao AgroLines", "Entre na sua conta para acessar propriedades e permissões."
        )
        card = Card("Acesso à conta", "O primeiro acesso exige conexão com o servidor.")
        card.setMaximumWidth(650)
        self.auth_tabs = QTabWidget()
        login = QWidget()
        form = form_layout(login)
        self.login_email = field(form, "E-mail", "seuemail@exemplo.com")
        self.login_password = field(form, "Senha", "Sua senha", True)
        self.login_password.returnPressed.connect(self.sign_in)
        form.addRow("", action("Entrar", self.sign_in, image="lock", variant="primary"))
        self.auth_tabs.addTab(login, "Login")
        register = QWidget()
        form = form_layout(register)
        self.register_name = field(form, "Nome", "Como você deseja ser chamado")
        self.register_email = field(form, "E-mail", "seuemail@exemplo.com")
        self.register_password = field(
            form, "Senha", f"Mínimo de {MIN_PASSWORD_LENGTH} caracteres", True
        )
        form.addRow(
            "", label("Use de 6 a 128 caracteres. Senhas maiores continuam aceitas.", "Hint")
        )
        form.addRow("", action("Criar conta", self.sign_up, image="plus", variant="primary"))
        self.auth_tabs.addTab(register, "Cadastro")
        recovery = QWidget()
        form = form_layout(recovery)
        self.recovery_email = field(form, "E-mail da conta", "seuemail@exemplo.com")
        form.addRow("", action("Solicitar código", self.recover_password, image="mail"))
        self.reset_token = field(form, "Código recebido", "Código do e-mail de recuperação", True)
        self.reset_password = field(
            form, "Nova senha", f"Mínimo de {MIN_PASSWORD_LENGTH} caracteres", True
        )
        form.addRow(
            "", action("Redefinir senha", self.reset_password_now, image="check", variant="primary")
        )
        form.addRow(
            "",
            label(
                "O envio do código depende do serviço de e-mail configurado pelo operador.", "Hint"
            ),
        )
        self.auth_tabs.addTab(recovery, "Recuperar senha")
        card.body.addWidget(self.auth_tabs)
        page.body.addWidget(card, alignment=Qt.AlignHCenter)
        page.body.addStretch()
        return page

    def account_page(self):
        page = Page("Minha conta", "Dados da conta e identificação para receber convites.")
        card = Card("Dados pessoais")
        card.setMaximumWidth(800)
        holder = QWidget()
        form = form_layout(holder)
        self.account_name = field(form, "Nome")
        self.account_email = field(form, "E-mail")
        self.account_email.setReadOnly(True)
        self.account_id = field(form, "Identificador")
        self.account_id.setReadOnly(True)
        form.addRow("", action("Copiar identificador", self.copy_identifier, image="users"))
        card.body.addWidget(holder)
        controls = QHBoxLayout()
        action("Salvar nome", self.save_account, controls, "check", "primary")
        controls.addStretch()
        action("Sair da conta", self.logout, controls, "logout")
        card.body.addLayout(controls)
        page.body.addWidget(card)
        page.body.addStretch()
        return page

    def farms_page(self, shared):
        if shared:
            return self.shared_page()
        page = Page(
            "Minhas propriedades",
            "Cadastre a propriedade e organize suas safras e operações no mesmo lugar.",
        )
        card = Card("Propriedades")
        row = QHBoxLayout()
        self.farm_name = inline_input(row, "Nome da propriedade")
        self.farm_name.returnPressed.connect(self.create_farm)
        action("Criar propriedade", self.create_farm, row, "plus", "primary")
        card.body.addLayout(row)
        self.owned_list = RecordTable(["Propriedade", "Perfil"])
        card.body.addWidget(self.owned_list)
        context = FlowLayout()
        action("Renomear", self.rename_farm, context, "edit")
        action("Compartilhar", self.share_selected_property, context, "share")
        action("Transferir", self.transfer_farm, context, "transfer")
        context.addStretch()
        action("Atualizar propriedades", self.reload_access, context, "refresh")
        card.body.addLayout(context)
        detail = Card(
            "Safras e operações", "Cadastros mínimos usados para organizar os escopos de acesso."
        )
        row = QHBoxLayout()
        row.addWidget(label("Propriedade sob gestão"))
        self.property_farm = self.farm_selector(row)
        detail.body.addLayout(row)
        self.property_tabs = QTabWidget()
        seasons = QWidget()
        from PySide6.QtWidgets import QVBoxLayout

        body = QVBoxLayout(seasons)
        body.setContentsMargins(0, 8, 0, 0)
        row = QHBoxLayout()
        self.new_season_name = inline_input(row, "Ex.: 2026/2027")
        action("Criar safra", self.create_scope_season, row, "plus", "primary")
        body.addLayout(row)
        self.property_seasons = RecordTable(["Safra"])
        body.addWidget(self.property_seasons)
        self.property_tabs.addTab(seasons, "Safras")
        operations = QWidget()
        body = QVBoxLayout(operations)
        body.setContentsMargins(0, 8, 0, 0)
        row = QHBoxLayout()
        row.addWidget(label("Safra"))
        self.property_season = QComboBox()
        row.addWidget(self.property_season, 1)
        body.addLayout(row)
        row = QHBoxLayout()
        self.new_operation_name = inline_input(row, "Ex.: Plantio")
        action("Criar operação", self.create_scope_operation, row, "plus", "primary")
        body.addLayout(row)
        self.property_operations = RecordTable(["Operação"])
        body.addWidget(self.property_operations)
        self.property_tabs.addTab(operations, "Operações")
        detail.body.addWidget(self.property_tabs)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(card)
        splitter.addWidget(detail)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([230, 280])
        page.body.addWidget(splitter, 1)
        self.owned_list.currentRowChanged.connect(self.select_owned_property)
        self.property_farm.currentIndexChanged.connect(self.load_property_seasons)
        self.property_season.currentIndexChanged.connect(self.load_property_operations)
        self.property_seasons.currentRowChanged.connect(self.select_property_season)
        return page

    def shared_page(self):
        page = Page(
            "Compartilhadas comigo",
            "Selecione uma propriedade para consultar somente os escopos autorizados.",
        )
        listing = Card("Propriedades compartilhadas")
        self.shared_list = RecordTable(["Propriedade", "Perfil", "Escopo"])
        listing.body.addWidget(self.shared_list)
        row = QHBoxLayout()
        action("Atualizar compartilhadas", self.reload_access, row, "refresh")
        row.addStretch()
        listing.body.addLayout(row)
        detail = Card("Escopos permitidos", "Selecione uma safra para consultar suas operações.")
        self.authorized_seasons = RecordTable(["Safra"])
        self.authorized_operations = RecordTable(["Operação"])
        detail.body.addWidget(self.authorized_seasons)
        detail.body.addWidget(self.authorized_operations)
        split = QSplitter(Qt.Horizontal)
        split.addWidget(listing)
        split.addWidget(detail)
        split.setChildrenCollapsible(False)
        page.body.addWidget(split, 1)
        self.responsive_splits.append(split)
        self.shared_list.currentRowChanged.connect(self.read_shared_seasons)
        self.authorized_seasons.currentRowChanged.connect(self.read_shared_operations)
        return page

    def members_page(self):
        page = Page(
            "Usuários e permissões",
            "Consulte os escopos, ajuste o perfil ou revogue uma concessão de acesso.",
        )
        card = Card()
        row = QHBoxLayout()
        row.addWidget(label("Propriedade"))
        self.member_farm = self.farm_selector(row)
        action("Atualizar permissões", self.load_members, row, "refresh")
        card.body.addLayout(row)
        self.member_list = RecordTable(["Usuário", "Perfil", "Escopo"])
        card.body.addWidget(self.member_list)
        row = QHBoxLayout()
        row.addWidget(label("Perfil selecionado"))
        self.member_role = QComboBox()
        for role in ("administrator", "editor", "operator", "viewer"):
            self.member_role.addItem(ROLE_NAMES[role], role)
        row.addWidget(self.member_role, 1)
        action("Alterar perfil", self.change_member, row, "edit", "primary")
        action("Revogar acesso", self.revoke_member, row, "close", "danger")
        card.body.addLayout(row)
        card.body.addWidget(
            label(
                "O proprietário possui titularidade; ela é transferida na tela de propriedades.",
                "Hint",
            )
        )
        page.body.addWidget(card, 1)
        self.member_farm.currentIndexChanged.connect(self.load_members)
        self.member_list.currentRowChanged.connect(self.select_member)
        return page

    def sharing_page(self):
        page = Page(
            "Compartilhar propriedade",
            "Escolha o destinatário, limite o acesso e revise antes de enviar o convite.",
        )
        cards = []
        card = Card("1. Propriedade", "Você pode compartilhar propriedades que administra.")
        self.share_farm = self.farm_selector(card.body)
        card.body.addWidget(
            label("Não encontrou a propriedade? Cadastre-a ou confira suas permissões.", "Hint")
        )
        action(
            "Ir para propriedades",
            lambda: self.navigate_to("Minhas propriedades"),
            card.body,
            "farm",
        )
        card.body.addStretch()
        cards.append(card)
        card = Card(
            "2. Destinatário", "Informe o e-mail ou identificador de uma conta já cadastrada."
        )
        holder = QWidget()
        form = form_layout(holder)
        self.recipient = field(form, "Conta do destinatário", "E-mail ou identificador")
        card.body.addWidget(holder)
        card.body.addStretch()
        cards.append(card)
        card = Card("3. Perfil", "O servidor verifica o perfil e o escopo em cada solicitação.")
        self.share_role = QComboBox()
        for role in ("viewer", "operator", "editor", "administrator"):
            self.share_role.addItem(ROLE_NAMES[role], role)
        card.body.addWidget(self.share_role)
        self.role_description = label(ROLE_DESCRIPTIONS["viewer"], "Description")
        card.body.addWidget(self.role_description)
        card.body.addStretch()
        cards.append(card)
        card = Card("4. Escopo", "Escolha a propriedade inteira, safras ou operações específicas.")
        row = QHBoxLayout()
        self.share_scope = QComboBox()
        self.share_scope.addItems(
            ["Propriedade inteira", "Safras específicas", "Operações de uma safra"]
        )
        row.addWidget(self.share_scope, 1)
        action("Atualizar escopos", self.load_seasons, row, "refresh")
        card.body.addLayout(row)
        self.scope_views = QStackedWidget()
        self.scope_views.addWidget(
            label("Acesso inclui todas as safras e operações da propriedade.", "Description")
        )
        self.season_list = QListWidget()
        self.season_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.season_list.setMinimumHeight(110)
        self.scope_views.addWidget(self.season_list)
        operations = QWidget()
        from PySide6.QtWidgets import QVBoxLayout

        body = QVBoxLayout(operations)
        body.setContentsMargins(0, 0, 0, 0)
        body.addWidget(label("Safra"))
        self.operation_season = QComboBox()
        body.addWidget(self.operation_season)
        self.operation_list = QListWidget()
        self.operation_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.operation_list.setMinimumHeight(110)
        body.addWidget(self.operation_list)
        self.scope_views.addWidget(operations)
        card.body.addWidget(self.scope_views, 1)
        self.scope_notice = label("", "FieldError")
        card.body.addWidget(self.scope_notice)
        cards.append(card)
        card = Card(
            "5. Revisar convite", "A concessão entra em vigor somente após o destinatário aceitar."
        )
        self.share_review = label("", "Review")
        card.body.addWidget(self.share_review)
        self.share_confirmed = QCheckBox("Confirmo os dados e os escopos do convite.")
        card.body.addWidget(self.share_confirmed)
        card.body.addWidget(
            label(
                "Compartilhar a propriedade não libera equipamentos particulares de terceiros.",
                "Hint",
            )
        )
        card.body.addStretch()
        cards.append(card)
        self.sharing_flow = SharingFlow(
            cards, self.validate_share_step, self.enter_share_step, self.send_invite
        )
        self.sharing_flow.submit_button.setEnabled(False)
        self.share_confirmed.toggled.connect(self.sharing_flow.submit_button.setEnabled)
        self.share_farm.currentIndexChanged.connect(self.reset_share_scopes)
        self.share_role.currentIndexChanged.connect(self.update_share_role)
        self.share_scope.currentIndexChanged.connect(self.scope_views.setCurrentIndex)
        self.operation_season.currentIndexChanged.connect(self.load_operations)
        page.body.addWidget(self.sharing_flow, 1)
        return page

    def invites_page(self):
        page = Page(
            "Convites", "Separe recebidos e enviados; selecione um convite para ver seus escopos."
        )
        card = Card()
        row = QHBoxLayout()
        self.invite_direction = QComboBox()
        self.invite_direction.addItems(["Recebidos", "Enviados"])
        self.invite_status = QComboBox()
        self.invite_status.addItem("Todos os estados", None)
        for value, name in (
            ("pending", "Pendentes"),
            ("accepted", "Aceitos"),
            ("declined", "Recusados"),
            ("revoked", "Revogados"),
            ("expired", "Expirados"),
        ):
            self.invite_status.addItem(name, value)
        row.addWidget(self.invite_direction)
        row.addWidget(self.invite_status)
        row.addStretch()
        action("Atualizar convites", self.load_invites, row, "refresh")
        card.body.addLayout(row)
        self.invite_list = RecordTable(["Propriedade", "Pessoa", "Estado"])
        card.body.addWidget(self.invite_list)
        self.invite_details = label(
            "Selecione um convite para consultar o perfil e o escopo.", "Description"
        )
        card.body.addWidget(self.invite_details)
        row = QHBoxLayout()
        self.accept_invite_button = action(
            "Aceitar convite", lambda: self.decide_invite("accept"), row, "check", "primary"
        )
        self.decline_invite_button = action(
            "Recusar convite", lambda: self.decide_invite("decline"), row, "close"
        )
        self.revoke_invite_button = action(
            "Revogar convite", lambda: self.decide_invite("revoke"), row, "close", "danger"
        )
        row.addStretch()
        card.body.addLayout(row)
        page.body.addWidget(card, 1)
        self.invite_direction.currentIndexChanged.connect(self.render_invites)
        self.invite_status.currentIndexChanged.connect(self.render_invites)
        self.invite_list.currentRowChanged.connect(self.select_invite)
        self.select_invite()
        return page
