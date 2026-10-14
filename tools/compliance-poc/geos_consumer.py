"""Synthetic LGPL experiment only; no AgroLines imports or project data. SPDX: 0BSD."""

import ctypes
import json
import sys

lib = ctypes.CDLL(sys.argv[1])
lib.GEOSversion.restype = ctypes.c_char_p
lib.GEOS_init_r.restype = ctypes.c_void_p
lib.GEOSGeomFromWKT_r.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.GEOSGeomFromWKT_r.restype = ctypes.c_void_p
lib.GEOSArea_r.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
lib.GEOSArea_r.restype = ctypes.c_int
lib.GEOSGeom_destroy_r.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
lib.GEOS_finish_r.argtypes = [ctypes.c_void_p]
context = lib.GEOS_init_r()
geometry = lib.GEOSGeomFromWKT_r(context, b"POLYGON ((0 0,10 0,10 10,0 10,0 0))")
area = ctypes.c_double()
assert lib.GEOSArea_r(context, geometry, ctypes.byref(area)) == 1
assert area.value == 100.0
print(json.dumps({"version": lib.GEOSversion().decode(), "area": area.value}))
lib.GEOSGeom_destroy_r(context, geometry)
lib.GEOS_finish_r(context)
