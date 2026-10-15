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
RESOURCE_ROOTS = (
    "_internal/fiona/",
    "_internal/pyproj/",
    "_internal/PySide6/resources/",
    "_internal/PySide6/translations/",
    "_internal/desktop/map_assets/",
    "_internal/certifi/",
)
RESOURCE_NOTICES = {
    "Fiona-data": ("Fiona-bindings", "proj-Fiona"),
    "PROJ-data": ("pyproj-bindings",),
    "Qt-resources": ("Qt-Base", "Qt-WebEngine"),
}


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


def render_policies(folder=None):
    folder = folder or POLICIES
    for name in DOCUMENTS:
        source = folder / name
        text = source.read_text(encoding="utf-8")
        source.with_suffix(".txt").write_text(text, encoding="utf-8-sig")
        if name in ("EULA.md", "politica-privacidade.md"):
            source.with_suffix(".html").write_text(render_markdown(text), encoding="utf-8")


def verify_policy_copies(folder=None):
    folder = folder or POLICIES
    for name in DOCUMENTS:
        source = safe_file(folder, name)
        text = source.read_text(encoding="utf-8")
        if source.with_suffix(".txt").read_bytes() != b"\xef\xbb\xbf" + text.encode():
            raise ValueError("Stale plain-text legal draft: " + name)
        if name in ("EULA.md", "politica-privacidade.md"):
            if source.with_suffix(".html").read_bytes() != render_markdown(text).encode():
                raise ValueError("Stale HTML legal draft: " + name)


def resource_files(payload):
    return {
        p.relative_to(payload).as_posix(): p
        for p in Path(payload).rglob("*")
        if p.is_file()
        and p.suffix.casefold() not in (".dll", ".pyd", ".exe")
        and p.relative_to(payload).as_posix().startswith(RESOURCE_ROOTS)
    }


def _resource_rows(payload, registry):
    audited = {row["path"]: row for row in registry["files"]}
    selected, rows = set(), []
    for relative, path in resource_files(payload).items():
        original = audited.get(relative)
        if original is None or digest(path) != original["sha256"]:
            raise ValueError("Unregistered/changed third-party resource: " + relative)
        selected.add(original["component"])
        rows.append({"path": relative, "component": original["component"], "sha256": digest(path)})
    return selected, rows


def _component_rows(payload, registry):
    """Bind all actual native files to the pre-existing audited origins."""
    native = {r["path"].casefold(): r for r in registry["files"]}
    selected, files = set(), []
    from distribution.libaec_build import SLOT
    from distribution.libaec_build import evidence as codec_evidence

    codec = codec_evidence(payload)
    from distribution.geos_delivery import evidence as geos_evidence

    geos = geos_evidence(payload)
    from distribution.license_dependencies import additions

    extra_natives, extra_components = additions(payload)
    registry["components"].extend(extra_components)
    for file in sorted(Path(payload).rglob("*")):
        if not file.is_file() or file.suffix.casefold() not in (".dll", ".pyd", ".exe"):
            continue
        relative = file.relative_to(payload).as_posix()
        if relative == SLOT:
            component = "libaec-SZIP"
        elif relative in geos:
            component = geos[relative]["component"]
        elif relative in extra_natives:
            component = extra_natives[relative]["component"]
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
    collected = Path(payload) / "third-party-notices/packages.json"
    if extra_components and collected.exists():
        packages = json.loads(collected.read_text())
        for item in extra_components:
            actual = next((p for p in packages if p["name"].lower() == item["id"].lower()), None)
            if actual:
                if actual["version"] != item["version"]:
                    raise ValueError("Commercial Python dependency version differs")
                selected.add(item["id"])

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
    resource_components, resources = _resource_rows(payload, registry)
    selected.update(resource_components)
    components_by_id = {row["id"]: row for row in registry["components"]}
    for resource, owners in RESOURCE_NOTICES.items():
        if resource in selected:
            components_by_id[resource]["notice_files"] = sorted(
                {notice for owner in owners for notice in components_by_id[owner]["notice_files"]}
            )
    supplemental = json.loads((SUPPLEMENT / "materials.json").read_text())
    choices = json.loads((ROOT / "distribution/legal/license-choices.json").read_text())
    audited_hashes = {
        row["path"]: row["sha256"]
        for row in json.loads((DOSSIER / "documents.json").read_text())["files"]
    }
    target.mkdir()
    documents = []
    commercial = any(row["id"] == "PyNaCl" for row in registry["components"])
    policies = ROOT / "docs/legal/commercial" if commercial else POLICIES
    verify_policy_copies(policies)

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
            safe_file(policies, str(Path(name).with_suffix(extension)))
        for extension in (".md", ".txt", ".html"):
            source = policies / Path(name).with_suffix(extension)
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
        if component.get("wheel_origin"):
            from distribution.license_dependencies import MATERIALS

            for item in component["wheel_origin"]["notices"]:
                destination = "licenses/commercial/" + item["file"]
                copy(
                    safe_file(MATERIALS, item["file"]),
                    destination,
                    component["wheel_origin"]["url"] + "#" + item["wheel_file"],
                    component["id"],
                )
                copies.append(destination)
        component_rows.append(
            {
                "component": component["id"],
                "version": component["version"],
                "license_evidence": choices.get(component["id"], {}).get(
                    "selected", component["license_evidence"]
                ),
                "license_choice_scope": choices.get(component["id"]),
                "notices": copies,
                "scope_complete": False,
                "wheel_origin": component.get("wheel_origin"),
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
    if any(row["component"].startswith("jpeg62-") for row in component_rows):
        notice.extend(
            [
                "Reconhecimento exigido pelas bibliotecas IJG/libjpeg-turbo utilizadas:",
                "This software is based in part on the work of the Independent JPEG Group.",
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
        ROOT / "distribution/legal/license-choices.json",
        "alternativas-adotadas.json",
        "Documented license elections, covered files only",
        "third-party-notices",
    )
    copy(
        payload / "libaec-provenance.json",
        "libaec-build.json",
        "Pinned official libaec source and local build recipe",
        "libaec-SZIP",
    )
    source_delivery = None
    delivery = payload / "third-party-sources/delivery.json"
    if delivery.is_file():
        source_delivery = json.loads(delivery.read_text())
        if digest(payload / source_delivery["payload_file"]) != source_delivery["sha256"]:
            raise ValueError("Source delivery differs from its manifest")
        copy(delivery, "fontes-disponibilizadas.json", "Version-local source delivery", "sources")
    if (payload / "geos-source-builds.json").is_file():
        copy(
            payload / "geos-source-builds.json",
            "geos-fontes-build.json",
            "Same-version builds with unmodified algorithm inputs",
            "GEOS",
        )
    docs = {
        "schema_version": 1,
        "documents": documents,
        "notices_index_sha256": digest(target / "THIRD_PARTY_NOTICES.txt"),
        "components": component_rows,
        "native_files": natives,
        "resource_files": resources,
        "source_delivery": source_delivery,
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
    resources = {row["path"]: row for row in data["resource_files"]}
    actual_resources = resource_files(payload)
    if set(resources) != set(actual_resources):
        raise ValueError("Third-party resource set changed")
    for relative, path in actual_resources.items():
        if digest(path) != resources[relative]["sha256"]:
            raise ValueError("Third-party resource content changed: " + relative)
    if data.get("source_delivery"):
        delivery = data["source_delivery"]
        source = safe_file(payload, delivery["payload_file"])
        if digest(source) != delivery["sha256"]:
            raise ValueError("Third-party source bundle changed")
    return {
        "legal_material_presence_verified": True,
        "documents": len(data["documents"]),
        "native_files": len(native_expected),
        "resource_files": len(resources),
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
