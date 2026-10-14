# Configuração posterior, sem credenciais no chat

Nada desta lista foi ativado no GitHub/Partner Center por este PR.

## Modo de validação agora

Push/PR aciona `.github/workflows/windows-msix.yml` sem acesso a chave. Após sucesso:
Actions → Microsoft Store MSIX candidate → execução → Artifacts →
`agrolines-signing-validation-NOT-FOR-SUBMISSION`.

O ZIP contém o MSIX **DIAGNOSTICO-ASSINATURA-PENDENTE**, relatórios antes/depois
iguais e `evidence/signing/plan.json`, reprodutibilidade e binding de origem.
Não enviar o MSIX à Store; o status é de diagnóstico. O gate detecta alterações
inesperadas e para o build; diagnóstico não equivale a promoção de release.

Não usar o MSIX original não assinado para instalação direta, nem baixar/instalar
roots/certificados de teste. A instalação real aguarda fluxo confiável autorizado.

## Promoção controlada para testar a rota Store sem certificado próprio

Depois de resolver procedência/direitos e obter aprovação explícita do responsável,
proteger main e configurar o ambiente com revisor conforme abaixo; definir
AGROLINES_STORE_HOMOLOGATION_AUTHORIZED=`true` e AGROLINES_STORE_REVIEW_REFERENCE
com referência não sensível ao registro real de revisão/autorização. Executar mode
`store-homologation` em main. Nenhuma dessas configurações foi feita aqui.

O job não usa runner/chave de assinatura nem dá aprovação jurídica: verifica o
binding, ausência de drift e procedência, prepara artefato exclusivamente para
homologação privada e para. **A submissão continua manual e depende de autorização
específica.** O campo distribution_approved fica false. Só após receber e testar o
pacote Store legítimo é possível avaliar a confiança de seus catálogos/PE/SAC.
Hoje esse fluxo é bloqueado também pelos 46 registros de origem ainda não fechados.

## Se decidir usar assinatura própria de PE

1. Após compra **autorizada** e validação do fornecedor, preparar Windows dedicado
   com SAC/Defender ativos, SDK/CPython 3.12 oficiais e provider aprovado token/HSM/KSP.
   Não usar esse runner para PRs, fork builds, testes de aplicativos ou uso diário.
   Não registrar os rótulos de bancada/PR no mesmo host. Preferir runner efêmero;
   workspace não pode conter PFX, PIN, credenciais ou projetos reais.
2. Registrar runner com label `agrolines-signing`, acesso restrito ao repositório e
   identidade de serviço com privilégio mínimo. A chave fica no hardware/serviço,
   não no workspace, artefato, chat, variável de ambiente do app ou Git.
3. GitHub Settings → Branches/Rules → proteger `main`; nenhum merge realizado aqui.
4. Settings → Environments → `windows-signing`: Required reviewers (aprovação
   manual antes do job), Deployment branches → Protected branches only. Verificar
   permissões do plano GitHub. A API é consultada novamente antes de usar a chave;
   falha de consulta ou configuração incompleta bloqueia.
5. Revisar cada entrada de `distribution/windows/signing/native-policy.json`.
   Para terceiro: confirmar procedência e direitos aplicáveis no dossiê privado,
   incluir referência não sensível em rights_evidence, origin_confirmed/rights_confirmed
   reais e action sign_third_party para **aquele hash**. Não marcar todos como
   permitidos por serem open source. Preservar signatures/bytes upstream válidos.
   Não resolver ou aprovar automaticamente o licenciamento Qt/LGPL por esse caminho.
6. Conferir a inclusão da CA no programa público Windows e seus roots por fontes
   oficiais/atestados. Registrar hashes SHA-256 e referências não sensíveis em
   approved_public_roots da política, com revisão em main. A lista está vazia;
   cadeia aceita apenas por um root privado/local não basta nem libera a chave.
   Esse pin identifica a âncora aprovada, não substitui a verificação documental
   de participação no programa público. Não instalar roots de laboratório.
   No ambiente protegido, configurar **variáveis públicas de identificação**:
   AGROLINES_PE_SIGNING_THUMBPRINT, AGROLINES_PE_SIGNER_SUBJECT,
   AGROLINES_PE_KEY_PROVIDER e AGROLINES_TIMESTAMP_URL. Devem corresponder ao
   certificado real em CurrentUser/My da conta do runner e a endpoint HTTPS RFC3161.
   O sujeito do PE é a pessoa/entidade verificada pela CA, não o nome de marca
   presumido. Assinatura de licença de cliente é outro mecanismo, sem chave compartilhada.
7. Se GitHub token não puder ler metadados de Environment, usar opcionalmente
   `AGROLINES_ENVIRONMENT_REVIEW_TOKEN`, protegido nesse ambiente, estritamente para
   leitura de ambiente/branch. Preferir token de curta duração de GitHub App com
   permissões mínimas. Nunca token de assinatura/chave privada/PIN nesse campo.
8. Configurar autenticação/MFA do provider por seu método seguro aprovado, fora do
   repositório. Não há importação PFX nem fallback para software/exportação. Se o
   provider exige sessão/PIN interativos, validar operação de CI com o fornecedor;
   script não elimina essa autenticação. Provider e attestation CA precisam de teste.
9. Somente quando autorizado, habilitar AGROLINES_SIGNING_ENABLED=`true` e usar
   Actions → workflow → Run workflow → branch `main`, mode `sign-native`. Não
   habilitar antes de revisão de política/ambiente/certificado. O job é sempre
   omitido em PR/feature branch, ainda que alguém selecione mode sign-native.

Sem esses itens, a implementação está preparada, **não há serviço de assinatura
operacional nem certificado comprovado**. A presença do script não prova integração
real com um provider específico.

## Envelope MSIX

Default: envelope unsigned para eventual fluxo Store autorizado, com identidade
`DelatorreCOrporation.AgroLines`, Publisher `CN=43189595-B928-4D57-90A4-24300E4D4976`,
Store ID `9NRDJ3ZTM978`, PFN `DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg`.
A Microsoft reassina o pacote após certificação; nada é submetido pelo workflow.

AGROLINES_MSIX_SIGN_ENABLED permanece desligado. A opção exige certificado público
legítimo cujo sujeito corresponda exatamente ao Publisher, com
AGROLINES_MSIX_SIGNING_THUMBPRINT/AGROLINES_MSIX_KEY_PROVIDER. Um certificado de
pessoa física normalmente não corresponde a esse GUID; **não alterar Publisher**
para acomodá-lo e não presumir que a CA emitirá certificado com esse sujeito.
A rota Store evita essa contratação para o envelope. Sign-ApprovedMSIX.ps1 falha
se identidade/hash/certificado/timestamp não corresponderem.

Não configurar cobrança, assinatura de licenças de uso ou publicação como parte deste PR.
