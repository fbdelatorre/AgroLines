# Solicitações residuais específicas — não enviadas

Usar com os anexos públicos já preparados no
[#16](../compliance/windows-validation/supplier-requests/), preservando os hashes
do [inventário por arquivo](../compliance/inventory.json). Estas atualizações
substituem apenas o trecho sobre material ainda faltante; não repetem pedidos de
LICENSE genérico ou materiais agora obtidos. **DEPENDE DE TERCEIRO** em cada caso.
Respostas de suporte não equivalem a parecer jurídico.

Nenhum contato foi feito, issue aberta ou dado pessoal enviado. O titular pode
enviar, após sua revisão, somente o anexo específico, versões e hashes públicos.
Não anexar aplicativo, código próprio, logs de usuário, contratos ou credenciais.
Contatos abaixo são canais públicos dos projetos; login pode ser necessário.

## U01 — Qt/PySide6/Shiboken

Canal oficial: [Qt for Python issue tracker](https://qt-project.atlassian.net/browse/PYSIDE),
referenciado nos metadados oficiais PyPI; documentação em
[Qt licensing](https://doc.qt.io/qt-6/licensing.html) e
[Qt for Python licenses](https://doc.qt.io/qtforpython-6/licenses.html).
Anexo específico existente:
[qt-pyside-attachment.json](../compliance/windows-validation/supplier-requests/qt-pyside-attachment.json).

> Subject: Remaining source/build and static-notice correspondence for Windows PySide6 6.12.0 wheels
>
> We are documenting redistribution of the attached exact Windows x64 wheel/native
> hashes under their available Community licenses. We already retained the license
> texts and public source revisions and demonstrated external Python bindings and
> a rebuilt Qt Core in an isolated frozen consumer. We are not requesting a generic
> commercial-license quotation or legal approval.
>
> Please identify the exact final source revisions, downstream patches, build/configure
> inputs and compiler/CRT configuration for the shipped PySide6, Shiboken and Qt 6.12.0
> binaries in the attachment. For the actually shipped Core/Gui/Widgets/Network,
> WebChannel/SVG/Quick/QML and plugins, please identify static third-party components
> and their required attribution files, including software OpenGL. Public revisioned
> recipes or archived generated configuration/notices would be sufficient where complete.
> Please distinguish public source-release configuration from the wheel build itself.

**Falta e razão:** não foi localizado um vínculo completo entre os targets desses
wheels e suas configurações/atribuições estáticas; fonte nominalmente 6.12 não
comprova tudo. **Quem:** responsável pelos builds Qt/PySide. **Evidência para encerrar:**
revisões/receitas/patches por alvo e avisos necessários, associados aos hashes;
validar integridade, incorporar os materiais e revisar o escopo LGPL. **Menor passo:**
titular revisar/enviar esse pedido com o anexo existente, sem pacote proprietário.

## U02 — Qt WebEngine/Chromium/PDFium

Mesmo canal Qt; referências oficiais:
[licenças WebEngine](https://doc.qt.io/qt-6/qtwebengine-licensing.html),
[fontes](https://code.qt.io/cgit/qt/qtwebengine.git/).
Anexo:
[qt-webengine-attachment.json](../compliance/windows-validation/supplier-requests/qt-webengine-attachment.json).

> Subject: Exact Chromium/PDFium source and generated notices for PySide6 WebEngine/PDF 6.12.0.140 Windows wheels
>
> The delivered wheel version is 6.12.0.140; runtime reports 6.140.0 and Chromium
> 140.0.7339.225. The public candidate source checked previously reports
> 140.0.7339.264, so we have not treated that as exact corresponding source.
> Please provide the final QtWebEngine/QtPdf and qtwebengine-chromium/PDFium revisions,
> downstream/security patches, GN arguments and enabled codec/features for the
> attached Windows binary hashes. Please include generated third-party credits and
> source/license lists for the actual linked GN targets, including static/resource
> components, plus their source/build inputs where redistribution requires them.
> An exact archived build recipe and generated notices are preferred over links to
> generic Chromium homepages. We are not asking you to approve our proprietary code.

**Falta e razão:** diferença comprovada de revisão e ausência de créditos completos
demonstráveis. A enumeração/decodificação adicional de recursos PAK não resolveu;
arquivos JS não foram apresentados como textos legais. **Quem:** mantenedor do build
WebEngine/PDF. **Evidência para encerrar:** gitlinks finais, flags/codecs e avisos/fontes
dos targets efetivos, conferidos contra o anexo. **Menor passo:** enviar pedido
específico; não repetir `chrome://credits` como solução garantida.

## U04 — Fiona/vendors

Canal oficial: [Toblerity/Fiona](https://github.com/Toblerity/Fiona/issues), referência
de origem e build no [repositório](https://github.com/Toblerity/Fiona).
Anexo:
[fiona-attachment.json](../compliance/windows-validation/supplier-requests/fiona-attachment.json).

> Subject: Residual native/static BOM and source mapping for Fiona 1.10.1 Windows wheel
>
> We have independently matched the nine GDAL recipe source inputs already listed
> in our evidence. We also obtained the official libiconv 1.17, FreeXL 2.0.0 and
> SpatiaLite 5.1.0 archives matching SHA512 in vcpkg baseline
> 1de2026f28ead93ff1773e6e680387643e914ea1, with their notices and port patches.
> We are not asking for these public files again. Runtime SpatiaLite HasGCP/HasRtTopo
> both return 0 for the attached original hash. The SZIP commercial-encoder issue
> was addressed in our new experimental payload with a separately source-built BSD
> libaec replacement; no permission to redistribute the original encoder is assumed.
>
> For the original Fiona wheel hashes, please identify the remaining exact native
> and static driver/codec BOM and source/build/patch correspondence, especially the
> GEOS 3.11.3 pair and any source changes not represented by the declared vcpkg ports.
> Please provide the corresponding copyright/notice files and clarify selected
> alternatives for the actual multi-licensed FreeXL/SpatiaLite configuration.
> A per-target build/cache provenance record would help distinguish declared recipes
> from actual binary inputs. We do not request generic GPL/LGPL legal approval.

**Falta e razão:** os inputs das receitas e as features conhecidas não cobrem todos
os objetos/drivers efetivamente incorporados. **Quem:** mantenedor do wheel Windows
e suas receitas. **Evidência para encerrar:** mapa residual fonte/patch/BOM por hash
e avisos correspondentes; não um novo inventário de todo ambiente de desenvolvimento.
**Menor passo:** enviar o delta com o anexo de hashes originais; juntar separadamente
o registro público libaec para deixar claro que o slot novo não é o binário upstream.

## U06 — pyproj/PROJ/dados

Canal oficial: [pyproj4/pyproj](https://github.com/pyproj4/pyproj/issues);
[licença PROJ](https://proj.org/en/stable/about.html#license).
Anexo:
[pyproj-attachment.json](../compliance/windows-validation/supplier-requests/pyproj-attachment.json).

> Subject: Residual source/build and database attribution mapping for pyproj 3.8.0 Windows wheel
>
> We retained the existing PROJ source/build inputs and license evidence and added
> exact libjpeg-turbo 3.1.4.1, TIFF 4.7.1 and zlib 1.3.1 notices to our package.
> For the attached native hashes, please identify remaining PROJ 9.8.1 build patches,
> static third-party components and required attribution documents not covered by
> those records. Please identify redistribution/attribution terms for the database
> contents actually bundled in this wheel (including PROJ-data/EPSG/ESRI/IGNF/NKG
> entries identified in the attached inventory), and distinguish them from optional
> grids that are not distributed. We are not asking for extra grids or asserting a
> copyleft source-delivery obligation for permissively licensed code.

**Falta e razão:** direitos/atribuições do conteúdo efetivamente entregue e mapa
residual de patches/estáticos não estão demonstrados integralmente pelo copyright
geral PROJ. **Quem:** mantenedores pyproj/PROJ ou titular específico da base quando
encaminhado pelo mantenedor. **Evidência para encerrar:** lista aplicável de termos e
componentes por release/hash, incorporada ao manifesto. **Menor passo:** enviar o
pedido restrito; não presumir país, contrato ou copyleft não documentados.

## Pedidos que não devem ser repetidos agora

- U05 Shapely: fonte e receita oficial foram obtidas e ligadas à publicação
  verificada; [escopo de fechamento](README.md#u05-escopo-exato-do-encerramento).
- U07: identificador/commit/receitas OpenBLAS obtidos. Primeiro revisar a aplicação
  concreta da GCC Runtime Library Exception com os materiais existentes; solicitar
  mapa/toolchain adicional apenas se essa revisão identificar necessidade específica.
- U08: contrato Store não bloqueia o canal standalone. Conferir primeiro os termos
  de redistribuição aplicáveis às ferramentas realmente usadas; não abrir chamado
  Microsoft genérico nem comprar licença por presunção.
