# Rotas legítimas, custos e elegibilidade

Consulta: 14/10/2026. Brasil, pessoa física, sem empresa ou certificado confirmados.
Preços abaixo são referências gerais da **Microsoft**, não propostas comerciais de
CAs nem custo total para este responsável. Não foi comprada licença ou assinatura.
URLs/status e SHA-256/blobs em [fontes.json](fontes.json).

| Alternativa | Elegibilidade/requisitos | Custo fundamentado ou cotação | CI / limitações / confiança esperada |
|---|---|---|---|
| Microsoft Store **MSIX** | Conta/app já cadastrados; identidade oficial; políticas e certificação | Microsoft declara assinatura gratuita; custos/condições da conta não avaliados | Microsoft reassina pacote. Sem compra de certificado para esse fluxo. Verificar catálogo/PE recebido e Windows 11 SAC real; sem garantia automática para todos os DLL/PYD |
| CA pública não EV / Individual | CABF admite pessoa natural/nome legal; CA deve confirmar emissão para residente no Brasil, requisitos e território | Cotação obrigatória. Microsoft cita OV genérico US$150–300/ano, **não preço confirmado para pessoa física**, sem impostos/token/frete/HSM/limites | CSP/KSP + token/HSM pode integrar runner protegido. Chave protegida, autenticação e timestamp. Assinatura pública pode fornecer confiança, não imunidade a Defender/SAC nem reputação instantânea |
| OV de organização | Nome comercial não prova organização constituída. Não elegível automaticamente ao produto OV ofertado a empresas | Cotação; mesma faixa genérica não prova contratação possível | Não fornecer CNPJ/empresa/endereço fictícios. Perguntar explicitamente por modalidade Individual não EV, não comprar OV organizacional por dedução |
| EV | CABF exige verificação mais rigorosa de existência/atividade/autoridade, conforme categoria de entidade. Perfil atual não comprovadamente elegível | Microsoft cita US$400+/ano genérico; proposta/entidade/taxas dependem da CA | Não recomendar só para eliminar alertas: Microsoft informa fim de bypass instantâneo SmartScreen em 2024. Não é garantia SAC |
| SSL.com eSigner | Integração oficial GitHub consultada; conta/credential ID e permissão contratual. Brasil/Individual não confirmados nas páginas comerciais bloqueadas | Cotar certificado + plano/cloud + 78 assinaturas iniciais por build e demais EXE/instaladores, timestamp, quotas e renovação | README mostra usuário/senha/TOTP/credential ID e batch; não foi instalado/ativado. API/Java requer adaptador próprio depois de escolher o serviço; não copiar exemplo TEST/develop ou armazenar MFA ao lado de senha sem análise |
| DigiCert Software Trust Manager | Conta DigiCert ONE, credenciais e certificado aceito; Individual/Brasil pendentes | Cotação de certificado/serviço, operações, lote, HSM e usuários. Não tratar trial como licença de produção | Repo oficial atual descreve Simple Signing e CSP/KSP/SignTool. KSP já é a interface preparada neste PR, após instalação aprovada do cliente. Action antiga ssm-code-signing foi descontinuada em 2026; não adotá-la |
| Certum / SimplySign | Candidato a consultar, não fornecedor elegível comprovado | Cotação; páginas oficiais inacessíveis pelo proxy nesta consulta | Confirmar natural person/Brasil, entrega de token ou automação remota e suporte a PE .pyd. Não afirmar disponibilidade ou preço sem resposta |
| Artifact Signing Public Trust | Quickstart vigente: indivíduos EUA/Canadá; responsável residente no Brasil | Não é alternativa elegível demonstrada; referência genérica Microsoft ~US$9,99/mês não resolve elegibilidade | Não cadastrar endereço/empresa fictícios. Private Trust/test signing não fornece confiança pública de clientes |
| Manter onedir/MSIX, reduzir payload dispensável após prova | Preserva núcleo, dependências ABI e formatos | Sem custo de certificado por simples redução; trabalho/testes a estimar | Diminui superfície/operações, não transforma unsigned em confiável. Nenhuma redução autorizada/executada aqui. Onefile não resolve: DLLs/PYDs extraídos continuam sujeitos a confiança |
| Build próprio de bibliotecas | Fonte exata, toolchain/options/drivers/licenças e testes de precisão | Trabalho/manutenção + certificado/serviço se rota própria | Último recurso, não recompilar sem necessidade; compilação não produz assinatura pública automaticamente |
| SignPath Foundation gratuito / certificados de teste | Programa citado pela Microsoft é para open source qualificado, não prova elegibilidade do produto proprietário | Não assumido como alternativa gratuita para AgroLines | Nenhum autoassinado, Developer Mode, instalação manual de root ou exceção adotada |

CABF CSBR oficial consultado: identidade Individual (§3.2.3), proteção de chave
(§6.2.7), e máximo de validade de certificados emitidos a partir de 01/03/2026 de
**460 dias** (§6.3.2). Assinatura timestamped continua sendo verificada segundo sua
política; não confundir expiração genérica atual com rejeição Authenticode.
Tokens/HSM/serviços têm requisitos específicos por papel: confirmar o nível e
atestado aceitos pela CA, não afirmar que qualquer token USB ou KSP é certificado.

## O que confirmar por escrito antes de contratar

1. Pessoa física residente no Brasil, nome legal real, sem pessoa jurídica; modalidade
   de certificado e documentos requeridos **somente no portal seguro do fornecedor**.
2. Cadeia no programa de raízes Windows para Code Signing, algoritmos/SDK, token/HSM
   aprovado, não exportação da chave e titularidade da identidade que aparecerá aos usuários.
3. EXE, DLL e **PYD (PE)**, permissões de assinatura de cópias redistribuíveis de
   terceiros e eventuais políticas de malware/supply chain do próprio serviço.
4. Custos totais: emissão/renovação, impostos/câmbio, token/frete, instalação de
   middleware, assinatura por arquivo/hash/lote, usuários/CI, quotas/rate limits,
   retenção de logs, timestamp e suporte. Não contar apenas um MSIX como uma assinatura
   se serão assinados 78 PE internamente.
5. Autenticação interativa/MFA ou server-to-server aprovada, disponibilidade de CSP/KSP
   e execução não interativa Windows, revogação/recuperação, auditoria e isolamento.
6. Se serviço requer upload de binário ou somente hash, termos de confidencialidade
   e localização/tratamento; não enviar código/projetos automaticamente para orçamento.
7. Endpoint RFC3161 HTTPS suportado e verificação de timestamp/cadeia em testes reais.

As páginas comerciais de SSL.com/Certum/DigiCert/GlobalSign foram bloqueadas pelo
proxy antes do servidor nesta sessão; isso **não é prova de inelegibilidade**. A
integração oficial GitHub comprova funcionalidades documentadas, não preço, contrato
ou admissão do responsável no Brasil. Não escolher fornecedor como contratado sem
essas respostas. Não foi contatado fornecedor em nome do usuário.

A decisão de compra pode ser adiada até avaliar confiança Store/catálogo/SAC do
pacote real, após autorização e saneamento jurídico. Caso se escolha assinatura
própria, comparar cotações de certificado Individual público + CSP/KSP/HSM; o código
já aceita essa interface sem trocar algoritmos GIS ou identidade MSIX.
