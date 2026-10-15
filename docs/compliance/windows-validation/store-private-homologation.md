# Roteiro futuro — homologação privada legítima da Store

**Preparado; nenhuma ação realizada na conta.** Certificação, publicação privada,
convites e coleta em computador real dependem de autorizações distintas. O MSIX
`e6a2…` é diagnóstico, não aprovado para envio/instalação. Não há pacote confiável
novo nesta fase. Não confundir roteiro pronto com produto pronto para submissão.

## Requisitos oficiais conferidos e evidências

Fontes Microsoft consultadas em 15/10/2026, com hash/status em official-research.json:

| Tema | Documento oficial e consequência |
| --- | --- |
| MSIX desktop/Win32 e integridade | [Behind the scenes](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes): instalação protegida, virtualização e integridade. Manifesto não comprova sozinho preservação em atualização/desinstalação. |
| Pacotes | [Upload packages](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/upload-app-packages): atender validação de identidade, arquitetura e versão no fluxo MSIX. |
| Assinatura | [Code signing options](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options) e [certificação](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/app-certification-process): Store assina MSIX/AppX; pode-se fornecer MSIX sem assinatura própria nesse fluxo, sem inferir confiança de cada PE/SAC. Não é necessário comprar certificado apenas para o envelope Store. |
| Capabilities/Full Trust | [Declarations](https://learn.microsoft.com/en-us/windows/uwp/packaging/app-capability-declarations) e [submission options](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/manage-submission-options): justificar capacidades restritas e obter aprovação aplicável. |
| Privacidade/direitos/conta | [Store policies](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies): §10.5.1 URL de privacidade e deveres aplicáveis Win32/Desktop Bridge; §10.5.4 segurança/criptografia para dados pessoais; §11.2 direitos de terceiros; §10.14 tipo de conta e apresentação como negócio. Revisão permanece necessária. |
| Audiência | [Visibility](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/visibility-options): Private audience com contas Microsoft pessoais do grupo; ocultação/link direto sozinho não substitui audiência privada. Mudança para público tem limitações de reversão. |
| Controle de publicação | [Submission options](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/manage-submission-options): padrão é publicação após certificação; selecionar explicitamente **Don't publish this submission until I select Publish now**. |
| Contrato | [App Developer Agreement — link oficial nas políticas](https://go.microsoft.com/fwlink/?linkid=528905): acesso 403 neste ambiente; conteúdo/versão aceitos na conta não verificados. Não inventar cláusulas. |

## Pré-requisitos e pontos de parada

1. Revisão jurídica Qt/LGPL3, GEOS/LGPL2.1, fontes/avisos/EULA e direitos dos
   fornecedores; resolver ou delimitar documentadamente U01–U08. Assinatura Microsoft
   não resolve obrigações de terceiros. Não criar uma oferta de fonte incompleta.
2. Revisar `docs/privacy/offline/`: bases legais e mecanismos de transferência,
   data efetiva e URL HTTPS pública ainda não aprovadas. Suporte Gmail pessoal ainda
   planejado; configurar controles/retentividade antes de começar. Programa 18+,
   aceite verificável, sem documentos de identidade. Não alterar classificação
   Brasil Livre/IARC 3+/Microsoft 3+, nem audiência/grupo.
3. Esclarecer com Microsoft a conta **Individual no Brasil**, nome reservado
   `Delatorre COrporation`, §10.14, condições/EULA e `unvirtualizedResources`.
   Não mudar identidade/inscrição por conta própria.
4. Depois das decisões, produzir somente se necessário um novo candidato autorizado,
   com inventário/notices/licenças/fontes e novo SHA. Não usar o MSIX de referência
   como se estes bloqueios estivessem resolvidos. Guardar SHA e origem da execução.
5. Validar pacote sem instalar unsigned: manifesto/MakeAppx/estrutura, todas as
   dependências locais, offline-only, código nativo e bundle de avisos. Executar
   WACK nas condições suportadas, sem instalar candidato não confiável ou reduzir
   proteções. Resultado WACK continua pendente, não inferir de CI.

## Passos do proprietário no Partner Center — somente após autorização

1. Abrir **Apps and games → AgroLines → submissão MSIX**. Confirmar produto
   Store ID `9NRDJ3ZTM978`, sem criar outro aplicativo ou alterar licenciamento.
2. Em **Pricing and availability / Audience / Visibility**, conferir **Private
   audience** e `AgroLines - Testadores Internos`. Conferir que os membros e contas
   corretos já autorizados se enquadram no programa 18+. Não inserir convites nesta
   tarefa. Um link oculto de audiência pública não protege acesso. A audiência da
   Store não torna privados repositório, URLs de artefatos ou cópias externas.
3. Em **Submission options → Publishing hold options**, escolher **Don't publish
   this submission until I select Publish now**. Registrar evidência dessa opção
   antes de qualquer botão de envio. Não confiar no padrão ou só em uma data futura.
4. Em **Packages**, carregar **somente o candidato futuro expressamente autorizado**.
   Conferir Name `DelatorreCOrporation.AgroLines`, Publisher
   `CN=43189595-B928-4D57-90A4-24300E4D4976`, PFN
   `DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg`, x64, Windows.Desktop
   mínimo `10.0.22000.0`. A referência é versão `1.0.0.0`, máximo testado
   `10.0.26100.0` (não é teto garantido de suporte). Conferir a versão maior que
   pacotes já aceitos na conta; não presumir que não existam submissões anteriores.
5. Em **Notes for certification**, explicar: offline-only, sem conta remota, banco
   SQLite local, GIS/Qt WebEngine/Leaflet locais, etapas com dados sintéticos, sem
   serviços de autenticação/PG. Justificar `runFullTrust` (Win32 e auxiliares Qt)
   e `unvirtualizedResources` (exclusão estreita `%LOCALAPPDATA%/AgroLines` para
   dados duráveis; não acesso irrestrito a toda AppData). Avisar limites de teste.
6. Revisar política HTTPS **aprovada e sem campos pendentes**, direitos de terceiros,
   termos, acessibilidade/metadados, segurança e listagem precisa. Parar se houver
   bloqueios ou se a interface não oferecer retenção manual de publicação.
7. **Somente com autorização específica de envio**, selecionar **Submit to the
   Store**. Acompanhar relatório de certificação; corrigir reprovações em nova
   versão rastreável, sem trocar proteções do Windows.
8. Aprovação de certificação com hold **não instala nem publica**. Para obter a cópia
   legitimamente entregue pela Store, exigir nova autorização do proprietário para
   **publicação privada**; então **Publish now**, mantendo audiência privada.
   Não prometer download instalável da Store antes dessa etapa. Não extrair chaves,
   reaproveitar assinatura, instalar MSIX extraído/unsigned ou usar certificados de teste.
9. Conta autorizada do grupo: instalar pela Store em **Windows 11 físico limpo**,
   com SAC On e Defender ativos, sem Python/PostgreSQL de usuário. Registrar origem,
   versão e SignatureKind Store. Aplicar o roteiro SAC adjacente. Instalação pela
   Store requer conectividade; operação agrícola posterior deve funcionar com
   internet fisicamente desconectada.
10. Testar inicialização, imports dos cinco formatos, edição numérica, undo/redo,
    histórico, backup/restauração e reabertura. Para atualização, é necessário outro
    pacote legítimo de versão superior. Com dados exclusivamente sintéticos e backup,
    testar atualização e desinstalação/reinstalação, comparar hashes/revisões/precisão
    dos projetos em pasta durável. São ações futuras deliberadas, não executadas pelo
    coletor. Recusar aprovação se houver perdas, bloqueios ou evidências inconclusivas.

**Recomendação técnica adicional:** separar o recebimento Store com internet da
sessão física offline; registrar janela de tempo, máquina e pacote. Segurança de
projetos locais com possíveis dados pessoais, termos contratuais e integridade dos
materiais LGPL precisam de decisões reais, não apenas de um manifesto válido.
