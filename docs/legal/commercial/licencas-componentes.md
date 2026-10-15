# Decisão por componente — escopo comercial proprietário

Proposta técnica fundamentada, não parecer jurídico ou autorização de distribuição.
Referência dos PE originais: [inventário por arquivo](../../compliance/inventory.json).
O inventário novo, realmente empacotado, é `legal/legal-manifest.json`: caminhos,
versões evidenciadas, hashes atuais, documentos e recursos. MudançasGEOS/libaec e
perfil comercial têm identificação própria; não herdam o hash do MSIX antigo.

**RESOLVIDO nesta tabela significa que o problema material indicado na coluna foi
resolvido, no escopo da licença desse componente.** Não significa que o instalador,
o mecanismoLGPL emWindows protegido ou todas as obrigações de terceiros receberam
aprovação global. Licenças permissivas não exigem reconstrução binária bit a bit,
publicação de todo código ou uma autorização comercial individual do fornecedor.
Quando a composição/versão ainda é incerta, isso está indicado, sem inferir licença
universal de um wheel. Uma licença comercial do AgroLines não relicencia Qt/GEOS.

Fontes dos textos efetivamente copiados: [manifesto suplementar](../../../distribution/legal/supplemental/materials.json),
[documentos auditados](../../compliance/documents.json),
[lock de fontes](../../../distribution/legal/source-delivery.json),
[novos componentes criptográficos](../../../distribution/legal/commercial/materials.json).
Versões nominais ou de fontes candidatas não são apresentadas como correspondência
comprovada ao binário; ver a coluna abaixo e as origens de cada documento.

| Componente | Licença e situação anterior | Correção/evidência material | Situação final e menor solução residual |
|---|---|---|---|
| Python3.12.10 | PSF2.0 + avisos históricos | LICENSE original preservado, origem/versão e fonte pública fixadas | **RESOLVIDO** para Python; CRT/OpenSSL próprios separados abaixo. Não precisa abrir o AgroLines. |
| PyInstaller6.22.3 | GPL2+ com exceção expressa do bootloader; partesApache2 | Texto/exceção preservados; bootloader sem mudança própria | **RESOLVIDO** no escopo do bootloader. A exceção permite empacotar produto proprietário; não torna bibliotecas internas permissivas. |
| InnoSetup7.1.0 | Licença própria permite expressamente uso comercial | Texto original do commit7d634620… incorporado; compilador oficial fixado porhash/assinatura; stub não foi alterado | **RESOLVIDO** para uso do compilador/stub. Preservar copyrights/endereços do Inno. Não há compra obrigatória demonstrada. |
| QtBase6.12.0 | AlternativaLGPL3 confirmada em fontes; build/vendorizados incompletos | GPL/LGPL originais, fontes upstream, avisos disponíveis; Core substituído no mesmoEXE em#19 | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: LGPL3§§4/6 + GPL3§6 exigem materiais/fontes aplicáveis. Falta mapear fontes/patches e créditos estáticos ao build exato, não reprodutibilidade bit a bit. |
| PySide6 6.12.0 / bindingsWebEngine6.12.0.140 | LGPL3 alternativa das interfaces inspecionadas | PacotePython externo aoPYZ, substituição real em#18/#19, fontes/avisos entregues | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: geração/build dos PYD e fontes correspondentes ainda incompletos. Pedido delimitadoU01, sem solicitar permissão comercial genérica. |
| Shiboken6.12.0 | LGPL3 alternativa inspecionada | PacotePython externo e substituível; fontes/avisos preservados | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: comprovar materiais do binário nativo e mecanismo completo aplicável. |
| QtSVG6.12.0 | LGPL3 alternativa nas fontes inspecionadas | Fonte/avisos fixados e módulo preservado | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: fechar mapa exato de patches/avisos incorporados; não comprar módulo por presumirGPL. |
| QtWebChannel6.12.0 | LGPL3 alternativa inspecionada | Fonte/avisos; ponteJavaScript/Python existente preservada | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: correspondência do build e avisos transitivos. |
| QtDeclarative/Quick/QML6.12.0 | LGPL3 alternativa inspecionada, dependência nativa transitiva | Fonte/avisos e exclusão de QML de aplicação/plugins de depuração preservadas | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: fontes/avisos do que está efetivamente ligado. Não foi criada UIQML. |
| QtPositioning6.12.0 | LGPL3 alternativa inspecionada, transitivo | Fonte/avisos fixados; não há coleta de localização do usuário | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: mesma lacuna documental de build, não novo tratamento de GPS. |
| QtSerialPort6.12.0 | LGPL3 alternativa inspecionada, transitivo | Fonte/avisos fixados | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: mapa de build/avisos. Não é ferramenta agrícola operacional criada por esta etapa. |
| QtImageFormats6.12.0/plugins | LGPL3 + licenças próprias dos codecs | Fonte/avisos; plugins desnecessários continuam excluídos | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: atribuições estáticas porcodec. Uma licençaQt não substitui as delas. |
| QtWebEngine6.140.0 / wheel6.12.0.140 | Alternativas abertasQt e licenças própriasChromium; fonte candidata divergente | Fontes/avisos conhecidos e pesquisa de tags/histórico preservados; candidato.264 não apresentado como fonte.225 | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA** no escopoQt aberto: revisão/gitlinks/patches/configuração e créditos finais de.225 ainda faltam. Rebuild ou resposta precisa deU02; sem retirar mapa/ponte atual. |
| QtPDF/PDFium | Termos próprios porarquivo; versão/fonte do binário6.140 incompleta | Avisos conhecidos preservados, sem atribuirLGPL universal ao PDFium | **REVISÃO JURÍDICA ESPECÍFICA** após obter lista de arquivos/licenças do target. Não foi demonstrado módulo incompatível nem necessidade de compra. |
| Chromium140.0.7339.225/codecs | BSD e muitas licenças porcomponente; codecs/patentes dependem dos targets | Pesquisa de versões e créditos existentes; sem alegação de créditos completos | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA** nos componentes abertos identificados; fechar BOM/licenças/codecs reais. Patentes não são automaticamente liberadas pelo BSD/Qt. |
| Renderizador softwareOpenGL/Qt | Composição exata não comprovada | PE/origem conhecidos, lacunaBOM estática mantida explícita | **REVISÃO JURÍDICA ESPECÍFICA** com obtenção documental prévia: identificarMesa/LLVM/outros realmente incorporados e aplicar seus avisos/exceções. Não declarar licença somente pelo nomeDLL. |
| QtCharts/Graphs/DataVisualization/Quick3D/VirtualKeyboard/QuickTimeline | Famílias dispensáveisGPL/comercial já retiradas | Gates de análise/imports/payload impedem reintrodução | **RESOLVIDO** no escopo de ausência; não justificam QtCommercial para o candidato reduzido. |
| Fiona1.10.1 | BSD3 | Texto e origem do binding preservados | **RESOLVIDO** para binding. Cada dependência e dados são avaliados separadamente. |
| GDAL3.9.1 | MIT e avisos incluídos no LICENSE.TXT | Texto do payload associado porhash; SZIP restritivo trocado porlibaec | **RESOLVIDO** para GDAL original. BOM residual de vendors/drivers, fontes/avisos específicos e dados continuam nos respectivos itens. |
| GEOSFiona3.11.3 | LGPL2.1 | Mesma versão reconstruída de fonte fixada, nenhum arquivo de algoritmos/headers alterado: ver manifesto dos inputs; parC/C++ renomeado somente noCMake;22/22 eGIS emWindows | **RESOLVIDO** para fontes/build/avisos desse novo par. Avaliar separadamenteLGPL2.1§6 e confiança de variante modificada noWindows; não aplicarLGPL3. |
| GEOSShapely3.14.1 | LGPL2.1 | Mesmo procedimento independente, fontes/receita/version/hash próprios | **RESOLVIDO** para fontes/build/avisos; mesmo gate residual de substituição/instalação. Não se misturam pares/versões. |
| Shapely2.2.0 | BSD3 | Texto/atestações/receitas preservados; GEOS separado | **RESOLVIDO** para binding. |
| libiconv1.17/libcharset | LGPL2.1+; utilitárioiconv GPL é outro produto | COPYING.LIB/AUTHORS, fonteGNU fixada e quatro patches/receita entregues | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: confirmar aplicação dos patches ao DLL real e materiais/mecanismo§6. Não atribuirGPL do programaiconv à biblioteca nem reescreverGDAL. |
| FreeXL2.0.0 | MPL1.1 ou LGPL2.1+ ouGPL2+ | EleitaMPL1.1 para arquivos cobertos; COPYINGExhibitA, fonte/receita/patches e autoria entregues | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: fechar eventuais modificações cobertas do build e forma de entregaMPL§3. A eleição não exige abrir o AgroLines nem autoriza mudar licença de dependências. |
| SpatiaLite5.1.0 | MPL1.1 ou LGPL2.1+ ouGPL2+ | EleitaMPL1.1; fonte/receita/patches/avisos; provasHasGCP=0/HasRtTopo=0 preservadas | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: mesma confirmação específica de fontes modificadas/entregaMPL. GEOS/libiconv têm obrigações independentes. |
| SZIP original | Encoder com restrição comercial na configuração anterior | Removido do payload, substituído porlibaec sem reintroduzir encoder original | **INCOMPATÍVEL E SUBSTITUÍDO** neste canal; não é código malware nem motivo para removerGIS. |
| libaec1.1.7 | BSD2 | Fonte/hash/build/avisos,6testes e8HDF5+decoder original | **RESOLVIDO** no escopo da licença e substituição. Fonte acompanha a versão emboraBSD não imponha publicação geral. |
| pyproj3.8.0 | MIT | Texto, copyright e origem preservados | **RESOLVIDO** para binding. |
| PROJ9.3.1/Fiona | MIT | Fonte e seis inputs de receita/patches conferidos comSPDX; textos associados | **RESOLVIDO** para códigoPROJ permissivo; dados/terceiros separados. Não há obrigação geral de publicar fontesMIT. |
| PROJ9.8.1/pyproj | MIT | Cinco inputs de receita/patches conferidos comSPDX e avisos associados | **RESOLVIDO** para códigoPROJ; BOM residual/dados continuam delimitados. |
| EPSG/ESRI/IGNF/NKG e dadosGDAL/PROJ | Termos dos dados/fontes próprias, não licença inferida daDLL | Hashes de502recursos são verificados; NKGCCBY4 e atribuições originais acrescentados; versões de banco identificadas | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA** nos conjuntos com concessão identificada: consolidar avisos específicos restantes das bases reais. Referência a grid opcional não prova grid distribuído. |
| NumPy2.5.4 | BSD3 + termos vendorizados identificados | Licenças dewheel/copyleft/exceções e componentes preservados,22/22 | **RESOLVIDO** para NumPyBSD e avisos identificados; exceçãoGCC é item próprio. |
| OpenBLAS/LAPACK | BSD3, buildOpenBLAS0.3.34.106.0 | DLL idêntico ao wrapperSciPy porhash; fonte/commit/receitas/avisos/patchexatos identificados | **RESOLVIDO** paraBSD e associação ao wrapper. Não exige compra nem troca de motorGIS. |
| GCC/libgcc/libgfortran incorporados aoOpenBLAS | GPL3 comGCCRuntimeLibraryException3.1 declarada | Texto integral/exceção, wrappers e receitaGCC; testeupstream de ausênciaquadmath conhecido | **REVISÃO JURÍDICA ESPECÍFICA**: aplicar“EligibleCompilationProcess” aos processos documentados e identificar eventual objeto fora da exceção. `-static-libgcc` sozinho não exige abrir o AgroLines; não há evidência de otimizador proprietário deIRGCC. Não reescreverNumPy sem achado concreto. |
| MicrosoftMSVC/UCRT/CRT estático | Direitos de código redistribuível, nãoAuthentiCode | Origem porarquivo/versão/hash; termosCPython/Shapely; REDIST oficial e elegibilidadeIndividualCommunity consultados | **DEPENDE DO TITULAR** e revisão contratual delimitada: comprovar licença legítima das ferramentas e alcance das redistribuições do build hospedado; Community permite aplicativos próprios de indivíduo, sem compra presumida. Não afirmar contrato já aceito. |
| OpenSSL3.0.16/Python e3.3.1/Fiona | Apache2 | Textos integrais específicos preservados porhash | **RESOLVIDO** nos componentes identificados, com avisos preservados; não prometer ausência universal de patentes. |
| SQLite3.49.1/Python,3.46/Fiona,3.53/pyproj | Dedicação ao domínio públicoSQLite; extensões próprias | Textos/origem associados | **RESOLVIDO** paraSQLite original. ExtensõesSpatiaLite e outros vendors não recebem domínio público. |
| certifi2026.7.22 | MPL2.0 para conjunto coberto | Fonte fixada e cacert.pem idêntico ao arquivo de fonte, LICENSE incluído | **RESOLVIDO** no escopo de fonte/texto e arquivo inalterado; manter fontes/avisos acessíveis na entrega. |
| attrs26.1.0 | MIT | LICENSE do pacote incluído | **RESOLVIDO** para o pacote identificado. |
| defusedxml0.7.1 | PSF2 | LICENSE do pacote/fonte preservados | **RESOLVIDO**. |
| Leaflet1.9.4 | BSD2 | JS/CSS locais e LICENSE incluídos | **RESOLVIDO** para Leaflet; não foram adicionados tiles/serviços externos. |
| libffi/Python3.4.4 nominal | MIT | Textos e receitaCPython; versão exata do binário permanece qualificada no inventário | **RESOLVIDO** para concessão/avisosMIT identificados; não inferir igualdade de build pela versão da receita. |
| LERC/Fiona | Apache2 upstream; versão binária ainda não comprovada | LICENSE/NOTICE da releaseC++v4.0.0 obtidos; documentos do tagJS separados como pesquisa e não atribuídos aoDLL | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: vincular versão/NOTICE exatos doDLL. Não são cobradas permissões comerciais genéricas. |
| libgeotiff/Fiona | MIT e partes domínio público; fonte1.7.3, binário sem versão comprovada | Texto integral acrescentado | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: fechar autoria/versão no build concreto; não falta uma licença comercial. |
| giflib/Fiona | MIT upstream, versão não comprovada | Avisos conhecidos preservados | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: associar texto/copyright exatos. |
| minizip/Fiona | zlib upstream, versão não comprovada | Evidências e componentes registrados | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: fechar licença/avisos da variante real, não confundirminizip-ng comminizip original. |
| PCRE2/Fiona | BSD3; fonte10.43, binário ainda qualificado | LICENCE original acrescentado | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA**: confirmarcopyright/versão/patches do DLL e partes incorporadas. |
| curl8.8.0-DEV/Fiona e8.19.0/pyproj | Licençacurl, permissiva | Textos/avisos dos componentes identificados preservados | **PERMITIDO, MAS COM OBRIGAÇÃO NÃO CUMPRIDA** no snapshotDEVFiona: mapear versão/copyright do snapshot. pyproj8.19 mantém seu texto identificado. RedeGDAL continua bloqueada. |
| libpng1.6.43 | Licençapng | Texto integral/copyright preservados | **RESOLVIDO** para biblioteca identificada. |
| JPEG/IJG/libjpeg-turbo3.0.3 e3.1.4.1 | IJG + BSD/zlib porparte | LICENSE/README e reconhecimentoIJG literal noTHIRD_PARTY_NOTICES | **RESOLVIDO** para avisos/licenças identificados. |
| TIFF4.6.0 e4.7.1 | LicençaTIFF permissiva | Textos originais específicos incluídos | **RESOLVIDO** para libtiff; LERC/JPEG/etc vinculados mantêm obrigações próprias. |
| HDF5 1.14.4.3 nominal | LicençaHDF5 permissiva | COPYRIGHT/texto e limites de versão registrados; encoderSZIP trocado | **RESOLVIDO** para licençaHDF5 e avisos identificados. Composição real de filtros permanece no inventário específico, não herdada dessa linha. |
| netCDF4.8.1 | LicençaUnidata/netCDF permissiva | COPYRIGHT original preservado | **RESOLVIDO** para licença/avisos identificados. |
| Qhull2020.2.r | LicençaQhull permissiva | COPYING original preservado | **RESOLVIDO**; conservar as condições originais, não chamarQhull deMIT sem ressalva. |
| zlib1.3.1/Fiona epyproj | zlib | Texto/avisos preservados | **RESOLVIDO** para os componentes identificados. |
| zstd1.5.6 | BSD3 alternativa | TextoBSD preservado; não escolhida automaticamenteGPL | **RESOLVIDO** para alternativaBSD dos arquivos cobertos. |
| libwebp1.4.0 | BSD3 +PATENTS | LICENSE existente ePATENTS acrescentado | **RESOLVIDO** no escopo desses textos; concessão de patentes tem condições e não cobre qualquer patente de terceiros. |
| json-c0.17 | MIT | COPYING/copyright preservados | **RESOLVIDO**. |
| Expat2.6.2 | MIT | LICENSE/copyright preservados | **RESOLVIDO**. |
| libxml2 2.11.8 | MIT +avisos incluídos | Textos originais preservados | **RESOLVIDO** para arquivos/licenças identificados. |
| liblzma5.6.2/Fiona e5.8.3/pyproj | Termos porarquivo emCOPYING; utilitáriosXZ separados | COPYING preservado, não foi atribuídoGPL dos utilitários aoDLL | **RESOLVIDO** no escopo da biblioteca declarada; não autoriza distribuir utilitárioGPL como código próprio. |
| libpq16.2 | PostgreSQLLicense | COPYRIGHT preservado; DLL cliente não é servidor instalado | **RESOLVIDO**. O cliente não exige PostgreSQL local e não abre essa conexão no perfil agrícola local. |
| PyNaCl1.6.2 e libsodium incorporado | Apache2 +ISC dalibsodium | WheelWindows/hash de_sodium.pyd e ambos textos originais associados | **RESOLVIDO** para concessão/avisos identificados. Versão exata do libsodium/build deve ser conservada no material da release; não se usa licençaQt para criptografia. |
| cffi2.0.0 / libffiWindows incorporado | MIT0 no pacote; MIT nos arquivoslibffi | Wheelexato,LICENSE/AUTHORS e copyrights/permissões originais de sete headersfontesx64 acrescentados | **RESOLVIDO** para textos/concessões identificados; avisos não foram inferidos só da metadata. |
| pycparser2.23 | BSD3 | LICENSE do wheelexato, associado somente se realmente congelado | **RESOLVIDO** quando presente noPYZ; não é presumido entregue apenas por estar no builder. |

## Condições comuns que continuam bloqueando a comercialização

1. Fechar fontes/avisos exatosQt/Chromium e delta dos vendors/bases realmente
   pendentes; não falta uma autorização individual de uso comercial paraMIT/BSD.
2. Revisão focada no mecanismo compartilhadoLGPL3§4(d)(1), InstallationInformation
   quando aplicável eLGPL2.1§6; direitos preservados naEULA. Os experimentos não
   comprovam funcionamento de uma variante legítima emWindows11/SAC.
3. Completar e adotar os documentos/aceite, fundamentosLGPD, retenção comercial e
   fornecedores reais. Não há aprovação jurídica automática por passar testes.
4. Assinatura/confiançaWindows e homologação física de instalação, atualização,
   desinstalação e dados; privacidade/contratação do serviço de licenças.

Não foi demonstrada necessidade deQtCommercial, troca de interface ou reescrita
GIS. A alternativa prática é manter o stack, concluir os poucos materiais exatos
faltantes e revisar as questões delimitadas. ComprarQt não resolveGEOS, bases,
CRT, privacidade ou confiançaWindows. Não há prazo de aprovação comercial prometido.
