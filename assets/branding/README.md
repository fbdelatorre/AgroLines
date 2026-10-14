# Identidade visual aprovada

Os quatro PNGs são cópias binárias intactas do ZIP
`AgroLines_Logotipos_Microsoft_Store.zip` fornecido pelo responsável. Os hashes,
dimensões e presença de canal alfa estão registrados em `originals.json`.

A matriz de geração é `AgroLines_Arte_Caixa_1080x1080.png`, para manter o mesmo
desenho em todas as resoluções. Os outros três originais ficam preservados como
referência. Todos vieram opacos, com fundo branco: não removemos esse fundo nem
inventamos transparência. Não há recorte, alteração de cores ou geração por IA.

`distribution.icon` redimensiona proporcionalmente com Qt SmoothTransformation e
gera ICO com PNGs de 16, 32, 48, 64, 128 e 256 pixels. O ICO é utilizado pelo
PyInstaller e pela janela Qt do executável congelado. `distribution.branding`
gera os recursos MSIX de 44, 50 e 150 pixels, variantes de escala 100/125/150/200/400
e variantes targetsize para o shell. O manifesto continua apontando aos mesmos
nomes; identidade e pasta de projetos não mudam.

O workflow compara os hashes dos recursos **extraídos do MSIX**, do original
incluído, do ICO utilizado pela janela e os bytes RT_ICON embutidos no PE do EXE
com os seis PNGs do ICO. O relatório `evidence/msix/branding.json` não atesta a
aparência de um pacote instalado. A legibilidade em 16/32 pixels, menu Iniciar,
barra de tarefas e escalas do monitor requer revisão visual no Windows real com
o pacote confiável da Store. A arte detalhada naturalmente perde detalhes pequenos.
