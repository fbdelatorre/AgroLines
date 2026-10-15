"""Synthetic geometry only; no AgroLines imports. SPDX-License-Identifier: 0BSD."""

import ctypes
import json
import os
import sys
from pathlib import Path


def main():
    if sys.platform != "win32":
        raise RuntimeError("Windows-only laboratory")
    path = Path(sys.argv[1]).resolve(strict=True)
    # Only this child process; never an installed package, PATH or security policy.
    with os.add_dll_directory(str(path.parent)):
        lib = ctypes.CDLL(str(path), winmode=0x1100)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
    buf = ctypes.create_unicode_buffer(32768)
    if not kernel.GetModuleFileNameW(lib._handle, buf, len(buf)):
        raise ctypes.WinError(ctypes.get_last_error())
    loaded_path = buf.value
    lib.GEOSversion.restype = ctypes.c_char_p
    lib.GEOS_init_r.restype = ctypes.c_void_p
    lib.GEOSGeomFromWKT_r.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.GEOSGeomFromWKT_r.restype = ctypes.c_void_p
    lib.GEOSArea_r.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
    lib.GEOSArea_r.restype = ctypes.c_int
    lib.GEOSGeom_destroy_r.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.GEOS_finish_r.argtypes = [ctypes.c_void_p]
    ctx = lib.GEOS_init_r()
    if not ctx:
        raise RuntimeError("GEOS_init_r failed")
    areas = []
    try:
        for length in (0.001, 1, 10, 100):
            wkt = f"POLYGON ((0 0,{length} 0,{length} {length},0 {length},0 0))"
            geom = lib.GEOSGeomFromWKT_r(ctx, wkt.encode())
            if not geom:
                raise RuntimeError("Invalid synthetic polygon")
            area = ctypes.c_double()
            try:
                if lib.GEOSArea_r(ctx, geom, ctypes.byref(area)) != 1:
                    raise RuntimeError("GEOSArea_r failed")
                if abs(area.value - length * length) > 1e-12:
                    raise RuntimeError("Unexpected synthetic area")
                areas.append(area.value)
            finally:
                lib.GEOSGeom_destroy_r(ctx, geom)
    finally:
        lib.GEOS_finish_r(ctx)
    # Enumerate our own modules, including the C++ dependency, without injection.
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    handles = (ctypes.c_void_p * 2048)()
    needed = ctypes.c_ulong()
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    process = kernel.GetCurrentProcess()
    psapi.EnumProcessModulesEx.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_ulong,
    ]
    if not psapi.EnumProcessModulesEx(
        process, handles, ctypes.sizeof(handles), ctypes.byref(needed), 3
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    if needed.value > ctypes.sizeof(handles):
        raise RuntimeError("Module buffer insufficient")
    modules = []
    for handle in handles[: needed.value // ctypes.sizeof(ctypes.c_void_p)]:
        if (
            kernel.GetModuleFileNameW(handle, buf, len(buf))
            and "geos" in Path(buf.value).name.lower()
        ):
            modules.append(buf.value)
    print(
        json.dumps(
            {
                "version": lib.GEOSversion().decode(),
                "areas": areas,
                "loaded_path": loaded_path,
                "geos_modules": modules,
                "frozen": bool(getattr(sys, "frozen", False)),
            }
        )
    )


if __name__ == "__main__":
    main()
