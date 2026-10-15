"""Source-controlled builds of the SAME two GEOS versions, no algorithm patches."""

import argparse
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

from distribution.source_bundle import obtain, sha

ROOT = Path(__file__).resolve().parent.parent
VERSIONS = {"GEOS-Fiona": "3.11.3", "GEOS-Shapely": "3.14.1"}


def source_record(component):
    version = VERSIONS[component]
    return next(
        r
        for r in json.loads((ROOT / "distribution/legal/source-delivery.json").read_text())[
            "sources"
        ]
        if r["component"] == "geos-" + version
    )


def build(work, cache):
    work = Path(work).resolve()
    if work.exists():
        raise ValueError("Fresh GEOS source build directory required")
    work.mkdir(parents=True)
    original = json.loads((ROOT / "docs/compliance/inventory.json").read_text())
    records = []
    for component, version in VERSIONS.items():
        row = source_record(component)
        archive = obtain(row, cache)
        directory = work / version
        with tarfile.open(archive) as package:
            package.extractall(directory, filter="data")
        tree = directory / row["source_prefix"]
        algorithms = {
            p.relative_to(tree).as_posix(): sha(p)
            for p in tree.rglob("*")
            if p.is_file() and p.suffix in (".c", ".cpp", ".h", ".hpp", ".in")
        }
        targets = [r for r in original["files"] if r["component"] == component]
        if len(targets) != 2:
            raise ValueError("Expected both GEOS C/C++ DLLs")
        addition = (
            "\n"
            + "\n".join(
                "set_target_properties("
                + ("geos_c" if Path(r["path"]).name.startswith("geos_c-") else "geos")
                + ' PROPERTIES OUTPUT_NAME "'
                + Path(r["path"]).stem
                + '")'
                for r in targets
            )
            + "\n"
        )
        with (tree / "CMakeLists.txt").open("a", encoding="utf-8") as stream:
            stream.write(addition)
        binary_dir = directory / "build"
        configure = [
            "cmake",
            "-S",
            str(tree),
            "-B",
            str(binary_dir),
            "-G",
            "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_SHARED_LIBS=ON",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
            "-DBUILD_TESTING=OFF",
            "-DBUILD_BENCHMARKS=OFF",
        ]
        subprocess.run(configure, check=True)
        subprocess.run(["cmake", "--build", str(binary_dir), "--parallel", "2"], check=True)
        if any(sha(tree / p) != h for p, h in algorithms.items()):
            raise ValueError("GEOS algorithm/header input changed")
        for target in targets:
            binary = next(binary_dir.rglob(Path(target["path"]).name))
            records.append(
                {
                    "component": component,
                    "version": version,
                    "source": row,
                    "path": target["path"],
                    "original_sha256": target["sha256"],
                    "binary": str(binary),
                    "sha256": sha(binary),
                    "configure": configure,
                    "cmake_output_name_addition": addition,
                    "source_algorithms_unchanged": True,
                }
            )
    result = {"files": records, "legal_approved": False, "signing_performed": False}
    (work / "provenance.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def evidence(payload):
    payload = Path(payload)
    path = payload / "geos-source-builds.json"
    if not path.is_file():
        return {}
    rows = json.loads(path.read_text())["files"]
    if len(rows) != 4 or len({r["path"] for r in rows}) != 4:
        raise ValueError("Both independent GEOS pairs required")
    result = {}
    originals = {
        r["path"]: r
        for r in json.loads((ROOT / "docs/compliance/inventory.json").read_text())["files"]
    }
    for row in rows:
        if (
            row["source"] != source_record(row["component"])
            or row["version"] != VERSIONS[row["component"]]
            or not row["source_algorithms_unchanged"]
            or originals[row["path"]]["sha256"] != row["original_sha256"]
            or sha(payload / row["path"]) != row["sha256"]
        ):
            raise ValueError("GEOS source/build correspondence mismatch")
        result[row["path"]] = row
    return result


def stage(payload):
    import pefile

    payload = Path(payload)
    data = json.loads((ROOT / "build/legal-geos/provenance.json").read_text())
    for row in data["files"]:
        source, target = Path(row["binary"]), payload / row["path"]
        if sha(target) != row["original_sha256"] or sha(source) != row["sha256"]:
            raise ValueError("Unexpected original or rebuilt GEOS bytes")
        with pefile.PE(str(source), max_symbol_exports=65536) as pe:
            if pe.FILE_HEADER.Machine != 0x8664:
                raise ValueError("GEOS x64 required")
            exports = {s.name for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
        for consumer in payload.rglob("*"):
            if consumer.suffix.casefold() not in (".exe", ".dll", ".pyd"):
                continue
            with pefile.PE(str(consumer), fast_load=True) as pe:
                pe.parse_data_directories(directories=[1, 13])
                for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []) + getattr(
                    pe, "DIRECTORY_ENTRY_DELAY_IMPORT", []
                ):
                    if entry.dll.decode().casefold() == target.name.casefold():
                        if any(i.name is None or i.name not in exports for i in entry.imports):
                            raise ValueError("Rebuilt GEOS cannot satisfy actual imported ABI")
        shutil.copyfile(source, target)
    (payload / "geos-source-builds.json").write_text(json.dumps(data, indent=2) + "\n")
    return evidence(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    build(args.work, args.cache)
