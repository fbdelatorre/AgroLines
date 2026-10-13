# ADR 0002 — Sessões opacas e autorização hierárquica
Status: aceita para Etapa 2.

Tokens opacos aleatórios, com hashes no PostgreSQL, permitem revogação imediata no
servidor sem manter permissões antigas em JWT. Acesso dura 15 minutos, renovação
24 horas absolutas por padrão. Locks e histórico detectam replay de renovação.
Argon2id protege senhas; limites de login persistem entre processos.

Concessões têm fazenda e safra/operação opcionais. Proprietário é uma relação única;
administrador gerencia fazenda inteira. Demais perfis podem ser restritos. Permissões
aditivas são verificadas em cada consulta; não ampliar acesso por cabeçalhos/pais.
Locks da fazenda serializam alterações e aceite; auditoria não armazena segredos.

No Windows, DPAPI por usuário protege a sessão e o resumo de permissões. Resumo offline
expira em até 15 minutos; não permite alterações. Reconexão invalida cache antes de
consultar concessões. Sem DPAPI não persistir tokens; sem SMTP não recuperar senha
por meios inseguros. Convites por e-mail apontam conta existente, sem presumir prova
de posse da caixa postal. Sincronização e dados agrícolas offline ficam para etapas futuras.
