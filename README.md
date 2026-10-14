# AgroLines
Aplicativo nativo Windows para planejamento agrícola, com servidor próprio, sem Supabase.
A **Etapa 2.1** refina a interface escura e adota senhas de 6–128 caracteres.
A identidade visual segue a referência fornecida: barra superior, menu compacto
e estrutura central de mapa com painéis redimensionáveis/recolhíveis. A **Etapa 3.1** acrescenta mapa vetorial, importação de polígonos e edição numérica
como primeiro incremento da Etapa 3; veja [cartografia](docs/geography.md) e
[precisão](docs/precision.md). A Etapa 3 completa ainda não foi aprovada.
A **Etapa 2** implementa contas, autenticação, propriedades, safras/operações mínimas
para escopos, convites e permissões persistentes. A navegação da Etapa 1 e seu
healthcheck foram preservados. Talhões, equipamentos, geometria, planos, exportadores
e sincronização completa continuam **Em desenvolvimento**.

## Distribuição Windows para clientes

O produto final terá runtime embutido e instalador, sem exigir Python, pip,
PowerShell ou PostgreSQL local do cliente. A prova de distribuição ainda não está
aprovada para SAC: veja [executável, instalador e homologação](docs/windows-distribution-poc.md).
Delatorre Corporation é a marca informada, com identidade jurídica ainda não verificada.

## Desenvolvimento do servidor no Windows 11 — sem Docker
Estas instruções são para mantenedores do servidor, não para clientes.
Instale Python 3.12 e PostgreSQL com a extensão PostGIS compatível (por exemplo,
instalador PostgreSQL e PostGIS pelo Stack Builder). Docker é opcional.
A Etapa 2 foi validada pelo usuário com PostgreSQL 18/PostGIS 3.6.2 no Windows 11;
o ambiente de integração automatizado usa PostgreSQL 16/PostGIS 3.4.

No PowerShell, na raiz do checkout:
```powershell
.\scripts\Configure.ps1 -Desktop
```
Para **um banco novo**, configure uma conta própria e o banco. Não execute criação
novamente se já existirem; não apague o banco da Etapa 1. Ajuste o caminho à instalação:
```powershell
$env:Path = 'C:\Program Files\PostgreSQL\16\bin;' + $env:Path
psql --host 127.0.0.1 --username postgres --dbname postgres --password
```
No prompt psql:
```sql
CREATE ROLE agrolines LOGIN;
\password agrolines
CREATE DATABASE agrolines OWNER agrolines;
\connect agrolines
CREATE EXTENSION IF NOT EXISTS postgis;
\quit
```
`\password` solicita a senha sem incluí-la no comando. A aplicação não precisa de
superusuário. A instalação da extensão deve ser feita pelo administrador do banco.

Antes de atualizar um banco existente, siga [backup/restauração](docs/backup.md).
O script abaixo solicita a senha PostgreSQL de forma protegida, configura a URL
somente no processo, executa `alembic upgrade head` e inicia a API em loopback:
```powershell
.\scripts\Start-Server.ps1
# Para nomes diferentes:
# .\scripts\Start-Server.ps1 -DatabaseName meu_banco -DatabaseUser meu_usuario
```
Se `AGROLINES_DATABASE_URL` já estiver configurada, ela será reutilizada. O script
não cria, apaga nem recria o banco. Falhas de migração impedem a inicialização.

Em outro PowerShell, na raiz:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
$env:AGROLINES_API_URL = 'http://127.0.0.1:8000'
.\.venv\Scripts\python.exe -m desktop.main
```
Crie uma conta e entre. Em **Minhas propriedades**, cadastre sua fazenda e use
as abas **Safras** e **Operações** para os cadastros mínimos pelo nome. As ações
de renomear, compartilhar e transferir ficam junto à tabela de propriedades.
Em **Compartilhar propriedade**, avance por propriedade, destinatário, perfil,
escopo e confirmação. O destinatário precisa de conta existente e aceita em
**Convites recebidos e enviados**; filtre por direção e situação para consultar
os escopos. Consulte, altere perfis ou revogue acessos em **Usuários e permissões**.
Só o proprietário transfere titularidade, com confirmação.
A identificação por e-mail localiza uma conta; não comprova posse da caixa postal.
Convites ficam no aplicativo, sem envio automático de e-mail nesta etapa.

## Desenvolvimento Linux / execução direta
```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,desktop]'
# Configure AGROLINES_DATABASE_URL com seu provedor seguro de variáveis:
# formato postgresql+psycopg://usuario:senha-codificada@127.0.0.1:5432/agrolines
alembic upgrade head
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
A URL é segredo; não a publique nem a versione. Fora de loopback, o desktop exige HTTPS.
No Linux a sessão fica somente em memória; persistência protegida usa DPAPI no Windows.
`GET /health` mantém o contrato da Etapa 1 e é liveness, sem prometer banco saudável.
Endpoints autenticados exigem banco migrado. A API não cria tabelas automaticamente.

## Docker opcional
Copie `.env.example` para `.env` e preencha senha e URL correspondente localmente.
```sh
docker compose --env-file .env -f infra/compose.yaml up --build -d --wait
curl http://127.0.0.1:8000/health
```
Banco sem porta publicada; API apenas em `127.0.0.1:8000`; volume `postgres_data`
persistente. A API usa usuário de sistema sem privilégios e aplica migrações aditivas.
Não use `down -v` em dados reais. HTTPS/reverse proxy autenticado ou VPN e operação
segura continuam necessários antes de disponibilizar o serviço a terceiros.

## Testes
```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest
```
Linux: `ruff check .`, `ruff format --check .`, `pytest` após ativar o ambiente.
Para API com **banco de teste** migrado: `python scripts/integration_check.py`.
Esse smoke test cria dados sintéticos e não limpa nem redefine o banco.

CI: Linux/Windows, teste Qt offscreen, DPAPI real no Windows, migração de `0001`
para `0002` preservando marcador anterior, fluxo HTTP/PostgreSQL e backup/restauração.
Capturas Qt nativas Windows em escalas 100%, 125% e 150% são publicadas como
artefatos do CI para revisão visual; ver [validação visual](docs/visual-validation.md).
SQLite é usado apenas como banco isolado dos testes unitários; servidor real usa PostgreSQL.

Checklist manual Windows: criar conta, entrar/sair, reiniciar desktop e confirmar
sessão lembrada, compartilhar só Plantio de uma safra, aceitar em outra conta,
confirmar ausência de outras safras/operações, alterar perfil, revogar, perder
conexão, conferir bloqueio de alterações e prazo local; reconectar e confirmar
remoção do acesso revogado. Conferir escala/acentos, janela responsiva durante
consultas e encerramento com consulta em andamento. Offscreen não substitui esse teste.

Veja [autenticação e configuração](docs/authentication.md), [permissões](docs/permissions.md),
[arquitetura](docs/architecture.md), [roadmap](docs/roadmap.md), [backup](docs/backup.md)
e [dependências/licenças](docs/dependencies.md). Não avançar à Etapa 3 sem aprovação.

Compatibilidade Windows 11 com Smart App Control ativo ainda exige homologação.
Veja [diagnóstico, auditoria e aceitação](docs/windows-security.md); não desative
proteções para iniciar componentes bloqueados.

Prova de executável/instalador Windows com runtime embutido: [distribuição comercial](docs/windows-distribution-poc.md). Aprovação SAC e assinatura final continuam condicionadas à homologação real.

### Projetos locais e preparação comercial

O desktop abre projetos locais por padrão, sem login, API ou PostgreSQL.
Crie um arquivo `.agrolines`, importe polígonos, edite vértices, salve versões e
faça backup/restauração. A colaboração anterior continua disponível pela ação
**Colaboração online** ou, para mantenedores, `python -m desktop.main --remote`.
No PoC Windows, use **Projetos locais** ou o argumento `--local`.
Consulte [plano, execução e critérios offline/licenciamento](docs/offline-and-licensing.md).
Licenciamento comercial é um contrato futuro; desenvolvimento permanece liberado.
A homologação Windows 11/SAC com internet desconectada continua pendente.

### Microsoft Store / MSIX

A identidade oficial do Partner Center está configurada, sem publicação automática.
O pipeline gera um candidato MSIX x64 com todo o payload PyInstaller e dados locais
fora da instalação. Consulte [Microsoft Store: geração, homologação e pendências](docs/microsoft-store-msix.md).
Instalação MSIX, subprocessos Qt sob identidade de pacote e SAC só serão declarados
validados com pacote confiavelmente assinado e bancada Windows 11 real.
