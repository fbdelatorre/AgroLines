# Autenticação, configuração e sessão local

## Contratos HTTP
Documentação interativa local em `/docs`; contratos de entrada/saída em OpenAPI.

| Rota | Comportamento |
|---|---|
| POST /auth/register | Nome, e-mail único normalizado, senha de 6–128 caracteres |
| POST /auth/login | E-mail/senha; acesso e renovação opacos |
| POST /auth/refresh | `{ "token": "..." }`; rotação, prazo absoluto preservado |
| POST /auth/logout | Revoga a sessão atual; 204 |
| GET/PATCH /auth/me | Consulta conta/altera nome autenticado |
| GET /auth/sessions | Lista apenas sessões do próprio usuário, sem tokens |
| DELETE /auth/sessions/{id} | Revoga sessão própria |
| POST /auth/recover | `{ "email": "..." }`; exige SMTP configurado |
| POST /auth/reset | `{ "token": "...", "password": "..." }`; uso único |

Use `Authorization: Bearer <access_token>` nas rotas protegidas. Tokens não são JWT:
256 bits aleatórios, somente SHA-256 no banco. Cada consulta verifica sessão ativa,
prazo e autorização vigente; permissões não ficam embutidas no token. Argon2id usa
64 MiB, três iterações e paralelismo 2. Rehash ocorre após login quando necessário.

Cadastro e redefinição aceitam senhas de 6 a 128 caracteres, sem alteração do
hash Argon2id. A atualização não modifica credenciais nem invalida sessões
existentes. Login continua verificando a senha armazenada, sem impor o mínimo
novo a credenciais antigas. Senhas nunca são registradas em logs.

A renovação troca ambos os tokens sob lock da sessão. O acesso anterior é invalidado.
Reutilização de refresh antigo revoga a sessão inteira, incluindo tokens novos.
Perda da resposta durante rotação pode exigir novo login; não repetir silenciosamente
renovação com token antigo. Logout e redefinição invalidam sessões no servidor.

Hash/verificação têm limite de quatro operações simultâneas por processo (até
256 MiB de memória Argon2), retornando 429 quando saturado.

Bloqueio de login por conta e IP usa buckets persistentes e locks no PostgreSQL,
funciona entre workers e permanece após falhas de autenticação. Não confiar em
X-Forwarded-For arbitrário: configure proxy/hosts confiáveis ao implantar. Cadastro
e recuperação também têm limites. Resposta de login não distingue conta desconhecida.
Não há diretório público de usuários. Cadastro não verifica posse do e-mail;
convites são vinculados ao UUID de conta já existente, que o responsável deve confirmar.

## Variáveis

| Variável | Padrão / uso |
|---|---|
| AGROLINES_DATABASE_URL | URL SQLAlchemy PostgreSQL/psycopg; tratar como segredo |
| AGROLINES_APP_NAME | AgroLines |
| AGROLINES_API_URL | Desktop: http://127.0.0.1:8000; HTTPS obrigatório fora de loopback |
| AGROLINES_ACCESS_TTL | 900 segundos; permitido 60–3600 |
| AGROLINES_REFRESH_TTL | 86400 segundos absolutos; permitido 3600–604800 |
| AGROLINES_LOGIN_LIMIT | 10 tentativas por conta/janela; IP permite dez vezes esse limite |
| AGROLINES_LOGIN_WINDOW | 900 segundos |
| AGROLINES_SMTP_HOST | Ausente: recuperação indisponível, resposta 503 |
| AGROLINES_SMTP_PORT | 587; STARTTLS obrigatório com verificação de certificado |
| AGROLINES_SMTP_FROM | agrolines@example.com; configurar remetente autorizado |
| AGROLINES_SMTP_USERNAME | Opcional, conforme servidor SMTP |
| AGROLINES_SMTP_PASSWORD | Segredo do serviço SMTP, nunca no Git |
| POSTGRES_PASSWORD | Apenas Compose; senha da conta do banco |

Configure SMTP pelo provedor seguro de variáveis do servidor. Não há serviço externo
obrigatório. O e-mail contém código temporário de 15 minutos; informe-o na aba
**Recuperar senha**. A resposta 202 é genérica mesmo para conta ausente ou falha de
entrega, evitando revelar usuários. Falha de envio gera log operacional sem e-mail,
senha ou token. O operador deve monitorar esses logs. Token de reset é hash no banco,
uso único; senha redefinida revoga todas as sessões e códigos pendentes da conta.
O envio real depende do serviço SMTP do operador; testes usam transporte simulado.

## Offline e proteção local
O login inicial exige conexão. No Windows, `%LOCALAPPDATA%/AgroLines/session.dpapi`
contém apenas sessão e resumo de conta/permissões, protegidos por DPAPI do usuário
atual. Não há senha armazenada, nem token de longa duração em SQLite/plaintext.
Gravação é atômica; falha de descriptografia não libera uma sessão. Em outros sistemas,
sem DPAPI, só há memória, sem fallback inseguro. O blob é vinculado ao endereço da API;
mudar de servidor não envia os tokens anteriores. Redirecionamentos HTTP são recusados.

Resumo offline permite somente nomes das propriedades/perfis e identificação da conta,
por até 15 minutos desde a última consulta autenticada, nunca além do acesso vigente.
Não inclui dados agrícolas, arquivos ou planos. Relógio local deve permanecer correto;
um administrador que controla o computador/perfil Windows não é contido por essa política.
Cadastro, login, edição, convite, aceite, revogação e transferência exigem servidor online.

Revogação não pode chegar imediatamente a um computador desconectado: o prazo do
resumo local limita essa janela. Na reconexão, cache é invalidado antes da consulta
a `/auth/me` e `/farms`; sessão revogada e permissões removidas deixam de ser usadas.
Logout sem conexão limpa o blob local; sessão remota expira no prazo original, e pode
ser revogada por outra sessão via API. Não há sincronização completa nem fila de escritas.
Backups do perfil/servidor, renovação e expiração de registros antigos devem integrar
a política operacional; não remover histórico/auditoria sem definir retenção.
