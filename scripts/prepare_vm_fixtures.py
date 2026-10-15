"""Small completely synthetic GIS files for manual tests; no customer data."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def prepare(directory):
    import fiona
    from pyproj import Transformer

    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    metric = [
        [300000, 7500000],
        [300100, 7500000],
        [300100, 7500100],
        [300000, 7500100],
        [300000, 7500000],
    ]
    for extension, driver in (("shp", "ESRI Shapefile"), ("gpkg", "GPKG")):
        with fiona.open(
            root / ("TESTE." + extension),
            "w",
            driver=driver,
            crs="EPSG:32723",
            schema={"geometry": "Polygon", "properties": {"name": "str"}},
        ) as dataset:
            dataset.write(
                {
                    "geometry": {"type": "Polygon", "coordinates": [metric]},
                    "properties": {"name": "Talhao inteiramente sintetico"},
                }
            )
    transform = Transformer.from_crs(32723, 4326, always_xy=True)
    geographic = [list(transform.transform(*point)) for point in metric]
    (root / "TESTE.geojson").write_text(
        json.dumps(
            {
                "type": "Feature",
                "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                "properties": {"name": "Talhao sintetico"},
                "geometry": {"type": "Polygon", "coordinates": [geographic]},
            }
        )
    )
    points = " ".join(f"{x:.17g},{y:.17g},0" for x, y in geographic)
    (root / "TESTE.kml").write_text(
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Placemark>'
        "<name>TESTE sintetico</name><Polygon><outerBoundaryIs><LinearRing><coordinates>"
        + points
        + "</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></kml>"
    )
    with ZipFile(root / "TESTE.kmz", "x") as archive:
        archive.write(root / "TESTE.kml", "doc.kml")
    (root / "LINHA-NAO-SUPORTADA.geojson").write_text(
        json.dumps(
            {
                "type": "Feature",
                "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                "properties": {"name": "Caso negativo: linha"},
                "geometry": {"type": "LineString", "coordinates": geographic[:2]},
            }
        )
    )
    manifest = [
        {"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted(root.iterdir())
    ]
    (root / "fixture-manifest.json").write_text(
        json.dumps(
            {
                "synthetic_only": True,
                "metric_crs": "EPSG:32723",
                "geographic_crs": "EPSG:4326",
                "grid_square_metres": 10000,
                "grid_edge_metres": 100,
                "files": manifest,
            },
            indent=2,
        )
    )
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
