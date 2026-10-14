# Revisão e entrega — capturas reais Windows

Revisão: 14/10/2026. Conjunto atual: **run-38570070770**, source `931ff18`
(PR #10 + correções mínimas reais do PR #11). Não houve montagem ou alteração dos PNGs.

## Arquivos para revisão da listagem

| Arquivo | Dimensões PNG | Bytes | Conteúdo conferido |
|---|---|---:|---|
| [01 — principal](captures/run-38570070770/01-tela-principal.png) | 1920×1080 | 48.223 | Limite e três talhões fictícios, mapa local, toolbar e nomes completos |
| [02 — camadas](captures/run-38570070770/02-camadas-importadas.png) | 1920×1080 | 49.913 | Lista importada, GeoJSON/SHP/GPKG identificados e talhão selecionado |
| [03 — vértices](captures/run-38570070770/03-edicao-de-vertices.png) | 1920×1080 | 60.942 | Diálogo legível, coordenadas métricas, alteração aplicada, Salvar/Cancelar em português |
| [04 — projetos/backup](captures/run-38570070770/04-projetos-e-backups.png) | 1920×1080 | 72.170 | Seletor de arquivos real, projeto/backup/restauração sintéticos |

Os quatro cabeçalhos PNG, dimensões, tamanhos e SHA-256 foram verificados localmente
contra a [evidência original](captures/run-38570070770/capture-evidence.json).
Atendem aos limites técnicos Desktop consultados na documentação oficial Microsoft:
PNG, ao menos 1366×768 e menos de 50 MB. A revisão das quatro imagens em tamanho real
confirmou polígonos visíveis e ausência de erros, terminais, depuradores, contas reais,
login/convites ou controles de colaboração. Não foram adicionados painéis inexistentes.

A quarta imagem contém textos em inglês do **seletor nativo do Windows** do runner
(Open/Cancel/Name/Search etc.). Isso foi registrado, não traduzido sobre a imagem.
Para uniformidade integral da listagem pt-BR, recomenda-se recapturar esse estado em
Windows pt-BR com o roteiro manual. Não declarar que todos os textos desse PNG são
portugueses. O produto não dispõe de tela própria de navegação no histórico; a
quarta captura demonstra abertura de projetos/backups, com revisões comprovadas
no SQLite/evidência, não um navegador inventado.

## Execução e evidência

- [Execução de captura](https://github.com/fbdelatorre/AgroLines/actions/runs/38570070770)
- [ZIP das quatro imagens + evidências](https://github.com/fbdelatorre/AgroLines/actions/runs/38570070770/artifacts/11896836791)
- [Projeto e fontes sintéticas para reprodução](https://github.com/fbdelatorre/AgroLines/actions/runs/38570070770/artifacts/11897046664)
- [README e procedimento](README.md)

O Windows reportou sessão 2 ativa, desktop de entrada correspondente, janela
principal visível/foreground (ou seu diálogo do mesmo processo), WebEngine carregado
com quatro geometrias, duas revisões e backup/restauração reais. A captura copiou
pixels do desktop com GDI. A resolução original 1024×768 foi insuficiente; o driver
ofereceu 1920×1080, CDS_TEST e aplicação nativa retornaram sucesso, e o modo original
foi restaurado. Essa alteração foi restrita à bancada GitHub hospedada, sem modificar
SAC/Defender ou instalar driver/pacote no computador do usuário.

Downloads Azure dos artefatos foram negados por HTTP 403 neste workspace. Para
permitir revisão efetiva, cópias exatas foram preservadas pelo workflow somente na
branch do PR #11 e obtidas por Git. Hashes conferem; não houve alteração dos pixels.
O GitHub/ZIP continua sendo a forma de download pelo usuário, com login se necessário.

## Correções motivadas pela captura

O conjunto inicial `run-38569042216` é histórico e não é recomendado para listagem:
painel estreito cortava nomes e o diálogo de vértices herdava texto claro sobre fundo
branco, com Save/Cancel. O novo conjunto foi **recapturado** após correções reais de
QDialog/QSpinBox e dos textos Salvar/Cancelar/Fechar. O painel foi redimensionado por
seu QSplitter existente e o mapa deixou de citar um painel Objeto ausente no workspace
local. Não foi criada funcionalidade agrícola ou tela de histórico.

## Testes e limites

- Testes locais: 11 de fixture/persistência e recusa de Linux; depois, 14 focados na
  interface offline, desktop e captura. Ruff e verificação de diferenças passaram.
- CI do source revisado: Linux **127 passaram, 1 ignorado**; Windows **126 passaram,
  2 ignorados** (casos específicos da outra plataforma), além de integrações.
- Sessão gráfica foi verificada especificamente; o sucesso geral do CI não foi usado
  como substituto. Os quatro PNGs reais foram obtidos e examinados.
- Captura source de bancada não comprova instalação MSIX, assinatura, SAC, ausência
  completa de tráfego nativo, preservação em desinstalação ou aceitação pela Store.
  Conferir aparência no pacote final e resolver pendências anteriores antes de lançar.
- Não houve merge, submissão, publicação na Store ou mudança de proteções.
