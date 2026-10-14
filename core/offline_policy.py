"""Latched Store policy. No user setting can enable remote functionality."""

import importlib.abc
import os
import socket
import sys
from pathlib import Path

_ENABLED = False
_CONTEXT = None
REMOTE_MODULES = ("desktop.main", "desktop.client", "desktop.health", "desktop.vault", "server")


def is_offline_only():
    return _ENABLED


def require_remote():
    if _ENABLED:
        raise PermissionError("Esta edição Store é exclusivamente offline.")


class RemoteImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(fullname == name or fullname.startswith(name + ".") for name in REMOTE_MODULES):
            raise ImportError("Módulo remoto indisponível na edição Store offline: " + fullname)
        return None


def denied(*args, **kwargs):
    raise PermissionError("Conexões de rede próprias são proibidas nesta edição Store.")


def require_local_path(path):
    """Reject URLs, GDAL virtual paths, UNC and Windows mapped network drives."""
    if not _ENABLED:
        return
    text = str(path)
    if "://" in text or text.startswith(("//", "\\\\", "/vsi")):
        raise ValueError("Use um arquivo em armazenamento local, não uma URL ou pasta de rede.")
    if sys.platform == "win32":
        import ctypes

        # Inspect the lexical drive before resolving/accessing a mapped network path.
        root = Path(path).absolute().anchor
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetDriveTypeW.argtypes = [ctypes.c_wchar_p]
        kernel.GetDriveTypeW.restype = ctypes.c_uint
        if kernel.GetDriveTypeW(root) in (0, 1, 4):
            raise ValueError("Unidades de rede não são aceitas nesta edição offline.")


def enforce(native=True):
    global _ENABLED, _CONTEXT
    if sys.platform == "win32" and (
        os.getenv("QTWEBENGINE_DISABLE_SANDBOX") == "1"
        or "--no-sandbox" in os.getenv("QTWEBENGINE_CHROMIUM_FLAGS", "")
    ):
        raise RuntimeError("O sandbox Chromium deve permanecer ativo no Windows.")
    if _ENABLED:
        if native:
            configure_native()
        return
    _ENABLED = True
    sys.meta_path.insert(0, RemoteImports())
    # Also covers previously imported Python clients. Native networking is separately
    # constrained in WebEngine/GDAL/PROJ and must be observed on real Windows.
    for name in ("connect", "connect_ex", "sendto", "sendmsg"):
        if hasattr(socket.socket, name):
            setattr(socket.socket, name, denied)
    for name in (
        "create_connection",
        "getaddrinfo",
        "gethostbyname",
        "gethostbyname_ex",
        "gethostbyaddr",
        "getnameinfo",
    ):
        setattr(socket, name, denied)
    for name in (
        "PROJ_LIB",
        "PROJ_DATA",
        "GDAL_DATA",
        "QT_PLUGIN_PATH",
        "QTWEBENGINEPROCESS_PATH",
        "QTWEBENGINE_RESOURCES_PATH",
        "QTWEBENGINE_LOCALES_PATH",
    ):
        os.environ.pop(name, None)
    os.environ["PROJ_NETWORK"] = "OFF"
    if sys.platform == "win32":
        import tempfile

        from desktop.storage import data_directory

        temporary = data_directory() / "Temp"
        require_local_path(temporary)
        temporary.mkdir(parents=True, exist_ok=True)
        tempfile.tempdir = str(temporary)
        os.environ["TMP"] = os.environ["TEMP"] = str(temporary)
    # Do not honor environment flags that could enable remote debugging or alter
    # Chromium operation. Never disable its sandbox or Windows protections.
    os.environ.pop("QTWEBENGINE_REMOTE_DEBUGGING", None)
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-background-networking --disable-component-update "
        "--disable-domain-reliability --disable-sync --no-pings"
    )
    if native:
        configure_native()


def configure_native():
    global _CONTEXT
    if _CONTEXT is not None:
        return
    from pyproj import network

    network.set_network_enabled(False)
    import fiona

    _CONTEXT = fiona.Env(GDAL_SKIP="WMS WCS HTTP", PROJ_NETWORK="OFF")
    _CONTEXT.__enter__()
