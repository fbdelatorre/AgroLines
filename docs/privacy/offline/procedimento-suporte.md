# Procedimento manual — suporte, direitos e retenção

Responsável pela execução: FABRICIO JOSE DELATORRE. Canal:
FABRICIO.GRUPODELATORRE@GMAIL.COM. Decisões confirmadas em 14/10/2026.
Aplica-se à edição Store offline e ao grupo “AgroLines - Testadores Internos”.
Não há cadastro, envio de e-mail ou limpeza automática no aplicativo.

## 1. Preparar antes de receber dados

- Conferir segurança e acesso da conta Gmail e dos destinos de suporte; ativar
  proteções da conta disponíveis sem inserir credenciais no repositório.
- Criar uma lista privada de controle, com ID do atendimento, contato mínimo,
  finalidade, locais das cópias, abertura, encerramento, prazo-limite de exclusão,
  eventual exceção e confirmação de descarte. Evitar reproduzir o conteúdo sensível
  nessa lista. Não guardar lista, anexos ou dados reais em issues públicas/Git.
- Usar rótulos Gmail `AgroLines/Suporte/Aberto`, `Encerrado` e `Excecao` e uma pasta
  privada por ID quando necessário. Não criar regras de encaminhamento a terceiros.
- Conferir como excluir mensagens/anexos e lixeira no Gmail e cópias locais.
  Selecionar e verificar os arquivos, evitando exclusão indiscriminada de caixas/pastas.
- Validar este procedimento com mensagem e anexos sintéticos. Registrar o resultado.
  Não afirmar que a configuração ou validação da conta já foi realizada por este PR.

## 2. Receber e minimizar

1. Registrar o pedido recebido voluntariamente, atribuir ID e informar a finalidade
   de suporte e a retenção. Não usar conteúdo para publicidade, treinamento ou outra
   finalidade apenas porque foi enviado para diagnóstico.
2. Começar com descrição do erro, versão e passos de reprodução. Solicitar fixture
   sintética e captura recortada antes de projeto completo.
3. Avisar para não enviar senha, token, documentos ou informações pessoais
   desnecessárias. Originais e backups podem conter dados que não aparecem na tela.
4. Revisar cada anexo; remover cópias desnecessárias e não publicar XML bruto, caminhos
   de usuários, SIDs, nomes de máquina ou dados de outros aplicativos no GitHub.
5. Se o original for necessário, explicar o motivo e restringir acesso ao atendimento.
   Compartilhamento externo exige avaliação própria, informação e fundamento; não
   inferir autorização irrestrita do envio voluntário.

## 3. Encerrar e excluir em até 90 dias

1. Registrar a data de encerramento e comunicar a conclusão ou limitação do suporte.
   Calcular `limite = encerramento + 90 dias corridos` para cada atendimento.
2. Fazer revisão semanal. Para não exceder 90 dias entre revisões, descartar os casos
   que vencerão antes da próxima revisão, ou agendar a execução no dia do limite.
3. Localizar mensagens, anexos baixados, cópias de projetos, capturas, relatórios e
   repositórios/artefatos sob controle do responsável pelo ID e registro de destinos.
4. Excluir as cópias selecionadas, inclusive lixeiras sob controle quando cabível.
   Verificar que não permanecem nas contas/pastas/repositórios relacionados. Não
   prometer destruição forense ou eliminação imediata de backups do provedor.
5. Registrar confirmação de descarte sem reproduzir os dados eliminados. Se houver
   obrigação legal ou necessidade justificada, documentar fundamento, dados mínimos,
   restrição de acesso, duração/revisão e nova decisão de descarte. Não usar exceção
   genérica para conservar indefinidamente tudo.
6. Não reiniciar o prazo silenciosamente. Se houver novo atendimento, registrar o
   novo caso e conservar apenas conteúdo ainda necessário à finalidade informada.

O controle de execução/descarte deve ser mínimo. O prazo de suporte não altera
arquivos exclusivamente locais dos testadores. Para os demais controles manuais:

- Grupo: registrar saída/encerramento e `limite = saída/encerramento + 30 dias`.
  Eliminar dados de controle sob responsabilidade própria até esse limite; não
  prometer remoção de registros controlados exclusivamente pela Microsoft.
- Direitos: registrar conclusão e limite de 12 meses **calendários** depois dela.
  Conservar apenas pedido, resposta e evidência mínima necessária, sem manter
  anexos completos de suporte sob o pretexto de comprovar atendimento.
- Usar a mesma revisão semanal antecipada e registro mínimo de exceções para esses
  prazos. Informações que se encaixem em finalidades distintas devem ser minimizadas
  separadamente; não estender a retenção de todo o suporte para 12 meses.
- Definir/documentar retenção dos próprios comprovantes mínimos de descarte antes
  da operação; não armazenar o conteúdo eliminado dentro do registro.

Comunicar mudanças relevantes da política manualmente por e-mail, apenas com contatos
legitimamente disponíveis; não executar envios sem autorização. Não extrair contatos
para finalidade nova nem publicar a lista de testadores no GitHub. Conferir os
relatórios realmente consultados no Partner Center antes de registrar sua utilização.
Nenhuma base legal está definitivamente escolhida neste procedimento; revisar a
minuta de participação e o documento de hipóteses antes de receber dados reais.

## 4. Atender direitos

- Registrar data e pedido, confirmar recebimento e localizar dados sob controle.
- Preferir confirmação pelo canal já usado e perguntas mínimas. Documentos só quando
  necessários e proporcionais; não exigir cópia automaticamente ou pedir senha/token.
- Tratar confirmação/acesso conforme LGPD art. 19, inclusive resposta simplificada
  imediata ou declaração completa no prazo legal de até 15 dias quando aplicável;
  verificar exigências atuais específicas para os demais direitos. Não impor um
  prazo único inventado para todo pedido nem substituir prazos legais por 90 dias.
- Executar correção, informação e exclusão quando cabíveis; considerar anexos,
  backups sob controle e exceções legais documentadas. Comunicar ação/limitação com
  justificativa. Não apagar dados de outras pessoas ou projetos sem legitimidade.
- Explicar quando se trata de projeto que existe somente no computador do usuário:
  não há cópia remota automática para o responsável excluir. Orientar gerenciamento
  local e encaminhamento ao controlador de origem quando necessário.
- Não solicitar acesso remoto indiscriminado ao computador para demonstrar exclusão.

## 5. Incidentes e exposição acidental

1. Registrar relato, data, escopo conhecido e contato. Interromper links/encaminhamentos
   ou acesso acidental sob controle sem destruir evidências necessárias.
2. Avaliar confidencialidade, dados afetados, pessoas, destinatários e risco/dano;
   priorizar eventual dado de menor e informações sensíveis.
3. Solicitar remoção a destinatários/provedores quando cabível e proteger credenciais
   afetadas. Não prometer recuperar todas as cópias ou que o software detectará tudo.
4. Verificar LGPD art. 48 e regulamento vigente da ANPD, decidir e executar comunicação
   quando exigida, nos prazos aplicáveis; manter registro da avaliação e das medidas.
5. Informar titulares de forma clara quando necessário, minimizar os dados no relato
   e corrigir a causa. Não anexar publicamente o conteúdo exposto para provar o incidente.

## 6. Eventuais menores

Não há limite etário definido nem coleta de idade no aplicativo. Antes de incluir
ou receber dados de menor conhecido, avaliar melhor interesse (LGPD art. 14),
necessidade e base legal. Consentimento, quando usado para criança, deve observar
as condições legais de participação do responsável; não presumir que qualquer
mensagem de adolescente exige automaticamente consentimento parental.

Preferir testes sintéticos sem dados de terceiros. Não pedir documento/idade de
cada usuário sem necessidade. Em suporte/pedido envolvendo menor, reduzir anexos,
explicar de forma compreensível e envolver responsável legal quando aplicável,
verificando legitimidade proporcionalmente. Se não for possível cumprir os controles,
recomendar limitar a audiência inicial a adultos conhecidos, como decisão futura
explícita, e não como restrição já adotada.

Microsoft administra contas e distribuição; isso não substitui as obrigações do
responsável sobre dados que ele recebe. Confirmar classificação etária e controles
reais do grupo no Partner Center antes da distribuição, sem alterar nada neste PR.

## Implementado versus manual

| Medida | Situação |
|---|---|
| Não enviar suporte automaticamente | Controle técnico no pacote offline dependente; testes no relatório |
| Bloquear recursos remotos | Código/testes; homologação Windows/Store ainda pendente |
| Projetos, versões, backup e restauração locais | Código/testes existentes preservados |
| Registro, encerramento, prazo e limpeza de suporte | Procedimento manual adotado; configurar e validar pelo responsável |
| Direitos, incidentes, minimização e menores | Procedimento manual; comprovar execução antes de receber dados reais |
| Cifra de projetos/backup | Não implementada; não prometer |
| Apagar dados em provedores fora do controle | Não garantido; não prometer |
