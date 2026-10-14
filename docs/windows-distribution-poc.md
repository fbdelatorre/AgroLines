# Prova de distribuição Windows e proposta comercial

## Estado de aprovação

**Prova ainda não aprovada para Smart App Control.** O build interno sem assinatura
serve para validar empacotamento no CI. Não é um instalador para clientes, não deve
ser publicado como release comercial e provavelmente será bloqueado pelo SAC.
Não se modifica a proteção para executá-lo. A assinatura e a execução real com a
proteção ativa são pré-requisitos da aprovação, não tarefas substituídas pelo CI.

Esta prova mantém CPython 3.12/PySide6, NumPy/GEOS/GDAL/PROJ e o núcleo AgroLines.
Não inicia novas ferramentas agrícolas, não altera o banco ou exige PostgreSQL
no cliente. O relato “3.11” não foi usado para mudar silenciosamente a versão do
Python; a prova embute CPython 3.12.10 e registra o runtime efetivamente usado.
Fabricante jurídico, certificado/serviço de assinatura e máquina de homologação
continuam pendentes de configuração. A identidade provisória aparece claramente
no executável/instalador, nunca como fabricante comercial verificado.

## O que a prova executa

`AgroLinesPoC.exe` é um aplicativo GUI Windows x64 com ícone, versão PE e fabricante
parametrizado. O pacote PyInstaller **onedir**, sem UPX/strip, embute Python e todas
as dependências. O usuário abre um atalho, sem Python/pip/PowerShell instalado.
O instalador Inno Setup permite instalação por usuário, atualização por novo
instalador e desinstalação pelo Windows; o desinstalador fica fora do payload do
runtime. Seu AppId é exclusivo da prova, separado do futuro produto comercial.

A GUI verifica operações reais: array NumPy, distância GEOS, controle independente
WGS84/UTM via PROJ, escrita/leitura SHP com Fiona/GDAL, importação pelo núcleo,
edição de 1 mm/undo e as mesmas 22 referências numéricas. O mapa Leaflet usa o
componente Qt WebEngine existente, com sandbox Windows ativo. Não há algoritmos
agrícolas novos nem substituição de bibliotecas para evitar bloqueios.

Os recursos e PE do payload são identificados por SHA-256. A auditoria usa apenas
o conteúdo do pacote, evitando confundir ferramentas instaladas no builder com
bibliotecas distribuídas. O manifesto verifica corrupção/modificação/inclusão de
arquivos; **não é um manifesto autenticado ou atualizador remoto**. A segurança
final requer assinatura confiável dos PE e instalador e validação do pacote exato.

A GUI coleta evidências por APIs/tools Windows somente leitura, sem PowerShell,
via `CiTool`/`wevtutil` dos diretórios do sistema. Registra SAC, 3077/3033, versões,
checks e integridade. Ausência de permissão, estado desconhecido, canal desativado
ou query saturada significam evidência incompleta, nunca aprovação. Não pede
privilégios elevados nem muda registro, certificados, Defender, WDAC ou logs.
O botão abre a pasta `%LOCALAPPDATA%\AgroLinesDistributionPoC\evidence`.
Erros iniciais geram evidência limitada e mensagem Win32 sem registrar senhas.

`checks_passed` confirma testes funcionais. `sac_run_observed` registra observação
quando SAC e eventos puderam ser confirmados. `approved_for_distribution` e
`sac_compatibility_proven` permanecem falsos: instalação, assinaturas, origem do
artefato, todos os processos e revisão externa precisam ser avaliados conjuntamente.
Metas computacionais não comprovam exatidão absoluta no terreno.

## Build e assinatura (mantenedores)

Os comandos de manutenção abaixo não são requisitos do cliente final.

1. Builder Windows x64 com CPython 3.12.10, Windows SDK/SignTool e Inno Setup 6.
2. Ambiente isolado: `python -m venv build-env` e instalação de
   `distribution/windows/requirements.lock` usando `pip --require-hashes
   --only-binary=:all:`. O lock fixa versões e hashes de todas as dependências da
   prova; compilação não substitui bibliotecas por código aproximado.
3. Executar `python -m distribution.build --version 0.1.0.1 --manufacturer "Nome jurídico"`
   no ambiente isolado. PyInstaller gera `dist/AgroLinesPoC`; ícone e PE têm a mesma
   versão/fabricante do instalador. Avisos/licenças são coletados do ambiente.
4. Auditar payload com `python -m distribution.payload --root dist/AgroLinesPoC
   --output evidence/native-inventory.json` e `scripts/Audit-NativeWindows.ps1`.
5. No builder confiável, usar `Sign-Payload.ps1` com certificado de code signing
   público já disponível no certificate store, thumbprint e Subject esperado.
   Não enviar/exportar PFX ou chave privada no repositório/chat. Preserva assinaturas
   Authenticode upstream válidas, assina PE não assinados, recusa assinaturas inválidas
   ou dependência de catálogo não implantado e verifica todos com SignTool `/pa /all`.
   Timestamp verifica a assinatura em seu contexto; a cadeia atual isolada do relatório
   de diagnóstico não substitui WinVerifyTrust/SignTool para assinaturas antigas válidas.
6. Gerar `payload-manifest.json` **depois** de assinar componentes. Compilar com
   `Build-Installer.ps1 -CertificateThumbprint ...`; o callback Inno assina também
   o desinstalador embutido e o instalador final. Sem certificado, o compilador gera
   somente artefato interno explicitamente não assinado.
7. Conferir assinaturas e hashes após assinatura do instalador. Não alterar arquivos
   após essa etapa. Conferir também módulos de sistema/CRT e plugins realmente
   carregados; diretórios/metadados não resolvem todo o grafo de imports PE.

A coleta de notices não fecha obrigações LGPL, fontes/relinking Qt/GEOS, avisos
Chromium, redistribuição do runtime MSVC ou licença/EULA do AgroLines. Essa revisão
é requisito de release comercial; o pipeline não fornece aprovação jurídica.

## Pipeline e aceitação obrigatória em máquina real

`windows-distribution-poc.yml` constrói runtime, audita bytes distribuídos, instala,
abre o executável frozen com PATH apenas do sistema e sem configuração Python/GIS
do builder, verifica precisão/mapa/integridade e desinstala. Constrói
0.1.0.2 e exercita upgrade 0.1.0.1→0.1.0.2. Confirma conservação de evidências fora
do diretório de instalação. Runners Windows hospedados são teste de empacotamento,
**não homologação Windows 11/SAC**. Hashes e relatórios são artifacts internos.

`windows-poc-signed.yml` é disparado somente por mantenedor (`workflow_dispatch`),
sem execução automática de código de forks/PRs em runners privados. Usa ambientes
protegidos `windows-signing` e `windows-sac-acceptance` e dois runners dedicados:

- `agrolines-signing`: builder confiável, certificado com chave não exportada e
  configuração pública `AGROLINES_MANUFACTURER`, `AGROLINES_SIGNING_THUMBPRINT`,
  `AGROLINES_SIGNER_SUBJECT`. Identidade ou certificado ausentes interrompem o job.
- `agrolines-windows11-sac`: Windows 11 cliente real/VM equivalente, SAC **Ativado**,
  política em enforcement, Defender/WDAC sem exceções adicionais. Não precisa de
  Python/pip para instalar/executar o artefato; PowerShell é apenas a ferramenta de
  automação dos mantenedores. Não chamar um runner Windows Server de Windows 11.

O segundo runner instala o **mesmo instalador assinado**, verifica assinaturas dos
PE instalados (incluindo desinstalador), executa o aplicativo embutido e consulta
3077/3033. Sem SAC comprovado, query ilegível, assinatura inválida, bloqueio ou
falha funcional, o teste não aprova. Não usa certificado autoassinado, exclusões,
atalhos de carregamento ou flags para reduzir proteções.

Checklist de homologação humana, além do job:

1. Imagem limpa Windows 11/SAC ativo; registrar edição/build, políticas e captura
   Segurança do Windows. Registrar fabricante e SHA-256 do instalador final.
2. Download pelo canal previsto, fabricante verificado e instalação sem Python
   preexistente/PowerShell/pip/banco local configurado pelo cliente.
3. Primeira execução pelo atalho: cinco bibliotecas carregadas, mapa visível,
   referências e edições numéricas válidas; conferir os processos filhos Qt.
4. Revisar eventos desde antes da instalação até após execução/desinstalação,
   inclusive DLLs cujo nome não esteja no inventário principal. Coleta limitada ou
   sem permissão impede aprovação; não limpar o histórico para produzir “zero”.
5. Atualização de candidato assinado anterior, recusa de pacote adulterado e
   preservação de dados; interromper atualização para avaliar recuperação. O CI de
   upgrade interno ainda **não prova** atualização remota autenticada/atômica.
6. Desinstalação assinada e preservação dos dados definidos pela política do produto.
7. Revisor registra os hashes/evidências e decisão. Promover somente os mesmos bytes
   aprovados; rebuild, mudança de certificado/biblioteca ou empacotador exige nova prova.

Não há máquina equivalente ou certificado configurado nesta sessão. O pipeline
real é entregue preparado; sua execução e revisão continuam pendentes. A prova
não se declara aprovada apenas por CI verde.

## Comparação de distribuição, requisitos e custos

MSIX, Store e Artifact Signing não são três substitutos equivalentes: MSIX é o
formato/implantação, Store é um canal e Artifact Signing é um serviço de assinatura.

| Opção | Requisitos e vantagens | Limitações para AgroLines | Custos e verificação |
|---|---|---|---|
| Inno + executável frozen (primeira prova técnica) | Runtime embutido; controle do payload, assinatura do instalador/desinstalador e PE; canal próprio; mantém a GUI Win32 | Atualizador autenticado/atômico precisa ser projetado; instalação per-user não isola dados como AppContainer; reputação e SAC precisam ser testados | Ferramentas abertas; certificado público/hardware ou serviço, CI, hospedagem e suporte têm custos. Cotação CA depende da entidade e fornecedor, não foi inventada nesta prova. |
| MSIX assinado, fora da Store | Identidade estável e Publisher compatível com certificado; implantação gerenciada, integridade e updates por App Installer; uninstall do pacote pelo Windows | Adaptar caminhos/dados, full-trust desktop/capabilities e processo QtWebEngine; conferir perda/retenção de dados e plugins; MSIX não prova aceitação de cada DLL/PYD pelo SAC | Ferramentas Windows SDK; assinatura, hosting e testes. MSIX não é assinatura gratuita ou licença de distribuição. |
| Microsoft Store (preferencial para avaliar a distribuição pública) | Partner Center, identidade verificada, requisitos/certificação Store; canal confiável e updates gerenciados; avaliar MSIX vs listagem de instalador Win32 | Certificação, países, identidade/pagamentos; listagem EXE/MSI ainda exige installer hospedado/assinado conforme requisitos. Não presumir que Store assina todas as DLLs do instalador tradicional | A página atual Microsoft consultada informa **sem taxa de registro para Individual e Company** no novo onboarding. Custos de desenvolvimento, assinatura externa quando aplicável, hospedagem e comissões/pagamentos dependem do modelo e termos; confirmar antes de comercializar. |
| Microsoft Artifact Signing Public Trust | Azure **pago**, validação de identidade elegível, account/profile, RBAC/OIDC e timestamps; chave gerenciada HSM; pode atender Inno ou MSIX | Elegibilidade do fabricante é distinta da região do recurso. Public Trust não lista Brasil para organizações nem indivíduos; Private Trust/Test não substituem confiança pública em máquinas de clientes | API pública oficial consultada pelo CI: **Basic US$ 9,99/mês**, **Premium US$ 99,99/mês**, Global/USD; franquias, excedentes, impostos e oferta devem ser confirmados na tabela/calculadora. Volume de PE por build influencia o custo. Não comprar assinatura ou criar recursos pagos nesta prova. |

**Elegibilidade atual Artifact Signing:** organizações nos EUA, Canadá, UE, Reino
Unido, Austrália, Nova Zelândia, Japão, Coreia do Sul, Singapura, Suíça, Noruega e
Israel; indivíduos EUA/Canadá. Brazil South aparece como região de serviço, mas isso
não inclui pessoa/empresa brasileira na elegibilidade Public Trust. Se o fabricante
for brasileiro, avaliar certificado público de CA aceita e/ou Store; não contornar
com endereço fictício ou Private Trust instalado manualmente no cliente.

A integração Artifact Signing é avaliada, ainda não escolhida: sua action oficial
`Azure/artifact-signing-action` suporta GitHub/OIDC e lista de arquivos. A integração
Inno precisaria de callback SignTool/Dlib para assinar **também** o desinstalador;
assinar só o EXE externo pela action é insuficiente. A prova atual fornece o fluxo
certificate-store para CA pública; a decisão de serviço depende da identidade real.

Fontes oficiais consultadas:
[MSIX overview](https://learn.microsoft.com/windows/msix/overview),
[Store developer accounts](https://learn.microsoft.com/windows/apps/publish/partner-center/open-a-developer-account),
[Artifact Signing overview](https://learn.microsoft.com/azure/artifact-signing/overview),
[prerequisites/eligibility](https://learn.microsoft.com/azure/artifact-signing/quickstart),
[FAQ/assinatura e cobrança](https://learn.microsoft.com/azure/artifact-signing/faq),
[preços oficiais](https://azure.microsoft.com/pricing/details/artifact-signing/).
Microsoft Learn foi acessível nesta sessão; preço Azure/retail API não foi acessível
inicialmente pela política de rede. O pipeline coleta a API pública de preços como
informação opcional, registra indisponibilidade explicitamente e não inventa valores.
A API pública retornou preços nesta execução CI: produto ainda chamado `Trusted Signing`,
medidores Basic Account/Premium Account, unidade `1/Month`, vigência informada
2024-06-01. O snapshot completo está em `evidence/signing-prices.json`, com URL,
data de consulta e registros de excedente. Valores são referência pública em USD,
não orçamento de fabricante inelegível ou autorização de contratação.
Requisitos, preços e elegibilidade devem ser reconferidos antes da contratação.

## Migração proposta — condicionada à aprovação da prova

Este é um plano preliminar, não migração para um modelo já aprovado. Só confirmar
a escolha após installer/runtime assinados passarem no Windows real.

1. **Fundação aprovada:** selecionar Inno/CA ou MSIX/Store segundo a homologação;
   fixar fabricante, Package/AppId, certificado/canal, versionamento e política de
   atualização. Produzir SBOM/manifestos de fontes/bytes e encerrar licenças.
2. **Desktop existente:** trocar o entrypoint PoC pela GUI AgroLines atual, mantendo
   módulos `core`/desktop e seus testes. Identidade/versão em um contrato único,
   logs com redaction e diagnósticos utilizáveis sem comandos do cliente.
3. **Servidor central gerenciado:** PostgreSQL/PostGIS continua no servidor próprio;
   instalador cliente não instala servidor/PG. Provisionar API HTTPS e endpoint
   confiável por configuração do produto, autenticação/grants existentes e serviço
   operacional de backup/restauração. Nenhuma senha/credencial embutida no instalador.
4. **Offline integrado:** SQLite por usuário fora dos diretórios binários; schema
   versionado/aditivo, backups via API SQLite, proteção DPAPI/chaves locais quando
   aplicável. Fila durável, versões/conflitos, prazo de autorização e revogação antes
   de expor edição/sync offline. Essa implementação ainda não existe nesta prova.
5. **Atualização/recuperação:** canal autenticado com fabricante esperado, manifestos
   assinados, hashes, rejeição de downgrade/adulteração e staging. Instalação atômica
   ou mecanismo gerenciado MSIX, rollback de binários, backups antes de schema upgrade,
   restauração isolada e preservação de sessões/propriedades. Não restaurar banco
   destruindo alterações recentes nem confundir uninstall com limpeza de dados.
6. **Release comercial:** repetir matriz em instalação limpa, primeira execução,
   startup, mapa/GIS, precisão, offline permitido, upgrade/interrupção e recuperação.
   Assinar os componentes/instalador e publicar somente artefatos homologados; erros
   profissionais orientam suporte e preservam dados/proteções, sem pedir pip/PowerShell.

Nenhuma funcionalidade agrícola seguinte é iniciada até a validação dessa fundação.
