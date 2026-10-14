# Offline e licenciamento — implementação incremental

A fundação é funcional e não exige conta remota: criar/abrir projeto local,
importar polígonos SHP/KML/KMZ/GPKG/GeoJSON, visualizar no mapa local, editar
vértices numericamente em metros, salvar versões, fechar/reabrir, fazer backup e
restaurar em novo arquivo. Arquivos sem SRC exigem indicação explícita; SRC original
é preservado. PROJ não baixa grids na execução local. Um grid necessário ausente
causa erro em vez de transformação aproximada silenciosa.

Para mantenedores: `python -m desktop.main` abre projetos locais;
`python -m desktop.main --remote` mantém o fluxo anterior de autenticação.
A ação **Colaboração online** abre a interface remota existente sem converter o
projeto local em projeto compartilhado. Não existe sincronização automática.
No executável experimental use **Projetos locais · sem conexão ou login**;
`AgroLinesPoC.exe --local` também abre diretamente esse espaço.
Clientes futuros usarão atalhos/instalador, sem Python ou comandos de shell.

Use **Novo**, informe nome, SRC de trabalho (padrão EPSG:32723; altere para outra
zona quando apropriado) e caminho do arquivo. **Importar** mantém os arquivos
originais e pede confirmação dos avisos. Selecione a camada e use **Editar
vértices**: aplicar/desfazer/refazer são temporários; **Salvar** cria revisão.
**Backup** e **Restaurar** exigem destinos novos. Os arquivos pertencem ao usuário
local e dependem das permissões do Windows; não incluir credenciais/contas remotas.

## Incrementos

| Fase | Entrega e critério |
|---|---|
| Agora | SQLite local, histórico, importação/edição existentes, backup, separação remota, contratos de licença e testes sem rede |
| Fundação Windows | Assinar/auditar todo payload e instalador; executar roteiro abaixo em Windows real/SAC ativo; nenhuma aprovação apenas por CI |
| Dados agrícolas locais | Integrar hierarquia/safras/operações ao repositório local, migrações e importação dos projetos existentes sem perda; preservar API e autorização |
| GIS offline | Criar/editar também linhas e polígonos graficamente, exportar os cinco formatos, mapas de fundo locais licenciados; testes de ida/volta com SRC/Z/atributos |
| Algoritmos existentes/futuros | Execução exclusivamente local, precisão/distorção/terreno documentadas; não implementar novos cálculos agrícolas antes da validação Windows |
| Sincronização opcional | Outbox idempotente, mapeamento de IDs, revisões-base, tombstones, transações e reconciliação explícita com PostGIS; conflitos mostram ambas versões e nunca descartam silenciosamente |
| Comercial posterior | Verificador assimétrico auditado e emissão externa, ativação offline assinada/online opcional, renovação, planos, cobrança e administração |

Linhas, novos algoritmos, exportadores, mapas de fundo locais, migração automática
de projetos remotos, sincronização e licenças comerciais **não estão prontos**.
Não há botões que simulem essas funcionalidades. Eventos no banco permanecem
`local`; futuros estados pending/conflict/synced não enviam dados nesta versão.
Revisões concorrentes são detectadas localmente; conflitos remoto/local ainda
serão implementados. Não há promessa de precisão centimétrica absoluta no terreno:
continuam os relatórios/testes existentes e os limites de grade/projeção/datum.

## Verificação reproduzível

Mantenedores: `pytest tests/test_local_projects.py tests/test_offline_desktop.py`.
Testes negam socket/connect/DNS, verificam os cinco importadores, preservação Z/SRC,
deslocamento de 1 mm, histórico, transação com falha, conflito, backup e restauração.
O PoC empacotado executa também os controles Qt do editor e reabre SQLite; o campo
`offline_projects` do relatório é obrigatório para aprovação do teste de instalação.
A rede de GDAL/Qt não é interceptada pelo monkeypatch Python: PROJ tem rede
explicitamente desabilitada, KML externo é recusado e o mapa local bloqueia recursos
remotos. Isso ainda não substitui desconexão física.

Roteiro de aceitação real (registrar versão/hash do instalador e capturas/evidências):

1. Windows 11 real com SAC **On**, Defender ativo, nenhum Python instalado e
   nenhum serviço PostgreSQL instalado; registrar versão do Windows e políticas.
2. Usar somente instalador/payload assinados e auditados. Desconectar totalmente a
   internet e confirmar ausência de adaptadores/conectividade; não alterar proteções.
3. Instalar, abrir projetos locais, criar projeto EPSG:32723, importar fixture SHP
   com sidecars (ou outro formato declarado), conferir SRC e limites no mapa.
4. Editar vértice 1 mm, desfazer/refazer, salvar; fechar todas as janelas e reabrir
   arquivo. Conferir valores sem arredondamento e revisão 2.
5. Fazer backup, restaurar em novo destino e comparar histórico/geometria; testar
   arquivo existente protegido contra sobrescrita. Repetir em outra zona UTM.
6. Conferir logs CodeIntegrity 3077/3033, mapa e bibliotecas; testar atualização e
   desinstalação preservando projeto externo à pasta do aplicativo.

Resultado atual: testes de fonte/CI podem comprovar o código e o runtime embutido,
mas **aceitação Windows/SAC/desconexão física permanece pendente**. Não existe
certificado/conta de assinatura disponível; fabricante informado é a marca
Delatorre Corporation, sem identidade jurídica verificada. Seguir
[distribuição Windows](windows-distribution-poc.md) para os gates de assinatura.
