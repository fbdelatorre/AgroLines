"""Bounded local vector import. No remote datasets or implicit unknown CRS."""

import base64
import hashlib
import json
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

import fiona
from defusedxml.ElementTree import fromstring
from shapely.geometry import mapping, shape

from core.geography import inspect_polygon, overlap_area

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_BATCH_BYTES = 32 * 1024 * 1024
MAX_FEATURES = 100
ALLOWED = {".shp", ".gpkg", ".kml", ".kmz", ".geojson", ".json"}


@dataclass
class ImportPreview:
    plots: list[dict]
    sources: list[dict]
    warnings: list[str]
    repair_invalid: bool = False

    def payload(self, acknowledge_overlaps=False):
        return {**asdict(self), "acknowledge_overlaps": acknowledge_overlaps}


def file_bytes(path):
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Arquivo ausente ou maior que 8 MiB.")
    return path.read_bytes()


def check_kml(data):
    try:
        root = fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except Exception as exc:
        raise ValueError("KML inválido ou com entidades XML proibidas.") from exc
    if any(
        element.tag.rsplit("}", 1)[-1].lower() in ("networklink", "href") for element in root.iter()
    ):
        raise ValueError("KML com referências externas não é aceito.")


def datasets(path, override):
    suffix = path.suffix.lower()
    if suffix in (".json", ".geojson"):
        raw = json.loads(file_bytes(path))
        declared = raw.get("crs", {}).get("properties", {}).get("name")
        crs = override or declared
        if not crs:
            raise ValueError("GeoJSON sem declaração de SRC: informe o SRC, inclusive EPSG:4326.")
        features = raw.get("features", []) if raw.get("type") == "FeatureCollection" else [raw]
        yield crs, features
        return
    if suffix == ".kmz":
        with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory() as directory:
            if (
                len(archive.infolist()) > 100
                or sum(x.file_size for x in archive.infolist()) > MAX_FILE_BYTES
            ):
                raise ValueError("KMZ excede limites de descompressão.")
            names = [x for x in archive.namelist() if x.lower().endswith(".kml")]
            if len(names) != 1:
                raise ValueError("KMZ deve conter exatamente um documento KML neste incremento.")
            data = archive.read(names[0])
            check_kml(data)
            local = Path(directory, "document.kml")
            local.write_bytes(data)
            yield from datasets(local, override)
        return
    if suffix == ".kml":
        check_kml(file_bytes(path))
    for layer in fiona.listlayers(str(path)):
        with fiona.open(str(path), layer=layer, allow_unsupported_drivers=True) as source:
            # KML declares geographic WGS84 by specification; other formats must
            # carry a CRS or receive an explicit operator override.
            crs = override or ("EPSG:4326" if suffix == ".kml" else source.crs_wkt)
            if not crs:
                raise ValueError("SRC ausente: informe o SRC de origem.")
            features = []
            for record in source:
                if len(features) >= MAX_FEATURES:
                    raise ValueError("Importação limitada a 100 polígonos por lote.")
                features.append(
                    {
                        "type": "Feature",
                        "geometry": mapping(shape(record.geometry)),
                        "properties": dict(record.properties),
                    }
                )
            yield crs, features


def import_polygons(paths, source_crs=None, repair=False, work_crs=None):
    selected = [Path(p) for p in paths]
    if not selected or len(selected) > 32:
        raise ValueError("Selecione de 1 a 32 arquivos locais.")
    sources, plots, warnings = [], [], []
    total = 0
    seen_files = set()
    datasets_selected = [p for p in selected if p.suffix.lower() in ALLOWED]
    if not datasets_selected:
        raise ValueError("Selecione SHP, GPKG, KML, KMZ ou GeoJSON.")
    for path in datasets_selected:
        companions = [path]
        if path.suffix.lower() == ".shp":
            companions = []
            for extension in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                candidate = next(
                    (
                        p
                        for p in path.parent.iterdir()
                        if p.stem == path.stem and p.suffix.lower() == extension
                    ),
                    None,
                )
                if candidate is None:
                    if extension in (".shp", ".shx", ".dbf") or (
                        extension == ".prj" and not source_crs
                    ):
                        raise ValueError("Shapefile incompleto: falta " + extension)
                    continue
                companions.append(candidate)
        source_ids = []
        for companion in companions:
            resolved = companion.resolve()
            content = file_bytes(companion)
            if resolved not in seen_files:
                total += len(content)
                if total > MAX_BATCH_BYTES:
                    raise ValueError("Lote acima de 32 MiB.")
                sources.append(
                    {
                        "name": companion.name,
                        "sha256": hashlib.sha256(content).hexdigest(),
                        "content_base64": base64.b64encode(content).decode(),
                    }
                )
                seen_files.add(resolved)
            source_ids.append(
                next(
                    i
                    for i, s in enumerate(sources)
                    if s["sha256"] == hashlib.sha256(content).hexdigest()
                    and s["name"] == companion.name
                )
            )
        for crs, records in datasets(path, source_crs):
            for record in records:
                if len(plots) >= MAX_FEATURES:
                    raise ValueError("Importação limitada a 100 polígonos por lote.")
                properties = record.get("properties") or {}
                result = inspect_polygon(
                    record.get("geometry") or record,
                    crs,
                    repair,
                    work_crs=work_crs,
                    metadata=properties,
                )
                attributes = json.loads(json.dumps(properties, default=str, allow_nan=False))
                if len(json.dumps(attributes)) > 65536:
                    raise ValueError("Atributos acima de 64 KiB por polígono.")
                name = str(
                    properties.get("name")
                    or properties.get("nome")
                    or f"{path.stem} {len(plots) + 1}"
                )[:120]
                plots.append(
                    {
                        "name": name,
                        "geometry": result.geometry,
                        "original_geometry": result.source_geometry,
                        "source_crs": result.source_crs,
                        "source_ids": source_ids,
                        "attributes": attributes,
                        "area_m2": result.area_m2,
                        "perimeter_m": result.perimeter_m,
                        "metric_crs": result.metric_crs,
                        "work_crs": work_crs,
                        "metadata": attributes,
                        "precision_report": result.precision_report,
                    }
                )
                warnings.extend(result.warnings)
    for i, plot in enumerate(plots):
        for other in plots[:i]:
            if overlap_area(plot["geometry"], other["geometry"]) > 0.01:
                warnings.append(f"Sobreposição: {plot['name']} / {other['name']}.")
    if not plots:
        raise ValueError("Nenhum polígono encontrado.")
    return ImportPreview(plots, sources, sorted(set(warnings)), repair)
