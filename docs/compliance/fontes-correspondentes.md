# Fontes de terceiros — obtenção e limites de correspondência

Índice verificável: [sources-index.json](sources-index.json). Não são links genéricos:
cada sdist tem URL do arquivo exato e SHA-256 confirmado pelo JSON oficial PyPI;
cada árvore Git tem repositório oficial, commit fixo e SHA-256 do `git archive`.
A integridade foi verificada por HTTPS/digest/commit; não se declara validação
criptográfica de assinatura de tag dos fornecedores.

## Materiais preparados, sem publicação

- GEOS 3.11.3 e 3.14.1: árvores oficiais completas, COPYING, build CMake/C API;
  pares distintos distribuídos em Fiona e Shapely. O build Windows e patches dos
  wheels ainda não estão relacionados por prova completa a esses commits.
- Qt Base 6.12.0 e PySide/Shiboken 6.12.0: árvores oficiais com textos de licença,
  fontes e scripts; incluem scripts de build. Também foram preparados Qt Declarative, Positioning,
  SerialPort, SVG, WebChannel e ImageFormats 6.12.0 de commits oficiais fixos.
  QtWebEngine/Chromium, submódulos e flags do wheel continuam sem fechamento;
  não são uma oferta completa LGPL.
- CPython 3.12.10: árvore oficial com PCbuild e lista versionada de fontes externas.
  Fontes externas não são todas incorporadas ao arquivo Git e devem ser obtidas
  quando exigidas; nenhuma exigência universal de fonte é inferida da PSF.
- PROJ 9.3.1: árvore oficial; SPDX do wheel declara recurso OSGeo/PROJ@9.3.1 e
  SHA-512, além dos hashes dos patches/receita. Não equivale a build reproduzido.
- Sdists oficiais exatos de NumPy 2.5.4, Shapely 2.2.0, pyproj 3.8.0, Fiona 1.10.1,
  certifi 2026.7.22, attrs 26.1.0 e defusedxml 0.7.1. Sdist do binding **não contém
  necessariamente a fonte de suas DLLs vendorizadas**.

**Correspondência material comprovada:** `certifi/cacert.pem` possui SHA idêntico
no payload e no sdist exato; esse é o escopo da evidência MPL, não uma certificação
de todo o wheel. Para Leaflet, JS/CSS/licença no repositório também são idênticos
às entradas distribuídas. Nenhum fonte Qt/GEOS foi declarado correspondente exato
a todo o build Windows apenas por coincidir a versão. Os 177 PE de terceiros
inalterados em relação ao candidato original tampouco provam ausência de patches
no fornecedor.

## Reproduzir os arquivos

Para entradas Git, clonar o repositório oficial e selecionar o **commit** do índice;
`git archive --format=tar --prefix=<nome>/ -o <filename> <commit>`. Conferir SHA-256
contra o índice antes de usar. Para sdists, baixar a URL exata e conferir digest;
não executar setup.py nem instalar o código recebido. Não usar downloads sem TLS.

```sh
python -m scripts.compliance_bundle \
  --source-dir /tmp/agrolines-compliance-sources \
  --output build/compliance/third-party-sources-PARTIAL-NOT-FOR-DISTRIBUTION.zip
```

O empacotador aceita só os arquivos do índice e documentos legais, verifica hashes,
recusa links/caminhos fora da raiz e sobrescrita. Não inclui fonte, objeto ou
bytecode do AgroLines. O ZIP fica local/ignorado; não há workflow de publicação de
fontes. O resultado é **parcial, para revisão**, não oferta de fonte aprovada.

## Material ainda necessário

1. Qt/PySide: revisão exata dos wheels, commits de todos os módulos/submódulos,
   patches, compiladores, configure/CMake flags, scripts/geradores e fontes de
   terceiros necessários para produzir as bibliotecas. WebEngine informa 6.140.0,
   Chromium 140.0.7339.225; as tags finais correspondentes não foram comprovadas.
   Não trocar silenciosamente por `dev`, beta ou RC. Obter confirmação do fornecedor.
2. GEOS: receita/patches e import repairs dos dois pares de DLLs Windows; objetos
   ou mecanismo compartilhado conforme a alternativa LGPL2.1 escolhida.
3. libiconv 1.17, SpatiaLite/FreeXL: determinar licença escolhida e fonte correspondente
   à versão exata; não tratar os três como MIT por estarem em um wheel Fiona.
4. OpenBLAS 0.3.34.106.0 (declaração de build), LAPACK e runtime GCC estático:
   revisão do build e condições da exceção, versões/patches/componentes efetivos.
5. Chromium/PDFium/software OpenGL, drivers e codecs: créditos e source/build BOM
   exatos. PROJ database e dados EPSG/outros: conferir notices/versão das bases
   realmente incluídas, não baixar grids adicionais nem inferir direitos de uso.

Arquivos SPDX vcpkg preservados no payload e wheels dão hashes/nomes de patches.
As receitas do repositório `sgillies/fiona-wheels` examinado **não foram equiparadas
sem comparação** ao builder registrado: arquivo de mesmo nome pode divergir.
A solicitação reproduzível ao fornecedor deve incluir paths/SHA de `inventory.json`,
versão dos wheels e SPDX, e pedir fontes, patches, scripts e atribuições desses
bytes. Nenhuma mensagem foi enviada a fornecedores nesta tarefa.

## Forma futura de disponibilização

LGPLv3/GPLv3: revisar a modalidade de §6 aplicável à distribuição; para §6(d),
acesso equivalente às fontes correspondentes com instruções claras e meios
permitidos, inclusive servidor de terceiro quando atendidas as condições. Um link
à homepage e um arquivo parcial não bastam. Oferta de três anos não é solução
universal a toda modalidade. LGPLv2.1: analisar separadamente §6(a)–(e), inclusive
materiais/forma da alternativa adotada. MPL-2.0: acesso aos arquivos cobertos e
modificações, com informação ao destinatário. Não licenciar o código próprio sob
MPL/LGPL por engano nem publicar materiais próprios sem autorização.

## WebEngine: material candidato delimitado

Foi arquivada também a branch oficial 6.140 em commit fixo, com gitlinks dos
submódulos registrados. Esse arquivo **não contém** as árvores Chromium/PDFium dos
submódulos e não é fonte correspondente comprovada do wheel. Serve para identificar
os scripts/alvos de créditos e preparar a solicitação exata ao fornecedor. A prova
Windows de ausência de chrome://credits está em `evidence/qt-credits-runtime.json`;
a captura falhou e não foi apresentada como aviso reunido. Ver
[solicitações não enviadas](solicitacoes-fornecedores.md).
