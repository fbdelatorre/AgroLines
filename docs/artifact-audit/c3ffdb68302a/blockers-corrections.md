# Bloqueios reais, correções e decisão recomendada

| Achado | Correção/ação proposta | Situação e critério de fechamento |
| --- | --- | --- |
| 106 cadeias agregadas sem distinguir 78 unsigned/28 expiração | Exibir os três conjuntos exclusivos e preservar ambos os verificadores. Não ignorar expiração/revogação. | **CONCLUÍDO COM EVIDÊNCIA** para reconciliação estática: CSV/JSON, 72+28+78=178. Revalidação Windows atual permanece pendente. |
| Relatório não separa reprodução de conteúdo e envelope | Acrescentar status explícito not_run/null/quantidade de MSIX comparados em build futuro; executar dois empacotamentos somente quando justificado/autorizado. | **IMPLEMENTADO, AGUARDANDO VALIDAÇÃO** para comparador sintético; mudança no pipeline **proposta**, não aplicada ao candidato. |
| Normalização silenciosa de nomes pelo leitor ZIP Windows na ferramenta nova | Validar orig_filename e recusar mudança silenciosa/NUL antes de caminhos normalizados; manter fixture malformada em bytes. | **IMPLEMENTADO, AGUARDANDO VALIDAÇÃO** Windows; 16 controles Linux, inclusive simulação independente da plataforma. Não afeta bytes ou execução do candidato. |
| Assinatura/pacote e aceitação SAC ainda ausentes | Rota legítima Store após demais gates; verificar catálogo/PE e instalação real, sem presumir que todos PE precisam de assinatura embutida nem que envelope cobre toda confiança. | **BLOQUEADO** para homologação: W00–W10, pacote confiável e autorizações futuras. Não comprar certificado por presunção. |
| Origem de builder comprovada, fontes/builds/vendors incompletos | Fechar solicitações técnicas U01/U02/U04/U05/U06/U07 já preparadas, fontes/patches/flags/avisos e correspondência por componente. | **PENDENTE DE FORNECEDOR / DOCUMENTAÇÃO**. U03 posterior fecha só insumos limitados GDAL, não todos vendors. |
| LGPL Qt3/GEOS2.1 sob MSIX não demonstrada integralmente | Revisar alternativas e exigir mecanismo utilizável para cópia distribuída, fontes, direitos/EULA. Não publicar materiais próprios sem autorização. | **PENDENTE DE REVISÃO JURÍDICA** e demonstração técnica. Consumidores sintéticos não são recombinação AgroLines. |
| Política embutida contém quatro confirmações | Fechar bases/transferências com evidências, operação Gmail/18+/retenção, data real e HTTPS público só após aprovação. Revisar proteção de dados Store e contratos/capabilities. | **PENDENTE DE REVISÃO JURÍDICA / DOCUMENTAÇÃO / DECISÃO OPERACIONAL**. Não publicar campos pendentes. |
| Helper de teste instala/remove; switches fortes opcionais | Manter separado de coletores e futuramente exigir preflight e autorização explícitos, origem legítima, dados sintéticos, duas versões e backup. | **Proposta técnica**, sem execução ou alteração de payload; este roteiro para antes de instalar. |
| Provas offline não incluem captura nativa completa | Testar conectado por processo/filhos e desconectado fisicamente, rede DNS/TCP/UDP e DLLs reais. | **IMPLEMENTADO, AGUARDANDO VALIDAÇÃO** para roteiro; captura/teste físico **NÃO EXECUTADOS**. |

## O que foi materialmente entregue agora

Verificador de arquivo fixado por SHA, mapa de blocos/payload/PE/avisos/política,
inventário individual com motivos, controles negativos, snapshot SQLite de leitura,
roteiro e formulário Windows com todos os ensaios not_run. Nenhum binário ou artefato
oficial foi modificado; nenhum novo MSIX foi produzido. Os novos arquivos são de
auditoria/laboratório, fora dos caminhos do payload; a igualdade do candidato é
conferida novamente pelo SHA-256. Testes locais/CI não substituem o Windows físico.

## Próximo passo recomendado

**Manter o candidato como diagnóstico imutável.** Primeiro, fechar materiais exatos
dos fornecedores e revisão LGPL/EULA/privacidade, aproveitando pedidos já preparados.
Em paralelo, designar bancada Windows 11 clean e preparar fixtures/evidências. Só
após os gates e autorização separada obter um pacote legitimamente entregue pela
Store para W00–W10. Não assinar em massa os 78, não remover DLLs não observadas e não
tratar os 28 carimbados como bibliotecas corrompidas.

Até cinco decisões externas do responsável: encaminhar solicitações aos fornecedores;
encaminhar revisão jurídica e escolher rota LGPL após parecer; configurar operação
Gmail/testadores; designar bancada física; autorizar futuramente e separadamente
submissão/publicação privada/homologação. **Nenhuma foi executada por esta auditoria.**
