# U07 — NumPy / OpenBLAS / LAPACK / GCC runtime: draft, NOT SENT

Canal: https://github.com/numpy/numpy/issues
Projeto oficial consultado: https://github.com/numpy/numpy
Canal público = não postar sem autorização. Para Qt, bug tracker é indicado nos arquivos oficiais versionados; acesso/criação pode exigir conta e não foi executado. Para Microsoft, abrir **Help + support** no Partner Center autenticado; categoria e elegibilidade exigem verificação na conta. Nenhuma conversa de suporte ou condição contratual foi presumida.

## Message ready for owner review

Subject: Exact Windows binary source, build and redistribution materials — AgroLines compliance case U07

Hello maintainers/support,

We are preparing an offline Windows x64 proprietary desktop application for a future private Microsoft Store test. We wish to meet the actual third-party redistribution obligations without exposing application source. This is a request for technical distribution materials, not a request for a legal opinion.

The attached `numpy-attachment.json` lists exact distributed paths, SHA-256 hashes, wheel origins/versions and existing license evidence. Candidate reference SHA-256: `e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b`. The unsigned diagnostic MSIX will NOT be attached, installed or submitted.

Requested material: Resolve OpenBLAS build identifier 0.3.34.106.0 to exact upstream commit/patches, bundled LAPACK version and build recipe; identify static GCC runtime components and eligible compilation-process evidence for GCC Runtime Library Exception 3.1. The full bundled wheel license is already retained.

Could you provide version-specific source archives/commits, submodule revisions, all relevant patches, build/packaging scripts, configuration flags and required notices, and explain which exact binary hashes/build IDs they correspond to? If material is already publicly available, please provide immutable artifact URLs and integrity checks. Please identify any source not included in the archive, prerequisites to obtain it, and any redistribution restrictions on supplied materials. If you do not maintain these builds, please identify the official build maintainer.

We do not assume that a same-version upstream tag proves binary correspondence. Please distinguish confirmed build records from reconstructed suggestions. We do not request private keys, customer data or proprietary third-party source beyond rights actually provided by applicable licenses.

Thank you.

## Anexos seguros e encerramento

Enviar somente o JSON adjacente, e trechos SPDX/versões públicos estritamente necessários. Não anexar MSIX/EXE, dumps, logs de ambiente completo, código AgroLines, projetos, segredos ou dados de testadores.

Resposta esperada: (1) identificação de build/hashes; (2) fontes/submódulos completos por componente; (3) patches/receitas/flags e toolchain; (4) licenças/avisos e escolha de alternativas aplicáveis; (5) termos de redistribuição desses materiais; (6) lacunas explicitadas.

Critério técnico de encerramento: validar material obtido contra os bytes/identificadores anexos, arquivar hashes e receitas, demonstrar aplicação dos patches e conferir cobertura dos avisos. Uma resposta genérica ou coincidência nominal de versão não encerra a pendência. Direitos e interpretação jurídica continuam sujeitos a revisão profissional. Para U08, encerrar somente as questões efetivamente respondidas com documentos aplicáveis à conta; suporte técnico não substitui parecer jurídico.
