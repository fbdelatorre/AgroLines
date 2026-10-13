# Validação visual — Etapa 2.1

O CI `windows-visual` abre a interface com o plugin Qt `windows`, fonte Segoe UI,
dados sintéticos e API isolada. Captura a janela nativa com `QScreen.grabWindow`
em escalas 100%, 125% e 150%, sem fallback offscreen. Captura indisponível ou vazia
falha o job. Cada artefato contém 15 telas PNG e um manifesto com plataforma,
resolução lógica/física, fonte e escala. Revisar as imagens é necessário: o job
não julga contraste, legibilidade ou organização sozinho.

Para reproduzir no Windows com as dependências de desenvolvimento instaladas:

```powershell
.\.venv\Scripts\python.exe -m scripts.render_desktop --scale 1 --output visual-windows
.\.venv\Scripts\python.exe -m scripts.render_desktop --scale 1.25 --output visual-windows-125
.\.venv\Scripts\python.exe -m scripts.render_desktop --scale 1.5 --output visual-windows-150
```

As capturas cobrem login, validação junto ao campo, propriedades/safras/operações,
permissões, convites recebidos/enviados, etapas de compartilhamento, consulta de
acesso compartilhado janela compacta e estrutura cartográfica com painéis abertos/recolhidos. Os dados vivem apenas em SQLite de teste;
não há conexão ao banco do usuário, gravação de tokens ou migração nesse roteiro.

Conferir texto completo, acentos, contraste, seleção de seção, botões contextuais,
rolagem de conteúdo em janelas pequenas e ausência de sobreposição. Na estação
Windows 11, complementar com o checklist funcional do README e troca real de DPI
entre monitores, escala de acessibilidade, navegação por teclado e redimensionamento.
Capturas de runner Windows não substituem essa conferência do hardware do usuário.

`--reference` permite gerar imagens Linux/offscreen somente para ajustes locais.
O manifesto identifica essas imagens como referências; elas não validam aparência
Windows. Os testes pytest offscreen verificam callbacks e regras funcionais.

## Referência de identidade visual

A imagem fornecida pelo usuário orienta as cores, bordas, tipografia, menu, barra
superior e distribuição dos painéis. A seção **Mapa** oferece a estrutura visual
com área central substituível, painéis de **Camadas**, **Parâmetros** e
**Informações da propriedade**. Não renderiza a fotografia de referência como mapa.
Ferramentas e parâmetros GIS são desabilitados e marcados como etapa futura, sem
coordenadas, métricas, imagens licenciadas ou geometrias fictícias.

Arraste os separadores para redimensionar e os títulos para reposicionar os painéis;
use o X ou os ícones da barra superior para recolher/reabrir. Em janelas com menos
de 1050 pixels lógicos, os painéis começam recolhidos e podem ser abertos um a um.
As escolhas de visibilidade em resolução ampla e compacta são independentes,
lembradas durante a sessão. A opção **Recolher menu** amplia a área útil.
Formulários continuam ocupando a área central inteira ao navegar para cadastros.

A barra superior seleciona propriedades realmente autorizadas; o painel inferior
mostra perfis/escopos reais e abre o cadastro ou consulta correspondente. Logout,
expiração e revalidação limpam esse contexto junto com as telas existentes.
Não há chamadas de mapas, provedores de imagens ou cálculos em segundo plano.
