import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from desktop.main import MainWindow
from tests.conftest import account
from tests.test_desktop_session import client_for


@pytest.fixture(scope="module")
def qt():
    return QApplication.instance() or QApplication([])


def wait_for_idle(window):
    deadline = time.monotonic() + 10
    while window.job is not None and time.monotonic() < deadline:
        QTest.qWait(10)
    QTest.qWait(20)
    assert window.job is None, "Solicitação do desktop não completou"


def click(window, label):
    matches = [b for b in window.findChildren(QPushButton) if b.text() == label]
    assert len(matches) == 1
    matches[0].click()
    wait_for_idle(window)


def test_desktop_login_farm_and_real_invitation_flow(api, qt, monkeypatch):
    _, _, _ = account(api)
    recipient, recipient_headers, _ = account(api, "recipient@example.com")
    monkeypatch.setattr("desktop.main.check_health", lambda url: True)
    client = client_for(api)
    window = MainWindow(client)
    window.timer.stop()
    window.worker.wait()
    qt.processEvents()
    window.online = True
    window.show()
    try:
        window.login_email.setText("owner@example.com")
        window.login_password.setText("Senha sintetica 123!")
        click(window, "Entrar")
        assert window.login_password.text() == ""
        assert window.account_email.text() == "owner@example.com"
        window.farm_name.setText("Propriedade desktop")
        click(window, "Criar propriedade")
        assert window.owned_list.count() == 1
        window.owned_list.setCurrentRow(0)
        QTest.keyClicks(window.account_name, " rascunho")
        draft_name = window.account_name.text()
        window.apply_snapshot({"user": client.state["user"], "farms": client.state["farms"]})
        assert window.account_name.text() == draft_name
        assert window.owned_list.currentItem() is not None
        window.new_season_name.setText("2026/2027")
        click(window, "Criar safra")
        assert window.property_seasons.count() == 1
        window.new_operation_name.setText("Plantio")
        click(window, "Criar operação")
        assert window.property_operations.count() == 1
        window.navigate_to("Compartilhar propriedade")
        click(window, "Continuar")
        window.recipient.setText(recipient["email"])
        click(window, "Continuar")
        click(window, "Continuar")
        window.share_scope.setCurrentIndex(2)
        wait_for_idle(window)
        window.operation_list.item(0).setSelected(True)
        click(window, "Continuar")
        assert "Plantio" in window.share_review.text()
        click(window, "Voltar")
        assert len(window.operation_list.selectedItems()) == 1
        assert window.operation_list.count() == 1
        click(window, "Continuar")
        assert "Plantio" in window.share_review.text()
        assert not window.sharing_flow.submit_button.isEnabled()
        window.share_confirmed.setChecked(True)
        click(window, "Enviar convite")
        invitations = api.get("/invitations", headers=recipient_headers).json()
        assert len(invitations) == 1
        assert invitations[0]["scopes"][0]["operation_id"] is not None
        api.post("/invitations/" + invitations[0]["id"] + "/accept", headers=recipient_headers)
        window.navigate_to("Convites recebidos e enviados")
        wait_for_idle(window)
        window.invite_direction.setCurrentIndex(1)
        click(window, "Atualizar convites")
        window.invite_list.setCurrentRow(0)
        assert "Plantio" in window.invite_details.text()
        invited_client = client_for(api)
        invited_client.authenticate(recipient["email"], "Senha sintetica 123!")
        invited_window = MainWindow(invited_client)
        invited_window.timer.stop()
        invited_window.worker.wait()
        qt.processEvents()
        wait_for_idle(invited_window)
        invited_window.online = True
        try:
            assert invited_window.shared_list.count() == 1
            invited_window.shared_list.setCurrentRow(0)
            wait_for_idle(invited_window)
            assert invited_window.authorized_seasons.item(0).text() == "2026/2027"
            invited_window.authorized_seasons.setCurrentRow(0)
            wait_for_idle(invited_window)
            assert invited_window.authorized_operations.item(0).text() == "Plantio"
        finally:
            invited_window.close()
            qt.processEvents()
        window.navigate_to("Usuários e permissões")
        wait_for_idle(window)
        click(window, "Atualizar permissões")
        assert window.member_list.count() == 2
        assert "Plantio" in window.member_list.item(1, 2).text()
        assert "2026/2027" in window.member_list.item(1, 2).text()
        window.member_list.setCurrentRow(1)

        def confirm_revocation():
            dialog = QApplication.activeModalWidget()
            assert isinstance(dialog, QMessageBox)
            dialog.button(QMessageBox.Yes).click()

        QTimer.singleShot(50, confirm_revocation)
        click(window, "Revogar acesso")
        assert window.member_list.count() == 1
        assert api.get("/farms", headers=recipient_headers).json() == []
        window.show_health(False)
        assert "offline" in window.connection.text()
        count = window.owned_list.count()
        window.farm_name.setText("Não deve criar offline")
        click(window, "Criar propriedade")
        assert window.owned_list.count() == count
        assert "exige conexão" in window.message.text()
        window.show_health(True)
        wait_for_idle(window)
        click(window, "Sair da conta")
        assert window.account_email.text() == ""
        assert window.owned_list.count() == 0
        assert client.offline_snapshot() is None
    finally:
        window.close()
        qt.processEvents()


@pytest.mark.parametrize(
    "password,accepted", [("abcde", False), ("abcdef", True), ("abcdefghijkl", True)]
)
def test_desktop_password_validation_near_field(api, qt, monkeypatch, password, accepted):
    monkeypatch.setattr("desktop.main.check_health", lambda url: True)
    client = client_for(api)
    window = MainWindow(client)
    window.timer.stop()
    window.worker.wait()
    qt.processEvents()
    try:
        window.register_name.setText("Nova conta")
        window.register_email.setText("new@example.com")
        window.register_password.setText(password)
        window.auth_tabs.setCurrentIndex(1)
        click(window, "Criar conta")
        if accepted:
            assert window.auth_tabs.currentIndex() == 0
            assert window.register_password.text() == ""
            window.login_password.setText(password)
            click(window, "Entrar")
            assert window.account_email.text() == "new@example.com"
        else:
            assert window.auth_tabs.currentIndex() == 1
            assert "6 caracteres" in window.register_password.validation_label.text()
            assert (
                api.post(
                    "/auth/login", json={"email": "new@example.com", "password": password}
                ).status_code
                == 401
            )
    finally:
        window.close()
        qt.processEvents()
