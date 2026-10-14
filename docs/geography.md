# Cartografia — Etapa 3.1

Primeiro PR da Etapa 3, baseada na Etapa 2.1. Não representa aprovação completa da Etapa 3.

## Uso no Windows, sem Docker
Faça backup antes de atualizar o servidor. Com Python 3.12 e PostgreSQL/PostGIS já
instalados, execute na raiz:

```powershell
.\scripts\Configure.ps1 -Desktop
.\scripts\Start-Server.ps1
# Em outro terminal:
.\.venv\Scripts\python.exe -m desktop.main
```

O servidor aplica migrações 0003/0004/0005 aditivas. Não recrie o banco. PostgreSQL 18 e
PostGIS 3.6.2 seguem o mesmo procedimento nativo; CI também testa séries 16/3.4 e
18/3.6. Nunca altere a versão principal de um volume Docker existente sem um plano
separado de upgrade PostgreSQL. A imagem padrão e o PGDATA de uso existente são mantidos.

Entre e abra **Mapa**. Selecione propriedade, safra e talhão pela barra superior.
A roda do mouse e os botões permitem zoom; arraste para deslocar. Clique num polígono
para consultar atributos, métricas e precisão. **Extensão** enquadra os talhões carregados.
Camadas têm visibilidade, ordem por arraste, opacidade e cores. O estado de navegação
é mantido ao trocar telas no mesmo contexto. Os painéis são redimensionáveis/recolhíveis.

## Importação e edição
Selecione a propriedade e use **Importar**. Aceita SHP, GPKG, KML, KMZ e GeoJSON,
com múltiplos arquivos e até 100 polígonos por lote. SHP exige SHP/SHX/DBF e PRJ,
ou um SRC informado explicitamente; CPG é preservado se disponível. Um GPKG pode
conter múltiplas camadas poligonais. KML declara WGS84 por especificação; KMZ admite
um documento KML, sem links/entidades externas. GeoJSON sem SRC declarado exige
confirmação explícita pelo campo SRC; não se presume um datum desconhecido.

Os padrões oficiais são WGS 84 (EPSG:4326) para coordenadas geográficas e
WGS 84 / UTM 23S (EPSG:32723) para cálculos métricos. Cada propriedade inicia em
EPSG:32723; no painel Camadas, **Salvar SRC** permite outro UTM.
A alteração não reescreve versões anteriores. O SRC original permanece preservado,
inclusive quando diferente de WGS84; entradas sem referencial exigem confirmação.
O cursor mostra latitude/longitude e coordenadas no SRC de trabalho via PROJ.
O mapa usa EPSG:3857 exclusivamente para apresentação, nunca para cálculos.

Confira a prévia, atributos pelo mapa e avisos. Correção GEOS só ocorre ao marcar
**Corrigir inválidas**. Originais nunca são sobrescritos por essa correção. Sobreposições
exigem confirmação; geometrias exatamente repetidas não criam outro talhão.
**Salvar importação** cria talhões e preserva arquivos; **Descartar** remove só a prévia.
Troca de propriedade/encerramento com prévia oferece Salvar, Descartar ou Cancelar.

Para editar, selecione um talhão e use **Editar vértices numericamente**. Escolha o
vértice, informe X/Y em metros ou deslocamento/azimute. `0,001` e `0,01` são aceitos.
Ctrl+Z/Ctrl+Y desfazem/refazem alterações temporárias sem quantização. Salvar cria
nova versão após validação topológica e revalidação de permissão; um conflito de
versão retorna 409, sem sobrescrever a outra alteração. Não é desenho por pixels.

A vinculação de talhões a safras/operações está disponível na API:
`POST /farms/{farm}/plots/{plot}/scopes` com `season_ids` e `operation_ids`.
O formulário dessa associação é um incremento posterior. Usuários com acesso restrito
veem somente geometrias vinculadas ao escopo escolhido; arquivos originais completos
não são liberados para um escopo parcial. Importação e alteração global de limites
exigem perfil com edição na propriedade inteira, confirmado no servidor.

Limites operacionais: 8 MiB por arquivo, 32 MiB de originais por lote, 48 MiB por
requisição HTTP, 100 mil vértices por polígono e extensão local até 3° por eixo.
Arquivos originais são guardados transacionalmente no servidor com hash SHA-256.
Não há provider de imagens padrão. Não há sincronização nem fila de gravação offline.

## Imagens autorizadas
Opcionalmente configure um provedor HTTPS cujos termos autorizem o uso no aplicativo:

```powershell
$env:AGROLINES_TILE_AUTHORIZED = '1'
$env:AGROLINES_TILE_URL = 'https://seu-provedor-autorizado.example/{z}/{x}/{y}.png'
$env:AGROLINES_TILE_ATTRIBUTION = 'Atribuição exigida pelo provedor'
$env:AGROLINES_TILE_LICENSE_URL = 'https://seu-provedor-autorizado.example/licenca'
```

Esses valores são exemplos de configuração, não um serviço disponível. Não copie
credenciais para o Git ou chat. Atribuição aparece no mapa; somente o host configurado
é autorizado pelo renderizador. O perfil Qt é efêmero, sem cache HTTP persistente;
imagens exigem conectividade e são removidas quando o servidor fica offline.
O operador deve conferir termos, limites e eventual necessidade de cache diferente;
esta etapa não promete imagens de terceiros offline. Rasters locais, COG/MDT e
ortomosaicos são preparação arquitetural, não funcionalidades disponíveis.

## Precisão, testes e etapas restantes
Veja [política e relatório de precisão](precision.md) e a [decisão técnica](adr/0003-map-and-precision.md).

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m scripts.precision_report --output precision-report.json
.\.venv\Scripts\python.exe -m scripts.render_desktop --output visual-windows
```

O último comando usa Qt nativo Windows, vetores sintéticos, clique real de identificação,
importação e salvamento. Inspecione as capturas; offscreen Linux não comprova aparência
ou interação Windows. Complete manualmente roda do mouse, pan, DPI entre monitores,
edição numérica, revogação enquanto mapa está aberto e reconexão.

Ainda faltam: produtores completos, associação por formulário, desenho livre, criação
de pontos/linhas, snapping, adicionar/remover vértices, dividir/unir/copiar/excluir,
raster/MDT e cache GeoPackage. Essas entregas pertencem a próximos PRs da Etapa 3.
Não iniciar algoritmos agrícolas, exportadores ou Etapa 4 sem aprovação.
