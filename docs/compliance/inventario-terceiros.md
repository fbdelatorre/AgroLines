# Inventário dos componentes efetivamente presentes

Referência imutável: `75fe75bd8d7097b826d46c4cd50576162f99aede3eb2db9def34d21a3b25ac90`.

Todos os 798 caminhos foram registrados; 178 são PE. Isso não fecha os componentes incorporados estaticamente. O inventário por arquivo completo está em [inventory.json](inventory.json); origem exata, importadores, assinatura e carregamento estão em [evidence/native.json](evidence/native.json).

| Componente/projeto | Versão identificada/declarada | Licença/evidência disponível | PE | Pendência real |
|---|---|---|---:|---|
| CPython | 3.12.10 | PSF-2.0 and historical/bundled terms | 20 | Exact upstream source/build mapping and complete static dependency attribution |
| Fiona-bindings | 1.10.1 | BSD-3-Clause; native dependencies separately recorded | 7 | Exact upstream source/build mapping and complete static dependency attribution |
| freexl-Fiona | 2.0.0 (PE exported constant, read without execution) | FreeXL dual licensing requires exact source/build evidence | 1 | Obtain exact-version source/license selection, patches and build recipe from supplier |
| gdal-Fiona | 3.9.1 | MIT-style and terms in distributed GDAL LICENSE.TXT | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| GEOS-Fiona | 3.11.3 | LGPL-2.1 per GEOS COPYING; version/patch review pending | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| geotiff-Fiona | Não comprovada | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| gif-Fiona | Não comprovada | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| HDF5-Fiona | 1.14.4.3 (DLL version banner; exact source/build mapping pending) | HDF5 permissive license, third-party terms separate — versioned upstream text; Windows build/embedded scope not automatically cleared | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| iconv-Fiona | 1.17 | GNU libiconv LGPL-2.1-or-later candidate; exact build notice/source pending | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| jpeg62-Fiona | 3.0.3 (PE file resource) | IJG and BSD/Zlib portions; LICENSE.md/README.ijg — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| json-c-Fiona | 0.17 (PE exported constant, read without execution) | MIT — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| lerc-Fiona | Não comprovada | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| OpenSSL-Fiona | 3.3.1 (PE file resource) | Apache-2.0 — versioned upstream text; Windows build/embedded scope not automatically cleared | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| libcurl-Fiona | 8.8.0-DEV (PE file resource) | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| libexpat-Fiona | 2.6.2.0 (PE file resource) | MIT — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| liblzma-Fiona | 5.6.2 (PE file resource) | XZ COPYING explains per-component terms; liblzma scope differs from tools — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| libpng16-Fiona | 1.6.43 (PE exported constant, read without execution) | libpng license; full versioned text — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| libpq-Fiona | 16.2 (PE file resource) | PostgreSQL License — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| libwebp-Fiona | 1.4.0 (exported integer 0x010400) | BSD-3-Clause and additional patent grant file review — versioned upstream text; Windows build/embedded scope not automatically cleared | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| libxml2-Fiona | 2.11.8 (PE file resource) | MIT and included notices — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| minizip-Fiona | Não comprovada | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| Microsoft-VC-runtime | multiple; see each PE product_version | Microsoft distributable-code terms; no blanket right inferred from signature | 14 | Exact upstream source/build mapping and complete static dependency attribution |
| netcdf-Fiona | 4.8.1 of Sep 16 2024 17:22:37 $ (PE exported constant, read without execution) | NetCDF permissive copyright license — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| openjp2-Fiona | 2.5.2 (PE exported constant, read without execution) | BSD-2-Clause — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| pcre2-Fiona | Não comprovada | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| proj-Fiona | 9.3.1 | MIT per bundled vcpkg SPDX/COPYING | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| qhull_r-Fiona | 2020.2.r 2020/08/31 (PE exported constant, read without execution) | Qhull permissive license — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| spatialite-Fiona | 5.1.0 (PE exported constant, read without execution) | SpatiaLite LGPL/MPL/GPL alternatives require exact source/build evidence | 1 | Obtain exact-version source/license selection, patches and build recipe from supplier |
| sqlite3-Fiona | 3.46.0 (PE file resource) | SQLite public-domain dedication; extensions/build separate — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| szip-Fiona | Não comprovada | Exact component license pending supplier evidence | 1 | Obtain exact SZIP source/license and encoder/patent conditions; exported SZ_encoder_enabled alone is not permission or proof of use |
| tiff-Fiona | 4.6.0 (PE file resource) | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| zlib1-Fiona | 1.3.1 (PE exported constant, read without execution) | Zlib — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| zstd-Fiona | 1.5.6 (PE exported constant, read without execution) | BSD-3-Clause alternative in supplied LICENSE — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| OpenSSL-CPython | 3.0.16 | Apache-2.0 — versioned upstream text; Windows build/embedded scope not automatically cleared | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| libffi-CPython | 3.4.4 (CPython recipe; binary version unconfirmed) | MIT upstream; bundled source mapping pending | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| NumPy | 2.5.4 | BSD-3-Clause and full vendored terms in wheel license | 13 | Exact upstream source/build mapping and complete static dependency attribution |
| OpenBLAS-NumPy | 0.3.34.106.0 (wheel build configuration) | BSD-3-Clause; LAPACK BSD; statically linked GCC GPL-3.0-or-later WITH GCC-exception-3.1 | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| pyproj-bindings | 3.8.0 | MIT | 10 | Exact upstream source/build mapping and complete static dependency attribution |
| jpeg62-pyproj | 3.1.4.1 (PE file resource) | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| libcurl-pyproj | 8.19.0 (PE file resource) | curl license — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| liblzma-pyproj | 5.8.3 (PE file resource) | XZ COPYING explains per-component terms; liblzma scope differs from tools — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| PROJ-pyproj | 9.8.1 | MIT; database/data licensing separate | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| sqlite3-pyproj | 3.53.0 (PE file resource) | SQLite public-domain dedication; extensions/build separate — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| tiff-pyproj | 4.7.1 (PE file resource) | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| zlib1-pyproj | 1.3.1 (PE exported constant, read without execution) | Exact component license pending supplier evidence | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| Software-OpenGL-Qt | Não comprovada | Mesa/software renderer attribution/build/license pending exact supplier SBOM | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-Base | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 18 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-SVG | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 3 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-ImageFormats | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 5 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-PDF | 6.140.0 (wheel family; exact DLL version below) | Exact module/source licensing and PDFium notices pending supplier evidence | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-Positioning | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 4 | Exact upstream source/build mapping and complete static dependency attribution |
| PySide6-bindings | 6.12.0; WebEngine bindings wheel 6.12.0.140 | LGPL-3.0-only alternative in inspected versioned headers; all generated binding inputs/build pending | 16 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-Declarative | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 6 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-SerialPort | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-WebChannel | 6.12.0 | LGPL-3.0-only alternative in inspected versioned headers; embedded components not covered generically | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| Qt-WebEngine | 6.140.0 / Chromium 140.0.7339.225 | Qt LGPL alternative candidate; exact 6.140.0 source and Chromium build credits NOT proven | 3 | Exact upstream source/build mapping and complete static dependency attribution |
| Shapely-bindings | 2.2.0 | BSD-3-Clause | 3 | Exact upstream source/build mapping and complete static dependency attribution |
| GEOS-Shapely | 3.14.1 | LGPL-2.1 per GEOS COPYING; version/patch review pending | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| Shiboken | 6.12.0 | LGPL-3.0-only alternative in versioned header | 2 | Exact upstream source/build mapping and complete static dependency attribution |
| SQLite-CPython | 3.49.1.0 | SQLite public-domain dedication; extensions/build separate — versioned upstream text; Windows build/embedded scope not automatically cleared | 1 | Exact upstream source/build mapping and complete static dependency attribution |
| AgroLines-executable | 1.0.0.0 | Proprietary terms not adopted; bootloader exception separate | 1 | Own EULA and PyInstaller bootloader rights review |
| attrs | 26.1.0 | MIT | 0 | Static resources / exact source / complete attributions require review |
| certifi | 2026.7.22 | MPL-2.0 | 0 | Static resources / exact source / complete attributions require review |
| defusedxml | 0.7.1 | PSF-2.0 | 0 | Static resources / exact source / complete attributions require review |
| Leaflet | 1.9.4 | BSD-2-Clause | 0 | Static resources / exact source / complete attributions require review |
| PyInstaller-embedded | 6.22.3 | GPL-2.0-or-later WITH Bootloader-exception; Apache-2.0 portions | 0 | Static resources / exact source / complete attributions require review |
| Chromium-embedded | 140.0.7339.225 | Mixed; complete exact-build credits, source and codecs pending | 0 | Static resources / exact source / complete attributions require review |
| Qt-resources | Não comprovada | Resource provenance/subcomponent review; no license inferred | 0 | Classify embedded resource content; filename coverage is not source-code SBOM completeness |
| resource-review-required | Não comprovada | Resource provenance/subcomponent review; no license inferred | 0 | Classify embedded resource content; filename coverage is not source-code SBOM completeness |
| AgroLines-resources | Não comprovada | Resource provenance/subcomponent review; no license inferred | 0 | Classify embedded resource content; filename coverage is not source-code SBOM completeness |
| Fiona-data | Não comprovada | Resource provenance/subcomponent review; no license inferred | 0 | Classify embedded resource content; filename coverage is not source-code SBOM completeness |
| PROJ-data | Não comprovada | Resource provenance/subcomponent review; no license inferred | 0 | Classify embedded resource content; filename coverage is not source-code SBOM completeness |
| archive-notices-only | Não comprovada | Resource provenance/subcomponent review; no license inferred | 0 | Classify embedded resource content; filename coverage is not source-code SBOM completeness |

## Limites do inventário

`archive-notices-only` são textos que já estavam no pacote, inclusive de ferramentas do builder. Não significa que pip, setuptools ou cada dependência de ferramenta seja código de runtime. `resource-review-required` mantém visível qualquer recurso sem classificação final. Os 517 módulos da Analysis estão em [evidence/module.json](evidence/module.json), incluindo módulos próprios e stdlib; módulos comprimidos/estáticos não se tornam componentes jurídicos identificados só por esse nome.

A versão de cada DLL no PE, quando presente, permanece no registro por arquivo; versões ausentes não foram adivinhadas. OpenBLAS 0.3.34.106.0 é declaração do `numpy/__config__.py` do wheel exato, não identificação de commit ou do LAPACK/GCC. GEOS 3.11.3 e 3.14.1 foram conferidos nas strings dos dois pares de DLLs de wheels com SHA validado, e a segunda também no probe congelado. PROJ 9.3.1 consta no SPDX/CMake da Fiona; PROJ 9.8.1 no probe do pyproj.

Os copyrights transcritos e os textos completos conservam o escopo original. Não se usa o copyright da FSF no texto LGPL como se fosse o copyright de Qt ou GEOS. A inexistência de patch AgroLines não comprova que o fornecedor não aplicou patches, nem elimina os reparos do delvewheel.

## Bases de coordenadas realmente incluídas

Os dois proj.db foram lidos com SQLite `mode=ro&immutable=1`, após confirmar seus
hashes contra o manifesto do MSIX; hashes permaneceram iguais. Fiona: PROJ 9.3.1,
PROJ_DATA 1.16, EPSG v10.098 (24/11/2023), ESRI ArcGIS Pro 3.2. pyproj: PROJ 9.8.1,
PROJ_DATA 1.24, EPSG v12.029 (02/10/2025), ESRI ArcGIS Pro 3.6. Também contêm
registros IGNF e NKG com versões/origens em
[evidence/proj-databases.json](evidence/proj-databases.json). Isso identifica as
bases, sem aplicar automaticamente a licença MIT do software aos datasets.
Nenhuma base, configuração de projeção, grid ou algoritmo foi alterado/atualizado.
