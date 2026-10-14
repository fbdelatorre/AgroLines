# Respostas aos critérios de conclusão

O estado é específico para a referência SHA `75fe75…ac90` e os materiais desta etapa.
Nenhuma linha aprova distribuição, LGPL, LGPD ou SAC por resultado de CI.

| # | Pergunta | Resposta objetiva | Classificação |
|---:|---|---|---|
| 1 | Todos os componentes distribuídos identificados? | 798 caminhos/178 PE identificados, com hashes e origens. Não: fechamento de código estático, Chromium, codecs e algumas versões depende de build BOM | PENDENTE DE FORNECEDOR |
| 2 | Todos os textos obrigatórios reunidos? | Não: 104 documentos legais/SPDX originais preservados e complementos versionados reunidos; faltam atribuições/termos exatos de builds incorporados | PENDENTE DE DOCUMENTAÇÃO |
| 3 | Fontes com correspondência comprovada? | `certifi/cacert.pem` igual ao sdist (escopo MPL). Recursos Leaflet iguais aos arquivos do projeto. Isso não comprova fontes completas dos builds LGPL Windows | CONCLUÍDO COM EVIDÊNCIA somente para essas comparações |
| 4 | Quais fontes faltam? | Qt/PySide completo, engine 6.140/Chromium/PDF, GEOS Windows com patches/receitas, libiconv, SpatiaLite/FreeXL e internos conforme licença; detalhes em fontes-correspondentes.md | PENDENTE DE FORNECEDOR |
| 5 | Mecanismo LGPL demonstrado Qt? | Qt Core modificado em consumidor sintético Linux inalterado: sim. Obra PySide/MSIX/Store/Windows: não | IMPLEMENTADO, AGUARDANDO VALIDAÇÃO; rota MSIX BLOQUEADA |
| 6 | Mecanismo LGPL demonstrado GEOS? | GEOS 3.11.3 modificado com C API e área esperada em consumidor sintético Linux: sim. Duas famílias Windows no aplicativo/MSIX: não | IMPLEMENTADO, AGUARDANDO VALIDAÇÃO |
| 7 | Pode continuar proprietário sem Commercial? | Em princípio, se atender integralmente às licenças dos módulos, avisos/fontes, direitos e mecanismo aplicável; candidato atual ainda não demonstrou isso | PENDENTE DE REVISÃO JURÍDICA |
| 8 | O que foi materialmente cumprido? | Preservação/hash da referência, inventário por arquivo, cópias integrais/evidências dos textos reunidos, arquivos upstream locais, coletor corrigido, mecanismos sintéticos e verificações negativas | CONCLUÍDO COM EVIDÊNCIA para esses materiais; não para conformidade integral |
| 9 | O que depende de jurídico? | Escolha/adequação das rotas LGPL, EULA, termos exatos de copyleft/redistribuição/patentes quando aplicáveis, privacidade/bases/transferências e requisitos Store | PENDENTE DE REVISÃO JURÍDICA |
| 10 | O que depende de fornecedor? | Fontes/BOM/patches/build/credits exatos e direitos faltantes; Microsoft sobre conta/capabilities/Store trust. Qt Commercial só se essa opção vier a ser escolhida | PENDENTE DE FORNECEDOR |
| 11 | Privacidade pronta para revisão? | Política MD/HTML/TXT, termo adulto/aceite e plano/registros/retencão já preparados; sem status aprovado, data/URL e decisões obrigatórias ainda pendentes | IMPLEMENTADO, AGUARDANDO VALIDAÇÃO |
| 12 | O que falta para submissão privada? | Fechar os blocos materiais/jurídicos/Store listados e autorização. Homologação física SAC só poderá ser concluída com pacote legítimo; não é prova obtida por este MSIX unsigned | BLOQUEADO |
| 13 | Motivo técnico comprovado para comprar Commercial agora? | Nenhum demonstrado que decorra só de ser proprietário. A rota LGPL MSIX segue sem prova; eventual necessidade/benefício contratual depende dessa avaliação e resposta de migração Qt | PENDENTE DE REVISÃO JURÍDICA |
| 14 | Menor lista de decisões do responsável? | Adotar documentos/rotinas após revisão; escolher rota LGPL/contratual após evidências (autorizar à parte eventual material próprio); autorizar separadamente Pages, merge e submissão futura | IMPLEMENTADO, AGUARDANDO VALIDAÇÃO |

O relatório automático separa falha técnica, pendência documental, jurídica e
contratual. Seu retorno zero significa integridade material, nunca aprovação legal.
