# Backup inicial e segurança
O volume `postgres_data` persiste entre reinícios. Não remover volumes de produção.
Antes de migrações ou atualizações, criar backup e verificar restauração isolada.
Com `.env` preenchido e serviços iniciados (Linux):
```sh
mkdir -p backups
chmod 700 backups
docker compose --env-file .env -f infra/compose.yaml exec -T db pg_dump -U agrolines -d agrolines -Fc > backups/agrolines.dump
```
Não repetir o nome cegamente: preservar backups anteriores com nomes únicos.
Verificar exit status de pg_dump; arquivo criado não prova sucesso.
Para ensaio, criar banco separado, nunca sobrescrever o banco original:
```sh
docker compose --env-file .env -f infra/compose.yaml exec -T db createdb -U agrolines agrolines_restore
docker compose --env-file .env -f infra/compose.yaml exec -T db pg_restore -U agrolines -d agrolines_restore --exit-on-error < backups/agrolines.dump
docker compose --env-file .env -f infra/compose.yaml exec -T db psql -U agrolines -d agrolines_restore -c 'SELECT version_num FROM alembic_version;'
```
Banco de restauração deve conter a versão e dados esperados. Remover apenas após
conferência e conforme política de retenção. Backup externo criptografado e retenção
precisam ser configurados pelo operador; não estão automatizados nesta etapa.
Nunca versionar dumps, SQLite, credenciais ou dados de clientes. Restringir acesso
ao host; PostgreSQL não tem porta publicada. Produção exige TLS e reverse proxy
 autenticado/VPN, autenticação da aplicação e conta de banco com menor privilégio.

## Atualização para Etapa 2
Faça backup **antes** de `alembic upgrade head`. A revisão `0002` adiciona tabelas de
contas e autorização e não remove tabelas/volumes. Seu downgrade é bloqueado para
não destruir usuários/sessões. Para rollback, restaure backup em outro banco,
valide versão e registros e planeje troca de conexão; nunca resetar o banco atual.
Dumps passam a conter hashes de credenciais e identificadores pessoais: proteger
permissões do arquivo, criptografar backups externos e definir retenção.

Após restauração, conferir `SELECT count(*) FROM users;` e
`SELECT count(*) FROM credentials;`, comparando com o banco original, além da versão.
A CI valida migração de 0001 com marcador pré-existente, fluxo de contas/escopos e
restauração de versão e contagens. Produção precisa testar restauração dos dados reais
em ambiente protegido e isolado; esses dados nunca devem entrar no repositório.
