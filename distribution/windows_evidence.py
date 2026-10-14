"""Read-only Windows evidence from system tools; no PowerShell or policy changes."""

import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

CHANNEL = "Microsoft-Windows-CodeIntegrity/Operational"
POLICY_ID = "0283ac0f-fff1-49ae-ada1-8a933130cad6"


def system_tool(name, args):
    import ctypes

    buffer = ctypes.create_unicode_buffer(32768)
    if not ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer)):
        raise OSError("System directory unavailable")
    result = subprocess.run(
        [str(Path(buffer.value) / name), *args],
        capture_output=True,
        timeout=20,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.returncode:
        raise OSError("Windows evidence command failed")
    if len(result.stdout) > 8 * 1024 * 1024:
        raise ValueError("Evidence too large")
    # Windows tools may use UTF-16 output; never print stderr or the environment.
    return result.stdout.decode("utf-16" if result.stdout.startswith(b"\xff\xfe") else "utf-8-sig")


def classify_events(xml, native_names):
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        root = ET.fromstring("<Events>" + xml + "</Events>")
    events = [root] if root.tag.split("}")[-1] == "Event" else list(root)
    result = []
    names = [n.casefold() for n in native_names]
    for event in events:
        values = "\n".join(event.itertext()).casefold()
        result.append(
            {
                "associated_with_payload": any(n in values for n in names),
                "xml": ET.tostring(event, encoding="unicode"),
            }
        )
    return result


def collect(started, native_names):
    data = {
        "observed_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "sac_active_confirmed": False,
        "code_integrity_readable": False,
        "events": [],
        "errors": [],
    }
    if sys.platform != "win32":
        data["errors"].append("Windows 11 evidence unavailable on this platform")
        return data
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\CI\Policy"
        ) as key:
            state = winreg.QueryValueEx(key, "VerifiedAndReputablePolicyState")[0]
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\ProductOptions"
        ) as key:
            client = winreg.QueryValueEx(key, "ProductType")[0] == "WinNT"
        policies = json.loads(system_tool("CiTool.exe", ["-lp", "-json"]))["Policies"]
        enforced = any(
            p.get("PolicyID", "").strip("{}").casefold() == POLICY_ID
            and p.get("IsEnforced") is True
            for p in policies
        )
        data["registry_state"] = state
        data["policies"] = policies
        data["sac_active_confirmed"] = (
            client and sys.getwindowsversion().build >= 22000 and state == 1 and enforced
        )
    except Exception:
        data["errors"].append("SAC state could not be confirmed; no elevation attempted")
    try:
        config = ET.fromstring(system_tool("wevtutil.exe", ["gl", CHANNEL, "/f:xml"]))
        if config.attrib.get("enabled", "").casefold() != "true":
            raise ValueError("Log not confirmed enabled")
        stamp = started.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        query = f"*[System[(EventID=3077 or EventID=3033) and TimeCreated[@SystemTime>='{stamp}']]]"
        output = system_tool(
            "wevtutil.exe", ["qe", CHANNEL, f"/q:{query}", "/f:xml", "/rd:true", "/c:1000"]
        )
        data["events"] = classify_events(output, native_names) if output.strip() else []
        # Saturated query cannot establish completeness.
        data["code_integrity_readable"] = len(data["events"]) < 1000
    except Exception:
        data["errors"].append("Code Integrity evidence unavailable or incomplete")
    return data
