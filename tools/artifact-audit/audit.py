"""Read-only, pinned artifact inspection; never load PE files or install packages."""

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from defusedxml import ElementTree as ET

COMMIT = "c3ffdb68302a0c46e640e68dc0b561acce250e6d"
OUTER_SHA = "daad44ae384df63c357225474e531bf8d7ba39205212b3b0c8a02b97a82679e1"
MSIX_SHA = "e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b"
PREFIX = "VFS/ProgramFilesX64/AgroLines/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_entries(archive):
    names = archive.namelist()
    seen = set()
    for info in archive.infolist():
        # ZipInfo normalizes Windows separators on read as well as write. Validate
        # the original decoded name, including NULs, before trusting the normalized key.
        name = info.orig_filename
        require(name == info.filename, "ZIP name was silently normalized or truncated")
        require(
            name
            and "\\" not in name
            and ":" not in name
            and not PurePosixPath(name).is_absolute()
            and all(p not in ("", ".", "..") for p in name.rstrip("/").split("/"))
            and not any(p.endswith((".", " ")) for p in name.rstrip("/").split("/"))
            and name.casefold() not in seen
            and (info.external_attr >> 16) & 0o170000 != 0o120000,
            f"Unsafe, duplicate or symlink ZIP member: {name}",
        )
        seen.add(name.casefold())
        require(info.file_size < 1024**3, "Oversized archive member")
    require(sum(i.file_size for i in archive.infolist()) < 2 * 1024**3, "Oversized ZIP")
    return names


def pe_header(data):
    require(len(data) >= 64 and data[:2] == b"MZ", "Invalid DOS header")
    offset = struct.unpack_from("<I", data, 60)[0]
    require(offset + 24 + 152 <= len(data), "Truncated PE")
    require(data[offset : offset + 4] == b"PE\0\0", "Invalid PE header")
    require(struct.unpack_from("<H", data, offset + 4)[0] == 0x8664, "Not x64")
    optional = offset + 24
    require(struct.unpack_from("<H", data, optional)[0] == 0x20B, "Not PE32+")
    start, size = struct.unpack_from("<II", data, optional + 112 + 32)
    require(bool(start) == bool(size), "Invalid certificate table pair")
    require(not size or start + size <= len(data), "Certificate table outside file")
    return bool(size)


def chain_class(row):
    sig, tool = row["signature"], row["signtool"]
    require(sig["integrity_matches"] and tool["integrity_matches"], "Digest binding failed")
    require(not sig.get("inspection_error") and not tool.get("timeout"), "Inspection failed")
    if sig["status"] == "NotSigned":
        require(
            not sig["chain_valid"] and not sig["chain_status"],
            "Unsigned chain conflict",
        )
        require(tool["exit_code"] != 0, "Unsigned SignTool conflict")
        return "unsigned_no_signer_chain"
    require(sig["status"] == "Valid" and tool["exit_code"] == 0, "Unaccepted signature")
    if sig["chain_valid"]:
        require(not sig["chain_status"], "Unexpected chain warning")
        return "historical_chain_valid"
    require(set(sig["chain_status"]) == {"NotTimeValid"}, "Unexpected trust failure")
    require(
        bool(sig.get("timestamp_signer"))
        and "The signature is timestamped:" in tool["stdout"]
        and "Timestamp Verified by:" in tool["stdout"],
        "Missing timestamp acceptance evidence",
    )
    return "current_time_expiry_historical_signtool_accepted"


def compare_containers(first, second):
    with ZipFile(first) as a, ZipFile(second) as b:
        safe_entries(a)
        safe_entries(b)
        ah = {n: sha(a.read(n)) for n in a.namelist()}
        bh = {n: sha(b.read(n)) for n in b.namelist()}
        metadata = [
            n
            for n in ah.keys() & bh.keys()
            if (
                a.getinfo(n).date_time,
                a.getinfo(n).compress_type,
                a.getinfo(n).external_attr,
            )
            != (
                b.getinfo(n).date_time,
                b.getinfo(n).compress_type,
                b.getinfo(n).external_attr,
            )
        ]
        return {
            "comparison_status": "performed",
            "container_bytes_identical": sha(Path(first).read_bytes())
            == sha(Path(second).read_bytes()),
            "entry_content_identical": ah == bh,
            "entry_order_identical": a.namelist() == b.namelist(),
            "metadata_differences": sorted(metadata),
        }


def audit(artifact, repo):
    raw = Path(artifact).read_bytes()
    require(sha(raw) == OUTER_SHA, "Outer artifact SHA256 mismatch")
    with ZipFile(io.BytesIO(raw)) as outer:
        names = safe_entries(outer)
        packages = [n for n in names if n.endswith(".msix")]
        require(len(names) == 26 and len(packages) == 1, "Unexpected artifact entries")
        package = outer.read(packages[0])
        require(sha(package) == MSIX_SHA, "MSIX SHA256 mismatch")
        original = {n: sha(outer.read(n)) for n in names}
        read = lambda n: json.loads(outer.read(n))  # noqa: E731
        rows = read("evidence/qt-minimal/native-current.json")["files"]
        first = read("evidence/signing/first-build.json")
        build_inputs = read("evidence/qt-minimal/build-inputs.json")["files"]
        source_metadata = read("evidence/qt-minimal/source-metadata.json")["files"]
        binding = read("evidence/signing/input-binding.json")
        require(binding["source_commit"] == COMMIT, "Wrong source commit")
        require(binding["package_sha256"] == MSIX_SHA, "Wrong report binding")
        require(
            binding["plan_sha256"]
            == sha(
                json.dumps(
                    read("evidence/signing/plan.json"), sort_keys=True, separators=(",", ":")
                ).encode()
            ),
            "Wrong plan",
        )
        with ZipFile(io.BytesIO(package)) as msix:
            members = safe_entries(msix)
            hashes = {n: sha(msix.read(n)) for n in members}
            require("AppxSignature.p7x" not in members, "Unexpected package signature")
            root = ET.fromstring(msix.read("AppxBlockMap.xml"))
            block_files = []
            for file in root:
                name = file.attrib["Name"].replace("\\", "/")
                block_files.append(name)
                data = msix.read(name)
                require(len(data) == int(file.attrib["Size"]), f"Block map size: {name}")
                blocks = [data[i : i + 65536] for i in range(0, len(data), 65536)]
                expected = [base64.b64encode(hashlib.sha256(b).digest()).decode() for b in blocks]
                require(
                    expected
                    == [
                        b.attrib["Hash"]
                        for b in file
                        if b.tag == "{http://schemas.microsoft.com/appx/2010/blockmap}Block"
                    ],
                    f"Block hash: {name}",
                )
                for child in file:
                    if child.tag == "{http://schemas.microsoft.com/appx/2021/blockmap}FileHash":
                        require(
                            child.attrib["Hash"]
                            == base64.b64encode(hashlib.sha256(data).digest()).decode(),
                            f"FileHash: {name}",
                        )
                    else:
                        require(
                            child.tag == "{http://schemas.microsoft.com/appx/2010/blockmap}Block",
                            "Unknown block map element",
                        )
            require(
                set(block_files) == set(members) - {"AppxBlockMap.xml", "[Content_Types].xml"},
                "Block map coverage mismatch",
            )
            payload = json.loads(msix.read(PREFIX + "payload-manifest.json"))
            require(first["files"] == payload["files"], "First build/payload mismatch")
            paths = {r["path"]: r["sha256"] for r in payload["files"]}
            actual = {
                n.removeprefix(PREFIX): h
                for n, h in hashes.items()
                if n.startswith(PREFIX) and n != PREFIX + "payload-manifest.json"
            }
            require(paths == actual and len(paths) == 768, "Payload mismatch")
            native = {
                n.removeprefix(PREFIX): msix.read(n)
                for n in members
                if n.startswith(PREFIX) and msix.read(n)[:2] == b"MZ"
            }
            require(set(native) == {r["path"] for r in rows}, "PE coverage mismatch")
            results = []
            for row in rows:
                path = row["path"]
                digest = sha(native[path])
                require(
                    digest
                    == row["sha256"]
                    == row["signature"]["sha256"]
                    == row["signtool"]["sha256"],
                    f"PE/report mismatch: {path}",
                )
                category = chain_class(row)
                require(
                    pe_header(native[path]) == (row["signature"]["status"] == "Valid"),
                    f"Certificate table/report mismatch: {path}",
                )
                require(row["pinned_origin_confirmed"], f"Unknown builder origin: {path}")
                require(
                    row["group"] == "own" or row["exact_build_source_match"],
                    f"Not matched to builder input: {path}",
                )
                if row["group"] != "own":
                    require(
                        row["build_input"] in build_inputs
                        and row["build_input"]["source_sha256"] == digest,
                        f"Unbound builder input: {path}",
                    )
                    require(
                        row["build_input_metadata"] in source_metadata
                        and row["build_input_metadata"]["sha256"] == digest,
                        f"Unbound source metadata: {path}",
                    )
                results.append(
                    {
                        "path": path,
                        "sha256": digest,
                        "group": row["group"],
                        "packages": row["packages"],
                        "build_input": row["build_input"],
                        "build_input_metadata": row["build_input_metadata"],
                        "importers_by_dll_name": row["importers_by_dll_name"],
                        "package_license_evidence": row["package_license_evidence"],
                        "signature": row["signature"],
                        "signtool_exit_code": row["signtool"]["exit_code"],
                        "signtool_stdout": row["signtool"]["stdout"],
                        "classification": category,
                        "loaded_phases": row["loaded_phases"],
                        "exact_builder_binary_match": row["exact_build_source_match"],
                        "license_review": row["license_review"],
                    }
                )
            notices = json.loads(msix.read(PREFIX + "third-party-notices/collected-notices.json"))
            for doc in notices["documents"]:
                require(
                    hashes[PREFIX + "third-party-notices/" + doc["path"]] == doc["sha256"],
                    "Notice mismatch",
                )
            policy_markers = {}
            git = lambda path: subprocess.check_output(  # noqa: E731
                ["git", "show", f"{COMMIT}:{path}"], cwd=repo
            )
            for ext in ("md", "html", "txt"):
                data = msix.read(
                    PREFIX + f"_internal/desktop/privacy_assets/politica-privacidade.{ext}"
                )
                require(
                    data == git(f"docs/privacy/offline/politica-privacidade.{ext}"),
                    "Privacy snapshot mismatch",
                )
                policy_markers[ext] = sorted(
                    set(re.findall(r"\[CONFIRMAR[^\]]*\]", data.decode("utf-8-sig")))
                )
            for key, path in (
                ("policy_sha256", "distribution/windows/signing/native-policy.json"),
                ("lock_sha256", "distribution/windows/requirements.lock"),
            ):
                # Discover exact pinned paths from the source tree, never a mutable HEAD.
                candidates = (
                    subprocess.check_output(
                        ["git", "ls-tree", "-r", "--name-only", COMMIT], cwd=repo
                    )
                    .decode()
                    .splitlines()
                )
                matches = [p for p in candidates if p.endswith(Path(path).name)]
                require(any(sha(git(p)) == binding[key] for p in matches), f"Unbound {key}")
            manifest = msix.read("AppxManifest.xml").decode("utf-8-sig")
            required = (
                "DelatorreCOrporation.AgroLines",
                "CN=43189595-B928-4D57-90A4-24300E4D4976",
                'Version="1.0.0.0"',
                'ProcessorArchitecture="x64"',
            )
            require(all(v in manifest for v in required), "Manifest identity mismatch")
            summary = {
                "source_commit": COMMIT,
                "source_tree": subprocess.check_output(
                    ["git", "rev-parse", f"{COMMIT}^{{tree}}"], cwd=repo
                )
                .decode()
                .strip(),
                "source_parents": subprocess.check_output(
                    ["git", "show", "-s", "--format=%P", COMMIT], cwd=repo
                )
                .decode()
                .strip()
                .split(),
                "outer_sha256": OUTER_SHA,
                "msix_sha256": MSIX_SHA,
                "outer_size": len(raw),
                "msix_size": len(package),
                "outer_entries": len(names),
                "msix_entries": len(members),
                "payload_manifest_verified": len(paths),
                "block_map_files_verified": len(block_files),
                "native_files": len(results),
                "classifications": dict(Counter(r["classification"] for r in results)),
                "groups": {
                    g: {
                        "total": sum(r["group"] == g for r in results),
                        "unsigned": sum(
                            r["group"] == g and r["classification"] == "unsigned_no_signer_chain"
                            for r in results
                        ),
                        "observed": sum(
                            r["group"] == g and bool(r["loaded_phases"]) for r in results
                        ),
                    }
                    for g in sorted({r["group"] for r in results})
                },
                "indexed_notices_verified": len(notices["documents"]),
                "privacy_pending_markers": policy_markers,
                "reproducibility_report": read("evidence/signing/reproducibility.json"),
                "msix_comparison_status": "not_run_no_second_msix",
                "historical_signature_results_only": True,
                "installed": False,
                "sac_validated": False,
                "legal_compliance_approved": False,
                "artifact_members_sha256": original,
            }
            return summary, results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary, rows = audit(args.artifact, args.repo)
    args.output.mkdir(parents=True, exist_ok=False)
    for name, data in (("audit.json", summary), ("native-files.json", rows)):
        (args.output / name).write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )
    fields = (
        "path",
        "sha256",
        "group",
        "packages",
        "classification",
        "chain_status",
        "signer",
        "signtool_exit_code",
        "loaded_phases",
    )
    with (args.output / "native-files.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **{k: row[k] for k in fields if k in row},
                    "packages": json.dumps(row["packages"], ensure_ascii=False),
                    "chain_status": ";".join(row["signature"]["chain_status"]),
                    "signer": row["signature"].get("signer"),
                    "loaded_phases": json.dumps(row["loaded_phases"]),
                }
            )
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "native_files",
                    "classifications",
                    "payload_manifest_verified",
                    "block_map_files_verified",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
