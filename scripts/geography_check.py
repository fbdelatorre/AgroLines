"""Real PostGIS/HTTP smoke test on a synthetic test database; never resets data."""

import argparse
import base64
import hashlib
import json
import time
from pathlib import Path
from uuid import uuid4

from shapely.geometry import Polygon, mapping
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.geography import inspect_polygon
from scripts.integration_check import request
from server.config import get_settings
from server.db import make_engine
from server.models import Plot, PlotVersion

PASSWORD = "Synthetic GIS integration 123!"


def prepare(checkpoint):
    suffix = uuid4().hex
    email = f"gis-{suffix}@example.com"
    request(
        "POST",
        "/auth/register",
        {"name": "GIS sintético", "email": email, "password": PASSWORD},
        expected=201,
    )
    login = request("POST", "/auth/login", {"email": email, "password": PASSWORD})
    token = login["access_token"]
    farm = request("POST", "/farms", {"name": "GIS sintético " + suffix}, token, 201)
    geometry = mapping(
        Polygon(
            [
                (300000.0001234568, 7500000.0001234568),
                (300100, 7500000),
                (300100, 7500100),
                (300000, 7500100),
            ]
        )
    )
    result = inspect_polygon(geometry, "EPSG:31983")
    original = json.dumps(
        {
            "type": "Feature",
            "geometry": geometry,
            "properties": {"name": "Um hectare"},
            "crs": {"type": "name", "properties": {"name": "EPSG:31983"}},
        }
    ).encode()
    payload = {
        "sources": [
            {
                "name": "synthetic.geojson",
                "sha256": hashlib.sha256(original).hexdigest(),
                "content_base64": base64.b64encode(original).decode(),
            }
        ],
        "plots": [
            {
                "name": "Um hectare",
                "geometry": result.geometry,
                "original_geometry": geometry,
                "source_crs": "EPSG:31983",
                "source_ids": [0],
                "attributes": {"synthetic": True},
            }
        ],
    }
    path = f"/farms/{farm['id']}/plots"
    saved = request("POST", path + "/import", payload, token, 201)
    assert len(saved["created"]) == 1
    repeated = request("POST", path + "/import", payload, token, 201)
    assert not repeated["created"] and repeated["duplicates"]
    checkpoint.write_text(
        json.dumps({"email": email, "farm_id": farm["id"], "plot_id": saved["created"][0]["id"]})
    )
    verify(checkpoint)


def verify(checkpoint):
    state = json.loads(checkpoint.read_text())
    # Fresh login and new DB connection also validate persisted state after restart.
    token = request("POST", "/auth/login", {"email": state["email"], "password": PASSWORD})[
        "access_token"
    ]
    collection = request("GET", f"/farms/{state['farm_id']}/plots", token=token)
    assert len(collection["features"]) == 1
    assert collection["features"][0]["id"] == state["plot_id"]
    assert abs(collection["features"][0]["properties"]["area_m2"] - 10000) < 0.1
    engine = make_engine(get_settings())
    with Session(engine) as db:
        row = db.execute(
            select(
                func.ST_IsValid(PlotVersion.geometry),
                func.ST_SRID(PlotVersion.geometry),
                func.ST_GeometryType(PlotVersion.geometry),
            )
            .join(Plot, Plot.id == PlotVersion.plot_id)
            .where(Plot.id == state["plot_id"])
        ).one()
        assert tuple(row) == (True, 4326, "ST_MultiPolygon")
        version = db.scalar(select(PlotVersion).where(PlotVersion.plot_id == state["plot_id"]))
        assert version.native_geometry["srid"] == 31983
        native = version.native_geometry["geometry"]["coordinates"][0][0][0]
        original = version.original_geometry["coordinates"][0][0]
        assert native[0] == original[0] and native[1] == original[1]
        assert version.precision_report["numeric_tolerance_m"] == 0.005
        assert not version.precision_report["absolute_centimeter_accuracy_validated"]
    engine.dispose()
    print("PostGIS polygon, metrics, original version and duplicate checks passed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="/tmp/agrolines-gis-check.json")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    for attempt in range(30):
        try:
            request("GET", "/health")
            break
        except Exception:
            if attempt == 29:
                raise
            time.sleep(0.5)
    (verify if args.verify else prepare)(Path(args.checkpoint))


if __name__ == "__main__":
    main()
