# Saneamento material da distribuição standalone — PR #20

Atualização posterior, sem substituir este histórico: [correções e licenciamento no PR #21](commercial/README.md).

Evidências de 15/10/2026. [PR #20](https://github.com/fbdelatorre/AgroLines/pull/20),
dependente do [#19](https://github.com/fbdelatorre/AgroLines/pull/19).
Este documento registra entregas executadas. **Não autoriza distribuição comercial,
não aprova contratos e não comprova SAC.** Os relatórios #14–#19 permanecem históricos.

## O que foi efetivamente entregue

- [EULA completa em português](standalone/EULA.md), com opções comerciais não
  inventadas, direitos do consumidor e exceções expressas para modificação,
  substituição e engenharia reversa necessária às bibliotecas LGPL.
- [Política standalone](standalone/politica-privacidade.md), em Markdown, HTML
  estático e texto UTF-8: tratamento local comprovado separado do futuro suporte
  Gmail pessoal, sem telemetria, servidor, criptografia ou retenção automática fictícios.
- [Instruções LGPL](standalone/INSTRUCOES-LGPL.md) e [leitura inicial](standalone/LEIA-ME.md).
  Reutilizam as demonstrações #18/#19; não estendem Qt Core a todo o Qt/WebEngine.
- **57 materiais suplementares originais**: 26 textos/avisos e 31 receitas/patches,
  com [origem, versão e SHA-256](../../distribution/legal/supplemental/materials.json).
  Incluem libiconv 1.17, FreeXL 2.0.0, SpatiaLite 5.1.0, GEOS 3.14.1,
  libaec 1.1.7, attrs 26.1.0, OpenBLAS/LAPACK/GCC, JPEG 3.0.3/3.1.4.1,
  TIFF 4.6.0/4.7.1, zlib e condições Microsoft efetivamente encontradas.
  Os textos originais não foram substituídos por traduções.
- **SZIP restritivo substituído pontualmente por libaec BSD**, sem reescrever o GIS,
  remover funcionalidade ou alterar algoritmo agrícola. [Descrição e hashes](szip-libaec.md).
- `distribution/legal_materials.py` monta **153 documentos registrados** no payload
  real, mais `legal-manifest.json` e `THIRD_PARTY_NOTICES.txt`. Associa todos os
  **178 PE** aos componentes, versões e hashes; preserva licenças já auditadas.
  O aviso IJG requerido foi incluído literalmente no índice em português.
- Inno inclui `legal/` na pasta **da versão**, mostra aviso explícito de minuta
  e cria atalho para os avisos. Há verificação antes e depois da compilação e log
  de inclusão dos documentos críticos. Isso comprova entrada no pacote compilado;
  não é extração independente nem ensaio de instalação/atualização/desinstalação.

As minutas são identificadas como não adotadas. A tela `InfoBeforeFile` não é
aceite contratual. Não foi implementada ativação, cadastro, coleta de idade,
telemetria ou comunicação com fornecedores. O manifesto não declara que todos os
avisos vendorizados estão completos: conserva a lista específica ainda faltante.

## Resultado dos sete casos solicitados

Unidade de contagem: **pacotes de trabalho originais**, não número de bibliotecas,
arquivos ou frases. U03 já estava encerrado e não voltou à contagem.

| ID | Componente | Problema original | Solução aplicada / evidência | Estado |
| --- | --- | --- | --- | --- |
| U01 | Qt Base/PySide6/Shiboken 6.12.0 e transitivos | Mapeamento exato wheel–fontes/build e avisos estáticos | Textos e provas #18/#19 preservados; instruções/EULA entregues. Faltam configurações/patches e atribuições precisas dos targets restantes; [pedido restrito](supplier-delta.md#u01--qtpyside6shiboken). | **DEPENDE DE TERCEIRO** |
| U02 | WebEngine/PDF 6.12.0.140, runtime 6.140.0, Chromium 140.0.7339.225 | Gitlinks/patches/GN/codecs e créditos dos targets distribuídos | Não usamos a fonte candidata Chromium 140.0.7339.264 como se fosse exata. Busca adicional em recursos não encontrou créditos completos demonstráveis; [pedido específico](supplier-delta.md#u02--qt-webenginechromiumpdfium). | **DEPENDE DE TERCEIRO** |
| U04 | Fiona 1.10.1/GDAL 3.9.1 e vendors | Fontes/receitas/avisos e restrição SZIP | Fontes oficiais libiconv/FreeXL/SpatiaLite conferidas contra SHA-512 vcpkg; avisos/receitas incorporados; SZIP substituído por BSD e testado. Falta mapa estático/drivers e correspondência restante do wheel, inclusive GEOS Fiona; [delta](supplier-delta.md#u04--fionavendors). GCP/RTTOPO permanecem comprovadamente desabilitados. | **DEPENDE DE TERCEIRO** |
| U05 | Shapely 2.2.0/GEOS 3.14.1 | Obter fonte, receita Windows/patches/CRT/delvewheel e avisos | Fonte oficial, LGPL/AUTHORS e receita do commit de publicação verificado incorporados; MSVC 14.44, GEOS 3.14.1, shared/Ninja/Release e reparo delvewheel identificados. [Escopo de encerramento](#u05-escopo-exato-do-encerramento). | **RESOLVIDO** |
| U06 | pyproj 3.8.0/PROJ 9.8.1 e bases | Atribuições de dados e componentes incorporados | Avisos JPEG 3.1.4.1, TIFF 4.7.1 e zlib 1.3.1 agora associados aos componentes reais. Falta confirmação delimitada de build/BOM e direitos das bases efetivamente empacotadas; [pedido](supplier-delta.md#u06--pyprojprojdados). | **DEPENDE DE TERCEIRO** |
| U07 | NumPy 2.5.4/OpenBLAS/LAPACK/GCC | Identificador de build e GCC Runtime Library Exception | Identificador resolvido por igualdade do DLL com scipy-openblas64; commit/patches/receitas e textos reunidos; três publicações PyPI verificadas criptograficamente. Resta aplicar a exceção ao processo GCC concreto, [questão J03](decisoes-e-revisao.md). | **REVISÃO JURÍDICA** |
| U08 | Microsoft/MSVC/UCRT | Contrato Store e direitos de redistribuição | Store removida dos requisitos deste canal; condições CPython/Shapely reais entregues. Falta avaliar alcance da licença de ferramentas/CRT, inclusive launcher estático, [questão J04](decisoes-e-revisao.md). | **REVISÃO JURÍDICA** |

**Contagem: 7 originais; 1 RESOLVIDO; 4 DEPENDE DE TERCEIRO; 2 REVISÃO JURÍDICA;
0 DEPENDE DO TITULAR e 0 BLOQUEADO nesses sete casos.** As decisões comerciais
do titular e os gates globais de distribuição estão separados abaixo; não foram
escondidos na contagem nem multiplicados como novas pendências originais.

### U05: escopo exato do encerramento

Encerra-se o pedido **documental ao fornecedor de Shapely**: os materiais antes
solicitados genericamente estão disponíveis e foram obtidos. A
[verificação oficial PyPI](records/publication-verification.json) liga o wheel
SHA-256 `90895df6542ae039fc6557dec6194e3509e883fbd6f5788e3c3e7a38fe46b257`
à publicação `shapely/shapely`, commit
`229c71f7128713b37201f3c77336d32b52467454`. As receitas desse commit estão no
suplemento; `ci/install_geos.cmd` usa a release oficial 3.14.1, sem etapa de patch
do algoritmo. O arquivo de fontes e seus textos estão no artefato de fontes.
A receita identifica o toolset e o reparo, não fixa necessariamente toda ferramenta
auxiliar e não comprova que o cache upstream seja reconstruível byte a byte.

Isso **não encerra** a avaliação global LGPLv2.1 §6, a modalidade de entrega de
fontes, a suficiência de instalação/substituição no Windows protegido ou a EULA.
Não se afirma reconstrução binária exata. O campo conservador
`source_binary_correspondence=false` da coleta dos arquivos-fonte permanece:
baixar um tarball e verificar publicação não é reproduzir a DLL. Não se criou
nova obrigação de reproducibilidade bit a bit como condição genérica da LGPL.

## Fontes, receitas e procedência

[Resultado dos arquivos oficiais](records/official-source-results.json) registra
URLs completas, membros extraídos, hashes dos textos e dos arquivos-fonte.
libiconv 1.17, FreeXL 2.0.0 e SpatiaLite 5.1.0 conferem com os inputs SHA-512
do vcpkg `1de2026f28ead93ff1773e6e680387643e914ea1` declarado pelo build Fiona.
Isso comprova inputs declarados, não toda a BOM estática ou ausência universal
de patches. FreeXL/SpatiaLite preservam as alternativas MPL 1.1/LGPL 2.1+/GPL 2+;
a eleição e a aplicação ao build devem ser revisadas. O GPL do utilitário GNU
iconv não foi atribuído indiscriminadamente à DLL libiconv LGPL.

O DLL OpenBLAS do NumPy é byte a byte o do pacote scipy-openblas64
0.3.34.106.0: SHA-256
`ed4f167a5330424524f45258e7ca2c8d7f03c0cba1f30ee4985553ac1f88ecf8`.
A publicação verificada aponta ao wrapper
`78fc0eaf6de71d92fd98f74f7e5bfa356a2f83e3`, submódulo OpenBLAS
`446c436e10450c348169808f1a6b3fae0925c9f7`. Licenças LAPACK/OpenBLAS/GCC e
patches/receitas Windows estão preservados. O script upstream usa `-static-libgcc`
e rejeita `libquadmath.a` no mapa; não se inventa um mapa original não obtido nem
se transforma essa guarda em decisão jurídica sobre a exceção GCC.

Não foi obtida documentação exata suficiente para todos os vendors Qt/Chromium,
Fiona e dados PROJ. Portanto **não é afirmado que todos os textos obrigatórios já
foram reunidos**. Identificar os 178 PE não equivale a identificar cada componente
estático. Não há nova família Qt GPL/comercial introduzida; isso não é certificado
de ausência universal de código incompatível nos vendors ainda incompletos.

Os arquivos de fontes baixados são exclusivamente de terceiros. Estão disponíveis
no artefato de pesquisa abaixo, com expiração; **isso ainda não é modalidade
durável de entrega de fontes aprovada para clientes**. Não foi publicada oferta
escrita irrevogável nem código próprio. O arquivo-fonte SZIP restritivo não está
no artefato atual; conserva-se apenas seu texto legal e a inspeção estática.
Um artefato novo de pesquisa que inicialmente o incluía foi removido quando a
restrição foi constatada; nenhum artefato original #14–#19 foi removido.

## Evidências e download

| Evidência | Execução / artefato | Conteúdo e limite |
| --- | --- | --- |
| Runtime e Inno standalone | [38759477055](https://github.com/fbdelatorre/AgroLines/actions/runs/38759477055) / [11984893921](https://github.com/fbdelatorre/AgroLines/actions/runs/38759477055/artifacts/11984893921) | `agrolines-standalone-HOMOLOGATION-EVIDENCE-ONLY`: inclui `packaged-legal/`, manifesto, notas/receitas, provas e log Inno; não contém instalador ou runtime executável. Digest Actions `05e07ed1ba385177d5242f40f539163a5d7af3fceb8adaad7aae831bfdf37b61`. |
| Fontes e textos oficiais | [38758884599](https://github.com/fbdelatorre/AgroLines/actions/runs/38758884599) / [11984287835](https://github.com/fbdelatorre/AgroLines/actions/runs/38758884599/artifacts/11984287835) | `official-upstream-license-materials-REVIEW-ONLY`; digest Actions `3faf33c5385f3fb4e3d60b1bb2dc9faf15eaec7de48174b10b2a2ed614068e28`. |
| Atestações PyPI verificadas | Mesma execução / [11984302868](https://github.com/fbdelatorre/AgroLines/actions/runs/38758884599/artifacts/11984302868) | `verified-public-pypi-provenance-EVIDENCE-ONLY`; digest Actions `a909a2f194b1eb8be4876373a2979317238feaed3834c00e8c751ab0b30a921f`. Sem wheels executáveis. |
| Qualidade Windows/Linux | [38759477160](https://github.com/fbdelatorre/AgroLines/actions/runs/38759477160) | Windows **246 aprovados/2 ignorados**; Linux **247/1**; Ruff e formatação aprovados; **22/22** em ambos. |

No GitHub: abrir a execução, seção **Artifacts**, baixar o nome indicado. Pode ser
necessário login GitHub para baixar. Os digests acima são os informados pela API
Actions, [preservada](records/build-artifacts-api.json); o ZIP final não foi
independentemente baixado/medido neste ambiente devido à recusa do proxy de download.
Os JSONs de resultado foram extraídos dos logs da mesma execução, sem URLs de acesso
temporário ou credenciais. Use o manifesto de cada conjunto para conferir os arquivos.

### Identificação do diagnóstico compilado

- Head testado: `cb7c6bc7f075bbb062d3313a2b5de467022342d5`.
- Merge de teste: `bc9ac1948cc865ea2ce0c69aae4a14375d70cd49`.
- Versão **1.0.0.2 x64**, perfil `standalone-offline`.
- `AgroLines-Standalone-1.0.0.2-x64-bc9ac1948cc8-EXPERIMENTAL-UNSIGNED.exe`.
- SHA-256 **`932860894fd6ace488b89c879927458439a064c3a79265039c816e3ff0626d73`**;
  159.977.796 bytes. Manifesto do payload:
  `461460d70397633163f97ae31b06e672e60b993cbeac1b7a26d4d54ecb8ed290`.
- Compilado somente no builder autorizado. **Não assinado, não instalado,
  não oferecido para download, não autorizado para distribuição.**

[Resultados brutos](records/windows-build-results.json): 178 PE, 100 assinaturas
upstream aceitas/78 sem assinatura; nenhuma assinatura realizada. **176 PE de
terceiros preservados**, um codec substituído legitimamente por fonte BSD, mais
o EXE próprio reconstruído. O launcher próprio adicional fica fora desses 178.
É um novo candidato: não usa o hash das referências antigas.

## Testes e limites

- 6/6 testes libaec; 8 round-trips HDF5 BSD + leitura exata dos mesmos oito casos
  pela pilha original em outro processo; encoder SZIP original nunca executado.
- Janela normal observada e fechada no builder; GUI/PySide6/WebEngine auxiliar,
  Leaflet local, SHP/GPKG/KML/KMZ/GeoJSON, edição/undo/redo, SQLite, histórico,
  backup/restauração e precisão do aplicativo congelado aprovados. Pacotes Python
  PySide6/Shiboken modificados carregados em cópia isolada.
- Testes negativos de materiais verificam falta/alteração/arquivo extra, novo PE
  sem registro, alteração do código nativo e autoaprovação indevida. Campos
  Authenticode adicionados a PE originalmente sem assinatura só podem preservar
  conteúdo; essa verificação **não valida confiança criptográfica**. O gate
  SignTool separado permanece obrigatório.
- Uma execução inicial recusou corretamente um aviso alterado por conversão CRLF
  no checkout Windows. Corrigiu-se `.gitattributes`, preservando os hashes originais.
  Uma linha Ruff foi ajustada. Execuções intermediárias canceladas não contam como
  aprovação. Nenhum teste/critério foi removido ou enfraquecido.
- CI hospedado não demonstra Windows 11 físico, SAC, ciclo Inno instalado, pins,
  múltiplos usuários ou preservação após atualização/desinstalação. O roteiro
  [já preparado no #19](../commercial-standalone/installer-homologation.md)
  continua exigindo candidato legitimamente confiável e autorização.
- O workflow MSIX preexistente também foi acionado automaticamente por este PR
  ([execução](https://github.com/fbdelatorre/AgroLines/actions/runs/38759476776)).
  Não houve submissão, assinatura ou instalação. Esse diagnóstico do canal Store
  não recebe a correção libaec nem os materiais standalone e **não é o candidato
  comercial deste trabalho**; não foi usado para substituir a referência histórica.

## Menor lista para liberar comercialmente

1. **DEPENDE DE TERCEIRO:** respostas delimitadas U01/U02/U04/U06 em
   [supplier-delta.md](supplier-delta.md). Nenhum contato ou issue foi enviado.
2. **REVISÃO JURÍDICA:** LGPL3/LGPL2.1, alternativas MPL, GCC, Microsoft,
   EULA/consumidor e LGPD/transferências: [questões concretas](decisoes-e-revisao.md).
3. **DEPENDE DO TITULAR:** quadro comercial, identificação contratual segura,
   modalidade durável de fontes, adoção das minutas e rotinas de suporte/privacidade.
   A [lista exata](decisoes-e-revisao.md#decisões-do-titular) não exige compra agora.
4. **BLOQUEADO:** distribuição/instalação comercial até assinatura/confiança legítima
   e homologação Windows 11 físico, SAC/Defender ativos e ciclo update/uninstall.
   Não há achado novo que demonstre obrigação de comprar Qt Commercial.

Main e PRs #14–#19 preservados; MSIX referência
`e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b`
intacto. Não houve instalação AgroLines, assinatura, compra, contato, merge, convite,
Pages, envio à Store ou alteração de segurança/visibilidade/classificação etária.
A configuração da nuvem recebeu apenas um rascunho de domínios oficiais para
pesquisa; não foi publicada e não cria requisito de rede para o aplicativo.
O repositório já é público; não se promete que empacotamento torne confidencial
o código anteriormente público. Nenhuma visibilidade foi alterada.
