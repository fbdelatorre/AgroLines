# AgroLines standalone — bibliotecas livres, fontes e substituição

INSTRUÇÕES TÉCNICAS E MINUTA DE AVISOS. Não são aprovação jurídica nem oferta
completa de fontes dos componentes cujos materiais ainda estão identificados como
incompletos. Os direitos vêm das licenças originais em licenses/, não deste resumo.

## 1. Identifique sua versão

Conserve o instalador, seu hash e os arquivos legal-manifest.json,
THIRD_PARTY_NOTICES.txt, fontes-terceiros.json e o manifesto do payload da versão.
O inventário nativo associa caminho, versão evidenciada, componente e SHA-256 aos
arquivos realmente empacotados. Fontes upstream identificadas por commit ou
checksum não são declaradas reconstrução exata dos wheels quando faltam patches,
configuração ou componentes estáticos do fornecedor.

O mecanismo de distribuição é PyInstaller onedir: Python integrado, DLLs e PYDs
separados, fontes Python dos pacotes PySide6/Shiboken externas ao PYZ. Não é um
executável único e não incorpora código GPL do QGIS. Código próprio continua no
arquivo do aplicativo; isso não garante impossibilidade de extração de bytecode.

## 2. Direitos e avisos LGPL

Qt/PySide6/Shiboken inspecionados oferecem alternativa LGPLv3; seus componentes
embutidos têm termos próprios. GEOS é analisado separadamente sob LGPLv2.1.
libiconv, SpatiaLite e FreeXL têm suas próprias licenças/alternativas; não recebem
LGPLv3 por estarem no mesmo pacote. Verifique a licença da biblioteca e configuração.

A EULA proposta ressalva modificação/substituição de bibliotecas livres, engenharia
reversa necessária à depuração dessas modificações e demais direitos aplicáveis.
Não condiciona o exercício desses direitos a autorização discricionária ou compra
de Qt Commercial e não invalida licença legítima apenas por substituição permitida.
Os textos LGPL/GPL referenciados e copyrights devem acompanhar a distribuição.

As alternativas e a modalidade de disponibilização devem ser validadas juridicamente:
LGPLv3 §4(d)(1) para mecanismo compartilhado apropriado, §4(d)(0) para materiais de
recombinação quando aplicável, §4(e)/GPLv3 §6 para Installation Information quando
devida; LGPLv2.1 §6 para GEOS e demais componentes sob essa versão. Não transportar
automaticamente as obrigações de uma versão para outra.

## 3. Fontes e materiais já identificados

fontes-terceiros.json conserva versão, commit/URL exatos, SHA-256, origem e limites
de correspondência. origens-suplementares.json associa textos/receitas adicionais
aos componentes. As fontes oficiais libiconv 1.17, FreeXL 2.0.0 e SpatiaLite 5.1.0
são conferidas contra SHA-512 das receitas vcpkg indicadas; guardar também patches
e receitas da versão de build. Os materiais são de terceiros, não código próprio.

Para Qt 6.12.0/PySide6/Shiboken e GEOS 3.11.3/3.14.1, os arquivos upstream e receitas
de laboratório existentes estão identificados por commit/hash no índice. A lista
não transforma fontes candidatas Qt WebEngine/Chromium em fonte correspondente
completa dos binários 6.140.0. Obter gitlinks, patches/GN args, codecs/targets e
avisos gerados do build exato que continuarem faltantes antes da liberação comercial.

Na liberação final, o responsável deve entregar ou tornar disponíveis os materiais
correspondentes completos na modalidade permitida/adotada para cada licença,
com acesso equivalente, avisos e instruções adequados. Uma homepage genérica,
link instável, conjunto incompleto ou promessa de enviar no futuro não substitui
essa obrigação. O material de teste atual não faz oferta escrita definitiva.

## 4. Ambiente de trabalho e proteção do original

Faça backup dos projetos e use somente dados sintéticos nos ensaios. Conserve o
runtime original intacto e crie uma cópia integral independente para a variante;
não altere DLLs do Windows, QGIS ou de outros programas. As permissões de Program
Files não são modificadas pelo mecanismo. Não sobrescreva a instalação oficial
assinada para produzir evidência.

Utilize ferramentas de compilação e bibliotecas obtidas legitimamente. O resultado
modificado precisa ser compatível com x64, Python 3.12, a ABI de Qt/Shiboken/GEOS e
o consumidor. O Windows pode exigir confiança legítima dos novos executáveis.
Não desative SAC/Defender, não habilite Developer Mode, não instale certificado de
teste e não contorne bloqueios. Se o sistema recusar a variante, preserve os logs;
não há aprovação SAC de biblioteca modificada decorrente do ensaio hospedado.

## 5. Qt Core e bindings: procedimento demonstrado

1. Use a versão 6.12.0 e os commits/hashes do índice. Conserve as fontes originais,
   licença, patches e opções. As receitas exatas do laboratório estão no repositório
   em tools/standalone-native-lab e os logs incluem CMakeCache/exports/hash.
2. Em ambiente de build MSVC x64 autorizado, compile biblioteca compartilhada original
   e variante com a mesma interface. O ensaio altera somente a string de identificação
   qVersion para conter um marcador, sem alterar algoritmo. Bibliotecas de produção
   não são modificadas por esse procedimento de laboratório.
3. Copie a Qt6Core.dll reconstruída para _internal/PySide6 da cópia independente;
   confira exports exigidos por todos os consumidores. Preserve QtGui/Widgets,
   WebEngine, plugins e demais arquivos daquela cópia. Se houver incompatibilidade,
   não misture versões nem declare substituição aprovada.
4. Para bindings Python, altere somente PySide6/__init__.py ou shiboken6/__init__.py
   compatíveis na cópia, preservando licenças. O #18 demonstrou os pacotes modificados
   carregados e chamadas reais de binding; o próprio EXE foi preservado.
5. Registre caminho/hash/versão dos módulos realmente carregados e execute GUI,
   WebEngine/Leaflet, importação, edição, histórico, backup e precisão 22/22.

Evidência já existente: execução GitHub Actions 38737953304. Qt Core modificado
funcionou no AgroLines completo com o mesmo EXE; não equivale a reconstrução de
todos os módulos Qt, Shiboken nativo, WebEngine ou Chromium. Módulos restantes e
componentes transitivos exigem suas próprias fontes/avisos e compatibilidade ABI;
não se estende automaticamente a eles o resultado do Core.

## 6. GEOS: duas cópias diferentes

Fiona usa GEOS 3.11.3; Shapely usa GEOS 3.14.1. Preserve os pares C/C++ coerentes:

- _internal/fiona.libs/geos-cf4fccef073a506b3207c8a036a9d063.dll e
  geos_c-4d7a52e330cb609ee4db6bd3c1f7e7b5.dll.
- _internal/Shapely.libs/geos-bf067cd6ff74ee0ad5f3ff52c7ef08c9.dll e
  geos_c-6dd9fd915eef8a7928285416bef1e666.dll.

Compile BUILD_SHARED_LIBS=ON em MSVC x64, a partir das fontes e receitas indicadas,
com versão/ABI compatíveis. O laboratório ajusta OUTPUT_NAME no CMake para preservar
os nomes delvewheel exigidos pelos importadores, sem modificar o EXE do AgroLines.
Substitua o par correspondente na cópia integral, não só metade dele. O marcador
inofensivo de GEOSversion permite observar a variante realmente carregada.

Os dois pares foram demonstrados separadamente no AgroLines completo, preservando
importadores, motor GIS e 22 referências. A receita oficial Shapely 2.2.0 fixa GEOS
3.14.1, MSVC 14.44, compilação compartilhada e reparo delvewheel; fontes e receitas
são materiais adicionais, não alegação de build bit a bit reproduzido.

Não copie DLLs de QGIS nem troque as duas versões por uma única sem prova de ABI
para cada consumidor. LGPLv2.1 do GEOS deve ser avaliada em seu próprio escopo,
inclusive fontes, alterações e mecanismo permitido ao destinatário.

## 7. Outros LGPL e recompilação

libiconv, FreeXL, SpatiaLite, módulos Qt adicionais e componentes estáticos não são
homologados pelo ensaio de Core/GEOS. As alternativas LGPL/MPL indicadas em seus
próprios fontes podem permitir uso proprietário, com condições. GCP e RTTOPO já
foram comprovados desabilitados no SpatiaLite distribuído; não é necessário repetir
essa investigação sem nova evidência.

As receitas e patches públicos encontrados devem ser preservados com licença,
procedência e hash. Onde faltar correspondência do fornecedor, não apresentar
recompilação nominalmente da mesma versão como prova exata de todas as modificações.
Se a alternativa legal exigir kit de recombinação com material próprio, delimitar
antes os itens estritamente necessários e obter decisão do titular/revisão jurídica;
esta distribuição de teste não publica código, objetos ou bytecode próprios.

## 8. Verificações e informação de instalação

Confirme quais DLLs/PYDs foram efetivamente carregados, não apenas os nomes na pasta.
Compare hashes/versões antes/depois, exports/imports, erros de carregamento e resultados
funcionais. O manifesto jurídico é um controle de build/empacotamento e não é usado
como DRM novo para bloquear a execução normal com biblioteca modificada.

Informação de instalação legalmente exigida deve descrever ferramentas, etapas,
interfaces, formatos e materiais necessários à versão realmente distribuída. Não
se disponibiliza chave privada de assinatura nem se afirma que basta substituir
DLL dentro de MSIX assinado. Esta edição standalone não usa a integridade MSIX.
A suficiência do mecanismo e eventuais requisitos adicionais continuam questão
jurídica concreta, com prova técnica e escopo delimitados.

## 9. Suporte e registros

Contato: fabricio.grupodelatorre@gmail.com. Informe versão/componente e problema
com exemplo sintético; não envie projeto real, dados pessoais, credenciais ou
código próprio desnecessários. O procedimento de suporte e a política distinguem
dados locais dos envios voluntários. Estes materiais ainda aguardam revisão antes
da adoção comercial e não declaram que respostas de fornecedor são parecer jurídico.
