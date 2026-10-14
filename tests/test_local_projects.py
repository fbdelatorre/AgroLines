import json
import socket

import pytest

from core.licensing import DevelopmentLicense, Entitlements, Module
from core.local_projects import LocalProject, RevisionConflict
from core.precision import VertexEditor


@pytest.fixture
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network access forbidden in offline tests")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)


@pytest.fixture
def vector(tmp_path):
    path = tmp_path / "boundary.geojson"
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [300000.000123, 7500000.000123, 600.123456789],
                [300100.000123, 7500000.000123, 600.123456789],
                [300100.000123, 7500100.000123, 600.123456789],
                [300000.000123, 7500000.000123, 600.123456789],
            ]
        ],
    }
    path.write_text(
        json.dumps(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {"name": "Synthetic"},
                "crs": {"properties": {"name": "EPSG:32723"}},
            }
        )
    )
    return path, geometry


def test_offline_import_edit_reopen_backup_restore(offline, vector, tmp_path):
    path, geometry = vector
    project_path = tmp_path / "project.agrolines"
    project = LocalProject.create(project_path, "Local")
    project.import_files([path], acknowledge_warnings=True)
    feature = project.features()[0]
    assert feature["original_geometry"] == geometry
    assert project.db.execute("SELECT COUNT(*) FROM source").fetchone()[0] == 1
    editor = VertexEditor(geometry, feature["source_crs"], project.work_crs)
    location = next(editor.vertices())[0]
    editor.move_vertex(location, 0.001, 90)
    edited = editor.source_geometry()
    project.save_geometry(feature["id"], edited, 1)
    project.backup(tmp_path / "backup.agrolines")
    project.close()
    reopened = LocalProject(project_path)
    assert reopened.features()[0]["original_geometry"] == edited
    assert reopened.history(feature["id"])[0][1]["original_geometry"] == geometry
    assert len(reopened.history(feature["id"])) == 2
    assert reopened.features()[0]["precision_report"]["source_metadata"] == feature["metadata"]
    assert reopened.db.execute("SELECT COUNT(*) FROM event").fetchone()[0] == 2
    reopened.close()
    restored = LocalProject.restore(tmp_path / "backup.agrolines", tmp_path / "restored.agrolines")
    assert restored.features()[0]["original_geometry"] == edited
    restored.close()


def test_conflict_does_not_overwrite_or_append(offline, vector, tmp_path):
    path, geometry = vector
    a = LocalProject.create(tmp_path / "project", "Local")
    a.import_files([path], acknowledge_warnings=True)
    feature = a.features()[0]
    b = LocalProject(a.path)
    a.save_geometry(feature["id"], geometry, 1)
    with pytest.raises(RevisionConflict):
        b.save_geometry(feature["id"], geometry, 1)
    assert len(b.history(feature["id"])) == 2
    a.close()
    b.close()


def test_atomic_import_and_non_destructive_create(offline, vector, tmp_path):
    path, _ = vector
    project = LocalProject.create(tmp_path / "project", "Local")
    with pytest.raises(ValueError):
        project.import_files([path, tmp_path / "missing.shp"])
    assert project.features() == []
    with pytest.raises(FileExistsError):
        LocalProject.create(project.path, "Overwrite")
    with pytest.raises(FileExistsError):
        project.backup(project.path)
    assert project.name == "Local"
    project.close()


def test_development_and_module_boundary(offline, tmp_path):
    assert DevelopmentLicense().verify().permits(Module.GEOMETRY)
    assert not Entitlements("basic", frozenset({Module.PROJECTS}), True, "").permits(
        Module.GEOMETRY
    )
    assert not Entitlements("expired", frozenset(Module), False, "").permits(Module.PROJECTS)

    class Denied:
        def verify(self):
            return Entitlements("invalid", frozenset(), False, "Invalid signature")

    project = LocalProject.create(tmp_path / "project", "Local")
    project.close()
    with pytest.raises(PermissionError):
        LocalProject(project.path, Denied())
    with pytest.raises(PermissionError):
        LocalProject.create(tmp_path / "denied", "Denied", license_verifier=Denied())
    assert not (tmp_path / "denied").exists()

    class ProjectsOnly:
        def verify(self):
            return Entitlements("basic", frozenset({Module.PROJECTS}), True, "")

    restricted = LocalProject(project.path, ProjectsOnly())
    with pytest.raises(PermissionError):
        restricted.import_files([])
    with pytest.raises(PermissionError):
        restricted.backup(tmp_path / "denied-backup")
    restricted.close()
    assert not (tmp_path / "denied-backup").exists()


@pytest.mark.parametrize("suffix,driver", [(".shp", "ESRI Shapefile"), (".gpkg", "GPKG")])
def test_native_formats_offline(offline, tmp_path, suffix, driver):
    import fiona

    path = tmp_path / ("boundary" + suffix)
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [300000, 7500000],
                [300100, 7500000],
                [300100, 7500100],
                [300000, 7500000],
            ]
        ],
    }
    with fiona.open(
        path,
        "w",
        driver=driver,
        crs="EPSG:31983",
        schema={"geometry": "Polygon", "properties": {"name": "str"}},
    ) as sink:
        sink.write({"geometry": geometry, "properties": {"name": "Synthetic"}})
    project = LocalProject.create(tmp_path / "project", "Local")
    project.import_files([path], source_crs="EPSG:4326", acknowledge_warnings=True)
    assert "SIRGAS" in project.features()[0]["source_crs"]
    project.close()


@pytest.mark.parametrize("compressed", [False, True])
def test_kml_kmz_offline(offline, tmp_path, compressed):
    import zipfile

    data = (
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark>'
        "<Polygon><outerBoundaryIs><LinearRing><coordinates>"
        "-47,-22 -46.999,-22 -46.999,-21.999 -47,-22"
        "</coordinates></LinearRing></outerBoundaryIs></Polygon>"
        "</Placemark></Document></kml>"
    )
    path = tmp_path / ("boundary.kmz" if compressed else "boundary.kml")
    if compressed:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("doc.kml", data)
    else:
        path.write_text(data)
    project = LocalProject.create(tmp_path / "project", "Local")
    project.import_files([path], acknowledge_warnings=True)
    assert len(project.features()) == 1
    project.close()


def test_storage_rolls_back_failed_batch_and_immutable_history(
    offline, vector, tmp_path, monkeypatch
):
    import sqlite3

    path, _ = vector
    project = LocalProject.create(tmp_path / "project", "Local")
    original = project._append

    def fail(*args):
        original(*args)
        raise RuntimeError("Simulated failure before commit")

    monkeypatch.setattr(project, "_append", fail)
    with pytest.raises(RuntimeError):
        project.import_files([path], acknowledge_warnings=True)
    assert project.features() == []
    assert project.db.execute("SELECT COUNT(*) FROM source").fetchone()[0] == 0
    monkeypatch.setattr(project, "_append", original)
    project.import_files([path], acknowledge_warnings=True)
    with pytest.raises(sqlite3.IntegrityError):
        project.db.execute("DELETE FROM revision")
    project.db.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        project.db.execute("UPDATE source SET payload='{}'")
    project.db.rollback()
    project.close()
