import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QTimer
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


def test_reference_workspace_panels_and_authorized_context(api, qt, monkeypatch):
    user, headers, _ = account(api)
    farm = api.post("/farms", headers=headers, json={"name": "Contexto autorizado"}).json()
    monkeypatch.setattr("desktop.main.check_health", lambda url: True)
    client = client_for(api)
    snapshot = client.authenticate(user["email"], "Senha sintetica 123!")
    window = MainWindow(client)
    window.timer.stop()
    window.worker.wait()
    qt.processEvents()
    wait_for_idle(window)
    window.apply_snapshot(snapshot)
    window.resize(1440, 900)
    window.show()
    try:
        window.navigate_to("Mapa")
        QTest.qWait(30)
        workspace = window.workspace
        assert window.pages.currentWidget() is workspace.map_viewport
        assert window.page_indices["Mapa"] == workspace.map_index
        assert all(d.isVisible() for d in workspace.docks.values())
        assert workspace.map_viewport.width() > workspace.layers.width()
        assert workspace.map_viewport.width() > workspace.parameters.width()
        assert workspace.context_farm["id"] == farm["id"]
        assert workspace.context_table.item(0, 0).text() == "Proprietário"
        workspace.toggles["layers"].trigger()
        assert not workspace.layers.isVisible()
        window.navigate_to("Minhas propriedades")
        assert all(not d.isVisible() for d in workspace.docks.values())
        window.navigate_to("Mapa")
        assert not workspace.layers.isVisible()
        assert workspace.parameters.isVisible()
        workspace.open_button.click()
        wait_for_idle(window)
        assert window.owned_list.currentItem().data(Qt.UserRole)["id"] == farm["id"]
        window.navigate_to("Mapa")
        window.resize(760, 540)
        QTest.qWait(20)
        assert all(not d.isVisible() for d in workspace.docks.values())
        workspace.toggles["layers"].trigger()
        assert workspace.layers.isVisible()
        window.resize(780, 550)
        QTest.qWait(20)
        assert workspace.layers.isVisible()
        window.navigate_to("Minha conta")
        window.navigate_to("Mapa")
        assert workspace.layers.isVisible()
        # Revoked/expired authorization cannot survive in the top or bottom panels.
        window.clear_views()
        assert window.context_property.count() == 0
        assert workspace.context_farm is None
        assert workspace.context_table.count() == 0
        assert not workspace.open_button.isEnabled()
    finally:
        window.close()
        qt.processEvents()


def test_future_map_replacement_keeps_existing_navigation(qt):
    from PySide6.QtWidgets import QFrame, QStackedWidget

    from desktop.workspace import VisualWorkspace

    pages = QStackedWidget()
    workspace = VisualWorkspace(pages)
    form = QFrame()
    form_index = pages.addWidget(form)
    replacement = QFrame()
    workspace.set_map_component(replacement)
    assert pages.widget(form_index) is form
    assert pages.widget(workspace.map_index) is replacement
    workspace.close()


def test_numeric_dialog_grid_millimetre_save_and_undo(api, qt, monkeypatch):
    from pyproj import CRS
    from shapely.geometry import Polygon, mapping

    from desktop.vertex_editor import NumericVertexDialog
    from tests.test_geography import body

    _, headers, _ = account(api)
    farm = api.post("/farms", headers=headers, json={"name": "Numeric dialog"}).json()
    geometry = mapping(
        Polygon([(300000.000123, 7500000), (300100, 7500000), (300100, 7500100), (300000, 7500100)])
    )
    imported = api.post(f"/farms/{farm['id']}/plots/import", headers=headers, json=body(geometry))
    assert imported.status_code == 201
    monkeypatch.setattr("desktop.main.check_health", lambda url: True)
    client = client_for(api)
    client.authenticate("owner@example.com", "Senha sintetica 123!")
    window = MainWindow(client)
    window.timer.stop()
    window.worker.wait()
    qt.processEvents()
    wait_for_idle(window)
    window.resize(1280, 860)
    window.show()
    try:
        window.navigate_to("Mapa")
        wait_for_idle(window)
        feature = window.geo.features[0]
        dialog = NumericVertexDialog(window.geo, feature)
        original_x = dialog.number(dialog.x)
        assert abs(original_x - 300000.000123) < 0.005
        assert CRS.from_user_input(dialog.editor.work_crs).to_epsg() == 32723
        dialog.distance.setText("0,001")
        dialog.move()
        assert abs(dialog.number(dialog.x) - original_x - 0.001) < 1e-8
        dialog.undo()
        assert dialog.number(dialog.x) == original_x
        dialog.redo()
        dialog.save()
        wait_for_idle(window)
        assert dialog.saved
        current = api.get(f"/farms/{farm['id']}/plots", headers=headers).json()["features"][0]
        assert current["properties"]["revision"] == 2
        assert (
            abs(
                current["properties"]["original_geometry"]["coordinates"][0][0][0]
                - 300000.000123
                - 0.001
            )
            < 1e-8
        )
    finally:
        window.close()
        qt.processEvents()
