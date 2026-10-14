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
