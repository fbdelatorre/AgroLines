# ADR 0003 — Cartografia e precisão na Etapa 3.1
Status: implementada como primeiro incremento da Etapa 3; não aprova a Etapa 3 completa.

## Escolha
PySide6 permanece a interface nativa. Leaflet 1.9.4, distribuído localmente sob BSD,
renderiza vetores dentro de Qt WebEngine. Qt WebChannel transporta apenas coleções
para apresentação e IDs de seleção; tokens da API ficam em Python. Nenhuma conexão
externa é necessária para exibir polígonos. Qt WebEngine mantém seu sandbox na aplicação.

PyQGIS foi avaliado e não adotado neste incremento: utiliza os bindings e a distribuição
Qt/Python do QGIS, normalmente PyQt, com custo elevado para combinar com a aplicação
PySide6/Python 3.12 e para um futuro instalador. Isso não impede interoperabilidade
por formatos e SRC usados no QGIS. Não há motor GIS próprio: Leaflet cuida da navegação,
GEOS/Shapely da geometria, PROJ/pyproj de SRC e GDAL/Fiona da leitura de SHP/GPKG/KML.
DefusedXML recusa entidades e referências externas no KML; KMZ é lido com limites.

## Geometria de precisão
A geometria nativa e o original são independentes da geometria WGS84 de apresentação.
PostGIS armazena a nativa em `geometry`, com SRID original quando identificável, em
dupla precisão; SRC personalizado sem EPSG permanece SRID 0 com WKT explícito.
Originais e atributos são preservados, incluindo Z e metadados de levantamento.
A representação 2D do mapa nunca substitui esses dados nem alimenta cálculos por pixels.

Os padrões oficiais são EPSG:4326 geográfico e EPSG:32723 de trabalho.
Cada propriedade inicia em UTM 23S e permite escolher outro UTM EPSG em metros.
O SRC original é sempre preservado, inclusive SIRGAS 2000. Alterar o SRC de trabalho
não reescreve versões históricas nem comprova equivalência centimétrica entre datums.
Transformações usam `always_xy`
e `TransformerGroup` sem ballpark; falta da melhor grade/parâmetro bloqueia o fluxo.
Datums dinâmicos são recusados até existir transformação temporal validada.

Distâncias e áreas projetadas são de malha. Área/perímetro geodésicos usam o elipsoide
do SRC original como comparação; não são corrigidos para altitude do terreno.
O relatório registra datum, unidades, erro de consistência, precisão declarada das
transformações, distorção da projeção e metadados originais. Não classifica RTK FIX
nem qualquer arquivo como centimétrico em campo apenas pela origem.

O objetivo numérico de 0,005 m aplica-se a operações controladas demonstradas por
testes. Não é uma garantia universal de datum, georreferenciamento ou posicionamento.
Vértices numéricos usam float64 sem arredondamento decimal imposto, deslocamentos
matemáticos em metros e azimute da malha. Vértices não alterados mantêm valores
originais exatos. Undo/redo restaura snapshots; gravação cria nova versão, com
controle otimista para não sobrescrever trabalho concorrente. Não há simplificação
destrutiva nem exportação classificada como centimétrica.

## Persistência e autorização
Migrações 0003/0004/0005 são aditivas; 0004 não reconstrói coordenadas nem inventa relatórios
para versões legadas. Elas continuam disponíveis com originais e precisão desconhecida.
Importação é atômica sob lock da propriedade, deduplica geometria exata normalizada,
verifica hashes de originais e requer confirmação para sobreposições acima de 0,01 m².
Esse limiar é aviso topológico, não tolerância de posicionamento nem quantização.

Leitura exige autorização no servidor. Acesso por safra/operação mostra apenas talhões
explicitamente vinculados ao escopo; conhecer o cabeçalho da propriedade não concede
seus limites. Edição/importação de limites globais requer `edit` na propriedade inteira.
Histórico e arquivos originais completos exigem leitura da propriedade inteira, pois
um arquivo pode conter objetos de outros escopos. Logout, expiração e revalidação
limpam os vetores; não há cache offline autorizado de geometrias neste incremento.

## Distribuição e limites
Fiona, PROJ e GEOS usam wheels Windows; `Configure.ps1 -Desktop` instala dependências.
O instalador futuro deverá empacotar automaticamente runtimes, avisos de licença e
grades aprovadas, sem depender de um QGIS instalado. Não se exige Docker.

Este incremento entrega mapa, importação de polígonos, versões e edição numérica.
Desenho livre, pontos/linhas de cadastro, snapping, divisão/união, produtores completos,
raster local, MDT e sincronização ficam em PRs subsequentes da própria Etapa 3.
Algoritmos agrícolas e exportadores de monitores permanecem fora do escopo.
