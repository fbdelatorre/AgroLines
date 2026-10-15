# Qt Windows — escopo e evidências

Complementa o experimento Linux do PR #15; não o repete nem modifica o candidato.
O resultado Windows e links da execução são registrados em `validation-results.json`
e na seção de resultados abaixo após a conclusão. Não confundir Qt Core sintético
com todo Qt/PySide/WebEngine, AgroLines recomposto ou MSIX confiável.

## Componentes reais necessários no candidato

`reference-components.json` contém **70 PE da família de empacotamento Qt**,
incluindo CRT Microsoft (estes não são licenciados automaticamente como Qt),
**40 observados** nas três fases do candidato. Cada linha tem hash, origem, versão,
importadores e fases de carregamento reais. A observação usa amostragem de módulos;
ausência na amostra não autoriza remover dependência.

| Camada | Componentes preservados e motivo |
| --- | --- |
| Imports diretos desktop | QtCore, QtGui, QtWidgets, QtSvg, QtWebChannel, QtWebEngineCore e QtWebEngineWidgets |
| Qt Base transitivo | Network, OpenGL, PrintSupport, bibliotecas de suporte e opengl32sw; CRT Microsoft separado |
| Qt WebEngine/PDF | WebEngineCore/Widgets, QtWebEngineProcess, PDF, recursos/translations do payload; versões do wheel e runtime são distintas |
| Declarative / Quick | Qml, QmlMeta, QmlModels, QmlWorkerScript, Quick, QuickWidgets e pyside6qml; transitivos WebEngine, sem tela QML própria |
| Outros transitivos | Positioning e SerialPort, suas extensões/plugins preservados; SVG/WebChannel necessários |
| Binding | pyside6.abi3.dll, pyside6qml.abi3.dll, extensões Qt*.pyd; shiboken6.abi3.dll e Shiboken.pyd |
| Plugins observados | platforms/qwindows.dll, styles/qmodernwindowsstyle.dll, imageformats/qico.dll |
| Plugins presentes não observados na amostra | generic/qtuiotouchplugin; iconengines/qsvgicon; demais imageformats; networkinformation/qnetworklistmanager; platforms/qdirect2d,qminimal,qoffscreen; position/nmea,positionpoll,winrt; tls/qcertonlybackend,qschannelbackend. Paths/hashes exatos no JSON. |

Sem novas famílias Charts, Graphs, DataVisualization, Quick3D, VirtualKeyboard ou
QuickTimeline. Recursos QML externos dispensados não foram reintroduzidos; manter
as DLLs QML transitivas não significa usar interface QML própria.

## Ensaio reproduzível

`tools/windows-lgpl-lab/run.py --component qtbase-6.12.0 --work <pasta-nova>` em
shell MSVC x64. Workflow `windows-lgpl-lab.yml` executa no Windows hospedado.
Fontes QtBase oficiais commit `025bdad181de241e81bf853c8a2d7bf3d19261a9`,
SHA-256 do arquivo Git `e5317b2dfaf4cc2769be0cc8267fd9b209020fbb94a20b33da95f0e7df33bce4`
conferido contra o índice anterior. Clone/checkout/arquivo usam conversão LF e
umask explícita; o esperado não foi trocado para fazer o teste passar.

Compila Core compartilhado Release; guarda a DLL original. Consumidor C++ sintético
0BSD executa QString `talhao-sintetico` (16 caracteres) e qVersion. Marca apenas o
retorno qVersion com `-agrolines-synthetic`, recompila Core e executa o mesmo EXE
em outra pasta de laboratório. Registra GetModuleFileNameW da Qt6Core.dll efetiva,
hash por fase, PE x64, resultado funcional, versão, patch e CMakeCache. O consumidor
é byte a byte o mesmo nas duas pastas; nenhum código AgroLines é necessário.

Essa QtCore compilada tem configuração de laboratório. Coincidir a versão 6.12.0
não a torna cópia exata do wheel nem comprova ABI com todo PySide6/WebEngine. Não
se recompilaram módulos adicionais sem as fontes/configurações exatas; U01/U02
tratam essas lacunas. O ensaio Windows não instala MSIX, não assina, não modifica
WindowsApps e não contorna código bloqueado por SAC/Defender.

## Níveis de conclusão

- Consumidor QtCore independente em Windows: ver resultado registrado da execução.
- Qt/PySide/WebEngine completo modificado: **NÃO DEMONSTRADO**.
- Recombinação AgroLines/PyInstaller: **NÃO DEMONSTRADO**.
- Pacote MSIX confiável com substituição: **BLOQUEADO POR REQUISITO EXTERNO**;
  não há cópia legitimamente entregue pela Store autorizada para o teste.
- Cumprimento LGPL: **PENDENTE DE REVISÃO JURÍDICA** e fechamento U01/U02;
  experimento sintético não é aprovação.

## Histórico das correções do laboratório

As falhas anteriores permanecem no GitHub: geração de arquivo Git com conversões
de host diferentes (opções agora explícitas, checksum esperado preservado); ferramenta
windeployqt dependente de Network no configure Core-only (desativada apenas no lab);
consumidor MSVC exigindo `/Zc:__cplusplus` e `/permissive-`, conforme
`src/corelib/global/qcompilerdetection.h` e `cmake/QtFlagHandlingHelpers.cmake`
do commit fixado. As duas opções estão explícitas. Não foram modificados headers,
asserções Qt ou critérios para ocultar as falhas.

## Resultado executado e arquivado

[Execução Windows aprovada](https://github.com/fbdelatorre/AgroLines/actions/runs/38664013105)
(commit `34a9793599e14bdd4fc8d6b7a5d267cb84bd507b`). Os três relatórios brutos
`lab-*.json` foram preservados byte a byte, com hashes conferidos contra a
captura dos artefatos e dados iguais aos logs. Ver
[validation-results.json](validation-results.json) e
[verificação](lab-evidence-verification.json).

**DEMONSTRADO NO WINDOWS / DEMONSTRADO SOMENTE EM CONSUMIDOR SINTÉTICO.**
O host foi **Windows Server 2025 Datacenter, build 26100, x64**. Estado SAC não
confirmado; serviço/antivírus Defender ativos, proteção em tempo real reportada
`false`. Nenhuma configuração foi alterada. Não é Windows 11 físico com SAC On.
Não usar este resultado como prova de integridade/instalação MSIX ou proteção ativa.

Qt6Core original `0532ec4cd6d66c355ff5dedfe870327e24db7beb296c5ec4c798d1c45358b559`;
modificada `3e7d3883a2a05dde1e036d302b27ea29dc7f212193cd8b08e9e589dc39e02a7f`.
Mesmo consumidor SHA-256
`a0159d9315c21364bc67e7032592e5002b96099204b82e924d39cb572f426507`,
QString length 16 nas duas fases; qVersion passou de `6.12.0` para
`6.12.0-agrolines-synthetic`; GetModuleFileNameW mostrou a pasta original/modificada
selecionada. Recombinação AgroLines e MSIX confiável continuam não demonstrados.
