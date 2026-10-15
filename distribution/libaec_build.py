"""Maintainer build of BSD libaec's SZIP-compatible DLL; no geometry changes."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

SOURCE_COMMIT = "0c4c01463d2c64a112a61271d317b74efb660608"
SOURCE_SHA256 = "33d1207ee309154331b58715cef998d65b86bd8421fa5418254c16e18ccb3da8"
SOURCE_URL = (
    "https://codeload.github.com/Deutsches-Klimarechenzentrum/libaec/tar.gz/" + SOURCE_COMMIT
)
VERSION = "1.1.7"
SLOT = "_internal/fiona.libs/szip-d0425ee11b05cea2ef5907b56ab33522.dll"
ORIGINAL_SHA256 = "aaff372f56a8221f198522cca5a5494109b3151613620c13aabdddbcedfdd876"
ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(directory):
    directory = Path(directory).resolve()
    if directory.exists():
        raise ValueError("Fresh source build directory required")
    directory.mkdir(parents=True)
    archive = directory / "libaec-1.1.7.tar.gz"
    with urllib.request.urlopen(SOURCE_URL, timeout=90) as response:
        archive.write_bytes(response.read())
    if sha(archive) != SOURCE_SHA256:
        raise ValueError("libaec official source hash mismatch")
    with tarfile.open(archive) as source:
        source.extractall(directory / "source", filter="data")
    source = next((directory / "source").iterdir())
    # Only the filename needed by already-linked HDF5 changes. No source algorithm patch.
    addition = f'\nset_target_properties(sz-shared PROPERTIES OUTPUT_NAME "{Path(SLOT).stem}")\n'
    with (source / "CMakeLists.txt").open("a", encoding="utf-8") as stream:
        stream.write(addition)
    (directory / "output-name.cmake.txt").write_text(addition, encoding="utf-8")
    configure = [
        "cmake",
        "-S",
        str(source),
        "-B",
        str(directory / "build"),
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBUILD_SHARED_LIBS=ON",
        "-DBUILD_STATIC_LIBS=OFF",
        "-DBUILD_TESTING=ON",
    ]
    subprocess.run(configure, check=True)
    subprocess.run(["cmake", "--build", str(directory / "build"), "--parallel", "2"], check=True)
    tests = subprocess.run(
        ["ctest", "--test-dir", str(directory / "build"), "--output-on-failure"],
        check=True,
        capture_output=True,
        text=True,
    )
    (directory / "ctest.txt").write_text(tests.stdout + tests.stderr)
    binary = next((directory / "build").rglob(Path(SLOT).name))
    import pefile

    with pefile.PE(str(binary)) as pe:
        if pe.FILE_HEADER.Machine != 0x8664:
            raise ValueError("x64 libaec required")
        exports = sorted(s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name)
        imports = [r.dll.decode() for r in pe.DIRECTORY_ENTRY_IMPORT]
    if any("aec" in name.casefold() or "szip" in name.casefold() for name in imports):
        raise ValueError("Unexpected extra codec DLL: require self-contained libsz/aec objects")
    record = {
        "component": "libaec-SZIP",
        "version": VERSION,
        "license": "BSD-2-Clause",
        "source_commit": SOURCE_COMMIT,
        "source_url": SOURCE_URL,
        "source_archive_sha256": SOURCE_SHA256,
        "source_algorithm_modified": False,
        "filename_only_cmake_addition": addition,
        "binary": str(binary),
        "binary_sha256": sha(binary),
        "binary_size": binary.stat().st_size,
        "exports": exports,
        "imports": imports,
        "configure": configure,
        "ctest_passed": True,
        "ctest_output": tests.stdout,
        "replaced_slot": SLOT,
        "original_sha256": ORIGINAL_SHA256,
        "legal_approved": False,
        "signing_performed": False,
    }
    (directory / "provenance.json").write_text(json.dumps(record, indent=2) + "\n")
    print("AGROLINES_LIBAEC_BUILD=" + json.dumps(record))
    return record


def evidence(root):
    root = Path(root)
    record = json.loads((root / "libaec-provenance.json").read_text())
    if (
        record["source_commit"] != SOURCE_COMMIT
        or record["source_archive_sha256"] != SOURCE_SHA256
        or record["version"] != VERSION
        or record["source_algorithm_modified"]
        or record["ctest_passed"] is not True
    ):
        raise ValueError("Unrecognized codec source/build evidence")
    if sha(root / SLOT) != record["binary_sha256"]:
        raise ValueError("Codec differs from bound source build")
    return record


def stage(root):
    root = Path(root)
    record = json.loads((ROOT / "build/legal-native/provenance.json").read_text())
    source = Path(record["binary"])
    target = root / SLOT
    if sha(target) != ORIGINAL_SHA256 or sha(source) != record["binary_sha256"]:
        raise ValueError("Unexpected original SZIP or rebuilt libaec bytes")
    # All imports of the existing consumers must remain available.
    import pefile

    required = set()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in (".exe", ".dll", ".pyd"):
            continue
        with pefile.PE(str(path), fast_load=True) as pe:
            pe.parse_data_directories(directories=[1])
            for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
                if entry.dll.decode().casefold() == target.name.casefold():
                    required.update(i.name.decode() for i in entry.imports if i.name)
    if not required or not required.issubset(record["exports"]):
        raise ValueError("SZIP replacement does not satisfy actual consumer ABI")
    shutil.copyfile(source, target)
    record["required_consumer_exports"] = sorted(required)
    (root / "libaec-provenance.json").write_text(json.dumps(record, indent=2) + "\n")
    return evidence(root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    build(parser.parse_args().build)
