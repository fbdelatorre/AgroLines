# Fechamento dirigido de fontes e avisos

Unidade de contagem: **oito casos de trabalho**, definidos em upstream-cases.json,
não número de bibliotecas nem os 107 campos documentais pendentes do PR #15.
**Um caso fechado com evidência; sete casos de contato preparados (seis conjuntos
de mantenedores de bibliotecas e um caso Microsoft). Zero solicitações enviadas.**
Não se afirma que estes sejam todos os textos de licença ainda necessários.

| Caso | Componente/versão distribuída | Material realmente faltante e próxima ação |
| --- | --- | --- |
| U01 | Qt Base/PySide/Shiboken 6.12.0; Declarative/Quick/QML transitivos, SVG, WebChannel, Positioning, SerialPort, ImageFormats, software OpenGL | Mapa exato dos builds/wheels, patches/flags/CRT e atribuições estáticas completas. Solicitação Qt específica; não reincluir as seis famílias Qt dispensadas. |
| U02 | WebEngine/PDF wheel 6.12.0.140; runtime WebEngine 6.140.0, Chromium 140.0.7339.225 | Commit final e submódulos Chromium/PDFium, GN args, patches, codecs/fontes e saída de créditos dos dois alvos reais. Solicitação WebEngine; chrome://credits falhou anteriormente e não foi repetido. |
| U03 | GDAL 3.9.1 do Fiona 1.10.1 | **Entradas declaradas de receita/fonte fechadas**, conforme abaixo. Demais drivers/build permanecem U04. |
| U04 | Fiona: GEOS 3.11.3, libiconv 1.17, SpatiaLite 5.1.0, FreeXL 2.0.0, SZIP e drivers | Fontes exatas, patches/receitas, alternativa de licença efetivamente aplicável, copyright/avisos vendorizados e estáticos; confirmar implementação/configuração SZIP, sem presumir uso de encoder ou patentes. Solicitar ao mantenedor do wheel. |
| U05 | Shapely 2.2.0 / GEOS 3.14.1 | Receitas Windows/patches/CRT/delvewheel ligando os dois hashes às fontes exatas. Upstream versionado e LGPL2.1 já reunidos; isso não fecha automaticamente o build. |
| U06 | pyproj 3.8.0 / PROJ 9.8.1 e vendors; dados PROJ/EPSG/outros realmente incluídos | Build/patches/BOM e atribuições/termos das versões dos datasets. Não exigir fontes indiscriminadamente de bibliotecas permissivas; verificar obrigações reais e escopo. |
| U07 | NumPy 2.5.4 / OpenBLAS 0.3.34.106.0 declarado / LAPACK / GCC runtime estático | Resolver identificador à revisão/build; versões e elegibilidade da Runtime Library Exception. Texto integral do wheel já disponível; não pedir novamente só LICENSE genérico. |
| U08 | Microsoft: MSVC/Store | Termos efetivamente aplicáveis à redistribuição e conta Individual, acordo aceito/EULA, capacidades e restrições MSIX. Exige documentação da conta/resposta específica. |

Cada solicitação tem JSON adjacente contendo **nome, versão evidenciada, arquivo,
SHA-256, origem do wheel e licença/evidência já disponível**. Não se atribui LGPL a
todo um wheel. Os JSON são recortados somente de arquivos cujo hash confere com
o MSIX atual. Recursos incorporados podem conter mais componentes do que as
classes do inventário; ausência de SBOM estático completo está explicitamente em
U01/U02/U04/U06/U07, não ocultada por metadados Python.

## U03 — nova evidência material

[Verificação](gdal-inputs-verification.json): wheel Fiona SHA-256
`41cde2c52c614457e9094ea44b0d30483540789e62fe0fa758c2a2963e980817`.
Seu `fiona/gdal_data/vcpkg.spdx.json` identifica árvore vcpkg
`65b271a32a93a9dfa4dfd3905fcd0b5388926f81`. É um **Git tree**, não presumir que
seja commit. Os nove blobs oficiais foram obtidos pela API GitHub Microsoft/vcpkg,
conferidos por Git blob SHA-1 e por SHA-256 do SPDX, reproduzindo CRLF Windows
quando necessário. Inclui quatro patches, dois arquivos CMake auxiliares,
portfile, usage e vcpkg.json.

Arquivo oficial [OSGeo/gdal v3.9.1](https://github.com/OSGeo/gdal/archive/refs/tags/v3.9.1.tar.gz):
SHA-256 `38d844e8e321e1bb1bfc87118740b28ca10bfc8b69e754a0f5f22d49fecca0e4`;
SHA-512 coincide integralmente com o recurso do SPDX (ver JSON). O verificador
`tools/compliance-sources/verify_gdal.py` baixa e valida sem executar código.
Os materiais ficaram locais para revisão; não foram adicionados ao payload nem
publicados como oferta completa de fontes. Fonte e receitas não equivalem ao
build reproduzido, nem ao fechamento de todas as dependências do GDAL.

As seis receitas PROJ 9.3.1 e fonte SHA-512 já fechadas no PR #15 não foram
reinvestigadas. Os 151 documentos anteriores não foram recriados. Links
indisponíveis (403/404) permanecem registrados, sem alegar leitura. Fontes Qt
6.140 candidatas continuam sem correspondência exata; os fornecedores devem
responder com revisões e materiais específicos, não homepages.
