# Pendências — primeira edição Store exclusivamente offline

Atualização: 14/10/2026. Este documento complementa a auditoria original do PR #9;
não a substitui nem transforma o pacote anterior em um produto offline.

## Resolvido por decisão do responsável

- FABRICIO JOSE DELATORRE; privacidade e suporte pelo Gmail já informado.
- Grupo Partner Center “AgroLines - Testadores Internos”; sem cadastro próprio no app.
- Suporte recebe arquivos apenas por envio voluntário, para a finalidade solicitada.
- Retenção de suporte até 90 dias após encerramento, com descarte sob controle e
  exceções justificadas/documentadas; não se estende a projetos locais do usuário.
- Não foi definida restrição etária. Não declarar exclusividade para adultos ou
  direcionamento a crianças. Avaliar proteção de eventuais menores.
- Edição Store inicial sem funcionalidades ou conexões remotas próprias.

## Antes de considerar a política publicável

| Pendência | Ação/evidência necessária |
|---|---|
| Base legal por finalidade | Confirmar/documentar suporte, gestão do grupo e direitos; recebimento voluntário não é autorização genérica. Atendimento de obrigações legais e suporte têm finalidades diferentes. Se adotar legítimo interesse, registrar necessidade/balanceamento e melhor interesse de menores quando aplicável |
| Dados realmente acessados no Partner Center | Conferir campos da audiência/avaliações e quem os acessa; não inventar que o responsável recebe todo dado Microsoft |
| Outros destinatários e transferências | Confirmar acesso a suporte, eventuais ferramentas, países/mecanismos aplicáveis de Gmail e Microsoft; não inferir que não haja transferência porque o programa é offline |
| Retenção restante | Definir critérios de grupo, pedidos de privacidade e registro mínimo de descarte; o prazo de suporte já foi definido |
| Operação manual | Configurar e validar registro/fechamento/descarte, direitos, incidentes e minimização com fixtures sintéticas; documentação não prova exclusão real de Gmail/anexos |
| Menores e classificação etária | Avaliar LGPD art. 14 e Store 10.5.8; conferir classificação etária e permissões reais do grupo. Não há controles próprios de idade. Se não puder cumprir medidas, recomendar restrição inicial futura explícita |
| Vigência e URL | Definir data, aviso aos testadores e URL HTTPS pública estável, acessível sem login, com texto final sem campos CONFIRMAR |
| Conta Individual/publicador | Resolver com Microsoft a adequação à seção 10.14 do nome Delatorre COrporation em conta Individual; não alterar a identidade oficial ou declarar empresa inexistente |
| Proteção dos arquivos | Avaliar a seção 10.5.4 da Store e medidas proporcionais para dados pessoais. Projetos/backup não têm cifra própria; revelar a limitação não resolve sozinho requisitos de segurança |

A política foi revisada e contém as decisões confirmadas, mas **não está pronta para
publicação enquanto os campos obrigatórios estiverem pendentes**. Não declarar
conformidade integral LGPD/Store por ter removido recursos remotos.

## URL no Partner Center — verificação documental

Fonte oficial consultada em 14/10/2026: [Microsoft Store Policies 7.20, seção
10.5.1](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies).
O texto exige inserir a **privacy policy URL** no Partner Center na submissão e
informa que Desktop Bridge/Win32 devem sempre possuir política. A política pode
adicionalmente estar dentro do produto, mas isso não elimina o campo URL.

Não encontramos nessa exigência aceitação de texto colado como substituto de URL
para o MSIX desktop. O arquivo TXT é fornecido para revisão/cópia se houver campo
auxiliar adequado; não presumir que ele atende o requisito. A redação consultada
menciona URL, sem determinar literalmente o esquema HTTPS nessa cláusula: preparar
URL pública HTTPS por segurança, verificar acesso sem login e conferir o fluxo real
do Partner Center antes de submissão. Nenhum campo/configuração foi alterado.

## Pendências técnicas de distribuição/homologação

- Gerar e revisar o novo MSIX x64; embutir runtime, GIS, Qt, recursos do WebEngine e
  política local. CI produz candidato não assinado; isso não é pacote instalado.
- Rever inventário/assinaturas de todos os EXE/DLL/PYD. Não usar certificado
  autoassinado, Developer Mode, AllowUnsigned ou redução de proteções.
- Obter pacote distribuído pela Store quando houver autorização futura. Não houve
  publicação ou envio para certificação nesta tarefa.
- Testar esse pacote em Windows 11 real, com SAC ativo, sem Python/PostgreSQL e
  fisicamente desconectado. Verificar interface e helpers Qt; CI não aprova SAC.
- Observar conexões nativas de aplicativo e helpers em execução conectada de bancada
  separada, sem dados reais, sem modificar proteções. Bloqueio Python/CSP e teste
  HTTP local não cobrem todas as possibilidades de DNS/UDP/native networking.
- Testar criação/importação/edição/reabertura/backup e restauração. Executar upgrade
  real e desinstalação, comparar hashes e reabrir projetos após reinstalação.
  Não assumir preservação pelo manifesto ou teste de arquivo isolado.
- Auditar/minimizar evidências de Windows real antes de upload GitHub ou suporte;
  eventos podem conter dados de outros programas. Upload deve ser decisão consciente
  do operador, não coleta do aplicativo.

Responsável executa as confirmações e procedimentos de conta/suporte e fornece
bancada/pacotes confiáveis. Código e testes são revisáveis no PR técnico dependente;
nenhum merge, submissão ou publicação está autorizado automaticamente.
