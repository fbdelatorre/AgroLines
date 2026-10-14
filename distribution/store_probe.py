"""Opt-in synthetic offline probe; never uploads evidence or changes OS security."""

import importlib
import json
import socket
import tempfile
import zipfile
from pathlib import Path

from core.offline_policy import REMOTE_MODULES, enforce, require_local_path


def run(output, probe_url="http://127.0.0.1:9/forbidden"):
    enforce()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from core.imports import import_polygons
    from desktop.local_projects import LocalProjectsWindow
    from distribution.checks import run_checks
    from distribution.offline_checks import run_offline_checks

    app = QApplication.instance() or QApplication([])
    result = {"sac_approved": False, "native_network_trace_validated": False}
    result["components"] = run_checks()
    result["projects"] = run_offline_checks()
    for name in REMOTE_MODULES:
        try:
            importlib.import_module(name)
        except ImportError:
            continue
        raise AssertionError("Remote module loaded: " + name)
    result["remote_imports_denied"] = True
    for callback in (
        lambda: socket.create_connection(("127.0.0.1", 9)),
        lambda: socket.getaddrinfo("example.com", 443),
        lambda: socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(b"x", ("127.0.0.1", 9)),
    ):
        try:
            callback()
        except PermissionError:
            continue
        raise AssertionError("Python network operation escaped policy")
    result["python_network_denied"] = True
    for path in ("https://example.com/a.geojson", "//host/share/a.shp", "/vsicurl/https://x/a"):
        try:
            require_local_path(path)
        except ValueError:
            continue
        raise AssertionError("Remote path accepted")
    result["remote_paths_denied"] = True
    import fiona
    from pyproj import network

    assert not network.is_network_enabled()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for extension, driver in (("shp", "ESRI Shapefile"), ("gpkg", "GPKG")):
            path = root / ("synthetic." + extension)
            with fiona.open(
                path,
                "w",
                driver=driver,
                crs="EPSG:32723",
                schema={"geometry": "Polygon", "properties": {"name": "str"}},
            ) as dataset:
                # Component check returns geographic geometry; use explicit metric fixture.
                dataset.write(
                    {
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [300000, 7500000],
                                    [300100, 7500000],
                                    [300100, 7500100],
                                    [300000, 7500000],
                                ]
                            ],
                        },
                        "properties": {"name": "Synthetic"},
                    }
                )
            assert len(import_polygons([path]).plots) == 1
        kml = root / "synthetic.kml"
        kml.write_text(
            '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark>'
            "<Polygon><outerBoundaryIs><LinearRing><coordinates>"
            "-45,-22 -44.999,-22 -44.999,-21.999 -45,-22"
            "</coordinates></LinearRing></outerBoundaryIs></Polygon>"
            "</Placemark></Document></kml>"
        )
        kmz = root / "synthetic.kmz"
        with zipfile.ZipFile(kmz, "w") as archive:
            archive.write(kml, "doc.kml")
        for path in (kml, kmz):
            assert len(import_polygons([path]).plots) == 1
    result["local_formats"] = ["SHP", "GPKG", "KML", "KMZ", "GeoJSON"]
    window = LocalProjectsWindow()
    window.show()
    assert all(
        a.text() != "Colaboração online"
        for a in window.findChildren(
            __import__("PySide6.QtWidgets", fromlist=["QToolBar"]).QToolBar
        )[0].actions()
    )
    try:
        window.open_remote()
    except PermissionError:
        result["remote_ui_denied"] = True
    else:
        raise AssertionError("Remote window opened")
    window.map.set_online(True)
    assert not window.map.interceptor.online and window.map.imagery is None
    errors = []

    def complete():
        window.map.page.runJavaScript("JSON.stringify(window.offlineResults)", received)

    def received(value):
        value = json.loads(value or "{}")
        result["webengine_ready"] = window.map.is_ready
        result["webengine_external_requests_rejected"] = value
        if not value or not all(value.get(key) for key in ("fetch", "image", "websocket")):
            errors.append("WebEngine did not reject all synthetic network attempts")
        app.quit()

    def ready():
        target = json.dumps(probe_url)
        ws = json.dumps(probe_url.replace("http:", "ws:").replace("https:", "wss:"))
        window.map.page.runJavaScript(
            f"""window.offlineResults = {{}};
            fetch({target}).catch(() => window.offlineResults.fetch = true);
            let image = new Image(); image.onerror = () => window.offlineResults.image = true;
            image.src = {target};
            try {{ let ws = new WebSocket({ws});
                ws.onerror = () => window.offlineResults.websocket = true;
            }} catch (e) {{ window.offlineResults.websocket = true; }}"""
        )
        QTimer.singleShot(1500, complete)

    window.map.readyChanged.connect(ready)
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: (errors.append("Map timeout"), app.quit()))
    timer.start(30000)
    app.exec()
    timer.stop()
    window.close()
    app.processEvents()
    result["passed"] = not errors
    result["errors"] = errors
    Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["passed"] else 1
