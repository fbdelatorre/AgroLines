> Atualização da primeira edição: pacote exclusivamente offline conforme
> [store-offline-only.md](store-offline-only.md). A política vigente de preparação
> está em [privacy/offline/README.md](privacy/offline/README.md).
> A auditoria histórica do PR #9 continua preservada.

# Microsoft Store — MSIX oficial do AgroLines

Esta entrega prepara o candidato x64 e a homologação. Não publica, não configura
cobrança, não emite licenças comerciais e não declara compatibilidade SAC aprovada.
Complementa o PoC PyInstaller e a fundação offline, preservando os PRs anteriores.

## Identidade imutável

| Campo | Valor exato do Partner Center |
|---|---|
| Package/Identity/Name | `DelatorreCOrporation.AgroLines` |
| Package/Identity/Publisher | `CN=43189595-B928-4D57-90A4-24300E4D4976` |
| Package/Properties/PublisherDisplayName | `Delatorre COrporation` |
| Store ID | `9NRDJ3ZTM978` |
| Package Family Name | `DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg` |
| URL | https://apps.microsoft.com/detail/9NRDJ3ZTM978 |

Manifesto em `distribution/windows/msix/AppxManifest.xml`; registro e verificações
em `identity.json`. Maiúsculas, espaços e Publisher não são normalizados. PFN é
calculado pelo Windows, não escrito como atributo inexistente no manifesto; o
aplicativo e o teste de instalação conferem seu valor efetivo em runtime.
Store ID não é uma licença comercial nem uma chave criptográfica.

Versão inicial do **candidato não publicado**: `1.0.0.0`; major precisa ser maior
que zero e revision (quarto campo) precisa ser zero na submissão. A Store pode
atribuir revision posteriormente. Próxima versão de teste: `1.0.1.0`, com a mesma
identidade. Não substituir Publisher para assinar com certificado de outra conta.

## Pacote e execução

O pacote contém o diretório PyInstaller **inteiro** em
`VFS/ProgramFilesX64/AgroLines`, incluindo Python embutido, DLLs/PYDs, GEOS,
PROJ/database/grids disponíveis, GDAL/Fiona, NumPy, Qt, recursos e
`QtWebEngineProcess.exe`, Leaflet local e avisos de dependências. Não usa download
de dependências durante instalação. O ponto de entrada é `AgroLinesPoC.exe`
(nome interno herdado), com identidade/display name **AgroLines** no MSIX/PE.
O canal Store abre projetos locais por padrão; smoke tests são opções de
mantenedores, sem exigir Python/PowerShell no computador do cliente.

Runtime `packagedClassicApp`, `mediumIL`, `Windows.FullTrustApplication`: aplicativo
Win32/PySide6, não UWP reescrito. Capacidade restrita `runFullTrust` precisa de
justificativa/aprovação no Partner Center para bibliotecas nativas, edição de
arquivos escolhidos pelo usuário e processamento GIS local. O sandbox Chromium
continua ativo. Nenhum caminho alternativo de carregamento de DLL ou bypass é
introduzido. Qt encontra seus recursos/processos auxiliares pelo layout padrão do
PyInstaller. O teste efetivo MSIX ativa **AUMID** via IApplicationActivationManager;
rodar o EXE extraído não prova comportamento dentro do pacote.

`GetCurrentPackageFullName/FamilyName/Path` conferem identidade efetiva e manifesto.
O probe verifica mapa pronto e enumera descendentes QtWebEngine, caminhos dentro
do pacote e a identidade observada dos auxiliares. Origem/execução dos subprocessos
é obrigatória no gate MSIX; eventual identidade diferente de um auxiliar sandboxed
fica registrada para revisão. Carregamento NumPy/GEOS/PROJ/Fiona/PySide6, referências
numéricas, SQLite e edição de 1 mm continuam no smoke test real do executável.

## Dados e ciclo de vida

Projetos/backup padrão: `%LOCALAPPDATA%\AgroLines\Projects`. Sessão DPAPI existente:
`%LOCALAPPDATA%\AgroLines\session.dpapi`. Evidências:
`%LOCALAPPDATA%\AgroLines\Evidence`. Arquivos escolhidos pelo usuário também podem
ficar em outra pasta pessoal. Não colocar projetos/configurações em WindowsApps,
no VFS da instalação ou em `%LOCALAPPDATA%\Packages\<PFN>`.

O aplicativo resolve LocalAppData pela API SHGetKnownFolderPath com
KF_FLAG_NO_PACKAGE_REDIRECTION; não depende de AppData redirecionado no processo.
O manifesto Windows 11 declara `unvirtualizedResources` com exclusão **apenas** de
`$(KnownFolder:LocalAppData)\AgroLines`. Isso mantém essa pasta real fora dos dados
privados MSIX removidos na desinstalação, preservando compatibilidade com os
arquivos anteriores. A capacidade é restrita: justificar retenção de projetos,
backups e configuração local, sem solicitar exclusões amplas de AppData/registro.
Não desabilita proteções do Windows. Se a Store não aprovar essa capacidade, avaliar
uma pasta pessoal não virtualizada e migração testada antes de mudar o manifesto.

SQLite/revisões/arquivos importados mantêm a arquitetura da ADR 0004; nenhuma
migração do PostgreSQL ou do motor geográfico foi alterada. Atualização via mesma
identidade/versão crescente substitui o código do pacote, não o projeto externo.
Desinstalação mantém os arquivos; informar ao cliente onde ficam. Exclusão de dados
será ação explícita futura. Não remover sessões/arquivos automaticamente junto com
projetos; sessão continua cifrada por DPAPI e pode ser encerrada pelo logout.

## Geração e testes no CI

Workflow `windows-msix.yml`:

1. Ambiente build x64 Python 3.12 com lock/hash e PyInstaller existente.
2. Metadados oficiais, ícones, inventário de **todos** os executáveis nativos e
   Authenticode individual; registrar DLLs/PYDs ainda não assinadas.
3. Manifesto SHA-256 do payload; copiar integralmente e verificar hashes.
4. Windows SDK MakeAppx **com validação de schema**, pack/unpack e comparação de
   payload; gerar `.msix` e SHA-256 para revisão/submissão manual.
5. Executar o runtime **extraído**, PATH isolado, bibliotecas GIS, Qt e ciclo offline
   SQLite/backup; declarar explicitamente que essa execução não é instalação MSIX.
6. Publicar apenas artifact de CI `agrolines-official-store-msix-UNSIGNED-submission-candidate`.
   Não criar release, submeter ao Partner Center, assinar com certificado improvisado
   ou tocar cobrança. Workflow anterior Inno/PoC permanece funcional.

Para mantenedores Windows com SDK oficial e build-env preparado:

```text
build-env\Scripts\python.exe -m distribution.build --store --version 1.0.0.0 --manufacturer "Delatorre COrporation"
build-env\Scripts\python.exe -m distribution.payload --root dist/AgroLinesPoC --manifest --output dist/AgroLinesPoC/payload-manifest.json
```

Executar `distribution/windows/msix/Build-MSIX.ps1` na bancada/build. Script é
ferramenta de mantenedor; o cliente usará Microsoft Store/App Installer. SDK,
MakeAppx e assinatura da ferramenta são verificados; não usar `/nv` para ignorar
schema. A pasta de staging/pacote é nova, sem sobrescrever artefatos auditados.

O arquivo `AgroLines-1.0.0.0-x64-STORE-SUBMISSION-UNSIGNED.msix` **não é instalador
homologado para clientes nem pacote instalável sob as restrições atuais**. Sem
assinatura confiável, parar antes de instalar. Não usar Developer Mode, AllowUnsigned,
alteração de Publisher/OID, Import-Certificate ou certificado autoassinado.

## Assinatura, certificação e homologação

1. Revisar manualmente candidato, hashes/inventário, direitos de redistribuição
   Qt/LGPL/Chromium/GDAL/PROJ e licenças; finalizar privacidade, suporte e listagem.
2. No Partner Center do Store ID acima, preparar submissão/voo privado apropriado
   e avaliar as capacidades restritas. **A ação de enviar/certificar/publicar é
   futura, manual e depende de autorização**; este PR não a executa.
3. Obter pacote(s) de teste realmente assinados pelo fluxo oficial da Microsoft
   Store. Assinatura Microsoft do pacote não é troca da identidade declarada por
   um Publisher Microsoft: manter exatamente os campos acima. Certificado CA de
   teste, se existir, precisa de Subject compatível com o Publisher exato, cadeia
   confiável e validação de MSIX; não alterar identidade para adequar certificado.
4. Executar Windows App Certification Kit na bancada e guardar relatório completo,
   incluindo falhas de APIs/recursos/manifesto. Corrigir tecnicamente; MakeAppx/CI
   não substitui WACK ou certificação do Partner Center.
5. Testar em Windows 11 real/SAC **On**, Defender ativo, sem Python/PostgreSQL
   preinstalados. Checar app instalado pelo AUMID, auxiliares Qt, imports e precisão.
6. Desconectar completamente a internet e repetir criação/importação/edição/save,
   fechar e reabrir projeto, backup/restauração. PROJ não baixa grids, mapa local
   não solicita tiles remotos, nenhuma licença de desenvolvimento exige servidor.
7. Atualizar para o segundo pacote assinado de mesma identidade, reabrir o mesmo
   projeto/revisões e comparar SHA-256; desinstalar e conferir arquivo preservado.
   Reinstalar pela Store quando disponível e repetir a abertura.
8. Revisar 3077/3033, assinatura de pacote/payload, estado SAC antes/depois e evidência
   de rede desconectada. Só depois declarar a compatibilidade validada.

Automação de bancada: `Test-SignedMSIX.ps1 -FirstPackage <pacote-assinado-v1>
-UpdatePackage <pacote-assinado-v2> -OutputDirectory <pasta-nova> -RequireSac
-RequireCleanMachine -RequireDisconnected`. Não altera rede/proteções nem desinstala
aplicativo preexistente: recusa bancada que já tenha a identidade oficial instalada.
Mantém projeto sintético para inspeção após desinstalar. Se ocorrer falha, mantém
pacote/evidências para diagnóstico; não remove arquivos do usuário na limpeza.
Ausência de Python/PostgreSQL é verificada por registros/serviços/Store e confirmada
pelo inventário manual da bancada (não varre todos os arquivos pessoais).

Workflow manual `windows-msix-signed-validation.yml`: self-hosted interativo
`agrolines-store-validation`, ambiente protegido `microsoft-store-validation`,
variáveis **não secretas** `AGROLINES_MSIX_FIRST/UPDATE` com caminhos locais de
pacotes assinados previamente verificados. Não importa certificados nem emite
assinaturas. Conta Store/credenciais não entram no Git/CI. O runner depende da rede
GitHub; seu resultado registra **offline físico ainda pendente**. Para aceitação
fisicamente desconectada, rodar o roteiro/script local e recolher evidências depois
de reconectar. Clientes não precisam desses scripts de bancada.

## Relatório de pendências

| Requisito | Evidência/estado nesta entrega |
|---|---|
| Identidade, manifesto, x64, versão e ícones | Implementados; SDK/CI verifica candidato |
| Payload nativo íntegro + runtime embutido | Inventário/hash e smoke extraído; sem Python/PG externo no PATH |
| Dados fora da instalação e virtualização restrita | Código/manifesto implementados; preservação efetiva na desinstalação depende do MSIX assinado |
| Qt WebEngine/auxiliares em identidade MSIX | Probe/automação preparados; execução instalada ainda pendente |
| Offline/precisão/licenciamento | Regressão existente preservada; aceitação física do pacote pendente |
| Instalação/update/uninstall MSIX | Script funcional preparado, requer duas versões realmente assinadas e bancada limpa |
| Assinatura oficial/Store/WACK | Não executados por este PR; pendentes de pacote confiável e processo manual |
| SAC Win11 real sem Python/PG e sem rede | Não comprovado por CI/extração; não aprovado |
| Publicação e cobrança | Não executadas/configuradas |

## Referências oficiais

- [Identidade, versões e requisitos de pacote](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/app-package-requirements)
- [Virtualização flexível Windows 11](https://learn.microsoft.com/en-us/windows/msix/desktop/flexible-virtualization)
- [Arquivos/dados e MSIX desktop](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes)
- [Application: RuntimeBehavior/TrustLevel](https://learn.microsoft.com/en-us/uwp/schemas/appxpackage/uapmanifestschema/element-application)
- [MakeAppx](https://learn.microsoft.com/en-us/windows/msix/package/create-app-package-with-makeappx-tool)
- [Ativação AUMID](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-iapplicationactivationmanager-activateapplication)
