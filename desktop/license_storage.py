"""Windows-only protected state, outside the versioned runtime directory."""

import json

from desktop.protected_storage import WindowsVault
from desktop.storage import data_directory


class RegistryAnchor:
    path = r"Software\AgroLines\Licensing"

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
