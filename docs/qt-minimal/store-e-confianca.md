# Rota Store e confiança — documentação oficial consultada em 14/10/2026

As URLs, resultados HTTP e hashes das páginas consultadas ficam em `fontes.json`.

- [Opções de assinatura](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options): MSIX pela Store é reassinado pela Microsoft após certificação, sem compra/gestão de certificado pelo desenvolvedor. O fluxo MSI/EXE da Store é diferente e exige assinatura do instalador pelo editor. A geração local sem assinatura é entrada técnica possível para o fluxo MSIX, sujeita às validações do Partner Center; não permite instalar/distribuir o candidato agora.
- [Assinatura MSIX](https://learn.microsoft.com/en-us/windows/msix/package/signing-package-overview): instalação exige pacote assinado e confiável; integridade do envelope/BlockMap não implica assinatura Authenticode individual de DLL/PYD.
- [Visibilidade MSIX](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/visibility-options): Private audience permite a primeira distribuição a grupos conhecidos sem listagem pública. Contas Microsoft pessoais são exigidas para aquisição; conta trabalho/escola não equivale. Após submeter como Public audience não se pode voltar a Private audience. Link direto com audiência pública não substitui audiência privada. Reconfirmar configuração relatada no Partner Center, sem alterá-la automaticamente.
- [Package flights](https://learn.microsoft.com/en-us/windows/apps/publish/package-flights): também passam por certificação; são outra ferramenta, não dispensa universal de revisão. Podem publicar automaticamente após certificação se opções não forem ajustadas. Para a primeira fase, conferir Private audience + publicação manual; não criar flights nesta tarefa.
- [Visão geral MSIX](https://learn.microsoft.com/en-us/windows/msix/overview): footprint files adicionais existem quando a feature correspondente é usada; `AppxMetadata/CodeIntegrity.cat` contém metadados de integridade de código. Não inferir que MakeAppx cria catálogo de confiança em todo pacote, nem criar um artificial para aprovar os unsigned. Verificar presença, assinatura e associação de **cada hash** no pacote entregue.
- [Desktop Win32 empacotado](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-root): MSIX preserva aplicação desktop e agrega identidade; não converte automaticamente o runtime em UWP nem elimina requisitos nativos/capabilities.
- [SAC](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/code-signing-for-smart-app-control): separar reputação/assinatura admitida, confiança do pacote e execução real. Preservar SAC/Defender. Não transformar ausência de assinatura embutida em aprovação pelo catálogo, nem tratar presença de catálogo como garantia SAC.

Inspeção somente leitura já preparada:
`distribution/windows/signing/Test-StoreDeliveredTrust.ps1 -OutputDirectory <pasta-nova>`.
Requer pacote oficial instalado pela Store e SDK SignTool confiável na bancada
de inspeção; cliente final não precisa de SDK/PowerShell. Registra SignatureKind,
PFN, SHA por PE, verificação embutida, verificação explícita `/c` quando catálogo
real estiver presente, e estado SAC/Defender; nunca instala catálogo/certificado.
O resultado continua `sac_approved=false` até avaliação funcional física.

CI comprova build, assinatura upstream no runner, integridade, importação e
operação do EXE extraído sob ambiente limitado. Não comprova identidade instalada,
reputação SAC, funcionamento sem todos os runtimes da imagem Windows, atualização
ou desinstalação reais. Probes com PATH limpo não substituem máquina limpa.

Não é necessário comprar certificado agora para a assinatura de envelope MSIX
pela Store. Se o pacote Store real apresentar bloqueios de PE, coletar eventos e
verificações por arquivo antes de decidir assinatura própria. Direitos de
redistribuir/assinar terceiros, CA pública para pessoa física residente no Brasil,
chave em hardware/serviço, timestamp e configuração protegida continuam pré-requisitos
se essa rota se tornar necessária. Nenhuma contratação realizada.
