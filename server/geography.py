"""Authorized, transactional polygon import and version retrieval."""

import base64
import hashlib
import json

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from pyproj import CRS
from sqlalchemy import select

from core.geography import inspect_polygon, overlap_area
from server import security
from server.dependencies import DB, Actor
from server.models import (
    ImportSource,
    Operation,
    Plot,
    PlotOperation,
    PlotSeason,
    PlotVersion,
    Season,
    VersionSource,
)
from server.permissions import can, farm_for

router = APIRouter(tags=["Cadastro geográfico"])


class SourceInput(BaseModel):
    name: str = Field(min_length=1, max_length=255, pattern=r"^[^/\\]+$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content_base64: str = Field(max_length=12_000_000)


class PolygonInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    geometry: dict
    original_geometry: dict
    source_crs: str = Field(min_length=1, max_length=16384)
    metadata: dict = Field(default_factory=dict)
    work_crs: str | None = Field(default=None, max_length=16384)
    source_ids: list[int] = Field(default_factory=list, max_length=32)
    attributes: dict = Field(default_factory=dict)


class ImportInput(BaseModel):
    sources: list[SourceInput] = Field(default_factory=list, max_length=32)
    plots: list[PolygonInput] = Field(min_length=1, max_length=100)
    acknowledge_overlaps: bool = False
    repair_invalid: bool = False


class ScopeLinks(BaseModel):
    season_ids: list[str] = Field(default_factory=list, max_length=100)
    operation_ids: list[str] = Field(default_factory=list, max_length=100)


def version_json(plot, version):
    return {
        "type": "Feature",
        "id": plot.id,
        "geometry": version.geometry,
        "properties": {
            "name": plot.name,
            "revision": version.revision,
            "area_m2": version.area_m2,
            "perimeter_m": version.perimeter_m,
            "metric_crs": version.metric_crs,
            "actor_id": version.actor_id,
            "created": version.created,
            "attributes": version.attributes,
            "original_geometry": version.original_geometry,
            "source_crs": version.source_crs,
            "precision_report": version.precision_report,
        },
    }


def plot_versions(db, farm_id):
    return list(
        db.execute(
            select(Plot, PlotVersion)
            .join(
                PlotVersion,
                (PlotVersion.plot_id == Plot.id) & (PlotVersion.revision == Plot.current_revision),
            )
            .where(Plot.farm_id == farm_id)
        ).all()
    )


def read_scope(db, user_id, farm_id, season_id, operation_id):
    farm = farm_for(db, user_id, farm_id)
    if season_id:
        season = db.get(Season, season_id)
        if not season or season.farm_id != farm_id:
            raise HTTPException(404, "Escopo não encontrado.")
    if operation_id:
        operation = db.get(Operation, operation_id)
        if not season_id or not operation or operation.season_id != season_id:
            raise HTTPException(404, "Escopo não encontrado.")
    if not can(db, user_id, farm, "read", season_id, operation_id):
        raise HTTPException(404, "Geometrias não encontradas ou acesso não autorizado.")
    return farm


@router.get("/farms/{farm_id}/plots")
def list_plots(
    farm_id: str,
    actor: Actor,
    db: DB,
    season_id: str | None = None,
    operation_id: str | None = None,
):
    read_scope(db, actor[0].id, farm_id, season_id, operation_id)
    rows = plot_versions(db, farm_id)
    permitted = None
    if operation_id:
        permitted = set(
            db.scalars(
                select(PlotOperation.plot_id).where(PlotOperation.operation_id == operation_id)
            )
        )
    elif season_id:
        permitted = set(
            db.scalars(select(PlotSeason.plot_id).where(PlotSeason.season_id == season_id))
        )
    return {
        "type": "FeatureCollection",
        "features": [version_json(p, v) for p, v in rows if permitted is None or p.id in permitted],
    }


@router.post("/farms/{farm_id}/plots/import", status_code=201)
def import_plots(farm_id: str, body: ImportInput, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "edit", lock=True)
    normalized = []
    try:
        for item in body.plots:
            if len(json.dumps(item.original_geometry, allow_nan=False)) > 8 * 1024 * 1024:
                raise ValueError("Geometria original acima de 8 MiB.")
            if len(json.dumps(item.metadata, allow_nan=False)) > 65536:
                raise ValueError("Metadados excedem 64 KiB.")
            if not item.name.strip():
                raise ValueError("Nome do talhão obrigatório.")
            if len(json.dumps(item.attributes, allow_nan=False)) > 65536:
                raise ValueError("Atributos excedem 64 KiB.")
            result = inspect_polygon(
                item.original_geometry,
                item.source_crs,
                body.repair_invalid,
                work_crs=item.work_crs,
                metadata=item.metadata,
            )
            # Server recomputes the transformation and all metrics from the original.
            from shapely.geometry import shape

            if not shape(result.geometry).equals_exact(shape(item.geometry), 1e-9, normalize=True):
                raise ValueError("Prévia não corresponde à geometria original e ao SRC informado.")
            if any(i < 0 or i >= len(body.sources) for i in item.source_ids):
                raise ValueError("Referência de arquivo original inválida.")
            normalized.append((item, result))
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(422, str(exc)) from None
    existing = plot_versions(db, farm.id)
    fingerprints = {p.fingerprint for p, _ in existing}
    created, duplicates = [], []
    accepted = []
    for item, result in normalized:
        if result.fingerprint in fingerprints:
            duplicates.append(item.name)
            continue
        if not body.acknowledge_overlaps:
            if any(overlap_area(result.geometry, v.geometry) > 0.01 for _, v in existing) or any(
                overlap_area(result.geometry, r.geometry) > 0.01 for _, r in accepted
            ):
                raise HTTPException(
                    409, "Sobreposição detectada. Confira a prévia e confirme explicitamente."
                )
        fingerprints.add(result.fingerprint)
        accepted.append((item, result))
    source_rows = []
    total = 0
    for source in body.sources:
        try:
            content = base64.b64decode(source.content_base64, validate=True)
        except ValueError:
            raise HTTPException(422, "Arquivo original inválido.") from None
        total += len(content)
        if (
            len(content) > 8 * 1024 * 1024
            or total > 32 * 1024 * 1024
            or hashlib.sha256(content).hexdigest() != source.sha256
        ):
            raise HTTPException(422, "Limite ou hash do arquivo original inválido.")
        row = db.scalar(
            select(ImportSource).where(
                ImportSource.farm_id == farm.id, ImportSource.sha256 == source.sha256
            )
        )
        if row is None:
            row = ImportSource(
                farm_id=farm.id,
                actor_id=actor[0].id,
                name=source.name,
                sha256=source.sha256,
                content=content,
                created=security.now(),
            )
            db.add(row)
            db.flush()
        source_rows.append(row)
    for item, result in accepted:
        plot = Plot(
            farm_id=farm.id,
            name=item.name.strip(),
            current_revision=1,
            fingerprint=result.fingerprint,
        )
        db.add(plot)
        db.flush()
        version = PlotVersion(
            plot_id=plot.id,
            revision=1,
            actor_id=actor[0].id,
            created=security.now(),
            geometry=result.geometry,
            original_geometry=result.source_geometry,
            native_geometry={
                "geometry": result.native_geometry,
                "srid": CRS.from_user_input(result.source_crs).to_epsg() or 0,
            },
            precision_report=result.precision_report,
            source_crs=result.source_crs,
            metric_crs=result.metric_crs,
            attributes=item.attributes,
            area_m2=result.area_m2,
            perimeter_m=result.perimeter_m,
        )
        db.add(version)
        db.flush()
        for index in set(item.source_ids):
            db.add(VersionSource(version_id=version.id, source_id=source_rows[index].id))
        security.audit(db, actor[0].id, "plot.import", plot.id, farm.id)
        created.append(version_json(plot, version))
    return {"created": created, "duplicates": duplicates}


@router.post("/farms/{farm_id}/plots/{plot_id}/scopes", status_code=204)
def link_scopes(farm_id: str, plot_id: str, body: ScopeLinks, actor: Actor, db: DB):
    farm_for(db, actor[0].id, farm_id, "edit", lock=True)
    plot = db.get(Plot, plot_id)
    if not plot or plot.farm_id != farm_id:
        raise HTTPException(404, "Talhão não encontrado.")
    for season_id in set(body.season_ids):
        season = db.get(Season, season_id)
        if not season or season.farm_id != farm_id:
            raise HTTPException(404, "Safra não encontrada.")
        if not db.get(PlotSeason, (plot_id, season_id)):
            db.add(PlotSeason(plot_id=plot_id, season_id=season_id))
    for operation_id in set(body.operation_ids):
        operation = db.get(Operation, operation_id)
        if not operation or db.get(Season, operation.season_id).farm_id != farm_id:
            raise HTTPException(404, "Operação não encontrada.")
        if not db.get(PlotOperation, (plot_id, operation_id)):
            db.add(PlotOperation(plot_id=plot_id, operation_id=operation_id))
        if not db.get(PlotSeason, (plot_id, operation.season_id)):
            db.add(PlotSeason(plot_id=plot_id, season_id=operation.season_id))
    security.audit(db, actor[0].id, "plot.scope.link", plot_id, farm_id)
    return Response(status_code=204)


@router.get("/farms/{farm_id}/plots/{plot_id}/versions")
def history(farm_id: str, plot_id: str, actor: Actor, db: DB):
    read_scope(db, actor[0].id, farm_id, None, None)
    plot = db.get(Plot, plot_id)
    if not plot or plot.farm_id != farm_id:
        raise HTTPException(404, "Talhão não encontrado.")
    return [
        version_json(plot, version)
        for version in db.scalars(
            select(PlotVersion).where(PlotVersion.plot_id == plot_id).order_by(PlotVersion.revision)
        )
    ]


@router.get("/farms/{farm_id}/sources/{source_id}")
def original_source(farm_id: str, source_id: str, actor: Actor, db: DB):
    read_scope(db, actor[0].id, farm_id, None, None)
    source = db.get(ImportSource, source_id)
    if not source or source.farm_id != farm_id:
        raise HTTPException(404, "Arquivo não encontrado.")
    return {
        "name": source.name,
        "sha256": source.sha256,
        "content_base64": base64.b64encode(source.content).decode(),
    }


class RevisionInput(PolygonInput):
    acknowledge_overlaps: bool = False
    expected_revision: int = Field(ge=1)


@router.put("/farms/{farm_id}/plots/{plot_id}/geometry")
def revise_geometry(farm_id: str, plot_id: str, body: RevisionInput, actor: Actor, db: DB):
    farm = farm_for(db, actor[0].id, farm_id, "edit", lock=True)
    plot = db.get(Plot, plot_id)
    if not plot or plot.farm_id != farm_id:
        raise HTTPException(404, "Talhão não encontrado.")
    if plot.current_revision != body.expected_revision:
        raise HTTPException(409, "Versão alterada no servidor. Recarregue antes de editar.")
    previous = db.scalar(
        select(PlotVersion).where(
            PlotVersion.plot_id == plot.id, PlotVersion.revision == plot.current_revision
        )
    )
    if CRS.from_user_input(body.source_crs) != CRS.from_user_input(previous.source_crs):
        raise HTTPException(422, "A edição não pode substituir o SRC original silenciosamente.")
    try:
        result = inspect_polygon(
            body.original_geometry, body.source_crs, work_crs=body.work_crs, metadata=body.metadata
        )
        from shapely.geometry import shape

        if not shape(result.geometry).equals_exact(shape(body.geometry), 1e-9, normalize=True):
            raise ValueError("Prévia não corresponde à geometria editada.")
        if len(json.dumps(body.attributes, allow_nan=False)) > 65536:
            raise ValueError("Atributos excedem o limite.")
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from None
    duplicates = db.scalar(
        select(Plot).where(
            Plot.farm_id == farm.id, Plot.fingerprint == result.fingerprint, Plot.id != plot.id
        )
    )
    if duplicates:
        raise HTTPException(409, "Geometria duplica outro talhão.")
    if not body.acknowledge_overlaps and any(
        p.id != plot.id and overlap_area(result.geometry, v.geometry) > 0.01
        for p, v in plot_versions(db, farm.id)
    ):
        raise HTTPException(409, "Sobreposição na edição. Confira e autorize explicitamente.")
    plot.current_revision += 1
    plot.fingerprint = result.fingerprint
    version = PlotVersion(
        plot_id=plot.id,
        revision=plot.current_revision,
        actor_id=actor[0].id,
        created=security.now(),
        geometry=result.geometry,
        original_geometry=result.source_geometry,
        native_geometry={
            "geometry": result.native_geometry,
            "srid": CRS.from_user_input(result.source_crs).to_epsg() or 0,
        },
        source_crs=result.source_crs,
        metric_crs=result.metric_crs,
        attributes=body.attributes,
        area_m2=result.area_m2,
        perimeter_m=result.perimeter_m,
        precision_report=result.precision_report,
    )
    db.add(version)
    db.flush()
    security.audit(db, actor[0].id, "plot.geometry.revise", plot.id, farm.id)
    return version_json(plot, version)
