"""Independent mathematical/geodetic acceptance references, not field guarantees."""

import argparse
import json
import math
from pathlib import Path

from pyproj import Geod, Transformer
from shapely import affinity, buffer, from_wkb, offset_curve, to_wkb
from shapely.geometry import LineString, Point, Polygon, mapping

from core.geography import NUMERIC_TOLERANCE_M, inspect_polygon
from core.precision import VertexEditor


def build_report():
    checks = []

    def check(name, expected, actual, tolerance, reference):
        error = abs(actual - expected)
        entry = {
            "name": name,
            "reference": reference,
            "expected": expected,
            "actual": actual,
            "absolute_error": error,
            "relative_error": error / abs(expected) if expected else None,
            "tolerance": tolerance,
            "passed": error <= tolerance,
        }
        checks.append(entry)
        return entry

    for length in (1, 10, 100, 1000):
        line = LineString([(300000, 7500000), (300000 + length, 7500000)])
        check(
            f"grid distance {length} m",
            length,
            line.length,
            NUMERIC_TOLERANCE_M,
            "Euclidean Cartesian horizontal segment; source projected grid",
        )
    for offset in (0.01, 0.001):
        point = Point(300000.123456789, 7500000.987654321)
        shifted = affinity.translate(point, xoff=offset)
        check(
            f"translation {offset} m",
            offset,
            shifted.x - point.x,
            0.000001,
            "Specified Cartesian x displacement",
        )
    close = Polygon(
        [(300000, 7500000), (300000.001, 7500000), (300000.001, 7500000.001), (300000, 7500000.001)]
    )
    check("close vertices area", 0.000001, close.area, 1e-11, "1 mm square, area in square metres")
    line = LineString([(0, 0), (1000, 0)])
    parallel = offset_curve(line, 6)
    check(
        "parallel spacing",
        6,
        line.distance(parallel),
        NUMERIC_TOLERANCE_M,
        "Horizontal parallel lines, 6 metre grid spacing",
    )
    a = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    b = affinity.translate(a, xoff=5)
    check(
        "intersection area",
        50,
        a.intersection(b).area,
        1e-8,
        "Two 10 metre squares overlap over a 5 by 10 metre rectangle",
    )
    buffered = buffer(Point(0, 0), 10, quad_segs=4096)
    check(
        "buffer area",
        math.pi * 100,
        buffered.area,
        0.0001,
        "Analytic circle; polygonal chord approximation explicitly bounded",
    )
    check(
        "buffer radial error",
        10,
        math.sqrt(buffered.area / math.pi),
        NUMERIC_TOLERANCE_M,
        "Equivalent circle radius, explicitly bounded discretization",
    )
    native = mapping(
        Polygon([(300000, 7500000), (300100, 7500000), (300100, 7500100), (300000, 7500100)])
    )
    editor = VertexEditor(native, "EPSG:31983")
    original_x = next(editor.vertices())[1][0]
    for _ in range(1000):
        editor.move_vertex((0, 0, 0), 0.001, 90)
    check(
        "repeated numeric edits",
        1,
        next(editor.vertices())[1][0] - original_x,
        NUMERIC_TOLERANCE_M,
        "1000 specified 1 mm Cartesian increments",
    )
    for _ in range(1000):
        editor.undo()
    assert (
        editor.geometry["coordinates"] == VertexEditor(native, "EPSG:31983").geometry["coordinates"]
    )
    check(
        "undo loss",
        0,
        editor.comparison(),
        0,
        "Original exact float64 snapshot, no inverse pixel operation",
    )
    for _ in range(1000):
        editor.redo()
    check(
        "redo displacement",
        1,
        next(editor.vertices())[1][0] - original_x,
        NUMERIC_TOLERANCE_M,
        "Exact edited snapshot restoration",
    )
    result = inspect_polygon(native, "EPSG:31983")
    check(
        "known source grid area",
        10000,
        result.area_m2,
        1e-6,
        "Cartesian 100 by 100 metre square in declared source grid",
    )
    check(
        "known source grid perimeter",
        400,
        result.perimeter_m,
        NUMERIC_TOLERANCE_M,
        "Four exact 100 metre grid edges",
    )
    check(
        "CRS consistency",
        0,
        result.precision_report["roundtrip_consistency_m"],
        NUMERIC_TOLERANCE_M,
        "PROJ source/WGS84/source consistency only; not datum accuracy proof",
    )
    # Independent EPSG/ellipsoid origin controls in addition to roundtrip tests.
    converter = Transformer.from_crs(4326, 32631, always_xy=True)
    east, north = converter.transform(3, 0)
    check(
        "UTM central meridian origin",
        500000,
        east,
        NUMERIC_TOLERANCE_M,
        "EPSG UTM false easting at zone 31 central meridian, equator",
    )
    check(
        "UTM equator origin",
        0,
        north,
        NUMERIC_TOLERANCE_M,
        "EPSG UTM northern false northing at equator",
    )
    geod = Geod(ellps="WGS84")
    check(
        "independent equatorial geodesic",
        111319.49079327357,
        geod.inv(0, 0, 1, 0)[2],
        NUMERIC_TOLERANCE_M,
        "WGS84 equatorial arc: semi-major axis 6378137 times pi/180",
    )
    extensive = Polygon(
        [
            (
                300000 + 100 * math.cos(2 * math.pi * i / 10000),
                7500000 + 100 * math.sin(2 * math.pi * i / 10000),
            )
            for i in range(10000)
        ]
    )
    expected = 10000 * 10000 * math.sin(2 * math.pi / 10000) / 2
    check(
        "10000 vertices polygon area",
        expected,
        extensive.area,
        0.00001,
        "Analytic area of a regular 10000-sided polygon of radius 100 m",
    )
    recovered = from_wkb(to_wkb(extensive))
    check(
        "binary coordinate preservation",
        0,
        extensive.hausdorff_distance(recovered),
        0,
        "Float64 WKB lossless roundtrip",
    )
    return {
        "computational_tests_passed": all(c["passed"] for c in checks),
        "absolute_field_centimeter_accuracy_validated": False,
        "notes": [
            "Grid distances are not ground distances; projection, height, datum, epoch "
            "and source uncertainty remain separate.",
            "Buffer/offset fixtures validate library primitives; agricultural planning "
            "algorithms and monitor exports are not implemented.",
            "No centroid/projection/roundtrip test establishes RTK absolute accuracy.",
        ],
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="precision-report.json")
    args = parser.parse_args()
    report = build_report()
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"Precision references: {sum(c['passed'] for c in report['checks'])}/"
        f"{len(report['checks'])} passed; field accuracy remains unvalidated."
    )
    if not report["computational_tests_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
