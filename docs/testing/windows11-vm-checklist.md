# Homologação manual — Windows 11 Pro / Hyper-V

**Preencher durante a execução. Nada está aprovado só por constar neste checklist.**
Use exclusivamente os arquivos sintéticos do pacote privado. Não use dados pessoais,
clientes ou propriedades reais. Registre APROVADO / FALHOU / NÃO EXECUTADO / NÃO
IMPLEMENTADO, versão, commit, data/hora, código do evento e evidência para cada caso.
CI Windows Server não comprova instalação em Windows 11 ou aceitação por SAC.

## 1. Preparar a VM e preservar o hospedeiro

- [ ] Confirme Hyper-V no hospedeiro e mídia/licenciamento Windows 11 Pro legítimos.
  No **Hyper-V Manager → New → Virtual Machine**, crie `AgroLines-Teste`:
  **Generation 2**, **16.384 MB RAM**, **8 processadores virtuais**, VHDX **120 GB**.
  Depois, **Settings → Security**: Secure Boot habilitado, template Microsoft Windows
  e **Enable Trusted Platform Module**. O hospedeiro precisa ter recursos suficientes.
- [ ] Instale/atualize Windows 11 Pro na VM. Não instale Python, pip, QGIS, GDAL,
  PostgreSQL, Visual Studio, Node.js ou Docker nela. A VM de build/servidor é separada.
- [ ] Mantenha Defender, firewall, Secure Boot e vTPM ativos. Não instale certificados
  de teste, não crie exclusões e não habilite Developer Mode. Não altere proteções
  do **hospedeiro**. Use rede virtual para download privado e rede de laboratório
  configurada pelo titular para HTTPS do servidor, sem exposição na internet.
- [ ] Registre versão/build Windows e o estado visível de SAC em **Windows Security →
  App & browser control → Smart App Control**. Estado ausente/desconhecido não é
  “ativo”. Fotografe/capture a tela sem dados pessoais. Não presuma que toda VM tenha SAC.
- [ ] Com a VM desligada, no Hyper-V Manager, crie checkpoint **ANTES-AGROLINES**.
  Registre a data, configuração e estado inicial. Checkpoint não é backup durável.
- [ ] Baixe os instaladores/relatórios pelo [canal privado](private-installer.md).
  Compare SHA-256 pelo **Get-FileHash** ou ferramenta equivalente antes de executar:

```powershell
Get-FileHash 'C:/Teste/AgroLines-Setup-1.0.0.7-TESTE-x64.exe' -Algorithm SHA256
```

  O hash esperado é o da **sua execução privada**, não o hash antigo do #23.
  PowerShell aqui é ferramenta do operador; não é dependência do aplicativo.
- [ ] Opcional, com o script desta revisão copiado pelo titular, dentro da VM:

```powershell
./scripts/Collect-VMTestEnvironment.ps1 -Output C:/Teste/evidencias/inicial.json -Phase initial -Installer C:/Teste/AgroLines-Setup-1.0.0.7-TESTE-x64.exe
```

  O script só lê estado e cria arquivo novo. Não copia nome de usuário, SID, chaves
  ou projetos. Revise mesmo assim antes de compartilhar. Estados desconhecidos ficam pendentes.

## 2. Instalação e eventual bloqueio

- [ ] Tente iniciar o EXE. Ele é **experimental e não assinado**. Se SAC bloquear,
  registre mensagem, horário e hash. Colete CodeIntegrity 3077/3033/AppModel pelo
  roteiro existente em `docs/windows-signing/`, sem habilitar/desabilitar políticas.
  Não marque o instalador como compatível com SAC.
- [ ] **Opção explícita autorizada pelo titular somente nesta VM descartável:** após
  registrar o bloqueio/estado inicial e confirmar checkpoint, o titular pode optar
  por desligar SAC na **Windows Security da VM → App & browser control → Smart App
  Control → Off**. Nenhum script deste projeto faz isso. Não se aplica ao hospedeiro,
  não autoriza desligar Defender/firewall/Secure Boot e não contorna políticas geridas.
  Pode ser necessário restaurar checkpoint/reinstalar a VM para recuperar o estado
  inicial; não prometa que o botão permite reativar. Se a opção não estiver disponível,
  pare. Esses resultados serão **testes funcionais com SAC desligado**, nunca homologação SAC.
- [ ] Execute o instalador, escolha pasta exclusiva com acentos e espaços, por exemplo
  `C:/Program Files/AgroLines TESTE Açúcar`. Confira nome, ícone e versão 1.0.0.7.
- [ ] Instale com atalho desktop marcado; confira **Menu Iniciar → AgroLines TESTE**,
  atalho da área de trabalho e registro em **Settings → Apps → Installed apps**.
- [ ] Abra por ambos os atalhos, sem terminal. Deve aparecer a identificação TESTE.
  Não copie DLLs ou configure PATH. Qualquer pedido de dependência externa é falha.
- [ ] Tente uma pasta que pertença a outra instalação AgroLines: deve haver recusa,
  sem sobrescrever. Cancele uma atualização interativa e confirme a preservação.

## 3. Ativação e operação offline

- [ ] Siga o [laboratório HTTPS](test-license-lab.md). Ative usando conta/chave fictícias
  do servidor correspondente ao build; não use e-mail ou chave real de cliente.
- [ ] Feche e reabra: licença preservada por DPAPI no mesmo perfil Windows.
- [ ] Desligue o adaptador de rede **da VM** nas configurações Hyper-V. Não desligue
  o adaptador do hospedeiro. Abra novamente: licença válida permite trabalho offline.
- [ ] Abra a janela principal, redimensione e confira legibilidade em 100%, 125% e 150%.
  Confira painel de camadas, splitter, status, controles existentes e ausência de
  colaboração online. Não há imagens de satélite remotas disponíveis neste perfil.
- [ ] Confirme Leaflet local sem página vazia, erro de JS ou recursos de rede.
  Aplique zoom/pan, escolha feição/camada, confira realce e coordenadas do cursor
  (ponte Python/JavaScript). Registre controles inexistentes como não implementados.
  As verificações automáticas da ponte complementam, não substituem, cliques reais.

## 4. Projetos e cinco formatos GIS

- [ ] Em pasta de dados **fora da instalação**, clique **Novo**, nomeie `TESTE fictício`
  e selecione `.agrolines`. Salve/feche/abra com **Abrir**. Não existe obrigação de um
  botão “Salvar projeto” separado: edições confirmadas são persistidas em transação.
- [ ] Use `synthetic-gis/TESTE.shp` com todos os sidecars `.shx/.dbf/.prj/.cpg` juntos.
  Clique **Importar**, confira avisos/SRC, selecione a feição e visualize o contorno.
- [ ] Repita em projetos separados para `TESTE.gpkg`, `TESTE.kml`, `TESTE.kmz` e
  `TESTE.geojson`, evitando confundir sobreposição/duplicação com falha de importação.
  SHP/GPKG usam EPSG:32723; KML/KMZ/GeoJSON usam EPSG:4326.
- [ ] Confira coordenadas numéricas. O quadrado sintético tem lado **100 m na grade
  UTM**, área **10.000 m² na grade**. Não é distância/área de terreno corrigida.
  Transformações geográficas possuem arredondamentos; as 22 referências existentes
  são a evidência computacional adicional, não uma promessa de precisão de campo.
- [ ] Selecione feição → **Editar vértices**, anote Leste/Norte e vértice; altere
  Leste em **0,001 m**, clique **Aplicar**, **Desfazer**, **Refazer**, **Salvar**.
  Reabra projeto e diálogo; confirme a alteração e nova revisão. O diálogo usa
  coordenadas de trabalho métricas, preservando SRC original dos dados.
- [ ] Consulte histórico se existir controle visual; caso não exista, registre
  “persistência de revisões testada automaticamente, consulta visual não implementada”.
  Não invente botão de histórico.
- [ ] **Backup** em novo `.agrolines`, **Restaurar** em outro arquivo, reabra e compare
  feições/coordenadas. O arquivo anterior não deve ser sobrescrito silenciosamente.
- [ ] **Exportar dados** produz **GeoJSON** no cliente comercial atual. Abra o exportado
  em outro projeto e compare geometria/revisão/SRC e coordenadas. Não marque exportação
  SHP/KML/GPKG ou exportadores de monitores como implementados por existirem importadores.
- [ ] `LINHA-NAO-SUPORTADA.geojson` é caso **negativo**: o importador deste workspace é
  de polígonos. Deve recusar/avisar sem corromper o projeto. Não implementar linhas,
  curvas, cabeceiras ou novos algoritmos para passar este checklist.
- [ ] Visibilidade: testar controles presentes. Se um checkbox individual não existir
  na UI atual, registrar a ausência; o teste automático Leaflet hide/show não prova
  que há um botão operacional na interface. Não apresentar ferramenta futura como aprovada.

## 5. Licenciamento e rede

- [ ] Reconecte só a VM e clique **Minha licença → Verificar licença agora**.
- [ ] Teste Mensal/Anual, duas vagas e terceira recusada conforme o roteiro do servidor.
- [ ] Renove, verifique e reinicie. Para expiração offline curta, use `short-expiry`,
  receba a licença atualizada, desconecte e aguarde sem alterar o relógio do Windows.
- [ ] Pare o servidor e confirme que timeout não trava a janela nem invalida licença
  local ainda válida. Reinicie o servidor depois.
- [ ] Revogação é o último caso: reconecte/verifique/reinicie e confira bloqueio de
  novas edições e recuperação/exportação dos dados preservadas. Não prometa revogação
  imediata enquanto a VM estiver offline sem receber a decisão.

## 6. Atualização, desinstalação e diagnóstico

- [ ] **Antes da revogação**, feche o app e instale 1.0.0.8 da mesma execução privada
  na mesma pasta. Confirme a atualização; projetos, licença e runtime anterior preservados.
- [ ] Abra 1.0.0.7 pelo atalho **Versões** e 1.0.0.8 pelo atalho principal, uma de cada vez.
- [ ] Desinstale pelo Windows. Atalhos/registro próprios removidos; projetos, backups,
  `TestProfile/license.dpapi` e âncora externa devem permanecer. Reinstale e reabra.
  Não remova pastas de dados manualmente antes de conferir a preservação.
- [ ] Na barra **Licença → Diagnóstico**, escolha eventos e, opcionalmente, módulos
  nativos. Revise o JSON e só então salve ZIP. Cancelar não deve criar arquivo.
  O ZIP contém apenas `diagnostico.json` e `LEIA-ME.txt`; não envia nada automaticamente.
  Registre códigos de correlação, versão/commit, Windows, etapa, erro sanitizado e DLLs.
- [ ] Se não abrir: **Win+R → `%LOCALAPPDATA%/AgroLines/Diagnostics`**; guarde logs
  rotativos `desktop.log[.1/.2]`. Não inclua `license.dpapi`, registry, chaves do
  servidor, perfis WebEngine, projetos ou dump de memória. Revise antes do suporte.
  Falhas anteriores ao Python/logger podem exigir eventos Windows e não ter desktop.log.
- [ ] Guarde resultados/checksums/capturas somente em armazenamento privado autorizado.
  Separe erro reproduzível, passos, resultado esperado/real e evidência sanitizada.
  Não mande dados de clientes para issues públicas.

## 7. Critério de encerramento

- **Funcional na VM:** casos implementados passaram, dados preservados, nenhum crash
  inexplicado, recursos GIS locais e 22 referências computacionais preservados.
- **SAC aprovado:** somente se instalação e operações reais passaram com SAC ativo
  confirmado e origem/assinatura legítimas. Executar com SAC desligado não satisfaz isso.
- **Produção/comercial:** continuam pendentes assinatura, serviço real e condições
  anteriores. Este roteiro não aprova EULA, privacidade, licenças ou comercialização.
