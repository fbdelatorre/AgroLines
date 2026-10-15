# Fase 4 — validação LGPL Windows e preparação de homologação

**Não é aprovação jurídica nem autorização de distribuição.** PR dependente do
[PR #15](https://github.com/fbdelatorre/AgroLines/pull/15), que depende do
[PR #14](https://github.com/fbdelatorre/AgroLines/pull/14). Nenhuma alteração ao
aplicativo, motor GIS, biblioteca de produção, identidade, política de privacidade
ou configuração da Store/Pages é necessária nesta fase.

## Referência preservada

`AgroLines-1.0.0.0-x64-CONFORMIDADE-c3ffdb68302a-DIAGNOSTICO-ASSINATURA-PENDENTE.msix`

SHA-256: `e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b`.
[Execução de referência](https://github.com/fbdelatorre/AgroLines/actions/runs/38657579756).
**Não assinado; não instalar, distribuir ou submeter.** Hash conferido diretamente
na cópia do artefato, sem alteração. 178 PE, 177 de terceiros; 100 aceitos pelo
SignTool e 78 sem assinatura. Os números históricos não são homologação SAC.

[reference-components.json](reference-components.json) recorta o relatório real
**deste candidato**: caminho, SHA-256, origem, versão, importadores e fases observadas
de Qt/GEOS. O inventário completo do PR #15 continua preservado, vinculado ao
candidato anterior `75fe…`; não o reescrevemos para fingir uma nova auditoria.

## Entregas

- [Qt Windows](qt-windows-experiment.md), [GEOS Windows](geos-windows-experiment.md):
  ensaios isolados, consumidores sintéticos 0BSD, evidências e limites.
- [Análise MSIX/LGPL](msix-lgpl-analysis.md): substituição, recombinação e ABI.
- [Materiais pendentes](missing-upstream-materials.md),
  [casos verificáveis](upstream-cases.json), [solicitações não enviadas](supplier-requests/).
- [Homologação privada](store-private-homologation.md),
  [coleta SAC somente de leitura](sac-test-procedure.md).
- [Questões jurídicas](legal-review-questions.md),
  [bloqueios restantes](remaining-blockers.md).

Fontes oficiais consultadas em 15/10/2026: [URLs, status HTTP e hashes](official-research.json).
Status `unavailable` não significa conteúdo conferido. Nenhum contrato autenticado
ou resposta de fornecedor foi presumido. Os relatórios originais continuam em
`docs/native-store-audit/`, `docs/windows-signing/` e no diretório pai.

Os únicos artefatos novos publicados pelo workflow de laboratório são JSON,
patches sintéticos e CMakeCache de build sem credenciais. Não incluem executáveis,
fontes/bytecode/objetos AgroLines, MSIX, projetos ou informações de testadores.
Evidências físicas do coletor são privadas e **não** são enviadas pelo workflow.

## Execuções e download

- [Windows Qt/GEOS: sucesso](https://github.com/fbdelatorre/AgroLines/actions/runs/38664013105).
- [Regressões Windows/Linux: sucesso](https://github.com/fbdelatorre/AgroLines/actions/runs/38664082723).
- [Consolidação de evidências: sucesso](https://github.com/fbdelatorre/AgroLines/actions/runs/38664078921).
- [Artefato de evidências, NÃO instalador](https://github.com/fbdelatorre/AgroLines/actions/runs/38664078921/artifacts/11940062835):
  `windows-lgpl-consolidated-EVIDENCE-NOT-LEGAL-APPROVAL`. GitHub pode exigir login
  para baixar artefatos de Actions; também pode-se abrir a execução → Artifacts.
  SHA-256 ZIP informado pelo GitHub:
  `294f4f28fff11c5149cfdd5b887b868c435070197d8d8812743e9188a90ec5ee`.
  O endpoint de download ZIP não ficou acessível neste ambiente; os três JSON
  foram recuperados por logs/annotations e seus hashes originais conferidos.
  O job GitHub baixou os originais e incluiu copyrights/textos LGPL/GPL para
  acompanhar os patches, sem binários e sem código AgroLines.

[Resultados consolidados](validation-results.json), [host](lab-hosts.json),
[preservação do candidato](preservation.json) e relatórios brutos permanecem no
repositório, além dos artefatos com retenção finita do GitHub. Windows: 224 passed /
2 skipped; Linux: 225 passed / 1 skipped; precisão baseline 22/22 em ambos; cinco
controles negativos adicionais locais, quatro por job Windows. Ruff aprovado.
Os skips anteriores não foram removidos. Nenhuma regressão do aplicativo observada.

O Windows hospedado é Server 2025, SAC não confirmado e proteção em tempo real
Defender reportada inativa, sem alteração por este trabalho. Não equivale ao cenário
de homologação exigido. MSIX/Qt sob identidade Store, instalação/atualização/
desinstalação e operação física desconectada continuam pendentes.
