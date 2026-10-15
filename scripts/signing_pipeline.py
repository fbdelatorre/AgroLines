"""Fail-closed native signing policy. No certificate access or signing in Python."""

import argparse
import hashlib
import json
import re
import shutil
import struct
from collections import Counter
from pathlib import Path, PurePosixPath, PureWindowsPath
from zipfile import ZipFile

from distribution.payload import manifest, verify
from scripts.native_inventory import file_hash, inventory

RELEASE_REVIEWS = ("licensing", "lgpl_mechanism", "privacy_readiness", "owner_submission")


def release_review_blockers(policy):
    reviews = policy.get("release_reviews", {})
    blockers = []
    for name in RELEASE_REVIEWS:
        review = reviews.get(name, {})
        if review.get("approved") is not True or not review.get("evidence"):
            blockers.append(name)
    return blockers


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def safe_relative(value):
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or ":" in value
        or PureWindowsPath(value).drive
        or PurePosixPath(value).is_absolute()
        or any(p in ("", ".", "..") or p.endswith((" ", ".")) for p in value.split("/"))
    ):
        raise ValueError("Unsafe/noncanonical policy path")
    return value


def policy_records(policy):
    if policy.get("schema_version") != 1 or not policy.get("files"):
        raise ValueError("Missing signing policy")
    rows = {}
    for row in policy["files"]:
        key = safe_relative(row["path"]).casefold()
        if key in rows:
            raise ValueError("Duplicate Windows policy path")
        if row["action"] not in ("preserve_original", "sign_own", "sign_third_party", "blocked"):
            raise ValueError("Unknown signing action")
        if any(
            type(row.get(flag)) is not bool for flag in ("rights_confirmed", "origin_confirmed")
        ):
            raise ValueError("Rights/origin decisions must be explicit booleans")
        if not re.fullmatch(r"[a-f0-9]{64}", row["baseline_sha256"]):
            raise ValueError("Missing exact baseline SHA256")
        rows[key] = row
    return rows


def pe_content_digest(path, expected_unsigned_size=None, require_unsigned=False):
    """Mutation guard, not an Authenticode implementation or trust decision."""
    import hashlib

    data = bytearray(Path(path).read_bytes())
    if data[:2] != b"MZ" or len(data) < 64:
        raise ValueError("Missing DOS header")
    offset = struct.unpack_from("<I", data, 60)[0]
    if data[offset : offset + 4] != b"PE\0\0":
        raise ValueError("Missing PE header")
    optional = offset + 24
    magic = struct.unpack_from("<H", data, optional)[0]
    directory = optional + (112 if magic == 0x20B else 96 if magic == 0x10B else 0)
    if directory == optional or directory + 40 > len(data):
        raise ValueError("Invalid PE optional header")
    security = directory + 32
    start, size = struct.unpack_from("<II", data, security)
    if bool(start) != bool(size) or size and (start < security + 8 or start + size > len(data)):
        raise ValueError("Invalid PE certificate table")
    if require_unsigned and size:
        raise ValueError("Unrecognized existing certificate table must not be overwritten")
    if expected_unsigned_size is not None and (
        not size
        or start != (expected_unsigned_size + 7) // 8 * 8
        or start + size != len(data)
        or any(data[expected_unsigned_size:start])
    ):
        raise ValueError(
            "Only an appended certificate table and zero alignment padding are allowed"
        )
    data[optional + 64 : optional + 68] = b"\0" * 4
    data[security : security + 8] = b"\0" * 8
    if size:
        del data[start : start + size]
    data.extend(b"\0" * (-len(data) % 8))
    return hashlib.sha256(data).hexdigest()


def reproducibility(first, root):
    second = manifest(root)
    passed = first["files"] == second["files"]
    return {
        "payload_bytes_reproduced": passed,
        "files": len(second["files"]),
        "msix_bytes_reproduced": False,
        "note": "Same pinned builder/commit/path/epoch; not independent build proof",
    }


def evaluate(root, policy, native, signatures, signtool, source_commit, policy_sha):
    root = Path(root).resolve()
    if not verify(root, read(root / "payload-manifest.json")):
        raise ValueError("Payload manifest invalid before signing evaluation")
    if policy.get("embedded_policy_required") is True:
        embedded = root / "native-signing-policy.json"
        if not embedded.is_file() or file_hash(embedded) != policy_sha:
            raise ValueError("Embedded native policy differs from the reviewed policy")
    rows = policy_records(policy)
    if not re.fullmatch(r"[a-f0-9]{40}", source_commit):
        raise ValueError("Expected exact source commit")
    actual = inventory([root], distributions=[])
    if not actual["inspection_complete"]:
        raise ValueError("Incomplete native inventory")
    if not native.get("inspection_complete"):
        raise ValueError("Incomplete input inventory")
    declared = {Path(f["path"]).resolve(): f for f in native["files"]}
    signed = {Path(f["path"]).resolve(): f for f in signatures["files"]}
    tools = {Path(f["path"]).resolve(): f for f in signtool["files"]}
    paths = {Path(f["path"]).resolve() for f in actual["files"]}
    if any(set(d) != paths for d in (declared, signed, tools)):
        raise ValueError("Inventory/signature coverage differs from actual native tree")
    matrix, violations, pending, seen = [], [], [], set()
    for file in actual["files"]:
        path = Path(file["path"]).resolve()
        relative = safe_relative(path.relative_to(root).as_posix())
        key = relative.casefold()
        if key in seen:
            raise ValueError("Duplicate native Windows path")
        seen.add(key)
        if file["format"] != "PE" or file["architecture"] != "x64":
            violations.append(relative + ": expected PE x64")
        if declared[path]["sha256"] != file["sha256"]:
            raise ValueError("Native input changed after inventory")
        sig, tool, entry = signed[path], tools[path], rows.get(key)
        if (
            not sig["integrity_matches"]
            or sig["sha256"] != file["sha256"]
            or not tool["integrity_matches"]
            or tool["sha256"] != file["sha256"]
        ):
            raise ValueError("Native bytes changed during trust verification")
        accepted = sig["status"] == "Valid" and tool["exit_code"] == 0
        if not accepted and sig["status"] != "NotSigned":
            violations.append(
                relative + ": existing signature failed/inconclusive; never overwrite"
            )
        action, authorization, blocker = "blocked", False, "New native path requires review"
        if entry:
            action = entry["action"]
            same = entry["baseline_sha256"] == file["sha256"]
            if action != "sign_own" and not same:
                violations.append(relative + ": third-party SHA differs from approved baseline")
            if action == "sign_own":
                own_entrypoint = (
                    "AgroLines.exe"
                    if policy.get("profile") == "standalone-offline"
                    else "AgroLinesPoC.exe"
                )
                if relative != own_entrypoint or file["packages"]:
                    violations.append(
                        relative + ": own exemption is restricted to the built entrypoint"
                    )
                authorization = (
                    entry["rights_confirmed"] is True
                    and entry["origin_confirmed"] is True
                    and bool(entry.get("rights_evidence"))
                )
                blocker = (
                    "Certificate/signing service not configured"
                    if authorization
                    else "Own rights pending"
                )
            elif action == "sign_third_party":
                authorization = (
                    entry["rights_confirmed"] is True
                    and bool(entry.get("rights_evidence"))
                    and entry["origin_confirmed"] is True
                    and same
                )
                blocker = (
                    "Certificate/signing service not configured"
                    if authorization
                    else "Third-party rights/origin pending"
                )
            elif action == "preserve_original":
                if not accepted or sig.get("signer") != entry["baseline_signer"]:
                    violations.append(relative + ": original trusted signature must be preserved")
                blocker = (
                    None
                    if entry["origin_confirmed"]
                    else "Origin dossier pending; preserve original"
                )
            else:
                blocker = entry.get("blocker", "Rights/signing authorization pending")
            if accepted and action in ("sign_own", "sign_third_party", "blocked"):
                # A new signed distribution needs an explicit hash/signer policy update.
                violations.append(relative + ": unexpected signature in pre-sign build")
        if blocker:
            pending.append({"path": relative, "reason": blocker})
        matrix.append(
            {
                "path": relative,
                "sha256": file["sha256"],
                "size_bytes": path.stat().st_size,
                "pe_content_sha256": (
                    pe_content_digest(path, require_unsigned=True)
                    if sig["status"] == "NotSigned"
                    else None
                ),
                "group": entry["group"] if entry else "unknown",
                "origin_confirmed": entry["origin_confirmed"] if entry else False,
                "action": action,
                "sign_authorized": authorization and sig["status"] == "NotSigned",
                "authenticode": sig["status"],
                "signtool_exit": tool["exit_code"],
                "generic_chain_flags": sig["chain_status"],
                "blocker": blocker,
            }
        )
    removed = sorted(set(rows) - seen)
    if removed:
        violations.append("Native removals require policy update/dependency regression evidence")
    unknown = sorted(seen - set(rows))
    if unknown:
        violations.append("New native files require exact provenance/rights policy review")
    ready = (
        not violations
        and not unknown
        and not removed
        and all(
            r["action"] == "preserve_original" and not r["blocker"] or r["sign_authorized"]
            for r in matrix
        )
    )
    technical_inputs_verified = (
        not violations
        and not unknown
        and not removed
        and all(r["origin_confirmed"] for r in matrix)
    )
    release_blockers = release_review_blockers(policy)
    return {
        "schema_version": 1,
        "source_commit": source_commit,
        "policy_sha256": policy_sha,
        "status": "ASSINATURA PENDENTE",
        "files": matrix,
        "before": dict(Counter(r["authenticode"] for r in matrix)),
        "after": dict(Counter(r["authenticode"] for r in matrix)),
        "signing_performed": False,
        "ready_for_authorized_signing": ready,
        "ready_for_store_homologation": (technical_inputs_verified and not release_blockers),
        "technical_inputs_verified": technical_inputs_verified,
        "release_review_blockers": release_blockers,
        "native_signature_gate_passed": False,
        "distribution_approved": False,
        "sac_approved": False,
        "violations": violations,
        "pending": pending,
        "new_paths": unknown,
        "removed_paths": removed,
    }


def transition(plan, root, after, tools, signer_subject, thumbprint):
    """Permit only exact approved PE changes; never treats current-time expiry as SAC failure."""
    root = Path(root).resolve()
    actual = inventory([root], distributions=[])
    if not actual["inspection_complete"]:
        raise ValueError("Post-sign inventory incomplete")
    by_path = {
        safe_relative(Path(f["path"]).relative_to(root).as_posix()): f for f in actual["files"]
    }
    expected = {r["path"]: r for r in plan["files"]}
    signatures = {Path(r["path"]).resolve(): r for r in after["files"]}
    verifiers = {Path(r["path"]).resolve(): r for r in tools["files"]}
    if (
        set(expected) != set(by_path)
        or set(signatures) != {root / p for p in expected}
        or set(verifiers) != set(signatures)
    ):
        raise ValueError("Post-sign file coverage differs")
    if not plan["ready_for_authorized_signing"] or plan["violations"]:
        raise ValueError("Signing was not authorized for this complete payload")
    for path, before in expected.items():
        sig, tool, native = signatures[root / path], verifiers[root / path], by_path[path]
        if (
            not sig["integrity_matches"]
            or not tool["integrity_matches"]
            or sig["sha256"] != native["sha256"]
            or tool["sha256"] != native["sha256"]
        ):
            raise ValueError("Post-sign bytes changed during verification")
        if sig["status"] != "Valid" or tool["exit_code"] != 0:
            raise ValueError("All PE require accepted Authenticode after signing")
        if before["sign_authorized"]:
            if (
                pe_content_digest(root / path, expected_unsigned_size=before["size_bytes"])
                != before["pe_content_sha256"]
            ):
                raise ValueError("PE content changed beyond signature fields/certificate table")
            if (
                sig["signer"] != signer_subject
                or sig["signer_thumbprint"].casefold() != thumbprint.casefold()
                or not sig["timestamp_signer"]
            ):
                raise ValueError("Authorized signature identity/timestamp mismatch")
        elif before["sha256"] != native["sha256"]:
            raise ValueError("Original vendor signature/bytes were changed")
    return {
        **plan,
        "status": "ASSINATURAS NATIVAS VERIFICADAS; SAC PENDENTE",
        "after": dict(Counter(r["status"] for r in after["files"])),
        "signing_performed": any(r["sign_authorized"] for r in plan["files"]),
        "native_signature_gate_passed": True,
    }


def bind(package, plan, source_commit, lock, policy):
    if plan["source_commit"] != source_commit or plan["policy_sha256"] != file_hash(policy):
        raise ValueError("Signing input does not match approved source/policy")
    return {
        "source_commit": source_commit,
        "package_file": Path(package).name,
        "size_bytes": Path(package).stat().st_size,
        "package_sha256": file_hash(package),
        "policy_sha256": file_hash(policy),
        "lock_sha256": file_hash(lock),
        "plan_sha256": hashlib.sha256(
            json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def prepare_packaging(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if (
        source == destination
        or source.is_relative_to(destination)
        or destination.is_relative_to(source)
    ):
        raise ValueError("Packaging stage must be separate")
    # Only SDK-generated envelope entries; never excludes payload or vendor signatures.
    excluded = {"AppxSignature.p7x", "AppxBlockMap.xml", "[Content_Types].xml"}
    shutil.copytree(
        source,
        destination,
        ignore=lambda folder, names: excluded & set(names) if Path(folder) == source else set(),
    )


def check_package(path, payload_manifest):
    import xml.etree.ElementTree as ET

    from distribution.msix import NS, identity, package_family_name

    expected = identity()
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(n.casefold() for n in names)):
            raise ValueError("Duplicate package names")
        tree = ET.fromstring(archive.read("AppxManifest.xml"))
        declared = tree.find("f:Identity", NS).attrib
        if (
            declared["Name"] != expected["name"]
            or declared["Publisher"] != expected["publisher"]
            or declared["ProcessorArchitecture"] != "x64"
            or package_family_name(declared["Name"], declared["Publisher"])
            != expected["package_family_name"]
        ):
            raise ValueError("Official Store identity changed")
        prefix = "VFS/ProgramFilesX64/AgroLines/"
        if json.loads(archive.read(prefix + "payload-manifest.json")) != payload_manifest:
            raise ValueError("MSIX manifest differs from signed payload manifest")
        for f in payload_manifest["files"]:
            import hashlib

            if (
                hashlib.sha256(archive.read(prefix + safe_relative(f["path"]))).hexdigest()
                != f["sha256"]
            ):
                raise ValueError("MSIX contains unexpected signed payload bytes")
        actual = {n[len(prefix) :] for n in names if n.startswith(prefix) and not n.endswith("/")}
        if actual - {"payload-manifest.json"} != {f["path"] for f in payload_manifest["files"]}:
            raise ValueError("MSIX payload file coverage differs")
    return {
        "package_sha256": file_hash(path),
        "identity": declared,
        "sac_approved": False,
        "distribution_approved": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "evaluate",
            "reproduce",
            "bind",
            "verify-input",
            "transition",
            "manifest",
            "stage",
            "package",
        ],
    )
    for name in (
        "root",
        "policy",
        "native",
        "signatures",
        "tools",
        "plan",
        "source-commit",
        "package",
        "lock",
        "first",
        "destination",
        "subject",
        "thumbprint",
        "output",
        "binding",
    ):
        parser.add_argument("--" + name)
    args = parser.parse_args()
    if args.command == "evaluate":
        data = evaluate(
            args.root,
            read(args.policy),
            read(args.native),
            read(args.signatures),
            read(args.tools),
            args.source_commit,
            file_hash(args.policy),
        )
    elif args.command == "reproduce":
        data = reproducibility(read(args.first), args.root)
        if not data["payload_bytes_reproduced"]:
            raise ValueError("Payload build not reproducible")
    elif args.command == "bind":
        data = bind(args.package, read(args.plan), args.source_commit, args.lock, args.policy)
    elif args.command == "verify-input":
        data = bind(args.package, read(args.plan), args.source_commit, args.lock, args.policy)
        if data != read(args.binding):
            raise ValueError("Artifact/source/policy/lock binding changed")
    elif args.command == "transition":
        data = transition(
            read(args.plan),
            args.root,
            read(args.signatures),
            read(args.tools),
            args.subject,
            args.thumbprint,
        )
    elif args.command == "manifest":
        data = manifest(args.root)
    elif args.command == "stage":
        prepare_packaging(args.root, args.destination)
        return
    else:
        data = check_package(args.package, read(args.first))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(data, indent=2), encoding="utf-8")
    if args.command == "evaluate":
        print(
            "AGROLINES_SIGNING_STATUS="
            + json.dumps(
                {
                    k: data[k]
                    for k in (
                        "status",
                        "before",
                        "after",
                        "signing_performed",
                        "ready_for_authorized_signing",
                        "violations",
                        "new_paths",
                        "removed_paths",
                    )
                }
            )
        )
        if data["violations"]:
            raise SystemExit(1)
    elif args.command in ("reproduce", "bind"):
        print("AGROLINES_SIGNING_" + args.command.upper() + "=" + json.dumps(data))


if __name__ == "__main__":
    main()
