# ADR 0001 — Servidor próprio, offline-first e exportadores isolados
Status: aceita para a arquitetura inicial.

Contexto: operação agrícola pode perder conectividade, exige controle de dados e
formatos de monitores variam por firmware.

Decisão: desktop nativo Windows com PySide6 e SQLite local futuro; servidor próprio
FastAPI/PostgreSQL/PostGIS, sem Supabase; núcleo Python independente; exportadores
versionados com fixtures e declaração de capacidades. Fila durável, idempotência e
resolução explícita de conflitos serão necessários para sincronização.

Consequências: suporte offline exige política de validade e revogação, backups,
migrações e restauração testada. Não há promessa de compatibilidade de monitor sem
evidência. Esta etapa fornece apenas esqueleto e healthcheck real.
