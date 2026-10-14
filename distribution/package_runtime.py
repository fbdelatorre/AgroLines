"""Read-only Windows package/process evidence; no registry or policy modifications."""

import ctypes
import json
import sys
import xml.etree.ElementTree as ET
from ctypes import wintypes
from pathlib import Path


def expected_identity():
    return json.loads((Path(__file__).parent / "windows/msix/identity.json").read_text())


def package_evidence():
    result = {"packaged": False, "official_identity_matches": False, "errors": []}
    if sys.platform != "win32":
        return result
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    for field, symbol in (
        ("full_name", "GetCurrentPackageFullName"),
        ("family_name", "GetCurrentPackageFamilyName"),
        ("install_path", "GetCurrentPackagePath"),
    ):
        function = getattr(kernel, symbol)
        function.argtypes = [ctypes.POINTER(wintypes.UINT), wintypes.LPWSTR]
        function.restype = wintypes.LONG
        length = wintypes.UINT(0)
        status = function(ctypes.byref(length), None)
        if status == 15700:  # APPMODEL_ERROR_NO_PACKAGE: unpackaged probe, not acceptance.
            return result
        if status != 122:
            result["errors"].append(f"{symbol}: {status}")
            return result
        buffer = ctypes.create_unicode_buffer(length.value)
        status = function(ctypes.byref(length), buffer)
        if status:
            result["errors"].append(f"{symbol}: {status}")
            return result
        result[field] = buffer.value
    result["packaged"] = True
    try:
        root = ET.parse(Path(result["install_path"]) / "AppxManifest.xml").getroot()
        ns = {"f": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
        declared = root.find("f:Identity", ns)
        expected = expected_identity()
        result["official_identity_matches"] = (
            result["family_name"] == expected["package_family_name"]
            and declared.attrib["Name"] == expected["name"]
            and declared.attrib["Publisher"] == expected["publisher"]
            and declared.attrib["ProcessorArchitecture"] == "x64"
            and root.find("f:Properties/f:PublisherDisplayName", ns).text
            == expected["publisher_display_name"]
        )
    except (OSError, ET.ParseError, AttributeError, KeyError) as exc:
        result["errors"].append(type(exc).__name__)
    return result


def qt_helper_evidence(install_path=None):
    if sys.platform != "win32":
        return []
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)

    class Entry(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("usage", wintypes.DWORD),
            ("pid", wintypes.DWORD),
            ("heap", ctypes.c_size_t),
            ("module", wintypes.DWORD),
            ("threads", wintypes.DWORD),
            ("parent", wintypes.DWORD),
            ("priority", wintypes.LONG),
            ("flags", wintypes.DWORD),
            ("name", wintypes.WCHAR * 260),
        ]

    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.GetCurrentProcessId.restype = wintypes.DWORD
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.GetPackageFamilyName.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.UINT),
        wintypes.LPWSTR,
    ]
    kernel.GetPackageFamilyName.restype = wintypes.LONG
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        return [{"error": "process_snapshot_unavailable", "inside_package": False}]
    entries = []
    try:
        entry = Entry()
        entry.size = ctypes.sizeof(entry)
        for symbol in ("Process32FirstW", "Process32NextW"):
            function = getattr(kernel, symbol)
            function.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
            function.restype = wintypes.BOOL
        success = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while success:
            entries.append((entry.pid, entry.parent, entry.name))
            success = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    descendants = {kernel.GetCurrentProcessId()}
    while True:
        extended = descendants | {pid for pid, parent, _ in entries if parent in descendants}
        if extended == descendants:
            break
        descendants = extended
    helpers = []
    for pid, _, name in entries:
        if pid not in descendants or name.casefold() != "qtwebengineprocess.exe":
            continue
        item = {"pid": pid, "name": name, "inside_package": False}
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            item["error"] = "process_query_unavailable"
        else:
            try:
                size = wintypes.DWORD(32768)
                path = ctypes.create_unicode_buffer(size.value)
                if kernel.QueryFullProcessImageNameW(handle, 0, path, ctypes.byref(size)):
                    item["path"] = path.value
                    item["inside_package"] = bool(
                        install_path
                        and Path(path.value).resolve().is_relative_to(Path(install_path).resolve())
                    )
                length = wintypes.UINT(0)
                if kernel.GetPackageFamilyName(handle, ctypes.byref(length), None) == 122:
                    family = ctypes.create_unicode_buffer(length.value)
                    if kernel.GetPackageFamilyName(handle, ctypes.byref(length), family) == 0:
                        item["family_name"] = family.value
            finally:
                kernel.CloseHandle(handle)
        helpers.append(item)
    return helpers
