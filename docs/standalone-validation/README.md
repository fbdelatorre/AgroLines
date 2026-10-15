# Validação do standalone experimental — 15/10/2026

PR [#18](https://github.com/fbdelatorre/AgroLines/pull/18), dependente do #17.
Implementação e instruções: [distribuição standalone](../distribution/standalone/README.md).
Este relatório fica fora dos documentos incorporados ao payload para registrar
seus hashes sem criar dependência circular de reconstrução.

## Artefato efetivamente gerado

- [Execução Windows aprovada](https://github.com/fbdelatorre/AgroLines/actions/runs/38733288326).
- [Download do artefato](https://github.com/fbdelatorre/AgroLines/actions/runs/38733288326/artifacts/11970829773),
  nome `agrolines-standalone-EXPERIMENTAL-UNSIGNED` (retenção configurada: 30 dias).
- Instalador em `dist/installers/AgroLines-Standalone-1.0.0.1-x64-471a90560eb3-EXPERIMENTAL-UNSIGNED.exe`.
- Versão **1.0.0.1**, x64, perfil `standalone-offline`, tamanho **159.754.061 bytes**.
- SHA-256 do **instalador**, calculado pelo builder Windows:
  `59c1312d1742a6b649483f6dcea5ce37b622b4eb24528c9c5633ceb9efe8b63f`.
- ZIP do Actions: 396.216.470 bytes; digest informado pelo GitHub:
  `bcedac586746e44aa449159b5f4c890d69b9690234fcf7f698d001fc98aad99d`.

**Não assinado (`NotSigned`). Não instalar/distribuir este experimento.** O builder
compilou o instalador e executou somente a árvore onedir, sem instalar AgroLines,
sem certificado, sem acesso a chave e sem alterar proteções do Windows.

O build usa o merge de teste GitHub
`471a90560eb326b27acf75bcb47c700d66e51782`, cujo conteúdo é idêntico ao commit da
branch `710a9664fe7112570775224909d174a7738f24a5`: ambos têm árvore
`25326d8c1b38b7c8527465e56903338abf6b2630`. O SHA no nome identifica esse build,
não um merge na main. Commits posteriores contendo apenas este relatório não
alteram o instalador já gerado.

Os valores estão associados aos logs/API da mesma execução em
[evidence.json](evidence.json). O download binário do Actions é bloqueado pelo
proxy deste ambiente; portanto não alegamos nova conferência independente dos
bytes baixados aqui. O responsável pode baixar pelo link, autenticado no GitHub,
e conferir o hash antes de qualquer homologação futura autorizada.

## Resultados

| Verificação | Evidência / resultado |
|---|---|
| Suíte Windows | 233 aprovados, 2 ignorados; Ruff e formatação aprovados. |
| Suíte Linux | 234 aprovados, 1 ignorado; Ruff e formatação aprovados. |
| Precisão computacional | 22/22 em Windows e Linux; também executada pelo aplicativo congelado original e pela cópia de laboratório. Não é homologação centimétrica de campo. |
| GUI congelada | Janela principal observada e fechada normalmente; Qt WebEngine auxiliar observado; saída zero. Execução no servidor hospedado do Actions. |
| GIS/offline | SHP, GPKG, KML, KMZ, GeoJSON; edição numérica, undo/redo, histórico, reabertura, backup/restauração; mapa/Leaflet local; recusa de API/DNS/socket e tentativas WebEngine sintéticas. Sem Python/GIS do builder no PATH. |
| LGPL Python | Fontes PySide6/Shiboken fora do PYZ; marcadores modificados efetivamente carregados pelo AgroLines congelado em cópia independente; chamadas de binding e probes funcionais aprovados. |
| Preservação nativa | 178 PE: 177 de terceiros com hashes preservados e um executável próprio novo. Gate sem divergências, caminhos novos ou remoções frente à política derivada. |
| Assinaturas | 100 aceitas por Authenticode/SignTool; 78 `NotSigned` = 77 dependências + executável próprio. Nenhuma assinatura aplicada; plano futuro continua bloqueado. |
| Inno Setup | 7.1.0 oficial, download fixado por SHA-256, assinatura verificada; compilação aprovada; nenhuma instalação AgroLines executada. |

[Execução da suíte completa](https://github.com/fbdelatorre/AgroLines/actions/runs/38733288209).
Os controles de rede são testes negativos da aplicação; não substituem desconexão
física nem rastreamento completo de todos os processos nativos.

### Correções durante a implementação

A instrumentação inicial acrescentava uma variável ao final de `PySide6/__init__.py`.
O PySide6 troca o dicionário do módulo nessa inicialização, de modo que a variável
ficava no dicionário antigo. O controle recusou corretamente essa evidência. A
instrumentação foi corrigida para definir o marcador no módulo realmente importado
(`sys.modules`), sem reduzir critérios, alterar DLLs ou algoritmos. Os testes
funcionais completos da cópia modificada então passaram. Artefatos de execuções
falhas não são candidatos autorizados para instalação.

## O que está implementado e o que falta

**Implementado e validado em CI:** perfil independente da Store e offline fixo,
onedir, exclusões Qt preservadas, fontes dos bindings externos sem sombra no PYZ,
clonagem/substituição Python demonstrada no aplicativo congelado, instalador
experimental pt-BR, atalhos, desinstalador, pastas por versão, manifesto/inventário,
plano somente leitura para assinatura e documentação. Código de `core/`, `desktop/`,
`exporters/`, `server/` e dependências do projeto não mudou em relação ao #17.

**Implementado, aguardando validação física:** instalação, atualização e
desinstalação Inno, fechamento de aplicações em uso, preservação real de dados,
múltiplos usuários, escala e atalhos fixados na barra de tarefas. Os atalhos
gerados pelo instalador são atualizados; atalhos fixados manualmente podem continuar
apontando para versão anterior. Não há launcher estável nem rollback automático
implementado. Executar o [roteiro](../distribution/standalone/validation-and-signing.md)
com candidato legitimamente assinado e autorização específica.

**Pendências comerciais reais:**

1. Fontes/receitas/avisos e licenças ainda pendentes nos dossiês #15–#17, inclusive
   componentes vendorizados/GPL/codecs; decisão jurídica sobre LGPL e futura EULA.
2. Qt/GEOS nativos modificados e ABI compatível dentro do AgroLines completo ainda
   não demonstrados; os laboratórios sintéticos anteriores são evidência separada.
3. Certificado/serviço público elegível para o titular no Brasil, direitos por
   arquivo e pipeline protegido para PE, instalador e desinstalador. Nenhuma compra
   necessária ou efetuada nesta etapa; não declarar Qt Commercial obrigatório.
4. Windows 11 físico com SAC/Defender ativos, instalação e ciclo de dados, testes
   sem internet, observação dos auxiliares/eventos e investigação de bloqueios.
5. Revisões de privacidade, bases legais/transferências, vigência/URL e procedimentos
   antes dos testes comerciais. Políticas existentes continuam minutas. O
   repositório continua público, como encontrado; empacotamento não torna o fonte
   já público confidencial. Qualquer decisão sobre visibilidade fica com o responsável.

Main permanece `a7af60408fbd85105d58696386a0b985668b4bb9`; PRs #14–#17 abertos,
com suas branches preservadas. O MSIX de referência de hash `e6a2ab8e...686068b`
não foi modificado nem instalado. Não houve merge, assinatura, publicação em
Pages/Store, certificação ou convite de testadores.
