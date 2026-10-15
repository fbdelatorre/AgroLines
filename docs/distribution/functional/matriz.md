# Matriz funcional — funcionalidades existentes

Use somente dados sintéticos. A coluna automática identifica verificações
executáveis; o estado final exige consultar o relatório da execução, não esta lista.
Teste manual significa evidência adicional emWindows11 real, sem alterar proteções.

| Área/caso | Verificação automatizada existente ou adicionada | Conferência manual posterior |
|---|---|---|
| Criar/abrir/salvar/reabrir `.agrolines` | offline_checks com verificador real de licença sintética; probes congelados e instalado | Operar pela interface, fechar e reabrir |
| Backup/restauração | Comparação de geometrias e revisões, cópia SQLite íntegra | Selecionar backup e destino próprios |
| Histórico | Duas revisões após edição; persistência entre processos/versões | Consultar versões na tela |
| SHP/GPKG/KML/KMZ/GeoJSON | store_probe gera/importa cinco formatos locais | Arquivos sintéticos adicionais e validação de erros |
| Camadas/vetores/visibilidade | Python envia coleção ao Leaflet; esconde/restaura camada no renderizador | Controles da lista/painel e resolução do monitor |
| Seleção | JavaScript seleciona feição e evento chega ao Python por WebChannel | Clique físico no mapa e seleção pela lista |
| Edição de vértices/salvar | LocalVertexDialog numérico, alteração de1mm, persistência | Campos, ferramentas e mensagens de validação |
| Desfazer/refazer | Reversão/reaplicação e histórico do projeto | Sequência mais longa pela interface |
| SRC/transformações/unidades | 22referências; SRCoriginal preservado e transformaçãoUTM | Comparar coordenadas conhecidas emSRC adequado |
| Mapaoffline | Leaflet/JS/CSS locais, WebEngine pronto | Rede fisicamente desconectada |
| Zoom/pan/vetores | Funções reaisLeaflet, resultados deviewState e visibilidade | Mouse/teclado/escalaWindows |
| Coordenadas/ponteJS↔Python | Evento de cursor atualizaEPSG32723 no painel | Conferência de ponto sintético conhecido |
| Sem serviços remotosGIS | Tentativas fetch/image/WebSocket e sockets recusadas; PROJnetworkdesativado | Trace/proteções e desconexãofísica |
| Ativação inicial e duas vagas | CicloAPI sintético, testes de concorrência e assinatura do#21 | HTTPS implantado, doisPCs e terceiro recusado |
| Offline apósativação | Assinatura sintéticaDPAPI válida no congelado/instalado | Desconexão real até validade contratada |
| Renovação/expiração/revogação | Suíte comercial e restauração de arquivo antigo após revogação | Servidor real, relógio e persistência após reboot |
| Falha de rede/servidor | Timeout/503 não revogam licença local válida; GUI assíncrona | Endpoint real lento/indisponível |
| Reinício/atualização/reinstalação | Vault/âncora/projetos externos preservados no cicloInno | PerfilWindows real autorizado |
| Launcher/atalhos/ícones | AtalhoShell para launcher instalado e UI; recursos oficiais embutidos | ÍconeStartMenu/taskbar, ausência de console |
| Caminho com espaços/acentos | Instalação e execução reais em pasta sintéticaUnicode | Pasta escolhida pelo testador |
| Versões ladoalado | Runtime anterior preservado porhash e executado após instalar sucessor | Abrir atalhos porversão, fechar antes de atualizar |
| Desinstalação | Launcher/registro próprios removidos, arquivos externos preservados | Conferir projetos/backups e pastas restantes |
| DLLs/PYDs | Manifesto porhash e módulos observados comPATHsistema | Máquina limpa sem ferramentasGIS/Python |
| Diagnósticos | Loglocal com rotação e teste de não registrar mensagem/segredo | Solicitação manual de trecho mínimo ao suporte |

Colaboração, convites, APIagrícola remota ePostgreSQLcliente continuam indisponíveis
neste perfil. As regras preservadas do backend são testadas nas suítes apropriadas;
isso não é funcionalidade exposta pelo pacote. Ferramentas agrícolas futuras,
exportadores de monitores e telas ainda não operacionais não são aprovados por
esta matriz. Base de mapa vetorial offline não significa imagem de satélite local.
