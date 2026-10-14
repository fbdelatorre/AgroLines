import base64
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from core.imports import import_polygons
from core.local_projects import LocalProject
from core.precision import VertexEditor
from server.config import Settings
from server.db import Base
from server.main import create_app
from server.models import ImportSource, Permission, PlotVersion, User
from tests.conftest import account

results = {}
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    path = root / "synthetic.geojson"
    canary = "SYNTHETIC_PERSONAL_DATA_ONLY"
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [300000.000123, 7500000.000123],
                [300100.000123, 7500000.000123],
                [300100.000123, 7500100.000123],
                [300000.000123, 7500000.000123],
            ]
        ],
    }
    path.write_text(
        json.dumps(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "name": "Synthetic privacy boundary",
                    "contact": "synthetic@example.test",
                },
                "extra_metadata_not_rendered": canary,
                "crs": {"properties": {"name": "EPSG:32723"}},
            }
        )
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("No network permitted")

    with patch("socket.socket.connect", forbidden), patch("socket.getaddrinfo", forbidden):
        project = LocalProject.create(root / "project.agrolines", "Synthetic privacy audit")
        project.import_files([path], acknowledge_warnings=True)
        feature = project.features()[0]
        source = json.loads(project.db.execute("SELECT payload FROM source").fetchone()[0])
        results["original_archive_contains_unrendered_metadata"] = (
            canary in base64.b64decode(source["content_base64"]).decode()
        )
        results["sqlite_has_plaintext_contact_attribute"] = (
            b"synthetic@example.test" in (root / "project.agrolines").read_bytes()
        )
        results["sqlite_standard_unencrypted_header"] = (
            (root / "project.agrolines").read_bytes().startswith(b"SQLite format 3\x00")
        )
        editor = VertexEditor(feature["original_geometry"], feature["source_crs"], project.work_crs)
        editor.move_vertex(next(editor.vertices())[0], 0.001, 90)
        project.save_geometry(feature["id"], editor.source_geometry(), 1)
        results["previous_revision_retains_contact_attribute"] = (
            project.history(feature["id"])[0][1]["attributes"]["contact"]
            == "synthetic@example.test"
        )
        try:
            project.db.execute("DELETE FROM revision")
            results["individual_revision_deletion_blocked"] = False
        except sqlite3.IntegrityError:
            project.db.rollback()
            results["individual_revision_deletion_blocked"] = True
        project.backup(root / "backup.agrolines")
        results["backup_copies_plaintext_personal_attribute"] = (
            b"synthetic@example.test" in (root / "backup.agrolines").read_bytes()
        )
        project.close()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with TestClient(create_app(Settings(database_url="sqlite://"), engine)) as api:
        owner, oh, _ = account(api, "privacy-owner@example.com")
        viewer, vh, _ = account(api, "privacy-viewer@example.com")
        farm = api.post("/farms", headers=oh, json={"name": "Synthetic privacy farm"}).json()
        preview = import_polygons([path])
        saved = api.post(
            f"/farms/{farm['id']}/plots/import", headers=oh, json=preview.payload(True)
        )
        assert saved.status_code == 201
        with Session(engine) as db:
            source_id = db.scalar(select(ImportSource)).id
        invite = api.post(
            f"/farms/{farm['id']}/invitations",
            headers=oh,
            json={"user_id": viewer["id"], "scopes": [{"role": "viewer"}]},
        ).json()
        assert api.post(f"/invitations/{invite['id']}/accept", headers=vh).status_code == 200
        original = api.get(f"/farms/{farm['id']}/sources/{source_id}", headers=vh)
        results["whole_farm_viewer_can_retrieve_original_source"] = original.status_code == 200
        results["viewer_original_includes_unrendered_metadata"] = (
            canary in base64.b64decode(original.json()["content_base64"]).decode()
        )
        with Session(engine) as db:
            permission_id = db.scalar(select(Permission)).id
        assert api.delete(f"/permissions/{permission_id}", headers=oh).status_code == 204
        results["revocation_blocks_future_source_request"] = (
            api.get(f"/farms/{farm['id']}/sources/{source_id}", headers=vh).status_code == 404
        )
        with Session(engine) as db:
            results["revocation_keeps_server_geometry_history"] = (
                db.scalar(select(PlotVersion)) is not None
            )
        results["no_delete_me_route"] = api.delete("/auth/me", headers=oh).status_code == 405
        assert api.post("/auth/logout", headers=oh).status_code == 204
        with Session(engine) as db:
            results["logout_keeps_account_record"] = db.get(User, owner["id"]) is not None
    engine.dispose()
results["all_expected_findings_confirmed"] = all(results.values())
print(json.dumps(results, indent=2))
assert results["all_expected_findings_confirmed"]
