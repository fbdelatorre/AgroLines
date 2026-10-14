"""Numeric vertex editing with lossless snapshots, independently of rendering."""

from copy import deepcopy
from math import cos, isfinite, radians, sin

from pyproj import CRS
from shapely.geometry import shape

from core.geography import apply_transform, exact_transform, inspect_polygon


class VertexEditor:
    def __init__(self, geometry, source_crs, work_crs=None):
        source = CRS.from_user_input(source_crs)
        crs = CRS.from_user_input(work_crs) if work_crs else source
        if not crs.is_projected or any(a.unit_conversion_factor != 1 for a in crs.axis_info[:2]):
            raise ValueError("Edição métrica requer SRC de trabalho projetado em metros.")
        if geometry["type"] not in ("Polygon", "MultiPolygon"):
            raise ValueError("Somente polígonos podem ser editados neste incremento.")
        self.source_crs = source.to_wkt()
        self.work_crs = crs.to_wkt()
        self.source_original = deepcopy(geometry)
        self.inverse = exact_transform(crs, source)
        if source != crs:
            from shapely.geometry import mapping

            geometry = mapping(apply_transform(shape(geometry), exact_transform(source, crs)))
        self.original = deepcopy(geometry)
        self.geometry = deepcopy(geometry)
        self.geometry["coordinates"] = self._lists(self.geometry["coordinates"])
        self.changed_vertices = set()
        self.undo_stack = []
        self.redo_stack = []

    @staticmethod
    def _lists(value):
        return (
            [VertexEditor._lists(v) for v in value] if isinstance(value, (list, tuple)) else value
        )

    def vertices(self):
        polygons = (
            [self.geometry["coordinates"]]
            if self.geometry["type"] == "Polygon"
            else self.geometry["coordinates"]
        )
        for polygon_index, polygon in enumerate(polygons):
            for ring_index, ring in enumerate(polygon):
                for vertex_index, coordinate in enumerate(ring[:-1]):
                    yield (polygon_index, ring_index, vertex_index), tuple(coordinate)

    def _ring(self, location):
        polygon, ring, _ = location
        polygons = (
            [self.geometry["coordinates"]]
            if self.geometry["type"] == "Polygon"
            else self.geometry["coordinates"]
        )
        return polygons[polygon][ring]

    def set_vertex(self, location, x, y):
        if not isfinite(x) or not isfinite(y):
            raise ValueError("Coordenadas devem ser finitas.")
        ring = self._ring(location)
        index = location[2]
        if not 0 <= index < len(ring) - 1:
            raise ValueError("Vértice inválido.")
        self.undo_stack.append((deepcopy(self.geometry), self.changed_vertices.copy()))
        self.redo_stack.clear()
        self.changed_vertices.add(tuple(location))
        ring[index][0:2] = [float(x), float(y)]
        if index == 0:
            ring[-1] = list(ring[0])

    def move_vertex(self, location, distance_m, azimuth_degrees):
        if not isfinite(distance_m) or not isfinite(azimuth_degrees):
            raise ValueError("Distância e azimute devem ser finitos.")
        coordinate = self._ring(location)[location[2]]
        angle = radians(azimuth_degrees)
        self.set_vertex(
            location,
            coordinate[0] + distance_m * sin(angle),
            coordinate[1] + distance_m * cos(angle),
        )

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append((deepcopy(self.geometry), self.changed_vertices.copy()))
            self.geometry, self.changed_vertices = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append((deepcopy(self.geometry), self.changed_vertices.copy()))
            self.geometry, self.changed_vertices = self.redo_stack.pop()

    def comparison(self):
        # Grid displacement, not ground/absolute GNSS positioning accuracy.
        return shape(self.geometry).hausdorff_distance(shape(self.original))

    def validate(self):
        return inspect_polygon(self.source_geometry(), self.source_crs, work_crs=self.work_crs)

    def source_geometry(self):
        result = deepcopy(self.source_original)
        result["coordinates"] = self._lists(result["coordinates"])
        polygons = [result["coordinates"]] if result["type"] == "Polygon" else result["coordinates"]
        for location in self.changed_vertices:
            p, r, index = location
            working = self._ring(location)[index]
            x, y = self.inverse.transform(working[0], working[1], errcheck=True)
            polygons[p][r][index][0:2] = [x, y]
            if index == 0:
                polygons[p][r][-1] = list(polygons[p][r][0])
        return result
