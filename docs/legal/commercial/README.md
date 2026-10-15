# Regularização material e licenciamento comercial — PR #21

Dependente do PR #20, preservando #18/#19 e main. Este é trabalho implementado,
ainda não uma distribuição comercial aprovada. A tabela por componente está em
[licencas-componentes.md](licencas-componentes.md). As evidências de CI do commit
final e os resultados consolidados ficam na descrição do [PR #21](https://github.com/fbdelatorre/AgroLines/pull/21).
Os relatórios anteriores continuam históricos, sem alteração dos seus candidatos.

## 1. Correções materiais, antes do licenciamento

- Fontes de terceiros passam a acompanhar a pasta da versão, dentro de
  `third-party-sources/AgroLines-Third-Party-Sources.zip`: 24 arquivos de fontes
  fixados por versão/commit/hash, com licenças, receitas e patches explicitamente
  selecionados. Nenhum varrimento de diretórios privados ou fonte própria. O ZIP
  não é publicado nos artefatos desta branch. Os manifests públicos registram seu
  hash e associação ao payload. Isso implementa entrega local; a suficiência da
  modalidade jurídica depende das licenças e das lacunas expressamente restantes.
- O instalador inclui esse ZIP e atalho para ele; o gate antes da compilação e o
  log Inno verificam inclusão. Não executamos o instalador AgroLines. A entrega
  não depende de um link temporário Actions como oferta durável de fontes.
- GEOS3.11.3/Fiona e3.14.1/Shapely são reconstruídos das fontes fixadas e entregues,
  sem patch de algoritmo/header. Apenas OUTPUT_NAME noCMake conserva os nomes de
  DLL importados. Verificamos exports exigidos e a arquitetura; os quatro DLLs
  têm novos hashes e procedência de build próprios. O candidato antigo não muda.
- libaecBSD continua no lugar do encoderSZIP restritivo, com6 testes nativos,
  oito casosHDF5 e leitura pelo decoder original, sem executar o encoder antigo.
- Eleitas alternativasMPL1.1 para arquivos cobertosFreeXL/SpatiaLite, preservando
  fontes, patches e avisos; isso não muda as licenças das dependências.
- Acrescentados textosPCRE2, LERCnativo/LICENSE+NOTICE, libgeotiff, libwebpPATENTS,
  Inno7.1 eNKGCCBY4/atribuições originais, além das receitasPROJ9.8.1 verificadas
  contra os checksumsSPDX. Dois documentos de um tagJS não são atribuídos ao
  LERCnativo; conservam-se só como pesquisa. Há74 registros suplementares,
  dos quais72 se destinam a componentes empacotados, com hashes explícitos.
- O gate agora verifica também502 recursos nãoPE deGIS/Qt/Leaflet/CA, contrapondo
  hashes ao inventário auditado. Não se limita aos DLLs. Recusa recurso novo ou
  alterado, textoHTML/TXT desatualizado, versão/hash nativo divergente e membro
  não autorizado no kit de fontes, mesmo com sidecar internamente consistente.
- Novos componentes do cliente comercial têm lock separado e origem no wheel
  oficial: PyNaCl1.6.2/libsodium, cffi2.0.0/libffi epycparser2.23 quando realmente
  congelado. Textos originais, copyrights e hashes são incorporados ao inventário.
  A bibliotecaCryptography usada para emissão/AESGCM permanece só no servidor;
  não é adicionada ao instalador. Não ignoramos os termos dos componentes estáticos.

A primeira validação completa dessas correções ocorreu antes do commit do serviço:
[Windows38779063513](https://github.com/fbdelatorre/AgroLines/actions/runs/38779063513),
headc5d0988, merge de teste2471c1159ea8. Foram169 documentos/178PE/502recursos,
GIS/offline/congelado e mecanismo de bindings aprovados. Instalador experimental
1.0.0.3, não instalado/não distribuído, SHA256
`cd60190aa93788998c195fe2ea2c98d2e256f742b69cd17dbc6fd51f433ab2ab`.
Esse resultado não é atribuído ao perfil comercial posterior ou às adições seguintes.

## 2. Serviço comercial funcional e isolado

[Instruções do servidor](servidor.md),
[matriz de testes](testes.md),
[EULA proposta](EULA.md) e [política proposta](politica-privacidade.md).

- FastAPI separado, PostgreSQL no servidor, migração0006 aditiva. O aplicativo
  cliente não instala PostgreSQL, Python, pip ouDocker. A API antiga de colaboração
  não recebe essas rotas por simples configuração de cliente.
- Assinatura mensal/anual por usuário, duas posições1/2 impostas no banco. Duas
  chaves aleatórias de256bits, somente hashes armazenados. Ativação serializada
  por assinatura/vaga e atualização condicional; terceiro computador recusado.
- EmissãoEd25519 com chave privada somente no servidor. Cliente contém chave(s)
  pública(s), verifica os bytes assinados antes de interpretar formato/revisão/
  instalação/validade/módulos. Não há segredo compartilhado embutido no cliente.
- Primeira ativaçãoHTTPS; perfil comercial compilado com origem fixa. Não habilita
  colaboração, recuperação de senha ou serviçosGIS remotos. Os perfis antigos
  Store/standalone exclusivamente offline continuam fechados e não têm botão ou
  configuração do usuário para mudar esse comportamento.
- Após ativação, validade offline até a expiração assinada, sem janela7/15/30dias.
  Consulta assíncrona no início e a cada15min quando em execução, com timeout;
  falhas não revogam. Revogações assinadas/revisões ficam em registroDPAPI
  independente do arquivo local; restaurar só o arquivo antigo não elimina a decisão.
  As instâncias usam mutexWindows porperfil e recarga/mescla das revisões e revogações;
  uma instância antiga não pode sobrescrever decisões confirmadas poroutra. Arquivo
  DPAPI é gravado por substituição atômica, comtemporário exclusivo eflush. Uma
  resposta atrasada para outra ativação não substitui a licença atual.
- DPAPI por perfilWindows, UUID aleatório estável, sem coleta de MAC/serial/CPF.
  A identidade representa instalação/perfil, não atestado físico anticlonagem.
  Reinstalação no mesmo perfil preserva dados/registro; novo perfil exige tratamento
  de substituição. Administrador local continua capaz de manipular seu sistema.
- Detecção proporcional de retrocesso de relógio. Após correção legítima de uma
  data antes adiantada, nova respostaHTTPS assinada/revisada permite reconciliar
  a âncora. Ausência de rede não corrige inconsistência nem renova licença vencida.
- Painel administrativo com senhaArgon2+TOTP, antirreplay, sessão10min em memória,
  perfisviewer/manager/owner, checagem no servidor e auditoria mínima. Criar/corrigir
  usuário, criar/renovar/suspender/retomar/revogar assinatura, substituir/liberar
  vaga, revogar ativação e consultar histórico. Sem cobrança ou alegações de pagamento.
- UI de ativação/status/dispositivos/suporte integrada à janela local existente.
  Licença expirada/revogada mantém leitura, exportação e backup/restauração. Edição
  de vértices já iniciada conserva permissão apenas daquela operação para salvar.
  Registro de licença danificado abre modo de recuperação, sem apagar projetos.

## 3. Evidências e limites

O fluxo sintético completo também foi aprovado com PostgreSQL real, incluindo três
requisições concorrentes à mesma vaga:
[execução38781435680](https://github.com/fbdelatorre/AgroLines/actions/runs/38781435680).
Valida regras, transações e migrações; não é implantaçãoHTTPS pública. A emissão
sintética não é assinaturaWindows nem uso de certificado de teste para instalar.

O workflowstandalone constrói primeiro a referência offline e depois o perfil
comercial experimental1.0.0.4, sempre no builder descartável autorizado, conservando
as fontes e os paresGEOS/libaec já preparados. Executa provasDPAPI, licença local,
reabertura, revogação, GUI eGIS. Publica SOMENTE evidências: não envia executável,
runtime, instalador ou kit de fontes nesta branch. Valores exatos do candidato
estão no `evidence/commercial/artifact.json` da execução aprovada correspondente.

Não houve instalação, assinatura, compra, cobrança, mensagem a fornecedor, alteração
Store/Pages, merge ou mudança de visibilidade. O MSIX referênciaSHA256
`e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b`
continua intacto. Nenhuma proteçãoWindows foi modificada. CIWindowsServer e provas
extraídas não demonstramWindows11/SAC ou o ciclo instalado.

## 4. Bloqueios reais antes de clientes

1. **Fontes/avisos exatos ainda faltantes:** Qt/PySide/Shiboken/Chromium/PDFium e
   fornecedores estáticos/vendorizados/bases especificados na tabela. Pesquisa
   adicional está em[records](records/); inclusive branches6.140/6.140.0 e
   tagsbeta/rc: todas mantêm.264,
   enquanto o runtime observado é.225. Não foi provada correspondência final.
   Ambiente localLinux com menos de5GiB livres emworkspace, semMSVC, não comporta
   reconstruçãoWindowsChromium. Rebuild de outrocommit não provaria o binário real.
   A alternativa mínima é obter os materiais exatos; rebuild em builder dimensionado
   só após fixar revisão e testar compatibilidade. Troca porWebView2 exigiria novo
   host/bridge e homologação, não é alteração mínima comprovada nem foi fingida.
2. **Revisão delimitada:** LGPL3/2.1, eleição/entregaMPL/fontes, exceçãoGCC concreta,
   termosMicrosoft de redistribuição, EULA/consumidor eLGPD. Não é necessário pedir
   autorização individual comercial para todas as bibliotecas permissivas.
3. **Decisões do titular/infraestrutura:** identificação e condições contratuais,
   domínioTLS/hospedagem/operador, chaves privadas/recuperação, contaTOTP/admin,
   retenção comercial/logs, fornecedor/região/transferências, aceite, implantação
   e testesHTTPS reais. Não há certificado, hospedagem ou gateway comprados.
4. **ConfiançaWindows:** assinatura legítima devidas, pacote final e instalação/
   atualização/desinstalação emWindows11 físico comSAC/Defender ativos, incluindo
   estado de licença, arquivos locais, testesoffline e eventosCodeIntegrity.
   Permanecem os roteiros anteriores; não instalar o diagnóstico não assinado.

Não há evidência técnica que obrigue comprarQtCommercial ou trocar o motorGIS.
Não se declaraCommunity automaticamente regularizada, LGPD integralmente atendida
ou sistema pronto para venda sem esses passos. Minutas e mecanismos entregues
reduzem pendências; sua adoção depende de completar fatos e validações indicados.
