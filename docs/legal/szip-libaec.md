# Correção pontual de SZIP: libaec BSD no mesmo slot de ABI

## Problema comprovado

O [COPYING original SZIP 2.1.1](records/original-SZIP-COPYING.txt), extraído do
arquivo oficial `https://support.hdfgroup.org/ftp/lib-external/szip/2.1.1/src/szip-2.1.1.tar.gz`,
SHA-256 `21ee958b4f2d4be2c9cabfa5e1a94877043609ce86fde5f286f105f7ff84d412`,
distingue decompression em HDF e compressão para uso científico não comercial.
Não se presumiu que a licença do HDF5 autorize irrestritamente o encoder SZIP.

DLL original: `_internal/fiona.libs/szip-d0425ee11b05cea2ef5907b56ab33522.dll`,
SHA-256 `aaff372f56a8221f198522cca5a5494109b3151613620c13aabdddbcedfdd876`.
[Inspeção estática](records/original-szip-static-inspection.json) do export
`SZ_encoder_enabled` mostra retorno do valor inicial **1**. Não executa código
nativo e não demonstra que o AgroLines tenha usado compressão. Demonstra que não
podemos tratar esse binário como um build apenas decoder sem nova evidência.

## Solução implementada

libaec **1.1.7 BSD-2-Clause**, projeto oficial
[Deutsches-Klimarechenzentrum/libaec](https://github.com/Deutsches-Klimarechenzentrum/libaec),
commit `0c4c01463d2c64a112a61271d317b74efb660608`, arquivo-fonte SHA-256
`33d1207ee309154331b58715cef998d65b86bd8421fa5418254c16e18ccb3da8`.
Licença e autores originais incorporados. A licença permissiva não obriga entregar
código proprietário; seus avisos permanecem. Isso não é laudo universal de patentes.

`distribution/windows/standalone/Build-Libaec.ps1` compila com MSVC x64/CMake/Ninja e executa
os testes upstream. O target compartilhado `sz-shared` inclui os objetos AEC;
não é necessário adicionar outra DLL codec. A única adição no CMake é OUTPUT_NAME
para conservar o **basename importado por HDF5**, inclusive o sufixo antigo.
O nome não é alegação de conteúdo original: manifesto, licença e origem registram
**libaec**, seu hash e a substituição.

`distribution/libaec_build.py` exige a fonte fixa, hash do original, exports
usados por imports regulares e delay-load de todos os consumidores, x64 e evidência
do build. A política nativa derivada permite apenas essa mudança; não autoriza
assinatura comercial ou novos binários desconhecidos. Nenhum gate é desabilitado.

Novo DLL no build [38759477055](https://github.com/fbdelatorre/AgroLines/actions/runs/38759477055):
SHA-256 `6a03aef4acd2d846bbfd8e79c035cc9ffab61ff29c333657d76cc8cae3bf7c3a`,
33.792 bytes. O hash é específico desse build, não promessa de determinismo MSVC.
O HDF5 consumidor permanece byte a byte, SHA-256
`b1eef1c184173d1f8dfd17232a842cd5399540e7cef9c7a315fbf58c16fe6ead`.

## Provas

- **6/6 ctests** upstream aprovados.
- `tools/legal-native/hdf5_probe.py` cria dados sintéticos u8/u16/u32/f64,
  2.048 valores por caso, opções EC=4/NN=32; **8/8** comprimem e recuperam bytes
  idênticos com o novo codec.
- Outra cópia/processo usa HDF5/SZIP original **somente para ler** esses arquivos:
  **8/8** com bytes idênticos. Não executa o encoder antigo.
- `GetModuleHandleW`/`GetModuleFileNameW` e hashes conferem DLLs realmente carregadas.
- O aplicativo congelado completo passa pelos probes GIS/offline/22 referências.
- [Resultados e caminhos carregados](records/windows-build-results.json).

O build oficial anterior, MSIX e artefatos #18/#19 não foram substituídos.
A alteração só integra o **novo candidato standalone 1.0.0.2**. Nenhum código do
motor, formato GIS, interface ou tolerância foi alterado. Não se instala o candidato.

**U04.SZIP: RESOLVIDO** no novo payload: o encoder restritivo foi removido e sua
substituição BSD testada, com avisos/receita/origem entregues. Isso não encerra
outros vendors de U04, não valida toda a licença HDF5, assinatura/SAC ou obrigações
de redistribuição do MSVC usado na nova DLL. Estas continuam delimitadas no dossiê.
