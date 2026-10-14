# Auditoria nativa do MSIX original — PR #14

Referência imutável: execução [38615384532](https://github.com/fbdelatorre/AgroLines/actions/runs/38615384532),
MSIX `AgroLines-1.0.0.0-x64-STORE-SUBMISSION-UNSIGNED.msix`, SHA-256
`22286add49d873625f6a3ab898dc2b772b5514dd4fc30cddcfdbcfa369ea2a36`.
Auditoria de 14/10/2026. Não é assinatura, instalação ou aprovação SAC/LGPD/Store.
Política de privacidade e motor permanecem intactos.

## Como reproduzir sem alterar os binários

Workflow `.github/workflows/native-store-audit.yml`: Windows hospedado, download
do artefato original, SHA-256 fixado antes/depois, SDK MakeAppx/SignTool confiáveis,
somente unpack/verify; nenhum sign, instalação de MSIX/certificados ou modificação
de política Windows. O ambiente Linux não conseguiu baixar o ZIP (proxy 403);
a análise/execução do binário ocorre no runner Windows, sem relay de sites bloqueados.

`scripts/native_msix_audit.py` compara cada SHA-256 com o inventário original e
com inputs nativos de wheels fixados pelo lock e CPython 3.12.10. Ausência de match
fica explicitamente não confirmada, sem inventar mantenedor. Grupo lógico do motor
(GDAL/PROJ/GEOS) é distinto do pacote/wheel que o embutiu. O EXE próprio contém
bootloader PyInstaller e Python congelado, não algoritmo GIS nativo reescrito.

O relatório anterior passou `distributions=[]` à coleta, por isso todos os
453 arquivos ficaram `runtime/unowned`; isso não prova origem desconhecida dos
bytes. A atribuição nova usa evidência de hash, evitando classificar toda DLL pelo
nome de um pacote ou atribuir a licença do binding a suas bibliotecas vendorizadas.

Saídas no artefato `agrolines-original-msix-native-audit`:

- `native-audit/inventory.csv` e `.json`: cada caminho relativo, grupo/biblioteca,
  origem/basis, SHA-256, Authenticode, signer/validade, cadeia/elementos/motivos,
  SignTool/raw output, observações de carga e comparação com o inventário original.
- `native-audit/summary.json`: contagens por grupo/motivo/carga, limitações e flags
  de homologação false. JSON inclui lista/hash/tamanho dos notices realmente no pacote.
- `native-signatures.json`, `native-signtool.json`, `native-inventory.json`:
  evidências detalhadas; `native-observations/`: módulos e resultados sintéticos.

## Separar as três verificações de confiança

1. Get-AuthenticodeSignature: decisão Authenticode reportada pelo Windows, certificado
   e timestamp presentes. Não é prova de reputação/SAC.
2. X509Chain.Build genérico: hora atual, revogação Online, sem ignorar erros. É o
   critério conservador que gerou os 150 arquivos sem validação completa, incluindo
   78 não assinados. **72 não são necessariamente falhas de Authenticode**: cadeia
   na hora atual pode diferir de assinatura com timestamp historicamente válido.
3. SDK SignTool `verify /pa /all /v /tw`: política Authenticode/timestamps, stdout,
   stderr, exit code e timeout por arquivo. Código 0 não é homologação SAC; aviso,
   falha ou timeout não são convertidos em aprovação. Não se ajusta data do sistema,
   VerificationTime artificial, trusted roots ou assinatura para obter sucesso.

As causas reais serão obtidas dos resultados, sem presumir que as 72 cadeias
sejam expiradas, revogadas ou indisponíveis antes da execução. Certificado vencido
na cadeia genérica não invalida automaticamente assinatura com timestamp aceito
pelo Windows; preservar assinaturas upstream válidas até avaliação completa.

## Módulos efetivamente observados

Observer externo, leitura Process.Modules e descoberta dos descendentes apenas
dos processos iniciados pela tarefa. Três cenários: início normal da janela offline
sem projeto, smoke/GIS e importação/edição/backup/restauração sintéticos. PATH do
processo limitado a System32; variáveis externas Python/GIS retiradas. Código do
MSIX não é instrumentado, injetado ou modificado. Só fechar/terminar processos
sintéticos criados pela própria tarefa, nunca aplicativos do usuário.

Poll nominal 100 ms + custo de descoberta/leitura: não é trace completo de ImageLoad
nem atribuição precisa a cada algoritmo. Cargas transitórias, saída rápida ou
acesso negado a helper ficam como limitações. **Não observado não significa inútil
ou seguro para remover**. Distinguir módulos do payload, sistema Windows e externos.
Nenhum trace global, tráfego/entrada do usuário ou dados reais coletados.
Runner/extração não comprovam execução em identidade MSIX/Windows 11 com SAC On.

## Licenças e redistribuição — revisão ainda aberta

Fontes oficiais efetivamente lidas e bloqueios constam em [fontes.json](fontes.json).
Notices/metadata do pacote e correspondência com versões reais prevalecem sobre
generalizações. Arquivos vendorizados podem ter licença diferente do pacote Python.

| Componente | Evidência / obrigações a verificar |
|---|---|
| AgroLines/PyInstaller | Bootloader GPL com exceção de distribuição de executável; hooks/runtime têm termos próprios. Não estende exceção a Qt/GIS. Licença/EULA do produto e IP próprios ainda dependem de decisão |
| CPython | LICENSE da tag v3.12.10 conferida; manter textos PSF e terceiros incluídos no runtime. Certificado upstream não elimina licença/redistribuição |
| NumPy/OpenBLAS/GNU runtimes | NumPy BSD-3 conferida; wheel pode incluir OpenBLAS/LAPACK/GCC e exceções com termos próprios. Conferir notices exatos, não aplicar só BSD do NumPy a todos os DLLs |
| Shapely/GEOS | Shapely BSD-3; GEOS LGPL 2.1 e condições de linkage/source/relinking a verificar na versão efetiva. Notices sozinhos não encerram as obrigações |
| pyproj/PROJ | PROJ MIT-style conferida, preservar avisos; revisar dados/grids e outros componentes. Bindings têm seus próprios notices |
| Fiona/GDAL | GDAL LICENSE.TXT agrega termos de partes; revisar codecs/drivers/deps reais, além da licença Fiona. Não presumir licença homogênea do wheel |
| Qt/PySide6/Shiboken | QtBase v6.12.0 declara commercial OR LGPL3 OR GPL2 OR GPL3. QtCharts/QtGraphs v6.12.0 declaram **commercial OR GPL3**, sem alternativa LGPL nesses exemplos. Conferir se esses binários existem; não afirmar que tudo Qt é LGPL |
| Qt WebEngine/Chromium | Há obrigações adicionais/third-party notices e possíveis codecs; docs Qt bloqueados nesta consulta. Sources, versão/build options e mecanismos de cumprimento continuam a revisar, sem afirmar licença comercial adquirida |
| Outros/MSVC/OpenSSL/SQLite | Identificar por arquivo/versão e license/REDIST oficiais; assinatura Microsoft ou licença de Python não é autorização genérica de redistribuir qualquer DLL |

Para LGPL, avaliar fonte correspondente/oferta permitida, alterações, licença,
avisos, possibilidade de substituir/relinkar biblioteca e installation information
quando aplicável. Proteção WindowsApps/assinatura/Store exige análise do mecanismo
de cumprimento; não mandar desativar SAC para satisfazer licença. Modelo comercial
não determina código fechado: escolher LGPL compatível, GPL compatível ou licença
comercial aplicável depende do modelo e da revisão, não desta auditoria.

## Opções legítimas para a conta Individual

- **Store/MSIX:** Microsoft assina o pacote no fluxo aprovado. Preservar Name/Publisher
  oficiais; nunca trocar CN por certificado de outra identidade. Assinatura externa
  cobre integridade do pacote, sem dispensar auditoria de DLL/PYD/EXE e teste SAC.
- **PE internos próprios/redistribuíveis:** certificado público de CA que aceite a
  pessoa física e país reais, com identidade verificada, chave protegida, timestamp
  e verificação. Preservar vendor signatures válidas; avaliar permissão para assinar
  binários terceiros. Não comprar, emitir ou assinar nesta tarefa. Subject do PE
  não precisa ser confundido com Publisher GUID reservado da Store.
- **Artifact Signing Public Trust:** docs quickstart atuais permitem indivíduos
  residentes nos EUA/Canadá. Conta Individual Partner Center não dá automaticamente
  elegibilidade Azure. País do responsável ainda precisa ser confirmado; se Brasil,
  não tratar esse serviço como disponível nem usar endereço/empresa fictícios.
  Private Trust/test signing não fornecem confiança pública dos computadores clientes.
- **Fornecedor/build próprio verificável:** solicitar/avaliar builds oficialmente
  assinados ou compilar fontes permitidas com toolchain/SBOM/precisão preservados e
  assinatura legítima. Não trocar motor/arquitetura ou versões só para esconder falha.

Fonte Microsoft SAC atualizada em 28/09/2026 informa suporte a **RSA e ECC**; não
repetir a regra antiga “somente RSA”. Compatibilidade do algoritmo/cadeia com os
builds Windows alvo exige teste físico; docs atuais não provam qualquer build antigo.
País/elegibilidade CA, existência de licença Qt comercial e modelo do AgroLines
permanecem decisões a confirmar, sem documentos/credenciais no GitHub.

## Próximo passo proposto, sem executá-lo

Concluir tabela real de cargas/causas/licenças; selecionar conjunto mínimo que
preserve GIS/UI, removendo só dependências dispensáveis após testes e aprovação.
Resolver GPL/commercial/LGPL antes de distribuir software proprietário, se esse
modelo for adotado. Preservar signatures/timestamps upstream aceitos, escolher
CA elegível para PE unsigned realmente necessários se permitido, gerar novo inventário
e MSIX para fluxo Store. Em seguida, só com autorização, obter pacote Store confiável
e homologar Windows 11 com SAC **On** e Defender ativo, offline, incluindo helpers,
eventos de integridade e atualização/desinstalação/preservação. Certificação não
é inferida do CI. Política/URLs pendentes e aprovações anteriores continuam abertas.

Este PR prepara/verifica diagnóstico; não altera payload, política, licença adotada,
classificação, identidade, conta Store, proteção Windows ou certificados.
Não há merge, upload/certificação, convite ou publicação. Resultados efetivos e links
serão incorporados após o workflow; existência da ferramenta não prova execução.
