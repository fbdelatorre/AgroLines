"""Local delivery is hash-bound and never sweeps the maintainer's files."""

import hashlib
import json
import zipfile

import pytest

from distribution.source_bundle import create, obtain, stage


def source(tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    archive = cache / "third-party-upstream.tar.gz"
    archive.write_bytes(b"inert synthetic upstream archive, not an application")
    (cache / "private-app.py").write_text("never include this file")
    row = {
        "filename": archive.name,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "component": "synthetic-third-party",
        "version": "test",
    }
    return cache, {"sources": [row], "remaining": ["fixture"], "notice": "Not a real source offer"}


def test_local_delivery_has_exact_inputs_and_survives_copy_to_payload(tmp_path):
    cache, lock = source(tmp_path)
    output = tmp_path / "third-party-sources.zip"
    result = create(cache, output, lock)
    assert not result["own_application_source_included"]
    assert not result["complete_corresponding_source_offer"]
    with zipfile.ZipFile(output) as package:
        assert not any("private-app" in p for p in package.namelist())
        assert package.read(result["sources"][0]["archive_path"]).startswith(b"inert")
    payload = tmp_path / "payload"
    payload.mkdir()
    staged = stage(payload, output)
    assert (payload / staged["payload_file"]).is_file()
    assert staged["sha256"] == result["sha256"]


def test_source_corruption_and_unapproved_cache_files_do_not_pass(tmp_path):
    cache, lock = source(tmp_path)
    (cache / lock["sources"][0]["filename"]).write_bytes(b"changed upstream")
    with pytest.raises(ValueError, match="hash differs"):
        create(cache, tmp_path / "delivery.zip", lock)


def test_bundle_mutation_is_detected_before_staging(tmp_path):
    cache, lock = source(tmp_path)
    output = tmp_path / "delivery.zip"
    create(cache, output, lock)
    with output.open("ab") as stream:
        stream.write(b"unexpected data")
    with pytest.raises(ValueError, match="Invalid"):
        stage(tmp_path / "payload", output)


def test_source_path_escape_and_unencrypted_transport_are_refused(tmp_path):
    with pytest.raises(ValueError, match="named upstream"):
        obtain({"filename": "../application.tar.gz"}, tmp_path)
    with pytest.raises(ValueError, match="HTTPS"):
        obtain({"filename": "source.tar.gz", "url": "http://example.invalid/source"}, tmp_path)


def test_source_offer_is_never_promoted_by_a_local_manifest(tmp_path):
    cache, lock = source(tmp_path)
    output = tmp_path / "delivery.zip"
    result = create(cache, output, lock)
    sidecar = json.loads(output.with_suffix(".json").read_text())
    assert result["legal_approved"] is False and sidecar["distribution_approved"] is False
