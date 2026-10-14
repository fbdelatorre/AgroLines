"""Create only synthetic local files; refuse to overwrite any existing directory."""

import argparse
import hashlib
import json
from pathlib import Path

import fiona

from core.local_projects import LocalProject


def polygon(left, bottom, right, top):
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [left, bottom],
                [right, bottom],
                [right, top],
                [left, top],
                [left, bottom],
            ]
        ],
    }


def prepare(directory):
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    sources = root / "arquivos-ficticios"
    sources.mkdir()
    geojson = sources / "limite-e-talhao-01.geojson"
    geojson.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "crs": {"properties": {"name": "EPSG:32723"}},
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"name": "Limite · Fazenda Fictícia Horizonte"},
                        "geometry": polygon(300000, 7500000, 300800, 7500600),
                    },
                    {
                        "type": "Feature",
                        "properties": {"name": "Talhão 01 · Soja fictícia · GeoJSON"},
                        "geometry": polygon(300020, 7500020, 300390, 7500280),
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    paths = [geojson]
    for extension, driver, name, geometry in (
        (
            "shp",
            "ESRI Shapefile",
            "Talhão 02 · Milho fictício · SHP",
            polygon(300410, 7500020, 300780, 7500280),
        ),
        (
            "gpkg",
            "GPKG",
            "Talhão 03 · Soja fictícia · GPKG",
            polygon(300020, 7500300, 300780, 7500580),
        ),
    ):
        path = sources / ("talhao-ficticio." + extension)
        with fiona.open(
            path,
            "w",
            driver=driver,
            crs="EPSG:32723",
            schema={"geometry": "Polygon", "properties": {"name": "str"}},
            encoding="UTF-8",
        ) as target:
            target.write({"geometry": geometry, "properties": {"name": name}})
        paths.append(path)
    project_path = root / "Demonstracao-ficticia.agrolines"
    project = LocalProject.create(project_path, "Demonstração fictícia · Fazenda Horizonte")
    try:
        project.import_files(paths, acknowledge_warnings=True)
        assert len(project.features()) == 4
        project.backup(root / "Backup-demonstracao-ficticia.agrolines")
    finally:
        project.close()
    result = {
        "synthetic_only": True,
        "work_crs": "EPSG:32723",
        "coordinates": "Retângulos matemáticos; não derivados de propriedade real",
        "project": project_path.name,
        "files": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*")
            if p.is_file()
        },
    }
    (root / "origem-dos-dados.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return project_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()
    prepare(args.directory)
