# AgroLines
Etapa 1: esqueleto de aplicativo nativo Windows e servidor próprio. Todas as telas
estão **Em desenvolvimento**. Não há login, cadastros persistentes, sincronização,
planejamento geométrico nem exportadores. Não usa Supabase.

## Desenvolvimento (Python 3.12)
Linux:
```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,desktop]'
ruff check .
ruff format --check .
pytest
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,desktop]"
ruff check .
ruff format --check .
pytest
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
Em outro terminal ativado, execute `python -m desktop.main`.
`AGROLINES_API_URL` define o endereço do servidor (padrão http://127.0.0.1:8000).
A verificação ocorre a cada 10 segundos, com timeout de 3 segundos, fora da thread
principal. Não há indicador fictício de sincronização.

## API e banco
`GET /health` retorna `{"status":"ok","service":"agrolines","version":"0.1.0"}`.
É liveness do processo, não prova de conectividade com banco. A API isolada não exige
banco nesta etapa. Não há endpoints de domínio ou autenticação.
Configuração por `AGROLINES_APP_NAME` e `AGROLINES_DATABASE_URL` (PostgreSQL com psycopg).
A URL é tratada como segredo e não é devolvida pela API.

Com Docker e Compose instalados:
1. Copie `.env.example` para `.env` na raiz e preencha senha e URL correspondente.
2. Execute `docker compose --env-file .env -f infra/compose.yaml up --build -d`.
3. Execute `curl http://127.0.0.1:8000/health` (PowerShell: `Invoke-RestMethod`).
4. Inspecione `docker compose --env-file .env -f infra/compose.yaml logs api` em caso de erro.

O banco não publica portas. A API publica apenas em loopback. Não exponha esta API
sem autenticação à internet. A migração `0001` habilita PostGIS e mantém a extensão
em downgrade para preservar dados. Execução manual: `alembic upgrade head`, com
`AGROLINES_DATABASE_URL` definido para um banco autorizado. Não existem tabelas
de domínio ainda. PostgreSQL usa volume persistente; **não use `down -v` em dados reais**.

## Validação Windows manual
- Iniciar API e desktop; confirmar janela, navegação e rótulos em português.
- Confirmar Servidor online após resposta real de `/health`.
- Parar a API e aguardar próxima consulta; confirmar Servidor offline e UI responsiva.
- Reiniciar API; confirmar recuperação automática.
- Fechar janela durante consulta; confirmar encerramento sem thread destruída.
- Conferir escala de tela/acentos e instalação em máquina Windows limpa.

A CI executa lint e testes sem GUI em Linux e Windows. GUI nativa Windows exige
checklist manual; um teste offscreen Linux não demonstra compatibilidade Windows.
Veja [arquitetura](docs/architecture.md), [permissões](docs/permissions.md),
[roadmap](docs/roadmap.md) e [backup](docs/backup.md).
