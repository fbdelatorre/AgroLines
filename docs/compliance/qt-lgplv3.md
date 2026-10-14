# Qt/PySide6 Community — avaliação LGPLv3

**PENDENTE DE REVISÃO JURÍDICA**, com fontes/build ainda pendentes de fornecedor.
A preferência Community foi preservada; nenhum contrato comprado ou licença adotada.

## Módulos presentes, não apenas importações Python

Imports próprios: Core, Gui, Widgets, Svg, WebChannel, WebEngineCore e WebEngineWidgets.
O grafo PE retém Network, OpenGL, PrintSupport, Positioning, SerialPort, Qml,
QmlMeta/Models/WorkerScript, Quick/QuickWidgets, PDF, plugins e renderizador software.
[Inventário](inventory.json) relaciona cada DLL e importador real; diretórios externos
QML, depuradores QML e seis famílias GPL/comercial dispensáveis foram removidos na
referência, com guard existente preservado. QML/Quick transitivos não viram GPL
apenas por serem transitivos, nem LGPL por metadata do wheel.

Cabeçalhos oficiais versionados em [evidence/module-license-headers.json](evidence/module-license-headers.json)
demonstram alternativa LGPL para os trechos examinados de PySide, Shiboken, Qt Base,
Gui, Widgets, Network, OpenGL, PrintSupport, Declarative, Svg, WebChannel, Positioning,
SerialPort e ImageFormats. Não substituem revisão de todos os arquivos incorporados.
As cópias MSVC contidas nos wheels Qt são Microsoft, não código LGPL do Qt.
Qt WebEngine 6.140.0/Chromium 140.0.7339.225 e PDF exigem correspondência específica;
o texto de uma branch `dev` ou uma tag RC não comprova a licença do binário final.

## Obrigações que o modelo precisa atender

Texto LGPLv3 §4 permite Combined Work proprietário **sob condições**, não impõe
abertura universal de todo o código independente. Avaliar: aviso proeminente de uso
LGPL; LGPLv3 + GPLv3 integrais; atribuições específicas e fontes correspondentes;
marcação de alterações; termos que permitam modificação das partes LGPL e engenharia
reversa para depurar essas modificações; e §4(d)(0) ou §4(d)(1).

- §4(d)(1): mecanismo compartilhado adequado deve operar com versão modificada
  compatível com a interface. DLL separada num MSIX não prova isso.
- §4(d)(0): Minimal Corresponding Source + Corresponding Application Code em forma
  adequada para recombinação/relinking com versão modificada. O material pode incluir
  objetos/bytecode/outros arquivos utilizáveis; sua suficiência e impacto no sigilo
  precisam de avaliação antes de autorizar disponibilização.
- §4(e): Installation Information se/quando exigida por GPLv3 §6, com análise de
  User Product, operação e materiais necessários. Não concluir automaticamente
  que sempre é preciso entregar a chave privada, nem que assinatura elimina o dever.

[Alternativas e provas](relinking-msix.md) separam a demonstração Linux sintética
real de qualquer alegação sobre MSIX/Store/SAC. A política de integridade do release
não deve virar DRM contra exercício legítimo dos direitos LGPL. Um mecanismo futuro
não poderá invalidar a licença do AgroLines somente pela modificação compatível de
uma biblioteca quando isso impedir direitos assegurados; requisitos legítimos de
confiança do Windows continuam aplicáveis e não devem ser contornados.

## Community versus Commercial

Fechar/comercializar o código próprio **não é, isoladamente, motivo técnico para
comprar Qt Commercial**. Community só é alternativa de distribuição quando todos
os deveres aplicáveis forem cumpridos e a rota de substituição/recombinação for
realmente viável para a cópia entregue. Hoje isso não foi comprovado no MSIX.
Se nenhuma rota compatível for demonstrada, a distribuição desse candidato fica
bloqueada; avaliar contrato Commercial ou outra arquitetura mediante autorização,
sem reescrever o motor nesta tarefa.

A documentação comercial Qt/PySide anteriormente consultada descreve builds/wheels
comerciais via conta/instalador/qtpip. Não comprova que um contrato novo cubra
retroativamente este projeto iniciado em Community. Solicitar resposta escrita Qt:
projeto existente e histórico público, módulos/versões/WebEngine, migração, cobertura
de desenvolvedor e CI, redistribuição/atualizações após término e preço para pessoa
física no Brasil. Nenhuma resposta, licença ou elegibilidade contratual foi inventada.
Commercial não resolve LGPL GEOS/libiconv, avisos Chromium/codecs ou SAC de terceiros.
