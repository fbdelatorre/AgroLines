# AgroLines — programa privado inicial exclusivo para adultos

Decisão do responsável em 14/10/2026: testadores com **18 anos ou mais**.
Esta decisão substitui a proposta anterior de admitir menores na primeira fase.
Contato: **fabricio.grupodelatorre@gmail.com**. Responsável pessoa física:
FABRICIO JOSE DELATORRE. Não houve coleta de autorizações parentais nesta tarefa.

## Regra de participação e minimização

Participação voluntária e gratuita, com declaração simples de maioridade e aceite
manual da versão do termo aprovada antes da inclusão no grupo. Sem CPF, RG,
documentos de identidade, data completa de nascimento, imagens, cadastro de
menores ou investigação invasiva de idade como requisitos padrão. A declaração
não é apresentada como prova absoluta de idade ou consentimento irrestrito.

Não há autorização parental no fluxo inicial: ela não admite um menor no programa
18+. Futura ampliação exige nova revisão jurídica e operacional. O código do
aplicativo não foi alterado para bloquear idade; a regra é de participação no grupo,
não um mecanismo automático de execução/licenciamento do aplicativo offline.

## Classificação e Microsoft Store

Informações confirmadas pelo responsável sobre configurações anteriores, sem
verificação em tempo real do Partner Center:

| Item | Informação a preservar |
|---|---|
| Brasil | Livre / Todas as idades |
| IARC | 3+ |
| Microsoft Store | 3+ |
| Audiência | Público particular / Private audience |
| Grupo | AgroLines - Testadores Internos |
| Visibilidade informada | Acesso por link direto, com distribuição restrita ao grupo |
| Demais mercados | Classificações individuais ainda não confirmadas |
| Restrições da conta/Microsoft Family | Não verificadas; não inferir da classificação |

A classificação trata do conteúdo, conforme a documentação Microsoft; não é
verificação de idade nem definição obrigatória de quem integra um grupo privado.
Não há motivo demonstrado nesta alteração documental para elevar a classificação
para 18+. Respostas do IARC devem continuar verdadeiras sobre conteúdo/funcionalidades;
conferir os mercados antes da distribuição, sem alterar configurações nesta tarefa.

A documentação diferencia Private audience de Public audience com descoberta
restrita. O relato de acesso por link não foi usado para mudar a audiência:
confirmar no painel que ela continua privada e limitada ao grupo. O link sozinho
não dispensa inclusão no grupo e conta Microsoft pessoal correspondente. Não
compartilhar senhas ou contornar restrições da Store.

Fontes oficiais Microsoft consultadas em 14/10/2026:

- https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/age-ratings
- https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/visibility-options
- https://learn.microsoft.com/en-us/windows/apps/publish/create-customer-groups
- https://learn.microsoft.com/en-us/windows/apps/publish/store-policies

A consulta não acessou o painel particular do responsável. As fontes ANPD/Planalto
não ficaram acessíveis nesta execução; não foi atestada interpretação normativa
atualizada para eventual ampliação futura a menores. A regra atual não elimina os
cuidados LGPD sobre dados incidentais de menores ou direitos de outros titulares.

## Implementado, documentado e pendente

| Medida | Situação |
|---|---|
| Edição offline e ausência de cadastro etário no app | Arquitetura/código existentes preservados; sem mudança nesta tarefa |
| Programa 18+ e ausência de ingresso por autorização parental | Decisão registrada nos documentos dos PRs #12 e #13 |
| Declaração, aceite, lista e saída do grupo | Procedimento manual preparado; execução pelo responsável ainda não comprovada |
| Suporte e minimização | Procedimento manual revisado; sem coleta/telemetria automática nova |
| Retenção de suporte/grupo/direitos | Mantida: até 90 dias após encerramento; participação + até 30 dias; até 12 meses após conclusão, respectivamente, com exceções documentadas |
| Bases legais e transferências internacionais | Ainda dependem de revisão jurídica/documentação |
| Publicação da política | Bloqueada enquanto houver pendências; requer aprovação explícita |

O responsável precisa registrar declaração/aceite mínimos em controle privado,
restringir acesso à lista, proteger Gmail e conta Microsoft, validar fechamento e
exclusão periódica, atender direitos e incidentes. Registros reais não vão para GitHub
público, projetos agrícolas ou artefatos de CI. Não coletamos ou simulamos aceites
reais neste PR. Os prazos não alteram projetos exclusivamente no computador do usuário.

## Pendências antes da publicação e distribuição

1. Revisar/adotar termo: forma de aceite, confidencialidade se cabível,
   duração/encerramento e condições de saída, sem fingir contrato já firmado.
2. Definir/documentar bases legais por finalidade e transferências aplicáveis a
   Gmail, Microsoft e GitHub, pessoas com acesso e eventuais outros destinatários.
3. Definir a data efetiva e aprovar a política completa; ativar/verificar URL HTTPS
   pública sem login somente após autorização. Hash antigo não aprova HTML revisado.
4. Configurar e testar controles manuais de participação, suporte, direitos,
   incidentes, retenção e exclusão, com dados sintéticos antes de casos reais.
5. Conferir Partner Center/mercados e eventuais restrições de conta. Não houve
   mudança de classificação, audiência, grupo, identidade ou licenciamento.
6. Pendências Windows/Store anteriores permanecem: pacote confiável, validação real
   SAC, revisão nativa e persistência após atualização/desinstalação. Documentação
   do grupo não homologa aplicativo, instalação nem segurança.

Nenhum merge, ativação de Pages, publicação de aplicativo ou envio do MSIX à
certificação foi autorizado ou realizado. A política não está juridicamente aprovada.
Resultados de testes e revisão exata ficam registrados na atualização dos PRs.
