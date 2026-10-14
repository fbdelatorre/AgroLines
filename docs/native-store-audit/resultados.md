# Resultado da auditoria do candidato original

Auditoria final: [GitHub Actions 38624227575](https://github.com/fbdelatorre/AgroLines/actions/runs/38624227575),
commit de ferramentas `64ec321125979d067012bdd9f21db341bc37f912`.
[Download das evidências](https://github.com/fbdelatorre/AgroLines/actions/runs/38624227575/artifacts/11923226885)
— artefato **agrolines-original-msix-native-audit** (578.741 bytes ZIP).
Não é novo MSIX nem certificado. O MSIX original permanece não assinado e inalterado.

MSIX `AgroLines-1.0.0.0-x64-STORE-SUBMISSION-UNSIGNED.msix`, fonte `e3e55be9a45805a3277bc4b879704a88d8f207fd`,
SHA-256 `22286add49d873625f6a3ab898dc2b772b5514dd4fc30cddcfdbcfa369ea2a36`.
Verificado antes/depois; os 453 hashes nativos coincidem com o inventário original.
Auto-builds posteriores do PR não substituem a referência imutável desta análise.

## Cadeias e assinaturas: o que os 150 casos representam

- **375/453** arquivos: Get-AuthenticodeSignature `Valid` e SignTool `/pa /all /v /tw`
  exit code **0**, sem transformar aviso/falha em sucesso.
- **78/453**: `NotSigned`, SignTool exit code **1**; não há cadeia de assinante para validar.
- Dos assinados, **72** têm `NotTimeValid` na X509Chain genérica de **hora atual**;
  SignTool aceita suas assinaturas/timestamps sob política Authenticode. Não são
  72 reprovações Authenticode nem prova de revogação/rejeição SAC.
- Cadeia genérica válida: **303**; sem validação completa: **150 = 78 + 72**.
  Nenhum outro flag de cadeia, erro de inspeção ou alteração detectado nesta execução.
- **406** nativos com origem por hash exato de input fixado, mais 1 EXE pela entrada
  do manifesto; **46** sem origem confirmada por esse índice (API sets/UCRT/OpenSSL).
  Signer/nomes não substituem prova de procedência ou licença.

CSV por arquivo em [inventario-arquivos.csv](inventario-arquivos.csv), com caminho,
origem/biblioteca, SHA-256, signer, Authenticode, flags/motivo, SignTool e fases observadas.
O JSON completo no artefato contém elementos/validade da cadeia e saída bruta por PE;
[resultados.json](resultados.json) resume a execução. Certificados/keys não foram instalados.

## Riscos por grupo de biblioteca

Os grupos atribuem a **origem do wheel**, separando GDAL/PROJ/GEOS quando identificados.
Não significam que todos os 299 arquivos Qt tenham licença Qt, nem que haja 39 DLLs
somente do motor GDAL. Avisos/licenças por terceiros em
[licencas-componentes.md](licencas-componentes.md).

| Grupo | PE | Unsigned | Cadeia atual não validada | SignTool aceitos | PE observados | Risco / ação proposta |
|---|---:|---:|---:|---:|---:|---|
| Próprio / bootloader | 1 | 1 | 1 | 0 | 1 | Alto: EXE sem assinatura; CA pública elegível, EULA/exceção PyInstaller |
| CPython/runtime | 26 | 0 | 26 | 26 | 22 | Preservar assinaturas/timestamps aceitos; conferir PSF/terceiros e versão/suporte |
| Qt/PySide/Shiboken e terceiros do wheel | 299 | 0 | 0 | 299 | 40 | Alto por licenças: GPL/commercial presentes, LGPL/relinking/Chromium pendentes; confiança SAC ainda não testada |
| NumPy/OpenBLAS/runtime | 15 | 14 | 15 | 1 | 4 | Alto: `_multiarray_umath` e outros PE unsigned; revisar BSD/LAPACK/GCC-exception e assinatura permitida |
| Fiona/GDAL/dependências | 39 | 38 | 39 | 1 | 39 | Alto: uso efetivo, drivers/codecs/avisos/build e assinatura pública a resolver |
| PROJ/pyproj/dependências | 19 | 18 | 18 | 1 | 19 | Alto: transforms usadas; direitos/dados/precisão e assinatura das cópias |
| GEOS/Shapely/bindings | 8 | 7 | 7 | 1 | 8 | Alto: GIS usado, LGPL2.1/fonte/relinking e assinatura legítima |
| Outros sem origem fechada (API sets/UCRT/OpenSSL) | 46 | 0 | 44 | 46 | 1 | Médio/alto: Authenticode aceito, procedência/REDIST/textos de licença ainda não fechados |
| **Total** | **453** | **78** | **150** | **375** | **134** | Aprovação SAC e jurídica continuam false |

## Execução real observada e seus limites

Três cenários do **EXE congelado original** extraído, PATH limitado a System32 e
variáveis externas Python/GIS removidas: início normal da UI offline, smoke/GIS e
importação/edição/backup/restauração com dados sintéticos. Todos encerraram com código 0.
Os processos AgroLinesPoC e **QtWebEngineProcess** foram observados em todas as fases;
a imagem do helper está correlacionada por hash/caminho após normalização Windows.

**134 PE distintos** do pacote observados, incluindo **67 dos 78 unsigned**.
Referência completa de fases/processos/primeira observação no CSV e `loads.json` do
artefato. Polling de módulos não é trace completo ETW/ImageLoad: não observado não
significa não usado e não autoriza remover componentes. Nenhuma instrumentação do
MSIX ou redução de proteção aplicada.

Há **uma entrada classificada external por fase**: `MpOav.dll` em
`C:/ProgramData/Microsoft/Windows Defender/Platform/4.18.26080.4-0/`, no runner.
O prefixo é externo a WINDIR/payload; não é biblioteca agrícola do MSIX. Não removida,
assinada ou alterada. O caminho sozinho não é nova verificação de assinatura desse
componente do sistema. O runner com ferramentas instaladas e a extração sem
identidade MSIX impedem concluir que a máquina limpa real já foi comprovada.
Tamanhos por fase incluem instâncias de processos, não apenas PE únicos.

## Licenças, conta Individual e próximo passo

Foram preservados 84 notices/arquivos e metadata de 27 pacotes do builder, sem
relicenciar qualquer dependência. Texto NumPy Windows 2.5.4 foi lido no wheel oficial
com hash idêntico ao notice do MSIX; inclui OpenBLAS/LAPACK e GCC Runtime Exception.
Qt traz famílias **Charts, Graphs, Data Visualization, Quick 3D, Virtual Keyboard
 e Quick Timeline** com fonte consultada GPL3/commercial; não declarar todo bundle
LGPL. Falta comprovar cópias LGPL/GPL, fontes correspondentes, créditos completos e
substituição/relinking com instalação confiável.

Responsável no Brasil, Individual, sem Qt Commercial, código próprio proprietário.
Artifact Signing Public Trust atual admite indivíduos EUA/Canadá, **não Brasil**.
Alternativa: CA pública que aceite pessoa física/Brasil, com verificação legítima,
chave protegida, timestamp e direitos para assinar terceiros. Nenhuma compra/assinatura.
Store mantém Publisher oficial; assinatura MSIX não dispensa confiança dos PE.

Recomendação: **antes de certificar**, aprovar estudo do payload Qt mínimo e prova
LGPL/relinking/EULA, ou obter resposta escrita/contrato Qt Commercial que cubra a
migração de Community e o escopo real. Confirmar direitos/fontes de GEOS e demais
terceiros em ambas as rotas. Depois resolver 78 unsigned necessários e 46 origens,
preservar vendor signatures aceitas, executar suíte/precisão e gerar novo candidato
sob autorização. Só então testar pacote confiável instalado em Windows 11 real,
SAC On/Defender ativo, sem Python/PostgreSQL e fisicamente offline, incluindo helper,
eventos CodeIntegrity 3077/3033, atualização/desinstalação/preservação.

## Testes e controle de escopo

- Auditoria Windows acima: 453 arquivos, identidade/bytes preservados, SignTool,
  probes sintéticos e carregamentos; sem SAC/instalação aprovada.
- CI de qualidade das ferramentas `82160a4`: Windows **158 passaram / 2 skips**,
  Linux **159 passaram / 1 skip**, precisão **22/22**, lint/formatação/parse PowerShell.
- Local: **34 testes focados passaram**, precisão **22/22**, Ruff check/format
  (102 arquivos) e consistência de 453 caminhos/hashes passaram. Sem PostgreSQL.
  O venv inicial precisava de PySide6; o teste falhou por dependência ausente, e
  passou após instalar a versão já prevista em ambiente de build isolado, sem
  alterar dependências do repositório. Há aviso de depreciação Starlette/httpx.
- Core, desktop, server, distribuição/payload, política e licença do projeto preservados
  em relação ao candidato `e3e55be9`; mudanças deste incremento são ferramentas e
  documentação de auditoria. Main e PRs originais intactos; Pages desativado.

Sem merge, compra, novo licenciamento, assinatura, instalação MSIX, upload à Store,
certificação, publicação ou mudança de proteção. Não é conformidade jurídica aprovada.
