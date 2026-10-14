# Novo candidato Store — identidade visual e privacidade offline

Revisão: 14/10/2026. Branch `chore/store-finalization`, dependente do PR #11 e dos
PRs #6–#10. Auditoria original do PR #9 preservada. Não há merge, alteração da main,
publicação Store, envio para certificação ou mudança no licenciamento.

## Correções e evidências reproduzíveis

- `assets/branding/`: quatro originais do ZIP aprovado, hashes SHA-256 e matriz
  1080×1080. Originais opacos: não se remove o fundo branco. Sem IA ou arte substituta.
- `distribution/icon.py`, `build.py`, `branding.py`, `msix.py`, `poc.spec` e
  `poc.py`: ICO 16–256, janela Qt e 32 recursos MSIX de escala/targetsize derivados
  da mesma matriz. Verificação do original incluído, runtime ICO, assets **extraídos
  do MSIX** e seis recursos RT_ICON efetivamente embutidos no EXE. Relatório
  `evidence/msix/branding.json` no artefato; não confundir com inspeção visual instalada.
- `scripts/capture_store_windows.py`: futuras capturas usam a marca aprovada.
  As capturas anteriores permanecem históricas e não foram retocadas/montadas.
- `docs/privacy/offline/`: política Markdown/HTML/TXT revisada, procedimentos de
  90/30 dias e 12 meses, minuta de participação, hipóteses legais e fornecedores.
  Não há termos adotados, base legal escolhida ou conformidade integral declarada.
- `.github/workflows/privacy-pages.yml`: publicação da política preparada,
  exclusivamente manual e impedida enquanto o texto estiver pendente. Não executada;
  URL HTTPS pública ainda não validada. Não publica o aplicativo.
- `.github/workflows/windows-msix.yml`: pipeline de candidato sem assinatura,
  verificação de ícones incluída; integra dependências ancestrais e os recursos
  locais da política. Resultado, revisão exata e links ficam na seção de validação
  do PR e no relatório de entrega; uma descrição de pipeline não é prova de execução.

## Situação dos seis campos originais da política

| Campo original | Informação preenchida ou pendência |
|---|---|
| 1 — vigência | Será a primeira disponibilização efetiva aos testadores. Data ainda não definida: pendente |
| 2 — audiência e bases legais | Sem publicidade, perfilamento ou comercialização. Não há acesso a relatórios específicos comprovado. Base legal por finalidade continua pendente de revisão; minuta e hipóteses separadas |
| 3 — retenção restante | Decidido: controle próprio do grupo enquanto participação + até 30 dias após saída/encerramento; direitos até 12 meses após conclusão, com dados mínimos/exceções. Implementação operacional manual não comprovada |
| 4 — destinatários/transferências | Gmail, Microsoft, GitHub Actions identificados; Pages proposto. Consulta Google/Microsoft falhou no ambiente, GitHub verificado por fonte oficial. Mecanismos LGPD aplicáveis/contas/destinatários reais ainda pendentes; nenhum país de hospedagem específico inventado |
| 5 — acesso efetivo Partner Center | Redação condicional: se estatísticas agregadas forem consultadas, distribuição, problemas e melhoria. Não presume consulta ou anonimização de relatórios não inspecionados |
| 6 — URL e aviso | Aviso manual por e-mail legitimamente disponível definido. Pages preparado, não publicado; URL HTTPS sem login e data efetiva pendentes |

A política revisada continua **não publicável** enquanto houver campos obrigatórios
e operação/legalidade sem revisão. O TXT não substitui a URL exigida pela Store 10.5.1.
O pacote técnico pode ser gerado para revisão sem ser declarado pronto para submissão.

## Identidade, versão e Windows

- Name: `DelatorreCOrporation.AgroLines`; Publisher:
  `CN=43189595-B928-4D57-90A4-24300E4D4976`.
- PublisherDisplayName: `Delatorre COrporation`; produto AgroLines;
  Store ID `9NRDJ3ZTM978`.
- PFN: `DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg`, derivado e testado a partir
  de Name/Publisher (não é atributo para acrescentar ao manifesto).
- Versão mantida `1.0.0.0`, x64, revisão Store zero; mínimo Windows 11 build 22000,
  MaxVersionTested 26100. Se uma versão igual/maior já foi aceita no Partner Center,
  uma próxima revisão precisará incrementar um dos três primeiros componentes;
  não consultamos nem alteramos submissões privadas.
- Conta Individual e nome “COrporation”: explicar responsável pessoa física não
  garante aprovação. Store 10.14 exige avaliar percepção de entidade comercial e
  tipo de conta. Resolver com Microsoft sem alterar identidade unilateralmente.

## Capacidades restritas: justificativa para revisão da Store

`runFullTrust`: o ponto de entrada é Win32 `Windows.FullTrustApplication`,
`packagedClassicApp`, `mediumIL`; Python/PySide6/GIS congelados e helpers Qt não
são um aplicativo AppContainer. A documentação exige a capacidade para esse modelo.
Não implica execução administrativa nem requer reduzir SAC. Removê-la mantendo
esse ponto de entrada não é solução; migrar a AppContainer demandaria análise de
compatibilidade e autorização, sem reescrever o motor nesta tarefa.

`unvirtualizedResources`: permite a exclusão seletiva de virtualização de
`$(KnownFolder:LocalAppData)\AgroLines`, onde ficam os projetos duráveis. Não há
exclusão geral de AppData, nem do registro. `desktop/storage.py` usa o known folder
sem redirecionamento de pacote. Objetivo: projetos não tratados como dados descartáveis
do pacote; preservação real deve ser homologada por upgrade/desinstalação/reinstalação.

Alternativa a estudar: destino padrão escolhido pelo usuário fora do AppData
virtualizado, com migração, backup e verificação dos projetos existentes. Isso
altera a política de armazenamento e não foi aplicado sem autorização. Não remover
a capacidade simplesmente porque há teste SQLite passando fora da identidade MSIX.

A Microsoft avalia justificativas de capacidades restritas no Partner Center e pode
recusar a submissão. Textos acima são subsídio, não aprovação obtida. A ausência de
`internetClient` não garante falta de rede em um processo full trust; os controles
offline são de código, recursos e testes, não essa ausência no manifesto.

Fontes oficiais consultadas em 14/10/2026:

- https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/app-capability-declarations
- https://learn.microsoft.com/en-us/windows/msix/desktop/flexible-virtualization
- https://learn.microsoft.com/en-us/windows/apps/publish/store-policies (10.5 e 10.14)
- https://learn.microsoft.com/en-us/windows/msix/package/signing-package-overview

## Testes versus homologação

Suite pytest e CI qualidade cobrem autenticação/permissões preservadas no código de
desenvolvimento, precisão, projetos SQLite, originais/SRC, versões, vértices,
backup/restauração, importação e bloqueios offline. O pacote Store exclui módulos
remotos. Windows MSIX CI verifica SDK/schema, hashes, ícones, inventário nativo,
PATH limpo, GIS, mapa WebEngine e probe offline com fixtures. O runtime é congelado,
sem instalação de Python/pip/PostgreSQL no computador destinatário.

CI não comprova Windows 11 real sem esses programas preinstalados, SAC ativo,
instalação assinada pela Store, aparência do shell, rede nativa completa ou
persistência após **atualização/desinstalação real do MSIX**. Teste repetido de hash
SQLite não substitui esses ciclos. Assinatura de todos os nativos exige revisão do
inventário; não concluir que assinatura externa do MSIX aprova cada DLL/PYD.

O fluxo Store aceita o candidato não assinado para submissão e assinatura pela
Microsoft, conforme documentação oficial; não é pacote para instalação direta.
Não usamos certificado autoassinado, Developer Mode, AllowUnsigned ou modificações
de SAC/Defender. Certificação, assinatura e comportamento do pacote distribuído
dependem de ações posteriores autorizadas e bancada real.

**AINDA NÃO PRONTO PARA UPLOAD NO PARTNER CENTER**: URL e vigência pendentes,
base legal/transferências e procedimentos a revisar, tipo de conta/capacidades a
justificar e homologação real pendente. O novo MSIX é candidato técnico revisável.
