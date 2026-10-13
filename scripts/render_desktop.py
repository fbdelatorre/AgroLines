"""Capture native Windows Qt screens with synthetic, isolated API fixtures.

Run from the checkout with python -m scripts.render_desktop --output <directory>.
--reference allows local Linux/offscreen design references, never Windows validation.
"""

import argparse
import json
import os
import platform
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True)
parser.add_argument("--scale", default="1")
parser.add_argument("--reference", action="store_true")
args = parser.parse_args()
if platform.system() != "Windows" and not args.reference:
    raise SystemExit("Native visual validation requires Windows.")
os.environ["QT_QPA_PLATFORM"] = "offscreen" if args.reference else "windows"
os.environ["QT_SCALE_FACTOR"] = args.scale

# Qt reads QPA and scaling settings during import; configure them above first.
from fastapi.testclient import TestClient  # noqa: E402
from PySide6.QtCore import qVersion  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import desktop.main as desktop_main  # noqa: E402
from server.config import Settings  # noqa: E402
from server.main import create_app  # noqa: E402
from server.models import Base  # noqa: E402
from tests.test_desktop_session import client_for  # noqa: E402


def wait(window):
    for _ in range(1000):
        QApplication.processEvents()
        if window.job is None:
            QTest.qWait(60)
            if window.job is None:
                return
        QTest.qWait(10)
    raise RuntimeError("UI fixture request did not finish.")


def fixtures(api):
    accounts = []
    for name, email in [
        ("Ana Costa", "ana@example.com"),
        ("Renato Silva", "renato@example.com"),
        ("Marina Lopes", "marina@example.com"),
    ]:
        response = api.post(
            "/auth/register", json={"name": name, "email": email, "password": "demo21"}
        )
        assert response.status_code == 201
        login = api.post("/auth/login", json={"email": email, "password": "demo21"}).json()
        accounts.append((response.json(), {"Authorization": "Bearer " + login["access_token"]}))
    ana, renato, marina = accounts
    farms = []
    for title in ("Fazenda São João", "Fazenda Horizonte"):
        farm = api.post("/farms", headers=ana[1], json={"name": title}).json()
        farms.append(farm)
        for year in ("2026/2027", "2027/2028"):
            season = api.post(
                f"/farms/{farm['id']}/seasons", headers=ana[1], json={"name": year}
            ).json()
            for operation in ("Plantio", "Colheita"):
                api.post(
                    f"/farms/{farm['id']}/seasons/{season['id']}/operations",
                    headers=ana[1],
                    json={"name": operation},
                )
    invitation = api.post(
        f"/farms/{farms[0]['id']}/invitations",
        headers=ana[1],
        json={"user_id": renato[0]["id"], "scopes": [{"role": "editor"}]},
    ).json()
    api.post(f"/invitations/{invitation['id']}/accept", headers=renato[1])
    api.post(
        f"/farms/{farms[0]['id']}/invitations",
        headers=ana[1],
        json={"user_id": marina[0]["id"], "scopes": [{"role": "viewer"}]},
    )
    shared = api.post("/farms", headers=renato[1], json={"name": "Fazenda das Palmeiras"}).json()
    season = api.post(
        f"/farms/{shared['id']}/seasons", headers=renato[1], json={"name": "2026/2027"}
    ).json()
    operation = api.post(
        f"/farms/{shared['id']}/seasons/{season['id']}/operations",
        headers=renato[1],
        json={"name": "Plantio"},
    ).json()
    invitation = api.post(
        f"/farms/{shared['id']}/invitations",
        headers=renato[1],
        json={
            "user_id": ana[0]["id"],
            "scopes": [
                {"role": "viewer", "season_id": season["id"], "operation_id": operation["id"]}
            ],
        },
    ).json()
    api.post(f"/invitations/{invitation['id']}/accept", headers=ana[1])
    api.post(
        f"/farms/{shared['id']}/invitations",
        headers=renato[1],
        json={"user_id": ana[0]["id"], "scopes": [{"role": "operator", "season_id": season["id"]}]},
    ).json()
    return farms


def main():
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    if not args.reference:
        assert app.platformName() == "windows"
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)  # Isolated fixture DB only; never the configured PostgreSQL.
    files = []
    diagnostics = []
    with TestClient(create_app(Settings(database_url="sqlite://"), engine)) as api:
        farms = fixtures(api)
        client = client_for(api)
        desktop_main.check_health = lambda url: api.get("/health").status_code == 200
        window = desktop_main.MainWindow(client)
        window.timer.stop()
        window.worker.wait()
        app.processEvents()
        window.online = True
        available = app.primaryScreen().availableGeometry()
        width = max(640, min(1180, available.width() - 40))
        height = max(480, min(780, available.height() - 60))
        window.resize(width, height)
        window.move(available.x() + 10, available.y() + 10)
        window.show()
        window.raise_()
        window.activateWindow()
        QTest.qWait(250)

        def capture(name):
            wait(window)
            QTest.qWait(100)
            image = (
                window.grab() if args.reference else app.primaryScreen().grabWindow(window.winId())
            )
            if image.isNull():
                raise RuntimeError("Native screen capture is unavailable; no offscreen fallback.")
            pixels = image.toImage()
            colors = {
                pixels.pixelColor(x, y).rgba()
                for y in range(0, pixels.height(), 7)
                for x in range(0, pixels.width(), 7)
            }
            if len(colors) < 16:
                raise RuntimeError("Native window capture is blank.")
            filename = f"{name}.png"
            assert image.save(str(output / filename))
            files.append(filename)
            diagnostics.append(
                {
                    "file": filename,
                    "logical_size": [window.width(), window.height()],
                    "pixels": [image.width(), image.height()],
                    "device_pixel_ratio": window.devicePixelRatioF(),
                }
            )

        capture("01-login")
        window.auth_tabs.setCurrentIndex(1)
        window.register_name.setText("Ana Costa")
        window.register_email.setText("ana@example.com")
        window.register_password.setText("abcde")
        window.valid_password(window.register_password)
        capture("02-registration-validation")
        window.apply_snapshot(client.authenticate("ana@example.com", "demo21"))
        wait(window)
        window.navigate_to("Minhas propriedades")
        window.property_farm.setCurrentIndex(window.property_farm.findData(farms[0]["id"]))
        wait(window)
        capture("03-properties-seasons")
        window.property_tabs.setCurrentIndex(1)
        capture("04-properties-operations")
        window.navigate_to("Usuários e permissões")
        window.member_farm.setCurrentIndex(window.member_farm.findData(farms[0]["id"]))
        window.load_members()
        wait(window)
        if window.member_list.count() > 1:
            window.member_list.setCurrentRow(1)
        capture("05-permissions")
        window.navigate_to("Convites recebidos e enviados")
        wait(window)
        window.invite_direction.setCurrentIndex(0)
        if window.invite_list.count():
            window.invite_list.setCurrentRow(0)
        capture("06-invitations-received")
        window.invite_direction.setCurrentIndex(1)
        if window.invite_list.count():
            window.invite_list.setCurrentRow(0)
        capture("07-invitations-sent")
        window.navigate_to("Compartilhar propriedade")
        window.share_farm.setCurrentIndex(window.share_farm.findData(farms[0]["id"]))
        window.sharing_flow.show_step(0)
        window.sharing_flow.next()
        window.recipient.setText("marina@example.com")
        window.sharing_flow.next()
        window.share_role.setCurrentIndex(window.share_role.findData("operator"))
        capture("08-sharing-role")
        window.sharing_flow.next()
        wait(window)
        window.share_scope.setCurrentIndex(2)
        wait(window)
        if window.operation_list.count():
            window.operation_list.item(0).setSelected(True)
        capture("09-sharing-scope")
        window.sharing_flow.next()
        window.share_confirmed.setChecked(True)
        capture("10-sharing-review")
        window.navigate_to("Compartilhadas comigo")
        if window.shared_list.count():
            window.shared_list.setCurrentRow(0)
            wait(window)
            if window.authorized_seasons.count():
                window.authorized_seasons.setCurrentRow(0)
        capture("11-shared-properties")
        window.navigate_to("Minhas propriedades")
        window.resize(
            max(640, min(820, available.width() - 40)), max(480, min(600, available.height() - 60))
        )
        capture("12-compact-layout")
        window.close()
        app.processEvents()
    engine.dispose()
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "system": platform.system(),
                "os_version": platform.version(),
                "qt_platform": app.platformName(),
                "qt_version": qVersion(),
                "font": app.font().family(),
                "scale_factor": args.scale,
                "native_capture": not args.reference,
                "synthetic_fixtures": True,
                "screens": diagnostics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Captured {len(files)} {app.platformName()} screens with synthetic fixtures.")


if __name__ == "__main__":
    main()
