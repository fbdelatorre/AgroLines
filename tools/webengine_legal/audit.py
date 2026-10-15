"""Inspect official source and the Windows wheel without executing their code.

Matching version strings is useful evidence, not proof of complete corresponding
source or legal approval. No output of this module is an authorization to release.
"""

import argparse
import hashlib
import json
import re
import struct
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def checked_download(url, destination, expected, limit):
    destination = Path(destination)
    if destination.exists():
        if digest(destination) != expected:
            raise ValueError("Existing input hash differs; original file preserved")
        return destination
    temporary = destination.with_suffix(destination.suffix + ".part")
    if temporary.exists():
        raise ValueError("Previous partial download preserved; choose a fresh directory")
    if not url.startswith("https://"):
        raise ValueError("HTTPS source required")
    try:
        with urllib.request.urlopen(url, timeout=30) as response, temporary.open("xb") as out:
            if not response.url.startswith("https://"):
                raise ValueError("HTTPS redirect required")
            count = 0
            for block in iter(lambda: response.read(1024 * 1024), b""):
                count += len(block)
                if count > limit:
                    raise ValueError("Source exceeds the bounded expected size")
                out.write(block)
        if digest(temporary) != expected:
            raise ValueError("Official input checksum mismatch")
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def returned_literal(pe, address):
    """Recognize this x64 export's LEA RAX,[RIP+disp32]; RET. Never execute it."""
    code = pe.get_data(address, 8)
    if code[:3] != b"\x48\x8d\x05" or code[7:8] != b"\xc3":
        raise ValueError("Unsupported exported function; no string-search inference")
    target = address + 7 + struct.unpack("<i", code[3:7])[0]
    value = pe.get_string_at_rva(target, 64).decode("ascii")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2,3}", value):
        raise ValueError("Unexpected exported version literal")
    return value


def inspect_wheel(path, record):
    if digest(path) != record["sha256"]:
        raise ValueError("Wheel differs from the audited official input")
    import pefile

    names = {
        "?qWebEngineVersion@@YAPEBDXZ": "qt_webengine",
        "?qWebEngineChromiumVersion@@YAPEBDXZ": "chromium",
        "?qWebEngineChromiumSecurityPatchVersion@@YAPEBDXZ": "security_patch",
    }
    with ZipFile(path) as wheel:
        data = wheel.read(record["dll"])
        if hashlib.sha256(data).hexdigest() != record["dll_sha256"]:
            raise ValueError("Native input differs from the original payload inventory")
    with pefile.PE(data=data, fast_load=True) as pe:
        if pe.FILE_HEADER.Machine != 0x8664:
            raise ValueError("Only the audited Windows x64 input is accepted")
        pe.parse_data_directories(directories=[0])
        versions = {
            names[entry.name.decode()]: returned_literal(pe, entry.address)
            for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols
            if entry.name and entry.name.decode() in names
        }
    if set(versions) != set(names.values()):
        raise ValueError("Required version exports missing")
    return {"sha256": record["sha256"], "dll_sha256": record["dll_sha256"], **versions}


def inspect_archive(path, record):
    if digest(path) != record["sha256"]:
        raise ValueError("Source archive checksum mismatch")
    wanted = (
        "/.tag",
        "/.cmake.conf",
        "/CHROMIUM_VERSION",
        "/src/3rdparty/chromium/chrome/VERSION",
        "/src/core/configure/BUILD.root.gn.in",
        "/cmake/QtGnCredits.cmake",
    )
    files, notices, generated_credits = {}, [], []
    with tarfile.open(path, "r|xz") as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("Unsafe archive member")
            if not member.isfile():
                continue  # no extraction, no symlink traversal, no code execution
            selected = any(member.name.endswith(suffix) for suffix in wanted)
            notice = bool(
                re.fullmatch(
                    r"(?:LICENSE|LICENCE|COPYING|NOTICE|AUTHORS|COPYRIGHT)(?:[._-].*)?",
                    name.name,
                    re.I,
                )
            )
            if selected or notice:
                if member.size > 2 * 1024 * 1024:
                    raise ValueError("Unexpectedly large evidence document")
                value = archive.extractfile(member).read()
                row = {"path": member.name, "sha256": hashlib.sha256(value).hexdigest()}
                if notice:
                    notices.append(row)
                if selected:
                    files[member.name] = {**row, "text": value.decode("utf-8", errors="replace")}
            if name.name in ("chromium_attributions.qdoc", "pdf_attributions.qdoc"):
                generated_credits.append(member.name)
    versions = [r for p, r in files.items() if p.endswith(wanted[3])]
    if len(versions) != 1:
        raise ValueError("A single effective Chromium chrome/VERSION is required")
    parts = dict(line.split("=", 1) for line in versions[0]["text"].splitlines() if "=" in line)
    chromium = ".".join(parts[key] for key in ("MAJOR", "MINOR", "BUILD", "PATCH"))
    return {
        "sha256": record["sha256"],
        "chromium": chromium,
        "selected_documents": list(files.values()),
        "source_notice_inventory": notices,
        "generated_credits_paths": generated_credits,
        "source_notice_inventory_is_not_a_binary_target_bom": True,
    }


def assessment(wheel, candidate, archive=None):
    # Even complete equality of public strings cannot establish missing build facts.
    return {
        "versions_match_candidate": all(
            wheel.get(k) is not None and wheel[k] == candidate.get(k)
            for k in ("qt_webengine", "chromium", "security_patch")
        ),
        "source_archive_verified": archive is not None,
        "effective_source_chromium_matches": archive is not None
        and wheel["chromium"] == archive["chromium"],
        "exact_wheel_source_correspondence_proven": False,
        "actual_target_generated_credits_proven": False,
        "legal_approved": False,
        "distribution_approved": False,
        "remaining": [
            "Bind final source/build modifications to this exact wheel; "
            "version equality alone is insufficient",
            "Verify actual target notices/static components/codecs and permitted source delivery",
            "Review LGPL shared-library/recombination rights and final installation information",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--skip-archive", action="store_true")
    args = parser.parse_args()
    inputs = json.loads((HERE / "inputs.json").read_text())
    args.directory.mkdir(parents=True, exist_ok=True)
    record = inputs["wheel"]
    wheel = args.wheel or checked_download(
        record["url"], args.directory / record["filename"], record["sha256"], 500 * 1024 * 1024
    )
    observed = inspect_wheel(wheel, record)
    archive = None
    if not args.skip_archive:
        row = inputs["source_archive"]
        path = checked_download(
            row["url"], args.directory / row["filename"], row["sha256"], 800 * 1024 * 1024
        )
        archive = inspect_archive(path, row)
    report = {
        "wheel": observed,
        "candidate": inputs["candidate"],
        "source_archive": archive,
        "assessment": assessment(observed, inputs["candidate"], archive),
        "application_executed": False,
        "installation_performed": False,
        "payload_modified": False,
    }
    out = args.directory / "report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(out), "wheel": observed, **report["assessment"]}))


if __name__ == "__main__":
    main()
