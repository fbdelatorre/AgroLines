"""Windows-only synthetic shared-library experiments. SPDX-License-Identifier: 0BSD."""

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MARKER = "-agrolines-synthetic"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def x64(path):
    with Path(path).open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise ValueError("Not PE")
        stream.seek(60)
        offset = struct.unpack("<I", stream.read(4))[0]
        stream.seek(offset)
        if stream.read(6) != b"PE\0\0\x64\x86":
            raise ValueError("Not x64 PE")


def command(args, cwd=None):
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def apply_marker(tree, component):
    if component == "qtbase-6.12.0":
        path = tree / "src/corelib/global/qlibraryinfo.cpp"
        old = "return QT_VERSION_STR;"
        new = 'return QT_VERSION_STR "-agrolines-synthetic";'
    else:
        path = tree / "capi/geos_ts_c.cpp"
        old = '"%s", GEOS_CAPI_VERSION'
        new = '"%s-agrolines-synthetic", GEOS_CAPI_VERSION'
    source = path.read_text()
    if source.count(old) != 1:
        raise ValueError("Unexpected source; marker patch refused")
    path.write_text(source.replace(old, new))
    return path.relative_to(tree).as_posix()


def validate(result, phase, libdir):
    if (MARKER in result["version"]) != (phase == "modified"):
        raise ValueError("Unexpected original/modified version")
    loaded = Path(result["loaded_path"]).resolve(strict=True)
    if not loaded.is_relative_to(libdir.resolve()):
        raise ValueError("Loaded library outside selected laboratory directory")
    x64(loaded)
    result["loaded_sha256"] = sha(loaded)
    for path in result.get("geos_modules", []):
        path = Path(path).resolve(strict=True)
        if not path.is_relative_to(libdir.resolve()):
            raise ValueError("Unexpected GEOS dependency outside lab")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--component", choices=["qtbase-6.12.0", "geos-3.11.3", "geos-3.14.1"], required=True
    )
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != "win32" or not shutil.which("cl"):
        raise SystemExit("Requires Windows x64 MSVC developer environment; no security workaround")
    work = args.work.resolve()
    if work.exists():
        raise SystemExit("Choose a fresh lab directory")
    work.mkdir(parents=True)
    index = json.loads((REPO / "docs/compliance/sources-index.json").read_text())["sources"]
    record = next(r for r in index if r["component"] == args.component)
    tree, build = work / "source", work / "build"
    command(
        ["git", "-c", "core.autocrlf=false", "clone", "--no-checkout", record["repository"], tree]
    )
    command(
        ["git", "-c", "core.autocrlf=false", "checkout", "--detach", record["commit"]], cwd=tree
    )
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tree, text=True).strip()
    if head != record["commit"]:
        raise ValueError("Source commit mismatch")
    archive = work / "source.tar"
    command(
        [
            "git",
            "-c",
            "core.autocrlf=false",
            "-c",
            "tar.umask=0002",
            "archive",
            "--format=tar",
            "--prefix=" + args.component + "/",
            "-o",
            archive,
            "HEAD",
        ],
        cwd=tree,
    )
    if sha(archive) != record["sha256"]:
        raise ValueError("Committed source archive mismatch: " + sha(archive))
    qt = args.component.startswith("qt")
    config = [
        "cmake",
        "-S",
        tree,
        "-B",
        build,
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBUILD_SHARED_LIBS=ON",
    ]
    if qt:
        config += ["-DQT_BUILD_TESTS=OFF", "-DQT_BUILD_EXAMPLES=OFF"]
        config += [
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
    else:
        config += [
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
            "-DBUILD_TESTING=OFF",
            "-DBUILD_BENCHMARKS=OFF",
        ]
    command(config)
    command(["cmake", "--build", build, "--target", "Core" if qt else "geos_c", "-j", "2"])
    evidence = work / "evidence"
    evidence.mkdir()
    exe = work / "consumer.exe"
    if qt:
        command(
            [
                "cl",
                "/nologo",
                "/std:c++17",
                "/Zc:__cplusplus",
                "/EHsc",
                "/MD",
                "/I" + str(build / "include"),
                "/I" + str(build / "include/QtCore"),
                "/I" + str(build / "src/corelib"),
                HERE / "qt_consumer.cpp",
                build / "lib/Qt6Core.lib",
                "/Fe:" + str(exe),
            ],
            cwd=work,
        )
    else:
        command(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                "--onedir",
                "--name",
                "SyntheticGeos",
                "--distpath",
                work / "frozen",
                "--workpath",
                work / "freezer-work",
                "--specpath",
                work,
                HERE / "geos_consumer.py",
            ],
            cwd=work,
        )
        exe = work / "frozen/SyntheticGeos/SyntheticGeos.exe"
    results = {}
    for phase in ("original", "modified"):
        if phase == "modified":
            apply_marker(tree, args.component)
            patch = subprocess.check_output(
                [
                    "git",
                    "diff",
                    "--",
                    "src/corelib/global/qlibraryinfo.cpp" if qt else "capi/geos_ts_c.cpp",
                ],
                cwd=tree,
            )
            (evidence / "marker.patch").write_bytes(patch)
            command(["cmake", "--build", build, "--target", "Core" if qt else "geos_c", "-j", "2"])
        libdir = work / phase
        libdir.mkdir()
        libraries = [build / "bin/Qt6Core.dll"] if qt else list(build.rglob("geos*.dll"))
        if not libraries:
            raise ValueError("No built libraries")
        for library in libraries:
            x64(library)
            shutil.copy2(library, libdir / library.name)
        if qt:
            selected_exe = libdir / "consumer.exe"
            shutil.copy2(exe, selected_exe)
            call = [selected_exe]
            lib = libdir / "Qt6Core.dll"
        else:
            lib = libdir / "geos_c.dll"
            call = [sys.executable, HERE / "geos_consumer.py", lib]
        original = json.loads(subprocess.check_output([str(a) for a in call], text=True))
        results[phase] = {"synthetic": validate(original, phase, libdir)}
        if not qt:
            frozen = json.loads(subprocess.check_output([str(exe), str(lib)], text=True))
            if frozen["frozen"] is not True:
                raise ValueError("Consumer is not frozen")
            results[phase]["frozen"] = validate(frozen, phase, libdir)
        command(["dumpbin", "/dependents", lib])
        for file in libdir.glob("*.dll"):
            results[phase].setdefault("libraries", []).append(
                {"name": file.name, "sha256": sha(file), "architecture": "x64"}
            )
    before, after = results["original"]["synthetic"], results["modified"]["synthetic"]
    if before["loaded_sha256"] == after["loaded_sha256"]:
        raise ValueError("Modified library unchanged")
    if not qt and before["areas"] != after["areas"]:
        raise ValueError("Geometry regression")
    report = {
        "component": args.component,
        "repository": record["repository"],
        "commit": head,
        "source_archive_sha256": sha(archive),
        "consumer_sha256": sha(exe),
        "configure": [str(x) for x in config],
        "results": results,
        "windows": sys.getwindowsversion().build,
        "compiler": subprocess.run(["cl"], capture_output=True, text=True).stderr.strip(),
        "trusted_msix_demonstrated": False,
        "agrolines_recombination_demonstrated": False,
        "sac_approved": False,
        "legal_approved": False,
    }
    (evidence / "results.json").write_text(json.dumps(report, indent=2))
    shutil.copy2(build / "CMakeCache.txt", evidence)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
