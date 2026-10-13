# Validação visual — Etapa 2.1

O CI `windows-visual` abre a interface com o plugin Qt `windows`, fonte Segoe UI,
dados sintéticos e API isolada. Captura a janela nativa com `QScreen.grabWindow`
em escalas 100%, 125% e 150%, sem fallback offscreen. Captura indisponível ou vazia
falha o job. Cada artefato contém 12 telas PNG e um manifesto com plataforma,
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
acesso compartilhado e janela compacta. Os dados vivem apenas em SQLite de teste;
não há conexão ao banco do usuário, gravação de tokens ou migração nesse roteiro.

Conferir texto completo, acentos, contraste, seleção de seção, botões contextuais,
rolagem de conteúdo em janelas pequenas e ausência de sobreposição. Na estação
Windows 11, complementar com o checklist funcional do README e troca real de DPI
entre monitores, escala de acessibilidade, navegação por teclado e redimensionamento.
Capturas de runner Windows não substituem essa conferência do hardware do usuário.

`--reference` permite gerar imagens Linux/offscreen somente para ajustes locais.
O manifesto identifica essas imagens como referências; elas não validam aparência
Windows. Os testes pytest offscreen verificam callbacks e regras funcionais.
