# Dossiê de terceiros do AgroLines — proposta para revisão

Revisão: 14/10/2026. Produto próprio pretendido: proprietário/comercial. Não se
adota nem se altera a licença do projeto. Não há autorização de distribuição.

## Referência preservada

- PR [#14](https://github.com/fbdelatorre/AgroLines/pull/14), branch
  `integration/store-candidate`, commit `c7e32477e51a0ece2c304afe2a549abcdb76af22`.
- MSIX `AgroLines-1.0.0.0-x64-DIAGNOSTICO-ASSINATURA-PENDENTE.msix`, 240744630 bytes.
- SHA-256 `75fe75bd8d7097b826d46c4cd50576162f99aede3eb2db9def34d21a3b25ac90`.
- [Build original](https://github.com/fbdelatorre/AgroLines/actions/runs/38647878392),
  [artefato original](https://github.com/fbdelatorre/AgroLines/actions/runs/38647878392/artifacts/11933945487).
- Source efetivamente compilado: merge de teste `f11542027ce33561826dac00c961f726defc46e2`.
- Não assinado; não autorizado para instalação, distribuição ou submissão.
  178 PE / 100 aceitos pelo SignTool / 78 sem assinatura não equivalem a aceite SAC.

## Materiais utilizáveis

1. [Inventário](inventario-terceiros.md) e [registro por arquivo](inventory.json):
   798 arquivos mais o manifesto autorreferente, 178 PE, versões/owners/hashes;
   componentes estáticos e licenças sem prova continuam identificados como lacunas.
2. [Licenças e avisos](licencas-e-avisos.md): 104 documentos recuperados do próprio
   MSIX, originais sem tradução, e cabeçalhos/fontes complementares identificados.
3. [Fontes](fontes-correspondentes.md): arquivos de terceiros preparados localmente,
   hashes, commits, escopo comprovado e instruções; nenhum pacote de fontes publicado.
4. [Qt](qt-lgplv3.md), [GEOS](geos-lgplv21.md), [alternativas MSIX](relinking-msix.md)
   e [experimentos sintéticos](../../tools/compliance-poc/README.md).
5. [Minuta comercial](licenciamento-agrolines-minuta.md),
   [privacidade](privacidade-store-checklist.md), [Store](prontidao-store.md),
   [pendências externas](pendencias-juridicas.md).

## Reproduzir a conferência

```sh
python -m scripts.compliance_check --output build/compliance/verification.json
python -m pytest tests/test_compliance.py
```

`--submission` retorna código 2 enquanto este dossiê é preparatório. Aprovação
jurídica não pode ser obtida alterando um booleano ou deixando o CI verde.
`technical_failure`, `documentary_pending`, `legal_pending` e `contractual_pending`
são classes distintas. [documents.json](documents.json) fixa SHA-256 dos documentos;
`--refresh-documents` é atualização explícita para revisão, não correção de licenças.
Um manifesto de payload diferente fornecido com `--payload-manifest` falha: exige
outro candidato e revisão da associação de avisos. Nenhum teste altera SAC/Defender.

## Mudança de build proposta

O coletor agora procura LICENSE/LICENCE, COPYING, NOTICE, AUTHORS, CONTRIBUTORS e
COPYRIGHT pelo nome do documento, preserva bytes, registra hashes/origens e filtra
pelos arquivos efetivos/módulos da Analysis. Inclui a exceção do bootloader PyInstaller,
mas não atribui suas permissões a bibliotecas vinculadas. Não coleta ferramentas só
porque estão instaladas. Essa correção é para **um próximo build**, cujos avisos e
payload terão outro hash; não foi aplicada retroativamente ao MSIX de referência.
A pasta de conformidade completa não é copiada ao aplicativo: contém análises e
minutas internas, que não devem ser confundidas com avisos aprovados ao usuário.

As rotas de assinatura não foram aprovadas pelo dossiê. O workflow identifica
um eventual novo build como `CONFORMIDADE-<SHA do build>-DIAGNOSTICO-ASSINATURA-PENDENTE`;
o artefato de referência e sua política permanecem imutáveis. A mudança de payload
proposta limita-se ao escopo dos avisos e seu manifesto; novo build requer hash
e revisão próprios, e continua com os gates jurídicos/contratuais fechados.

Zero PE com procedência pendente significa correspondência com o **binário de
entrada** do build. Não significa código-fonte correspondente LGPL comprovado.
As fontes locais agora somam 20 arquivos, incluindo uma árvore candidata WebEngine
sem correspondência final/submódulos; nenhuma dessas lacunas foi convertida em aprovação.
