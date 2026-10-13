# Arquitetura inicial
`core/` contém modelos Python tipados, sem imports de UI ou banco. `desktop/` contém
PySide6 e cliente de saúde. `server/` contém FastAPI, configuração, SQLAlchemy e
Alembic. `exporters/` será composto por adaptadores versionados. `infra/` executa
API e PostgreSQL/PostGIS, com volume persistente. SQLite será o armazenamento local
na etapa de persistência; nenhum arquivo de dados é criado nesta etapa.

Esquema proposto: produtor → fazenda → talhão → versões de limite; safra/operação,
equipamentos, planos versionados, pacotes de exportação e concessões de acesso.
Somente Producer, Farm e Field têm modelos iniciais; nenhuma tabela de domínio
foi criada. O contrato HTTP atual é apenas GET /health, sem dependência de banco.

Offline: fila durável, UUIDs imutáveis, idempotência, versões e resolução explícita
de conflitos serão implementados na etapa 9. Convites/revogação exigem servidor.
A validade de autorização em cache precisa ser definida antes de liberar dados offline.
Geometria futura usará Shapely/PyProj, preservará CRS original e medirá em CRS métrico.
GDAL será avaliado quando formatos reais forem necessários, sem instalação prematura.

Decisões pendentes antes das etapas correspondentes: prazo de autorização offline,
provedor/licença de tiles, fixtures reais ISOXML e matriz modelo/firmware. Nenhuma
impede o esqueleto atual. API HTTPS e VPN/reverse proxy autenticado serão requisitos
para publicação; o Compose atual serve apenas desenvolvimento local.
