"""Per-user DPAPI storage on Windows; never fall back to plaintext."""

import ctypes
import json
import os
import sys
from pathlib import Path


class WindowsVault:
    def __init__(self, path=None):
        self.path = Path(
            path or Path(os.getenv("LOCALAPPDATA", Path.home())) / "AgroLines" / "session.dpapi"
        )
        self.available = sys.platform == "win32"

    @staticmethod
    def crypt(data: bytes, decrypt: bool) -> bytes:
        from ctypes import wintypes

        class Blob(ctypes.Structure):
            _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

        crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        function = crypt32.CryptUnprotectData if decrypt else crypt32.CryptProtectData
        function.argtypes = [
            ctypes.POINTER(Blob),
            ctypes.c_void_p,
            ctypes.POINTER(Blob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(Blob),
        ]
        function.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
        source, output = Blob(len(data), buffer), Blob()
        # No machine-wide flag: only this Windows user's profile can decrypt.
        if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(output)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return ctypes.string_at(output.data, output.size)
        finally:
            kernel32.LocalFree(output.data)

    def load(self):
        if not self.available or not self.path.exists():
            return None
        try:
            result = json.loads(self.crypt(self.path.read_bytes(), True))
            return result if isinstance(result, dict) else None
        except (OSError, ValueError):
            return None

    def save(self, data):
        if not self.available:
            return False
        blob = self.crypt(json.dumps(data).encode(), False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_bytes(blob)
        temporary.replace(self.path)
        return True

    def clear(self):
        self.path.unlink(missing_ok=True)
