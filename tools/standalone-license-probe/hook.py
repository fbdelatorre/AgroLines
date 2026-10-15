"""Read built resources and query a fresh in-memory vendor SQLite. SPDX-License-Identifier: 0BSD."""


def _agrolines_license_configuration():
    import ctypes as c
    import hashlib
    import json
    import os
    from pathlib import Path

    output = os.environ.get("AGROLINES_LICENSE_PROBE")
    if not output:
        return
    root = Path(output)
    result = {"errors": [], "qrc_notices": [], "spatialite": {}, "legal_approved": False}
    try:
        from PySide6.QtCore import QDirIterator, QFile, QIODevice

        iterator = QDirIterator(":/", QDirIterator.Subdirectories)
        count = 0
        while iterator.hasNext():
            path = iterator.next()
            count += 1
            if count > 100000:
                raise RuntimeError("Resource enumeration bound exceeded")
            if not any(word in path.lower() for word in ("credit", "license", "licence")):
                continue
            file = QFile(path)
            if not file.open(QIODevice.ReadOnly) or file.size() > 32 * 1024 * 1024:
                continue
            raw = bytes(file.readAll())
            file.close()
            digest = hashlib.sha256(raw).hexdigest()
            if raw and (b"license" in raw.lower() or b"copyright" in raw.lower()):
                (root / ("qrc-" + digest + ".txt")).write_bytes(raw)
                result["qrc_notices"].append(
                    {"resource": path, "bytes": len(raw), "sha256": digest}
                )
        result["qrc_resources_scanned"] = count
        kernel = c.WinDLL("kernel32", use_last_error=True)
        kernel.GetModuleHandleW.argtypes = [c.c_wchar_p]
        kernel.GetModuleHandleW.restype = c.c_void_p
        kernel.GetProcAddress.argtypes = [c.c_void_p, c.c_char_p]
        kernel.GetProcAddress.restype = c.c_void_p
        kernel.GetModuleFileNameW.argtypes = [c.c_void_p, c.c_wchar_p, c.c_uint]
        names = {
            "spatialite": "spatialite-e03c16976c81110a807ddde663a483fb.dll",
            "sqlite": "sqlite3-0cb9f6e67fd2491114f55ace5268f7aa.dll",
        }
        handles = {key: kernel.GetModuleHandleW(value) for key, value in names.items()}
        if not all(handles.values()):
            raise RuntimeError(
                "Expected Fiona vendor modules were not loaded; no fallback DLL load"
            )
        for key, handle in handles.items():
            path = c.create_unicode_buffer(32768)
            if not kernel.GetModuleFileNameW(handle, path, len(path)):
                raise RuntimeError("Cannot observe vendor path")
            result[key + "_module"] = {
                "path": path.value,
                "sha256": hashlib.sha256(Path(path.value).read_bytes()).hexdigest(),
            }

        def function(group, name, restype, *arguments):
            address = kernel.GetProcAddress(handles[group], name.encode("ascii"))
            if not address:
                raise RuntimeError("Missing actual vendor export " + name)
            return c.CFUNCTYPE(restype, *arguments)(address)

        version = function("spatialite", "spatialite_version", c.c_char_p)().decode()
        result["spatialite"]["version"] = version
        db = c.c_void_p()
        if function("sqlite", "sqlite3_open", c.c_int, c.c_char_p, c.POINTER(c.c_void_p))(
            b":memory:", c.byref(db)
        ):
            raise RuntimeError("Synthetic memory database could not open")
        cache = function("spatialite", "spatialite_alloc_connection", c.c_void_p)()
        if not cache:
            raise RuntimeError("SpatiaLite cache allocation failed")
        callback_type = c.CFUNCTYPE(
            c.c_int, c.c_void_p, c.c_int, c.POINTER(c.c_char_p), c.POINTER(c.c_char_p)
        )
        try:
            function("spatialite", "spatialite_init_ex", None, c.c_void_p, c.c_void_p, c.c_int)(
                db, cache, 0
            )
            execute = function(
                "sqlite",
                "sqlite3_exec",
                c.c_int,
                c.c_void_p,
                c.c_char_p,
                callback_type,
                c.c_void_p,
                c.POINTER(c.c_char_p),
            )
            for query in ("HasGeos()", "HasProj()", "HasRtTopo()", "HasGCP()"):
                values = []

                @callback_type
                def receive(unused, columns, data, names, values=values):
                    values.extend(data[i].decode() if data[i] else None for i in range(columns))
                    return 0

                message = c.c_char_p()
                code = execute(db, ("SELECT " + query).encode(), receive, None, c.byref(message))
                result["spatialite"][query] = {
                    "sqlite_status": code,
                    "values": values,
                    "error": message.value.decode() if message.value else None,
                }
                if message.value:
                    function("sqlite", "sqlite3_free", None, c.c_void_p)(
                        c.cast(message, c.c_void_p)
                    )
        finally:
            function("sqlite", "sqlite3_close", c.c_int, c.c_void_p)(db)
            function("spatialite", "spatialite_cleanup_ex", None, c.c_void_p)(cache)
    except Exception as error:
        result["errors"].append(type(error).__name__ + ": " + str(error))
    (root / "configuration.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


__import__("atexit").register(_agrolines_license_configuration)
