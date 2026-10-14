# Pendências — primeira edição Store exclusivamente offline

Atualização: 14/10/2026. Este documento complementa a auditoria original do PR #9;
não a substitui nem transforma o pacote anterior em um produto offline.

## Resolvido por decisão do responsável

- FABRICIO JOSE DELATORRE; contato oficial de privacidade e suporte:
  **fabricio.grupodelatorre@gmail.com**, reafirmado pelo responsável em 14/10/2026.
- Grupo Partner Center “AgroLines - Testadores Internos”; sem cadastro próprio no app.
- Suporte recebe arquivos apenas por envio voluntário, para a finalidade solicitada.
- Retenção de suporte até 90 dias após encerramento, com descarte sob controle e
  exceções justificadas/documentadas; não se estende a projetos locais do usuário.
- Não foi definida restrição etária. Não declarar exclusividade para adultos ou
  direcionamento a crianças. Avaliar proteção de eventuais menores.
- Edição Store inicial sem funcionalidades ou conexões remotas próprias.
- Controle próprio do grupo: participação + até 30 dias após saída/encerramento;
  pedidos de privacidade: até 12 meses após conclusão, com dados mínimos e exceções.
- Mudanças relevantes: aviso manual por e-mail e página pública atualizada.
- Preparar GitHub Pages gratuito; não declarar URL disponível antes de teste.
- Ainda não existem termos adotados/base legal ou avaliação de interesse confirmados.

## Verificação dos campos de contato

O mesmo endereço oficial atende privacidade, suporte e participação/saída do
programa de testes. Política Markdown/HTML/TXT, minuta e procedimento de atendimento
foram padronizados. Não há campo de e-mail ou canal próprio de contato pendente
nesses documentos da edição offline. Isso não comprova configuração, acesso seguro
ou teste de atendimento da conta Gmail.

A revisão dos fornecedores, destinatários adicionais e eventuais pessoas com acesso
aos dados de suporte continua pendente; não é uma lacuna no endereço oficial.
Campos de operador/SMTP das versões históricas não representam serviços habilitados
na edição offline. A auditoria original do PR #9 permanece preservada.

## Antes de considerar a política publicável

| Pendência | Ação/evidência necessária |
|---|---|
| Base legal por finalidade | Confirmar/documentar suporte, gestão do grupo e direitos; recebimento voluntário não é autorização genérica. Atendimento de obrigações legais e suporte têm finalidades diferentes. Se adotar legítimo interesse, registrar necessidade/balanceamento e melhor interesse de menores quando aplicável |
| Dados realmente acessados no Partner Center | Conferir campos da audiência/avaliações e quem os acessa; não inventar que o responsável recebe todo dado Microsoft |
| Outros destinatários e transferências | Confirmar acesso a suporte, eventuais ferramentas, países/mecanismos aplicáveis de Gmail e Microsoft; não inferir que não haja transferência porque o programa é offline |
| Retenção restante | Grupo 30 dias e direitos 12 meses definidos; configurar execução manual, justificar necessidade e definir retenção dos comprovantes mínimos de descarte |
| Operação manual | Configurar e validar registro/fechamento/descarte, direitos, incidentes e minimização com fixtures sintéticas; documentação não prova exclusão real de Gmail/anexos |
| Menores e classificação etária | Avaliar LGPD art. 14 e Store 10.5.8; conferir classificação etária e permissões reais do grupo. Não há controles próprios de idade. Se não puder cumprir medidas, recomendar restrição inicial futura explícita |
| Vigência e URL | Data será a primeira disponibilização efetiva, ainda não marcada; aviso por e-mail definido. Workflow Pages preparado, não executado: aprovar texto e testar URL HTTPS sem login |
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

- Novo build inclui originais aprovados e verifica ícones do PE/recursos extraídos.
  Consultar o resultado do workflow no relatório de finalização; não confundir
  verificação binária com aparência do shell instalada.
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
