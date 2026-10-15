import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from distribution.build import prepare
from distribution.msix import identity, stage
from distribution.payload import manifest


@pytest.mark.parametrize("entrypoint", ["distribution.store", "distribution.standalone"])
def test_store_offline_native_workspace_ignores_online_configuration(tmp_path, entrypoint):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    url = f"http://127.0.0.1:{server.server_port}/must-not-be-requested"
    output = tmp_path / "probe.json"
    environment = dict(os.environ)
    environment.update(
        AGROLINES_API_URL=url,
        AGROLINES_TILE_AUTHORIZED="1",
        AGROLINES_TILE_URL="https://example.com/{z}/{x}/{y}.png",
        AGROLINES_TILE_ATTRIBUTION="Synthetic",
        AGROLINES_TILE_LICENSE_URL="https://example.com",
        PROJ_NETWORK="ON",
        QTWEBENGINE_REMOTE_DEBUGGING="9222",
    )
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                entrypoint,
                "--offline-network-report",
                str(output),
                "--probe-url",
                url,
            ],
            env=environment,
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        report = json.loads(output.read_text())
        assert report["passed"] and report["webengine_ready"]
        assert report["remote_ui_denied"] and report["python_network_denied"]
        assert report["remote_imports_denied"] and report["remote_paths_denied"]
        assert report["projects"]["backup_restored"]
        assert report["local_formats"] == ["SHP", "GPKG", "KML", "KMZ", "GeoJSON"]
        assert not requests, "Native WebEngine issued a request to the observation server"
        assert not report["sac_approved"] and not report["native_network_trace_validated"]
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def test_store_staging_rejects_payload_without_explicit_offline_policy(tmp_path):
    root = tmp_path / "payload"
    metadata = root / "_internal/distribution/windows"
    prepared = prepare(metadata, "1.0.0.0", identity()["publisher_display_name"], store=True)
    assert prepared["offline_only"] is True
    prepared.pop("offline_only")
    (metadata / "metadata.json").write_text(json.dumps(prepared))
    (root / "AgroLinesPoC.exe").write_bytes(b"MZsynthetic")
    (root / "payload-manifest.json").write_text(json.dumps(manifest(root)))
    with pytest.raises(ValueError, match="matching metadata"):
        stage(root, tmp_path / "stage", "1.0.0.0")


def test_offline_html_has_no_external_assets_or_network_csp():
    page = Path("desktop/map_assets/map-offline.html").read_text()
    assert "https:" not in page and "http:" not in page
    assert "connect-src 'none'" in page and "frame-src 'none'" in page
    for resource in ("leaflet.css", "map.css", "leaflet.js", "map.js"):
        assert resource in page
        assert Path("desktop/map_assets", resource).is_file()
