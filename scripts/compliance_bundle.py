"""Assemble allowlisted THIRD-PARTY sources locally; never upload or publish them."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath


def pack(dossier, source_dir, output):
    dossier, source_dir, output = Path(dossier), Path(source_dir), Path(output)
    data = json.loads((dossier / "sources-index.json").read_text())
    files = []
    for record in data["sources"]:
        if "sha256" not in record or "filename" not in record:
            continue
        name = record["filename"]
        if PurePosixPath(name).name != name or "\\" in name:
            raise ValueError("Source archive must have a plain filename")
        candidates = [source_dir / name, source_dir / "pypi" / name]
        source = next((p for p in candidates if p.is_file()), None)
        if (
            source is None
            or source.is_symlink()
            or not source.resolve().is_relative_to(source_dir.resolve())
        ):
            raise ValueError("Missing or unsafe third-party archive: " + name)
        if hashlib.file_digest(source.open("rb"), "sha256").hexdigest() != record["sha256"]:
            raise ValueError("Source hash mismatch: " + name)
        files.append((source, "sources/" + name))
    for file in sorted((dossier / "notices").rglob("*")):
        if file.is_symlink():
            raise ValueError("No symlinks in legal documents")
        if file.is_file():
            files.append((file, "notices/" + file.relative_to(dossier / "notices").as_posix()))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError("Refusing to overwrite a prepared bundle")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source, target in files:
            entry = zipfile.ZipInfo(target, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, source.read_bytes())
        archive.writestr("sources-index.json", json.dumps(data, indent=2))
        archive.writestr(
            "README.txt",
            (
                "PARTIAL THIRD-PARTY MATERIALS FOR REVIEW ONLY. NOT AN APPROVED SOURCE OFFER.\n"
                "No AgroLines implementation, objects, bytecode, keys or customer data.\n"
                "Exact Windows binary/build correspondence remains as recorded in the index.\n"
                "No publication, installation, signature or license approval is performed.\n"
            ),
        )
    report = {
        "filename": output.name,
        "sha256": hashlib.file_digest(output.open("rb"), "sha256").hexdigest(),
        "size_bytes": output.stat().st_size,
        "third_party_archives": len(data["sources"]),
        "published": False,
        "complete_corresponding_source": False,
    }
    output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", type=Path, default=Path("docs/compliance"))
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(pack(args.dossier, args.source_dir, args.output), indent=2))


if __name__ == "__main__":
    main()
