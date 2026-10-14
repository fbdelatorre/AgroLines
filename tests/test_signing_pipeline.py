"""Synthetic policy regression; no real signature/certificate or trust claim is created."""

import copy
import json
import struct
from pathlib import Path

import pytest

from distribution.payload import manifest
from scripts.native_inventory import file_hash, inventory
from scripts.signing_pipeline import (
    bind,
    evaluate,
    pe_content_digest,
    policy_records,
    reproducibility,
    safe_relative,
    transition,
)

COMMIT = "a" * 40


def pe(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = bytearray(513)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 64)
    data[64:68] = b"PE\0\0"
    struct.pack_into("<H", data, 68, 0x8664)
    struct.pack_into("<H", data, 88, 0x20B)
    path.write_bytes(data)


@pytest.fixture
def specimen(tmp_path):
    root = tmp_path / "payload"
    pe(root / "AgroLinesPoC.exe")
    pe(root / "_internal/vendor.dll")
    (root / "payload-manifest.json").write_text(json.dumps(manifest(root)))
    native = inventory([root], [])
    signatures, tools, rules = [], [], []
    for row in native["files"]:
        own = Path(row["path"]).name == "AgroLinesPoC.exe"
        signatures.append(
            dict(
                path=row["path"],
                sha256=row["sha256"],
                status="NotSigned" if own else "Valid",
                integrity_matches=True,
                signer=None if own else "vendor",
                chain_status=["NotTimeValid"],
            )
        )
        tools.append(
            dict(
                path=row["path"],
                sha256=row["sha256"],
                exit_code=1 if own else 0,
                integrity_matches=True,
            )
        )
        rules.append(
            dict(
                path=Path(row["path"]).relative_to(root).as_posix(),
                group="own" if own else "other",
                baseline_sha256=row["sha256"],
                baseline_signer=None if own else "vendor",
                action="sign_own" if own else "preserve_original",
                rights_confirmed=own,
                origin_confirmed=True,
                rights_evidence="owner instruction" if own else None,
            )
        )
    return (
        root,
        {"schema_version": 1, "files": rules},
        native,
        {"files": signatures},
        {"files": tools},
    )


def run(specimen):
    return evaluate(*specimen, COMMIT, "b" * 64)


def test_valid_timestamp_policy_does_not_reject_generic_expiry(specimen):
    result = run(specimen)
    assert result["ready_for_authorized_signing"]
    assert result["before"] == result["after"] == {"NotSigned": 1, "Valid": 1}
    assert result["status"] == "ASSINATURA PENDENTE"
    assert not result["signing_performed"] and not result["native_signature_gate_passed"]
    assert not result["sac_approved"] and not result["distribution_approved"]


@pytest.mark.parametrize(
    "field,value",
    [("origin_confirmed", False), ("rights_confirmed", False), ("rights_evidence", None)],
)
def test_unsigned_third_party_needs_independent_rights_and_origin(specimen, field, value):
    root, policy, native, sig, tools = specimen
    vendor = next(f for f in policy["files"] if f["action"] == "preserve_original")
    vendor.update(
        action="sign_third_party",
        rights_confirmed=True,
        origin_confirmed=True,
        rights_evidence="reviewed record",
    )
    vendor[field] = value
    for f in sig["files"]:
        if f["signer"] == "vendor":
            f.update(status="NotSigned", signer=None)
    for t in tools["files"]:
        t["exit_code"] = 1
    result = evaluate(root, policy, native, sig, tools, COMMIT, "b" * 64)
    assert not result["ready_for_authorized_signing"]


def test_new_native_path_and_removal_block_signing(specimen):
    root, policy, native, sig, tools = specimen
    policy["files"][1]["path"] = "removed.dll"
    result = evaluate(root, policy, native, sig, tools, COMMIT, "b" * 64)
    assert result["new_paths"] and result["removed_paths"] and result["violations"]
    assert not result["ready_for_authorized_signing"]


def test_third_party_hash_drift_blocks_even_if_signature_is_valid(specimen):
    next(r for r in specimen[1]["files"] if r["action"] == "preserve_original")[
        "baseline_sha256"
    ] = "f" * 64
    result = run(specimen)
    assert result["violations"] and not result["ready_for_authorized_signing"]


def test_incomplete_signature_coverage_is_not_approval(specimen):
    specimen[3]["files"].pop()
    with pytest.raises(ValueError, match="coverage"):
        run(specimen)


@pytest.mark.parametrize(
    "path", ["../a.dll", "/a.dll", "C:/a.dll", "a\\b.dll", "a/../b.dll", "a//b.dll", "a./b.dll"]
)
def test_path_traversal_aliases_rejected(path):
    with pytest.raises(ValueError):
        safe_relative(path)


def test_duplicate_windows_paths_rejected(specimen):
    policy = specimen[1]
    duplicate = dict(policy["files"][0])
    duplicate["path"] = duplicate["path"].upper()
    policy["files"].append(duplicate)
    with pytest.raises(ValueError, match="Duplicate"):
        policy_records(policy)


def test_mutated_input_manifest_or_signature_hash_fails(specimen):
    (specimen[0] / "AgroLinesPoC.exe").write_bytes(b"changed")
    with pytest.raises(ValueError, match="manifest"):
        run(specimen)


def test_image_content_mutation_guard_excludes_only_signature_fields(tmp_path):
    path = tmp_path / "synthetic.exe"
    pe(path)
    before = pe_content_digest(path)
    raw = bytearray(path.read_bytes())
    raw.extend(b"\0" * (-len(raw) % 8))
    certificate = len(raw)
    raw.extend(b"TESTCERTNOTVALID")
    struct.pack_into("<II", raw, 88 + 112 + 32, certificate, 16)
    raw[88 + 64 : 88 + 68] = b"ABCD"
    path.write_bytes(raw)
    assert pe_content_digest(path, expected_unsigned_size=513) == before
    raw[400] = 1
    path.write_bytes(raw)
    assert pe_content_digest(path) != before


def test_reproducibility_checks_actual_payload_bytes(specimen):
    root = specimen[0]
    first = manifest(root)
    assert reproducibility(first, root)["payload_bytes_reproduced"]
    (root / "extra.txt").write_text("drift")
    assert not reproducibility(first, root)["payload_bytes_reproduced"]


def test_binding_enforces_source_and_policy(specimen, tmp_path):
    plan = run(specimen)
    path = tmp_path / "policy.json"
    path.write_text("policy")
    plan["policy_sha256"] = file_hash(path)
    package = tmp_path / "input.msix"
    package.write_bytes(b"synthetic, not MSIX")
    record = bind(package, plan, COMMIT, path, path)
    assert record["package_sha256"] == file_hash(package) and record["plan_sha256"]
    with pytest.raises(ValueError, match="source/policy"):
        bind(package, plan, "f" * 40, path, path)


def test_original_vendor_bytes_cannot_change_after_signing(specimen):
    plan = run(specimen)
    root = specimen[0]
    signatures = copy.deepcopy(specimen[3])
    tools = copy.deepcopy(specimen[4])
    for sig in signatures["files"]:
        sig.update(
            status="Valid",
            signer="our-subject",
            signer_thumbprint="c" * 40,
            timestamp_signer="timestamp",
        )
    for tool in tools["files"]:
        tool["exit_code"] = 0
    # Byte-layout fixture only: this is not an X509 certificate or valid signature.
    own = root / "AgroLinesPoC.exe"
    own_data = bytearray(own.read_bytes())
    own_data.extend(b"\0" * (-len(own_data) % 8))
    offset = len(own_data)
    own_data.extend(b"TESTCERTNOTVALID")
    struct.pack_into("<II", own_data, 88 + 112 + 32, offset, 16)
    own.write_bytes(own_data)
    vendor = root / "_internal/vendor.dll"
    data = bytearray(vendor.read_bytes())
    data[400] = 1
    vendor.write_bytes(data)
    for rows in (signatures["files"], tools["files"]):
        for row in rows:
            row["sha256"] = file_hash(row["path"])
    with pytest.raises(ValueError, match="vendor"):
        transition(plan, root, signatures, tools, "our-subject", "c" * 40)
