"""Material integrity checks must fail on drift without treating legal gaps as approvals."""

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from distribution.notices import collect, is_notice
from scripts import compliance_capture
from scripts.compliance_bundle import pack
from scripts.compliance_check import manifest, verify

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs/compliance"


@pytest.fixture
def dossier(tmp_path):
    result = tmp_path / "dossier"
    shutil.copytree(DOSSIER, result)
    return result


def alter(root, name, callback):
    path = root / name
    data = json.loads(path.read_text())
    callback(data)
    path.write_text(json.dumps(data))


def test_actual_reference_has_material_integrity_but_no_legal_approval():
    result = verify(DOSSIER)
    assert result["technical_failure"] == []
    assert result["documentary_pending"] and result["legal_pending"]
    assert result["contractual_pending"] and not result["distribution_approved"]


def test_unregistered_file_and_hash_drift_are_technical_failures(dossier):
    def mutate(data):
        data["files"][0]["sha256"] = "0" * 64
        data["files"].append(
            {"path": "unreviewed.dll", "sha256": "0" * 64, "component": "unregistered"}
        )

    alter(dossier, "inventory.json", mutate)
    errors = verify(dossier)["technical_failure"]
    assert any("Unexpected hash" in e for e in errors)
    assert any("unauthorized" in e for e in errors)
    assert any("Unregistered distributed dependency" in e for e in errors)


def test_owner_version_and_copyright_drift(dossier):
    def mutate(data):
        native = next(r for r in data["files"] if r.get("owner_packages"))
        native["owner_packages"][0]["version"] = "0.0-wrong"
        component = next(c for c in data["components"] if c["copyright_evidence"])
        component["copyright_evidence"][0]["excerpt"].append("INVENTED COPYRIGHT")

    alter(dossier, "inventory.json", mutate)
    errors = verify(dossier)["technical_failure"]
    assert any("Owner/version drift" in e for e in errors)
    assert any("Copyright absent" in e for e in errors)


def test_required_original_license_missing(dossier):
    notice = json.loads((dossier / "evidence/notices.json").read_text())[0]
    (dossier / "notices/reference" / notice["path"]).unlink()
    assert any("notice missing" in e for e in verify(dossier)["technical_failure"])


def test_forbidden_qt_dependency_is_not_cleared_by_new_document_hash(dossier):
    def mutate(data):
        data["files"][0]["path"] = "_internal/PySide6/Qt6Charts.dll"

    alter(dossier, "inventory.json", mutate)
    manifest(dossier)
    assert any("Forbidden Qt" in e for e in verify(dossier)["technical_failure"])


def test_changed_candidate_requires_separate_inventory(dossier, tmp_path):
    payload = json.loads((dossier / "evidence/payload.json").read_text())
    payload[0]["sha256"] = "0" * 64
    target = tmp_path / "new-payload.json"
    target.write_text(json.dumps({"files": payload}))
    assert any("Payload changed" in e for e in verify(dossier, target)["technical_failure"])


def test_document_and_unsafe_path_drift(dossier):
    (dossier / "qt-lgplv3.md").write_text("replaced without review")
    assert any("Document absent or changed" in e for e in verify(dossier)["technical_failure"])
    alter(
        dossier,
        "documents.json",
        lambda d: d["files"].append({"path": "../outside", "sha256": "0" * 64}),
    )
    with pytest.raises(ValueError, match="Unsafe"):
        verify(dossier)


def test_submission_cannot_be_approved_by_booleans(dossier):
    alter(
        dossier,
        "inventory.json",
        lambda d: d.update(distribution_approved=True, reviews={"legal": {"approved": True}}),
    )
    manifest(dossier)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.compliance_check", "--root", str(dossier), "--submission"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert '"legal_compliance_approved": false' in result.stdout


def test_notice_names_and_code_exclusion():
    for name in (
        "COPYING",
        "NOTICE",
        "AUTHORS",
        "COPYRIGHT",
        "LICENCE",
        "CONTRIBUTORS.md",
        "demo.dist-info/licenses/BSD-3-Clause.txt",
    ):
        assert is_notice(name)
    for name in ("license.py", "authors.pyc", "license.dll", "src/notice/logging.py", "data.dat"):
        assert not is_notice(name)


def test_collector_uses_payload_or_frozen_modules_and_preserves_originals(tmp_path):
    payload, installed = tmp_path / "payload", tmp_path / "site"
    (payload / "_internal/native").mkdir(parents=True)
    (payload / "_internal/native/lib.dll").write_bytes(b"synthetic native input")
    installed.mkdir()
    packages = []
    for name, files in [
        ("native", ["native/lib.dll", "native/AUTHORS", "native/COPYING"]),
        ("pure", ["pure/__init__.py", "pure/NOTICE"]),
        ("builder-only", ["builder/__init__.py", "builder/LICENSE"]),
    ]:
        for name_file in files:
            path = installed / name_file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Original copyright; no translation\r\n")
        packages.append(
            SimpleNamespace(
                metadata={"Name": name, "License": "synthetic test"},
                version="1.0",
                files=files,
                locate_file=lambda f: installed / f,
            )
        )
    rows = collect(payload, ["pure"], packages)
    assert {r["name"] for r in rows} == {"native", "pure"}
    notices = json.loads((payload / "third-party-notices/collected-notices.json").read_text())
    assert len(notices["documents"]) == 3
    for doc in notices["documents"]:
        raw = (payload / "third-party-notices" / doc["path"]).read_bytes()
        assert raw.endswith(b"\r\n")
        assert hashlib.sha256(raw).hexdigest() == doc["sha256"]
    with pytest.raises(ValueError, match="fresh"):
        collect(payload, ["pure"], packages)


def test_bundle_only_explicit_third_party_archives_and_notices(tmp_path):
    dossier, sources = tmp_path / "dossier", tmp_path / "sources"
    (dossier / "notices").mkdir(parents=True)
    sources.mkdir()
    raw = b"synthetic upstream archive fixture"
    (sources / "upstream.tar").write_bytes(raw)
    (sources / "AgroLines-secret.py").write_text("must never be copied")
    index = {"sources": [{"filename": "upstream.tar", "sha256": hashlib.sha256(raw).hexdigest()}]}
    (dossier / "sources-index.json").write_text(json.dumps(index))
    (dossier / "notices/LICENSE").write_text("synthetic license")
    (dossier / "documents.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "notices/LICENSE",
                        "sha256": hashlib.sha256(b"synthetic license").hexdigest(),
                    }
                ]
            }
        )
    )
    archive = tmp_path / "sources.zip"
    result = pack(dossier, sources, archive)
    assert not result["published"] and not result["complete_corresponding_source"]
    with zipfile.ZipFile(archive) as packed:
        assert set(packed.namelist()) == {
            "sources/upstream.tar",
            "notices/LICENSE",
            "sources-index.json",
            "README.txt",
        }
    (sources / "upstream.tar").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        pack(dossier, sources, tmp_path / "bad.zip")


def test_capture_refuses_other_msix_without_execution(tmp_path):
    package = tmp_path / "other.msix"
    package.write_bytes(b"another candidate")
    with pytest.raises(ValueError, match="reference MSIX mismatch"):
        compliance_capture.capture(package, tmp_path, tmp_path / "output")


def test_missing_binary_provenance_cannot_be_cleared_by_document_refresh(dossier):
    alter(
        dossier,
        "evidence/native.json",
        lambda rows: rows[0].update(pinned_origin_confirmed=False, exact_build_source_match=False),
    )
    manifest(dossier)
    errors = verify(dossier)["technical_failure"]
    assert any("without verified provenance" in error for error in errors)
    assert any("input hash not established" in error for error in errors)


def test_source_bundle_rejects_unreviewed_material_in_notices(tmp_path):
    dossier, sources = tmp_path / "dossier", tmp_path / "sources"
    (dossier / "notices").mkdir(parents=True)
    sources.mkdir()
    (dossier / "sources-index.json").write_text(json.dumps({"sources": []}))
    (dossier / "documents.json").write_text(json.dumps({"files": []}))
    (dossier / "notices/AgroLines-private.py").write_text("must not enter any archive")
    with pytest.raises(ValueError, match="Unreviewed"):
        pack(dossier, sources, tmp_path / "must-not-exist.zip")
    assert not (tmp_path / "must-not-exist.zip").exists()
