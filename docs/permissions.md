# Permissões propostas — ainda não implementadas
Todas as decisões devem ser verificadas no servidor, com isolamento entre propriedades.

| Papel | Consulta | Operação/exportação | Edição | Gestão de acesso |
|---|---|---|---|---|
| Visualizador | Sim | Não | Não | Não |
| Operador/exportador | Sim | Sim | Não | Não |
| Editor | Sim | Sim | Sim | Não |
| Administrador | Sim | Sim | Sim | Sim, no escopo delegado |
| Proprietário | Sim | Sim | Sim | Sim, inclusive propriedade |

Escopos: fazenda, safra e/ou operação. Compartilhar uma fazenda não concede acesso
a equipamentos privados de terceiros. Convites e revogações exigem servidor online.
Autorização offline terá janela de validade explícita; nunca assumir cache autorizado
indefinidamente. Login, tokens com expiração, hashing robusto, auditoria e testes
negativos de isolamento pertencem à etapa 2. O endpoint /health é público e não
retorna dados de usuários, banco ou credenciais.
