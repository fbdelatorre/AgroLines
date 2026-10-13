# Política de precisão geométrica

A geometria de precisão trabalha em Python/GEOS/PROJ; Leaflet/Qt só apresenta vetores.
Nenhum pixel, simplificação visual ou valor arredondado de um rótulo é salvo como vértice.

## SRC de trabalho e de exportação
UTM pode ser usado como no QGIS. Preservar UTM/datum originais quando declarados, ou
escolher explicitamente outro SRC projetado em metros, incluindo WGS84/UTM (EPSG
326xx/327xx). Geometria de apresentação é EPSG:4326 e o mapa usa EPSG:3857; este último
não é o SRC de cálculo. Em entradas geográficas, a seleção automática busca UTM no
mesmo datum; se não houver informação suficiente, exige escolha manual.

Futuros monitores podem exigir SHP WGS84 geográfico (`EPSG:4326`). Isso é separado do
SRC de cálculo das linhas. A futura exportação deverá verificar datum, época, precisão
numérica do formato e modelo/firmware; nenhum exportador está disponível neste PR.
SIRGAS 2000 e WGS84 não são tratados como sinônimos para prometer RTK centimétrico.

## Preservação e falha segura
Float64 e PostGIS EWKB preservam coordenadas nativas, com SRC em WKT e originais
independentes. Não há arredondamento imposto a duas casas, snapping automático ou
simplificação destrutiva. Versões novas não apagam anteriores nem futuros vínculos.
Dados legados sem relatório permanecem marcados como não avaliados.

Transformações rejeitam ballpark e grades essenciais ausentes. O erro de consistência
source→display→source deve ser <= 0,005 m. Essa ida/volta verifica consistência numérica,
não exatidão do datum. Datums dinâmicos são bloqueados até existir pipeline temporal
validado. Z, época, solução GNSS, base, precisões declaradas e outros metadados são
preservados quando presentes, sem inventar geóide ou conversão vertical.

Distâncias/áreas projetadas são de malha, sujeitas ao fator de escala UTM. O relatório
expõe distorção estimada em m/km e métricas geodésicas do elipsoide original; nenhuma
inclui correção de altitude do terreno. Um desvio de escala de 0,0004 pode corresponder
a 0,40 m por km, mesmo com aritmética milimétrica. Não usar UTM como prova universal
de erro < 1 cm. RTK FIX também não prova exatidão absoluta se base/datum/época forem incertos.

## Relatório executável
`python -m scripts.precision_report --output precision-report.json` gera referências,
valores esperados/obtidos, erro absoluto/relativo, tolerância e aprovação por caso.
O CI publica o JSON em Windows/Linux e falha se ultrapassar tolerância. Os testes
incluem referências cartesianas/analíticas e origem UTM/equador independente da ida/volta.

| Caso | Referência e tolerância |
|---|---|
| Segmentos 1/10/100/1000 m | Malha cartesiana, erro <= 0,005 m |
| Deslocamentos 0,01/0,001 m | Delta cartesiano conhecido, erro <= 0,000001 m |
| Vértices separados por 1 mm | Quadrado analítico, tolerância em m² |
| Paralelas, interseção, buffer | Primitivas GEOS contra referências analíticas; discretização explícita |
| 1000 edições, desfazer/refazer | Incrementos conhecidos e snapshots exatos |
| 10000 vértices | Área de polígono regular analítico e WKB sem perda |
| SRC/limites UTM | Consistência de ida/volta mais controles EPSG e geodésicos independentes |
| PostgreSQL/PostGIS | SRID, validade e coordenadas nativas exatas após recuperar/reiniciar |
| Datum/vertical/RTK | Rejeição de datum dinâmico sem pipeline; metadados/Z preservados, sem promessa absoluta |

As primitivas de buffer/offset nesse relatório não implementam planejamento agrícola.
A meta acumulada de 0,01 m de um planejamento só poderá ser declarada quando o fluxo
completo tiver testes próprios. Nenhum resultado deste PR é classificado como
centimétrico em campo, e não existe exportação centimétrica habilitada.

A acurácia real depende da fonte, datum, época, base RTK, modelos verticais e método
validado. O relatório mostra o que foi medido e o que permanece desconhecido; não
substitui controle de campo independente.
