"""Material integrity/adversarial controls; no legal approval or native execution."""

import json
import shutil
import struct

import pytest

from distribution import legal_materials as legal
from distribution.libaec_build import SLOT, SOURCE_COMMIT, SOURCE_SHA256, VERSION


def inert_pe(label):
    data = bytearray(1024)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 128)
    data[128:132] = b"PE\0\0"
    struct.pack_into("<H", data, 152, 0x20B)
    data[512 : 512 + len(label)] = label
    return data


@pytest.fixture
def material_payload(tmp_path, monkeypatch):
    dossier = tmp_path / "dossier"
    (dossier / "notices").mkdir(parents=True)
    original = dossier / "notices/LICENSE.txt"
    original.write_text("INERT UNIT FIXTURE license; not a real legal grant")
    ids = [
        "AgroLines-executable",
        "CPython",
        "PyInstaller-embedded",
        "Leaflet",
        "attrs",
        "certifi",
        "defusedxml",
        "Fiona-data",
        "Fiona-bindings",
        "proj-Fiona",
    ]
    payload = tmp_path / "payload"
    payload.mkdir()
    codec = payload / SLOT
    codec.parent.mkdir(parents=True)
    codec.write_bytes(inert_pe(b"codec fixture"))
    (payload / "AgroLines.exe").write_bytes(inert_pe(b"app fixture"))
    (payload / "libaec-provenance.json").write_text(
        json.dumps(
            {
                "source_commit": SOURCE_COMMIT,
                "source_archive_sha256": SOURCE_SHA256,
                "version": VERSION,
                "source_algorithm_modified": False,
                "ctest_passed": True,
                "binary_sha256": legal.digest(codec),
            }
        )
    )
    registry = {
        "files": [],
        "components": [
            {
                "id": n,
                "version": "fixture",
                "license_evidence": "fixture only",
                "notice_files": ["notices/LICENSE.txt"],
            }
            for n in ids
        ],
    }
    (dossier / "inventory.json").write_text(json.dumps(registry))
    (dossier / "documents.json").write_text(
        json.dumps({"files": [{"path": "notices/LICENSE.txt", "sha256": legal.digest(original)}]})
    )
    (dossier / "sources-index.json").write_text('{"source_offer_complete":false}')
    supplement = tmp_path / "supplement"
    supplement.mkdir()
    (supplement / "LICENSE.txt").write_text("Supplemental INERT fixture")
    (supplement / "materials.json").write_text(
        json.dumps(
            {
                "materials": [
                    {
                        "file": "LICENSE.txt",
                        "components": ["libaec-SZIP"],
                        "sha256": legal.digest(supplement / "LICENSE.txt"),
                        "origin": "inert fixture",
                    }
                ],
                "remaining_materials": ["Legal review is not automated"],
            }
        )
    )
    policies = tmp_path / "policies"
    shutil.copytree(legal.POLICIES, policies)
    monkeypatch.setattr(legal, "DOSSIER", dossier)
    monkeypatch.setattr(legal, "SUPPLEMENT", supplement)
    monkeypatch.setattr(legal, "POLICIES", policies)
    return payload


def test_actual_material_set_is_bound_and_never_grants_approval(material_payload):
    manifest = legal.prepare(material_payload)
    assert manifest["legal_approved"] is False and manifest["draft_fields_pending"]
    report = legal.verify(material_payload)
    assert (
        report["legal_material_presence_verified"] and not report["cryptographic_trust_validated"]
    )
    assert report["native_files"] == 2
    assert any(r["component"] == "libaec-SZIP" for r in manifest["components"])
    assert not any(r["component"] == "szip-Fiona" for r in manifest["components"])


@pytest.mark.parametrize(
    "mutation", ["missing", "changed", "new-file", "approve", "native-change", "new-native"]
)
def test_material_and_native_drift_cannot_pass(material_payload, mutation):
    legal.prepare(material_payload)
    root = material_payload / "legal"
    if mutation == "missing":
        (root / "EULA.txt").unlink()
    elif mutation == "changed":
        (root / "EULA.txt").write_text("substituted terms")
    elif mutation == "new-file":
        (root / "unreviewed.txt").write_text("not authorized")
    elif mutation == "native-change":
        (material_payload / "AgroLines.exe").write_bytes(inert_pe(b"altered application"))
    elif mutation == "new-native":
        (material_payload / "unexpected.dll").write_bytes(inert_pe(b"new dependency"))
    else:
        p = root / "legal-manifest.json"
        data = json.loads(p.read_text())
        data["legal_approved"] = True
        p.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        legal.verify(material_payload)


def test_source_notice_hash_cannot_be_bypassed(material_payload):
    (legal.SUPPLEMENT / "LICENSE.txt").write_text("changed upstream notice")
    with pytest.raises(ValueError, match="notice hash mismatch"):
        legal.prepare(material_payload)


def test_unknown_dependency_is_rejected_before_legal_material_assembly(material_payload):
    (material_payload / "unregistered.dll").write_bytes(inert_pe(b"unknown"))
    with pytest.raises(ValueError, match="Unregistered"):
        legal.prepare(material_payload)


def test_signature_region_is_distinct_from_content_and_never_approves_trust(material_payload):
    legal.prepare(material_payload)
    path = material_payload / "AgroLines.exe"
    data = bytearray(path.read_bytes())
    struct.pack_into("<II", data, 152 + 112 + 32, len(data), 8)
    data.extend(b"FAKECERT")  # Never loaded; content binding is not crypto approval.
    path.write_bytes(data)
    result = legal.verify(material_payload)
    assert result["authenticode_content_only_files"] == ["AgroLines.exe"]
    assert result["cryptographic_trust_validated"] is False
    assert result["legal_approved"] is False


@pytest.mark.parametrize("extension", [".txt", ".html"])
def test_stale_legal_representations_are_rejected(material_payload, extension):
    (legal.POLICIES / ("EULA" + extension)).write_text("previous contract text")
    with pytest.raises(ValueError, match="Stale"):
        legal.prepare(material_payload)


@pytest.mark.parametrize("mutation", ["changed", "new"])
def test_real_data_resources_are_bound_even_without_native_changes(material_payload, mutation):
    resource = material_payload / "_internal/fiona/proj_data/proj.db"
    resource.parent.mkdir(parents=True)
    resource.write_bytes(b"inert database fixture, never opened")
    path = legal.DOSSIER / "inventory.json"
    data = json.loads(path.read_text())
    data["files"].append(
        {
            "path": resource.relative_to(material_payload).as_posix(),
            "sha256": legal.digest(resource),
            "component": "Fiona-data",
        }
    )
    path.write_text(json.dumps(data))
    manifest = legal.prepare(material_payload)
    assert any(
        row["component"] == "Fiona-data" and row["notices"] for row in manifest["components"]
    )
    assert legal.verify(material_payload)["resource_files"] == 1
    if mutation == "changed":
        resource.write_bytes(b"different geodetic data")
    else:
        (resource.parent / "unreviewed-grid.gtx").write_bytes(b"new grid")
    with pytest.raises(ValueError, match="resource"):
        legal.verify(material_payload)
