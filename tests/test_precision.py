import json

import pytest
from shapely.geometry import Polygon, mapping
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.geography import inspect_polygon
from core.precision import VertexEditor
from scripts.precision_report import build_report
from server.models import PlotVersion
from tests.conftest import account
from tests.test_geography import body


def test_precision_mathematical_references():
    report = build_report()
    assert report["computational_tests_passed"], json.dumps(
        [c for c in report["checks"] if not c["passed"]]
    )
    assert not report["absolute_field_centimeter_accuracy_validated"]


def test_dynamic_datum_is_not_silently_assumed():
    with pytest.raises(ValueError, match="época"):
        inspect_polygon(
            mapping(Polygon([(-47, -22), (-46.999, -22), (-46.999, -21.999), (-47, -22)])), 7912
        )


def test_vertical_and_rtk_metadata_are_preserved_without_accuracy_claims():
    geometry = mapping(
        Polygon(
            [
                (-47, -22, 600.123456789),
                (-46.999, -22, 600.123456789),
                (-46.999, -21.999, 600.123456789),
                (-47, -22, 600.123456789),
            ]
        )
    )
    result = inspect_polygon(
        geometry,
        4326,
        metadata={
            "solution": "FIX",
            "epoch": 2025.25,
            "horizontal_accuracy_m": 0.008,
            "base_coordinates": [0, 0, 0],
        },
    )
    assert result.source_geometry == geometry
    assert result.precision_report["source_metadata"]["solution"] == "FIX"
    assert result.precision_report["vertical_transformation"] == "not_performed"
    assert not result.precision_report["absolute_centimeter_accuracy_validated"]


def test_numeric_edit_version_conflict_and_original_history(api):
    geometry = mapping(
        Polygon(
            [
                (300000.000123, 7500000.000123),
                (300100.000123, 7500000.000123),
                (300100.000123, 7500100.000123),
                (300000.000123, 7500100.000123),
            ]
        )
    )
    _, headers, _ = account(api)
    farm = api.post("/farms", headers=headers, json={"name": "Precisão"}).json()
    path = f"/farms/{farm['id']}/plots"
    payload = body(geometry)
    saved = api.post(path + "/import", headers=headers, json=payload)
    assert saved.status_code == 201, saved.text
    plot = saved.json()["created"][0]
    editor = VertexEditor(geometry, "EPSG:31983")
    editor.move_vertex((0, 0, 0), 0.001, 90)
    result = editor.validate()
    revision = {
        **payload["plots"][0],
        "expected_revision": 1,
        "original_geometry": editor.geometry,
        "geometry": result.geometry,
    }
    updated = api.put(path + f"/{plot['id']}/geometry", headers=headers, json=revision)
    assert updated.status_code == 200, updated.text
    assert updated.json()["properties"]["revision"] == 2
    assert (
        api.put(path + f"/{plot['id']}/geometry", headers=headers, json=revision).status_code == 409
    )
    history = api.get(path + f"/{plot['id']}/versions", headers=headers).json()
    assert len(history) == 2
    with Session(api.app.state.engine) as db:
        rows = list(db.scalars(select(PlotVersion).order_by(PlotVersion.revision)))
        assert (
            rows[0].native_geometry["geometry"]["coordinates"][0][0][0][0]
            == geometry["coordinates"][0][0][0]
        )
        assert (
            rows[1].native_geometry["geometry"]["coordinates"][0][0][0][0]
            == editor.geometry["coordinates"][0][0][0]
        )
