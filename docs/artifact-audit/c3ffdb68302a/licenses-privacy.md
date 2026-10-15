# Licenças e privacidade: revisão do conteúdo efetivamente distribuído

## Licenças — evidências e obrigações ainda abertas

Foram conferidos os hashes dos **40 avisos indexados dentro do MSIX**. Estão presentes
os textos originais LGPL-2.1-only, LGPL-3.0-only e GPL-3.0-only no diretório reviewed-texts.
O índice packages.json lista 14 pacotes selecionados do runtime/bootloader e adverte
que metadata não cobre vendors. **151 documentos do dossiê não significam 151 textos
embutidos, nem completude de avisos/fontes.**

| Família efetiva | Análise e material exigido | Situação |
| --- | --- | --- |
| PySide6/Shiboken/Qt 6.12.0 | Conferir alternativa de licença por módulo/arquivo, copyright, LGPL3 + GPL3 originais, fontes exatas/patches/builds, direitos de modificação e depuração. QtCore, GUI/Widgets, WebEngine, WebChannel, SVG e transitivos/plugins precisam evidência própria. Ausência de famílias GPL-only dispensáveis foi registrada; não licencia automaticamente os binários restantes. | PENDENTE DE DOCUMENTAÇÃO / FORNECEDOR / REVISÃO JURÍDICA |
| Qt WebEngine/Chromium/PDFium/software OpenGL | Créditos, fontes/patches/flags exatos, inventário incorporado estaticamente/recursos/codecs. Licença do wrapper não cobre todo Chromium. Patentes/codecs não ficam liberados por metadata ou assinatura. | PENDENTE DE FORNECEDOR |
| GEOS 3.11.3 de Fiona e 3.14.1 de Shapely | Duas cópias (pares C/C++), fontes/builds correspondentes, LGPLv2.1 §§4–6, modificação e relinking/substituição analisados separadamente de LGPL3. Bindings permissivos não removem obrigações GEOS. | PENDENTE DE DOCUMENTAÇÃO / JURÍDICA; rota MSIX NÃO DEMONSTRADA |
| Fiona/GDAL 1.10.1/3.9.1 e vendors | BSD/MIT de camadas principais não cobre FreeXL, libiconv, SpatiaLite, SZIP, OpenSSL, codecs/drivers. Conferir variantes, avisos, fontes e condições aplicáveis. Receita GDAL/SPDX é insumo, não prova de todas as fontes dos DLLs. | PENDENTE DE FORNECEDOR |
| pyproj/PROJ 3.8.0/9.8.1 | Avisos permissivos, dados/grids e respectivas licenças, fontes/builds e vendors. Não habilitar downloads para cumprir offline. | PENDENTE DE DOCUMENTAÇÃO |
| NumPy 2.5.4, OpenBLAS/LAPACK/runtime | BSD do NumPy não substitui avisos BLAS/LAPACK nem análise dos runtimes GCC e exceções efetivamente usadas. Não inferir GPL sem considerar a exceção aplicável. | PENDENTE DE DOCUMENTAÇÃO / FORNECEDOR |
| CPython 3.12.10, OpenSSL, libffi, SQLite | PSF e textos/atribuições próprios dos incorporados; SQLite público domínio não transforma todo runtime em domínio público. | Material existente; completude depende do mapa de vendors |
| PyInstaller bootloader | GPL com exceção de distribuição do bootloader: conferir termos e modificações reais. Não implica automaticamente GPL do código AgroLines. Ferramentas só de build não devem virar dependências distribuídas por engano. | Conferir escopo/avisos do bootloader |
| Leaflet local, certifi e outros puros | Avisos BSD/permissivos e MPL2 nos arquivos cobertos do certifi; não distribuir só um crédito genérico. | Avisos indexados verificados; completude documental separada |
| MSVC/UCRT | Assinatura Microsoft não concede licença REDIST. Confirmar origem e direitos nos termos efetivamente aplicáveis ao builder. | PENDENTE CONTRATUAL / DOCUMENTAÇÃO |

Fontes técnicas e textos já reunidos: [inventário](../../compliance/inventario-terceiros.md),
[fontes](../../compliance/fontes-correspondentes.md), [Qt](../../compliance/qt-lgplv3.md),
[GEOS](../../compliance/geos-lgplv21.md). No snapshot c3ffdb, gates licensing,
lgpl_mechanism, privacy_readiness e owner_submission permanecem não aprovados.

Evidências **posteriores** do PR #16: [experimentos Windows](../../compliance/windows-validation/README.md)
e [pendências precisas por fornecedor](../../compliance/windows-validation/missing-upstream-materials.md).
Qt modificado foi carregado por consumidor sintético; GEOS por consumidor sintético
e congelado. Isso não recompõe AgroLines, não garante ABI de todos os importadores,
nem demonstra substituição em pacote Store confiável.

MSIX protege WindowsApps e o envelope: DLL separada não é prova de substituibilidade.
Reempacotar requer outra rota legítima de assinatura/instalação, não reutilização da
assinatura Store. As alternativas A/B/C e materiais (objetos/bytecode/import libs,
fontes/build scripts/ABI) estão na [análise MSIX](../../compliance/windows-validation/msix-lgpl-analysis.md).
Não foram publicados materiais proprietários nem introduzida busca externa de DLL.
A EULA deve preservar direitos LGPL de modificação e engenharia reversa necessária
à depuração dessas modificações. PyInstaller não garante sigilo do código Python.

**Software proprietário pode ser compatível com LGPL sob condições; estas condições
não estão integralmente demonstradas para a cópia Store.** Não há evidência técnica
que torne obrigatória a compra imediata de Qt Commercial; também não há aprovação
Community automática. Uma contratação não resolveria GEOS, Chromium, confiança Windows
ou LGPD. Revisão jurídica e fechamento de materiais continuam necessários.

## Privacidade — cópias exatas, ainda não publicáveis

As políticas MD/HTML/TXT embutidas são byte a byte iguais às do commit auditado.
O verificador registra as quatro marcações CONFIRMAR em [audit.json](audit.json):

1. Data da primeira disponibilização efetiva, ainda não definida.
2. URL pública HTTPS estável testada sem login, ainda não publicada.
3. Bases legais documentadas por finalidade, sem termos adotados/legítimo interesse comprovados.
4. Mecanismos de transferência internacional aplicáveis a Gmail, Microsoft, GitHub e
   destinatários adicionais efetivamente identificados nos procedimentos.

O texto declara “NÃO PUBLICAR”; esta auditoria não o reescreve nem o aprova.
FABRICIO JOSE DELATORRE e fabricio.grupodelatorre@gmail.com correspondem às decisões
confirmadas. Os termos preveem programa inicial **18+** com declaração/aceite verificável,
sem coleta padrão de documento/data completa nem bloqueio etário no aplicativo.
Brasil Livre/IARC 3+/Microsoft 3+ são classificação do conteúdo, não elegibilidade do
programa; configurações Store não foram alteradas/verificadas na conta nesta auditoria.

Projetos SQLite, versões, originais e backups são locais e **não têm criptografia
própria AgroLines**. Importações podem incluir dados pessoais/metadados invisíveis;
histórico, cópias de backup e arquivos originais não desaparecem com uma edição.
Desinstalar não equivale a excluir arquivos externos do usuário. A exigência de
proteção de dados da Store (§10.5.4, conforme aplicabilidade) precisa avaliação;
mero aviso de ausência de criptografia não resolve a questão.

Não há promessa de telemetria própria, envio automático por Gmail ou colaboração
neste pacote offline. Suporte será voluntário e minimizado; Gmail pessoal gratuito
**ainda não começou a receber suporte**, acesso único foi informado pelo responsável,
não auditado na conta. Não se presume Workspace, DPA, encaminhamento, Drive ou países
específicos. Microsoft distribui/gerencia contas separadamente; uso de relatórios e
exportações Partner Center não foi confirmado. GitHub Pages permanece desativado.

Retenção proposta/manual: suporte até **90 dias após encerramento**; controle de
testadores durante participação + **30 dias após saída/fim**; pedidos de privacidade
**12 meses após conclusão**, com exceções concretas justificadas. Não são jobs de
exclusão implementados/testados, nem prazos dos projetos locais. Configurar Gmail/MFA,
aceite/registro mínimo privado, encerramento/revisões mensais, exclusão de anexos/cópias,
resposta a titulares/incidentes e revisão dos contratos/transferências antes do início.
Nenhum registro pessoal de testador deve ir para GitHub/artefato público.

Documentos prontos **para revisão**, não para publicação:
[política e anexos](../../privacy/offline/README.md),
[termo](../../privacy/offline/termo-participacao-minuta.md),
[plano mínimo](../../privacy/offline/plano-operacional-minimo.md),
[bases/fornecedores](../../privacy/offline/hipoteses-legais-e-fornecedores.md).
