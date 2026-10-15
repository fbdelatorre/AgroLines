"""Isolated Linux experiment. SPDX-License-Identifier: 0BSD. Never changes AgroLines."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CMAKE = shutil.which("cmake")
NINJA = shutil.which("ninja")


def command(args, cwd=None, env=None):
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--cmake", default=CMAKE)
    parser.add_argument("--ninja", default=NINJA)
    args = parser.parse_args()
    if not sys.platform.startswith("linux") or not args.cmake or not args.ninja:
        raise SystemExit(
            "This PoC requires Linux, trusted cmake/ninja and GCC; not a Windows route"
        )
    if args.work.exists():
        raise SystemExit("Choose a fresh isolated working directory")
    args.work.mkdir(parents=True)
    sources = json.loads((REPO / "docs/compliance/sources-index.json").read_text())["sources"]
    for name in ("qtbase-6.12.0", "geos-3.11.3"):
        record = next(r for r in sources if r["component"] == name)
        archive = args.source_dir / record["filename"]
        with archive.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == record["sha256"]
        with tarfile.open(archive) as source:
            source.extractall(args.work, filter="data")
        tree, build = args.work / name, args.work / (name + "-build")
        common = [
            args.cmake,
            "-S",
            tree,
            "-B",
            build,
            "-G",
            "Ninja",
            "-DCMAKE_MAKE_PROGRAM=" + args.ninja,
            "-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_SHARED_LIBS=ON",
        ]
        if name.startswith("qt"):
            features = (
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
            )
            command(
                common
                + ["-DQT_BUILD_TESTS=OFF", "-DQT_BUILD_EXAMPLES=OFF"]
                + ["-DFEATURE_" + f + "=OFF" for f in features]
            )
            target, patch, library = "Core", "qt-synthetic.patch", "libQt6Core.so.6.12.0"
            command([args.cmake, "--build", build, "--target", target, "-j", "2"])
            base = args.work / "qt-original"
            shutil.copytree(build / "lib", base, symlinks=True)
            exe = args.work / "qt-synthetic-consumer"
            command(
                [
                    "g++",
                    REPO / "tools/compliance-poc/qt_consumer.cpp",
                    "-I" + str(build / "include"),
                    "-I" + str(build / "include/QtCore"),
                    "-I" + str(build / "src/corelib"),
                    "-L" + str(base),
                    "-lQt6Core",
                    "-Wl,-rpath," + str(base),
                    "-o",
                    exe,
                ]
            )
            consumer = [exe]
        else:
            command(
                common
                + [
                    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
                    "-DBUILD_TESTING=OFF",
                    "-DBUILD_BENCHMARKS=OFF",
                ]
            )
            target, patch, library = "geos_c", "geos-synthetic.patch", "libgeos_c.so.1.17.3"
            command([args.cmake, "--build", build, "--target", target, "-j", "2"])
            base = args.work / "geos-original"
            shutil.copytree(build / "lib", base, symlinks=True)
            consumer = [sys.executable, REPO / "tools/compliance-poc/geos_consumer.py"]
        results = {}
        for phase in ("original", "modified"):
            if phase == "modified":
                command(["git", "apply", REPO / "tools/compliance-poc" / patch], cwd=tree)
                command([args.cmake, "--build", build, "--target", target, "-j", "2"])
            libroot = base if phase == "original" else build / "lib"
            env = os.environ.copy()
            # Child-only ELF test; no Windows setting, code policy or installed app is changed.
            env["LD_LIBRARY_PATH"] = str(libroot)
            call = consumer if name.startswith("qt") else consumer + [libroot / "libgeos_c.so"]
            output = subprocess.check_output([str(a) for a in call], env=env, text=True)
            result = json.loads(output)
            assert ("agrolines-synthetic" in result["version"]) == (phase == "modified")
            results[phase] = result
        (args.work / (name + "-results.json")).write_text(json.dumps(results, indent=2))
        assert (base / library).read_bytes() != (build / "lib" / library).read_bytes()


if __name__ == "__main__":
    main()
