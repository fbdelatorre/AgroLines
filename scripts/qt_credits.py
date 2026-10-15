"""Export exact Windows Qt WebEngine built-in credits; no MSIX installation or mutation."""

import argparse
import hashlib
import importlib.metadata
import json
import sys
import zipfile
from pathlib import Path

from scripts.compliance_capture import PREFIX, REFERENCE_SHA


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != "win32":
        raise SystemExit("Windows only; another platform's credits cannot stand for this MSIX")
    with args.package.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != REFERENCE_SHA:
            raise ValueError("Reference MSIX mismatch")
    rows = json.loads(args.native.read_text())["files"]
    checked = []
    with zipfile.ZipFile(args.package) as archive:
        for row in rows:
            if row["group"] != "qt":
                continue
            if hashlib.sha256(archive.read(PREFIX + row["path"])).hexdigest() != row["sha256"]:
                raise ValueError("Reference Qt metadata/hash mismatch")
            matching = []
            for owner in row["packages"]:
                package = importlib.metadata.distribution(owner["name"])
                file = Path(package.locate_file(owner["input_relative"]))
                if package.version != owner["version"]:
                    raise ValueError("Qt builder version differs from reference")
                if (
                    file.is_file()
                    and hashlib.sha256(file.read_bytes()).hexdigest() == row["sha256"]
                ):
                    matching.append(str(file))
            if not matching:
                raise ValueError("Builder Qt file differs from reference: " + row["path"])
            checked.append({"path": row["path"], "sha256": row["sha256"]})
    if len(checked) != 70:
        raise ValueError("Unexpected Qt reference coverage")
    # Import only after verifying all Qt/shiboken/Qt-wheel runtime file hashes.
    from PySide6.QtCore import QTimer, QUrl
    from PySide6.QtWebEngineCore import (
        QWebEnginePage,
        QWebEngineProfile,
        QWebEngineUrlRequestInterceptor,
        qWebEngineChromiumVersion,
        qWebEngineVersion,
    )
    from PySide6.QtWidgets import QApplication

    class LocalOnly(QWebEngineUrlRequestInterceptor):
        def interceptRequest(self, info):
            if info.requestUrl().scheme() not in ("chrome", "data", "qrc"):
                info.block(True)

    app = QApplication([])
    profile = QWebEngineProfile(app)
    interceptor = LocalOnly(profile)
    profile.setUrlRequestInterceptor(interceptor)
    profile.downloadRequested.connect(lambda request: request.cancel())
    page = QWebEnginePage(profile, app)
    outcome = {"ok": False, "error": "Timed out or built-in credits unavailable"}

    def save(html):
        if "license" not in html.lower() or len(html) < 5000:
            outcome["error"] = "Built-in credits not sufficiently populated"
            app.quit()
            return
        args.output.mkdir(parents=True, exist_ok=True)
        raw = html.encode("utf-8")
        (args.output / "chromium-credits.html").write_bytes(raw)
        report = {
            "reference_msix_sha256": REFERENCE_SHA,
            "qt_files_verified": checked,
            "qt_webengine": qWebEngineVersion(),
            "chromium": qWebEngineChromiumVersion(),
            "credits_sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "source": "Built-in chrome://credits from same-hash Windows wheel libraries",
            "scope": "Credits only; not complete source/build correspondence or patent clearance",
            "msix_installed": False,
            "sac_approved": False,
            "legal_compliance_approved": False,
        }
        (args.output / "credits-evidence.json").write_text(json.dumps(report, indent=2))
        print("AGROLINES_QT_CREDITS=" + json.dumps(report))
        # Bounded legal-text chunks allow reconstructing bytes without publishing application code.
        import base64

        for offset in range(0, len(raw), 8192):
            print(
                "AGROLINES_QT_CREDITS_CHUNK="
                + json.dumps(
                    {
                        "offset": offset,
                        "base64": base64.b64encode(raw[offset : offset + 8192]).decode(),
                    }
                )
            )
        outcome["ok"] = True
        app.quit()

    def loaded(ok):
        if not ok:
            outcome["error"] = "chrome://credits load failed"
            app.quit()
        else:
            QTimer.singleShot(1500, lambda: page.toHtml(save))

    page.loadFinished.connect(loaded)
    QTimer.singleShot(45000, app.quit)
    page.load(QUrl("chrome://credits/"))
    app.exec()
    page.deleteLater()
    if not outcome["ok"]:
        if outcome["error"] != "chrome://credits load failed":
            raise SystemExit(outcome["error"])
        # This Qt route is unsupported, not a source/notice completeness approval.
        # Hash/import/timeout failures remain technical errors above.
        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "reference_msix_sha256": REFERENCE_SHA,
            "qt_files_verified": checked,
            "qt_webengine": qWebEngineVersion(),
            "chromium": qWebEngineChromiumVersion(),
            "credits_available": False,
            "documentary_pending": [
                "Built-in chrome://credits is unavailable; obtain exact build attribution output"
            ],
            "source": "Exact-reference Windows Qt runtime probe",
            "msix_installed": False,
            "sac_approved": False,
            "legal_compliance_approved": False,
        }
        (args.output / "credits-evidence.json").write_text(json.dumps(report, indent=2))
        print("AGROLINES_QT_CREDITS_STATUS=" + json.dumps(report))


if __name__ == "__main__":
    main()
