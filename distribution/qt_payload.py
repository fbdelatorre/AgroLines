"""Narrow Qt exclusions, applied before binary dependency expansion, never by load polling."""

import ast
import json
import re
from pathlib import Path

# These six families are not used by the Widgets/WebEngine application. Qt3D's
# quick3dcoreplugin is a different module and intentionally does not match.
FAMILIES = ("Charts", "Graphs", "DataVisualization", "Quick3D", "VirtualKeyboard", "QuickTimeline")
PYTHON_EXCLUDES = ["PySide6.Qt" + name for name in FAMILIES]


def forbidden_family(path):
    value = str(path).replace("\\", "/").casefold()
    for family in FAMILIES:
        name = family.casefold()
        if re.search(r"(?:^|[/\.])(?:pyside6\.)?qt(?:6)?" + name, value):
            return family
    if "/qml/qtquick/timeline/" in value + "/":
        return "QuickTimeline"
    if "/qml/qtquick/virtualkeyboard/" in value + "/":
        return "VirtualKeyboard"
    if value.endswith("/qtvirtualkeyboardplugin.dll"):
        return "VirtualKeyboard"
    if value.endswith("/qmldbg_quick3dprofiler.dll"):
        return "Quick3D"
    return None


def filter_collected(entries):
    """PyInstaller hook tuples are (source, destination directory)."""
    return [
        entry
        for entry in entries
        if not forbidden_family(entry[0]) and not qml_debug_tool(entry[0])
    ]


def qml_debug_tool(path):
    value = str(path).replace("\\", "/").casefold()
    return "/plugins/qmltooling/" in "/" + value or value.split("/")[-1].startswith("qmldbg_")


def external_qml(path):
    return "/pyside6/qml/" in "/" + str(path).replace("\\", "/").casefold()


def assert_widget_deployment(root):
    """A future QML UI must explicitly revisit the deployment contract."""
    for directory in (Path(root) / "desktop", Path(root) / "distribution"):
        if list(directory.rglob("*.qml")):
            raise ValueError("Application QML requires deployment review")
        for path in directory.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = (
                    [node.module]
                    if isinstance(node, ast.ImportFrom)
                    else [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else []
                )
                if isinstance(node, ast.ImportFrom) and node.module == "PySide6":
                    names += ["PySide6." + alias.name for alias in node.names]
                if any(
                    name in ("PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets")
                    for name in names
                ):
                    raise ValueError("Application QML/Quick import requires deployment review")


def omit_system_copies(analysis, retired):
    """Only exact reviewed Windows runtime copies; never discard MSVC/GIS runtimes."""
    from scripts.native_inventory import file_hash

    known = {entry["destination"].casefold(): entry for entry in retired["files"]}
    kept = []
    for destination, source, kind in analysis.binaries:
        entry = known.get(destination.replace("\\", "/").casefold())
        if entry:
            if file_hash(source) != entry["sha256"]:
                raise ValueError("Retired incidental runtime changed; review before excluding")
        else:
            kept.append((destination, source, kind))
    analysis.binaries = kept


def inspect_tree(root, python_modules=()):
    root = Path(root)
    files = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    rejected = [
        p
        for p in files + list(python_modules)
        if forbidden_family(p) or external_qml(p) or qml_debug_tool(p)
    ]
    if rejected:
        raise ValueError("Forbidden Qt family reintroduced: " + ", ".join(rejected))
    return {"forbidden_components": [], "files_scanned": len(files), "passed": True}


def record_analysis(analysis, output):
    """Keep exact build source hashes and PE imports; no private application objects."""
    import pefile

    from scripts.native_inventory import file_hash

    records = []
    for destination, source, kind in analysis.binaries:
        if (
            forbidden_family(destination)
            or external_qml(destination)
            or qml_debug_tool(destination)
        ):
            raise ValueError("Forbidden Qt binary after dependency expansion: " + destination)
        path = Path(source)
        if path.suffix.lower() not in (".dll", ".pyd", ".exe"):
            continue
        with pefile.PE(str(path), fast_load=True) as binary:
            binary.parse_data_directories(
                directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT"],
                ]
            )
            imports = sorted(
                {
                    item.dll.decode("ascii")
                    for key in ("DIRECTORY_ENTRY_IMPORT", "DIRECTORY_ENTRY_DELAY_IMPORT")
                    for item in getattr(binary, key, [])
                }
            )
        if any(forbidden_family(name) or qml_debug_tool(name) for name in imports):
            raise ValueError("Retained binary depends on excluded Qt library: " + destination)
        records.append(
            {
                "destination": destination.replace("\\", "/"),
                "source": str(path.resolve()),
                "source_sha256": file_hash(path),
                "imports": imports,
                "kind": kind,
            }
        )
    for name, _source, _kind in analysis.pure:
        if forbidden_family(name):
            raise ValueError("Forbidden Qt Python module: " + name)
    for destination, _source, _kind in analysis.datas:
        if (
            forbidden_family(destination)
            or external_qml(destination)
            or qml_debug_tool(destination)
        ):
            raise ValueError("Forbidden Qt QML/resource after collection: " + destination)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(
        json.dumps(
            {"files": records, "python_modules": [name for name, _, _ in analysis.pure]}, indent=2
        ),
        encoding="utf-8",
    )
