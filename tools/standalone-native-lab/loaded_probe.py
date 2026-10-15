"""Appended ONLY to the LGPL Python package in lab copies. SPDX-License-Identifier: 0BSD."""


def _agrolines_capture_loaded_native():
    import ctypes
    import hashlib
    import json
    import os
    from pathlib import Path

    output = os.environ.get("AGROLINES_NATIVE_LAB_REPORT")
    if not output:
        return
    result = {"errors": [], "modules": [], "sac_approved": False}
    try:
        import sys

        from PySide6.QtCore import qVersion

        result["qt_version"] = qVersion()
        result["frozen"] = bool(getattr(sys, "frozen", False))
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
        kernel.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        kernel.GetProcAddress.restype = ctypes.c_void_p
        psapi.EnumProcessModulesEx.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.c_ulong,
        ]
        handles = (ctypes.c_void_p * 4096)()
        needed = ctypes.c_ulong()
        if not psapi.EnumProcessModulesEx(
            kernel.GetCurrentProcess(), handles, ctypes.sizeof(handles), ctypes.byref(needed), 3
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        if needed.value > ctypes.sizeof(handles):
            raise RuntimeError("Module buffer insufficient")
        for handle in handles[: needed.value // ctypes.sizeof(ctypes.c_void_p)]:
            name = ctypes.create_unicode_buffer(32768)
            if not kernel.GetModuleFileNameW(handle, name, len(name)):
                raise ctypes.WinError(ctypes.get_last_error())
            path = Path(name.value).resolve()
            if path.name.casefold() != "qt6core.dll" and "geos" not in path.name.casefold():
                continue
            record = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            if path.name.casefold().startswith("geos_c"):
                # Wrap the ALREADY LOADED handle: never LoadLibrary a second test DLL.
                address = kernel.GetProcAddress(handle, b"GEOSversion")
                if not address:
                    raise RuntimeError("GEOSversion export missing on loaded C API handle")
                record["version"] = ctypes.CFUNCTYPE(ctypes.c_char_p)(address)().decode("ascii")
            result["modules"].append(record)
    except Exception as error:
        result["errors"].append(type(error).__name__ + ": " + str(error))
    Path(output + "-" + str(os.getpid()) + ".json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )


__import__("atexit").register(_agrolines_capture_loaded_native)
