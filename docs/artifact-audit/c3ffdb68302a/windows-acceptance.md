# Testes Windows controlados — preparados, NÃO executados nesta auditoria

## Gate obrigatório antes de qualquer instalação futura

**Parar agora para o MSIX e6a2ab8e…: unsigned e diagnóstico, instalação proibida.**
Este plano não autoriza submissão, distribuição nem instalação. Exige autorização
futura separada e cópia obtida legitimamente da Microsoft Store; não reutilizar a
assinatura de outro pacote ou certificados de teste. Nenhum comando de instalação
foi adicionado. A referência permanece imutável.

Bancada: Windows 11 físico x64, conta dedicada ao teste, dados somente sintéticos,
SAC **On** na interface Windows Security (Evaluation não serve), Defender ativo com
proteção em tempo real, nenhum Python/pip/PostgreSQL de usuário, sem SDK/GIS do
ambiente de desenvolvimento fornecendo DLLs. Não habilitar Developer Mode nem mudar
ExecutionPolicy, ACLs, antivírus ou confiança. Se bloqueado, guardar evidência e parar.

Preparar duas versões **legítimas, autorizadas e crescentes** do mesmo produto para
update; existe apenas a referência 1.0.0.0 unsigned nesta análise. Não fabricar um
update alterando só a identidade/versão do diagnóstico. Preparar backup de bancada e
cópia externa dos projetos sintéticos, inventário de arquivos e horários UTC.

A cópia Store deve apresentar identidade/Publisher/PFN oficiais, x64, Status saudável,
SignatureKind **Store**, IsDevelopmentMode false e prova da origem de obtenção.
Distinguir SHA do pacote enviado do pacote entregue/assinado pela Microsoft: assinatura
pode mudar bytes. Comparar conteúdo lógico e diferenças autorizadas, não exigir
igualdade do envelope assinado com o unsigned. Não pressupor catálogos; se presentes,
verificar assinatura **e associação criptográfica por arquivo**.

## Matriz de execução e aprovação

| ID | Ação futura controlada | Evidência/critério objetivo |
| --- | --- | --- |
| W00 | Fotografar estado inicial, coletar OS/Defender/SAC/pacote e inventário da máquina | Windows 11 físico, SAC On/Defender realtime true, clean machine e origem confiável documentados; desconhecido bloqueia aprovação |
| W01 | Instalar exclusivamente pela Store após autorização; abrir pelo menu Iniciar | Identidade oficial, sem erro/bloqueio, janela pt-BR e WebEngine/Leaflet local; sem terminal/ferramentas de dev necessárias ao cliente |
| W02 | Fechar, desconectar fisicamente internet/Wi-Fi e reabrir | Sem autenticação, servidor, PostgreSQL ou downloads; projeto local abre após nova inicialização do processo/sessão, não apenas cache de UI |
| W03 | Criar .agrolines e importar um exemplar de cada SHP+sidecars, GPKG, KML, KMZ, GeoJSON | Cinco formatos efetivamente importados; contagens/geometria/SRC originais e metadados comparados às fixtures; nenhum download de dados PROJ |
| W04 | Selecionar vértice, deslocar 0,001 m em SRC métrico, undo/redo, salvar/fechar/reabrir | Coordenadas esperadas e versões anteriores preservadas sem arredondamento de persistência; erros computacionais dentro dos critérios existentes, não 1 cm arbitrário para tudo |
| W05 | Conferir histórico, fazer backup, restaurar em **novo arquivo** e reabrir | Versões/originais/SRC/eventos e geometria iguais ao estado esperado; projeto anterior não sobrescrito; SQLite quick_check e foreign_key_check sem falhas |
| W06 | Em sessão conectada controlada, repetir início/importação/edição/backup/fechamento | Nenhuma tentativa de DNS/TCP/UDP/HTTP do processo AgroLines, QtWebEngineProcess e demais filhos; captura atribuída por PID/caminho/horário, não só ausência de bytes transmitidos |
| W07 | Fechar app, obter snapshots antes, atualizar via Store para a segunda versão autorizada | Mesma identidade/Publisher e versão crescente, sem Python/PG; sem migração prevista, hashes dos arquivos fechados iguais; esquema/revisões/SRC/valores originais preservados após reabrir |
| W08 | Fechar app, tirar snapshot, desinstalar via Settings > Apps > Installed apps | Pacote removido; projetos/backups externos e LocalAppData/AgroLines preservados conforme escopo prometido, comprovados por inventário/hashes; sem confundir dados virtualizados com externos |
| W09 | Reinstalar a versão legítima via Store e reabrir projeto preservado, inclusive offline | Histórico, precisão, backups e UI pt-BR intactos; ausência de migração inesperada/recadastro remoto |
| W10 | Coletar eventos/assinaturas/módulos por etapa e reconciliar com fixtures | Nenhum bloqueio atribuível 3077/3033/DLL/AppModel não resolvido, nenhuma procedência inesperada; ausência de evento com canal inacessível/desativado é **inconclusiva** |

Todos começam **not_run** em [windows-results.template.json](windows-results.template.json).
Preencher expected/actual/evidência por etapa, não transformar checklist em aprovação
automática. Não testar eliminação de arquivos pessoais nem interrupção forçada da
máquina. Crash/power-loss e rollback de pacote são campanhas adicionais separadas;
recuperação mínima aqui é backup/restauração em novo arquivo.

### Fixtures e precisão

Reutilizar fixtures sintéticas de `scripts/store_demo.py`, testes GIS/local_projects
existentes e probe offline do candidato; gerar SHP/GPKG em máquina de preparação,
transferir só dados, registrar hashes e resultados esperados. Não exigir Python no
Windows de homologação. Incluir geometria com casas decimais, Z quando suportado,
EPSG:4326 e EPSG:32723; manter SRC original e transformação PROJ local. Fontes externas,
camadas remotas e arquivos de clientes ficam fora da bancada. Malformados/SRC ausente
ou incompatível devem falhar explicitamente sem alterar projeto anterior.

Executar relatório de **22/22 referências computacionais** no build autorizado e
conferir o mesmo motor no instalado; esses resultados não comprovam precisão absoluta
centimétrica no terreno. Não confundir distância da grade UTM com terreno nem exigir
algoritmos agrícolas ainda não implementados.

### Rede, observação e privacidade da bancada

O coletor existente [Collect-Homologation.ps1](../../../tools/windows-lgpl-lab/Collect-Homologation.ps1)
é de leitura e usa [Test-StoreDeliveredTrust.ps1](../../../distribution/windows/signing/Test-StoreDeliveredTrust.ps1).
Seguir [procedimento SAC](../../compliance/windows-validation/sac-test-procedure.md):
coletar antes/depois, intervalos por etapa, logs de inicialização e eventos existentes.
Não habilita canais, instala, ativa o app ou modifica proteções. O histórico de
assinaturas desta auditoria não substitui nova coleta do instalado.

Esse coletor **não faz captura completa de rede nem enumera todos os módulos filhos**.
Preparar observação adicional por ferramentas Microsoft já aprovadas/documentadas
(ex.: Process Monitor para Load Image e rede com árvore de processos; ETW/TCPIP/DNS
quando disponível) em sessão isolada com operador autorizado. Não instalar ferramenta
sem procedência/assinatura ou afrouxar política para executá-la. Se a captura exigir
permissão/driver não autorizado, registrar W06/W10 inconclusivos até bancada adequada;
netstat/Get-NetTCPConnection em snapshots não detectam tentativas curtas ou todo UDP.
Consultar canais oficiais [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)
e [Packet Monitor](https://learn.microsoft.com/en-us/windows-server/networking/technologies/pktmon/pktmon).
Não iniciar captura neste trabalho, não enviar PCAPs/eventos automaticamente.

Separar tráfego próprio da Store/Windows/consulta de revogação de certificados do
tráfego do aplicativo e filhos. A Store precisa de rede para instalação/update;
o teste funcional desconectado começa depois. “Não precisou de internet” e “não
iniciou conexão própria quando conectado” são dois critérios diferentes.

### Preservação de dados sem modificar o projeto

Após fechar normalmente o aplicativo e cessar acessos SQLite, conferir arquivos
projeto/-wal/-shm/-journal. Não apagar/checkpoint manualmente arquivos abertos. O novo
`tools/artifact-audit/project_snapshot.py` recusa sidecars, versão desconhecida,
quick_check/FK inválidos; lê com mode=ro/query_only/trusted_schema off, gera hashes de
esquema e todas as linhas de project/feature/revision/source/event, sem expor conteúdo.
Não usa LocalProject, não migra, não carrega extensões, confere hash antes/depois.

É ferramenta do auditor: pode ser usada em **cópias privadas fechadas transferidas
para a máquina de análise**. Não instalar Python no computador clean para executá-la.
Na máquina clean, usar hashes/inventário de leitura já disponíveis e reabertura pela UI.
Para update sem migração, comparar hash bruto pré/pós antes de reabrir; para backup e
restauração, comparar esquema e hashes das linhas, pois paginação SQLite pode mudar.
Uma migração futura legítima precisa especificação e comparador lógico aprovados;
não aceitar diferença arbitrária nem exigir igualdade binária de migração autorizada.
Guardar resultados fora do repositório e dos projetos, com revisão/minimização antes
de compartilhar. Mesmo hashes e eventos são diagnósticos privados.

## Scripts existentes que NÃO são somente de leitura

`distribution/windows/msix/Test-SignedMSIX.ps1` executa **Add-AppxPackage** e
**Remove-AppxPackage**. Não executar, dot-source ou confundir com o coletor. Seus
switches RequireSac/RequireDisconnected/RequireCleanMachine são opcionais; para esta
aceitação os requisitos são obrigatórios. O helper checa origem Store após instalar;
o plano acima escolhe obtenção pela Store e origem conhecida **antes de ativar**.
Registro/services não detectam todo Python portátil/ambiente GIS. Estas limitações
estão propostas para correção futura, não foram alteradas para produzir resultado verde.

## Aprovação separada

1. **Estática:** todos os hashes/cobertura/identidade conferidos; já obtida no escopo auditado.
2. **Funcional/segurança física:** W00–W10 completos, resultados reais, rede atribuída,
   erros explicados, SAC On/Defender e clean machine preservados. **Não obtida.**
3. **Redistribuição/legal/privacidade:** fontes/avisos/rota LGPL, contratos e documentos
   revisados/aprovados por responsáveis competentes. **Não obtida.**
4. **Autorização:** proprietário decide ações futuras de envio/publicação/instalação
   separadamente. Esta auditoria não autoriza nenhuma delas.
