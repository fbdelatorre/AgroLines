"""Collect unchanged legal texts for identified payload inputs, not the whole builder."""

import hashlib
import importlib.metadata
import json
import re
import shutil
from pathlib import Path

WORDS = ("license", "licence", "copying", "notice", "copyright", "authors", "contributors")
CODE = {".py", ".pyc", ".pyo", ".pyd", ".dll", ".exe", ".so", ".dylib"}


def is_notice(path):
    path = Path(path)
    return (
        path.suffix.casefold() not in CODE
        and any(word in path.name.casefold() for word in WORDS)
        or (
            path.suffix.casefold() not in CODE
            and any(part.casefold() in ("licenses", "licences") for part in path.parts[:-1])
        )
    )


def normalized(name):
    return re.sub(r"[-_.]+", "-", name).casefold()


def shipped_distributions(payload, modules, distributions):
    root = Path(payload)
    paths = {
        p.relative_to(root).as_posix().removeprefix("_internal/").casefold()
        for p in root.rglob("*")
        if p.is_file() and "third-party-notices" not in p.parts
    }
    selected = []
    for package in distributions:
        matches = []
        for entry in package.files or []:
            value = str(entry).replace("\\", "/")
            if is_notice(value) or ".dist-info/" in value:
                continue
            module = value.removesuffix(".py").replace("/", ".").removesuffix(".__init__")
            if value.casefold() in paths or (value.endswith(".py") and module in modules):
                matches.append(value)
        bootloader = normalized(package.metadata["Name"]) == "pyinstaller" and any(
            p.suffix.casefold() == ".exe" for p in root.glob("*.exe")
        )
        if matches or bootloader:
            selected.append((package, sorted(matches), bootloader))
    return selected


def collect(payload, modules=(), distributions=None):
    root = Path(payload) / "third-party-notices"
    # Fail rather than silently mix a previous collector's output with this build.
    if root.exists():
        raise ValueError("Notice output must be fresh")
    root.mkdir(parents=True)
    rows, documents = [], []
    distributions = list(
        importlib.metadata.distributions() if distributions is None else distributions
    )
    for package, matches, bootloader in shipped_distributions(payload, set(modules), distributions):
        name = package.metadata["Name"]
        rows.append(
            {
                "name": name,
                "version": package.version,
                "license": package.metadata.get("License-Expression")
                or package.metadata.get("License", "not declared"),
                "evidence_scope": "Metadata only; vendored components need independent review",
                "payload_inputs": matches,
                "embedded_bootloader_or_runtime": bootloader,
            }
        )
        for entry in package.files or []:
            if not is_notice(entry):
                continue
            source = Path(package.locate_file(entry))
            if not source.is_file():
                raise ValueError("Missing declared notice: " + str(entry))
            safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(entry))
            target = root / name / safe
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError("Notice name collision")
            shutil.copyfile(source, target)
            raw = target.read_bytes()
            documents.append(
                {
                    "path": target.relative_to(root).as_posix(),
                    "package": name,
                    "version": package.version,
                    "source_member": str(entry),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "size_bytes": len(raw),
                }
            )
    (root / "packages.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (root / "collected-notices.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "documents": documents,
                "scope": "Identified payload input notices; "
                "static components not automatically cleared",
                "legal_compliance_approved": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return rows
