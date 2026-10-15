# Prova isolada de substituição compartilhada

Código sintético sob 0BSD, separado do AgroLines. Dados: um texto e um quadrado
10×10; sem projetos reais, código/objetos/bytecode proprietários ou chaves.

Resultados reais em [results.json](results.json): Qt Core 6.12.0 e GEOS 3.11.3
compilados de commits oficiais, depois modificados pelos patches neste diretório.
O mesmo consumidor Qt executa com a versão original e a modificada; QString mantém
16 caracteres. O mesmo consumidor GEOS usa a C API original e modificada e calcula
área 100 nas duas. Hashes das bibliotecas diferem. A alteração adiciona um marcador
à versão, não altera algoritmos. Patches são explicitamente sintéticos.

Os comandos e o script consolidado foram executados nesta sessão Linux, em
diretórios separados, com as mesmas receitas e fontes pinadas. Os dois pares
original/modificado passaram novamente. Requer compilador GCC,
CMake 4.4.4/Ninja 1.13.2 disponíveis e fontes do índice de conformidade:

```sh
python tools/compliance-poc/reproduce.py \
  --source-dir /tmp/agrolines-compliance-sources \
  --work /tmp/agrolines-relink-reproduction
```

Não se altera nenhuma instalação, MSIX, ambiente global ou proteção do Windows.
`LD_LIBRARY_PATH` existe somente nos filhos do teste ELF Linux, com diretórios do
experimento controlados. Isto não é instrução para redirecionar DLL bloqueada no
Windows. Não foi instalada biblioteca/pacote Windows unsigned.

**Limites:** prova a mecânica em consumidores sintéticos; não valida o aplicativo
PySide congelado, GEOS 3.14.1, duas famílias ABI dos wheels, integridade MSIX,
assinatura/catálogo Store, SAC ou conformidade integral LGPL. Rota oficial de
substituição/recombinação continua pendente de fontes/receitas, revisão jurídica e
prova Windows legítima. Nenhuma fonte correspondente Windows foi inferida deste build.
