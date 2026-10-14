# Auditoria de privacidade — código atual e PRs #6, #7 e #8

Data da análise: 14/10/2026. Responsável confirmado pelo usuário: **FABRICIO JOSE
DELATORRE**, pessoa física; contato **FABRICIO.GRUPODELATORRE@GMAIL.COM**.
O usuário informou que poderá haver colaboração online opcional para testar o
produto. Não confirmou hospedagem, países, SMTP, imagens externas ou coleta de suporte.

## 1. Escopo e metodologia

Foram lidos código de desktop/core/server, entrada PyInstaller, manifesto MSIX,
configuração Compose, rotinas de segurança, diagnóstico e workflows. Foi verificada
a cadeia dos PRs pela API GitHub e por ancestralidade Git; nenhum PR foi modificado
ou mesclado durante a análise.

| PR | Commit auditado | Alteração relevante |
|---|---|---|
| [#6](https://github.com/fbdelatorre/AgroLines/pull/6) | `7edbd731998eebeb54286a09ac7b02e68f8cf98c` | PoC embutido, diagnóstico local Windows, inventário, artefatos de CI, instalador |
| [#7](https://github.com/fbdelatorre/AgroLines/pull/7) | `479fbe5d6b8c827ceb64b6ac7e425a012254e933` | Projetos SQLite, backups, cópias originais, histórico imutável, interface de licença |
| [#8](https://github.com/fbdelatorre/AgroLines/pull/8) | `714f96dda425ad21e36631f0605b803a1a92f2ea` | Canal Store local por padrão, identidade MSIX, caminho permanente, virtualização, diagnóstico de auxiliares |

#7 inclui #6; #8 inclui ambos. As funções de autenticação, compartilhamento e
geografia do servidor são herdadas das etapas anteriores e continuam no escopo.
A política descreve o estado cumulativo #8; resíduos/diagnósticos de PoCs anteriores
são indicados quando relevantes.

Foi executada uma prova funcional isolada com dados sintéticos: arquivos em pasta
temporária, SQLite em memória para a API e nenhum acesso ao banco de clientes. A
prova local bloqueia socket/DNS. Não foram lidos arquivos `.env`, credenciais ou
projetos reais. Não foram acessados servidores de produção, Partner Center ou contas
Microsoft. Não houve mudança na aplicação, no manifesto, na Store ou em proteções.

A análise **não** prova configuração de TLS/criptografia de uma implantação real,
retenção operacional, segurança de todos os componentes nativos, cookies de um
fornecedor não identificado ou práticas internas de Microsoft/Google/GitHub. Não
substitui homologação do MSIX assinado em Windows 11 real.

## 2. Inventário de dados e fluxos comprovados

Referências abaixo apontam para o código no commit cumulativo #8, por arquivo e
função/linha inicial. Um fluxo implementado não significa que já exista serviço de
produção configurado.

| ID | Dados e acesso | Destino/condição | Evidência |
|---|---|---|---|
| E01 | Nome de projeto, UUID, SRC de trabalho; nomes/UUIDs de feições | SQLite local `.agrolines`, criado/aberto pelo usuário | `core/local_projects.py:45`, `create`, `features`; `desktop/local_projects.py:99` |
| E02 | Coordenadas originais/derivadas, Z quando presente, atributos livres, medidas, relatórios de precisão e datas | Versões locais, originais e backup; metadados podem identificar pessoas/propriedades | `core/imports.py:101`; `core/geography.py:60` e `source_metadata`; `core/local_projects.py:119` |
| E03 | Nome, SHA-256 e conteúdo integral dos arquivos selecionados e sidecars SHP | `source.payload.content_base64` local; `import_sources.content` remoto quando importação online confirmada | `core/imports.py:131`; `server/geography.py:135`; `server/models.py:178` |
| E04 | Histórico de geometria/atributos, arquivos e eventos UUID | Atualização cria revisão; SQLite bloqueia UPDATE/DELETE de revisão/original; não há limpeza por prazo | `core/local_projects.py:14`, `save_geometry`, triggers |
| E05 | Cópia completa do projeto, histórico e originais | Backup SQLite e restauração para outro arquivo; não há cifra de aplicação | `core/local_projects.py:169`, `backup`, `restore`; conexão `sqlite3.connect` sem SQLCipher/chave |
| E06 | Nome, e-mail, ID e estado ativo | Servidor no cadastro; retornados ao próprio usuário e em gestão/convites conforme acesso | `server/models.py:27`; `server/auth.py:17`; `server/properties.py:205`, `invitation_json` |
| E07 | Senha em memória/trânsito para autenticação; hash Argon2 no banco | Fluxo opcional online; não há persistência de senha em texto claro no mecanismo de credenciais | `desktop/main.py:449`, `468`, `513`; `server/auth.py:43`; `server/security.py:15`, `hash_password` |
| E08 | Access/refresh tokens, expiração, origem API, usuário e resumo de farms/permissões | Estado em memória e sessão DPAPI no Windows; não inclui os projetos locais | `desktop/client.py:82`, `authenticate`, `synchronize_access`; `desktop/vault.py:11` |
| E09 | Hash de tokens, IDs de sessão, datas de validade/revogação e histórico de refresh/reset | Banco servidor; expiração não apaga a linha | `server/models.py:41`, `52`, `58`; `server/auth.py:21`, `refresh`, `reset_password` |
| E10 | IP percebido pelo servidor e e-mail usado nas tentativas | API recebe IP; buckets guardam SHA-256 de chave com IP/e-mail e contadores; logs de acesso podem conter IP | `server/auth.py:45`, `63`, `155`; `server/security.py:66`; Compose inicia Uvicorn com access log padrão |
| E11 | Propriedade/safra/operação, conta proprietária, perfis, escopos, participantes e convites | PostgreSQL/PostGIS no servidor; desktop usa HTTP API, não PG direto | `server/models.py:73`–`135`; `server/properties.py`; `server/db.py:11`; `infra/compose.yaml` |
| E12 | Geometrias, atributos, autor, datas, versões e originais | Prévia online é inicialmente local; botão Salvar faz POST com plots e sources; consultas retornam dados autorizados | `desktop/geography.py:choose_files`, `import_files`, `save`; `server/geography.py:59`, `135`, `278`, `292` |
| E13 | Autor, ação, recurso/propriedade, data/hora | Auditoria no banco; gestores consultam até 200 eventos por resposta, sem purga dos demais | `server/security.py:54`; `server/models.py:135`; `server/properties.py:396` |
| E14 | Destinatário, remetente e mensagem com código de recuperação | SMTP só se configurado; exige STARTTLS e verifica certificado; nenhuma empresa SMTP identificada no código | `server/auth.py:150`; `server/mail.py:6`; `server/config.py:16` |
| E15 | IP/requisição e, com sessão, revalidação de usuário/farms/permissões | Janela online inicia healthcheck a cada 10 segundos, antes mesmo do login; com sessão revalida acessos | `desktop/main.py:177`, `refresh`, `show_health`; `desktop/health.py:6`; `desktop/client.py:109` |
| E16 | Coordenadas e nome de feição no renderizador local | Leaflet/JS local via QWebChannel; tokens/atributos completos não são repassados ao JS de apresentação | `desktop/gis_map.py:176`; `desktop/map_assets/map.html`; `map.js` |
| E17 | IP, região/zoom de tiles e metadados HTTP | Apenas mapa online configurado; modo local passa `offline=True`, sem imagens externas; configuração por variáveis não é consentimento do titular | `desktop/gis_map.py:27`, `Requests`; `desktop/local_projects.py:123`; `desktop/geography.py:37` |
| E18 | Versões, tipo de erro/módulo, estado SAC/políticas, XML 3077/3033, caminhos, PIDs e identidade de pacote | Relatório local no modo PoC/smoke; abertura comum do canal Store retorna antes dessa coleta | `distribution/poc.py:31`, `64`, `complete`; `windows_evidence.py:35`, `54`; `package_runtime.py:15`, `60` |
| E19 | Inventário de DLL/PYD/EXE, hashes, arquiteturas, donos dos arquivos, certificados e caminhos de usuário | Ferramentas de manutenção/build; artefatos de CI. Não há envio por todos os clientes desktop | `scripts/native_inventory.py:48`; `scripts/Audit-NativeWindows.ps1`; workflows de distribuição |
| E20 | Evidências reais da bancada Windows, inclusive falhas, caminhos e eventos de sistema | Workflow manual signed-validation usa upload-artifact `if: always()`; pode transmitir metadados da bancada para GitHub | `.github/workflows/windows-msix-signed-validation.yml:20`; `windows-poc-signed.yml`; `Test-SignedMSIX.ps1` |
| E21 | ID público Store/PFN, nome legal e contato para a política | Identidade do aplicativo não é ID de hardware. Contato Gmail é informação confirmada; mensagens de privacidade passam pela Google | `distribution/windows/msix/identity.json`; confirmação do usuário nesta conversa |
| E22 | ID da própria conta copiado para área de transferência | Ação explícita de copiar; Windows/outras ferramentas de clipboard podem ter comportamento próprio | `desktop/main.py:533`; sem integração própria de nuvem de clipboard |

Nomes, coordenadas e UUIDs não são automaticamente anônimos. O identificador do
projeto, o hash de arquivo ou o resumo de IP podem ser associados a outras informações.
Base64 é codificação reversível, não criptografia nem anonimização.

## 3. Conexões e terceiros: o que existe e o que não se pode presumir

- **API configurável:** `AGROLINES_API_URL`; padrão de desenvolvimento loopback.
  Cliente exige HTTPS fora de loopback, envia Bearer e JSON ao serviço. A abertura
  normal Store/local não instancia ApiClient; abrir Colaboração online o faz.
- **Healthcheck:** usa `urllib.request.urlopen`, que aceita redirecionamentos padrão.
  A regra `NoRedirect` do cliente autenticado não cobre esse healthcheck. Um endpoint
  que redirecione pode gerar conexão com outro host; não contém Bearer nesse fluxo,
  mas revela metadados de conexão. Verificar destinos reais antes dos testes.
- **PostgreSQL/PostGIS:** ligação é do servidor. `create_engine` não impõe `sslmode`
  ou criptografia de disco; configuração SecretStr reduz exposição acidental da URL,
  mas não comprova segurança/criptografia da implantação. Compose usa rede interna,
  volume persistente e API em loopback; não identifica hospedagem comercial.
- **SMTP:** nome de host configurável, não fixado em fornecedor. Não presumir Gmail
  para recuperação só porque o contato de privacidade informado é Gmail.
- **Tiles:** provedor não identificado. Configuração exige HTTPS/licença/atribuição e
  flag de autorização, mas não apresenta uma tela de consentimento de privacidade.
  URL pode conter parâmetros de API; cabe analisar fornecedor/configuração real.
  Pedidos z/x/y permitem inferir região e zoom sem envio de todo o polígono. O perfil
  off-the-record/NoCache não é um bloqueio de todos os cookies temporários.
- **Bibliotecas:** nenhuma integração de analytics/crash-reporting publicitário foi
  encontrada nos módulos próprios pesquisados. Não se auditou todo código de Qt,
  Chromium/GDAL/PROJ nem o tráfego nativo em Windows real; ausência de SDK próprio
  não equivale a prova de que Windows/Store ou bibliotecas nunca fazem rede.
- **Build/manutenção:** DigiCert timestamp nos scripts de assinatura e Azure Retail
  Prices em `distribution/costs.py` são fluxos de manutenção. Não são envio dos
  projetos agrícolas pelo aplicativo comum. GitHub Actions armazena artefatos de
  builds e pode receber evidências de bancada real no workflow manual.
- **Store/Windows:** distribuição e diagnósticos de plataforma seguem mecanismos
  Microsoft não auditados aqui. Partner Center pode disponibilizar informações ao
  desenvolvedor; confirmar uso de audiência privada/analytics do painel, em vez de
  afirmar que o desenvolvedor nunca recebe nenhuma informação da plataforma.
- **Contato Gmail:** mensagens de privacidade/suporte enviadas ao endereço confirmado
  são recebidas por serviço Google. Não foram comprovados países de processamento,
  ferramentas de suporte ou política de exclusão dessa caixa.

## 4. Retenção, exclusão e exposição a destinatários

### 4.1 Projetos e backups

SQLite guarda versões/originais sem cifra de aplicação. Não há remoção de feição,
atributo histórico ou projeto via interface; usuário pode apagar arquivos externamente
após fechar o projeto. Triggers impedem editar/excluir revisões e fontes. Isso protege
o histórico, mas exige procedimento de correção/exclusão de dados pessoais, sem
prometer que uma edição apaga o que havia antes. Exclusão de arquivo não comprova
apagamento forense e não atinge backups ou arquivos em programas externos.

O conteúdo original é integral: GPKG/GeoJSON/KMZ podem incluir metadados não exibidos.
Mesmo eliminando um campo da visualização, a cópia original do arquivo pode reter esse
campo. Backup/restauração mantêm histórico e originais. Não existe expiração automática
para esses arquivos.

### 4.2 Conta, autorização e dados do servidor

As únicas rotas DELETE encontradas em auth/properties revogam sessões e permissões.
Não existe DELETE de conta/farm/plot/histórico/original nem purga programada de
sessions, refresh_tokens, password_resets, invitations, rate_buckets ou audit_events.
Atualizar nomes é possível em alguns recursos; alterar e-mail e eliminação completa
exigem procedimento externo que ainda não foi especificado.

| Mecanismo | Valor no código | O que não implica |
|---|---|---|
| Access token | Padrão 900 s, configurável em Settings | Não é prazo de exclusão de conta/sessão |
| Refresh/session | Padrão 86400 s, configurável | Não apaga refresh histórico ou DPAPI automaticamente |
| Cache de resumo de farms | Até 900 s e limitado pela expiração do access token | Não remove cópias obtidas fora desse cache |
| Código de recuperação | 900 s; pode ser marcado usado | Não apaga registro de reset |
| Convite | 7 dias de validade; status expirado calculado | Não elimina convite/scopes |
| Tentativas/rate buckets | Janela configurável, padrões 900 s em login | Não é anonimização ou rotina de purga |
| Auditoria GET | Limite 200 registros por resposta | Não é retenção de 200 registros no banco |

A conta/registro continua existindo após logout, reset de senha ou revogação. O
cliente limpa DPAPI no logout, mas sem rede não confirma revogação remota. No encerramento
normal da janela, a sessão persistente não é apagada como se fosse logout.

### 4.3 Compartilhamento e cópias

`server/geography.original_source` exige leitura da propriedade inteira, **não** a ação
`export`. Um viewer com essa leitura pode obter o arquivo completo, mesmo que `ACTIONS`
não inclua export para viewer e não haja botão de exportação GIS na interface. Limitações
de escopo são verificadas, mas não impedem cópia por destinatário autorizado.

`members` revela nome/e-mail/ID a gestores; convites revelam participantes conforme
acesso. Revogação remove Permission e bloqueia requisições seguintes, preservando
geometrias, originais e auditoria. Não há apagamento remoto de arquivos que outro usuário
salvou. `exporters/README.md` declara adaptadores futuros; não existe exportador
operacional de planos/formatos de monitores. A ação export no modelo de permissões
não comprova um botão/exportador implementado. Cópias SQLite/backup e obtenção de
originais/JSON da API são os meios atuais de movimentação de informações. Projetos locais próprios são separados de dados compartilhados; não existe
sincronização bidirecional implementada ou propagação de exclusão.

### 4.4 Atualização e desinstalação

No #8, KnownFolder `KF_FLAG_NO_PACKAGE_REDIRECTION` resolve `%LOCALAPPDATA%\AgroLines`.
O manifesto exclui somente essa pasta da virtualização, com capacidade restrita
`unvirtualizedResources`; os projetos ficam em Projects, DPAPI na raiz, relatórios em
Evidence. A exclusão pretende manter **também sessão/relatórios**, não só geometrias.
O Inno do #6 remove arquivos de instalação e não tem rotina de descarte desses dados;
PoCs antigos podem deixar a pasta AgroLinesDistributionPoC/evidence.

A preservação MSIX efetiva após upgrade/uninstall não foi homologada com pacote
assinado/SAC; o teste do #8 que passou no CI é de **pacote extraído**, schema/hashes e
runtime. Não transformar a intenção do manifesto em uma garantia já validada.
Desinstalar não chama DELETE de conta nem encerra necessariamente a sessão remota.

## 5. Logs, diagnóstico e possíveis excessos

O desktop normal Store usa o ramo local que retorna antes de `report/collect`. O
PoC não-Store/smoke consulta políticas Windows, log 3077/3033, versões, arquivos e
processos. `classify_events` marca associação, mas conserva **todos** os eventos do
intervalo consultado, incluindo `associated_with_payload=False`, como XML integral.
Isso pode incluir Computer, Security/UserID, nomes de conta/pastas, programas não
relacionados e informação corporativa. Não há anonimização/redação antes do upload
no workflow manual. Process snapshot lê entradas de todos os processos em memória;
a saída de auxiliares filtra descendentes Qt.

O app não implementa autoenvio de erro/telemetria. O workflow de manutenção envia
artefatos automaticamente **depois de acionado**, inclusive em falhas. Publicidade,
Sentry/Google Analytics, coleta de contatos/câmera/microfone, fingerprint de hardware
para licença e pagamentos não foram encontrados nos módulos próprios. A licença
atual DevelopmentLicense é local e não faz heartbeat. Isso não é prova de ausência de
dados pessoais incidentais em XML de sistema ou de serviços do Windows.

Servidor: auditoria persistente e Uvicorn access/error logs são distintos. A validação
422 remove o campo input para não repetir segredo; recuperação SMTP registra mensagem
genérica sem token/e-mail. Ainda assim, não existe configuração abrangente de redação
ou retenção de logs. Exceções de infraestrutura/SQLAlchemy e reverse proxy podem conter
parâmetros/contexto pessoais; `make_engine` não usa `hide_parameters=True`. Isso é risco
a avaliar na implantação, **não afirmação de vazamento de senha observado**.

## 6. Provas funcionais e reprodutibilidade

Resultado em [evidence/findings.json](evidence/findings.json): **12 constatações
esperadas confirmadas**, mais o indicador geral. Os achados problemáticos são resultados
de auditoria, não critérios de aprovação de privacidade.

- Contato sintético legível no SQLite e no backup, cabeçalho SQLite comum;
- Metadado sintético não exibido no mapa conservado no arquivo original;
- Contato/histórico da revisão anterior preservado; DELETE de revisão recusado;
- Viewer de propriedade inteira obteve original com esse metadado;
- Revogação bloqueou a requisição seguinte, mas manteve histórico no banco;
- DELETE `/auth/me` respondeu 405; logout preservou a conta.

Reprodução em checkout de desenvolvimento com dependências instaladas:

```text
python -m docs.privacy.evidence.reproduce_audit
```

[Script](evidence/reproduce_audit.py) usa apenas fixtures próprias, SQLite temporário/em
memória e TestClient interno; não necessita do banco PostgreSQL de clientes. Exibe somente
constatações booleanas, não tokens, senhas ou hashes de credenciais.

Foram também executados os testes existentes de auth, mail, sessão, projetos e MSIX:
**41 aprovados e 1 ignorado** no executor Linux.
A prova DPAPI nativa requer Windows e é distinguida como ignorada no executor Linux.
Esse conjunto confirma comportamento no ambiente de desenvolvimento, não atendimento
operacional da LGPD ou aceitação física do MSIX.

## 7. Normas aplicáveis e limites da conclusão

Referência LGPD: Lei 13.709/2018, especialmente arts. 5º/6º (conceitos/princípios),
7º/11 (hipóteses legais), 9º (transparência), 14 (menores), 15/16 (término/conservação),
18/19/20 (direitos), 33 (transferência), 46/48 (segurança/incidentes). Pessoa física que
atua fora da exceção estritamente particular e não econômica do art. 4º não ganha uma
isenção automática por usar conta Individual de desenvolvedor. Nenhuma base legal,
prazo de retenção ou país de hospedagem pode ser deduzido só de um hash ou biblioteca.

Foram consultadas as [políticas atuais da Microsoft Store](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies)
na data da auditoria:

| Cláusula | Requisito observado | Efeito no AgroLines |
|---|---|---|
| 10.5.1 | Política para acesso/coleta/transmissão, URL no Partner Center; Win32/Desktop Bridge sempre requer política | Vale mesmo para operação local/private testers; informar práticas atuais, controles e destinatários |
| 10.5.2 | Publicação de informação pessoal em serviço externo/terceiro exige opt-in expresso na UI, descrição prévia e opt-out na UI | Revisar compartilhamento, tiles e fluxos de relatório; configuração de licença de tiles não é consentimento |
| 10.5.3 | Informação de não cliente publicada ou disponibilizada a outro cliente exige consentimento expresso escrito e retirada | Atributos/originais podem ter dados de terceiros; estabelecer fluxo/limites antes de compartilhar dados reais |
| 10.5.4 | Coleta/armazenamento/transmissão segura com criptografia moderna | Argon2/DPAPI/HTTPS comprovam partes; SQLite e backups sem cifra de aplicação e infraestrutura desconhecida não autorizam declaração geral de conformidade |
| 10.5.5 | Dados altamente sensíveis devem ser relacionados à funcionalidade, com consentimento expresso | Não há filtro desses dados nos atributos/originais; minimizar fixtures e tratamento de arquivos |
| 10.5.7 | Localização do dispositivo e controles correspondentes | Não há API de localização do dispositivo; coordenadas de arquivos ainda podem ser informação pessoal |
| 10.5.8 | Leis de privacidade de menores | Idade do grupo/autorizações não confirmadas |
| 10.14 | Conta Company quando nome do app/publicador aparenta entidade comercial, entre outras situações | Conta Individual informada e “Delatorre COrporation” exigem avaliação do responsável/Microsoft; não inventar CNPJ nem alterar identidade por conta própria |

Não se conclui que uma política escrita, um grupo privado ou aprovação de schema
MakeAppx resolvam esses requisitos. A conclusão é **minuta fundamentada + pendências
materiais**: divulgação final depende de confirmações e, em certos fluxos, controles
operacionais/técnicos adicionais.

Referências normativas para revisão do responsável:
[LGPD — texto oficial](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm),
[ANPD](https://www.gov.br/anpd/pt-br),
[Microsoft Privacy](https://www.microsoft.com/pt-br/privacy/privacystatement),
[GitHub Privacy](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement),
[Google Privacy](https://policies.google.com/privacy?hl=pt-BR).
O ambiente não permitiu obter diretamente as páginas governamentais/Microsoft Privacy;
isso não deve ser apresentado como consulta atualizada desses documentos. Não foi
verificada a regulamentação específica ou contrato aplicável a um fornecedor não informado.
