# Memória de consulta — documentos oficiais e limites

Data de consulta: 14/10/2026. Não há aprovação jurídica, contrato/DPA firmado ou
mecanismo de transferência adotado por esta pesquisa. As condições aceitas nas
contas do responsável e os dados do painel particular não foram inspecionados.

## Fontes efetivamente acessadas

| Fonte oficial | Evidência conferida | Limite de aplicação |
|---|---|---|
| Microsoft: [Create customer groups](https://learn.microsoft.com/en-us/windows/apps/publish/create-customer-groups) | Grupo conhecido e e-mails de contas Microsoft pessoais; gestão pelo publicador | Não acessa a lista real do AgroLines nem comprova permissões/aceite da conta |
| Microsoft: [Store Policies](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies) | Exigências de privacidade/transparência, URL da política e proteção de dados | Não declara qual base ou mecanismo o responsável já adotou |
| Microsoft: [Age ratings](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/age-ratings) | Microsoft informa compartilhar nome de publicador e e-mail com IARC no questionário | Contato exato transmitido, entidades/termos IARC e localização não verificados; classificação não é verificação de maioridade |
| Microsoft: [EU Model Clauses](https://learn.microsoft.com/en-us/compliance/regulatory/offering-eu-model-clauses) | Declara SCC/Model Clauses para serviços em escopo de DPA, lista os serviços e remete ao acordo existente para outros | Não estender Azure/M365 empresarial a Microsoft Store/Partner Center pessoal nem ao Gmail |
| Microsoft: [Improved Health Report](https://learn.microsoft.com/en-us/windows/apps/publish/improved-health-report) | Documenta métricas de falha/dispositivos; algumas métricas dependem de diagnóstico opcional do Windows | Não comprova que relatórios estejam disponíveis/consultados no AgroLines nem telemetria própria do app |
| Microsoft: [Recent acquisitions](https://learn.microsoft.com/en-us/windows/apps/publish/recent-data-acquisitions-reports) | Documenta instalações/visualizações e agregações em intervalos | Não presumir anonimização, dados reais da audiência ou exportação pelo responsável |
| Microsoft: [Actionable insights](https://learn.microsoft.com/en-us/windows/apps/publish/actionable-analytics-insights) | Documenta recursos de análise/resumos de avaliações, inclusive com IA | Não há confirmação de disponibilidade/uso pelo AgroLines; não declara envio de projetos/suporte a IA |
| GitHub: [General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement), consultada pelo [repositório oficial](https://github.com/github/site-policy/blob/main/Policies/privacy-policies/github-general-privacy-statement.md) | Regiões gerais incluindo EUA/outros países, SCC UE e DPF com escopo UE/UK/Suíça; dados técnicos de conta/uso/site | Declaração geral não prova região da conta, contrato/DPA ou instrumento LGPD desse fluxo |

O blob GitHub `b845c1d819e4a661873a8ac0d60b25c577e3aa9a` identifica o conteúdo
consultado e está registrado no JSON; é hash do arquivo, não commit. O link para
`main` é navegável e pode mudar posteriormente. Os três textos de analytics foram
lidos no repositório oficial `MicrosoftDocs/windows-dev-docs`, branch `docs`,
`hub/apps/publish/`, e rechecados em suas páginas públicas conforme o JSON.
Essa consulta não prova funcionalidade ativa ou acesso pelo publicador.
Datas/versões das fontes podem ser distintas da data de consulta.

## Fontes oficiais cujo conteúdo não foi obtido

O proxy do ambiente respondeu **403 Forbidden antes do acesso à origem**. Não
concluímos que o fornecedor exija login, que o site esteja fora do ar ou que não
exista transferência. Certificados/TLS não foram desativados e não usamos relé
ou outra rota para contornar a restrição.

- Google: https://policies.google.com/privacy?hl=pt-BR
- Google: https://policies.google.com/privacy/frameworks?hl=pt-BR
- Google: https://policies.google.com/terms?hl=pt-BR
- Microsoft: https://privacy.microsoft.com/pt-br/privacystatement
- Microsoft: https://www.microsoft.com/pt-br/servicesagreement
- IARC: domínio https://www.globalratings.com indicado pela documentação Microsoft;
  caminho da política atual precisa ser confirmado. Tentativa no caminho candidato
  `privacy-policy.aspx` foi bloqueada antes de confirmar existência/conteúdo.
- LGPD: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- ANPD: portal https://www.gov.br/anpd/pt-br para regulamentação vigente de
  transferências. A referência Resolução CD/ANPD nº 19/2024 precisa ser conferida
  com o texto e eventuais alterações atuais; caminho de notícia tentado não foi validado.

Sem os textos, não marcamos como atuais/comprovados os mecanismos Google/Gmail,
Microsoft consumer/Store/Partner Center ou IARC. Não substituímos Gmail pessoal por
DPA Workspace/Cloud, nem inferimos que a pessoa física tenha um contrato empresarial.
Não inventamos país de armazenamento, normas corporativas, SCC ANPD aceitas ou
certificação aplicável a uma conta específica.

Para completar a consulta primária, permitir **adição**, sem substituir a lista de
rede existente, dos domínios necessários na configuração do ambiente:
`policies.google.com`, `privacy.microsoft.com`, `www.microsoft.com`,
`www.globalratings.com`, `www.gov.br`, `www.planalto.gov.br`. Redirecionamentos
adicionais devem ser avaliados se ocorrerem. Não alteramos a configuração de rede.
Outra opção é fornecer cópias oficiais vigentes com URL, data e versão, sem dados
privados/credenciais, para conferência. Responder sobre a conta não resolve a falta
de acesso à fonte primária.

## Fatos de conta confirmados, sem inspeção privada

Gmail pessoal gratuito, não Workspace; somente FABRICIO informa acesso. Suporte
AgroLines não iniciado, sem encaminhamento ou download sincronizado informado.
Partner Center usado para preparar cadastro/classificação/listagem/grupo/distribuição,
sem uso de relatórios confirmado. Não há confirmação documental de termos adicionais
ou DPA separados. Esses relatos não substituem as políticas vigentes bloqueadas,
condições comuns realmente aplicáveis, prova de contrato ou segurança implementada.

## Registro de rastreabilidade

`evidencias-fontes-transferencias.json` contém URLs públicas, resultado da consulta,
data, hashes quando obtidos e identificadores de fonte GitHub. Não contém token,
headers de autenticação, e-mails de testadores, mensagens ou arquivos de projetos.
Tentativas de descoberta com 404 não são tratadas como referências autoritativas.
O JSON é documentação interna; não integra o artefato permitido do GitHub Pages.
