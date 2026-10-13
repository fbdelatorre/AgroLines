# Primeiro comando para o Codex — Etapa 1

Leia integralmente `AGENTS.md` e `PROMPT_MESTRE_CODEX.md` neste repositório. Execute **somente a Etapa 1** do AgroLines.

Entregue:
1. Monorepo organizado com `desktop/`, `server/`, `core/`, `exporters/`, `tests/`, `infra/`, `docs/`, `scripts/` e README em português.
2. `server/`: aplicação FastAPI mínima com `GET /health`, configuração por variáveis de ambiente, preparação para PostgreSQL/PostGIS e migrações Alembic, sem expor credenciais.
3. `desktop/`: janela PySide6 nativa Windows com navegação inicial (Painel, Produtores, Fazendas, Talhões, Safras, Operações, Máquinas, Implementos, Planejamentos, Exportações, Configurações). Seções não implementadas devem estar claramente marcadas como 'Em desenvolvimento'. Mostrar indicador de conexão usando healthcheck real e tratamento de falhas; sem fingir sincronização.
4. `core/`: modelos tipados iniciais e separação entre domínio e UI, sem implementar geometria avançada nesta etapa.
5. `infra/`: Docker Compose para API, PostgreSQL/PostGIS e volume persistente, configuração de exemplo `.env.example`, documentação de backup inicial e segurança de rede. Não publicar porta do banco para a internet.
6. `tests/`: testes mínimos da API, configurações e inicialização dos componentes testáveis sem interface gráfica. Ruff e pytest.
7. GitHub Actions para lint e testes em pull requests, e `.gitignore` adequado (SQLite, backups, secrets, envs, dados de clientes).
8. `docs/architecture.md`, `docs/roadmap.md`, `docs/permissions.md` e ADR inicial explicando offline-first, servidor próprio e separação de exportadores.

Critérios de aceite: API sobe localmente e `/health` responde; janela desktop abre no Windows com instruções claras; testes passam; serviços usam volumes persistentes; repositório não contém segredos; README fornece comandos exatos de instalação, execução e teste. Não implementar login fictício, sincronização fictícia, exportador fictício ou geração de linhas nesta etapa. Se não puder executar testes de GUI Windows no ambiente Codex, documente essa limitação e forneça checklist de teste manual.

Ao final, mostre resumo, comandos para rodar e evidências dos testes. Não avance para a Etapa 2 sem solicitação.
