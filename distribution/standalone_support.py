"""Read-only diagnostics of bindings actually imported by the frozen executable."""

import hashlib
import json
import sys
from pathlib import Path

from core.offline_policy import is_offline_only, require_local_path


def taskbar_identity():
    """Match the stable installed shortcuts; this does not grant package identity/trust."""
    if sys.platform == "win32":
        import ctypes

        function = ctypes.WinDLL("shell32").SetCurrentProcessExplicitAppUserModelID
        function.argtypes = [ctypes.c_wchar_p]
        function.restype = ctypes.c_long
        if function("Delatorre.AgroLines.Standalone") < 0:
            raise RuntimeError("Unable to configure standalone taskbar identity")


def binding_report(output):
    require_local_path(output)
    import PySide6
    import shiboken6
    from PySide6 import QtCore, QtSvg, QtWebChannel, QtWebEngineCore, QtWidgets

    # Exercise the C++ binding as well as its Python package, without a QApplication.
    obj = QtCore.QObject()
    obj.setObjectName("synthetic-lgpl-probe")
    assert shiboken6.isValid(obj) and obj.objectName() == "synthetic-lgpl-probe"
    internal = Path(sys._MEIPASS).resolve() if getattr(sys, "frozen", False) else None
    records = []
    for module in (PySide6, shiboken6, QtCore, QtWidgets, QtSvg, QtWebChannel, QtWebEngineCore):
        path = Path(module.__file__).resolve()
        records.append(
            {
                "module": module.__name__,
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "inside_runtime": bool(internal and path.is_relative_to(internal)),
                "marker": getattr(module, "AGROLINES_LGPL_LAB_MARKER", None),
            }
        )
    report = {
        "offline_only": is_offline_only(),
        "frozen": bool(internal),
        "qt_version": QtCore.qVersion(),
        "modules": records,
        "binding_call_passed": True,
        "sac_approved": False,
        "full_native_recombination_proven": False,
    }
    Path(output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
