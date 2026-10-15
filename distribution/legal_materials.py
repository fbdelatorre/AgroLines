"""Build-time legal materials only. No runtime approval, network or DRM."""

import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICIES = ROOT / "docs/legal/standalone"
DOSSIER = ROOT / "docs/compliance"
SUPPLEMENT = ROOT / "distribution/legal/supplemental"
DOCUMENTS = ("EULA.md", "politica-privacidade.md", "INSTRUCOES-LGPL.md", "LEIA-ME.md")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_file(root, relative):
    path = Path(root) / relative
    if (
        "\\" in relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
        or not path.resolve().is_relative_to(Path(root).resolve())
        or path.is_symlink()
        or not path.is_file()
    ):
        raise ValueError("Unsafe/missing legal material: " + relative)
    return path


def render_markdown(text):
    # Literal text: no remote assets, script, external font or legal paraphrasing.
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>AgroLines — minuta jurídica</title><style>"
        "body{margin:1.5rem auto;padding:0 1rem;max-width:75ch;color:#17251d;"
        "background:#fff;font:16px/1.6 system-ui,sans-serif}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}"
        "</style></head><body><pre>" + html.escape(text) + "</pre></body></html>\n"
    )


def render_policies():
    for name in DOCUMENTS:
        source = POLICIES / name
        text = source.read_text(encoding="utf-8")
        source.with_suffix(".txt").write_text(text, encoding="utf-8-sig")
        if name in ("EULA.md", "politica-privacidade.md"):
            source.with_suffix(".html").write_text(render_markdown(text), encoding="utf-8")


def _component_rows(payload, registry):
    """Bind all actual native files to the pre-existing audited origins."""
    native = {r["path"].casefold(): r for r in registry["files"]}
    selected, files = set(), []
    from distribution.libaec_build import SLOT
    from distribution.libaec_build import evidence as codec_evidence

    codec = codec_evidence(payload)
    for file in sorted(Path(payload).rglob("*")):
        if not file.is_file() or file.suffix.casefold() not in (".dll", ".pyd", ".exe"):
            continue
        relative = file.relative_to(payload).as_posix()
        if relative == SLOT:
            component = "libaec-SZIP"
        elif relative == "AgroLines.exe":
            component = "AgroLines-executable"
        else:
            row = native.get(relative.casefold())
            if not row or digest(file) != row["sha256"]:
                raise ValueError("Unregistered/changed distributed native component: " + relative)
            component = row["component"]
        selected.add(component)
        from scripts.signing_pipeline import pe_content_digest

        unsigned_size = None
        try:
            pe_content_digest(file, require_unsigned=True)
            unsigned_size = file.stat().st_size
        except ValueError as error:
            if "existing certificate" not in str(error):
                raise
        files.append(
            {
                "path": relative,
                "component": component,
                "build_sha256": digest(file),
                "pe_content_sha256": pe_content_digest(file),
                "unsigned_size": unsigned_size,
            }
        )
    if not files:
        raise ValueError("No actual native payload to associate with legal materials")
    # These are actually frozen Python/JS/data inputs, not builder dependencies.
    selected.update(("PyInstaller-embedded", "Leaflet", "attrs", "certifi", "defusedxml"))
    registry["components"].append(
        {
            "id": "libaec-SZIP",
            "version": codec["version"],
            "license_evidence": "BSD-2-Clause; source and aec objects incorporated in libsz",
            "notice_files": [],
        }
    )
    return selected, files


def prepare(payload):
    payload = Path(payload)
    target = payload / "legal"
    if target.exists():
        raise ValueError("Fresh legal output required")
    registry = json.loads((DOSSIER / "inventory.json").read_text())
    selected, natives = _component_rows(payload, registry)
    supplemental = json.loads((SUPPLEMENT / "materials.json").read_text())
    audited_hashes = {
        row["path"]: row["sha256"]
        for row in json.loads((DOSSIER / "documents.json").read_text())["files"]
    }
    target.mkdir()
    documents = []

    def copy(source, relative, origin, component):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if digest(destination) != digest(source):
                raise ValueError("Legal material collision")
            return
        shutil.copyfile(source, destination)
        documents.append(
            {
                "path": relative,
                "sha256": digest(destination),
                "size_bytes": destination.stat().st_size,
                "origin": origin,
                "component": component,
            }
        )

    for name in DOCUMENTS:
        for extension in (".md", ".txt"):
            safe_file(POLICIES, str(Path(name).with_suffix(extension)))
        for extension in (".md", ".txt", ".html"):
            source = POLICIES / Path(name).with_suffix(extension)
            if source.exists():
                copy(
                    source,
                    source.name,
                    "AgroLines preliminary legal draft; not adopted",
                    "AgroLines",
                )
    component_rows = []
    for component in registry["components"]:
        if component["id"] not in selected:
            continue
        copies = []
        for relative in component["notice_files"]:
            source = safe_file(DOSSIER, relative)
            if digest(source) != audited_hashes.get(relative):
                raise ValueError("Audited original license changed: " + relative)
            destination = "licenses/audited/" + relative.removeprefix("notices/")
            copy(source, destination, "Audited unchanged document " + relative, component["id"])
            copies.append(destination)
        for row in supplemental["materials"]:
            if component["id"] not in row["components"]:
                continue
            source = safe_file(SUPPLEMENT, row["file"])
            if source.suffix.casefold() in (
                ".dll",
                ".exe",
                ".pyd",
                ".obj",
                ".o",
                ".pyc",
                ".pyo",
                ".key",
                ".pem",
            ):
                raise ValueError("Executable, key or object is not a supplemental legal document")
            if digest(source) != row["sha256"]:
                raise ValueError("Official supplemental notice hash mismatch: " + row["file"])
            destination = "licenses/supplemental/" + row["file"]
            copy(source, destination, row["origin"], component["id"])
            copies.append(destination)
        component_rows.append(
            {
                "component": component["id"],
                "version": component["version"],
                "license_evidence": component["license_evidence"],
                "notices": copies,
                "scope_complete": False,
            }
        )
    if selected - {r["component"] for r in component_rows}:
        raise ValueError("Missing component in legal inventory")
    notice = [
        "AGROLINES — AVISOS DE TERCEIROS",
        "Materiais para revisão. Não constituem aprovação jurídica ou oferta completa de fontes.",
        "Os textos originais em licenses/ prevalecem sobre este índice em português.",
        "A licença proprietária proposta não reduz direitos das licenças de terceiros.",
        "Veja INSTRUCOES-LGPL.txt e fontes-terceiros.json para fontes e lacunas específicas.",
        "",
    ]
    for row in component_rows:
        notice.extend(
            [
                row["component"] + " — " + str(row["version"] or "versão ainda não comprovada"),
                row["license_evidence"],
                *("  Texto original: " + path for path in row["notices"]),
                "",
            ]
        )
    (target / "THIRD_PARTY_NOTICES.txt").write_text("\n".join(notice), encoding="utf-8")
    # Exact source pins and limitations, not generic homepages or an approved offer.
    copy(
        DOSSIER / "sources-index.json",
        "fontes-terceiros.json",
        "Existing pinned source index",
        "third-party-sources",
    )
    copy(
        SUPPLEMENT / "materials.json",
        "origens-suplementares.json",
        "Official material origin/hash records",
        "third-party-notices",
    )
    copy(
        payload / "libaec-provenance.json",
        "libaec-build.json",
        "Pinned official libaec source and local build recipe",
        "libaec-SZIP",
    )
    docs = {
        "schema_version": 1,
        "documents": documents,
        "notices_index_sha256": digest(target / "THIRD_PARTY_NOTICES.txt"),
        "components": component_rows,
        "native_files": natives,
        "distribution_approved": False,
        "legal_approved": False,
        "draft_fields_pending": True,
        "missing_upstream_materials": supplemental["remaining_materials"],
    }
    (target / "legal-manifest.json").write_text(
        json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verify(payload)
    return docs


def verify(payload):
    payload = Path(payload)
    root = payload / "legal"
    data = json.loads((root / "legal-manifest.json").read_text(encoding="utf-8"))
    if data.get("legal_approved") is not False or data.get("distribution_approved") is not False:
        raise ValueError("This draft material gate cannot grant legal or commercial approval")
    expected = {row["path"] for row in data["documents"]}
    if len(expected) != len(data["documents"]):
        raise ValueError("Duplicated legal document")
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    if actual != expected | {"legal-manifest.json", "THIRD_PARTY_NOTICES.txt"}:
        raise ValueError("Missing or unauthorized legal file")
    for row in data["documents"]:
        if digest(safe_file(root, row["path"])) != row["sha256"]:
            raise ValueError("Changed legal text: " + row["path"])
    if digest(root / "THIRD_PARTY_NOTICES.txt") != data["notices_index_sha256"]:
        raise ValueError("Changed third-party notices index")
    native_expected = {row["path"]: row for row in data["native_files"]}
    native_actual = {
        p.relative_to(payload).as_posix(): p
        for p in payload.rglob("*")
        if p.is_file() and p.suffix.casefold() in (".dll", ".exe", ".pyd")
    }
    if set(native_actual) != set(native_expected):
        raise ValueError("Actual payload no longer matches its legal component inventory")
    from scripts.signing_pipeline import pe_content_digest

    signature_only = []
    for relative, file in native_actual.items():
        row = native_expected[relative]
        if digest(file) == row["build_sha256"]:
            continue
        # Only allow appended Authenticode fields on originally unsigned PE.
        # This is content binding, never signature/trust approval: the independent
        # native signature gate must verify all real signatures after signing.
        if (
            row["unsigned_size"] is None
            or pe_content_digest(file, expected_unsigned_size=row["unsigned_size"])
            != row["pe_content_sha256"]
        ):
            raise ValueError("Changed native content beyond permitted signature fields")
        signature_only.append(relative)
    for component in data["components"]:
        if any(path not in expected for path in component["notices"]):
            raise ValueError("Missing component license reference")
    return {
        "legal_material_presence_verified": True,
        "documents": len(data["documents"]),
        "native_files": len(native_expected),
        "authenticode_content_only_files": signature_only,
        "cryptographic_trust_validated": False,
        "legal_approved": False,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("AGROLINES_LEGAL_MATERIALS=" + json.dumps(result))
