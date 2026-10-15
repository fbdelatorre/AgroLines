# Substituição nativa no AgroLines completo — evidências de 15/10/2026

**CONCLUÍDO: experimento técnico no Windows Server descartável autorizado.**
**PARCIAL: cumprimento LGPL do produto. BLOQUEADO: homologação física SAC.**

[Execução aprovada, três jobs](https://github.com/fbdelatorre/AgroLines/actions/runs/38737953304),
commit do laboratório `77ca169c376ae2292745194153f14062b0469341`.
[Resultados estruturados](evidence/native-results.json) foram extraídos dos registros
`AGROLINES_FULL_NATIVE_RESULT` dessa mesma execução, sem editar seus valores.
Logs completos, patches e caches de compilação estão nos artefatos abaixo.

## Consumidor preservado

Reutilizado o onedir do [PR #18](../standalone-validation/README.md), execução
`38733288326`, artefato `11970829773`. Cada job confere seu manifesto
SHA-256 `cd462d33214018a28d364b2cea65a9e172a140a13fd50a2cdf162a43b95f32e0`.
Não recompila o código próprio nem modifica o original. Em todas as variantes:

- AgroLines.exe SHA-256:
  `e9a497948ecd272f4ba4b5c9f3ece4bcfee4624a33c44055ee2b89bebbe05cd7`.
- Fonte do consumidor: `710a9664fe7112570775224909d174a7738f24a5`;
  merge **de teste** GitHub equivalente `471a90560eb326b27acf75bcb47c700d66e51782`.
- Duas árvores independentes por componente: reconstrução upstream original e
  variante marcada. Somente as DLLs-alvo e a instrumentação do Python LGPL PySide6
  são diferentes. O manifesto do payload original é conferido novamente ao final.
- Instrumentação registra módulos do próprio processo, caminhos, hashes e versões
  consultadas via `GetProcAddress` nos handles **já carregados**, sem carregar
  outra biblioteca para produzir um resultado artificial.

## Resultados e bytes carregados

| Componente alvo | Variante original recompilada → modificada | Resultado |
| --- | --- | --- |
| Qt Core 6.12.0 | `qVersion`: `6.12.0` → `6.12.0-agrolines-synthetic` | GUI, WebEngine, GIS e precisão 22/22 nas duas variantes |
| Fiona: GEOS 3.11.3 | `GEOSversion`: `3.11.3-CAPI-1.17.3` → mesma versão com `-agrolines-synthetic` | Mesmo executável; importadores e Shapely preservados; 22/22 |
| Shapely: GEOS 3.14.1 | `GEOSversion`: `3.14.1-CAPI-1.20.5` → mesma versão com `-agrolines-synthetic` | Mesmo executável; Fiona preservada; 22/22 |

Caminhos relativos e SHA-256 das variantes **modificadas** efetivamente observadas:

| Arquivo em `_internal/` | SHA-256 |
| --- | --- |
| `PySide6/Qt6Core.dll` | `fe87ca493480fe252e8fc56fa2d8942339380a2bc5083cec1cda6bf1bec70739` |
| `fiona.libs/geos_c-4d7a52e330cb609ee4db6bd3c1f7e7b5.dll` | `0ce7d47996c57ac0b498f53f42d1ed466010fdc5c847792b43805899e3e90754` |
| `fiona.libs/geos-cf4fccef073a506b3207c8a036a9d063.dll` | `ee1a2bd7e61b7ae8d065975f909c0389f47118b154e0e3a1c26d36cbf0ff1255` |
| `Shapely.libs/geos_c-6dd9fd915eef8a7928285416bef1e666.dll` | `90e66c01c4c08225a6ad4c519d98a584067de0d9578d41eb8749364ea9d000fb` |
| `Shapely.libs/geos-bf067cd6ff74ee0ad5f3ff52c7ef08c9.dll` | `52d9efd9395219237ff3579b324d8d590123e84f2a176f83ea580c86f870f9d4` |

GEOS substitui o **par coerente C/C++**; somente a string retornada pela API C
recebe o marcador. O C++ reconstruído tem o mesmo hash nas duas fases de seu job.
O job Qt substitui **apenas Core**; os demais módulos Qt, plugins e WebEngine
originais funcionaram com esse Core. Não é demonstração de reconstrução de todos
os módulos Qt, nem de todas as configurações ABI possíveis.

## Fontes, receitas e limites de correspondência

Commits e SHA-256 dos arquivos upstream arquivados, conferidos antes de compilar:

| Fonte oficial | Commit | SHA-256 do arquivo fonte |
| --- | --- | --- |
| [qtbase](https://github.com/qt/qtbase) 6.12.0 | `025bdad181de241e81bf853c8a2d7bf3d19261a9` | `e5317b2dfaf4cc2769be0cc8267fd9b209020fbb94a20b33da95f0e7df33bce4` |
| [GEOS](https://github.com/libgeos/geos) 3.11.3 | `17e3cb142d2592ce09c4530267ee2fb6ee1c6f79` | `e6cd4eaa975f5b9f787248929c815349f43b13ddbed3043e6f8143f86ef9c967` |
| GEOS 3.14.1 | `c389f532d25fe6228861d9b19339f9cb57ca4bdb` | `9ff4f171747da4e87a2f3cd1a79fdb43e7f6ef0ed83d20298b21cfedac6cff3a` |

A receita [run.py](../../tools/standalone-native-lab/run.py) compila x64 MSVC/CMake/Ninja
com bibliotecas compartilhadas; exports necessários são comparados aos consumidores
originais. Nomes vendorizados GEOS são produzidos via CMake `OUTPUT_NAME`, sem
reescrever importadores proprietários. Patches alteram somente identificação de versão.
Comandos, configuração e hashes vinculam **os binários de laboratório** às suas fontes.
Não comprovam patches/configuração exatos dos **wheels originais**: U01/U04/U05
continuam limitados por essa documentação. Assinatura da tag upstream não foi validada.

O aplicativo abre a janela normal e executa os probes existentes: Qt WebEngine/
Leaflet locais, SHP/GPKG/KML/KMZ/GeoJSON, edição numérica, undo/redo, histórico,
reabertura, backup/restauração e 22 referências computacionais. Há três capturas de
módulos por fase. Controles negativos recusam marcador incorreto, hash diferente,
precisão incompleta ou captura faltante (`tests/test_native_replacement.py`).

## Evidências para baixar

| Artefato somente de evidências | Link | Digest SHA-256 informado pelo Actions |
| --- | --- | --- |
| Qt Core | [11974424730](https://github.com/fbdelatorre/AgroLines/actions/runs/38737953304/artifacts/11974424730) | `14e0ca6b2d56e87c19b85f0e20d08399688768ee22e88cb785df4a6642c7ef5c` |
| GEOS Fiona | [11974249427](https://github.com/fbdelatorre/AgroLines/actions/runs/38737953304/artifacts/11974249427) | `19982c5eba20b14ad879b1fd3bd0d7fe8b99faf2d3e7bf3764471e9e1ea8f594` |
| GEOS Shapely | [11974624500](https://github.com/fbdelatorre/AgroLines/actions/runs/38737953304/artifacts/11974624500) | `637348deb667a25f2b5c09c38c4f9e0816cb6f5db58497c6f8c8142e31643e28` |

Nenhum artefato deste laboratório redistribui as DLLs modificadas ou o aplicativo.
Downloads binários do Actions estão bloqueados pelo proxy local; hashes dos
artefatos são os fornecidos pela API, não uma alegada conferência local do ZIP.
Os resultados internos foram obtidos dos logs do próprio builder Windows.

A primeira execução `38736595143` falhou no coletor: o limite padrão de 8192
exports do pefile truncava Qt Core; o wrapper ctypes do PyInstaller recusava a
consulta de handle GEOS. Corrigidos coleta completa com verificação de contagem e
`GetProcAddress` no módulo existente. Não foram relaxados critérios de ABI/GIS.

## Significado para LGPL e SAC

A árvore onedir **permite substituição nativa efetiva no aplicativo completo**,
sem abrir o código próprio ou recompilar o EXE. PySide6/Shiboken Python já tinham
prova independente no #18. LGPLv3 do Qt e LGPLv2.1 de GEOS devem ser avaliadas
separadamente, inclusive fontes/avisos e EULA. Isso não declara conformidade jurídica.

As DLLs de laboratório não foram assinadas nem instaladas. Windows Server hospedado
não é Windows 11 com SAC. Demonstrar a liberdade de substituição sob exigências de
confiança do equipamento do cliente ainda requer revisão jurídica e ensaio legítimo;
a prova não promete que qualquer DLL modificada sem confiança será aceita pelo SAC.
Nenhum MSIX foi modificado; limitações de integridade do MSIX continuam distintas.
