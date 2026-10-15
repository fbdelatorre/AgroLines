# Instalador e homologação física futura

**PARCIAL: implementação e testes de processo no builder. BLOQUEADO: instalação
física até existir candidato legitimamente assinado e autorização específica.**
O produto não exige Python, pip, PostgreSQL, QGIS ou PowerShell do cliente.
PowerShell 7 e ferramentas de coleta são de mantenedor/homologação, não pré-requisitos
de uso. Não foi executado instalador AgroLines nesta tarefa.

## Arquitetura preservada e melhoria implementada

- PyInstaller onedir, dependências organizadas sem achatar `_internal`, Python
  integrado e exclusões Qt existentes; perfil offline fixo independente da Store.
- Inno com identidade experimental separada, pt-BR, Windows 11/x64, instalação
  administrativa em `Program Files/AgroLines Experimental`; o app não pede elevação.
- Runtime em `versions/<versão>-<12hex>/`, um diretório completo por candidato.
  Não copiar DLL nova sobre versão antiga nem misturar QGIS no PATH. Atualizações
  iniciais por instaladores completos; nenhum atualizador online acrescentado.
- **Novo launcher nativo estável `{app}/AgroLines.exe`**: lê somente
  `AgroLines.current.txt`, valida formato/escopo, recusa reparse/path escape,
  inicia o EXE na pasta completa escolhida e repassa argumentos Unicode/aspas.
  Atalhos Iniciar/Desktop apontam à raiz fixa. Ponteiro instalado depois da árvore.
- Ícone oficial e recursos de versão/fabricante incorporados ao launcher; identidade
  de taskbar `Delatorre.AgroLines.Standalone` também definida no processo Python.
  Não altera a identidade MSIX. Atalho fixado a partir do menu Iniciar é o caminho
  recomendado para o teste; fixação a partir da janela em execução precisa ser
  observada no Windows real antes de prometer comportamento universal.
- Mutex global de execução compartilhado entre usuários e `AppMutex`/`SetupMutex`
  no Inno; evita atualização planejada com app aberto. O launcher mantém o mutex
  enquanto o filho roda. Não mata projetos nem implementa fechamento forçado.
  Ainda é necessário testar corridas entre sessões/UAC/instalação com app aberto.
- Sem `UninstallDelete`/`InstallDelete` para projetos e backups; dados ficam fora
  da instalação. Configurações por usuário preservadas por desenho, mas o ciclo
  real de desinstalação e preservação **não foi executado**.

[Launcher](../../distribution/windows/standalone/launcher.cpp),
[build](../../distribution/windows/standalone/Build-Launcher.ps1),
[teste de processo](../../distribution/windows/standalone/Test-Launcher.ps1),
[Inno](../../distribution/windows/installer.iss). O primeiro link MSVC precisou de
`user32.lib`, corrigido antes do resultado aprovado. Não houve mudança GIS.

O teste de processo usa o app congelado completo: seleciona versão A, move a mesma
árvore para versão B, seleciona B mantendo launcher/atalho estável, roda smoke e
probe offline e recusa quatro ponteiros inseguros. Isso comprova seleção de árvore,
**não instalação/atualização Inno nem múltiplas sessões reais**.

## Pré-requisitos de homologação

1. Revisões de licença, direitos de redistribuição/assinatura e privacidade no escopo
   autorizado; não tratar o pacote de testes como distribuição comercial aprovada.
2. Dois instaladores completos legitimamente assinados, de candidatos distintos,
   hashes entregues por canal confiável, timestamp e fonte/payload/gate rastreáveis.
   Nenhum certificado de teste, alteração de raiz, Developer Mode ou política de
   execução para contornar proteção. Se script ou componente for bloqueado, parar.
3. Máquina dedicada Windows 11 x64 cliente, SAC **On** (não Evaluation) e Defender
   ativo, sem AgroLines anterior ou projetos reais. Registrar build, estado e hora.
   Inventário de softwares e inspeção manual devem confirmar ausência de Python,
   pip e PostgreSQL; PATH mínimo sozinho não prova que não estão instalados.
4. Obter instaladores e ferramentas aprovadas por canal legítimo; depois desconectar
   fisicamente a rede. Não alterar adaptadores/proteções por script. A aceitação
   offline deve funcionar após instalação/ativação pertinente, sem login remoto.
5. Guardar evidências fora de Program Files e fora de repositórios públicos. Usar
   exclusivamente fixtures sintéticas e não compartilhar logs com PII sem revisão.

## Ciclo automatizado preparado — não executado

[Test-SignedLifecycle.ps1](../../distribution/windows/standalone/Test-SignedLifecycle.ps1)
exige `-AuthorizeSyntheticInstallation`, dois arquivos/SHAs e subject esperado,
PowerShell 7 de mantenedor, Windows 11 x64 e elevação só para o instalador. Sem a
flag, falha antes de acessar máquina, arquivos ou certificados (controle testado).

Na execução futura autorizada:

1. Verifica SAC, Defender, rede física desconectada, pasta de instalação ausente,
   hashes, Authenticode válido com timestamp e identidade esperada; recusa assinatura
   autoassinada e raiz fora do dossiê público aprovado. Exige cadeia e revogação
   em cache válidas no ensaio offline; se inconclusivas, interrompe para investigação,
   sem desligar verificações. Esse preflight conservador não prova aceitação de
   um computador cliente sem cache anterior. Não instala certificados.
2. Instala A, confere assinatura de todos os PE instalados (critério conservador
   **deste candidato standalone**, não regra universal para todo pacote Store).
3. Inicia pelo launcher com PATH de sistema e variáveis Python/GIS/Qt externas
   removidas; cria SQLite/GeoJSON/histórico/backups sintéticos em LocalAppData
   separado. Exige probes offline e precisão 22/22.
4. Instala B, exige ponteiro distinto; reabre o projeto e compara SHA-256 dos arquivos
   de projeto/histórico/backup/restauração. Não aceita simples ausência de erro.
5. Confere confiança do uninstaller, desinstala e verifica remoção do launcher e
   preservação exata dos dados; reinstala B e reabre/compara novamente.
6. Registra SAC/Defender após o ciclo, eventos CodeIntegrity 3077/3033 desde o início
   e impede aprovação se há evento relevante. Deixa o app B assinado instalado e
   as fixtures/evidências para inspeção; não faz limpeza destrutiva automática.

Exemplo de **forma de chamada futura**, preencher somente com artefatos reais e
após autorização (não é comando para instalar o experimento atual):

```powershell
# Executar somente em estação de homologação autorizada com candidatos confiáveis.
./distribution/windows/standalone/Test-SignedLifecycle.ps1 `
  -AuthorizeSyntheticInstallation `
  -FirstInstaller <instalador-A-assinado> -FirstSha256 <sha256-A> `
  -NextInstaller <instalador-B-assinado> -NextSha256 <sha256-B> `
  -ExpectedSignerSubject <nome-legal-do-certificado> `
  -ApprovedPublicRootSha256 <hash-da-raiz-publica-revisada> `
  -EvidenceDirectory <pasta-nova-local-de-evidencias>
```

O parser e as recusas foram testados; o corpo de instalação, a confiança offline
real e as propriedades de uninstaller assinado aguardam essa execução autorizada.
Não usar a elevação desse script para alegar teste de uso com usuário comum.

## Complementos manuais obrigatórios e aprovação

| Ensaio | Critério objetivo |
| --- | --- |
| UAC e usuário comum | Instalar com mantenedor; abrir pelo Iniciar/Desktop e usar projeto com conta comum, sem UAC para usar app; Program Files sem escrita comum; dados fora dela. |
| Atualizar/desinstalar com app aberto | Inno deve impedir ou solicitar fechamento em ambas as sessões; salvar projeto antes; nenhuma terminação forçada/perda. Testar segunda conta conectada e corrida de nova abertura. |
| Barra de tarefas | Fixar atalho Iniciar e, separadamente, janela em execução; atualizar; ambos abrem versão B. Se pin de janela apontar ao filho antigo, não aprovar esse fluxo até corrigir relaunch metadata. |
| Múltiplos usuários | Dois perfis comuns, dados separados; shared binaries íntegros, segunda sessão detectada; update administrativo não altera projetos/configuração de nenhum perfil. |
| QGIS | Testar sem QGIS, depois QGIS já instalado e ambas as ordens de instalação; não modificar QGIS. Observar caminhos DLL carregados, nenhuma resolução de Qt/GDAL/GEOS/PROJ pelo QGIS. |
| GIS/offline instalado | GUI e WebEngine/helper, mapa Leaflet local, cinco formatos, edição/undo/redo, histórico, fechar/reabrir, backup/restauração e 22/22. Repetir sem rede e sem dependências instaladas. |
| Rede nativa/auxiliares | Coleta aprovada somente de leitura por processo, incluindo QtWebEngineProcess, durante os fluxos. Ausência de DNS/conexão/tiles/API próprios. Negativos Python/Qt não bastam para provar todos os PE. |
| Confiança | Assinaturas e timestamps válidos, origem e hashes preservados; SAC On antes/depois, Defender ativo, nenhuma falha relevante de carregamento/CodeIntegrity/AppModel não resolvida. Assinatura não substitui ensaio. |
| Atualização/dados | Hashes de fixtures e backups iguais após update/uninstall/reinstall; configurações por usuário preservadas; falha/cancelamento não deixa ponteiro em runtime incompleto. Não há rollback automático implementado. |
| LGPL | Em laboratório autorizado, testar cópia completa com biblioteca modificada confiável e compatível, sem contornar SAC; aceitar somente após revisão jurídica do mecanismo aplicável e fontes/avisos. |

Usar adicionalmente os coletores somente de leitura e roteiro em
[docs/compliance/windows-validation/sac-test-procedure.md](../compliance/windows-validation/sac-test-procedure.md)
para CodeIntegrity/AppModel/assinaturas/origem e registros de carregamento. Adaptar
somente a identificação standalone onde o roteiro anterior se referir a MSIX;
SignatureKind de pacote Store não existe nessa instalação Win32 comum.
Nenhum resultado físico ou conformidade comercial é declarado por este documento.
