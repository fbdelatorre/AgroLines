# Licenciamento do candidato proprietário — revisão ainda necessária

A redução técnica não demonstra conformidade LGPL. O AgroLines permanece com a
intenção de distribuição proprietária; não se adotou nova licença/EULA, não se
alterou a visibilidade e não se publicou um kit de recombinação ou fonte própria
adicional como suposta solução LGPL. Compra Qt/certificado não autorizada.

## Implementado e verificável

- Coletor de avisos inclui LICENSE, COPYRIGHT, COPYING e NOTICE, preservando os
  textos existentes nos inputs. Não coleta código `.py/.pyc` de bases de licenças.
- Textos integrais LGPLv3, GPLv3 e LGPLv2.1 em
  `distribution/windows/third-party/`; fontes oficiais/URL/blob/SHA no `sources.json`.
  O teste do archive confirma os hashes desses três textos dentro do MSIX.
  Incluir GPLv3 como texto requerido pela LGPLv3 não licencia o AgroLines sob GPL.
- Metadados de licença dos pacotes e fontes dos PE aparecem por arquivo em
  `evidence/qt-minimal/native-current.csv/json`. Metadados do wheel **não** cobrem
  automaticamente cada DLL vendorizada.
- `native-signing-policy.json` é copiado integralmente ao payload e comparado por
  hash com a política revisada. `payload-manifest.json` cobre ambos e os avisos.
- Exclusões de módulos não modificam o código interno dos PE retidos. A comparação
  de bytes com o baseline e com os inputs demonstra o alcance real dessa afirmação;
  não demonstra ausência de patches upstream na fabricação dos wheels.
- `release_reviews` mantém licenciamento, mecanismo LGPL, privacidade e autorização
  de envio pendentes. Não é possível promover apenas preenchendo uma flag de origem.

## Matriz de risco por biblioteca

| Componente | Evidência / condições a conferir | Risco ainda aberto |
|---|---|---|
| PySide6/Shiboken/QtBase, Svg, WebChannel, Positioning, Qml/Quick/QuickWidgets/SerialPort e plugins retidos | Headers e alternativas por módulo em `docs/native-store-audit/fontes.json`; comparação com os wheels fixados e imports PE desta revisão | **Alto jurídico:** avisos completos, fonte correspondente e mecanismo LGPLv3 §4 não comprovados; não tratar todo Qt como LGPL por inferência |
| Charts, Graphs, Data Visualization, Quick 3D, Virtual Keyboard, Quick Timeline | Removidos antes da expansão de dependências; guards em módulos Python, DLL/plugins, QML/dados e archive final | Reintrodução bloqueada; ausência dessas seis famílias não aprova o restante de Qt |
| Qt WebEngine/Chromium/helper | Preservados recursos/processo auxiliar; probe reporta versão real do engine e Chromium, separadamente da versão PySide6 | **Alto jurídico/técnico:** fonte exata, patches/configuração de build, notices completos Chromium/codecs e homologação sob identidade/SAC. `dev` ou tag RC não é fonte exata comprovada do wheel final |
| CPython 3.12.10 e seus componentes | Inputs da instalação Python fixada; LICENSE.txt copiado; assinaturas upstream preservadas | PSF e licenças dos componentes embutidos, incluindo OpenSSL; cadeia/timestamp no runner não é SAC físico |
| NumPy/OpenBLAS/LAPACK/GCC runtime | LICENSE do wheel Windows fixado, identificado na auditoria original; NumPy BSD e avisos específicos de OpenBLAS/LAPACK/GCC com exceções | **Alto de confiança:** `_multiarray_umath` e outros PE sem assinatura permanecem; não presumir BSD para todo conteúdo vendorizado nem que a exceção GCC elimine quaisquer obrigações de fonte |
| Fiona/GDAL | Fiona BSD; GDAL possui texto MIT e avisos internos no wheel; todos os nomes/hash/origens em inventário | **Alto de confiança e revisão:** não estender licença GDAL a toda `fiona.libs`; extensões e DLLs unsigned continuam bloqueadas para assinatura sem revisão de direitos |
| GEOS (cópias Fiona e Shapely) | LGPLv2.1; texto integral incluído; Shapely tem licença própria distinta | **Alto jurídico:** fonte exata de cada cópia, scripts/patches/avisos e LGPLv2.1 §6 substituição/relinking; Qt Commercial não resolve GEOS |
| pyproj/PROJ e bases de dados | Bindings/engine com textos próprios nos inputs; bases PROJ e SRC preservados, rede PROJ desativada | **Alto de confiança:** PE unsigned. Conferir licenças dos dados/grids individualmente, versão/fonte correspondente e precisão offline; não aplicar licença do engine a todos os dados |
| MSVC/VCRUNTIME/MSVCP de wheels/Python | Cópias necessárias permanecem, assinaturas preservadas; origem por hash | **Médio/alto jurídico:** licença/REDIST aplicável e direito de redistribuição ainda não aprovados apenas por estar dentro de wheel |
| UCRT/API sets incidentais e OpenSSL do MySQL do runner | 46 correspondências exatas documentadas em `proveniencia-46.json`; retirada das cópias incidentais, sem trocar OpenSSL GIS/Python | Instaladores oficiais JDK/MySQL não foram fixados/validados. Não afirmar conformidade desses produtos; estes arquivos deixam de ser redistribuídos, sujeitos à medição final |
| Leaflet local | Avisos/licença locais e recursos JS/CSS já no repositório; sem tiles remotos no Store offline | Preservar atribuições; licença Leaflet não concede direitos de imagens/mapas de terceiros |
| Bootloader PyInstaller | Build fixado, no UPX; licença GPL com exceção de distribuição do bootloader, avisos coletados | Não confundir licença do empacotador com licença do código AgroLines; conferir eventuais modificações ao bootloader, nenhuma introduzida nesta tarefa |

DLLs vendorizadas adicionais exigem revisão própria: FreeXL, GeoTIFF, GIF, HDF5,
iconv, JPEG/libsharpyuv/WebP, json-c, Lerc, OpenSSL, curl, expat, lzma, PNG,
PostgreSQL/libpq, XML2, minizip, netCDF, OpenJPEG, PCRE2, Qhull, SpatiaLite, SQLite,
SZIP, TIFF, zlib e Zstd. O CSV lista cada caminho/hash/pacote, e a matriz acima
não atribui licença genérica a essa lista. Para cada uma é preciso obter a versão,
licença/notices e condições do build efetivo; onde os wheels não trazem informação
suficiente, solicitar ao fornecedor/fabricante do wheel. Libpq é cliente vinculado
a GDAL, não instalação de um servidor PostgreSQL; não removê-lo sem prova de
independência e regressão. Bibliotecas LGPL (por exemplo, cópias GEOS e componentes
GNU quando presentes) não podem ficar escondidas sob um rótulo MIT de GDAL.

## Materiais e mecanismo LGPL ainda não demonstrados

1. Manifesto de versões/commits exatos e cópias de fonte correspondentes de Qt,
   PySide6/Shiboken/WebEngine/Chromium, GEOS e demais componentes que exijam fonte;
   incluir patches, opções de compilação e scripts de geração pertinentes.
2. Avisos/atribuições completos acessíveis ao destinatário, incluindo componentes
   embarcados nos engines; coletor automático e três textos GNU não são suficientes.
3. Demonstrar um mecanismo aplicável: LGPLv3 §4(d)(1) de biblioteca compartilhada
   substituível, ou §4(d)(0) com material de recombinação adequado; GEOS §6 tem
   requisitos próprios. Definir Installation Information quando juridicamente exigida.
4. **Não há mecanismo comprovado de substituir DLL diretamente em WindowsApps.**
   Integridade MSIX/Store e assinatura impedem presumir isso. Um kit alternativo
   também precisa permitir recombinação e execução legítimas, sob termos adequados,
   sem obter chave privada da Store, carregar de pasta insegura ou desativar SAC.
5. Qualquer entrega de objetos/bytecode próprios como possível material de
   recombinação exige autorização específica e revisão, ainda não concedidas.
   Não se conclui que publicar todo o source próprio é a única alternativa.
6. A futura EULA e ativação/licença própria devem preservar direitos aplicáveis de
   modificar bibliotecas e engenharia reversa para depurar tais modificações.
   Licença de uso AgroLines e licença Qt são decisões separadas.

Se essa rota não puder ser demonstrada, obter resposta escrita da Qt sobre
Application Development Commercial para pessoa física no Brasil, o projeto iniciado
com Community, redistribuições já realizadas, módulos/versões, assentos/CI,
condições temporais e distribuição Store. A documentação de migração técnica não
é autorização contratual retroativa. Qt Commercial não resolve GEOS nem demais
licenças, assinatura GIS ou SAC. Sem compra/contato automático nesta tarefa.

## Homologação e responsáveis

- Codex: inventário, guards, hashes, proveniência local, exclusões justificadas,
  textos disponíveis e regressões automatizadas; resultados no README.
- Fornecedores: fontes/builds/notices exatos ausentes dos inputs; direitos/termos
  e documentação de assinatura quando necessários.
- Revisão jurídica: mecanismo LGPL, EULA/REDIST/terceiros, bases legais e transferências.
- Responsável: decisões, procedimentos de privacidade e autorização de qualquer envio.
- Windows físico: instalação Store confiável, UI, operações offline, eventos SAC,
  atualização/desinstalação/restauração e preservação real.
- Microsoft: processamento/certificação, assinatura/entrega Store e capabilities.

Não adquirir certificado agora por inferência. A primeira rota a avaliar é MSIX
assinado pela Store, após saneamento jurídico e autorização. O pacote técnico
não é instalável/entregável aos testadores nem aprovado para envio/comercialização.

Versões observadas nos probes Windows do candidato intermediário `6077ee5`:
GEOS da cópia Shapely **3.14.1**, PROJ da cópia pyproj **9.8.1**, Qt WebEngine
**6.140.0**, Chromium **140.0.7339.225**. Probes saíram com código zero e mapa/GIS
passaram; o job completo foi bloqueado pelo encerramento da janela normal. Não
atribuir essas versões às outras cópias vendorizadas por inferência. As refs
oficiais consultadas de WebEngine 6.140 tinham beta/RC, sem tag final correspondente
comprovada ao wheel; confirmar fonte/build exatos com fornecedor. Header QtSerialPort
v6.12.0 lido declara alternativas LGPL/GPL/comercial, sem aprovar o build inteiro.
