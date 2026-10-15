"""Native replacement in the unchanged PR18 AgroLines EXE. SPDX-License-Identifier: 0BSD."""

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location(
    "synthetic_lab", REPO / "tools/windows-lgpl-lab/run.py"
)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
MARKER = lab.MARKER


def checked(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def imported_symbols(root, destination):
    import pefile

    required = set()
    for path in root.rglob("*"):
        if path.suffix.casefold() not in (".exe", ".dll", ".pyd"):
            continue
        with pefile.PE(str(path), fast_load=True) as pe:
            pe.parse_data_directories(directories=[1, 13])
            for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []) + getattr(
                pe, "DIRECTORY_ENTRY_DELAY_IMPORT", []
            ):
                if entry.dll.decode().casefold() == destination.name.casefold():
                    required.update(i.name for i in entry.imports if i.name)
    return required


def assert_exports(root, destination, replacement):
    import pefile

    # Qt Core has more than pefile's default 8192 export symbols.
    with pefile.PE(str(replacement), fast_load=True, max_symbol_exports=65536) as pe:
        pe.parse_data_directories(directories=[0])
        exports = {s.name for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
        if len(exports) != pe.DIRECTORY_ENTRY_EXPORT.struct.NumberOfNames:
            raise ValueError("Incomplete export-table observation; do not infer an ABI mismatch")
    missing = sorted(s.decode() for s in imported_symbols(root, destination) - exports)
    if missing:
        raise ValueError(
            "Missing imported ABI symbols in " + destination.name + ": " + str(missing)
        )


def validate_reports(directory, phase, component, replacements):
    snapshots = [json.loads(p.read_text(encoding="utf-8")) for p in directory.glob("loaded-*.json")]
    if len(snapshots) != 3:
        raise ValueError("Expected native self-observation from all three full-app processes")
    modified = phase == "modified"
    qt = component.startswith("qt")
    for snapshot in snapshots:
        if snapshot["errors"] or not snapshot["frozen"]:
            raise ValueError("Incomplete native self-observation: " + str(snapshot))
        if qt and ((MARKER in snapshot["qt_version"]) != modified):
            raise ValueError("Modified Qt version not observed by the real application")
        for destination, source in replacements.items():
            found = [
                m for m in snapshot["modules"] if Path(m["path"]).resolve() == destination.resolve()
            ]
            if len(found) != 1 or found[0]["sha256"] != lab.sha(source):
                raise ValueError(
                    "Replacement not loaded by the full application: " + str(destination)
                )
            if not qt and destination.name.casefold().startswith("geos_c"):
                if (MARKER in found[0]["version"]) != modified:
                    raise ValueError("Modified GEOSversion not observed on actual loaded handle")
    smoke = json.loads(
        (directory / "smoke-startup-and-gis-probe.json").read_text(encoding="utf-8-sig")
    )
    offline = json.loads(
        (directory / "offline-import-edit-backup-probe.json").read_text(encoding="utf-8-sig")
    )
    if (
        not smoke["checks_passed"]
        or not offline["passed"]
        or not offline["webengine_ready"]
        or len(smoke["precision"]["checks"]) != 22
    ):
        raise ValueError("Full application regression")
    return {
        "snapshots": snapshots,
        "computational_precision": "22/22",
        "formats": offline["local_formats"],
        "offline_passed": True,
        "webengine_ready": True,
        "own_executable_unchanged": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--component", choices=["qtbase-6.12.0", "geos-3.11.3", "geos-3.14.1"], required=True
    )
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != "win32" or not shutil.which("cl"):
        raise SystemExit("Authorized Windows/MSVC builder required")
    checked(
        ["pwsh", "-File", REPO / "distribution/windows/standalone/Assert-Laboratory.ps1"], cwd=REPO
    )
    from distribution.payload import manifest, verify

    payload, work = args.payload.resolve(), args.work.resolve()
    baseline = json.loads((payload / "payload-manifest.json").read_text())
    if (
        not verify(payload, baseline)
        or lab.sha(payload / "payload-manifest.json")
        != "cd462d33214018a28d364b2cea65a9e172a140a13fd50a2cdf162a43b95f32e0"
    ):
        raise ValueError("Not the immutable, verified PR18 baseline")
    if work.exists() or work.is_relative_to(payload):
        raise ValueError("Fresh independent laboratory required")
    work.mkdir(parents=True)
    evidence = work / "evidence"
    evidence.mkdir()
    report = {
        "component": args.component,
        "source_consumer_commit": "710a9664fe7112570775224909d174a7738f24a5",
        "own_exe_sha256": lab.sha(payload / "AgroLines.exe"),
        "phases": {},
        "production_payload_modified": False,
        "legal_approved": False,
        "sac_approved": False,
    }
    try:
        record = next(
            r
            for r in json.loads((REPO / "docs/compliance/sources-index.json").read_text())[
                "sources"
            ]
            if r["component"] == args.component
        )
        tree, build = work / "source", work / "build"
        checked(["git", "init", tree])
        checked(["git", "-C", tree, "config", "core.autocrlf", "false"])
        checked(["git", "-C", tree, "fetch", "--depth=1", record["repository"], record["commit"]])
        checked(["git", "-C", tree, "checkout", "--detach", "FETCH_HEAD"])
        archive = work / "upstream.tar"
        checked(
            [
                "git",
                "-C",
                tree,
                "-c",
                "tar.umask=0002",
                "archive",
                "--format=tar",
                "--prefix=" + args.component + "/",
                "-o",
                archive,
                "HEAD",
            ]
        )
        if lab.sha(archive) != record["sha256"]:
            raise ValueError("Pinned upstream archive mismatch")
        report["source"] = record
        qt = args.component.startswith("qt")
        if qt:
            targets = {"_internal/PySide6/Qt6Core.dll": "Qt6Core.dll"}
        else:
            folder = "fiona.libs" if args.component.endswith("3.11.3") else "Shapely.libs"
            targets = {
                p.relative_to(payload).as_posix(): p.name
                for p in (payload / "_internal" / folder).glob("geos*.dll")
            }
            if len(targets) != 2:
                raise ValueError("Expected independent C and C++ GEOS DLL pair")
            cmake = tree / "CMakeLists.txt"
            cmake.write_text(
                cmake.read_text()
                + "\n"
                + "\n".join(
                    "set_target_properties("
                    + ("geos_c" if name.startswith("geos_c-") else "geos")
                    + f' PROPERTIES OUTPUT_NAME "{Path(name).stem}")'
                    for name in targets.values()
                )
                + "\n"
            )
        configure = [
            "cmake",
            "-S",
            tree,
            "-B",
            build,
            "-G",
            "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_SHARED_LIBS=ON",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
        ]
        configure += (
            ["-DQT_BUILD_TESTS=OFF", "-DQT_BUILD_EXAMPLES=OFF"]
            + [
                "-DFEATURE_" + f + "=OFF"
                for f in (
                    "gui",
                    "widgets",
                    "network",
                    "sql",
                    "dbus",
                    "opengl",
                    "printsupport",
                    "concurrent",
                    "xml",
                    "testlib",
                    "icu",
                    "glib",
                    "windeployqt",
                )
            ]
            if qt
            else ["-DBUILD_TESTING=OFF", "-DBUILD_BENCHMARKS=OFF"]
        )
        checked(configure)
        report["configure"] = [str(x) for x in configure]
        for phase in ("upstream-original", "modified"):
            if phase == "modified":
                lab.apply_marker(tree, args.component)
            checked(["cmake", "--build", build, "--target", "Core" if qt else "geos_c", "-j", "4"])
            variant = work / phase
            shutil.copytree(payload, variant)
            hook = variant / "_internal/PySide6/__init__.py"
            with hook.open("a", encoding="utf-8") as stream:
                stream.write("\n" + (Path(__file__).parent / "loaded_probe.py").read_text())
            replacements = {}
            for relative, name in targets.items():
                matches = list(build.rglob(name))
                if len(matches) != 1:
                    raise ValueError("Ambiguous compiled library: " + name)
                source, destination = matches[0], variant / relative
                lab.x64(source)
                shutil.copy2(source, destination)
                replacements[destination] = source
            # Check the coherent replacement pair, not an old C API/new C++ mixture.
            for destination, source in replacements.items():
                assert_exports(variant, destination, source)
            # Reject changes to any other native, application, map or project file.
            actual = {r["path"]: r["sha256"] for r in manifest(variant)["files"]}
            original = {r["path"]: r["sha256"] for r in baseline["files"]}
            changed = {
                p for p in original.keys() | actual.keys() if original.get(p) != actual.get(p)
            }
            if changed != set(targets) | {"_internal/PySide6/__init__.py"}:
                raise ValueError("Unexpected laboratory payload changes: " + str(changed))
            directory = evidence / phase
            directory.mkdir()
            environment = os.environ.copy()
            environment["AGROLINES_NATIVE_LAB_REPORT"] = str(directory / "loaded")
            checked(
                [
                    "pwsh",
                    "-File",
                    REPO / "scripts/Observe-NativeModules.ps1",
                    "-Executable",
                    variant / "AgroLines.exe",
                    "-OutputDirectory",
                    directory,
                ],
                env=environment,
                cwd=REPO,
            )
            if lab.sha(variant / "AgroLines.exe") != report["own_exe_sha256"]:
                raise ValueError("Own executable modified")
            report["phases"][phase] = validate_reports(
                directory, phase, args.component, replacements
            )
        if not verify(payload, baseline):
            raise ValueError("Original PR18 payload changed")
        report["full_app_native_replacement_demonstrated"] = True
    except Exception as error:
        report["full_app_native_replacement_demonstrated"] = False
        report["error"] = type(error).__name__ + ": " + str(error)
        raise
    finally:
        if (work / "source/.git").exists():
            patch = subprocess.check_output(["git", "-C", work / "source", "diff"])
            (evidence / "laboratory.patch").write_bytes(patch)
        if (work / "build/CMakeCache.txt").exists():
            shutil.copy2(work / "build/CMakeCache.txt", evidence)
        (evidence / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("AGROLINES_NATIVE_REPLACEMENT=" + json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
