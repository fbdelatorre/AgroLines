# Arquitetura atual — Etapa 2
`core/` preserva modelos Python puros, sem UI ou persistência. `desktop/` contém
PySide6, cliente HTTP e cofre de sessão DPAPI. `server/` contém FastAPI, SQLAlchemy,
Alembic, autenticação, propriedades e autorização por escopo. `exporters/` segue
isolado para adaptadores futuros. PostgreSQL/PostGIS é o banco servidor; SQLite
local será usado na persistência agrícola/fila offline, sem segredos em texto puro.

## Persistência e contratos
Tabelas `users`, `credentials`, `sessions`, `refresh_tokens`, `password_resets`,
`rate_buckets`, `farms`, `seasons`, `operations`, `invitations`, `invitation_scopes`,
`permissions`, `audit_events`. IDs UUID imutáveis e foreign keys preparam relações
com talhões, equipamentos e planos futuros. Safras/operações são apenas nomes e
identificadores para controle de acesso, sem dados agrícolas avançados.

`auth.py` gerencia contas/sessões; `permissions.py` centraliza matriz/hierarquia;
`properties.py` filtra consultas e valida cada mutação. `dependencies.py` mantém uma
transação por requisição. Cada requisição autenticada consulta sessão e autorização
atuais. `/health` preserva liveness da Etapa 1; `/docs` documenta contratos reais.

Migração `0001` habilita PostGIS; `0002` adiciona tabelas sem apagar dados. O servidor
não cria tabelas automaticamente. Autogeração ignora tabelas externas sem modelo,
para não propor remoção de `spatial_ref_sys` ou tabelas de terceiros. Downgrade
`0002` é bloqueado por ser destrutivo; rollback requer restauração em banco isolado.

## Desktop e offline
Consultas HTTP e healthcheck executam em threads, sem bloquear a interface.
A autorização local guarda apenas resumo mínimo, com até 15 minutos de validade.
DPAPI por usuário protege tokens persistentes no Windows; sem DPAPI, só memória.
Reconexão invalida resumo e consulta `/auth/me` e `/farms` antes de restaurar acesso.
Não há fila de escritas nem sincronização completa. A detecção online/offline segue real.

## Futuras etapas
Dados agrícolas e versões de limites formarão produtor → fazenda → talhão, com
planos por safra/operação/equipamentos. Geometria usará Shapely/PyProj e CRS métrico,
preservando CRS original; GDAL será instalado conforme formatos efetivamente usados.
Exportadores terão fixtures, versão e matriz de compatibilidade por monitor/firmware.
Fila offline durável exigirá idempotência e resolução explícita de conflitos.

Prazos agrícolas offline, licença de tiles e fixtures ISOXML permanecem decisões
pendentes antes dos módulos correspondentes. Serviço exposto exige HTTPS e acesso
seguro por VPN/reverse proxy, autenticação própria, backups externos criptografados
e retenção de auditoria. O Compose atual destina-se ao desenvolvimento local.
