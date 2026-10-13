import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

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
        click(window, "Cadastrar propriedade")
        assert window.owned_list.count() == 1
        window.new_season_name.setText("2026/2027")
        click(window, "Cadastrar safra nesta propriedade")
        assert window.season_list.count() == 1
        window.new_operation_name.setText("Plantio")
        click(window, "Cadastrar operação na safra selecionada")
        assert window.operation_list.count() == 1
        window.recipient.setText(recipient["email"])
        window.share_scope.setCurrentIndex(2)
        window.operation_list.item(0).setSelected(True)
        click(window, "Enviar convite")
        invitations = api.get("/invitations", headers=recipient_headers).json()
        assert len(invitations) == 1
        assert invitations[0]["scopes"][0]["operation_id"] is not None
        api.post("/invitations/" + invitations[0]["id"] + "/accept", headers=recipient_headers)
        click(window, "Atualizar convites")
        assert "Plantio" in window.invite_list.item(0).text()
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
            click(invited_window, "Consultar safras autorizadas")
            assert invited_window.authorized_seasons.item(0).text() == "2026/2027"
            invited_window.authorized_seasons.setCurrentRow(0)
            click(invited_window, "Consultar operações autorizadas")
            assert invited_window.authorized_operations.item(0).text() == "Plantio"
        finally:
            invited_window.close()
            qt.processEvents()
        click(window, "Carregar usuários e permissões")
        assert window.member_list.count() == 2
        assert "Plantio" in window.member_list.item(1).text()
        assert "2026/2027" in window.member_list.item(1).text()
        window.member_list.setCurrentRow(1)
        click(window, "Revogar permissão selecionada")
        assert window.member_list.count() == 1
        assert api.get("/farms", headers=recipient_headers).json() == []
        window.show_health(False)
        assert "offline" in window.connection.text()
        count = window.owned_list.count()
        window.farm_name.setText("Não deve criar offline")
        click(window, "Cadastrar propriedade")
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
