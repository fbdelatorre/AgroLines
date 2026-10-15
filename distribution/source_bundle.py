"""Local, versioned THIRD-PARTY source delivery. Never includes application code."""

import argparse
import hashlib
import json
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def obtain(row, cache):
    name = row["filename"]
    if Path(name).name != name or name.endswith((".py", ".pyc", ".exe", ".dll", ".pyd")):
        raise ValueError("Only named upstream source archives are permitted")
    path = Path(cache) / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        if row.get("url"):
            if not row["url"].startswith("https://"):
                raise ValueError("HTTPS upstream source required")
            with urllib.request.urlopen(row["url"], timeout=90) as response:
                if not response.url.startswith("https://"):
                    raise ValueError("Insecure upstream redirect")
                with path.open("xb") as stream:
                    while block := response.read(1024 * 1024):
                        stream.write(block)
        else:
            repository, commit = row["repository"], row["commit"]
            if not repository.startswith("https://github.com/") or len(commit) != 40:
                raise ValueError("Pinned official source repository required")
            with tempfile.TemporaryDirectory(dir=cache) as work:
                subprocess.run(["git", "init", "--bare", work], check=True, capture_output=True)
                subprocess.run(
                    ["git", "-C", work, "fetch", "--depth=1", repository, commit],
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    [
                        "git",
                        "-C",
                        work,
                        "-c",
                        "tar.umask=0002",
                        "-c",
                        "core.autocrlf=false",
                        "-c",
                        "core.eol=lf",
                        "archive",
                        "--format=tar",
                        "--prefix=" + row["source_prefix"] + "/",
                        "-o",
                        str(path.resolve()),
                        commit,
                    ],
                    check=True,
                    capture_output=True,
                )
    if sha(path) != row["sha256"]:
        raise ValueError("Upstream source hash differs: " + name)
    return path


def create(cache, output, lock=None):
    lock = lock or json.loads((ROOT / "distribution/legal/source-delivery.json").read_text())
    output = Path(output)
    if output.exists():
        raise ValueError("Fresh source delivery required")
    output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        names = set()
        for row in lock["sources"]:
            path = obtain(row, cache)
            if path.name in names:
                raise ValueError("Duplicate upstream source name")
            names.add(path.name)
            package.write(path, "sources/" + path.name)
            records.append(
                {**row, "archive_path": "sources/" + path.name, "size_bytes": path.stat().st_size}
            )
        # Only hash-bound redistributable third-party notices/recipes, no repo-wide copy.
        materials = json.loads(
            (ROOT / "distribution/legal/supplemental/materials.json").read_text()
        )
        from distribution.legal_materials import safe_file

        for row in materials["materials"]:
            if not row["components"]:
                continue
            path = safe_file(ROOT / "distribution/legal/supplemental", row["file"])
            if sha(path) != row["sha256"]:
                raise ValueError("Changed source recipe/notice")
            package.write(path, "materials/" + row["file"])
        result = {
            "sources": records,
            "complete_corresponding_source_offer": False,
            "remaining": lock["remaining"],
            "own_application_source_included": False,
            "legal_approved": False,
            "distribution_approved": False,
        }
        package.writestr("manifest.json", json.dumps(result, ensure_ascii=False, indent=2))
        package.writestr("LEIA-ME.txt", lock["notice"])
    result["sha256"] = sha(output)
    result["file"] = output.name
    output.with_suffix(".json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def stage(payload, source, lock=None):
    import shutil

    source, payload = Path(source), Path(payload)
    record = json.loads(source.with_suffix(".json").read_text())
    lock = lock or json.loads((ROOT / "distribution/legal/source-delivery.json").read_text())

    if sha(source) != record["sha256"] or record["own_application_source_included"]:
        raise ValueError("Invalid third-party source delivery")
    with zipfile.ZipFile(source) as package:
        internal = json.loads(package.read("manifest.json"))
        if internal["sources"] != record["sources"]:
            raise ValueError("Source delivery manifest mismatch")
        measured = [
            {k: v for k, v in row.items() if k not in ("archive_path", "size_bytes")}
            for row in record["sources"]
        ]
        if measured != lock["sources"]:
            raise ValueError("Unauthorized source identity or version")
        expected = {r["archive_path"] for r in record["sources"]}
        materials = json.loads(
            (ROOT / "distribution/legal/supplemental/materials.json").read_text()
        )
        legal_files = {
            "materials/" + r["file"]: r["sha256"] for r in materials["materials"] if r["components"]
        }
        if set(package.namelist()) != expected | set(legal_files) | {
            "manifest.json",
            "LEIA-ME.txt",
        }:
            raise ValueError("Unauthorized source-bundle member")
        if len(package.namelist()) != len(set(package.namelist())):
            raise ValueError("Duplicate source-bundle member")
        for name, expected_hash in legal_files.items():
            if hashlib.sha256(package.read(name)).hexdigest() != expected_hash:
                raise ValueError("Changed source recipe/notice")

        if any(
            not name.startswith(("sources/", "materials/"))
            and name not in ("manifest.json", "LEIA-ME.txt")
            for name in package.namelist()
        ):
            raise ValueError("Unauthorized file in source delivery")
        for row in record["sources"]:
            with package.open(row["archive_path"]) as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != row["sha256"]:
                    raise ValueError("Changed source archive")
        if {n for n in package.namelist() if n.startswith("sources/")} != expected:
            raise ValueError("Unexpected upstream source archive")
    target = payload / "third-party-sources"
    target.mkdir()
    shutil.copyfile(source, target / "AgroLines-Third-Party-Sources.zip")
    record["payload_file"] = "third-party-sources/AgroLines-Third-Party-Sources.zip"
    (target / "delivery.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create(args.cache, args.output), ensure_ascii=False))


if __name__ == "__main__":
    main()
