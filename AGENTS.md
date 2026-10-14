# AgroLines — instruções permanentes para agentes de desenvolvimento

## Missão
Desenvolver o AgroLines, aplicativo nativo Windows para planejamento agrícola, com servidor próprio, operação offline, sincronização e exportadores de monitores. Interface em português brasileiro. Não usar Supabase.

## Stack proposta
Monorepo: `desktop/` Python 3.12 + PySide6; `server/` FastAPI + PostgreSQL/PostGIS; `core/` biblioteca Python pura com Shapely, PyProj e modelos geométricos; `exporters/` adaptadores versionados; `tests/`; `docs/`; `infra/` Docker Compose; `scripts/`. SQLite local no desktop. Alembic para migrações de banco, SQLAlchemy no servidor. Testes com pytest, lint com Ruff. Preferir ferramentas open-source e interfaces estáveis.

## Regras de desenvolvimento
- Executar em etapas incrementais e testáveis. Nunca prometer compatibilidade de monitor sem validação real.
- Nunca descartar ou sobrescrever dados do usuário em atualizações; usar migrações versionadas, backups e testes de restauração.
- Não abrir PostgreSQL diretamente na internet. API HTTPS e acesso seguro por VPN privada/reverse proxy autenticado.
- Não armazenar senha em texto puro; hashing robusto, autenticação por token com expiração, autorização sempre no servidor, trilha de auditoria.
- Nunca presumir que dados em cache offline permanecem autorizados indefinidamente. Definir janela de validade e política de revogação.
- Operações offline devem usar fila durável, IDs imutáveis, idempotência, versões e resolução explícita de conflitos.
- Não depender de tiles de satélite sem respeitar licença e termos do provedor. Prever cache autorizado e modo offline.
- Geometrias em CRS apropriado para medidas métricas; preservar CRS original e converter quando necessário.
- Exportadores de monitores devem ser módulos isolados com fixtures, validação de formato e matriz de compatibilidade por modelo/firmware.
- Planejamentos de manobra são propostas geométricas, não comandos de condução automática homologados. Não exportar manobras executáveis sem suporte comprovado e validação em campo.
- Manter documentação de decisões (ADRs), comandos de instalação e testes, e exemplos de uso.
- Não adicionar credenciais, tokens, arquivos sensíveis ou dados reais de propriedades ao Git.

## Domínio
Entidades: usuários; produtores; fazendas; talhões e versões de limites; safras; operações cadastráveis; máquinas motrizes; autopropelidos; implementos; vínculos de tração; monitores (marca, modelo, firmware); parâmetros operacionais; planos de linhas; linhas/cabeceiras/manobras; pacotes de exportação; compartilhamentos; permissões; sincronização; auditoria.

## Permissões
Cada usuário tem login próprio. Compartilhamento por fazenda inteira, por safra e/ou por operação, com papéis visualizador, operador/exportador, editor, administrador e proprietário. Princípio do menor privilégio, sem vazamento entre propriedades. Compartilhar fazenda não concede automaticamente acesso aos equipamentos particulares de terceiros. Convites e alterações de acesso exigem servidor online.

## Geometria e planejamento
- Importar limites por SHP (incluindo .shx/.dbf/.prj), GPKG, GeoJSON e KML quando implementado; validar geometria, CRS, área e anéis.
- Gerar Cabeceira 1, Cabeceira 2 opcional e limite interno com offsets configurados no implemento/autopropelido e parâmetros sobrescrevíveis por planejamento.
- Gerar linhas paralelas com largura de trabalho e azimute 0–359,999 graus (0=N, 90=L), ou direção definida no mapa.
- Raio mínimo de giro por máquina motora e restrições cinemáticas do implemento; escolher manobras automáticas ou não.
- Regra específica: durante o trecho de manobra designado à Cabeceira 1, o ponto de referência do centro do trator deve acompanhar a linha da Cabeceira 1. Transições devem respeitar continuidade e curvatura; se inviável, sinalizar e não produzir trajeto inválido.
- Verificar limites do talhão, largura física, colisões e deslocamento de implementos. Evitar alegações de segurança sem testes.
- Persistir histórico de planos por talhão+safra+operação+equipamento, com versões e geometria editável; gerar SHP para intercâmbio, mas armazenar geometrias em banco.

## Exportação
Primeiro adaptador: New Holland IntelliView 12, ISOXML ISO 11783 TaskData (usar amostras SMS Basic fornecidas como fixtures quando adicionadas ao repositório, sem inferir compatibilidade). Suportar seleção de múltiplos talhões e implementos para mesma operação, com identificação clara e sem colisão de IDs. Registrar versão do monitor e capacidades. Novos adaptadores para Jacto e outros sem alterar núcleo. Não declarar suporte a execução de manobras sem evidência.

## Qualidade
Testes unitários para geometria, limites de permissão e serialização; integração para API e migrações; fixtures sintéticas; testes de sincronização com servidor indisponível e retorno; CI GitHub Actions em Linux e Windows; build Windows só após o MVP estável. Documentar dependências, licença e configuração.

## Segurança e compatibilidade Windows
- Windows 11 com Smart App Control ativo é requisito obrigatório; instalação pip e CI Windows comum não comprovam aceitação. Antes da Etapa 3.2, apresentar diagnóstico, correções viáveis e evidências/limitações de aceitação, conforme docs/windows-security.md.
- Nunca desativar ou contornar SAC, Defender, WDAC ou integridade de código; não liberar DLLs por exclusões, registro, certificados autoassinados ou carregamento alternativo.
- Preservar GEOS/GDAL/PROJ e as tolerâncias geométricas. Solicitar aprovação antes de modificar a arquitetura por conflito de segurança/precisão.
- Auditar DLL/PYD/EXE, assinaturas/cadeias e 3077/3033; distribuição exige runtime embutido, payload/instalador confiáveis e atualização verificável. Seguir docs/windows-security.md e declarar evidências ainda pendentes.

## Distribuição comercial
- Produto final Windows deve embutir runtime/dependências e ter instalador, identidade, versão, atualização e desinstalação; clientes não precisam de Python, pip, PowerShell ou PostgreSQL local configurado manualmente.
- Preservar Python/PySide6 e o núcleo GIS. Prova de distribuição só é aprovada com assinatura/auditoria e validação Windows 11 real com SAC ativo; CI hospedado não substitui essa evidência.
- Seguir docs/windows-distribution-poc.md; não iniciar funcionalidades agrícolas seguintes antes da validação dessa fundação. Não usar publisher/certificado fictício nem adquirir serviços pagos sem autorização.

## Offline e licenciamento
- Projetos de propriedade local devem abrir e funcionar sem conta ou autenticação remota; dados compartilhados mantêm a política de autorização/revogação da ADR 0002.
- Seguir docs/offline-and-licensing.md e ADR 0004: SQLite integrado, originais/SRC/precisão preservados, revisões imutáveis, backups e conflitos explícitos; PostgreSQL/PostGIS é serviço opcional de colaboração.
- Licenciamento é independente do núcleo agrícola; manter desenvolvimento desbloqueado. Chaves privadas de emissão nunca entram no aplicativo. Licenças offline válidas não exigem heartbeat remoto; não coletar hardware/PII sem necessidade e transparência.
- Fundação offline foi autorizada como incremento atual; novos algoritmos agrícolas continuam condicionados à validação Windows/SAC. Aceitação offline exige Windows real desconectado, sem Python/PostgreSQL instalados, não apenas documentação/CI.
