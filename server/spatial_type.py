"""PostGIS column with a JSON-only SQLite adapter for isolated unit tests."""

import json

from shapely import from_wkb, to_wkt
from shapely.geometry import mapping, shape
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.types import UserDefinedType


class PolygonGeometry(UserDefinedType):
    cache_ok = True

    def __init__(self, *args):
        pass

    def get_col_spec(self, **kw):
        return "geometry(MULTIPOLYGON,4326)"

    def bind_expression(self, value):
        return GeometryInput(value)

    def column_expression(self, column):
        expression = GeometryOutput(column)
        expression.type = self
        return expression

    def bind_processor(self, dialect):
        if dialect.name == "postgresql":
            return lambda value: "SRID=4326;" + to_wkt(shape(value), rounding_precision=-1)
        return lambda value: json.dumps(value)

    def result_processor(self, dialect, coltype):
        if dialect.name == "postgresql":
            return lambda value: mapping(from_wkb(bytes(value))) if value is not None else None
        return lambda value: json.loads(value) if value is not None else None


class GeometryInput(FunctionElement):
    inherit_cache = True


class GeometryOutput(FunctionElement):
    inherit_cache = True


@compiles(PolygonGeometry, "sqlite")
def sqlite_geometry(type_, compiler, **kw):
    return "TEXT"


@compiles(GeometryInput, "postgresql")
def postgres_input(element, compiler, **kw):
    return "ST_GeomFromEWKT(" + compiler.process(list(element.clauses)[0], **kw) + ")"


@compiles(GeometryOutput, "postgresql")
def postgres_output(element, compiler, **kw):
    return "ST_AsEWKB(" + compiler.process(list(element.clauses)[0], **kw) + ")"


@compiles(GeometryInput)
@compiles(GeometryOutput)
def test_geometry(element, compiler, **kw):
    return compiler.process(list(element.clauses)[0], **kw)


ischema_names["geometry"] = PolygonGeometry


class NativeGeometry(PolygonGeometry):
    def get_col_spec(self, **kw):
        return "geometry"

    def bind_processor(self, dialect):
        if dialect.name == "postgresql":
            return lambda value: (
                f"SRID={value['srid']};" + to_wkt(shape(value["geometry"]), rounding_precision=-1)
                if value is not None
                else None
            )
        return lambda value: json.dumps(value) if value is not None else None

    def result_processor(self, dialect, coltype):
        if dialect.name == "postgresql":
            from shapely import get_srid

            def read(value):
                if value is None:
                    return None
                geometry = from_wkb(bytes(value))
                return {"geometry": mapping(geometry), "srid": get_srid(geometry)}

            return read
        return lambda value: json.loads(value) if value is not None else None


class ReflectedGeometry(UserDefinedType):
    cache_ok = True

    def __init__(self, *args):
        self.arguments = args

    def get_col_spec(self, **kw):
        return "geometry" + (
            "(" + ",".join(map(str, self.arguments)) + ")" if self.arguments else ""
        )


ischema_names["geometry"] = ReflectedGeometry
