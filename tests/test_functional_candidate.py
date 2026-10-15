"""Trust segregation, privacy of local logs and measured artifact identity."""

import json
import logging
import sys

import pytest
from nacl.signing import SigningKey

from core.license_protocol import encode
from desktop.diagnostics import initialize, record_failure
from distribution.commercial_profile import prepare_trust
from distribution.functional_report import report


def test_production_build_rejects_reserved_synthetic_trust_even_on_real_https_origin(tmp_path):
    keyfile = tmp_path / "public.json"
    keyfile.write_text(
        json.dumps({"synthetic-lab-only": encode(bytes(SigningKey.generate().verify_key))})
    )
    with pytest.raises(ValueError, match="Synthetic licensing trust"):
        prepare_trust(tmp_path / "production.py", "https://licensing.example.com", keyfile)
    assert not (tmp_path / "production.py").exists()
    prepare_trust(tmp_path / "test.py", "https://licenses.example.test", keyfile, experimental=True)
    assert "TEST_PROFILE = True" in (tmp_path / "test.py").read_text()


def test_local_diagnostics_do_not_log_exception_secrets_or_project_paths(tmp_path):
    logger = logging.getLogger("agrolines.desktop")
    original = logger.handlers[:]
    logger.handlers = []
    try:
        logger = initialize(tmp_path)
        try:
            raise ValueError("SECRET-KEY-DO-NOT-LOG C:/ClientName/PrivateProject.agrolines")
        except ValueError:
            record_failure(logger, *sys.exc_info())
        for handler in logger.handlers:
            handler.flush()
        text = (tmp_path / "desktop.log").read_text()
        assert "ValueError" in text
        assert "SECRET-KEY-DO-NOT-LOG" not in text and "PrivateProject" not in text
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.handlers = original


def test_artifact_report_measures_bytes_and_counts_without_approval(tmp_path):
    payload = tmp_path / "onedir"
    payload.mkdir()
    for name in ("AgroLines.exe", "Qt.dll", "native.pyd", "payload-manifest.json"):
        (payload / name).write_bytes(b"inert measurement fixture")
    setup = tmp_path / "AgroLines-Setup-1.0.0.5-TESTE-x64.exe"
    setup.write_bytes(b"not an executable")
    first = report(payload, setup, "synthetic-source")
    assert first["dll_count"] == first["pyd_count"] == first["exe_count"] == 1
    assert first["onedir_bytes"] == 4 * len(b"inert measurement fixture")
    assert not first["signed"] and not first["sac_approved"]
    setup.write_bytes(b"changed inert fixture")
    assert (
        first["installer_sha256"] != report(payload, setup, "synthetic-source")["installer_sha256"]
    )
