# Minuta de estrutura contratual e técnica — não adotada

**PENDENTE DE REVISÃO JURÍDICA.** Não altera licença do repositório nem constitui
contrato aceito. Titularidade/contribuições e razão social/nome do publicador devem
ser conferidos; fabricante informado é pessoa física, não empresa constituída.

## Cláusulas propostas para a futura EULA

1. A licença refere-se ao código original do AgroLines e aos módulos contratados,
   com modalidade, prazo, usuários/instalações e condições expressamente definidos.
   Direitos sobre dados/projetos do usuário não são transferidos por essa licença.
2. Bibliotecas de terceiros permanecem sujeitas às licenças identificadas nos avisos.
   A EULA não restringe permissões que essas licenças asseguram ao destinatário.
3. Eventual proibição de engenharia reversa do código próprio ressalva expressamente
   a engenharia reversa necessária à depuração de modificações de bibliotecas LGPL,
   a modificação dessas partes e os demais direitos legais/licenças aplicáveis.
   Não condicionar esses direitos à aprovação discricionária do fabricante.
4. Não invalidar uma licença legítima unicamente pelo exercício permitido de
   substituição/recombinação das bibliotecas LGPL compatíveis. Alterações podem
   afetar suporte técnico e garantias nos limites da lei e dos direitos de terceiros,
   sem impor penalidade que inviabilize a licença LGPL.
5. Disponibilizar fontes/materiais de terceiros e instruções de obtenção conforme a
   modalidade juridicamente escolhida. Links parciais, avisos genéricos ou mera
   menção ao fornecedor não substituem obrigação de entrega aplicável.
6. Ativação, renovação, limites, uso offline, saída, responsabilidade e direitos do
   consumidor exigem redação proporcional e compatível com regras Store e LGPD.
   Não foram definidos preço, cobrança, prazo comercial ou cláusula de revogação.
7. Não afirmar que PyInstaller impede extração: o runtime contém bytecode passível
   de inspeção. Empacotamento/assinatura não asseguram sigilo absoluto de implementação.

## Arquitetura proposta, sem ativação comercial implementada

Preservar `core/licensing.py`: verificador/entitlements desacoplados do motor GIS.
No futuro, documento de licença com edição/módulos/validade/identificador mínimo,
assinatura assimétrica e chave pública versionada. Emissor e chave privada ficam
fora do cliente/repositório/payload. Ativação online opcional ou arquivo offline;
licença offline válida não depende de heartbeat. Renovação troca documento assinado,
não exige reinstalação. Uso legítimo de biblioteca compatível não deve depender de
seu hash exato coincidir com o release oficial.

Desenvolvimento permanece desbloqueado. Não se implementaram coleta de hardware,
conta/ativação remota, cobrança ou emissão de licenças. Antes de qualquer identificação
por computador/usuário: justificar necessidade, minimização, transparência, base
legal, retenção e tratamento de recuperação/troca. A integridade do MSIX oficial e
as proteções do Windows permanecem preservadas; não equivalem ao token comercial.
