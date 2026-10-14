"""Standalone SQLite projects. No API, account, network or PostgreSQL dependency."""

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from pyproj import CRS, network

from core.geography import inspect_polygon
from core.imports import import_polygons
from core.licensing import DevelopmentLicense, Module

SCHEMA = """
CREATE TABLE project(id TEXT PRIMARY KEY, name TEXT NOT NULL, work_crs TEXT NOT NULL);
CREATE TABLE feature(id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE revision(feature_id TEXT REFERENCES feature(id), number INTEGER NOT NULL,
 payload TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY(feature_id, number));
CREATE TABLE source(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE event(id TEXT PRIMARY KEY, feature_id TEXT NOT NULL, revision INTEGER NOT NULL,
 state TEXT NOT NULL DEFAULT 'local' CHECK(state IN ('local','pending','conflict','synced')),
 FOREIGN KEY(feature_id, revision) REFERENCES revision(feature_id, number));
CREATE TRIGGER revision_no_update BEFORE UPDATE ON revision BEGIN
 SELECT RAISE(ABORT,'Revisions are immutable'); END;
CREATE TRIGGER revision_no_delete BEFORE DELETE ON revision BEGIN
 SELECT RAISE(ABORT,'Revisions are immutable'); END;
CREATE TRIGGER source_no_update BEFORE UPDATE ON source BEGIN
 SELECT RAISE(ABORT,'Sources are immutable'); END;
CREATE TRIGGER source_no_delete BEFORE DELETE ON source BEGIN
 SELECT RAISE(ABORT,'Sources are immutable'); END;
PRAGMA user_version=1;
"""


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class RevisionConflict(ValueError):
    pass


class LocalProject:
    def __init__(self, path, license_verifier=None):
        network.set_network_enabled(False)
        self.path = Path(path)
        self.license = license_verifier or DevelopmentLicense()
        self._require(Module.PROJECTS)
        # mode=rw prevents accidentally creating an empty file when opening a missing project.
        self.db = sqlite3.connect(self.path.resolve().as_uri() + "?mode=rw", uri=True)
        try:
            self.db.execute("PRAGMA foreign_keys=ON")
            self.db.execute("PRAGMA synchronous=FULL")
            if self.db.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise ValueError("Versão de projeto não suportada; arquivo preservado.")
            if self.db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("Projeto corrompido; restaure um backup em novo arquivo.")
            self.id, self.name, self.work_crs = self.db.execute("SELECT * FROM project").fetchone()
        except Exception:
            self.db.close()
            raise

    @classmethod
    def create(cls, path, name, work_crs="EPSG:32723", license_verifier=None):
        verifier = license_verifier or DevelopmentLicense()
        if not verifier.verify().permits(Module.PROJECTS):
            raise PermissionError("Módulo indisponível na licença local.")
        if not name.strip():
            raise ValueError("Informe o nome do projeto.")
        crs = CRS.from_user_input(work_crs)
        if not crs.is_projected or any(a.unit_name != "metre" for a in crs.axis_info):
            raise ValueError("O SRC de trabalho deve ser projetado em metros.")
        path = Path(path)
        # Exclusive creation: never overwrite an existing project.
        with path.open("xb"):
            pass
        try:
            with closing(sqlite3.connect(path)) as db:
                db.executescript(SCHEMA)
                with db:
                    db.execute(
                        "INSERT INTO project VALUES(?,?,?)", (str(uuid.uuid4()), name, crs.to_wkt())
                    )
            return cls(path, verifier)
        except Exception:
            path.unlink(missing_ok=True)
            raise

    def _require(self, module):
        if not self.license.verify().permits(module):
            raise PermissionError("Módulo indisponível na licença local.")

    def close(self):
        self.db.close()

    def features(self):
        self._require(Module.PROJECTS)
        rows = self.db.execute("""SELECT f.id,f.name,r.number,r.payload FROM feature f
          JOIN revision r ON r.feature_id=f.id WHERE r.number=(SELECT MAX(number)
          FROM revision WHERE feature_id=f.id) ORDER BY f.name,f.id""")
        return [dict(id=i, name=n, revision=v, **json.loads(p)) for i, n, v, p in rows]

    def history(self, feature_id):
        self._require(Module.PROJECTS)
        return [
            (v, json.loads(p))
            for v, p in self.db.execute(
                "SELECT number,payload FROM revision WHERE feature_id=? ORDER BY number",
                (feature_id,),
            )
        ]

    def _append(self, feature_id, revision, payload):
        self.db.execute(
            "INSERT INTO revision VALUES(?,?,?,?)",
            (feature_id, revision, encode(payload), datetime.now(UTC).isoformat()),
        )
        self.db.execute(
            "INSERT INTO event(id,feature_id,revision) VALUES(?,?,?)",
            (str(uuid.uuid4()), feature_id, revision),
        )

    def import_files(self, paths, source_crs=None, acknowledge_warnings=False):
        self._require(Module.GEOMETRY)
        preview = import_polygons(paths, source_crs=source_crs, work_crs=self.work_crs)
        if preview.warnings and not acknowledge_warnings:
            raise ValueError("Confirme os avisos antes de importar: " + "; ".join(preview.warnings))
        with self.db:
            ids = [str(uuid.uuid4()) for _ in preview.sources]
            for source_id, payload in zip(ids, preview.sources, strict=True):
                self.db.execute("INSERT INTO source VALUES(?,?)", (source_id, encode(payload)))
            for plot in preview.plots:
                payload = dict(plot)
                name = payload.pop("name")
                payload["source_ids"] = [ids[i] for i in plot["source_ids"]]
                feature_id = str(uuid.uuid4())
                self.db.execute("INSERT INTO feature VALUES(?,?)", (feature_id, name))
                self._append(feature_id, 1, payload)
        return preview

    def save_geometry(self, feature_id, geometry, expected_revision):
        self._require(Module.GEOMETRY)
        # Acquire write reservation before checking revision: concurrent editors cannot overwrite.
        self.db.execute("BEGIN IMMEDIATE")
        try:
            rows = self.history(feature_id)
            if not rows or rows[-1][0] != expected_revision:
                raise RevisionConflict(
                    "Projeto alterado por outro editor; recarregue e compare versões."
                )
            payload = rows[-1][1]
            result = inspect_polygon(
                geometry,
                payload["source_crs"],
                work_crs=self.work_crs,
                metadata=payload.get("metadata", payload.get("attributes")),
            )
            payload.update(
                original_geometry=result.source_geometry,
                geometry=result.geometry,
                area_m2=result.area_m2,
                perimeter_m=result.perimeter_m,
                precision_report=result.precision_report,
            )
            self._append(feature_id, expected_revision + 1, payload)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def backup(self, destination):
        self._require(Module.BACKUP)
        destination = Path(destination)
        with destination.open("xb"):
            pass
        try:
            with closing(sqlite3.connect(destination)) as target:
                self.db.backup(target)
                if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("Backup inválido.")
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    @classmethod
    def restore(cls, backup, destination, license_verifier=None):
        source = cls(backup, license_verifier)
        try:
            source.backup(destination)
        finally:
            source.close()
        return cls(destination, license_verifier)
