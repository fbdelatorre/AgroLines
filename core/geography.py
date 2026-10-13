"""Precision geometry: GEOS/PROJ calculations independent of map pixels."""

import hashlib
import math
from dataclasses import dataclass

from pyproj import CRS, Proj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from pyproj.transformer import TransformerGroup
from shapely import force_2d, get_coordinates, make_valid, normalize, transform
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.geometry.polygon import orient
from shapely.validation import explain_validity

MAX_VERTICES = 100_000
NUMERIC_TOLERANCE_M = 0.005


@dataclass
class GeographicPolygon:
    geometry: dict  # WGS84 presentation geometry; never authoritative for precision edits.
    native_geometry: dict  # Working geometry in the source CRS, without rounding.
    source_geometry: dict
    source_crs: str
    metric_crs: str
    area_m2: float
    perimeter_m: float
    fingerprint: str
    warnings: list[str]
    precision_report: dict


def polygonal(geometry):
    if isinstance(geometry, Polygon):
        return MultiPolygon([geometry])
    if isinstance(geometry, MultiPolygon):
        return geometry
    raise ValueError("Somente polígonos e multipolígonos são aceitos neste incremento.")


def exact_transform(source, destination):
    group = TransformerGroup(source, destination, always_xy=True, allow_ballpark=False)
    if not group.best_available or not group.transformers:
        raise ValueError("Transformação precisa indisponível: faltam grades/parâmetros PROJ.")
    return group.transformers[0]


def apply_transform(geometry, converter):
    try:
        return transform(
            geometry, lambda x, y: converter.transform(x, y, errcheck=True), interleaved=False
        )
    except Exception as exc:
        raise ValueError(
            "Transformação de coordenadas falhou; não há fallback aproximado."
        ) from exc


def inspect_polygon(data, source_crs, repair=False, work_crs=None, metadata=None):
    if not source_crs:
        raise ValueError("SRC ausente. Informe explicitamente o SRC de origem.")
    try:
        crs = CRS.from_user_input(source_crs)
        original = shape(data)
    except Exception as exc:
        raise ValueError("SRC ou geometria de origem inválido.") from exc
    if crs.datum and "dynamic" in crs.datum.type_name.lower():
        raise ValueError(
            "Datum dinâmico exige época e transformação temporal validada, ainda indisponível."
        )
    coords = get_coordinates(original, include_z=original.has_z)
    if len(coords) > MAX_VERTICES or not len(coords):
        raise ValueError("Geometria vazia ou acima do limite de 100 mil vértices.")
    if not all(math.isfinite(float(v)) for row in coords for v in row):
        raise ValueError("Coordenadas devem ser finitas.")
    warnings = []
    geometry = original
    if not geometry.is_valid:
        if not repair:
            raise ValueError("Geometria inválida: " + explain_validity(geometry))
        geometry = make_valid(geometry)
        if geometry.geom_type == "GeometryCollection":
            polygons = []
            for part in geometry.geoms:
                if isinstance(part, Polygon):
                    polygons.append(part)
                elif isinstance(part, MultiPolygon):
                    polygons.extend(part.geoms)
            geometry = MultiPolygon(polygons)
        warnings.append("Correção GEOS aplicada com confirmação; original preservado.")
    if original.has_z:
        warnings.append(
            "Cotas Z preservadas no original; cálculos são 2D, sem transformação vertical."
        )
    native = polygonal(force_2d(geometry))
    converter = exact_transform(crs, CRS.from_epsg(4326))
    canonical = polygonal(apply_transform(native, converter))
    if canonical.is_empty or not canonical.is_valid:
        raise ValueError("Geometria inválida após transformação.")
    west, south, east, north = canonical.bounds
    if not (-180 <= west <= east <= 180 and -80 <= south <= north <= 84):
        raise ValueError("Coordenadas fora do domínio WGS84/UTM suportado (-80° a 84°).")
    if east - west > 3 or north - south > 3:
        raise ValueError("Extensão excede o domínio local deste incremento (3°).")
    if work_crs:
        metric_crs = CRS.from_user_input(work_crs)
    elif crs.is_projected and all(a.unit_conversion_factor == 1 for a in crs.axis_info[:2]):
        metric_crs = crs
    else:
        center = canonical.centroid
        zone = min(60, max(1, int((center.x + 180) / 6) + 1))
        zone_name = f"{zone}{'N' if center.y >= 0 else 'S'}"
        candidates = query_utm_crs_info(
            datum_name=crs.geodetic_crs.name,
            area_of_interest=AreaOfInterest(west, south, east, north),
        )
        metric_crs = next(
            (
                candidate
                for info in candidates
                if (candidate := CRS.from_authority(info.auth_name, info.code)).utm_zone
                == zone_name
            ),
            None,
        )
        if metric_crs is None:
            raise ValueError(
                "UTM no datum original não identificado; escolha o SRC de trabalho manualmente."
            )
    if not metric_crs.is_projected or not all(
        a.unit_conversion_factor == 1 for a in metric_crs.axis_info[:2]
    ):
        raise ValueError("SRC de trabalho deve ser projetado, com unidades em metros.")
    metric_converter = exact_transform(crs, metric_crs)
    metric = native if crs == metric_crs else apply_transform(native, metric_converter)
    if metric.area <= 0:
        raise ValueError("Polígono sem área útil.")
    # Geodesic values use the SOURCE ellipsoid, not an assumed GNSS datum.
    geographic = apply_transform(native, exact_transform(crs, crs.geodetic_crs))
    geod = crs.get_geod()
    geodesic_area = geodesic_perimeter = 0.0
    for part in geographic.geoms:
        area, perimeter = geod.geometry_area_perimeter(orient(part, sign=1))
        geodesic_area += abs(area)
        geodesic_perimeter += perimeter
    metric_geographic = apply_transform(
        metric, exact_transform(metric_crs, metric_crs.geodetic_crs)
    )
    projection = Proj(metric_crs)
    factors = [projection.get_factors(x, y) for x, y in get_coordinates(metric_geographic)]
    distortion = max(max(abs(f.meridional_scale - 1), abs(f.parallel_scale - 1)) for f in factors)
    restored = apply_transform(canonical, exact_transform(CRS.from_epsg(4326), crs))
    # A consistency check, not proof of absolute datum accuracy.
    if crs.is_projected:
        factor = crs.axis_info[0].unit_conversion_factor
        roundtrip = (
            max(
                math.hypot(*(a - b))
                for a, b in zip(get_coordinates(native), get_coordinates(restored), strict=True)
            )
            * factor
        )
    else:
        roundtrip = max(
            abs(geod.inv(a[0], a[1], b[0], b[1])[2])
            for a, b in zip(get_coordinates(native), get_coordinates(restored), strict=True)
        )
    if roundtrip > NUMERIC_TOLERANCE_M:
        raise ValueError("Erro adicional de ida/volta excede 0,005 m; transformação recusada.")
    authority = metric_crs.to_authority()
    metric_label = ":".join(authority) if authority else "SRC projetado personalizado"
    report = {
        "numeric_tolerance_m": NUMERIC_TOLERANCE_M,
        "roundtrip_consistency_m": roundtrip,
        "display_transform_accuracy_m": converter.accuracy if converter.accuracy >= 0 else None,
        "work_transform_accuracy_m": metric_converter.accuracy
        if metric_converter.accuracy >= 0
        else None,
        "max_projection_scale_distortion": distortion,
        "estimated_grid_distortion_per_km_m": distortion * 1000,
        "geodesic_area_m2": geodesic_area,
        "geodesic_perimeter_m": geodesic_perimeter,
        "datum": crs.datum.name if crs.datum else None,
        "source_units": [a.unit_name for a in crs.axis_info],
        "source_metadata": metadata or {},
        "absolute_centimeter_accuracy_validated": False,
        "vertical_transformation": "not_performed",
        "metric_crs_wkt": metric_crs.to_wkt(),
    }
    warnings.append(
        "Métricas projetadas são valores de malha; exatidão centimétrica de campo não comprovada."
    )
    if converter.accuracy != 0:
        warnings.append("Visualização com incerteza declarada/desconhecida; consulte o relatório.")
    canonical = normalize(canonical)
    return GeographicPolygon(
        geometry=mapping(canonical),
        native_geometry=mapping(polygonal(geometry)),
        source_geometry=mapping(original),
        source_crs=crs.to_wkt(),
        metric_crs=metric_label,
        area_m2=metric.area,
        perimeter_m=metric.length,
        fingerprint=hashlib.sha256(canonical.wkb).hexdigest(),
        warnings=warnings,
        precision_report=report,
    )


def overlap_area(left, right):
    a, b = shape(left), shape(right)
    intersection = a.intersection(b)
    if intersection.is_empty or intersection.area == 0:
        return 0.0
    return abs(CRS.from_epsg(4326).get_geod().geometry_area_perimeter(intersection)[0])
