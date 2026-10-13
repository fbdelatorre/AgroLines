# Prompt mestre para Codex — AgroLines

Você é o engenheiro principal de um projeto novo chamado **AgroLines**. Desenvolva um sistema profissional de planejamento agrícola, com **aplicativo nativo Windows**, **servidor próprio** e **sincronização offline-first**, usando um repositório GitHub. Interface e documentação de uso em português brasileiro.

**Leia e obedeça o arquivo `AGENTS.md` do repositório como contrato técnico permanente.** Se ainda não existir, crie-o com o conteúdo do arquivo AGENTS.md fornecido junto deste prompt.

## Objetivo
O usuário cadastra produtores, fazendas, talhões, safras, operações, tratores, autopropelidos, implementos e monitores; importa limites externos; gera cabeceiras, limite interno, linhas de trabalho por azimute e, quando viável, manobras automáticas; visualiza no mapa de satélite; armazena histórico por operação/equipamento; exporta conjuntos selecionados para monitores agrícolas, inicialmente New Holland IntelliView 12.

## Requisitos funcionais
1. Login individual e permissões; compartilhamento de propriedades inteiras ou acesso restrito a safras e operações, inclusive combinações específicas. Convite e revogação pelo proprietário/admin autorizado. Papéis visualizador, operador/exportador, editor, administrador, proprietário. Restrições verificadas no servidor, não só na UI.
2. Hierarquia produtor → fazenda → talhão, com safras e operações configuráveis. Talhão tem geometria original versionada, área calculada, CRS e histórico.
3. Cadastro de máquina motora ou autopropelida: nome, marca, modelo, identificador, monitor (marca, modelo, firmware/versão), raio mínimo de giro, dimensões, comportamento de direção, velocidade de manobra, restrições e política de retorno (Cabeceira 1 ou livre).
4. Cadastro de implemento: nome, marca, modelo, largura de trabalho, distâncias configuráveis do limite externo à Cabeceira 1, Cabeceira 2 opcional e limite interno; vínculos com uma ou mais máquinas motrizes compatíveis; geometria, dimensões e parâmetros cinemáticos. Os valores precisam de definição geométrica explícita (offsets absolutos versus relativos) na interface.
5. Planejamento: selecionar talhão(ões), safra, operação, implemento(s), trator quando necessário, número de cabeceiras, raio de giro e azimute; gerar geometrias preservando versões. Permitir gerar só cabeceiras/limite, ou também linhas paralelas de trabalho, ou ambas.
6. Linhas paralelas com azimute editável numericamente e por direção desenhada no mapa, largura de trabalho e ajustes de deslocamento. Exibir prévia e métricas.
7. Manobras opcionais com cálculo de viabilidade. Se configuradas para Cabeceira 1, o centro de referência do trator acompanha essa linha no trecho designado; transições e retorno respeitam raio de giro e demais restrições. Alertar e recusar manobras inviáveis. Para implementos tracionados, modelar trajetória do implemento de forma separada. Não confundir linhas geométricas com automação de direção homologada.
8. Mapa com imagem de satélite sob licença adequada e camadas: limites, cabeceiras, limite interno, linhas de plantio, manobras. Filtros por produtor, fazenda, talhão, safra, operação, máquina e implemento. Ao abrir máquina, listar/mostrar planos dela; ao abrir talhão, mostrar planos filtráveis por operação.
9. Exportação de SHP com sidecars e, por adaptador, formatos nativos de monitores. Inicialmente ISOXML do IntelliView 12 baseado em amostras exportadas pelo SMS Basic, mas validar rigorosamente. Exportar um, vários ou todos os talhões, por operação, para um ou mais implementos, inclusive duas plantadeiras alternativas no mesmo trator; identificar planos inequivocamente no monitor. Pacotes exportados versionados, com manifesto e relatório de validação.
10. Desktop deve funcionar offline com SQLite local, fila durável de alterações e sincronização bidirecional quando o servidor retornar. Exibir estado 'Servidor offline' e pendências. Resolver conflitos explicitamente. Revogações têm limitações offline documentadas, com prazo de validade do cache e criptografia local quando aplicável.
11. Servidor próprio sempre ligado: FastAPI, PostgreSQL/PostGIS, armazenamento de arquivos, API segura, backups automatizados externos e restauração testada. Não usar Supabase. Instalação via Docker Compose, com instruções Windows/Linux.
12. Atualização frequente de aplicativo e exportadores com versões, migrações de banco seguras, backups e rollback. Nenhuma atualização pode apagar cadastros ou planejamentos. Distribuição do instalador por releases assinadas quando disponível.

## Arquitetura inicial
Monorepo `desktop/`, `server/`, `core/`, `exporters/`, `tests/`, `infra/`, `docs/`, `scripts/`. Python 3.12, PySide6, FastAPI, SQLAlchemy/Alembic, PostgreSQL/PostGIS, SQLite, Shapely, PyProj, GDAL/OGR conforme necessidade, pytest, Ruff, GitHub Actions. Use tipagem e contratos claros; separe domínio de interface e persistência. Registre decisões arquiteturais.

## Processo obrigatório
Não tente implementar todo o projeto de uma vez. Primeiro: analise requisitos, liste dúvidas que bloqueiam decisões irreversíveis, proponha arquitetura, esquema de dados, contratos de API, matriz de permissões, estratégia offline/sync, motor geométrico e cronograma de incrementos. Em seguida, implemente SOMENTE a etapa solicitada pelo usuário. Cada etapa deve produzir código funcional, testes automatizados, documentação de execução e critérios de aceite. Não simule funcionalidades inexistentes como se estivessem prontas. Não faça commits com segredos ou dados reais. Crie PRs pequenos, com resumo de mudanças, testes e limitações.

## Ordem de implementação
1. Esqueleto do monorepo, infraestrutura local, API de saúde, janela desktop mínima, configurações, CI, documentação.
2. Autenticação, autorização e compartilhamento por fazenda/safra/operação.
3. Cadastros, geometrias, importação e versionamento.
4. Mapa e visualização de camadas.
5. Cabeceiras e limites internos com testes geométricos.
6. Linhas por azimute.
7. Planejamento e verificação de manobras.
8. Exportador ISOXML IntelliView 12, testes com amostras e validação real.
9. Sincronização offline robusta, exportação em lote, atualizações e instalador.
10. Novos adaptadores de monitores.

Ao concluir uma etapa, apresente: arquivos criados/alterados, como executar, testes rodados, limitações e próximo passo recomendado.
