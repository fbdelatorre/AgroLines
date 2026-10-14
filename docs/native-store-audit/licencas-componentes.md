# Redistribuição proprietária — obrigações por componente

Diagnóstico de 14/10/2026; nenhuma base de licença adotada ou conformidade aprovada.
Escopo: MSIX original SHA-256 `22286add49d873625f6a3ab898dc2b772b5514dd4fc30cddcfdbcfa369ea2a36`.
Os 453 PE não esgotam a revisão: Python congelado, JavaScript, dados PROJ, recursos
Chromium e fontes/notices também importam. Ver [lgpl-proprietario.md](lgpl-proprietario.md).

## Evidência material e limitações do coletor

Execução de auditoria de notices [38622742768](https://github.com/fbdelatorre/AgroLines/actions/runs/38622742768):
**27 entradas de metadata do ambiente de build e 84 arquivos** na pasta original
`third-party-notices`. Cópias integrais, hash e tamanho foram preservados no artefato.
A lista de metadata inclui ferramentas de build; ela não prova importação de pip,
setuptools ou PyInstaller pelo cliente. O usuário continua sem precisar instalá-los.

O coletor atual seleciona nomes contendo `license`/`copyright`. Pode deixar passar
`COPYING`, `NOTICE` ou créditos embutidos e também copiar módulos `.py`/`.pyc` de
registradores SPDX de ferramentas. **Quantidade de arquivos não comprova
completude dos avisos ou licença de cada componente vendorizado.** Esses registros
SPDX contêm nomes GPL/LGPL que não provam uso de bibliotecas sob essas licenças.
Não corrigimos empacotamento ou dependências nesta tarefa de avaliação.

Na pasta de notices conferida, os seis pacotes PySide6/Shiboken fornecem apenas
`LicenseRef-Qt-Commercial.txt` (470 bytes cada), embora a metadata declare opções
LGPL/GPL. O texto é condicional a ter contrato comercial; **não demonstra contrato
adquirido** e não substitui cópias LGPLv3/GPLv3 nem créditos Qt/Chromium. A presença
integral destes em outros recursos e seu acesso pelo usuário precisam ser comprovados.
Não há evidência de oferta de fontes correspondente completa/mecanismo de relinking.

## Matriz de componentes

| Componente / versão material | Licença/evidência | Condições e pendências para uso proprietário |
|---|---|---|
| AgroLines / EXE próprio | Não há LICENSE/EULA próprio adotado; PyInstaller congela bytecode | Definir termos próprios com exceções de direitos de terceiros; titularidade de contribuições e exposição pública precisam de revisão. Não mudar licença ou visibilidade automaticamente |
| PyInstaller 6.22.3 | COPYING original contém GPL-2.0-or-later WITH Bootloader-exception e Apache-2.0 | Exceção permite distribuir executáveis não livres; preservar avisos aplicáveis, revisar alterações ao bootloader/hook. Não estender a exceção às dependências |
| hooks-contrib 2026.8 | LICENSE presente; metadata `not declared` | Revisar texto e hooks concretos incluídos, em vez de inferir licença pela ferramenta |
| CPython 3.12.10 | LICENSE original de 36.874 bytes; fonte versionada PSF/termos históricos | Manter copyrights/licenças/disclaimers, identificar componentes incluídos (OpenSSL/SQLite/runtime), documentar modificações se houver |
| NumPy 2.5.4 | Metadata BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0; LICENSE original 45.831 bytes | Avisos/disclaimers para redistribuição binária; não usar nomes como endosso. Há termos próprios de algoritmos e código vendorizado |
| OpenBLAS/LAPACK no wheel NumPy Windows | LICENSE do wheel exato lido, SHA coincide com notice original; OpenBLAS BSD-3 e LAPACK BSD-3-Clause-Open-MPI | Preservar avisos específicos; documentar versão/build da DLL, além da versão NumPy |
| GCC runtime dentro do OpenBLAS Windows | O mesmo LICENSE declara ligação estática, GPL-3.0-or-later WITH GCC-exception-3.1 | Exceção 3.1 permite combinações com módulos independentes em processos de compilação elegíveis; não é isenção universal de GPL. Preservar GPL/exceção e confirmar o build/componentes/obrigações de fonte de terceiros aplicáveis |
| Shapely 2.2.0 | BSD-3, LICENSE.txt original; LICENSE_win32 também presente | Manter atribuição/disclaimer; não aplicar BSD aos motores GEOS embutidos |
| GEOS (cópias em Shapely/Fiona) | LICENSE_GEOS original identifica LGPLv2.1; COPYING oficial conferido | Revisar LGPL2.1 §6, fonte correspondente, substituição/relinking e direitos de debug; versão efetiva de cada cópia e forma de cumprimento ainda não fechadas |
| pyproj 3.8.0 / PROJ | MIT do binding, LICENSE_proj/copyright no pacote; PROJ oficial MIT-style | Manter textos de ambos; proj.db/grids/dados adicionais têm termos/versionamento próprios, verificar o que realmente acompanha a instalação |
| Fiona 1.10.1 / GDAL 3.9.1 reportado no probe | BSD do binding; GDAL LICENSE.TXT/copyright original agrega termos de terceiros | GDAL é geralmente permissivo, mas drivers/codecs e DLLs vendorizadas exigem licença específica. Mapear versão de cada biblioteca e avisos, não usar BSD Fiona como licença de tudo |
| PySide6/Essentials/Addons 6.12.0; PDF/WebEngine 6.12.0.140; Shiboken 6.12.0 | Metadata original LGPL/GPL; headers oficiais e módulos GPL identificados | Avaliação detalhada em lgpl-proprietario.md: fontes/avisos, GPL-only empacotados, relinking/MSIX, escolha Community ou contrato Commercial |
| Chromium/QtWebEngine/PDF | Recursos/helper e wheels identificados; texto Qt `dev` não identifica fonte exata do build | Revisar créditos completos, fontes/versão/build options/codecs/patentes e atualizações de segurança; não presumir cobertos integralmente por Qt Commercial |
| MSVC/UCRT/API sets | Arquivos presentes e assinados; 46 origens não fechadas por hash do input index | Documento Microsoft limita redistribuição a licenças/REDIST aplicáveis. Assinatura Microsoft/Qt não é autorização legal genérica; registrar pacote de origem e direitos corretos |
| OpenSSL/libcrypto/libssl | DLLs presentes, sem match de origem no índice atual | Confirmar versão/build e licença Apache/avisos aplicáveis, fonte de redistribuição; não presumir que LICENSE Python cobre todas as cópias |
| SQLite | Runtime integrado e bibliotecas vendorizadas | Confirmar build/versão e extensões; SQLite upstream domínio público não licencia automaticamente todas as extensões/criptografia |
| Leaflet 1.9.4 | JS local identifica versão; `desktop/map_assets/LEAFLET-LICENSE` BSD-2 | Preservar arquivo/copyright; não há autorização de tiles/satélite implícita na licença Leaflet. Modo Store mantém recursos locais |
| defusedxml 0.7.1 | LICENSE original, metadata PSFL | Preservar texto/avisos e verificar eventuais alterações |
| attrs 26.1.0, altgraph 0.17.5, pefile 2024.8.26, pip 25.0.1, setuptools 84.0.0 | Metadata MIT, notices coletados; vários são builder-only | Preservar avisos para o que é realmente distribuído; vendorizados de setuptools têm termos próprios, incluindo autocommand/LGPL no arquivo coletado |
| click 8.5.0, click-plugins 1.1.1.2, cligj 0.7.2, idna 3.20, pywin32-ctypes 0.2.3 | Metadata BSD, notices presentes | Preservar copyrights/condições/disclaimers, distinguir build de runtime |
| certifi 2026.7.22 | Metadata MPL-2.0, LICENSE original | Revisar obrigações de fonte e avisos de arquivos cobertos/modificações; não classificar todo bundle como permissivo sem condições |
| packaging 26.3 | Apache-2.0 OR BSD-2-Clause; ambos os textos no original | Determinar alternativa aplicável e preservar avisos; revisar vendorizados e eventual NOTICE |
| dnspython 2.9.0 / email-validator 2.3.0 | Metadata ISC / Unlicense; LICENSE email-validator presente | Conferir arquivos realmente incluídos, preservação de textos/disclaimer; metadata não comprova completude de avisos ISC |

Esta matriz cobre os grupos e metadata identificados, com pendências explícitas.
Não é SBOM jurídica exaustiva de todos os códigos internos dos wheels: compilados
GDAL/Chromium/OpenBLAS podem incorporar componentes adicionais sem PE separado.

## Dossiê mínimo antes de redistribuição aprovada

1. SBOM por arquivo/build e lista de terceiros incorporados; corrigir 46 origens
   ainda não comprovadas sem inventar procedência só pelo nome.
2. Dossiê de avisos completo, versões, textos, modificações e fontes/ofertas aplicáveis.
   Não disponibilizar source próprio por engano; cumprir source de terceiros quando exigido.
3. Prova de LGPL/relinking e EULA compatível, ou contrato Qt Commercial confirmado;
   fonte/GEOS/Chromium/outros permanecem avaliados independentemente.
4. Direitos para redistribuir e eventualmente assinar binários de terceiros; mecanismo
   legítimo de assinatura e testes físicos SAC, sem substituir vendor signatures aceitas.
5. Revisão jurídica documentada e autorização antes de alterações de dependência,
   contratação ou distribuição. A aprovação automática do CI não aprova licenças.
