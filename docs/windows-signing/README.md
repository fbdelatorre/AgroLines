# Assinatura permanente e confiança do AgroLines

Implementação proposta no PR #14, branch `integration/store-candidate`.
Sem compra, assinatura efetiva, merge, instalação de certificados ou envio à Store.
Auditoria jurídica Qt/LGPL e seus documentos permanecem separados e pendentes.

## Decisão recomendada

**Priorizar a rota MSIX oficial da Store e comprovar a confiança do pacote entregue,
antes de contratar um certificado.** A Microsoft informa que reassina MSIX após a
certificação, gratuitamente, e dispensa compra/gestão de certificado nesse fluxo.
Isso não é promessa de que cada DLL/PYD receberá assinatura Authenticode embutida
nem de aprovação SAC. Não confundir esse fluxo com MSI/EXE na Store, onde o
publicador deve assinar instalador e PE. Fonte oficial atual: [opções de assinatura](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options).

Não submeter nesta tarefa: faltam direitos/avisos, autorização e homologação real.
Foi preparada verificação do **pacote instalado com SignatureKind Store**, da
assinatura embutida de cada PE e, quando existir, de sua associação criptográfica
explícita ao catálogo `AppxMetadata/CodeIntegrity.cat`. Catálogo ausente ou sem
cobertura não vira aprovação. A assinatura do envelope garante integridade do
pacote; só o catálogo e a política Windows aplicáveis podem estabelecer essa rota
adicional de confiança por arquivo. É preciso observar o pacote efetivamente recebido.

Para assinatura embutida dos PE, distribuição direta futura ou arquivos fora da
proteção/catalogação do pacote, preparar **certificado público não EV para pessoa
física**, condicionado à aceitação do Brasil/nome legal por uma CA. O código dá
suporte a SignTool com chave não exportável via CSP/KSP de token/HSM, inclusive
remoto quando o fornecedor suporta esse mecanismo. Não há elegibilidade/preço
individual confirmado com fornecedor; solicitar cotação e prova de requisitos.
**Não exigir constituir empresa nem comprar EV por inferência.**

## Evidências reutilizadas e ausência de redução Qt

Baseline original: 453 PE, 375 SignTool aceitos, 78 unsigned, 67 unsigned carregados,
72 NotTimeValid genéricos aceitos pela política Authenticode. SHA-256 do MSIX:
`22286add49d873625f6a3ab898dc2b772b5514dd4fc30cddcfdbcfa369ea2a36`.
Inventário, origem por hash e cargas em `docs/native-store-audit/` foram reaproveitados.
Não se repetiu a auditoria original de carga. Novos builds verificam só seus bytes
atuais e o desvio perante essa política.

**Não existe redução Qt no head inicial 3c7f5fb desta tarefa**; não inventar contagem
reduzida. Não removemos componentes ou trocamos versões/drivers/algoritmos. Alteração
futura de payload exige atualização revisada da política e regressões que justifiquem
adição/remoção. Não observado no polling não significa dispensável.

## Pipeline e bloqueios

Workflow: `.github/workflows/windows-msix.yml`, com três modos:

- **validation** (push/PR e padrão manual): instala inputs Windows 3.12.10 x64 com
  lock/hashes, fixa SOURCE_DATE_EPOCH e PYTHONHASHSEED, compila duas vezes e compara
  todos os bytes do payload no mesmo builder; não promete MSIX idêntico entre
  máquinas/SDKs. Executa testes, inventário/proveniência, Authenticode e SignTool,
  avalia política por arquivo, empacota/abre/verifica identidade e integridade, roda
  probes congelados locais. Sem chave/certificado: `ASSINATURA PENDENTE`, antes/depois
  iguais, flags de distribuição/SAC false. Só há artefato de diagnóstico, nunca
  promoção automática ou envio à Store.
- **sign-native**: exclusivamente workflow_dispatch de `refs/heads/main` protegida,
  repositório exato, variável habilitadora, ambiente `windows-signing` com revisor
  obrigatório e runner separado `agrolines-signing`. Não executável por PR/fork.
  A verificação da proteção falha fechada se a API não puder ser consultada. O fluxo
  continua desabilitado nesta branch e não alteramos configurações GitHub.

- **store-homologation**: rota independente de certificado próprio, somente dispatch
  de main protegida, autorização específica AGROLINES_STORE_HOMOLOGATION_AUTHORIZED,
  referência de revisão manual/legal e ambiente com revisor. Exige todos os arquivos
  conhecidos, sem drift e procedência fechada. Prepara apenas cópia identificada
  para teste privado na Store, **não envia**. Os 46 casos de origem ainda pendentes
  bloqueiam essa promoção hoje. Validade de catálogos/PE e SAC só se avalia depois
  da entrega legítima pela Microsoft; não exigir compra de certificado para iniciar
  essa avaliação autorizada. Distribuição a clientes continua não aprovada.

A construção ocorre em runner hospedado **sem credenciais de assinatura**. O runner
com token/HSM recebe só o artefato da mesma execução, valida commit/política/lock e
hashes, refaz verificações e **não executa o AgroLines**. Usa CPython 3.12/SDK de
manutenção previamente confiáveis, não instala dependências de build nesse host.
O pacote cliente continua sem Python/pip/PostgreSQL externos.

A política exige:

1. Cobertura exata dos PE x64; paths canônicos, sem symlinks/reparse points, adições,
   remoções ou alterações de terceiros não revisadas.
2. Hash original e assinatura upstream preservados; falha de assinatura existente
   bloqueia, sem sobrescrever/reassinar para esconder erro. Os 72 NotTimeValid
   genéricos não são rejeitados se Authenticode/SignTool/timestamp forem aceitos.
3. EXE próprio recompilado ligado ao commit aprovado; apenas o caminho explícito
   AgroLinesPoC.exe pode receber essa classificação, nunca wildcard por extensão.
4. Terceiro somente com origem e direitos documentados, hash exato e ação
   `sign_third_party` revisada. Hoje os 77 unsigned de terceiros estão bloqueados;
   46 arquivos assinados ainda precisam fechar procedência. O processo não inventa
   autorização jurídica nem a estende a módulos Qt/GPL.
5. Preflight completo antes de acessar chave; certificado público, EKU Code Signing,
   sujeito/thumbprint/provider esperados, validade/revogação/cadeia sem overrides,
   não exportável, provider aprovado e root de CA fixado na política após revisão
   documental do programa público (lista ainda vazia). Confiança privada/local não basta. Nome do provider não comprova certificação
   HSM por si só: atestado/contrato da CA é pré-requisito manual. RSA/ECC são aceitos
   pelo código, sujeitos ao SDK e ao Windows alvo.
6. Assinar só os hashes autorizados com SHA-256 e timestamp RFC3161 HTTPS. Verificar
   todos os PE por SignTool; originais permanecem byte a byte, e os novos mantêm
   o conteúdo anterior, admitindo apenas campos de assinatura/checksum, alinhamento
   zero e tabela de certificado acrescentada no final. Esse hash de conteúdo é uma
   proteção adicional, não uma implementação substituta de Authenticode.
7. Congelar manifesto **depois** das assinaturas, gerar envelope e verificar os bytes
   reais no MSIX. Assinatura opcional de envelope exige certificado legítimo com
   Publisher oficial exato. Certificado pessoal comum para PE não autoriza trocar
   o CN GUID da Store. Normalmente deixar o envelope para a Store.
8. Falha de critério impede artefato de candidato assinado. Evidências de falha podem
   ser guardadas; o artefato diagnóstico é claramente `NOT-FOR-SUBMISSION`.

`Sign-Payload.ps1` é agora um wrapper com plano/política obrigatórios, sem assinatura
cega de todo unsigned. O antigo workflow `windows-poc-signed.yml` foi aposentado
com job incondicionalmente desabilitado, evitando a rota antiga sem esses controles.

## Arquivos entregues

- `distribution/windows/signing/native-policy.json`: política executável dos 453 PE.
- [matriz-arquivos.csv](matriz-arquivos.csv): decisão, origem, bloqueio e alternativas por arquivo.
- `scripts/signing_pipeline.py`: inventário correlacionado, drift/reprodutibilidade,
  binding, pós-assinatura e verificação de pacote; não acessa chaves.
- `Signing-Helpers.ps1`, `Sign-ApprovedNative.ps1`, `Sign-ApprovedMSIX.ps1`,
  `Assert-SigningEnvironment.ps1`, `Test-SigningGuards.ps1`: CSP/KSP e gates.
- `Test-StoreDeliveredTrust.ps1`: leitura de confiança embutida/catálogo no instalado.
- [opcoes-e-custos.md](opcoes-e-custos.md), [configuracao.md](configuracao.md),
  [homologacao.md](homologacao.md): decisões, operação e bancada real.
- [fontes.json](fontes.json): fontes, hashes/blobs consultados e acessos bloqueados.

O licenciamento de uso do AgroLines, as pendências Qt/LGPL e a política de
privacidade não foram aprovados ou alterados por esta implementação.
