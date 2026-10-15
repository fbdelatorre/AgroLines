# GEOS Windows — LGPLv2.1, dois pares independentes

Não aplicar automaticamente LGPLv3 do Qt. Ver análise anterior
[GEOS LGPLv2.1](../geos-lgplv21.md) e [MSIX nesta fase](msix-lgpl-analysis.md).

## DLLs realmente distribuídas/carregadas

Todas x64, paths abaixo relativos a `_internal/`. As quatro aparecem nas três
fases: inicialização offline, importação/edição/backup e smoke GIS. Hashes e
importadores no recorte real `reference-components.json`. `_geos.cp312…pyd` é
binding Shapely, não uma quinta DLL GEOS upstream.

| Consumidor / versão | Caminho | SHA-256 |
| --- | --- | --- |
| Fiona 1.10.1 / GEOS 3.11.3 C++ | fiona.libs/geos-cf4fccef073a506b3207c8a036a9d063.dll | 9f487eb3f67a0c929ecf8bc06bbdf130876855f57a942055ffd93698807bc781 |
| Fiona / CAPI 1.17.3 | fiona.libs/geos_c-4d7a52e330cb609ee4db6bd3c1f7e7b5.dll | 55c98109de46bd30b4c908743045ed4be5ed3ae8ddf45158a0bfd45679f08596 |
| Shapely 2.2.0 / GEOS 3.14.1 C++ | Shapely.libs/geos-bf067cd6ff74ee0ad5f3ff52c7ef08c9.dll | 0948bdb5c70b82e5055b55e9419b78d68372b1d0ec877277fa6e79276f6299b9 |
| Shapely / CAPI 1.20.5 | Shapely.libs/geos_c-6dd9fd915eef8a7928285416bef1e666.dll | 6e65985b30831761887de3217853a720147626b18cb41668cd2bdc43d1bcded1 |

Fontes oficiais já arquivadas: GEOS 3.11.3 commit
`17e3cb142d2592ce09c4530267ee2fb6ee1c6f79`; 3.14.1 commit
`c389f532d25fe6228861d9b19339f9cb57ca4bdb`. Textos LGPL2.1 e build CMake já
reunidos. Correspondência exata das receitas/patches/reparos de importação dos
wheels permanece U04/U05; versão nominal sozinha não a prova.

## Laboratório — original e modificado de cada versão

Workflow e instruções em [reproduction.md](reproduction.md). Cada árvore Git é
conferida por commit e SHA-256 do arquivo do índice do PR #15. Compila GEOS C++
e C API compartilhados x64 com MSVC; copia DLLs para pasta original. Consumidor
sintético Python ctypes recebe caminho absoluto, chama GEOS_init_r, lê WKT,
calcula áreas de quadrados de lados 0.001, 1, 10 e 100 e libera objetos/contexto.

Um patch muda **somente a string GEOSversion** para incluir
`-agrolines-synthetic`. Não modifica algoritmos, coordenadas, tolerâncias ou
formatos. Recompila e repete as áreas com o mesmo consumidor. Registra o módulo
C API por GetModuleFileNameW do HMODULE real e enumera as DLLs GEOS C++/C carregadas
no próprio processo. Verifica x64, versão/marcador, hashes diferentes, resultados
numéricos iguais e dependências dentro da pasta de laboratório escolhida.

Depois executa as duas fases com **o mesmo EXE sintético PyInstaller onedir**, cuja
hash é registrada e `sys.frozen` deve ser verdadeiro. Esse EXE não contém código
AgroLines, Shapely ou Fiona. Ele aceita biblioteca externa no protocolo do laboratório:
prova seleção de C API em consumidor congelado isolado, sem afirmar que o congelador
oficial, os importadores com nomes delvewheel ou todo o aplicativo foram recompostos.

## Precisão e ABI

Quatro áreas são verificações adicionais do C API compilado, **não** as 22 referências
integrais do produto. As 22 referências existentes são executadas separadamente
no baseline GIS em cada job Windows e no CI Linux/Windows; seus resultados não
podem ser atribuídos à GEOS reconstruída. Não há modificação no motor de produção.
ABI demonstrada somente para consumidor/funções exercitados, arquitetura x64 e
importações registradas por dumpbin. A aplicação real usa mais funções e versões
vendorizadas reparadas; compatibilidade integral continua sem demonstração.

## Níveis

Resultado real Windows, hashes, execução e artefatos ficam em validation-results.json.
O nível sintético e o nível congelado isolado são informados separadamente para
cada versão. **GEOS em MSIX confiável NÃO DEMONSTRADO / BLOQUEADO POR REQUISITO
EXTERNO.** Nenhuma DLL do candidato foi substituída. Não há inferência automática
de cumprimento LGPL2.1, fonte exata dos wheels ou aceitação SAC.

## Resultado executado e arquivado

[Execução Windows aprovada](https://github.com/fbdelatorre/AgroLines/actions/runs/38664013105)
(commit `34a9793599e14bdd4fc8d6b7a5d267cb84bd507b`). Os três relatórios brutos
`lab-*.json` foram preservados byte a byte, com hashes conferidos contra a
captura dos artefatos e dados iguais aos logs. Ver
[validation-results.json](validation-results.json) e
[verificação](lab-evidence-verification.json).

**DEMONSTRADO NO WINDOWS / DEMONSTRADO SOMENTE EM CONSUMIDOR SINTÉTICO.**
O host foi **Windows Server 2025 Datacenter, build 26100, x64**. Estado SAC não
confirmado; serviço/antivírus Defender ativos, proteção em tempo real reportada
`false`. Nenhuma configuração foi alterada. Não é Windows 11 físico com SAC On.
Não usar este resultado como prova de integridade/instalação MSIX ou proteção ativa.

**GEOS 3.11.3 e 3.14.1:** consumidor Python independente e consumidor congelado
PyInstaller passaram com original/modificada. Os módulos C API **e** C++ foram
observados nas pastas esperadas. Em cada versão, as quatro áreas permanecem
`0.000001, 1, 100, 10000`; o C++ GEOS permanece com mesmo hash, mudando somente
a DLL C API que contém a string de versão marcada. Hashes completos, versões,
caminhos e SHA do mesmo consumidor congelado por versão constam dos dois
relatórios brutos. Nada disso comprova a substituição das cópias vendorizadas
usadas por Shapely/Fiona no AgroLines ou seu pacote Store.
