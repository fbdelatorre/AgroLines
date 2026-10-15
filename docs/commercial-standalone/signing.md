# Assinatura futura: fluxo preparado, nenhuma chave utilizada

**PARCIAL: infraestrutura implementada; assinatura real BLOQUEADA por autorização,
certificado público elegível e revisão dos direitos por arquivo.**
Não foi comprado/emitido certificado, utilizado segredo nem assinado arquivo.

## Escopo e preservação

O runtime de referência tem **178 PE: 100 aceitos e 78 NotSigned**, sendo 77 de
terceiros e o executável AgroLines. A estratégia conserva byte a byte os 100
originais com assinatura válida; nunca remove ou sobrescreve assinatura upstream.
Na execução nova, o verificador X509 informou 72 cadeias completas e 106 arquivos
sem verificação completa: 78 sem assinatura + 28 cadeias adicionais inconclusivas.
Isso é distinto dos 100 aceitos por Authenticode/SignTool; não tratar 106 como
assinaturas inválidas nem 100 como prova de que todos os verificadores concordam.
Investigar os estados por arquivo antes da assinatura/homologação real, mantendo
os dois relatórios e as evidências de rede/revogação/tempo da coleta.

[Prepare-SigningPlan.ps1](../../distribution/windows/standalone/Prepare-SigningPlan.ps1)
e o pipeline existente vinculam hashes, origem e permissões. As 77 dependências
não recebem autorização genérica: exigir direito de redistribuição e de assinatura
daquela cópia, conforme licença/termos e política da CA. Assinar como redistribuidor
não significa autoria upstream; preservar atribuições e hashes anterior/posterior.

O launcher é **um PE próprio adicional fora dos 178 do runtime**. Contando launcher,
instalador e desinstalador, o lote inicial conservador tem até **81 arquivos novos
para assinar** (77 terceiros + quatro papéis próprios: app, launcher, setup, unins).
Não são 178 assinaturas novas. Reutilizar futuramente terceiros já legitimamente
assinados e imutáveis pode reduzir lotes recorrentes; cache de assinaturas **não
foi implementado** neste PR e não é economia já garantida.

## Implementação concreta

1. [Sign-ApprovedNative.ps1](../../distribution/windows/signing/Sign-ApprovedNative.ps1)
   assina somente entradas expressamente aprovadas do plano e preserva as upstream.
   Transição de inventário/manifesto existente registra bytes antes/depois e confere
   que somente campos de assinatura/checksum foram alterados.
2. Novo [signing-configuration.example.json](../../distribution/windows/standalone/signing-configuration.example.json)
   tem todas as autorizações **false**, sem certificado/segredo. Não habilitar por
   simples cópia do exemplo. Exige SHA do fonte, candidato, versão, hashes do gate,
   manifesto do runtime assinado, launcher/fonte, compilador e registros das revisões.
3. [Sign-OwnedComponent.ps1](../../distribution/windows/standalone/Sign-OwnedComponent.ps1)
   recusa PR/branch desprotegida antes de arquivos/chaves; usa o guard existente de
   `workflow_dispatch`, main protegida, ambiente `windows-signing` com revisor e
   commit exato. Não foi criada/alterada proteção no GitHub. Esse fluxo permanece
   indisponível na branch atual; requer autorização futura e incorporação apropriada.
4. Cada papel próprio exige autorização/direitos separados, CompanyName/versão,
   arquivo novo NotSigned, escopo isolado sem reparse, compilador aprovado, gate
   nativo aceito, conferência real de **dist/AgroLines** e SignTool de todos os PE.
   Não aceita validar uma pasta e empacotar outra. Não aplica assinatura a fornecedor
   em nome de componente próprio.
5. Valida identidade do certificado, raiz pública previamente aprovada, cadeia/
   revogação/EKU e CSP/KSP protegido via helper existente; sem PFX/chave exportável,
   root de teste ou instalação de certificados. Timestamp RFC3161 HTTPS com SHA256;
   pós-verificação SignTool/Authenticode, thumbprint e timestamp; conteúdo PE deve
   permanecer igual exceto regiões permitidas. Produz `.signing.json` por arquivo.
6. [Build-SignedHomologation.ps1](../../distribution/windows/standalone/Build-SignedHomologation.ps1)
   e [callback Inno](../../distribution/windows/standalone/Inno-SigningCallback.ps1)
   preparam compilação com `SignedUninstaller=yes`, temporário exclusivo e compilador
   oficial vinculado por hash. Nome de saída:
   `AgroLines-Standalone-<versão>-x64-<candidato>-HOMOLOGACAO-ASSINADO-SAC-PENDENTE.exe`.
   Este nome é uma intenção do fluxo, **não um instalador assinado já existente**.

Nenhum workflow de PR chama esses signers. O teste
[Test-SigningDenial.ps1](../../distribution/windows/standalone/Test-SigningDenial.ps1)
comprova recusa **antes** de ler configuração inexistente ou acessar certificado;
também comprova recusa do ciclo de instalação sem autorização. Sintaxe foi validada
em PowerShell Windows. A execução completa do callback Inno, propriedades reais do
uninstaller assinado e integração CA continuam **aguardando validação autorizada**.
Não é uma declaração de pipeline criptográfico já homologado.

### Preparação do mantenedor, depois das aprovações

- Construir payload bloqueado, launcher e metadados na revisão autorizada; executar
  probes e plano nativo; revisar entradas de direitos/atribuição e armazenamento
  dos materiais LGPL. Não preencher aprovações apenas para obter gate verde.
- Em runner de assinatura protegido, usar o plano nativo aprovado e helper existente;
  atualizar manifestação pela transição verificada e guardar o gate resultante.
- Preencher configuração fora do repositório público: hashes reais, `native_payload`
  exatamente `dist/AgroLines`, compilador e diretório temporário novo, escopo de
  saídas próprias dentro do build isolado, evidências jurídicas/operacionais e
  aprovações específicas. Chaves ficam no hardware/serviço, não no JSON/aplicativo.
- Somente após autorização expressa e validação do ambiente protegido, invocar o
  build assinado. Arquivar logs e hashes; falha interrompe o candidato, sem fallback.
- Rodar a [homologação física](installer-homologation.md). Assinatura válida é
  necessária à estratégia conservadora adotada, mas não garante reputação,
  inexistência de malware ou aceitação SAC/SmartScreen/Defender.

## Provedores: fatos, preço e elegibilidade

Consulta oficial nesta sessão registrada com URLs, status e hashes em
[evidence/signing-sources.json](evidence/signing-sources.json). Reutilizar também
[CABF e requisitos já documentados](../windows-signing/opcoes-e-custos.md).
Preços comerciais atuais não puderam ser confirmados pelo proxy; **não existe
cotação comprovada para este titular**. Não chamar estimativa genérica de oferta.

| Opção real a avaliar | Pessoa física no Brasil | Custo / validade | Token, nuvem e GitHub Actions |
| --- | --- | --- | --- |
| [SSL.com Code Signing](https://www.ssl.com/certificates/code-signing/) / [validação individual](https://www.ssl.com/faqs/individual-code-signing-and-document-signing-certificate-validation-requirements/) | Solicitar confirmação territorial/modalidade Individual; páginas bloquearam com 403 | Emissão/renovação, token/frete ou eSigner/quotas/impostos a cotar; validade exata da oferta pendente | [Integração oficial eSigner](https://github.com/SSLcom/esigner-codesign) consultada; pede credenciais/MFA/credential ID. Não instalada. O adaptador protegido preparado é CSP/KSP; eSigner exige integração própria se escolhido. |
| [Certum / SimplySign](https://shop.certum.eu/code-signing-certificates.html) | Não demonstrada emissão para residente brasileiro nesta consulta | Certificado + serviço/token + renovação a cotar; página 403 | Confirmar suporte real a PE/PYD, CI não interativo, limites e middleware Windows. Não assumir compatibilidade porque existe app de assinatura. |
| [DigiCert Code Signing](https://www.digicert.com/signing/code-signing-certificates) | Modalidade Individual/Brasil a confirmar, não presumir OV empresarial | Certificado + Software Trust Manager/HSM e operações a cotar; página 403 | CSP/KSP/SignTool documentado no dossiê anterior; potencialmente aproveita interface existente. Action antiga descontinuada não adotada. |
| [GlobalSign](https://www.globalsign.com/en/code-signing-certificate) | Perfil/nome legal/tipo de cliente a confirmar; não presumir elegibilidade | Cotação e termos pendentes; página 403 | Token ou serviço compatível com CSP/KSP a confirmar, sem instalação aqui. |
| [Microsoft Artifact Signing Public Trust](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart) | Quickstart consultado: indivíduos EUA/Canadá. **Brasil Individual não é opção elegível demonstrada** | Mensalidade não resolve inelegibilidade; não contratar sob endereço/empresa fictícios | Serviço de nuvem/CI. Private Trust/teste não substitui confiança pública. |
| Microsoft Store MSIX | Identidade já reservada; certificação/direitos permanecem | Microsoft assina no fluxo Store; conta/termos aplicáveis a conferir | Canal alternativo futuro; não elimina LGPL nem prova os PE/SAC. Não necessário ao instalador standalone. |

O CABF admite certificados Individual, mas isso não obriga uma CA a aceitar todos
os países/clientes. CSBR vigente consultado no dossiê limita certificados novos a
**460 dias desde 01/03/2026** e exige proteção de chave conforme categoria/serviço;
confirmar atestados e validade real da oferta. Token genérico ou e-CPF ICP-Brasil
não equivalem automaticamente a certificado Authenticode público aceito no Windows.

**Recomendação econômica objetiva:** não comprar Qt Commercial nem assinatura
Store para resolver este canal. Solicitar duas cotações comparáveis: certificado
público **Individual Brasil + token/HSM** e serviço cloud compatível com assinatura
PE/PYD. Para poucos lançamentos, começar com lote manual em máquina de assinatura
protegida pode evitar custo fixo/complexidade de automação cloud; escolher o menor
custo total **somente depois de confirmar elegibilidade e preços**. Não é possível
nomear honestamente o provedor mais barato sem essas respostas. Para empresa futura,
comparar OV com identidade jurídica verdadeira; constituição não foi pressuposta.

Comparação de custo total: certificado/renovação + token/frete/middleware **ou**
mensalidade/operações cloud + timestamp + impostos/câmbio + armazenamento de
proveniência + manutenção do runner/MFA. Orçar até 81 operações iniciais e quatro
papéis próprios por lançamento somente se a reutilização verificável de vendors
for aprovada/implementada. Não transferir código próprio para orçamento.

### Mensagem curta para cotação — preparada, não enviada

> We need public-trust Authenticode code signing for a proprietary offline Windows
> desktop application, owned by an individual legally resident in Brazil. Please
> confirm eligibility, exact legal identity requirements, supported EXE/DLL/PYD
> signing and permission to sign lawfully redistributed unsigned third-party
> binaries while retaining upstream attribution. Quote certificate/renewal,
> token/HSM delivery to Brazil or cloud service, quotas/per-signature costs,
> RFC3161 HTTPS timestamps, CSP/KSP/SignTool integration, approved non-interactive
> Windows CI authentication, revocation/recovery and all additional charges.
> Initial conservative scope is 81 new signatures, preserving 100 valid upstream
> signatures. We are not requesting issuance or providing credentials/source code.

Assinar não corrige procedência, licença, fonte faltante ou vulnerabilidade. O
[SAC oficial](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/code-signing-for-smart-app-control)
considera confiança/avaliação do arquivo; política real só se comprova na máquina
Windows 11 apropriada. Nenhum bypass de proteção integra o plano.
