# Capturas da listagem pt-BR — edição Store offline

Base funcional: PR #10 e suas dependências #6–#9. As ferramentas deste incremento
não alteram o motor geográfico ou projetos reais. A revisão visual motivou correções
mínimas reais de contraste de QDialog/QSpinBox, tradução dos botões Salvar/Cancelar/
Fechar e remoção de uma referência a painel Objeto ausente no workspace local.
São alterações do produto neste PR; novas capturas usam esse código atualizado.
Não há instalação de MSIX, submissão, publicação, merge ou mudança de segurança.

## As quatro imagens

| PNG | Conteúdo real | Limitações da interface atual |
|---|---|---|
| `01-tela-principal.png` | Projeto “Demonstração fictícia · Fazenda Horizonte”, quatro polígonos, mapa vetorial local, lista e toolbar | Limite é um polígono nomeado, não um cadastro hierárquico de propriedade. Sem satélite/curvas/algoritmos futuros |
| `02-camadas-importadas.png` | Lista de objetos importados de GeoJSON, SHP e GPKG; talhão selecionado e destacado pelo componente real do mapa | Não inventar árvore de grupos, painéis GIS ou exportação ainda não disponíveis |
| `03-edicao-de-vertices.png` | Diálogo real “Vértices · coordenadas métricas”, campos Leste/Norte, Aplicar/Desfazer/Refazer/Salvar | Não sobrepor controles desenhados nem afirmar edição gráfica por arraste se não implementada |
| `04-projetos-e-backups.png` | Diálogo existente “Abrir projeto”, mostrando arquivos locais de demonstração, backup e restauração | Não há navegador de histórico. A lista principal mostra a revisão corrente; as duas revisões e cópias são comprovadas no projeto/evidência |

Dados são retângulos matemáticos em EPSG:32723. Não provêm de clientes, propriedades,
imagens de satélite ou contas reais. Arquivos importados, revisão após edição de
1 mm, backup e restauração são operações do código vigente, não respostas simuladas.

## Captura automática real — desenvolvedor/bancada

Em Windows com desktop desbloqueado, monitor com pelo menos 1366×768 pixels reais
(preferir 1920×1080), ambiente de desenvolvimento já aprovado e checkout desta branch:

```text
python -m scripts.capture_store_windows --output store-capture-novo --revision COMMIT_REVISADO
```

Não instalar esse ambiente de desenvolvimento no computador do cliente como solução
de distribuição. Não instalar o candidato MSIX não assinado. Uma máquina com SAC
que bloqueie dependência deve permanecer protegida; registrar a falha e usar pacote
confiável quando disponível, sem exclusões ou desativação.

A ferramenta verifica sessão Windows ativa, desktop de entrada correspondente,
janela visível, processo em primeiro plano e limites reais do monitor. Espera o
Qt WebEngine/Leaflet carregar as quatro geometrias. Captura **pixels do desktop**
com Win32 GDI BitBlt/GetDIBits e apenas codifica o buffer em PNG. Não usa
`QWidget.grab`, render offscreen, imagem gerada, montagem ou aumento de resolução.

O diálogo de projetos é o seletor existente do Windows. Apenas sua pasta inicial
é dirigida à pasta sintética, equivalente a navegar até ela; não é substituído
por UI inventada. Capturas são realizadas dentro da área da janela fullscreen do
app, incluindo seus diálogos modais reais. Por padrão não altera a resolução do monitor. No workflow hospedado, a opção
`--configure-hosted-display` pode aplicar temporariamente 1920×1080 somente se o
driver enumerar esse modo e CDS_TEST aprovar; restaura o modo anterior ao concluir.
A opção é recusada fora de runner GitHub hospedado. Não instala driver, persiste
registro, cria display artificial ou aumenta resolução de PNG.

Se qualquer requisito falhar, o conjunto parcial é removido e nenhuma imagem é
entregue como captura Store. `capture-evidence.json` e README registram o motivo;
exit 2 significa indisponível, não validação visual aprovada. O diretório precisa
ser novo; dados ou capturas existentes nunca são sobrescritos.

## Execução GitHub Actions e download

Workflow: `.github/workflows/store-screenshots.yml`. Executa no push das ferramentas
ou manualmente quando o workflow estiver disponível no seletor Actions. A branch
não precisa ser incorporada à main para a execução por push. Não presumir que o
runner hospedado ofereça desktop interativo/resolução suficiente: ler a evidência.

Na página **Actions → Real Windows offline Store screenshots**, abrir a execução:

- `windows-store-capture-readiness`: evidência e README, inclusive quando indisponível.
- `agrolines-synthetic-local-projects`: projeto .agrolines, backup, arquivos fictícios
  e evidência de origem, úteis para captura manual sem Python no computador do usuário.
- `agrolines-offline-real-windows-screenshots-REVIEW-REQUIRED`: somente se as quatro
  capturas reais concluírem e passarem nas verificações técnicas. Contém PNGs e evidência.

Baixar o ZIP clicando no artefato (pode exigir login GitHub). Em sucesso, a execução
também preserva os PNGs e evidências em `captures/run-ID` nesta branch de screenshots.
Somente esta branch pode receber os arquivos; nunca main ou outra branch/PR.
Esse caminho permite baixar por Git/GitHub mesmo quando a origem Azure de artefatos
está inacessível ao ambiente. São cópias exatas, com os mesmos hashes, para revisão. O aviso de captura
indisponível permite concluir o workflow e entregar o diagnóstico; **workflow verde
não significa que houve quatro screenshots**. Conferir `completed=true`, quatro
nomes e hashes na evidência, além da revisão humana abaixo.

## Alternativa manual segura — Windows com interface gráfica

1. Utilizar uma versão offline confiável, já instalada por fluxo autorizado. Não
   usar MSIX não assinado, certificado autoassinado, Developer Mode ou bypass. Se
   o pacote confiável ainda não estiver disponível, a captura oficial fica pendente.
2. Baixar o artefato sintético e extrair para uma pasta local de demonstração nova.
   Abrir `Demonstracao-ficticia.agrolines` no AgroLines; não abrir projetos reais.
3. Em Windows preferencialmente pt-BR, usar monitor 1920×1080, fechar terminais,
   depuradores, notificações e janelas de outros programas. Ajustar a janela por
   controles normais, mantendo a área capturada no mínimo 1366×768.
4. Capturar a janela real com a Ferramenta de Captura do Windows, salvar PNG:
   tela principal; camadas/seleção; diálogo de vértices; abertura de projetos/backup.
   Não incluir a própria ferramenta na captura; não adicionar elementos à imagem.
5. Para o terceiro estado, selecionar Talhão 01, clicar Editar vértices e mostrar
   coordenadas. Para comprovar versão seguinte, alterar 1 mm, Aplicar e Salvar.
6. Gerar Backup e Restaurar em arquivo novo pelos controles existentes. Abrir o
   seletor de projetos na pasta sintética para a quarta imagem. Não inventar uma
   tela de histórico. Registrar qual operação e arquivo apareceram em cada PNG.
7. Verificar dimensões/tamanho em Propriedades, revisar os quatro PNGs e registrar
   versão/commit do pacote, data, processo em execução e método. Evidências de SAC
   são separadas: screenshots não aprovam compatibilidade ou preservação em uninstall.
8. Compartilhar somente imagens e evidências revisadas, sem dados privados. Não
   colocar nomes de usuário, caminhos pessoais ou projetos reais nos artefatos.

## Requisitos Microsoft Store e revisão

Fonte oficial consultada em 14/10/2026: [App screenshots, images, and trailers for
MSIX app](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/screenshots-and-images).
Para Desktop, PNG, 1366×768 ou maior (suporte 4K), até 50 MB por imagem. Nosso limite
é estritamente inferior a 50.000.000 bytes. Cada evidência registra formato/método,
resolução, bytes e SHA-256. Não inserir logos, ícones ou mensagens de marketing extras.
A orientação oficial recomenda conteúdo crítico nos dois terços superiores;
legendas podem cobrir o terço inferior. Legendas sugeridas na tabela têm até 200
caracteres quando resumidas para o campo correspondente, não sobrepostas aos PNGs.

Antes de considerar oficiais, revisar cada imagem em tamanho real:

- App/diálogo legíveis, sem carregamento pendente, erro, terminal ou depurador;
- Nenhum recurso online disponível, dado real ou painel inventado;
- Interface portuguesa; diálogo nativo depende do idioma Windows. Se o runner usar
  inglês no seletor, preferir nova captura em Windows pt-BR para uniformidade;
- Nenhum recorte, cursor/tooltip/aviso indesejado ou janela sobreposta de outro app;
- Dimensões mínimas, PNG e limite de tamanho, sem upscale ou reconstrução;
- Funcionalidades correspondem ao pacote que será distribuído, não apenas a uma
  execução source de bancada. Repetir no pacote final se aparência mudar.

Capturas source demonstram a interface vigente em execução Windows, mas não atestam
instalação pela Store, assinatura, SAC, aceitação da listagem ou publicação. A política
privacidade e demais pendências do PR #9/#10 continuam independentes deste material.
