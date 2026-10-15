# Fundação comercial — dependente do PR #20

Trabalho em execução, sem aprovação jurídica ou autorização de distribuição.
Primeiro foram implementadas as correções materiais de licenças; depois será
implementado o licenciamento do produto. Referência preservada: PR20/c96938c.

## Correções materiais da primeira etapa

- Manifesto vincula também os recursos reais Fiona/PROJ/Qt, com hashes, e recusa
  recursos acrescentados/alterados. Avisos são associados aos respectivos grupos.
- Markdown, HTML e texto das minutas precisam reproduzir o mesmo conteúdo; cópia
  desatualizada impede empacotamento.
- Alternativa **MPL1.1** adotada para o código que a oferece em FreeXL/SpatiaLite;
  GEOS/libiconv e demais dependências conservam suas licenças independentes.
  GCP/RTTOPO continuam desabilitados conforme prova #19.
- Incluídos originais PCRE2, LERC/LICENSE/NOTICE, libgeotiff, libwebp/PATENTS,
  libiconv e atribuições NKG; cinco receitas PROJ9.8.1 batem com hashes do SPDX
  embarcado. A versão de referência de uma receita não é prova universal da DLL.
- Entrega local versionada de fontes de terceiros, com hash e manifesto, instalada
  fora do código proprietário, acessível sem assinatura comercial ativa. Não depende
  de link temporário Actions. Nenhum ZIP de fontes será publicado automaticamente.
- GEOS3.11.3 e3.14.1: preparados builds das mesmas versões, sem patches nos arquivos
  de algoritmos/headers, apenas OUTPUT_NAME para os quatro basenames existentes.
  O novo candidato dependerá de ABI e regressões/22 referências aprovadas. Não
  substitui as referências #18–#20 ou altera seus hashes.

O ZIP distingue fontes identificadas das correspondências ainda não comprovadas.
**QtWebEngine/Chromium/PDFium não são marcados resolvidos:** .225 do runtime não
corresponde à candidata .264; gitlinks finais/avisos dos targets continuam necessários.
Não há pedido de autorização comercial genérica: as licenças são a concessão.
Recompilar um componente não regulariza automaticamente todos os outros.

## Validação e distribuição

Testes locais iniciais:39 aprovados, incluindo deriva de recursos, minutas e fontes.
O candidato seguinte é diagnóstico não assinado; nenhum instalador é executado.
O perfil Store exclusivamente offline não recebe ativação remota por configuração.
A homologação Windows11/SAC permanece posterior e exige confiança legítima.

Este arquivo será consolidado com resultados Windows/Linux e o fluxo comercial
antes da entrega final. Fontes, minutas e status não recebem aprovação automática.
