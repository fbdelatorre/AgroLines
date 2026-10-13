import base64
import hashlib
import json
import zipfile
from pathlib import Path

import fiona
import pytest
from shapely.geometry import Polygon, mapping
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.geography import inspect_polygon
from core.imports import import_polygons
from server.models import ImportSource, PlotVersion
from tests.conftest import account


@pytest.fixture
def square():
    # Exactly one hectare and 400 m perimeter in SIRGAS 2000 / UTM 23S.
    return mapping(
        Polygon([(300000, 7500000), (300100, 7500000), (300100, 7500100), (300000, 7500100)])
    )


def test_metric_polygon_and_original_precision(square):
    result = inspect_polygon(square, "EPSG:31983")
    assert result.area_m2 == pytest.approx(10000, rel=1e-7)
    assert result.perimeter_m == pytest.approx(400, rel=1e-7)
    assert result.source_geometry == square
    assert result.metric_crs == "EPSG:31983"


@pytest.mark.parametrize("longitude", [-48.00001, -47.99999])
def test_near_utm_zone_boundary(longitude):
    result = inspect_polygon(
        mapping(
            Polygon(
                [
                    (longitude, -22),
                    (longitude + 0.001, -22),
                    (longitude + 0.001, -21.999),
                    (longitude, -21.999),
                ]
            )
        ),
        4326,
    )
    assert 11000 < result.area_m2 < 12000
    assert 420 < result.perimeter_m < 440


def test_invalid_geometry_requires_controlled_repair():
    data = mapping(Polygon([(-47, -22), (-46.999, -21.999), (-47, -21.999), (-46.999, -22)]))
    with pytest.raises(ValueError, match="inválida"):
        inspect_polygon(data, 4326)
    repaired = inspect_polygon(data, 4326, repair=True)
    assert repaired.warnings and repaired.source_geometry == data
    assert repaired.geometry["type"] == "MultiPolygon"


@pytest.mark.parametrize(
    "suffix,driver", [(".shp", "ESRI Shapefile"), (".gpkg", "GPKG"), (".geojson", "GeoJSON")]
)
def test_gdal_polygon_formats(tmp_path, square, suffix, driver):
    path = tmp_path / ("known" + suffix)
    with fiona.open(
        path,
        "w",
        driver=driver,
        schema={"geometry": "Polygon", "properties": {"name": "str"}},
        crs="EPSG:31983",
    ) as sink:
        sink.write({"geometry": square, "properties": {"name": "Um hectare"}})
    result = import_polygons([path])
    assert len(result.plots) == 1
    assert result.plots[0]["area_m2"] == pytest.approx(10000, rel=1e-7)
    assert result.plots[0]["attributes"]["name"] == "Um hectare"
    assert result.sources and all(
        hashlib.sha256(base64.b64decode(s["content_base64"])).hexdigest() == s["sha256"]
        for s in result.sources
    )
    if suffix == ".shp":
        assert {Path(s["name"]).suffix for s in result.sources} >= {".shp", ".shx", ".dbf", ".prj"}


@pytest.mark.parametrize("compressed", [False, True])
def test_kml_and_kmz(tmp_path, compressed):
    data = (
        b'<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2">'
        b"<Document><Placemark><name>Talhao KML</name><Polygon><outerBoundaryIs>"
        b"<LinearRing><coordinates>-47,-22,0 -46.999,-22,0 -46.999,-21.999,0 "
        b"-47,-21.999,0 -47,-22,0</coordinates></LinearRing></outerBoundaryIs>"
        b"</Polygon></Placemark></Document></kml>"
    )
    path = tmp_path / ("known.kmz" if compressed else "known.kml")
    if compressed:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("doc.kml", data)
    else:
        path.write_bytes(data)
    result = import_polygons([path])
    assert len(result.plots) == 1
    assert result.plots[0]["area_m2"] > 10000


def test_unknown_crs_and_external_kml_are_rejected(tmp_path):
    path = tmp_path / "unknown.geojson"
    path.write_text(
        json.dumps(
            {
                "type": "Polygon",
                "coordinates": [[[-47, -22], [-46.999, -22], [-46.999, -21.999], [-47, -22]]],
            }
        )
    )
    with pytest.raises(ValueError, match="SRC"):
        import_polygons([path])
    assert import_polygons([path], "EPSG:4326").plots
    kml = tmp_path / "unsafe.kml"
    kml.write_bytes(
        b"<kml><NetworkLink><Link><href>https://example.com/remote.kml</href></Link></NetworkLink></kml>"
    )
    with pytest.raises(ValueError, match="externas"):
        import_polygons([kml])


def body(square):
    normalized = inspect_polygon(square, "EPSG:31983")
    content = b"Synthetic original fixture"
    return {
        "sources": [
            {
                "name": "fixture.geojson",
                "content_base64": base64.b64encode(content).decode(),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        ],
        "plots": [
            {
                "name": "Talhao conhecido",
                "geometry": normalized.geometry,
                "original_geometry": square,
                "source_crs": "EPSG:31983",
                "source_ids": [0],
                "attributes": {"culture": "synthetic"},
            }
        ],
    }


def test_geometry_permissions_duplicate_and_atomic_originals(api, square):
    owner, headers, _ = account(api)
    recipient, theirs, _ = account(api, "reader@example.com")
    _, outsider, _ = account(api, "outsider@example.com")
    farm = api.post("/farms", headers=headers, json={"name": "GIS farm"}).json()
    path = f"/farms/{farm['id']}/plots"
    payload = body(square)
    assert api.post(path + "/import", headers=outsider, json=payload).status_code == 404
    response = api.post(path + "/import", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    plot_id = response.json()["created"][0]["id"]
    repeated = api.post(path + "/import", headers=headers, json=payload)
    assert repeated.status_code == 201 and not repeated.json()["created"]
    assert len(api.get(path, headers=headers).json()["features"]) == 1
    season = api.post(f"/farms/{farm['id']}/seasons", headers=headers, json={"name": "2026"}).json()
    operation = api.post(
        f"/farms/{farm['id']}/seasons/{season['id']}/operations",
        headers=headers,
        json={"name": "Plantio"},
    ).json()
    invitation = api.post(
        f"/farms/{farm['id']}/invitations",
        headers=headers,
        json={
            "user_id": recipient["id"],
            "scopes": [
                {"role": "viewer", "season_id": season["id"], "operation_id": operation["id"]}
            ],
        },
    ).json()
    api.post(f"/invitations/{invitation['id']}/accept", headers=theirs)
    assert api.get(path, headers=theirs).status_code == 404
    assert api.get(path + f"?season_id={season['id']}", headers=theirs).status_code == 404
    scoped = path + f"?season_id={season['id']}&operation_id={operation['id']}"
    assert not api.get(scoped, headers=theirs).json()["features"]
    assert (
        api.post(
            path + f"/{plot_id}/scopes",
            headers=headers,
            json={"season_ids": [season["id"]], "operation_ids": [operation["id"]]},
        ).status_code
        == 204
    )
    assert len(api.get(scoped, headers=theirs).json()["features"]) == 1
    assert api.get(path + f"/{plot_id}/versions", headers=theirs).status_code == 404
    assert api.post(path + "/import", headers=theirs, json=payload).status_code == 404
    with Session(api.app.state.engine) as db:
        version = db.scalar(select(PlotVersion))
        source = db.scalar(select(ImportSource))
        assert version.actor_id == owner["id"]
        assert source.content == b"Synthetic original fixture"
        source_id = source.id
    assert api.get(f"/farms/{farm['id']}/sources/{source_id}", headers=theirs).status_code == 404
    assert api.get(f"/farms/{farm['id']}/sources/{source_id}", headers=headers).status_code == 200
    permissions = api.get(f"/farms/{farm['id']}/members", headers=headers).json()
    permission_id = next(p["id"] for p in permissions if p["role"] != "owner")
    api.delete(f"/permissions/{permission_id}", headers=headers)
    assert api.get(scoped, headers=theirs).status_code == 404
    history = api.get(path + f"/{plot_id}/versions", headers=headers)
    assert history.status_code == 200 and len(history.json()) == 1


def test_forged_metrics_geometry_and_invalid_source_rollback(api, square):
    _, headers, _ = account(api)
    farm = api.post("/farms", headers=headers, json={"name": "Atomic farm"}).json()
    path = f"/farms/{farm['id']}/plots"
    payload = body(square)
    payload["sources"][0]["sha256"] = "0" * 64
    assert api.post(path + "/import", headers=headers, json=payload).status_code == 422
    assert not api.get(path, headers=headers).json()["features"]
    with Session(api.app.state.engine) as db:
        assert db.scalar(select(ImportSource)) is None
    payload = body(square)
    payload["plots"][0]["geometry"] = mapping(
        Polygon([(-47, -22), (-46, -22), (-46, -21), (-47, -22)])
    )
    assert api.post(path + "/import", headers=headers, json=payload).status_code == 422
