# Permissões da Etapa 2
Toda autorização ocorre no servidor. Não existe papel global de administrador:
a administração é delegada para uma fazenda. Equipamentos, arquivos e planos não
possuem endpoints nesta etapa; não são implicitamente compartilhados por essas regras.

| Perfil | Consulta | Exportação futura | Edição no escopo | Gerir acesso | Transferir titularidade |
|---|---|---|---|---|---|
| Proprietário | Sim | Sim | Sim | Sim | Sim |
| Administrador | Sim | Sim | Sim | Sim | Não |
| Editor | Sim | Sim | Sim | Não | Não |
| Operador | Sim | Sim | Não | Não | Não |
| Visualizador | Sim | Não | Não | Não | Não |

Proprietário é `farms.owner_id`, não um perfil que pode ser concedido por convite.
Administrador exige fazenda inteira. Editor, operador e visualizador admitem:
- `season_id=null, operation_id=null`: fazenda inteira.
- `season_id=<id>, operation_id=null`: safra inteira.
- `season_id=<id>, operation_id=<id>`: apenas operação dessa safra.

Um convite recebe lista de escopos, permitindo múltiplas safras/operações. O servidor
verifica que a safra pertence à fazenda e a operação pertence à safra. Permissões
são aditivas: uma concessão restrita não reduz outra concessão ampla existente.
Revogue ou restrinja a concessão ampla para reduzir acesso.

Quem possui só uma operação vê apenas o cabeçalho da fazenda/safra necessários à
navegação e essa operação. Não vê safras irmãs, operações irmãs ou outros usuários.
Editor restrito a operação pode editar seu nome, mas não renomear a safra, criar
operações irmãs nem editar a fazenda. Usuários sem acesso recebem 404 para recursos
de outras propriedades e 401 para sessão ausente/expirada. Respostas não contêm hashes.

## Rotas
- GET/POST `/farms`; GET/PATCH `/farms/{id}`.
- GET/POST `/farms/{id}/seasons`; PATCH `/farms/{id}/seasons/{season}`.
- GET/POST `/farms/{id}/seasons/{season}/operations`; PATCH com `/{operation}`.
- POST `/farms/{id}/invitations`: `user_id` **ou** `email`, mais `scopes`.
- GET `/invitations`: somente enviados/recebidos da própria conta.
- POST `/invitations/{id}/accept`, `/decline`, `/revoke`.
- GET `/farms/{id}/members`: proprietário/administrador.
- PATCH/DELETE `/permissions/{id}`: proprietário/administrador.
- POST `/farms/{id}/transfer`: proprietário, corpo `user_id`.
- GET `/farms/{id}/audit`: proprietário/administrador, últimos 200 eventos da fazenda.

Convites ficam pendentes por sete dias, ligados a conta existente por UUID. Aceite
exige destinatário correto e autoridade ainda vigente do emissor. Recusa não concede
acesso. Revogar convite remove todas as permissões originadas nele; revogar permissão
remove apenas aquela concessão. Alterar perfil/escopo é aplicado na próxima consulta.
Aceite, alteração de permissões, revogação e transferência são serializados pelo lock
da fazenda, para não criar concessões obsoletas em corridas concorrentes.

Transferência mantém as concessões de terceiros, remove concessões explícitas do novo
e do antigo proprietário, e retira o acesso anterior de proprietário. Convites pendentes
do antigo titular não poderão ser aceitos se ele perdeu poder de gestão.
Auditoria registra ator, ação, recurso e instante, sem senha, e-mail de login ou tokens.
A capacidade `export` é autorização futura: nenhum exportador foi implementado.
