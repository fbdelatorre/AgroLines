# Avisos de terceiros — documento principal em português

Este material identifica software de terceiros presente na referência indicada no
[README](README.md). Não é uma licença própria aprovada nem uma declaração de
conformidade. Textos originais estão em [notices/reference](notices/reference/),
com caminhos/hashes em [evidence/notices.json](evidence/notices.json). Preserve os
originais em inglês; este resumo não os substitui nem altera seus termos.

## O que já foi reunido

- CPython: texto integral distribuído, incluindo termos históricos e componentes
  ali descritos. OpenSSL 3.0.16 e SQLite 3.49.1 são identificados separadamente.
- NumPy: licença integral **do wheel Windows exato**, com copyright NumPy,
  OpenBLAS, LAPACK e GCC runtime/Runtime Library Exception 3.1; licenças de
  libdivide, pythoncapi-compat, Highway, dragon4, x86-simd-sort, SVML, pocketfft,
  lapack_lite e geradores aleatórios conservadas com seus próprios textos.
  Uma menção em um notice não prova que cada caminho de execução foi compilado.
- Fiona/GDAL: textos originais BSD da Fiona, agregado LICENSE.TXT/copyright do
  GDAL e copyright PROJ. O agregado GDAL não licencia automaticamente as 39 PE
  de seu grupo. Libiconv, GEOS, SpatiaLite, FreeXL, SZIP e demais drivers precisam
  da revisão específica indicada no inventário.
- Shapely: BSD, LICENSE_GEOS e aviso MSVC originais. GEOS tem obrigação própria;
  o antigo link MSVC do wheel não comprova termos de todas as versões atuais.
- pyproj: MIT do binding, licença PROJ e copyright dos dados incluídos; SQLite,
  curl, TIFF, JPEG e XZ vendorizados têm escopo próprio.
- Leaflet 1.9.4: BSD-2-Clause original do recurso **realmente empacotado**.
  Isso não fornece direitos sobre imagens de satélite ou tiles externos.
- attrs, certifi e defusedxml: originais associados a módulos/dados presentes.
  A cópia `cacert.pem` foi comparada com a fonte exata do certifi (MPL-2.0).
- LGPLv3, GPLv3 e LGPLv2.1 integrais já presentes na referência foram preservadas;
  cópias complementares verificadas e cabeçalhos Qt versionados estão em `upstream/`.
  A LGPLv3 exige também o texto GPLv3; o texto GPL não torna o código próprio GPL.

Os copyrights específicos estão preservados nos documentos originais e indexados
por componente em `inventory.json`. Cabeçalhos Qt guardam copyright do fornecedor,
SPDX e origem; não foram publicados arquivos de implementação Qt como se fossem
aplicação AgroLines. Os arquivos LicenseRef-Qt-Commercial de 470 bytes foram
preservados **como evidência do wheel**: são condicionais a contrato inexistente
confirmado e não conferem licença comercial nem substituem a alternativa LGPL.

## O que estes documentos ainda não cobrem

Não há prova de completude dos créditos Chromium/PDFium, build do software OpenGL,
fontes/codecs incorporados em Qt, nem de todos os vendorizados GIS. Não preenchê-los
com textos MIT genéricos. A seleção de codec, seu uso apenas offline ou uma licença
Qt Commercial não garantem liberação de patentes. Obter SBOM, flags de build,
licenças e atribuições exatas dos fornecedores; revisar patentes só para o que
estiver efetivamente presente e conforme mercados/uso, sem presumir taxas devidas.

`notices/reference/third-party-notices` reproduz também avisos excedentes de
ferramentas já existentes no MSIX. pip/setuptools/pefile/altgraph não são aqui
apresentados como bibliotecas de runtime só por esses textos. Sua manutenção no
arquivo de evidência evita apagar a história; o novo coletor corrige o escopo futuro.
Não foi demonstrada alteração própria dos motores; renomeação/patch de importação
delvewheel e patches de fornecedores continuam sujeitos a fonte e receita.

Antes de distribuir: resolver lacunas, revisar obrigações, selecionar apenas os
avisos aplicáveis ao novo payload, fornecer acesso adequado ao usuário e validar
novamente o pacote e seu manifesto. O dossiê separado não prova que avisos novos já
estejam dentro do MSIX imutável nem acessíveis pela interface instalada.

## Complementos versionados obtidos nesta etapa

Foram obtidos textos originais OpenSSL 3.0.16/3.3.1, json-c 0.17, PNG 1.6.43, WebP 1.4.0, netCDF 4.8.1, OpenJPEG 2.5.2, Qhull 2020.2, zlib 1.3.1, Zstd 1.5.6, JPEG-turbo 3.0.3, XML2 2.11.8, Expat 2.6.2, XZ 5.6.2/5.8.3, curl 8.19.0, HDF5 1.14.4.3, PostgreSQL 16.2 e SQLite. URLs versionadas, blobs e hashes estão em `evidence/upstream-notices.json`. A associação é por componente; não equivale a conceder direitos sobre todo o wheel. AUTHORS e COPYING GEOS de ambas as versões foram acrescentados.

A leitura estática dos exports identificou FreeXL 2.0.0, SpatiaLite 5.1.0 e versões adicionais sem executar DLLs. SZIP exporta SZ_encoder_enabled, cuja implementação não foi executada. Obter os termos específicos do build para codificação e patentes históricas; não se presume direito comercial de encoder, isenção ou pagamento devido. Fontes/licenças exatas das variantes copyleft e créditos Chromium permanecem lacunas materiais.
