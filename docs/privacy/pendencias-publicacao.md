# Pendências de privacidade antes da disponibilização aos testadores

Escopo: política e requisitos de dados. Não é autorização para publicar/submeter,
alterar a conta Microsoft ou adquirir serviços. A distribuição privada não dispensa
transparência ou os requisitos aplicáveis da Store/LGPD.

## Confirmado e já preenchido

- Responsável pessoa física: **FABRICIO JOSE DELATORRE**.
- Contato: **FABRICIO.GRUPODELATORRE@GMAIL.COM**. Gmail é o serviço do canal de contato;
  não prova fornecedor SMTP de recuperação ou infraestrutura do aplicativo.
- Distribuição inicial a grupo privado por conta de desenvolvedor Individual.
- Poderá existir colaboração online opcional para **testar** o produto; projetos
  locais não devem depender de autenticação remota contínua.
- Nome do publicador Store atual: **Delatorre COrporation**. Não é prova de empresa
  constituída nem substitui o nome legal da pessoa responsável.

## Bloqueadores de finalização/publicação da política

| ID | Informação/ação necessária | Critério de conclusão |
|---|---|---|
| P01 | Rever conta Individual e nome “Delatorre COrporation” à luz da cláusula 10.14 | Responsável obtém avaliação/regularização apropriada com Microsoft; não declarar empresa/CNPJ fictícios nem alterar identificadores neste trabalho |
| P02 | Hospedar política final em URL HTTPS pública estável | Usuário acessa sem login; sem conteúdo contraditório, placeholders ou tracking não declarado; responsável insere URL no Partner Center em ação futura autorizada |
| P03 | Decidir exatamente o que será habilitado no grupo | Informar se contas/servidor, SMTP, imagens e recepção de relatórios estão habilitados; testar a política contra o build/configuração realmente distribuídos |
| P04 | Identificar operador e infraestrutura de API, banco, logs e backups | Nome legal/contato, domínios, fornecedor, países de processamento, acesso administrativo e medidas implantadas; não inferir de localhost/Compose |
| P05 | Identificar SMTP e remetente, ou confirmar recuperação desabilitada | Fornecedor, política, países e dados recebidos; comprovar configuração TLS; distinguir do Gmail de privacidade |
| P06 | Definir bases legais por finalidade e papéis | Documentar hipóteses da LGPD, termos/acordo dos testes e legitimidade de dados de terceiros; se usar legítimo interesse, avaliar necessidade/balanceamento; consentimento não pode ser irrestrito |
| P07 | Definir retenção/descarte efetivos | Critérios/prazos por contas, hashes/sessões, tentativas, convites, auditoria, originais/histórico, logs, backup, suporte e grupo; responsáveis/processo de descarte e exceções legais justificadas |
| P08 | Tornar atendimento de direitos efetivamente executável | Canal verificado, fluxo proporcional de identificação, execução de acesso/correção/exclusão/portabilidade quando cabível e tratamento de backups/history/FKs. Não há delete-account no app |
| P09 | Definir suporte e relatórios | Quem recebe, quais campos/arquivos, canal, acesso, redação/minimização e retenção; se GitHub receber, explicar e avaliar transferências/acessos. Não chamar XML bruto de anônimo |
| P10 | Verificar transferências internacionais | Confirmar países e fundamento/mecanismos aplicáveis com fornecedores reais; incluir Gmail/Google, Microsoft/Store e GitHub nos fluxos em que forem usados; não prometer armazenamento exclusivo Brasil |
| P11 | Definir idade/gestão do grupo e dados de inscrição | Confirmar se há menores, dados de audiência privada/convites externos e avaliações; documentar responsabilidades/autorizações necessárias |
| P12 | Definir resposta a incidentes e atualização da política | Pessoas/canais, análise e comunicações legais, procedimento de aviso, data de vigência. Não prometer detecção ou notificação automática inexistente |

Não publicar a minuta com os campos `[CONFIRMAR: ...]`. Os dados conhecidos foram
preenchidos; os demais campos não podem ser resolvidos com inferências sobre nomes
de bibliotecas ou o endereço Gmail do responsável.

## Pontos técnicos/operacionais a resolver conforme os recursos habilitados

### Dados pessoais em arquivos e compartilhamento

- O original completo pode conter metadados não exibidos. Estabelecer revisão e
  minimização antes de transmitir; não basta remover uma coluna do mapa.
- Viewer da propriedade inteira obtém fontes pela API com permissão read. Decidir
  se esse comportamento é desejado, informar claramente e, se necessário, separar
  autorização de originais/exportação. Não afirmar “somente leitura impede download”.
- Rever opt-in/descrição/destinatários/opt-out de 10.5.2 e consentimento escrito de
  não clientes de 10.5.3. Convite/aceite e flag TILE_AUTHORIZED não comprovam todos
  esses requisitos. Configurar ou restringir o teste antes de usar informações reais.
- Revogação não apaga originais/histórico/cópias de destinatários. Procedimento de
  direitos precisa contemplar essas limitações e identificar os controladores das cópias.

### Proteção e retenção

- Avaliar/implantar medidas proporcionais e demonstráveis para SQLite, arquivos
  originais, backups e banco/infraestrutura do servidor, inclusive requisitos de
  criptografia da cláusula 10.5.4. O código não fornece cifra SQLite; DPAPI não é
  proteção do projeto. Não assumir BitLocker, TLS de PG ou backup cifrado sem evidência.
- Definir política e processo de limpeza; validade de token/convite ou limite de
  200 eventos por consulta não são retenção. As tabelas atuais não têm rotina de purga.
- Planejar correção/eliminação minimizada diante de histórico imutável e fontes
  integrais. Exclusão manual de conta precisa respeitar vínculos e direitos dos
  demais participantes; não remover bancos/revisões indiscriminadamente.
- Revisar access/error logs, proxy e exceções/SQL, redação de parâmetros, acesso,
  retenção e backups. Mensagem SMTP genérica e 422 sanitizado não cobrem toda infraestrutura.
- Explicar que fechar/desinstalar não é logout ou exclusão remota e que arquivos
  DPAPI/relatórios externos podem permanecer. Conferir o ciclo no MSIX assinado real;
  a intenção de unvirtualizedResources ainda não é uma garantia de retenção validada.

### Terceiros, imagens e diagnóstico

- Se tiles forem habilitados, identificar fornecedor e parâmetros da URL, tráfego
  de viewport, cookies temporários e autorizações necessárias. Modo local permanece
  sem provedor, mas isso não torna o modo online equivalente.
- Rever redirecionamentos do healthcheck e destinos de rede reais. O NoRedirect
  autenticado não cobre esse fluxo; fechar colaboração interrompe seu timer, mas
  abrir a janela já inicia requisições periódicas.
- Limitar/redigir XML de eventos e caminhos de usuário antes de compartilhar
  diagnósticos. O código registra eventos não associados ao app; pode expor outros
  programas, nomes de máquina e SIDs. Rever upload-artifact automático de bancada
  real, inclusive em falhas, visibilidade de repositório e retenção configurada.
- Confirmar dados que o responsável pretende usar de Partner Center/Windows/Store,
  Gmail e eventual ferramenta de suporte. Ausência de SDK analytics próprio não é
  prova de ausência de tratamento de plataforma.

## Antes de liberar a audiência privada

1. Fechar P01–P12 e substituir os campos com informação verdadeira e verificável.
2. Revisar minuta e build/configuração final. Publicar apenas a política revisada
   em hospedagem escolhida e autorizada; cadastrar URL posteriormente, com autorização.
3. Preferir fixtures sintéticas durante a validação dos controles. Isso reduz
   risco, mas não dispensa proteção de contas reais ou metadados de bancada/testadores.
4. Verificar acesso à política e canais de direitos com um testador, sem publicar
   dados pessoais reais em issues/artefatos para demonstrar funcionamento.
5. Guardar registro de versão, auditoria e confirmações do responsável. Atualizar
   a política e os controles antes de acrescentar novos fluxos de dados.

Este trabalho entrega texto e evidências. Não altera a conta, a identidade MSIX, o
manifesto, o aplicativo, bancos de produção, configurações Microsoft ou publicação.
