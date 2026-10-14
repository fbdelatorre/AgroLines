"""Durable paths outside MSIX installation and package-private AppData."""

import ctypes
import os
import sys
import uuid
from pathlib import Path

from core.offline_policy import require_local_path


def local_app_data():
    if sys.platform != "win32":
        return Path(os.getenv("LOCALAPPDATA", str(Path.home())))
    from ctypes import wintypes

    class Guid(ctypes.Structure):
        _fields_ = [
            ("first", wintypes.DWORD),
            ("second", wintypes.WORD),
            ("third", wintypes.WORD),
            ("rest", ctypes.c_ubyte * 8),
        ]

    folder = Guid.from_buffer_copy(uuid.UUID("F1B32785-6FBA-4FCF-9D55-7B8E7F157091").bytes_le)
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    ole = ctypes.WinDLL("ole32", use_last_error=True)
    shell.SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(Guid),
        wintypes.DWORD,
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    shell.SHGetKnownFolderPath.restype = wintypes.LONG
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole.CoTaskMemFree.restype = None
    output = ctypes.c_void_p()
    # KF_FLAG_NO_PACKAGE_REDIRECTION: never resolve package-private LocalCache.
    status = shell.SHGetKnownFolderPath(
        ctypes.byref(folder), 0x00010000, None, ctypes.byref(output)
    )
    if status:
        raise OSError("Nao foi possivel obter a pasta local permanente do Windows.")
    try:
        return Path(ctypes.wstring_at(output))
    finally:
        ole.CoTaskMemFree(output)


def data_directory():
    return local_app_data() / "AgroLines"


def project_directory():
    path = data_directory() / "Projects"
    require_local_path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
