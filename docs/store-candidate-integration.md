# AgroLines — integração técnica candidata à Microsoft Store

Auditoria de 14/10/2026, horário de Brasília. Branch `integration/store-candidate`,
criada de `origin/main` (`a7af60408fbd85105d58696386a0b985668b4bb9`).
**Candidato técnico: não é aprovação jurídica, certificação ou homologação SAC.**
Registro detalhado de heads, arquivos alterados e checks: [pr-audit.json](store-candidate/pr-audit.json).
Resultados do novo build ficam em `evidence/msix/candidate.json` no artefato da execução.

## Auditoria dos PRs e consolidação

Todos abertos, sem alteração de bases ou branches originais. “CI” abaixo é o estado
observado no head auditado, não teste de instalação Windows 11 com SAC ativo.

| PR / head abreviado | Base | Estado | Arquivos alterados | CI observado / função incorporada |
|---|---|---|---:|---|
| #6 / 7edbd73 | fix/windows-smart-app-control (#5) | Aberto, draft | 26 | Checks bem-sucedidos; uma execução PoC antiga cancelada deixa estado UNSTABLE. Executável/runtime e instalador PoC |
| #7 / 479fbe5 | feat/windows-distribution-poc (#6) | Aberto, draft | 17 | Sucesso; projetos locais e interfaces de licenciamento |
| #8 / 714f96d | feat/offline-projects-licensing (#7) | Aberto, draft | 21 | Sucesso; MSIX/identidade oficial |
| #9 / b3bbc07 | feat/microsoft-store-msix (#8) | Aberto, draft | 14 | Sucesso; auditoria de privacidade, preservada |
| #10 / a83aa46 | docs/privacy-policy-audit (#9) | Aberto, draft | 23 | Sucesso; pacote Store offline-only e caminhos locais |
| #11 / c10d7f4 | feat/store-offline-only (#10) | Aberto, draft | 22 | Sucesso; capturas reais históricas e interface localizada |
| #12 / 2357eb4 | chore/store-screenshots (#11) | Aberto | 38 | Sucesso; arte oficial, política offline e plano operacional 18+ |
| #13 / 8f0bf91 | chore/store-finalization (#12) | Aberto | 25 | Sucesso; publicação Pages preparada/bloqueada e verificações documentais |

PRs #4/#5, ainda abertos, são dependências ancestrais do #6: mapa/precisão e auditoria
Windows. Foram preservados junto com seus commits. Integração sequencial por merges
`--no-ff` dos heads #6 → #13 na branch nova, **sem conflitos**. Todos os oito heads
são ancestrais, sem rebase, squash ou force-push. A árvore inicial consolidada era
idêntica ao head #13; não houve duplicação dos arquivos.

O #13 recebeu atualizações do #12 por cherry-pick e não continha o head atual do
#12 como ancestral. O merge reconcilia os dois históricos; versões finais iguais
dos documentos comuns foram mantidas. A integração da main atual também preserva
os commits de merge já existentes nela, que não eram ancestrais da cadeia original.
Nenhuma funcionalidade foi reconstruída ou sobrescrita manualmente.

## Funcionalidades e limites do candidato

- Entrada Store `distribution/store.py` e runtime hook fixam offline-only antes
  de inicializar a UI. Variável de ambiente/preferência não habilita colaboração.
  Módulos de API/login remoto/convites/DPAPI são excluídos do payload; continuam no
  código de desenvolvimento para versões futuras. Não há telemetria/SMTP próprios.
- `core/local_projects.py` e `desktop/local_projects.py`: SQLite `.agrolines`,
  criação/reabertura, originais/SRC, geometrias versionadas, edição numérica de
  vértices com desfazer/refazer e backup/restauração. Interface em português.
- `core/imports.py`: importação de polígonos por SHP, GPKG, KML, KMZ e GeoJSON.
  Essa matriz não é promessa de importar toda geometria/driver GIS ou de exportar
  todos esses formatos; não foram implementados novos algoritmos ou exportadores.
- Leaflet, mapa, CSS/JS e recursos Qt/GIS são locais; PROJ online e referências
  externas são bloqueados. Testes/probes verificam caminhos, imports e tentativas
  JS/HTTP; captura completa de TCP/UDP/DNS dos helpers continua pendente.
- O usuário usa runtime embutido e SQLite, sem instalar Python, pip ou PostgreSQL.
  Python/pip são ferramentas do builder. Execução extraída com PATH System32 e sem
  variáveis Python/GIS é evidência do runtime; runner com Python instalado não
  substitui máquina limpa Windows 11 nem instalação sob identidade MSIX.

## Ajustes técnicos da integração

1. `distribution/windows/poc.spec` inclui apenas as três cópias da política
   (HTML/MD/TXT) com bytes preservados. Antes incluía todo o diretório, expondo
   análises internas e modelos operacionais no pacote. Nenhum registro real foi
   introduzido; documentos internos permanecem no repositório para revisão.
2. `distribution/candidate.py` inspeciona **o arquivo MSIX gerado**: identidade,
   versão/x64/Windows, capacidades, ausência de assinatura externa, runtime/nativos,
   banco PROJ e recursos/mapa/WebEngine/locales; compara os três arquivos da política
   com a fonte e rejeita documentos extras. Correlaciona probes congelados e auditoria
   PE, calcula SHA-256 e registra revisão/run sem aprovação inferida.
3. `windows-msix.yml` exige testes Windows/lint antes de empacotar. O probe offline
   agora também usa o helper com PATH System32 e variáveis Python/GIS removidas;
   timeout termina sua árvore de processos. Não instala MSIX ou certificados.
4. No CI dessa branch/PR, jobs PostgreSQL e instalador PoC legado são explicitamente
   omitidos: não se instala/inicia PostgreSQL e não se testa instalador não assinado.
   Jobs e testes de servidor permanecem disponíveis nas demais branches; testes de
   autenticação/permissões em SQLite e todo pytest Windows continuam executados.

Não foram modificados motor/precisão, bancos existentes, política jurídica,
classificação, audiência/grupo, identidade, licenciamento ou proteções Windows.
Pages só possui gatilho manual, confirmação/hash e recusa dos campos pendentes;
não foi executado. Não convidamos testadores nem enviamos dados reais ao CI.

## Manifesto e capacidades restritas

Identidade exata: `DelatorreCOrporation.AgroLines`, publisher
`CN=43189595-B928-4D57-90A4-24300E4D4976`, Store ID `9NRDJ3ZTM978` e PFN
`DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg`. Nome do publicador:
`Delatorre COrporation`. Versão **1.0.0.0**, x64, Windows.Desktop mínimo
**10.0.22000.0**, MaxVersionTested **10.0.26100.0**. Store ID vem da configuração,
não é atributo a inventar no XML; PFN é derivado da identidade.

- `runFullTrust`: necessária ao ponto de entrada Win32
  `Windows.FullTrustApplication`, packagedClassicApp/mediumIL e helpers Qt/nativos.
  Não significa elevação administrativa nem exceção ao SAC.
- `unvirtualizedResources`: habilita exclusão **somente** de
  `$(KnownFolder:LocalAppData)\AgroLines`; projetos precisam permanecer fora dos
  dados descartáveis do pacote. `desktop/storage.py` usa known folder sem redireção
  de pacote. Necessidade/justificativa devem ser avaliadas pela Microsoft; intenção
  do manifesto não comprova persistência em upgrade/desinstalação.

Não remover capacidades sem alterar/testar o modelo de execução/armazenamento e
preservar projetos existentes. Não há exclusão ampla de AppData ou registro.
Ausência de `internetClient` não impede rede de processo full trust: dependemos dos
controles de código e homologação nativa. Fontes oficiais para revisão:

- https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/app-capability-declarations
- https://learn.microsoft.com/en-us/windows/msix/desktop/flexible-virtualization
- https://learn.microsoft.com/en-us/windows/apps/publish/store-policies
- https://learn.microsoft.com/en-us/windows/msix/package/signing-package-overview

## Artefato e pendências de homologação

Validação local da revisão integrada: **145 testes passaram, 1 skip DPAPI Windows,
1 teste WebEngine desmarcado e 9 testes de telas Qt fora da coleta**. Ruff lint e
formatação (99 arquivos), `pip check` e `git diff --check` passaram; relatório de
precisão **22/22 referências computacionais**, sem precisão absoluta em campo atestada.
Dois ensaios mais amplos abortaram ao inicializar Qt neste Linux: sandbox SUID do
Chromium não configurado e, no ensaio sem módulos que fixam QPA, backend gráfico
indisponível. A seleção local passou com `QT_QPA_PLATFORM=offscreen`, sem desativar
sandbox; testes completos ficam a cargo do Windows. Não são testes de aparência.

Workflow: `.github/workflows/windows-msix.yml` (somente build/testes; contents read).
Artefato: `agrolines-official-store-msix-UNSIGNED-submission-candidate`.
Arquivo: `dist/msix/AgroLines-1.0.0.0-x64-STORE-SUBMISSION-UNSIGNED.msix`.
Links, hash, source SHA, versões, contagens de assinatura e resultados efetivos
serão registrados no relatório da execução/PR após a conclusão; não inferir sucesso
apenas pela existência do workflow ou de upload `if: always()`.

O candidato é **não assinado**, destinado à revisão e eventual fluxo da Microsoft
Store, que assina os pacotes aprovados. Não instalar diretamente, usar certificado
autoassinado, AllowUnsigned, Developer Mode, exclusões ou reduzir proteções.
Não há evidência de SAC aprovado: inclusive DLLs/PYDs sem assinatura/cadeia precisam
de revisão; assinatura externa do MSIX não comprova aceitação individual de cada nativo.

Continuam pendentes: instalação real pela Store com SAC On/Defender ativo, Qt/helpers
sob identidade, rede nativa/DNS/UDP, operação fisicamente offline em Windows sem
Python/PostgreSQL, atualização/desinstalação/reinstalação com projetos preservados,
obrigações de redistribuição de terceiros e justificativa das capacidades/conta
Individual. Política continua incompleta quanto a bases/transferências, vigência,
URL e controles manuais; nenhum texto foi marcado aprovado. Confirmar no painel se
versão 1.0.0.0 ainda é aceitável; se igual/maior já aceita, incrementar os componentes
permitidos antes de submissão. Não consultamos/alteramos submissões particulares.

Roteiro: [Windows 11 real](store-candidate/homologacao-windows11.md).
Dependem de autorização: merge/integrar main, publicar política e testar URL pública,
submeter/certificar/distribuir pacote pela Store e qualquer convite aos testadores.
Revisão jurídica/operacional e acesso a bancada Windows real são pré-requisitos
adicionais, não permissões inferidas deste build.
