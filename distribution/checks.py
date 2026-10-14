"""Actual geospatial checks for the frozen executable, without API/database setup."""

import json
import tempfile
from pathlib import Path


def run_checks():
    import fiona
    import numpy
    import pyproj
    import shapely
    from PySide6 import __version__ as qt_version
    from shapely.geometry import Point, Polygon, mapping

    from core.imports import import_polygons
    from core.precision import VertexEditor
    from scripts.precision_report import build_report

    assert numpy.array([1.0, 2.0]).sum() == 3.0
    assert Point(0, 0).distance(Point(3, 4)) == 5
    converter = pyproj.Transformer.from_crs(4326, 32723, always_xy=True)
    east, north = converter.transform(-45, 0, errcheck=True)
    assert abs(east - 500000) < 0.001 and abs(north - 10000000) < 0.001
    geometry = mapping(
        Polygon([(300000, 7500000), (300100, 7500000), (300100, 7500100), (300000, 7500100)])
    )
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "synthetic.shp"
        with fiona.open(
            path,
            "w",
            driver="ESRI Shapefile",
            crs="EPSG:32723",
            schema={"geometry": "Polygon", "properties": {"name": "str"}},
        ) as target:
            target.write({"geometry": geometry, "properties": {"name": "SAC PoC"}})
        imported = import_polygons([path])
        assert len(imported.plots) == 1 and abs(imported.plots[0]["area_m2"] - 10000) < 0.005
    editor = VertexEditor(geometry, "EPSG:32723")
    location, xy = next(editor.vertices())
    editor.set_vertex(location, xy[0] + 0.001, xy[1])
    assert abs(next(editor.vertices())[1][0] - xy[0] - 0.001) < 1e-8
    editor.undo()
    assert editor.source_geometry() == json.loads(json.dumps(geometry))
    precision = build_report()
    assert precision["computational_tests_passed"]
    return {
        "versions": {
            "numpy": numpy.__version__,
            "shapely": shapely.__version__,
            "pyproj": pyproj.__version__,
            "fiona": fiona.__version__,
            "gdal": fiona.__gdal_version__,
            "pyside6": qt_version,
        },
        "geospatial_checks_passed": True,
        "engine_versions": {
            "geos_shapely": shapely.geos_version_string,
            "proj_pyproj": pyproj.proj_version_str,
        },
        "precision": precision,
        "geometry": imported.plots[0]["geometry"],
    }
