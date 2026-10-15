# U02 — delta mínimo após identificar o snapshot público `.225`

Minuta, não enviada. Usar apenas se os materiais públicos e os registros de release
não fecharem a associação ao wheel e os avisos dos targets. Não solicita licença
comercial, autorização para BSD/MIT ou parecer jurídico do mantenedor.

Canal indicado pelo próprio wheel: [tracker Qt for Python/PYSIDE](https://qt-project.atlassian.net/browse/PYSIDE).
Submissão pode exigir conta. Não abrir issue nem enviar anexos automaticamente.

> Subject: Source release mapping and target notices for PySide6-WebEngine 6.12.0.140 Windows x64
>
> We are documenting third-party redistribution for a proprietary Windows application.
> The official PyPI input is pyside6_webengine-6.12.0.140-cp310-abi3-win_amd64.whl,
> SHA256 f9b61b1d457a591ee590a6b80515f25a3e61e2576a2a0a70566380f9d9de4ab0.
> Qt6WebEngineCore.dll SHA256 is 54488cfc8fea4057377302cec5a1fb1100fb4bc4231cd7e60f43e4fcff28e89e.
> Its exported values are QtWebEngine 6.140.0, Chromium 140.0.7339.225,
> security patch level 152.0.7977.83.
>
> We found the public v6.140.0-rc source release, module commit
> d505fc23640d2bd6345e6483eb73daf4e19f5829, Chromium gitlink
> 39352427a3245a19fb395547b3aa38be9d091ec4. The effective chrome/VERSION is .225,
> despite the module summary listing .264. We are not asking for these public sources again.
>
> 1. Can you confirm whether that source release corresponds to this Windows wheel,
> and identify any downstream modifications or build inputs needed in addition to
> the published archive? If it differs, please identify the actual revisions/release
> materials. An official build/release record is sufficient; byte-for-byte binary
> reproducibility or a general commercial-use permission is not requested.
> 2. Where are the generated attribution/license records for the shipped
> QtWebEngineCore and QtPdf targets, including enabled codecs and applicable static
> dependencies? Please provide the actual generated notices or equivalent coverage
> information needed to assemble the required notices and corresponding-source materials.
>
> No application source, installer, customer data, credentials or private keys are attached.

Anexo suficiente: nome/hash do wheel, hash do DLL, os três literais e referências
imutáveis acima. Não enviar fontes AgroLines, projetos, dumps ou pacote executável.

Encerramento documental: conferir resposta com o hash do input, identificar fontes
e alterações aplicáveis e obter cobertura demonstrável dos avisos necessários.
A suficiência da modalidade LGPL/EULA/instalação continua questão delimitada de
revisão profissional; uma resposta técnica não é parecer jurídico global.
