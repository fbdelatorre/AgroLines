# GEOS — análise própria da LGPLv2.1

Não se aplicou automaticamente a LGPLv3 do Qt. Duas cópias C/C++ continuam necessárias
no grafo e não foram eliminadas:

| Origem Windows | Versão comprovada no wheel | Vinculação observada | Fonte preparada |
|---|---|---|---|
| Fiona 1.10.1 | GEOS 3.11.3 / CAPI 1.17.3 | `geos_c-4d7a…dll` importa `geos-cf4f…dll`; GDAL/bindings vinculam essa família | libgeos/geos commit 17e3cb142d2592ce09c4530267ee2fb6ee1c6f79 |
| Shapely 2.2.0 | GEOS 3.14.1 / CAPI 1.20.5 | `geos_c-6dd9…dll` importa `geos-bf06…dll`; extensões Shapely vinculam essa família | libgeos/geos commit c389f532d25fe6228861d9b19339f9cb57ca4bdb |

Paths completos, SHA, importadores e carregamentos em [evidence/native.json](evidence/native.json).
Ambas não são a licença BSD do Shapely/Fiona. COPYING LGPL2.1 integral está reunido;
confirmar todos os headers, alternativas/versionamento e patches de cada build.
As fontes upstream coincidem em versão, mas ainda não constituem prova exata das
opções/patches dos wheels reparados pelo delvewheel.

LGPL2.1 §6 admite obra que usa a biblioteca sob termos próprios, observadas as
condições de modificação para uso próprio e engenharia reversa para debug das
modificações, avisos/copyright/texto da licença e uma das rotas §6(a)–(e).
§6(b) demanda mecanismo compartilhado adequado que funcione com versão modificada
compatível; §6(a) exige fonte correspondente da biblioteca/modificações e materiais
utilizáveis para modificar a biblioteca e relinkar o executável. Avaliar scripts e
utilitários necessários. Ofertas por escrito e outras modalidades não podem ser
presumidas equivalentes sem atender suas condições.

A redação, modalidade de fonte e limites de uma EULA precisam de revisão independente
de §4 LGPLv3. Não inferir dever idêntico de Installation Information do Qt, nem uma
isenção universal por serem DLLs. A biblioteca C++ deve acompanhar a C API compatível;
alterar só um nome com hash não comprova compatibilidade dos bindings e dependências.

**Prova implementada:** GEOS 3.11.3 compilado de fonte oficial, biblioteca C API
modificada somente para identificar a experiência, consumidor sintético inalterado
calcula área de 100 m² com as duas variantes. Fonte/patch/receita/hash/resultados em
[PoC](../../tools/compliance-poc/README.md). Nenhum código/dado AgroLines é necessário.
Isso comprova o mecanismo sintético fora de MSIX em Linux; **não comprova** substituição
das duas famílias Windows, compatibilidade de ABI com GDAL/Shapely, cadeia pública,
instalação Store nem cumprimento integral §6. O candidato oficial não foi modificado.
