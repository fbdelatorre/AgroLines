# Substituição nativa no AgroLines completo

Laboratório autorizado Windows Server descartável, sem instalar AgroLines,
certificados ou modificar proteções. Reutiliza byte a byte o executável e payload
do PR #18, conferido pelo manifesto fixado no script. Não reconstrói o produto.

Para cada Qt Base 6.12.0, GEOS 3.11.3 (Fiona) e GEOS 3.14.1 (Shapely), confere
fontes upstream por commit e hash do arquivo já auditado, compila original e
variante com string de versão marcada e substitui apenas DLLs em cópias isoladas.
GEOS preserva os nomes delvewheel via OUTPUT_NAME no CMake; não altera importadores
do AgroLines. Verifica exports necessários antes de carregar as variantes.

O mesmo executável congelado abre a GUI, executa smoke/precisão e o probe offline
completo. Instrumentação 0BSD acrescentada somente ao pacote LGPL Python PySide6
enumera módulos realmente carregados no próprio processo e consulta GEOSversion
nos handles existentes, sem LoadLibrary de outra cópia. Registra caminhos, hashes,
versões e erros. Nenhuma função de cálculo é alterada. O mecanismo de substituição
é a árvore onedir; a instrumentação serve somente para produzir evidências.

Uso de mantenedor em shell MSVC x64: `python tools/standalone-native-lab/run.py
--component geos-3.14.1 --payload <payload-verificado-PR18> --work <pasta-nova>`.
O guard recusa execução fora do builder autorizado; não usar para contornar SAC.

Fontes/receitas upstream reconstruídas não são declaradas correspondência exata
dos wheels dos fornecedores. Êxito é compatibilidade demonstrada nas operações
exercitadas, não prova jurídica, estabilidade universal ou homologação SAC.
Qt Core não representa reconstrução de todos os módulos Qt/WebEngine.

Código novo deste laboratório: SPDX-License-Identifier: 0BSD, nos mesmos termos
de `../windows-lgpl-lab/LICENSE.txt`. Artefatos contêm somente evidências e patches;
não redistribuem código próprio AgroLines nem DLLs experimentais.
