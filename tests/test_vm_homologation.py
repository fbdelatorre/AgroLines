"""Private handoff denies unsafe destinations; real lab TLS and synthetic activation."""

import json
import logging
import ssl
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import uuid4
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from core.license_protocol import verify
from desktop.diagnostics import export_zip, initialize, record_failure, snapshot
from desktop.license_transport import tls_context
from distribution.commercial_profile import prepare_trust
from distribution.private_delivery import authorize, lab_inputs, stage
from scripts.vm_license_lab import application, change
from scripts.vm_license_lab import initialize as prepare_lab


@pytest.fixture
def laboratory(tmp_path):
    root = tmp_path / "private-server"
    public = prepare_lab(root, "https://localhost")
    return root, public


@pytest.mark.parametrize(
    "field,value",
    [
        ("private", False),
        ("private", None),
        ("visibility", "public"),
        ("visibility", "internal"),
        ("full_name", "different/destination"),
        ("confirmation", "different/destination"),
        ("enabled", "false"),
        ("event", "pull_request"),
    ],
)
def test_private_handoff_fails_closed(field, value):
    metadata = {"private": True, "visibility": "private", "full_name": "owner/private"}
    arguments = {
        "repository": "owner/private",
        "confirmation": "owner/private",
        "enabled": "true",
        "event": "workflow_dispatch",
    }
    assert authorize(metadata, **arguments)["private_verified"]
    (metadata if field in metadata else arguments)[field] = value
    with pytest.raises(PermissionError):
        authorize(metadata, **arguments)


def test_live_lab_api_two_slots_third_refused_renew_expire_and_revoke(laboratory):
    root, public = laboratory
    keys = json.loads((public / "public.json").read_text())
    accounts = json.loads((root / "test-accounts.json").read_text())
    monthly, annual = accounts
    app = application(root)
    try:
        with TestClient(app, base_url="https://localhost") as client:

            def activate(account, slot):
                identifier = str(uuid4())
                response = client.post(
                    "/v1/activate",
                    json={
                        "email": account["email"],
                        "key": account["keys"][slot]["key"],
                        "installation_id": identifier,
                        "label": "TESTE synthetic VM",
                    },
                )
                return identifier, response

            first_id, first = activate(monthly, 0)
            second_id, second = activate(monthly, 1)
            assert first.status_code == second.status_code == 200
            assert activate(monthly, 0)[1].status_code == 409
            initial = verify(first.json()["license"], keys, first_id)
            assert initial["plan"] == "monthly"
            annual_id, annual_result = activate(annual, 0)
            assert (
                verify(annual_result.json()["license"], keys, annual_id)["expires_at"]
                > initial["expires_at"]
            )
            request = {
                "activation_id": initial["activation_id"],
                "installation_id": first_id,
                "credential": first.json()["credential"],
            }
            change(root, "monthly", "renew")
            assert (
                verify(client.post("/v1/check", json=request).json()["license"], keys, first_id)[
                    "expires_at"
                ]
                > initial["expires_at"]
            )
            change(root, "monthly", "expire")
            import time

            assert (
                verify(client.post("/v1/check", json=request).json()["license"], keys, first_id)[
                    "expires_at"
                ]
                < time.time()
            )
            change(root, "monthly", "revoke")
            assert (
                verify(client.post("/v1/check", json=request).json()["license"], keys, first_id)[
                    "status"
                ]
                == "revoked"
            )
            assert (
                client.post(
                    "/admin/login",
                    json={"email": "admin@example.com", "password": "none", "code": "000000"},
                ).status_code
                == 401
            )
    finally:
        app.state.engine.dispose()


def test_real_tls_accepts_only_lab_ca_and_matching_host_without_windows_trust_changes(laboratory):
    root, public = laboratory

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"synthetic TLS verified")

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(root / "tls-server.pem", root / "tls-server.key")
    server.socket = context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        ca = (public / "tls-ca.pem").read_text()
        with pytest.raises(ValueError, match="forbidden in production"):
            tls_context(ca)
        client_context = tls_context(ca, test_profile=True)
        assert client_context.check_hostname and client_context.verify_mode == ssl.CERT_REQUIRED
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=client_context)
        )
        port = server.server_address[1]
        with opener.open(f"https://localhost:{port}", timeout=5) as response:
            assert response.read() == b"synthetic TLS verified"
        with pytest.raises(urllib.error.URLError):
            opener.open(f"https://127.0.0.1:{port}", timeout=5)
        untrusted = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=tls_context())
        )
        with pytest.raises(urllib.error.URLError):
            untrusted.open(f"https://localhost:{port}", timeout=5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_public_lab_inputs_exclude_server_keys_and_production_rejects_lab_ca(laboratory, tmp_path):
    root, public = laboratory
    assert lab_inputs(public) == "https://localhost"
    assert {p.name for p in public.iterdir()} == {
        "origin.json",
        "public.json",
        "fixture.json",
        "tls-ca.pem",
    }
    prepare_trust(
        tmp_path / "lab.py",
        "https://localhost",
        public / "public.json",
        True,
        public / "tls-ca.pem",
    )
    with pytest.raises(ValueError):
        prepare_trust(
            tmp_path / "production.py",
            "https://localhost",
            public / "public.json",
            False,
            public / "tls-ca.pem",
        )
    (public / "server.key").write_text("inert secret sentinel")
    with pytest.raises(ValueError, match="four public"):
        lab_inputs(public)
    with pytest.raises(FileExistsError):
        prepare_lab(root, "https://localhost")


def test_reviewed_diagnostic_zip_excludes_raw_logs_projects_and_credentials(tmp_path):
    logger = logging.getLogger("agrolines.desktop")
    previous = logger.handlers[:]
    logger.handlers = []
    try:
        initialize(tmp_path)
        try:
            raise ValueError("SECRET-TOKEN C:/Personal/Private.agrolines")
        except ValueError:
            correlation = record_failure(logger, *sys.exc_info())
        for handler in logger.handlers:
            handler.flush()
        (tmp_path / "desktop.log.1").write_text("SECRET-TOKEN raw historical exception")
        (tmp_path / "license.dpapi").write_text("SECRET-TOKEN")
        (tmp_path / "Private.agrolines").write_text("SECRET-TOKEN")
        reviewed = snapshot(tmp_path)
        assert reviewed["events"][0]["event_id"] == correlation
        assert reviewed["events"][0]["error_type"] == "ValueError"
        destination = tmp_path / "reviewed.zip"
        export_zip(destination, reviewed)
        with ZipFile(destination) as archive:
            assert set(archive.namelist()) == {"diagnostico.json", "LEIA-ME.txt"}
            content = archive.read("diagnostico.json").decode()
            assert json.loads(content) == reviewed
            assert "SECRET-TOKEN" not in content and "Private.agrolines" not in content
        assert not snapshot(tmp_path, include_events=False)["events"]
        with pytest.raises(FileExistsError):
            export_zip(destination, reviewed)
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.handlers = previous


def test_private_staging_uses_allowlist_and_hashes_not_repository_or_lab_secrets(tmp_path):
    root, destination = tmp_path / "checkout", tmp_path / "private-output"
    paths = [
        "dist/AgroLines/payload-manifest.json",
        "dist/AgroLines/standalone-layout.json",
        "docs/testing/windows11-vm-checklist.md",
        "docs/testing/private-installer.md",
        "docs/testing/test-license-lab.md",
        "evidence/functional/installed/result.json",
        "evidence/functional/signing/native.json",
    ]
    for version in ("1.0.0.7", "1.0.0.8"):
        paths.extend(
            (
                f"dist/installers/AgroLines-Setup-{version}-TESTE-x64.exe",
                f"evidence/functional/artifact-{version}.json",
                f"evidence/functional/inno-{version}.log",
                f"evidence/functional/payload-{version}.json",
            )
        )
    for name in paths:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"inert synthetic file")
    (root / "issuer.private-key").write_text("SECRET-NOT-FOR-HANDOFF")
    from scripts.prepare_vm_fixtures import prepare

    fixtures = prepare(root / "build/vm-fixtures")
    from core.imports import import_polygons

    for extension in ("shp", "gpkg", "kml", "kmz", "geojson"):
        assert len(import_polygons([fixtures / ("TESTE." + extension)]).plots) == 1
    manifest = stage(root, destination, ("1.0.0.7", "1.0.0.8"))
    assert len(manifest) == len(paths) + len(list(fixtures.iterdir()))
    assert all(len(row["sha256"]) == 64 for row in manifest)
    assert not any(
        b"SECRET-NOT-FOR-HANDOFF" in p.read_bytes() for p in destination.rglob("*") if p.is_file()
    )


def test_diagnostic_dialog_exports_exact_preview_and_cancel_writes_nothing(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QPlainTextEdit, QWidget

    from desktop import diagnostics

    app = QApplication.instance() or QApplication([])
    value = {"correlation_id": "synthetic", "events": [], "automatic_transmission": False}
    monkeypatch.setattr(diagnostics, "snapshot", lambda **kwargs: value.copy())

    class Parent(QWidget):
        def run(self, callback):
            callback()

    parent = Parent()
    reviewed = []

    def approve(dialog):
        reviewed.append(json.loads(dialog.findChild(QPlainTextEdit).toPlainText()))
        return QDialog.Accepted

    monkeypatch.setattr(QDialog, "exec", approve)
    destination = tmp_path / "reviewed-from-ui.zip"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(destination), "ZIP"))
    diagnostics.review_export(parent)
    with ZipFile(destination) as archive:
        assert json.loads(archive.read("diagnostico.json")) == reviewed[0]
    monkeypatch.setattr(QDialog, "exec", lambda self: QDialog.Rejected)

    def forbidden(*args):
        pytest.fail("Save dialog must not open after cancellation")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", forbidden)
    diagnostics.review_export(parent)
    assert len(list(tmp_path.glob("*.zip"))) == 1
    parent.close()
    app.processEvents()


def test_builder_public_tls_fixture_never_imports_server_dependencies(tmp_path):
    import subprocess

    output, private = tmp_path / "public", tmp_path / "private"
    code = """
import importlib.abc, sys, runpy
class NoServer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in ('server', 'sqlalchemy', 'fastapi'):
            raise AssertionError('Server dependencies must not enter the client builder')
sys.meta_path.insert(0, NoServer())
sys.argv = ['fixture', '--output', sys.argv[1], '--tls-origin', 'https://localhost',
            '--tls-private-directory', sys.argv[2]]
runpy.run_module('scripts.prepare_license_lab', run_name='__main__')
"""
    subprocess.run(
        [sys.executable, "-c", code, str(output), str(private)], check=True, capture_output=True
    )
    assert lab_inputs(output) == "https://localhost"
    assert (private / "tls-server.key").is_file()
    assert not any("PRIVATE KEY" in file.read_text() for file in output.iterdir())
