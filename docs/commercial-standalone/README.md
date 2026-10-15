# Avanço comercial standalone — PR #19, dependente do #18

Data das evidências: **15/10/2026**. Branch
`compliance/standalone-native-validation`, base `compliance/standalone-offline`.
[PR #19](https://github.com/fbdelatorre/AgroLines/pull/19), sem merge ou publicação.

## Resultado objetivo

| Entrega | Estado | Evidência e limite |
| --- | --- | --- |
| Qt Core nativo modificado no AgroLines completo | **CONCLUÍDO** no laboratório | Mesmo EXE congelado; versão marcada carregada; GUI/WebEngine/GIS e 22/22. Não recompila os demais módulos Qt nem comprova SAC. |
| GEOS nativo Fiona 3.11.3 e Shapely 3.14.1 | **CONCLUÍDO** no laboratório | Dois pares C/C++ reconstruídos e substituídos em cópias independentes; caminhos/versões/hashes observados, 22/22. Nenhum algoritmo ou binário de produção alterado. |
| SpatiaLite: dúvida GCP/RTTOPO | **CONCLUÍDO** no escopo factual | Ambas features retornaram 0 no binário realmente carregado. Fontes, alternativas de licença e avisos ainda têm pendências. |
| Fontes/avisos/EULA comerciais | **PARCIAL** | Provas fecham subitens técnicos; U01/U02/U04–U08 não são encerrados por presunção. Revisão jurídica/fornecedores ainda necessários. |
| Launcher estável, ícone e pastas por versão | **CONCLUÍDO** em testes de processo | App completo pelo launcher, troca de seleção, argumentos Unicode/espaços e recusa de path escape. Atalhos fixados, múltiplos usuários e ciclo Inno físico continuam **PARCIAIS**. |
| Preparação Authenticode app/vendor/launcher/setup/uninstaller | **PARCIAL** | Guards, hashes, direitos, timestamp e pós-verificação preparados; recusas testadas. Zero assinatura realizada; integração real com CA/callback não homologada. |
| Instalação/atualização/desinstalação assinada | **BLOQUEADO** para execução | Script e critérios prontos; falta certificado/candidato legítimo, autorização e Windows 11 real com SAC/Defender ativos. Não houve instalação. |
| Regressões | **CONCLUÍDO** no código testado | 236 testes Windows, 237 Linux; 22/22. Não é precisão centimétrica absoluta de campo nem homologação SAC. |
| Prontidão para distribuição comercial | **BLOQUEADO** | Materiais de licença/EULA/privacidade, identidade/serviço de assinatura e homologação física. Qt Commercial não foi demonstrado obrigatório. |

Relatórios específicos:

- [Substituição nativa: fontes, versões, hashes e download das evidências](native-replacement.md).
- [Licenças: somente as pendências reais e nova evidência SpatiaLite](licenses-status.md).
- [Assinatura: fluxo implementado, opções para Brasil e cotação preparada](signing.md).
- [Instalador: arquitetura, roteiro assinado e critérios objetivos](installer-homologation.md).
- [Manifesto verificável dos dados de evidência](evidence/manifest.json).

## Execuções e artefatos

1. [Qt/GEOS no AgroLines completo — três jobs aprovados](https://github.com/fbdelatorre/AgroLines/actions/runs/38737953304).
2. [Features reais SpatiaLite e recursos Qt — aprovado](https://github.com/fbdelatorre/AgroLines/actions/runs/38739437306).
3. [Launcher/Inno/probes e recusas de assinatura — aprovado](https://github.com/fbdelatorre/AgroLines/actions/runs/38742958569).
   [Artefato somente de evidências](https://github.com/fbdelatorre/AgroLines/actions/runs/38742958569/artifacts/11976946285):
   `agrolines-standalone-HOMOLOGATION-EVIDENCE-ONLY`, digest Actions
   `82f9b3957ea1a978cd1556af98e2aed6697e9b49ad0b57550b5cb855a3a8e06a`.
4. [Qualidade completa Windows/Linux — aprovada](https://github.com/fbdelatorre/AgroLines/actions/runs/38742959630).
   Windows 236 aprovados/2 ignorados; Linux 237/1; Ruff/formatação aprovados.
   Controles negativos novos também passaram, incluindo marcador falso, hash
   observado divergente, precisão incompleta e captura ausente. Os jobs existentes
   de integração/API e visuais hospedados passaram; não são ensaio físico SAC.

Na execução 3 o builder compilou, **sem instalar**, o diagnóstico:
`AgroLines-Standalone-1.0.0.1-x64-46b5152df560-EXPERIMENTAL-UNSIGNED.exe`,
SHA-256 `8dd54d6cd4db49917e2ce96af3b9019f806627acb93ac594282619d7966a183f`,
159.869.911 bytes. **Não assinado; não distribuído como artefato nesta branch e
não autorizado para instalação.** O ZIP disponibilizado contém somente evidências.
[Registro do build](evidence/installer-build.json) vincula payload, lock, versão,
fonte head `ed3b3cecc9605ef6c4daf7d7e74053063bf97d6d` e merge de teste
`46b5152df56008a278324718000a946b41bd97c8`.
A compilação é evidência do empacotamento, não entrega comercial.

Os testes de substituição reutilizaram o artefato imutável **#18**, não esse novo
runtime. O novo candidato muda o ponto de entrada próprio somente para identidade
da barra de tarefas e adiciona launcher/instalação; motor GIS, desktop, formatos,
precisão e dependências de produção não mudaram. Hash novo de candidato não
substitui o hash das referências anteriores. O preflight somente de mantenedor exige raiz pública revisada e revogação offline
em cache; sua sintaxe e recusa sem autorização passaram nessa execução. Seu corpo
de instalação e verificação criptográfica real não foi executado.

## Preservação e limites

- Main preservada em `a7af60408fbd85105d58696386a0b985668b4bb9`.
  PRs originais não foram mesclados, fechados ou sobrescritos; #18 segue base.
- MSIX de referência
  `AgroLines-1.0.0.0-x64-CONFORMIDADE-c3ffdb68302a-DIAGNOSTICO-ASSINATURA-PENDENTE.msix`,
  SHA-256 `e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b`,
  e artefato standalone #18 preservados. Não foram instalados/assinados.
- Laboratórios modificam somente cópias separadas, nunca as 177 dependências PE
  originais. A árvore de produção continua com 178 PE; launcher é componente próprio
  adicional do instalador. Nada foi removido para esconder pendências.
- Nenhuma compra, assinatura real, instalação AgroLines, convite, envio a fornecedor,
  alteração de SAC/Defender, Developer Mode, certificado de teste, Pages, Store,
  classificação etária ou visibilidade foi realizada.
- Avisos/fontes/privacidade não foram marcados aprovados. Os relatórios anteriores
  permanecem históricos; este diretório documenta os avanços posteriores ao #18.

## Menor lista de bloqueios reais

1. **Jurídico/fornecedores:** completar materiais U01/U02/U04–U08 e revisar LGPLv3,
   LGPLv2.1, componentes estáticos/codecs, MSVC, fonte/avisos e EULA com exceções
   necessárias. Fontes de laboratório não são prova automática dos wheels originais.
2. **Titular/CA:** confirmar elegibilidade Individual Brasil, nome legal do certificado,
   direitos por arquivo e cotação total. Depois autorizar a integração de assinatura
   pública e configurar runner/ambiente protegido. Não há certificado contratado.
3. **Homologação:** autorizar um candidato realmente assinado e testar Windows 11
   físico com SAC/Defender, usuário comum, rede desconectada, update/uninstall/dados,
   QGIS, múltiplos usuários, pins e confiança dos auxiliares. Há roteiro e script,
   não resultado físico já aprovado.
4. **Privacidade/operação:** revisar minutas do canal standalone/testadores 18+,
   bases legais/transferências, vigência/URL e configurar suporte/retencão/conta.
   Nenhuma publicação jurídica pode ser inferida de sucesso de build.

Não há motivo técnico demonstrado para abandonar onedir/Inno ou comprar Qt
Commercial agora. A demonstração técnica de substituição avançou; a decisão de
regularidade e de disponibilização comercial continua dependente dos itens acima.
