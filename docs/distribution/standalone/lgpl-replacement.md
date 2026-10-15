# Substituição e recombinação — limites da implementação

O standalone não fica sob WindowsApps nem sob envelope MSIX. Mantém as DLLs/PYDs
originais separadas, nomes, diretórios, plugins, dados PROJ/GDAL e recursos WebEngine.
Uma cópia independente da árvore pode receber bibliotecas compatíveis sem editar
um pacote Store. Isso elimina a barreira do diretório protegido MSIX; não elimina
LGPL, ABI, requisitos SAC ou a necessidade de fontes correspondentes.

## Implementado e testável

O perfil standalone utiliza `module_collection_mode={'PySide6':'py','shiboken6':'py'}`.
Os módulos Python coletados dessas bibliotecas ficam em `_internal`, **sem cópia
sombreando no PYZ**. Módulos próprios permanecem no arquivo PYZ; este mecanismo
não publica fontes, objetos ou kit proprietário. PyInstaller não protege contra
extração/engenharia reversa; empacotamento não equivale a segredo criptográfico.

`standalone-layout.json` lista fontes externas e hashes. O gate lê o PYZ real,
rejeita bindings embutidos, fontes próprias externas, módulos Qt excluídos,
perfil online e ausência de recursos essenciais. São controles técnicos, sem
aprovação jurídica automática.

`Test-BindingReplacement.ps1` clona a árvore num laboratório autorizado, acrescenta
somente constante inofensiva aos `__init__.py` de PySide6/Shiboken e executa **o
AgroLines congelado**. Registra caminho, hash e marcador realmente importados,
chamada QObject/Shiboken, mapa WebEngine, 5 formatos GIS, edição, undo/redo,
histórico, backup/restauração e as 22 referências computacionais. A árvore original
não é modificada. O manifesto detecta a alteração na cópia; o probe registra a
divergência sem impedir o exercício das bibliotecas. Não há verificação de hash
para bloquear substituições na inicialização normal.

O teste não altera DLLs Qt/GEOS nem seus algoritmos. **Substituição de módulos Python
demonstrada não é recompilação/substituição de toda a pilha nativa.** Os laboratórios
Qt/GEOS Windows do PR #16 continuam evidências separadas, com consumidor sintético.

## Procedimento para bibliotecas nativas modificadas

1. Obter fontes, patches e receitas **correspondentes ao binário**. Usar
   [dossiê](https://github.com/fbdelatorre/AgroLines/blob/5291f8c06addc0550a2ab94a60115bd3357b1f79/docs/compliance/README.md) e
   [pendências upstream](https://github.com/fbdelatorre/AgroLines/blob/5291f8c06addc0550a2ab94a60115bd3357b1f79/docs/compliance/windows-validation/missing-upstream-materials.md).
2. Preparar cópia integral em diretório novo controlado pelo interessado. Nunca
   substituir DLLs do sistema, instalar certificados de teste, alterar o PATH
   global ou modificar o MSIX de referência.
3. Compilar bibliotecas x64 compatíveis com CPython 3.12, PySide6/Shiboken 6.12,
   ABI Qt e toolchain do wheel. Preservar exports, nomes e conjunto coerente de
   DLLs/PYDs/plugins/WebEngine/recursos; manter separadas as cópias GEOS de Fiona
   e Shapely. Nome com hash do delvewheel não garante correspondência da ABI.
4. Em ambiente legitimamente autorizado, substituir somente arquivos de terceiros
   identificados. Não contornar bloqueios SAC; biblioteca modificada pode precisar
   de assinatura/reputação própria aceita pelo Windows. Uma assinatura do AgroLines
   não torna qualquer substituição confiável.
5. Reexecutar probes, observar DLLs do processo principal e WebEngine, comparar
   hashes e precisão. Registrar falhas e versão da árvore. Não aceitar apenas
   carregar uma DLL modificada num processo sintético à parte.

**Pendente:** demonstrar Qt/GEOS nativos reconstruídos compatíveis dentro do AgroLines
congelado e numa máquina Windows 11 com proteção ativa; obter fontes/receitas e
avisos ainda incompletos; rever se o mecanismo atende LGPLv3 §4(d)(1)/§4(e) e
LGPLv2.1 §6(b) nas condições reais. Não foi entregue kit de recombinação de código
próprio nem declarado cumprimento por esse outro caminho.

A futura EULA e licença comercial devem preservar modificação/substituição e
engenharia reversa necessária à depuração dessas modificações, conforme licença
aplicável. Licença própria não pode invalidar esse exercício. Fontes públicas de
terceiros, avisos, correções vendorizadas e obrigações de codecs/GPL permanecem
objeto dos PRs #15–#17; não atribuir licença única a todo wheel. Qt Commercial
não foi comprado nem considerado obrigatório automaticamente.
