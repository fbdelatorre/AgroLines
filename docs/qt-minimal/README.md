# Candidato Qt reduzido — em validação técnica

Continuação do PR #14, sem merge, publicação, assinatura ou aprovação jurídica.
A auditoria original permanece em `docs/native-store-audit/`.

Remoção delimitada a Charts, Graphs, Data Visualization, Quick 3D, Virtual Keyboard e Quick Timeline: nenhum import direto no produto, plugins introduzidos por descoberta global de QML/platforminputcontexts. Hooks locais preservam análise transitiva upstream, eliminam essas famílias antes da expansão de dependências; qualquer PE mantido que importe uma família excluída bloqueia o build. Qt3D legado, ShaderTools, estilos, imagens, plataforma, impressão e recursos WebEngine permanecem conservadoramente. Ausência no polling não autoriza remoção.

A política lista as remoções exatas e seus hashes antigos; não libera assinatura de terceiros, roots ou distribuição. As métricas definitivas dependerão da execução Windows desta revisão.

Evidências por execução: `evidence/qt-minimal/build-inputs.json`, `source-metadata.json`, `native-current.json`, `loads/loads.json`; inventários/AuthentiCode/SignTool em `evidence/signing/` e `evidence/native-signatures.json`. Correspondência com fonte local de build não equivale a procedência comprovada em input oficial fixado.
