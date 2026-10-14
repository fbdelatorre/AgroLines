# Modelos vazios — controle privado manual

Estes CSVs têm **somente cabeçalhos**, sem pessoas reais nem aceites simulados.
Copiar para fora do checkout, em pasta privada sem sincronização não aprovada.
Usar editor local/planilha protegida por acesso da conta Windows; não converter
em Google Sheets/Drive ou outro serviço sem decisão/análise próprias. Não guardar
registros preenchidos no GitHub, CI, Pages ou projetos agrícolas. CSV não é cifrado.

## Participação — testadores.csv

- `id_testador`: ID interno, por exemplo `T0001`; não é anonimização garantida.
- `contato_participacao`: somente e-mail legitimamente usado no convite.
- `conta_microsoft_grupo`: e-mail da conta pessoal exigida pelo grupo; não repetir
  se for o mesmo contato — usar indicação `mesmo_contato`. Se diferente, registrar
  a associação confirmada pelo canal conhecido, sem senha/documentos.
- `declarou_18_mais`: `sim` somente após declaração efetiva; não inferir idade.
- `termo_versao`, `termo_sha256`, `politica_versao`, `politica_sha256`: arquivos
  efetivamente apresentados; hash tem 64 dígitos hexadecimais e não contém segredo.
- `aceite_em`: data/hora com fuso do e-mail recebido, formato ISO 8601.
- `evidencia_privada`: referência à mensagem/conversa/arquivo privado que relaciona
  remetente, resposta e convite; não URL pública nem conteúdo integral.
- `entrada_em`, `saida_em`, `excluir_ate`: datas ISO `AAAA-MM-DD`; último campo é
  saída/encerramento + até 30 dias; não preencher antes de conhecer o evento.
- `estado`: `ativo` ou `encerrado`. Não registrar convite como participante ativo;
  a necessidade/retenção de pendentes ainda exige decisão prévia.
- `locais_copias`: referências mínimas a Gmail/registro/`.eml`/backup controlados.
- `excecao_ref`: referência privada ao fundamento/duração/revisão, se houver.

Nome completo, CPF, RG, nascimento completo, imagem ou documentos não são campos
padrão. Não registrar credenciais ou método/códigos de recuperação da conta.

## Suporte — suporte.csv

ID `S0001`, contato, abertura ISO/data e estado `aberto`, `aguardando` ou `encerrado`.
Referência à conversa e aos destinos de cópias, datas de fechamento e limite
`encerramento + 90 dias corridos`; exceção apenas com justificativa privada.
Não copiar assunto/conteúdo do projeto ou da mensagem para o controle.
Quando eliminar o registro do caso, a prova de descarte deve ser mínima e separada,
sem reproduzir dados; sua retenção ainda depende de decisão prévia.

## Direitos — direitos.csv

ID `D0001`, contato, recebimento, tipo do direito (categoria curta, sem conteúdo),
prazo aplicável **verificado**, estado `aberto`/`concluido`, referência à resposta,
conclusão, limite de 12 meses calendários, destinos e exceção. `verificacao_resumo`
contém apenas método proporcional (por exemplo canal conhecido), nunca documentos
ou respostas pessoais. `resultado_resumo`: ação ou limitação sucinta, sem dados
do titular. A retenção de 12 meses não é prazo para responder ao pedido.

## Uso seguro e exclusão

Preferir campos como texto na planilha. Não colar mensagens, fórmulas ou conteúdo
de anexos; valores iniciados por `=`, `+`, `-` ou `@` podem ser interpretados como
fórmulas. Importar como texto ou usar editor de texto, sem macros/links ativos.
Não abrir CSV de terceiros como se fosse um modelo confiável. Limitar campo livre
a descrições neutras e referências privadas. Revisar destinatários antes de enviar
e-mail; não exportar lista para relatório público.

Rótulo Gmail ou exclusão de linha do CSV não apaga as outras cópias. Seguir
[retenção/exclusão](../retencao-e-exclusao.md) e conferir mensagens, enviados,
lixeiras, pastas e backups. Pseudônimos continuam protegidos enquanto identificáveis.
Após descarte do caso, não conservar uma cópia antiga da planilha por hábito.

As evidências de aceites/atendimentos reais só existirão após execução. O [plano
mínimo](../plano-operacional-minimo.md) separa decisões, configuração e revisão jurídica.
