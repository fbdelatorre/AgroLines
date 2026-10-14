# Dependências e licenças
Python 3.12 é a versão alvo. Dependências diretas e intervalos suportados constam
em `pyproject.toml`; os extras `dev` e `desktop` separam ferramentas e interface.

| Componente | Uso | Licença upstream |
|---|---|---|
| Python | Runtime | PSF |
| FastAPI, Uvicorn, Pydantic/Settings | API/configuração | MIT / BSD-3-Clause (Uvicorn) |
| SQLAlchemy, Alembic | Banco/migrações | MIT |
| Psycopg | Driver PostgreSQL | LGPL-3.0 |
| PySide6/Qt | Interface nativa | LGPL-3.0/GPL-3.0 ou comercial, conforme módulo |
| Argon2-cffi, email-validator | Hash/validação | MIT / Unlicense (email-validator) |
| pytest, Ruff, HTTPX | Qualidade/testes | MIT |
| PostgreSQL | Persistência servidor | PostgreSQL License |
| PostGIS | Extensão espacial | GPL-2.0-or-later |

Antes de distribuir o instalador, conferir licenças dos módulos Qt efetivamente
empacotados, avisos e obrigações de redistribuição. Esta etapa não produz instalador
nem define a licença do código do projeto. A Etapa 3.1 usa Shapely/GEOS (BSD/LGPL),
pyproj/PROJ (MIT), Fiona/GDAL (BSD/MIT) e DefusedXML (PSF). Leaflet 1.9.4 é incluído
localmente sob BSD-2-Clause, com aviso em desktop/map_assets/LEAFLET-LICENSE.
Qt WebEngine inclui Chromium e seus avisos de terceiros; o instalador deverá
redistribuir esses avisos e cumprir as obrigações dos módulos Qt efetivamente usados.
As wheels de Fiona/PROJ/GEOS trazem bibliotecas nativas; não é exigido um QGIS instalado.

Wheels não comprovam assinatura Authenticode ou compatibilidade Smart App Control.
A auditoria por arquivo e o plano de distribuição segura constam em
[segurança Windows](windows-security.md). Não reduzir a precisão GIS para evitar bloqueios.
