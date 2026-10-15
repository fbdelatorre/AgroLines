"""Verify exact Fiona GDAL recipe/source inputs; never executes downloaded code."""

import argparse
import base64
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path
from zipfile import ZipFile

WHEEL_SHA = "41cde2c52c614457e9094ea44b0d30483540789e62fe0fa758c2a2963e980817"
TREE = "65b271a32a93a9dfa4dfd3905fcd0b5388926f81"


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def digest(data, algorithm="sha256"):
    return hashlib.new(algorithm, data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Fresh output directory required")
    if digest(args.wheel.read_bytes()) != WHEEL_SHA:
        raise SystemExit("Wrong Fiona wheel")
    args.output.mkdir(parents=True)
    with ZipFile(args.wheel) as wheel:
        spdx_bytes = wheel.read("fiona/gdal_data/vcpkg.spdx.json")
    spdx = json.loads(spdx_bytes)
    tree_url = "repos/microsoft/vcpkg/git/trees/" + TREE
    tree = api(tree_url)
    records = []
    for entry in spdx["files"]:
        name = entry["fileName"].rsplit("/", 1)[-1]
        item = next(f for f in tree["tree"] if f["path"] == name)
        blob = api("repos/microsoft/vcpkg/git/blobs/" + item["sha"])
        data = base64.b64decode(blob["content"])
        git_sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if git_sha != item["sha"]:
            raise ValueError("Git blob mismatch")
        expected = entry["checksums"][0]["checksumValue"]
        crlf = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        actual = data if digest(data) == expected else crlf
        if digest(actual) != expected:
            raise ValueError("Recipe input differs from distributed SPDX: " + name)
        (args.output / name).write_bytes(actual)
        records.append(
            {
                "file": name,
                "git_blob": git_sha,
                "url": "https://api.github.com/repos/microsoft/vcpkg/git/blobs/" + git_sha,
                "sha256": expected,
                "windows_crlf": actual == crlf,
                "exact_spdx_match": True,
            }
        )
    source_url = "https://github.com/OSGeo/gdal/archive/refs/tags/v3.9.1.tar.gz"
    resource = next(p for p in spdx["packages"] if p["name"] == "OSGeo/gdal")
    expected = resource["checksums"][0]["checksumValue"]
    with urllib.request.urlopen(source_url, timeout=90) as response:
        data = response.read()
    if digest(data, "sha512") != expected:
        raise ValueError("Source archive differs from SPDX")
    (args.output / "gdal-3.9.1-exact.tar.gz").write_bytes(data)
    report = {
        "wheel_sha256": WHEEL_SHA,
        "spdx_sha256": digest(spdx_bytes),
        "recipe_tree": TREE,
        "records": records,
        "source": {
            "url": source_url,
            "sha512": expected,
            "sha256": digest(data),
            "bytes": len(data),
        },
        "scope": (
            "Exact declared source and recipe inputs; "
            "NOT binary reproduction or complete GDAL driver/source BOM"
        ),
        "legal_approved": False,
    }
    (args.output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Verified nine recipe files and source SHA-512 against shipped SPDX")


if __name__ == "__main__":
    main()
