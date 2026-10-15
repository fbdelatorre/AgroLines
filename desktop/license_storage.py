"""Windows-only protected state, outside the versioned runtime directory."""

import hashlib
import json
from contextlib import contextmanager

from desktop.protected_storage import WindowsVault
from desktop.storage import data_directory


class RegistryAnchor:
    path = r"Software\AgroLines\Licensing"

    @contextmanager
    def transaction(self):
        import ctypes
        from ctypes import wintypes

        name = (
            "Global\\AgroLinesLicense-"
            + hashlib.sha256((str(data_directory()).casefold() + self.path).encode()).hexdigest()
        )
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        kernel.CreateMutexW.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.ReleaseMutex.argtypes = [wintypes.HANDLE]
        kernel.ReleaseMutex.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        handle = kernel.CreateMutexW(None, False, name)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        acquired = False
        try:
            status = kernel.WaitForSingleObject(handle, 1000)
            if status not in (0, 0x80):
                raise OSError("Outro processo está atualizando a licença. Tente novamente.")
            acquired = True
            yield
        finally:
            if acquired:
                kernel.ReleaseMutex(handle)
            kernel.CloseHandle(handle)

    def load(self):
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path) as key:
                data, kind = winreg.QueryValueEx(key, "State")
        except FileNotFoundError:
            return None
        if kind != winreg.REG_BINARY:
            raise ValueError("Registro protegido de licença inválido.")
        return json.loads(WindowsVault.crypt(data, True))

    def save(self, value):
        import winreg

        data = WindowsVault.crypt(json.dumps(value).encode(), False)
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER, self.path, access=winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, "State", 0, winreg.REG_BINARY, data)
            winreg.FlushKey(key)
        return True


def make_manager(keyring, transport):
    from desktop.license_client import LicenseManager

    return LicenseManager(
        WindowsVault(data_directory() / "license.dpapi"), RegistryAnchor(), keyring, transport
    )
