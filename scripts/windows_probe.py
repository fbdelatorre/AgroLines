"""Isolated native import/functional probes; never prints credentials or traces."""

import argparse
import json
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def probe(case):
    if case == "numpy":
        import numpy

        assert numpy.array([1.0, 2.0]).sum() == 3.0
    elif case == "shapely":
        from shapely.geometry import Point

        assert Point(0, 0).distance(Point(3, 4)) == 5
    elif case == "fiona":
        import fiona

        assert fiona.__gdal_version__
        assert "ESRI Shapefile" in fiona.supported_drivers
    elif case == "pyproj":
        from pyproj import Transformer

        east, north = Transformer.from_crs(4326, 32723, always_xy=True).transform(-45, 0)
        assert abs(east - 500000) < 0.001 and abs(north - 10000000) < 0.001
    elif case == "pyside6":
        from PySide6.QtWidgets import QApplication, QWidget

        app = QApplication([])
        window = QWidget()
        window.show()
        app.processEvents()
        assert window.isVisible()
        window.close()
    elif case == "server-import":
        from server.main import app

        assert app.title
    elif case == "server-postgis":
        server_postgis()
    elif case == "shapefile":
        import fiona
        from shapely.geometry import Polygon, mapping

        from core.imports import import_polygons

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "synthetic.shp"
            geometry = mapping(
                Polygon(
                    [(300000, 7500000), (300100, 7500000), (300100, 7500100), (300000, 7500100)]
                )
            )
            with fiona.open(
                path,
                "w",
                driver="ESRI Shapefile",
                crs="EPSG:32723",
                schema={"geometry": "Polygon", "properties": {"name": "str"}},
            ) as target:
                target.write({"geometry": geometry, "properties": {"name": "SAC synthetic"}})
            result = import_polygons([path])
            assert len(result.plots) == 1
            assert abs(result.plots[0]["area_m2"] - 10000) < 0.005
    else:
        raise ValueError("Unknown probe")


def server_postgis():
    """Read-only DB readiness, then an actual temporary Uvicorn process/HTTP health."""
    import socket

    from sqlalchemy import text

    from server.config import get_settings
    from server.db import make_engine

    engine = make_engine(get_settings())
    try:
        if engine.dialect.name != "postgresql":
            raise RuntimeError("PostGIS required")
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT PostGIS_Version()"))
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0005"
    finally:
        engine.dispose()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "server.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("Server exited")
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/health", timeout=1
                ) as response:
                    assert json.load(response)["status"] == "ok"
                    return
            except urllib.error.URLError:
                time.sleep(0.1)
        raise RuntimeError("Server readiness timeout")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "case",
        choices=[
            "numpy",
            "shapely",
            "fiona",
            "pyproj",
            "pyside6",
            "server-import",
            "server-postgis",
            "shapefile",
        ],
    )
    args = parser.parse_args()
    try:
        probe(args.case)
    except Exception as error:
        print(f"{args.case}: FAILED ({type(error).__name__}); inspect locally.", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"{args.case}: passed; SAC acceptance requires Windows policy/event evidence.")


if __name__ == "__main__":
    main()
