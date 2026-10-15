# Solicitações prontas, não enviadas

Fornecer a referência do README e as linhas por arquivo de inventory.json, sem
projetos, dados pessoais, chaves ou fonte própria. Solicitações técnicas não adotam
licença comercial, compram produto ou autorizam publicação. Envio depende do canal
legítimo do responsável; nenhum e-mail foi enviado.

## Qt / PySide Community

Identificar wheels 6.12.0 (WebEngine/PDF 6.12.0.140), runtime WebEngine 6.140.0 e
Chromium 140.0.7339.225. Solicitar fontes correspondentes, módulos e submódulos,
commits/patches/scripts/configure flags, SBOM e notices/copyrights do build Windows
x64, incluindo Qt Quick/QML, codecs/fontes e opengl32sw.dll. Solicitar os resultados
**do mesmo build** de `generate_chromium_attributions` (chromium_attributions.qdoc)
e `generate_pdf_attributions` (pdf_attributions.qdoc), além das licenças de terceiros
necessárias à redistribuição e fontes aplicáveis. Esses alvos foram identificados
no CMake oficial; não são arquivos que conseguimos obter do wheel por metadata.

A tentativa Windows `chrome://credits` com as 70 PE Qt conferidas por hash falhou.
Isso não é crédito cumprido. O teste upstream da branch 6.140 também marca essa
rota como não suportada; não presumir que `chrome://qt` (versões/linha de comando)
forneça os avisos. Ver evidence/credits-investigation.json. Não coletar linha de
comando/ambiente de usuário real para tentar substituir o material jurídico.

Solicitar orientação técnica documentada sobre substituição/recombinação Community
com MSIX/Store, sem pedir aprovação jurídica genérica ou a chave privada de assinatura.
Se Commercial vier a ser avaliado: pedir resposta contratual escrita sobre migração
**deste projeto iniciado Community**, histórico e artefatos públicos anteriores,
versões/módulos/desenvolvedor/CI, distribuição/atualizações e orçamento. Não existe
resposta contratual comprovada nem compra autorizada.

## Fiona / wheel GIS Windows

Wheel 1.10.1 SHA `41cde2c52c614457e9094ea44b0d30483540789e62fe0fa758c2a2963e980817`.
Pedir SBOM do build, `installed/*/share/*/copyright` e licenças/notices, baseline/ports
vcpkg, patches e receitas com hashes dos SPDX distribuídos. Especificar GEOS 3.11.3,
libiconv 1.17, FreeXL 2.0.0, SpatiaLite 5.1.0 e SZIP: alternativa de licença escolhida,
fontes/modificações e configuração de encoder quando pertinente. GDAL MIT não licencia
por si todos os drivers. Não pedir remoção de DLLs necessárias sem regressão.

## Shapely / pyproj / NumPy

Shapely 2.2.0 com GEOS 3.14.1: fontes/build/patches/delvewheel, attributions e scripts.
pyproj 3.8.0/PROJ 9.8.1: mesmos materiais e licença/versão das bases/dados realmente
incluídos. NumPy 2.5.4: fonte/configuração OpenBLAS 0.3.34.106.0 declarada no wheel,
LAPACK e runtime GCC estático; condições da GCC Runtime Library Exception e fontes
quando exigidas, sem impor GPL ao código independente por presunção. Pedir direitos
e termos MSVC dos arquivos empacotados, preservando assinaturas de origem.

## Microsoft

Conferir acordo efetivamente aceito na conta e licença padrão/customizada aos usuários;
compatibilidade dos direitos LGPL com o fluxo MSIX, sem presumir aprovação. Pedir
esclarecimento §10.14 sobre conta Individual/nome de publicador informado e capacidades
runFullTrust/unvirtualizedResources. Não alterar identidade ou conta automaticamente.
Avaliar Store signing/catalog e confiança das DLL/PYD sem inferir SAC de assinatura
do envelope. Autorizar qualquer submissão e teste de distribuição separadamente.
