# Primeira edição Microsoft Store — exclusivamente offline

Base: PRs #6, #7, #8 e #9, sem merge ou alteração de main. A política e o procedimento
operacional estão em `docs/privacy/offline/`; a auditoria original permanece intacta.

## Controles técnicos

`distribution.build --store` gera `offline_only: true`. O spec seleciona a entrada
`distribution/store.py` e um runtime hook próprio antes da inicialização. A decisão
fica no código congelado: não é uma preferência ou variável de ambiente do usuário.
A execução normal sempre abre projetos locais, sem relatórios automáticos. Flags
explícitas de manutenção abrem somente verificações locais e não habilitam rede.

O spec exclui janela remota, cliente API, healthcheck, vault, páginas remotas,
servidor, FastAPI/Uvicorn e psycopg; falha se eles aparecerem na análise Python.
A arquitetura original continua no repositório e em builds de desenvolvimento.
O pacote Store não lê o vault DPAPI de versões anteriores nem reutiliza suas contas.

`core/offline_policy.py` ativa política sem opção de desativação, bloqueia imports
remotos e conexões/DNS Python, ignora configuração de tiles/debugging e desabilita
rede PROJ. Fiona restringe importação aos drivers vetoriais locais e o contexto GDAL
omite WMS/WCS/HTTP. Arquivos KML com referências externas continuam rejeitados.
Projetos/importação/backup/restauração rejeitam URLs, /vsi, UNC e unidades Windows
mapeadas de rede. Destinos de diagnóstico também são verificados antes de gravar.
No Windows, temporários ficam na pasta local AgroLines/Temp; configurações externas
de plugin/processo Qt e dados GIS são removidas antes dos hooks embutidos. Pastas locais sincronizadas por outro software não são controladas
pelo AgroLines; isso está explicado na política.

O WebEngine usa assets locais, sem fonte ou biblioteca remota obrigatória. A página
Store tem CSP sem conexões, imagens externas, frames, workers ou formulário remoto;
o interceptor bloqueia esquemas/hosts remotos mesmo após `set_online(True)`. O código
fixa flags de redução de atividades de rede de fundo do Chromium; não desativa seu
sandbox. Windows com flags de sandbox desativado é recusado. Não há alteração de
SAC, Defender, firewall, certificados ou outras proteções.

A ação Privacidade exibe o HTML local em QTextBrowser, sem abrir links externos.
O HTML/TXT/Markdown e as dependências nativas são incluídos no payload. O staging
recusa metadata Store sem política offline explícita. Identidade e publisher oficiais
são preservados, assim como a versão 1.0.0.0 do candidato inicial.

## Testes reproduzíveis

Desenvolvedor com ambiente preparado:

```text
python -m pytest tests/test_store_offline.py tests/test_local_projects.py tests/test_msix.py tests/test_geography.py tests/test_precision.py tests/test_distribution.py tests/test_offline_desktop.py -q
python -m distribution.store --offline-network-report caminho-local/resultado.json
```

`test_store_offline.py` roda a entrada Store em processo separado com configurações
hostis (`PROJ_NETWORK=ON`, tiles, API e remote debugging). Um servidor HTTP local
no processo de teste registra quaisquer requisições recebidas. A janela local e os
helpers WebEngine reais carregam Leaflet/Qt WebChannel; tentativas JS de fetch,
imagem e WebSocket são recusadas e o servidor não recebe requisições. Imports/API,
DNS/socket Python, botão/callback remoto e caminhos remotos são recusados.

O probe carrega NumPy, Shapely, pyproj, Fiona/GDAL e PySide6, executa testes do motor
de precisão e importa SHP/GPKG/KML/KMZ/GeoJSON sintéticos. Edita 1 mm, desfaz/refaz,
salva duas revisões, reabre e restaura backup. Não usa dados reais ou banco central.
O resultado mantém `sac_approved=false` e `native_network_trace_validated=false`:
interceptor/Python e servidor local não observam todo tráfego nativo/DNS/UDP.

O workflow `windows-msix.yml` gera o novo candidato x64 e executa esse probe também
no executável congelado extraído. Isso verifica recursos/helpers embutidos, mas não
instala o pacote nem comprova Store/SAC. Cliente não precisa executar esses comandos
ou possuir Python/PowerShell; são instrumentos de desenvolvimento/homologação.

## Homologação real obrigatória, ainda não executada aqui

1. Com autorização futura, obter o pacote efetivamente distribuído pela Store ao
   grupo privado. Registrar versão/hash/canal e sua assinatura; não usar certificado
   autoassinado ou substituir publisher. Não submeter/publicar nesta tarefa.
2. Em Windows 11 limpo, sem Python/PostgreSQL, manter SAC On e Defender ativo. Capturar
   estado e eventos de integridade usando os instrumentos de leitura existentes.
3. Em bancada conectada separada, com fixture sintética, observar árvore AgroLines +
   QtWebEngineProcess com ferramenta de captura de processos/rede aprovada (por
   exemplo Process Monitor para TCP/UDP, correlacionando PIDs; complementar DNS e
   captura de rede quando necessário). Capturar do início ao encerramento; validar
   a captura com tráfego positivo de um processo distinto. Não aceitar ausência de
   linhas em ferramenta mal configurada como prova de ausência de tráfego.
4. Abrir/importar/editar/salvar/backup/restaurar e tentar configurações de tiles/API.
   Examinar todo tráfego próprio e dos helpers, incluindo requisições breves, DNS,
   UDP e conexões de fundo. Diferenciar operações da Store/Windows de processos do
   aplicativo. Falha exige investigação, nunca exclusão no firewall/Defender/SAC.
5. Desconectar fisicamente a bancada e repetir o fluxo instalado. Conferir interface
   em monitor Windows real; offscreen não valida aparência. Verificar que não há
   dependência de serviços, downloads ou recursos GIS faltantes.
6. Instalar atualização Store confiável de versão superior mantendo dados externos,
   comparar hashes/histórico e reabrir projetos/backups. Desinstalar e verificar os
   arquivos e hashes; reinstalar pelo fluxo autorizado e reabrir/restaurar. Use dados
   sintéticos e backups externos, nunca projetos reais sem cópia.
7. O roteiro existente `Test-SignedMSIX.ps1` verifica instalação/upgrade/desinstalação
   de dois MSIX confiáveis, hashes e SAC sem alterar proteções, mas sideload assinado
   não substitui a homologação do pacote entregue pelo canal Microsoft Store.
8. Revisar/redigir evidências antes de enviá-las: eventos/caminhos podem conter dados
   pessoais ou de outros programas. Não executar workflow de upload da bancada sem
   decidir conscientemente compartilhar esse conteúdo.

Não há bancada Windows 11/Store/SAC neste ambiente Linux. Preservação real no ciclo
de instalação e ausência completa de tráfego nativo continuam pendentes. O manifesto
é intenção de configuração, não evidência de preservação. Não houve publicação,
certificação, merge, aquisição de serviço ou mudança de configuração Microsoft.

## Resultado desta revisão (Linux, 14/10/2026)

- Suíte completa: **125 passaram, 1 ignorado** (DPAPI nativa exige Windows).
- Conjunto focado: **52 passaram**, incluindo o novo processo Store e WebEngine real.
- Ruff check/format e verificação de diferenças: passaram.
- Nenhum teste alterou dados reais, main, SAC ou Defender. As flags de sandbox usadas
  pelo runner Linux isolado não fazem parte da distribuição Windows; Windows recusa
  execução configurada com sandbox desativado.
- Build Windows, captura nativa completa, instalação pela Store/SAC e ciclo real de
  atualização/desinstalação não foram executados neste ambiente.
