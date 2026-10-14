# Homologação real: Store, confiança nativa, SAC e offline

Roteiro de manutenção. Cliente final não precisa de PowerShell, Python, pip ou SDK.
**Não executado nesta sessão.** Windows hospedado/GitHub Actions, assinatura
embutida válida ou catálogo verificado não substituem bancada Windows 11 Pro real.
Nenhum comando deste roteiro desativa proteção, rede, políticas ou logging.

## Pré-condições e segurança

- Aprovação para distribuição/teste real pela Store, pendências jurídicas resolvidas
  e grupo privado de adultos/audiência preservados. Não há autorização de envio neste PR.
- Computador/VM Windows 11 de homologação separado do uso diário, SAC **On**
  (não Evaluation), Defender/antivírus/proteção em tempo real ativos, sem Python,
  pip, PostgreSQL ou instalação prévia AgroLines/projetos reais.
- Registrar versão/build Windows, versão do aplicativo e origem legítima de instalação
  da Store. Captura manual Windows Security/SAC/Defender, sem dados pessoais.
- Instalar somente pelo fluxo confiável oficialmente disponibilizado. Não obter
  pacotes por sites de extração de terceiros, instalar roots ou usar Developer Mode.
- Somente dados sintéticos; guardar relatórios fora de WindowsApps/LocalState e
  não enviar automaticamente logs do sistema que possam conter caminhos pessoais.

## Instalação normal pela Store (quando autorizada)

1. Instalar a primeira versão pelo cliente Store/audiência privada. Conferir
   Get-AppxPackage Name/PFN/Version/SignatureKind **Store**, Status Ok. Não usar
   execução do EXE extraído para declarar instalação aprovada.
2. Antes de desconectar, opcionalmente coletar confiança por arquivo usando as
   ferramentas oficiais SDK de manutenção (assinadas), em PowerShell de manutenção:

   ```powershell
   ./distribution/windows/signing/Test-StoreDeliveredTrust.ps1 -OutputDirectory evidence/store-trust-primeira-versao
   ```

   Script só lê instalado/assinaturas/catálogo/estado. Sem registrar catálogo,
   instalar certificado, alterar o pacote ou aprovar SAC. All-native trust false,
   catálogo ausente/incompleto ou erro deve ficar como pendência real. Guardar
   saídas SignTool por arquivo para comparar assinatura embutida com cobertura
   explícita de CodeIntegrity.cat; não chamar todas as DLLs de reassinadas pela Microsoft.
3. Desconectar fisicamente internet na bancada e registrar a evidência; script não
   altera adaptadores. Abrir AgroLines pelo menu Iniciar. Abrir/criar projeto local,
   importar **SHP + sidecars**, GPKG, KML, KMZ, GeoJSON sintéticos, com SRC explícito
   onde requerido. Conferir EPSG:4326/32723 e SRC original preservado.
4. Selecionar/editar vértice numericamente em UTM por 0,001 m, desfazer/refazer,
   salvar, fechar/reabrir e comparar coordenadas com referência; confirmar revisão
   histórica, backup/restauração. Não inferir precisão física em campo deste ensaio.
5. Verificar mapa/recursos locais/QtWebEngineProcess, ausência de UI/login remoto,
   nenhuma dependência externa Python/pip/PostgreSQL e nenhuma solicitação de
   reduzir proteção. A captura de tráfego TCP/UDP/DNS é verificação adicional
   separada; probes Python/JS bloqueados não provam todos os syscalls nativos.
6. Ler CodeIntegrity Operational desde antes da instalação/início, eventos **3077
   e 3033**, correlacionar com inventário/caminhos/horário/helper. Não limpar ou
   desativar log. Ausência de eventos sozinha não prova execução de todas as bibliotecas.
7. Registrar hashes dos projetos/backups locais. Quando autorizado, obter atualização
   pela Store; esta transferência exige rede. Desconectar novamente e repetir os
   ensaios. Desinstalar apenas a versão de bancada, confirmar hashes/dados fora da
   instalação, reinstalar versão legítima e confirmar reabertura.
8. Conferir SAC/Defender continuam ativos, revisar falhas e repetir só os casos
   afetados. Guardar relatório completo com resultado por etapa, não só screenshot.

## Caminho automatizado com dois pacotes Store legítimos disponíveis

Se a Microsoft/fluxo autorizado disponibilizar os dois arquivos MSIX confiáveis
assinados pela Store, a bancada pode executar:

```powershell
./distribution/windows/msix/Test-SignedMSIX.ps1 `
  -FirstPackage C:/Homologacao/primeiro.msix `
  -UpdatePackage C:/Homologacao/atualizacao.msix `
  -OutputDirectory C:/Homologacao/evidence-nova `
  -RequireSac -RequireCleanMachine -RequireDisconnected
```

Não pressupor que esse download de arquivos assinados estará disponível no Partner
Center. Sem arquivos legítimos, seguir instalação/atualização normais pela Store e
coleta de leitura; não contornar o mecanismo Store para obtê-los.

O helper recusa pacote/identidade divergentes, bancada com aplicativo existente,
Python/PostgreSQL, rede Up (quando solicitado) ou SAC não comprovado; exige Defender
ativo antes/depois e SignatureKind Store nas duas instalações. Instala apenas os
pacotes fornecidos para a bancada isolada. Ativa por AUMID, exercita runtime/helper,
projeto/backup/restauração e agora os **cinco formatos** efetivamente. Compara projeto
na atualização/desinstalação e lê eventos. Não instala/remova proteção ou certificado.

A função de resultado `real_clean_disconnected_sac_acceptance` só pode ser true
quando todas essas pré-condições/etapas passaram. Não executamos esse helper sem
pacotes/bancada/autorizações. Workflow de runner conectado não satisfaz desconexão
física: execução local independente é necessária; upload de evidências só depois,
por decisão do responsável e após revisar dados presentes.

## Critérios do relatório

Distinguir: confiança do envelope, assinatura **embutida** de PE, confiança por
catálogo, integridade/proveniência, efetiva execução de GIS/helpers, SAC/Defender e
preservação de dados. Arquivo unsigned embutido pode continuar como tal mesmo que
seja coberto por catálogo confiável: informar as duas contagens. Não falsificar
redução de unsigned ou afirmar garantia em qualquer máquina/build Windows.

Se a rota Store cobrir todos os PE e passar na bancada real, avaliar se certificado
próprio ainda é necessário para esse canal. Se houver lacunas/bloqueios, preservar
logs/hashes e usar o pipeline de PE autorizados/certificado público como alternativa,
sem baixar proteções nem mudar o motor geográfico por tentativa.
