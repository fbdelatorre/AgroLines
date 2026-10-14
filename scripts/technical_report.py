"""Write the diagnostic artifact's README from actual same-run evidence; never approve release."""

import argparse
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence
    binding = read(root / "signing/input-binding.json")
    native = read(root / "qt-minimal/native-current.json")
    candidate = read(root / "msix/candidate.json")
    plan = read(root / "signing/plan.json")
    offline = read(root / "qt-minimal/loads/offline-import-edit-backup-probe.json")
    cases = list(ET.parse(root / "tests/windows.xml").getroot().iter("testcase"))
    if not cases or any(
        c.find("failure") is not None or c.find("error") is not None for c in cases
    ):
        raise ValueError("Successful nonempty same-run Windows test evidence required")
    skipped = sum(c.find("skipped") is not None for c in cases)
    if skipped == len(cases):
        raise ValueError("A skipped-only suite is not validation")
    if binding["package_sha256"] != candidate["sha256"]:
        raise ValueError("README package hash must match the actually inspected archive")
    if candidate["sac_approved"] or plan["distribution_approved"]:
        raise ValueError("Diagnostic artifact cannot claim physical or release approval")
    current = native["summary"]
    precision = offline["components"]["precision"]
    if precision["computational_tests_passed"] is not True or len(precision["checks"]) != 22:
        raise ValueError("All 22 computational references must pass")
    summary = {
        "binding": binding,
        "native": current,
        "windows_tests": {"passed": len(cases) - skipped, "skipped": skipped},
        "computational_precision_checks": len(precision["checks"]),
        "engine_versions": offline["components"]["engine_versions"],
        "release_blockers": plan["release_review_blockers"],
        "sac_approved": False,
        "distribution_approved": False,
    }
    rows = [
        ("PE", 453, current["pe_files"]),
        ("SignTool aceitos", 375, current["accepted"]),
        ("Sem assinatura", 78, current["unsigned"]),
        ("Sem assinatura observados", 67, current["unsigned_observed"]),
        ("Origem pendente no payload", 46, current["origin_unconfirmed"]),
        ("Famílias Qt GPL/comercial dispensáveis", 6, 0),
    ]
    table = "\n".join(f"| {name} | {before} | {after} |" for name, before, after in rows)
    groups = Counter(row["group"] for row in native["files"])
    text = f"""# AgroLines — MSIX técnico NÃO AUTORIZADO PARA DISTRIBUIÇÃO

Arquivo: `{binding["package_file"]}`; x64 {candidate["version"]}.
SHA-256: `{binding["package_sha256"]}`.
Commit compilado: `{binding["source_commit"]}`.
Execução: {candidate["run_url"]}.
Envelope não assinado; nenhuma assinatura própria executada.

| Indicador | Original | Atual |
|---|---:|---:|
{table}

Windows: {len(cases) - skipped} testes passaram, {skipped} ignorados.
Precisão computacional: {len(precision["checks"])}/22; não é homologação de campo.
Linux: consultar a execução Qualidade do mesmo PR/commit; não foi executado neste builder Windows.
Grupos PE atuais: `{json.dumps(dict(groups), sort_keys=True)}`.
Versões efetivamente reportadas: `{json.dumps(summary["engine_versions"], sort_keys=True)}`.

Inventário por arquivo: [CSV](qt-minimal/native-current.csv) e
[JSON](qt-minimal/native-current.json).
Inclui hashes, inputs/versões/assinaturas/imports, observações e evidências de licença.
[Plano](signing/plan.json), [binding](signing/input-binding.json),
[reprodução dos bytes](signing/reproducibility.json), [archive/identidade](msix/candidate.json).
Recursos oficiais de marca verificados em [branding](msix/branding.json).
Probes sintéticos e módulos/erros: [loads](qt-minimal/loads/loads.json).
Os 46 inputs incidentais foram rastreados e excluídos;
não se declara validação dos instaladores JDK/MySQL.

O pacote inclui a política nativa exata e os textos GNU verificados.
Isso não completa fontes/notices/LGPL.
Pendências de revisão: `{", ".join(plan["release_review_blockers"])}`.
LGPL, privacidade, instalação/atualização/desinstalação, SAC e distribuição comercial não aprovados.
Não instalar este MSIX não assinado, não enviar aos testadores nem submeter à Store.
Homologação física depende de autorização e do pacote confiável efetivamente recebido pela Store.
Não alterar SAC/Defender, não instalar certificado de teste e não habilitar Developer Mode.
"""
    (root / "README.md").write_text(text, encoding="utf-8")
    (root / "technical-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("AGROLINES_TECHNICAL_REPORT=" + json.dumps(summary))


if __name__ == "__main__":
    main()
