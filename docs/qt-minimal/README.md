# Candidato Qt reduzido — em validação técnica

Continuação do PR #14, sem merge, publicação, assinatura ou aprovação jurídica.
A auditoria original permanece em `docs/native-store-audit/`.

Remoção delimitada a Charts, Graphs, Data Visualization, Quick 3D, Virtual Keyboard e Quick Timeline: nenhum import direto no produto, plugins introduzidos por descoberta global de QML/platforminputcontexts. Hooks locais preservam análise transitiva upstream, eliminam essas famílias antes da expansão de dependências; qualquer PE mantido que importe uma família excluída bloqueia o build. Qt3D legado, ShaderTools, estilos, imagens, plataforma, impressão e recursos WebEngine permanecem conservadoramente. Ausência no polling não autoriza remoção.

A política lista as remoções exatas e seus hashes antigos; não libera assinatura de terceiros, roots ou distribuição. As métricas definitivas dependerão da execução Windows desta revisão.

Evidências por execução: `evidence/qt-minimal/build-inputs.json`, `source-metadata.json`, `native-current.json`, `loads/loads.json`; inventários/AuthentiCode/SignTool em `evidence/signing/` e `evidence/native-signatures.json`. Correspondência com fonte local de build não equivale a procedência comprovada em input oficial fixado.

## Redução incremental e falha explícita

Execução intermediária [38638929735](https://github.com/fbdelatorre/AgroLines/actions/runs/38638929735), commit `39e5df6`: 396 PE, 318 assinaturas aceitas, 78 unsigned, 46 origens não fixadas. Os dois builds reproduziram os bytes. O gate **falhou corretamente** pelas remoções adicionais `Qt6OpenGLWidgets.dll` e `Qt6SpatialAudio.dll`, dependentes dos grupos removidos; nenhum MSIX foi promovido. Revisão seguinte registra essas remoções, mantendo bibliotecas de OpenGL/Quick efetivamente requeridas e bloqueando imports PE para as famílias proibidas.

A revisão seguinte testa a ausência da árvore **externa** `PySide6/qml`:
Widgets/`QWebEngineView` e mapa HTML não têm interface QML do aplicativo, assets
`.qml` nem imports diretos de QtQml/Quick/QuickWidgets. A análise upstream de
bibliotecas nativas, plugins e traduções continua; QtQuick/QtQml nativos exigidos
pelo WebEngine não são excluídos. `assert_widget_deployment` exige revisão se
uma futura interface QML for introduzida. A compatibilidade só será afirmada
após probes congelados das funcionalidades reais; não se usa ausência no polling
como justificativa. Plugins de plataforma/imagem/SVG/estilo/impressão permanecem.

## Os 46 inputs incidentais

`proveniencia-46.json` guarda hash/arquitetura/assinatura/versão, fonte de build,
metadados e correspondência exata dos **46** arquivos. Todos foram encontrados
com o mesmo SHA do payload: 44 em Temurin/JDK `17.0.20-101`, dois OpenSSL 3.5.5
em MySQL Server 8.0 do runner. Isso prova a cópia local de origem, **não** a
correspondência com um instalador oficial fixado nem direitos para redistribuir
MySQL/JDK como um todo. Não se atribui licença Oracle/Microsoft/OpenSSL apenas pelo
assinante do arquivo.

A implantação passa a excluir somente as **44 cópias Windows exatas** revisadas
em `retired-system-copies.json`, com recusa de novos hashes. O mínimo Windows 11
já fornece UCRT/API contracts; a Microsoft diz que o UCRT do sistema sempre é
utilizado no Windows 10/11 e desaconselha implantação local:
[Universal CRT deployment](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment?view=msvc-170).
Não se retiram VCRUNTIME/MSVCP necessários nem bibliotecas GIS.

O hook QtNetwork mantém sua análise nativa e o backend Schannel do Windows,
retira apenas o provider OpenSSL Qt não utilizado pela aplicação offline e deixa
de invocar `collect_qtnetwork_files()`, cuja descoberta buscou DLLs no PATH do
MySQL. O OpenSSL do Python e as cópias vendorizadas fixadas de GIS permanecem.
Não há troca do mecanismo de confiança do Windows nem carregamento alternativo.
A aceitação em Windows 11 limpo continua pendente mesmo com testes no runner.

## Gates independentes

Resolver a origem não aprova licenças nem autoriza envio. A política mantém
`release_reviews` (licenciamento, mecanismo LGPL, privacidade e autorização de
envio) todos `approved=false`, sem evidências inventadas. O gate de homologação
privada exige revisão explícita com evidências, além da proveniência e dos
controles protegidos já existentes. CI nunca aprova estes itens.

A medição seguinte [38640766301](https://github.com/fbdelatorre/AgroLines/actions/runs/38640766301),
commit `4ced81b`, encontrou **191 PE** (113 aceitos, 78 unsigned), **zero origem
pendente no payload**, 190 correspondências exatas de fonte de build e 811
arquivos totais. Houve 262 remoções perante o original: 216 Qt e 46 inputs
incidentais. Essa execução não concluiu os gates/probes nem gerou MSIX aprovado;
a saída de diagnóstico em grupo/linha agregada foi substituída por registros por
arquivo para manter os erros visíveis. A política foi então revisada caminho a
caminho contra os hashes originais; nenhuma remoção GIS ou alteração de PE de
terceiro foi aprovada. `remocoes-revisadas.csv` preserva todas as justificativas.
Uma cópia `ucrtbase.dll` removida havia sido observada originalmente: a justificativa
é a implantação UCRT fornecida pelo Windows 11, não ausência de observação.
Os probes de regressão do candidato final continuam sendo condição obrigatória.

A política correspondente é incorporada como `native-signing-policy.json` no
payload e validada por hash antes de assinatura. Os três textos GNU também são
verificados dentro do archive. Nenhum texto legal de privacidade foi alterado.
O workflow passa a executar builds automáticos de branch por PR, push apenas em
main, mantendo o dispatch manual, para evitar dois builds da mesma alteração.
A compilação dupla no mesmo job é intencional: prova reprodução dos bytes neste
builder/epoch, não reprodutibilidade independente entre máquinas.

## Perfil final e critérios de classificação

A política revisada passa a listar **179 caminhos PE esperados**: exclui também
os 12 plugins `qmltooling/qmldbg_*` de debug, profiler e transporte. A aplicação
Widgets/WebEngine release não habilita uma interface de depuração QML, não tem
assets/imports QML próprios e não fornece essa função ao cliente. A contagem real
e a execução desse perfil devem corresponder no gate; não é ajuste automático
ao que o CI encontrar. QtQuick/QtQml nativos e `opengl32sw.dll` continuam: o último
é um fallback dinâmico de renderização, mesmo sem import PE direto ou observação.

| Classificação | Componentes / evidência | Decisão |
|---|---|---|
| Necessário e observado | Core/Gui/Widgets/Svg, bindings e módulos nativos usados pelo mapa; fases por arquivo no inventário atual | Manter |
| Necessário por dependência comprovada | QtNetwork/OpenGL/PrintSupport/Qml/Quick/QuickWidgets/WebChannel/Positioning; imports PE e hooks upstream preservados, incluindo helper/recursos WebEngine | Manter a análise transitiva e os arquivos requeridos |
| Potencialmente necessário em configuração não exercitada | Plugins Windows, estilos, imagens/SVG/PDF, impressão, Schannel, provedores Positioning/SerialPort e fallback OpenGL | Manter conservadoramente; alguns respondem a escolhas de plataforma/dispositivo |
| Dispensável com evidência | Seis famílias listadas, árvore QML externa sem consumidor, seus dependentes sem raiz de uso e ferramentas de debug QML não habilitadas | Remoção revisada por hash; guards impedem retorno em Python, PE, plugins, QML/dados e archive |
| Indeterminado para licenciamento/substituição | Fontes/build/notices de WebEngine/Chromium/terceiros, mecanismo LGPL e direitos Microsoft | Bloquear promoção; não excluir bibliotecas GIS ou atribuir licença por nome |

O teste normal de janela da execução `38642374311` atingiu o corte antigo de
15 segundos; o processo foi encerrado pelo observador, não se constatou crash de
GIS. Os dois probes com término próprio saíram zero (mapa, precisão, cinco formatos,
edição e backup). Relatórios foram reutilizados **sem recompilar/instalar/executar
o pacote**, em `38643840250`, para diagnosticar o bloqueio. A correção atualiza
`Process.MainWindowHandle` via `Refresh()` e usa o deadline global já existente
de 120 segundos, com seis segundos após janela AgroLines visível antes de pedir
fechamento. Exige HWND observado, fechamento solicitado e saída zero; qualquer erro
de módulos, timeout, helper ausente ou runtime externo não aceito continua fatal.
Isso corrige a observação de abertura assíncrona e não aprova SAC/UI física.

O workflow `native-store-audit.yml` agora mantém a reauditoria original e a leitura
de JSONs de um candidato existente como modos manuais separados. O baseline
original foi revalidado em `38642366564` sem alteração de seus bytes. A cadeia
automática corrente audita o payload atual, reutilizando os hashes históricos.
O coletor por arquivo substitui linhas agregadas extensas por NDJSON legível.

O candidato final entrega `evidence/README.md` e `technical-summary.json` gerados
de XML de testes Windows da mesma execução, inventário, probes e binding real.
Esse é o relatório por artefato: nome/SHA/commit/versões/contagens e bloqueios
reais, sem inferir aprovação Linux, LGPL, assinatura de produção ou SAC. A
suíte Linux fica na execução Qualidade correspondente; o PR registra seus links
e resultados após conclusão. Não atualizar a política com uma suposta aprovação
só porque um build técnico passou.
