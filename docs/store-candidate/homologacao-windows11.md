# Homologação real Windows 11 — pendente de pacote confiável

Não executada neste ambiente Linux ou comprovada pelo CI hospedado. Usar somente
dados sintéticos e os pacotes entregues pelo canal confiável aprovado. O MSIX candidato
atual é **não assinado**: não instalar diretamente nem alterar Publisher/certificados.
Publicação/certificação e inclusão de testadores dependem de autorização futura.

1. Após revisão/autorização de distribuição, obter o pacote efetivamente entregue
   pela Microsoft Store ao grupo privado. Registrar versão, identidade, origem e
   assinatura. Não usar autoassinatura, Developer Mode ou AllowUnsigned.
2. Usar Windows 11 build 22000 ou superior, sem Python/pip/PostgreSQL instalados ou
   serviço de banco externo necessário. Conferir SAC **Ativado/On**, não Avaliação,
   em Segurança do Windows → Controle de aplicativos e navegador → Smart App Control.
   Conferir Defender/proteção ativa. Apenas registrar estados; não mudar proteções.
3. Instalar/abrir pela Store. Conferir ícone, interface em português, painel/mapa,
   carregamento Qt WebEngine/helpers, ausência de login/convites/colaboração. O cliente
   não deve executar terminal, pip ou configuração de servidor para abrir o app.
4. Antes de desconectar, obter fixture sintética de importação e backup local.
   Criar `.agrolines`, importar polígono SHP/GPKG/KML/KMZ/GeoJSON sintético com SRC
   conhecido, selecionar vértice, alterar coordenada numérica de modo controlado,
   desfazer/refazer, salvar e verificar versões. Fechar/reabrir e comparar valores
   com precisão disponível, preservando SRC/original. Backup/restauração em novo
   arquivo, sem sobrescrever projetos reais. Não precisa de Python no cliente.
5. Desconectar fisicamente internet/rede e repetir criação/importação/edição,
   gravação/reabertura/backup/restauração. Reiniciar o aplicativo offline. Verificar
   recursos GIS, mapa vetorial, CSS/JS/fontes locais; não exigir fundo remoto ou
   prometer camadas/algoritmos ainda não implementados.
6. Em bancada conectada separada, iniciar captura nativa aprovada do processo e
   filhos (incluindo QtWebEngineProcess) desde a abertura ao fechamento. Correlacionar
   PIDs, TCP/UDP e DNS, validar observador com tráfego positivo de processo distinto.
   Diferenciar Store/Windows de conexões próprias/helpers. Ausência de linhas em
   captura mal configurada não é prova. Não bloquear tráfego para simular sucesso.
7. Ler eventos Code Integrity 3077/3033 e avaliar cada arquivo associado ao payload,
   estado SAC e erros. Leitura com instrumentos administrativos de homologação é
   opcional para o usuário final e não requisito de uso do aplicativo. Bloqueio exige
   correção do componente/distribuição, nunca exclusão de segurança ou trust artificial.
8. Com outra versão Store confiável e autorização específica, atualizar, verificar
   hashes/valores/histórico dos projetos externos e restaurar backup. Desinstalar,
   confirmar arquivos/hashes, reinstalar e reabrir/restaurar. Não considerar o teste
   do instalador PoC ou o manifesto como evidência do ciclo MSIX.
9. Registrar resultados/versões/limitações em arquivo privado, revisando logs/eventos
   e capturas antes de eventual compartilhamento: podem conter nomes de usuário,
   caminhos, identificadores e dados de outros aplicativos. Não fazer upload automático
   nem publicar diagnósticos brutos em GitHub.

Concluir apenas após evidência real. Os relatórios do CI mantêm `sac_approved=false`,
`installed_msix_validated=false` e `native_network_trace_validated=false`.
Preservar classificação Livre/3+, audiência/grupo e licenciamento. Nenhuma ação da
Store, convite ou mudança de segurança foi realizada por esse roteiro.
