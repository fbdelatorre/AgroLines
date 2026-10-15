# Pendências de licenças: delta concreto em relação aos PRs #15–#18

Não substitui o [inventário por arquivo](../compliance/inventario-terceiros.md), os
151 documentos já reunidos nem as solicitações não enviadas em
[windows-validation](../compliance/windows-validation/README.md).
Nenhuma aprovação jurídica ou direito de assinatura foi alterado automaticamente.

## Nova evidência: SpatiaLite efetivamente carregado

[Execução aprovada](https://github.com/fbdelatorre/AgroLines/actions/runs/38739437306),
commit `382832f80ca3e7319ffea1df567b4b86ff4fc2f0`;
[resultado bruto](evidence/license-configuration.json).
[Artefato 11975346246](https://github.com/fbdelatorre/AgroLines/actions/runs/38739437306/artifacts/11975346246),
digest API `4b5b6707cfe2698f5292c5b141eaf5d7d222c84a0ac0e6f3420e326da4ad9a19`.

O mesmo EXE do #18 carregou `fiona.libs/spatialite-e03c16976c81110a807ddde663a483fb.dll`,
SpatiaLite **5.1.0**, SHA-256
`aac50734dd21a12d40a112c423f518cd41bedc5aa3c9f4fe713eb361525b9df2`.
SQLite da Fiona: `sqlite3-0cb9f6e67fd2491114f55ace5268f7aa.dll`, SHA-256
`70255ca0d3a5fa20cd10a2cbf41dd3e3819c82a42e825d2ec50d06838114fffb`.

Consultas oficiais em banco **novo `:memory:`**, funções obtidas nos módulos já
carregados, cache da própria conexão e limpeza somente desse contexto:

| Consulta | SQLITE_OK | Resultado |
| --- | --- | --- |
| `HasGeos()` | sim | 1 |
| `HasProj()` | sim | 1 |
| `HasRtTopo()` | sim | **0** |
| `HasGCP()` | sim | **0** |

Fontes oficiais: [funções SpatiaLite 5.1](https://www.gaia-gis.it/gaia-sins/spatialite-sql-5.1.0.html),
[receita vcpkg libspatialite](https://github.com/microsoft/vcpkg/blob/master/ports/libspatialite/vcpkg.json)
e receitas versionadas já preservadas no caso U04. A receita distingue as features
`gcp`/`rttopo` que restringem as alternativas a GPL. O teste resolve **essa dúvida
factual nesse binário**; não elege automaticamente licença, comprova toda a BOM
estática ou elimina as outras obrigações de redistribuição.

A enumeração dos recursos Qt retornou 532 entradas e nenhum crédito completo.
Ausência nesse escopo **não prova ausência universal de créditos nem dispensa
avisos**. Não acrescentamos arquivos JavaScript/PAK incorretamente como licenças.
U02 continua aberto.

## O que falta, por pacote de trabalho existente

| Caso | Avanço comprovado / situação | Material ou decisão realmente faltante |
| --- | --- | --- |
| U01 Qt/PySide6/Shiboken | **PARCIAL**: Qt Core modificado funciona no AgroLines completo; fontes Python externas já testadas no #18 | Correspondência exata de fontes, patches/flags/CRT, BOM estática e avisos dos wheels. Avaliação LGPLv3 §4, mecanismo de substituição e EULA para a distribuição real. Outros módulos Qt não foram recompilados neste PR. |
| U02 WebEngine/Chromium/PDFium | **BLOQUEADO documental**: nada novo prova créditos/fontes completos do wheel 6.12.0.140 / runtime 6.140.0 / Chromium 140.0.7339.225 | Gitlinks finais, patches, GN args, codecs habilitados e avisos gerados dos targets reais. Obter resposta Qt específica; não substituir por homepage Chromium. |
| U03 GDAL 3.9.1 | **CONCLUÍDO no escopo já declarado** | Nove receitas/inputs SHA512 verificados antes; não repetir nem ampliar a conclusão para toda a BOM. |
| U04 Fiona/vendors | **PARCIAL**: GEOS 3.11.3 substituído; GCP/RTTOPO desabilitados comprovados | Fontes/patches/receitas originais GEOS/SpatiaLite/libiconv/FreeXL, SZIP/encoder, eleição de alternativas e notices estáticos/drivers. Não presumir LGPL por metadata Fiona. |
| U05 Shapely/GEOS | **PARCIAL**: GEOS 3.14.1 substituído no aplicativo completo | Fonte/build/patch/CRT/delvewheel original; LGPLv2.1 §6, disponibilidade de fontes e avisos dos dois pares GEOS. BSD do binding não licencia GEOS. |
| U06 pyproj/PROJ/dados | **PARCIAL documental**: preservados dados e avisos já inventariados | Mapeamento dos builds PROJ 9.8.1, releases/atribuições de bases e datasets realmente incluídos. Não exigir copyleft que a licença permissiva não imponha. |
| U07 NumPy/OpenBLAS/LAPACK/GCC | **PARCIAL documental**: textos completos do wheel já preservados | Resolver identificador OpenBLAS 0.3.34.106.0 em commit/patch/build e LAPACK; identificar componentes GCC estáticos e aplicabilidade da Runtime Library Exception. |
| U08 Microsoft | **PARCIAL**: standalone dispensa contrato Store para esse canal | Confirmar direitos de redistribuição MSVC/UCRT, inclusive CRT estático do launcher e ferramentas de build. Questões específicas da Store permanecem separadas se esse canal for retomado. |

São oito pacotes de trabalho, não oito bibliotecas: **um encerrado no escopo U03,
sete ainda com materiais/decisões incompletos**. Testes novos resolvem subitens,
não encerram artificialmente pedidos ao fornecedor. Nenhuma mensagem foi enviada.
Solicitações exatas e anexos seguros existentes continuam prontos para revisão/envio
pelo responsável em [supplier-requests](../compliance/windows-validation/supplier-requests/).

## Próximo pacote comercial de conformidade

1. Obter somente as respostas acima; associar fontes/patches/receitas e avisos às
   DLLs pelos hashes do inventário. Arquivos genéricos não encerram correspondência.
2. Atualizar o manifesto dos materiais e coletor existente; executar os gates
   objetivos. O coletor ampliado do #15 já inclui COPYING/NOTICE/AUTHORS/COPYRIGHT;
   não foi reescrito nem reduzido neste PR.
3. Disponibilizar fontes de terceiros completas na modalidade aprovada para cada
   licença, com retenção/acesso e instruções de reconstrução. Os arquivos upstream
   identificados e as receitas do laboratório ainda não são oferta completa dos wheels.
4. Revisão jurídica separada: LGPLv3 Qt/PySide/Shiboken; LGPLv2.1 GEOS; bibliotecas
   vendorizadas/estáticas; patentes/codecs; futura EULA e direitos de modificação e
   engenharia reversa para depuração de bibliotecas modificadas.
5. Usar a [minuta EULA existente](../compliance/licenciamento-agrolines-minuta.md)
   com exceções LGPL, sem torná-la contrato adotado por teste de CI. Licenciamento
   comercial próprio futuro não deve retirar esses direitos; chaves privadas fora
   do cliente. PyInstaller não impede extração de bytecode.

Nenhum impedimento técnico novo demonstrou necessidade de comprar Qt Commercial.
Ele continua alternativa contratual, com elegibilidade de migração e preço a
confirmar, não correção automática para GEOS/Chromium/vendors nem assinatura SAC.

## Privacidade e testadores

Preservadas as minutas em [docs/privacy/offline](../privacy/offline/) e o programa
privado **18+**; classificação Store não alterada. Gmail pessoal previsto, sem
histórico de atendimentos confirmado; retenção proposta de 90 dias pós-suporte,
30 dias após saída para registros próprios de testadores, 12 meses pós-pedido de
privacidade. Rotinas manuais e controles ainda precisam ser executados pelo titular.
Bases legais e transferências não foram aprovadas. Não publicar política com
campos pendentes. Antes de distribuir standalone, revisar também as menções ao
canal Store e tratamentos efetivos deste novo canal, sem inventar fornecedor.

Projetos/backup SQLite locais permanecem sem criptografia própria AgroLines.
Recursos GIS/Leaflet continuam locais, nenhuma telemetria foi acrescentada. O
repositório foi encontrado público e não teve sua visibilidade alterada; onedir
não torna confidencial o fonte já público. Decisão sobre confidencialidade cabe
exclusivamente ao proprietário e não foi executada aqui.
