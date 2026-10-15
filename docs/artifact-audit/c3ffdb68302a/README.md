# Auditoria do artefato c3ffdb68302a — não autorizado para distribuição

**Resultado: integridade estática confirmada no escopo abaixo; homologação Windows,
confiança SAC e conformidade comercial não demonstradas.** Nenhuma instalação,
assinatura, alteração de segurança, merge ou publicação foi executada. Data: 15/10/2026.

## Objeto e cadeia de evidências

| Objeto | Identificação conferida |
| --- | --- |
| ZIP | `agrolines-signing-validation-NOT-FOR-SUBMISSION.zip`; 239270043 bytes; SHA-256 `daad44ae384df63c357225474e531bf8d7ba39205212b3b0c8a02b97a82679e1` |
| MSIX contido | `AgroLines-1.0.0.0-x64-CONFORMIDADE-c3ffdb68302a-DIAGNOSTICO-ASSINATURA-PENDENTE.msix`; 240694735 bytes; SHA-256 `e6a2ab8e65a91df3a2a1613d22b3ecc3c478d774e1d08b39561960085686068b` |
| Código do build | `c3ffdb68302a0c46e640e68dc0b561acce250e6d`; árvore `9da9efcecd00b510ec5732efe9efa47959d947ce` |
| Origem | [Actions 38657579756](https://github.com/fbdelatorre/AgroLines/actions/runs/38657579756), [artefato 11938080390](https://github.com/fbdelatorre/AgroLines/actions/runs/38657579756/artifacts/11938080390) |

O SHA do ZIP baixado coincide com o digest informado pelo GitHub; o do MSIX coincide
com input-binding.json e package-1.0.0.0.json. O ZIP tem 26 entradas e o MSIX 804.
Foram verificados 768 caminhos/hashes do payload, 802 arquivos no AppxBlockMap
(blocos SHA-256 de 64 KiB e FileHash quando presente), 178 cabeçalhos PE x64 e suas
tabelas de certificados, 40 avisos indexados e as três cópias da política.
Esses hashes não fornecem autenticidade independente do canal GitHub nem equivalem
a análise antimalware, autenticação criptográfica Windows atual ou certificação.

O SHA de execução informado pela API é `cecd02a43a03f8dff08fb8706f8923afcbbb1aae`
(PR #15). O checkout usa o merge de teste c3ffdb, cujos pais são
`c7e32477e51a0ece2c304afe2a549abcdb76af22` e cecd02a. **As árvores c3ffdb e cecd02a
são iguais.** Esse objeto histórico não foi integrado à main nesta auditoria.
O relatório de embalagem conserva o nome anterior `STORE-SUBMISSION-UNSIGNED`;
o workflow renomeou o arquivo posteriormente. O hash confirma a mesma sequência de bytes.

Identidade: `DelatorreCOrporation.AgroLines`, Publisher
`CN=43189595-B928-4D57-90A4-24300E4D4976`, versão **1.0.0.0 x64**.
PFN esperado `DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg`, Store ID `9NRDJ3ZTM978`.
Windows.Desktop mínimo 10.0.22000.0; MaxVersionTested 10.0.26100.0.
`runFullTrust` corresponde ao aplicativo desktop e helpers; `unvirtualizedResources`
acompanha exclusão restrita de LocalAppData/AgroLines. Necessidade/aceitação desta
segunda capacidade e preservação real dos dados ainda exigem validação; não é
permissão para ampliar exclusões. Não há AppxSignature.p7x nem CodeIntegrity.cat
nesta cópia. Nenhum deles deve ser inventado ou instalado como certificado de teste.

## Resultado das assinaturas: os conjuntos se sobrepõem

**178 = 100 Authenticode Valid (histórico SignTool) + 78 NotSigned.**
**106 cadeias não completas = 78 sem signatário + 28 assinados com NotTimeValid.**
As outras 72 cadeias foram aceitas pela consulta X.509 genérica histórica.
Não são 184 arquivos diferentes, nem 106 assinaturas necessariamente defeituosas.

| Grupo do inventário | PE | Sem assinatura | Cadeia genérica não válida | Observados carregados | Risco e encaminhamento |
| --- | ---: | ---: | ---: | ---: | --- |
| Python/runtime incorporado | 26 | 0 | 26 | 22 | Expiração atual com timestamp aceito no histórico; repetir verificação confiável atual, sem ignorar expiração/revogação |
| Qt e runtimes associados | 70 | 0 | 0 | 40 | Assinados não garante SAC; licenças de módulos/plugins/Chromium e mecanismo LGPL ainda exigem fechamento |
| Fiona/GDAL e vendorizados | 39 | 38 | 39 | 39 | Origem conhecida; confiança da cópia Store e licenças de cada vendor ainda pendentes; inclui um MSVC expirado na consulta genérica |
| pyproj/PROJ e associados | 19 | 18 | 18 | 19 | Origem conhecida; conferir cobertura/confiança real, grids/fontes e rede nativa |
| Shapely/GEOS e associados | 8 | 7 | 7 | 8 | Duas famílias GEOS distintas; LGPLv2.1 e substituição sob MSIX não demonstradas |
| NumPy/BLAS e associados | 15 | 14 | 15 | 4 | Origem conhecida; inclui outro MSVC com NotTimeValid; BLAS/LAPACK/runtime exigem avisos próprios |
| Executável próprio | 1 | 1 | 1 | 1 | Bootloader/runtime compilado não confiável por si; precisa rota legítima de distribuição e teste real |
| **Total** | **178** | **78** | **106** | **133** | **Não aprovado para distribuição** |

“Grupo” é agrupamento operacional, não licença: Qt inclui CRT Microsoft; Python
inclui OpenSSL/libffi/SQLite; GEOS inclui extensões do Shapely. Consulte os caminhos,
versões, signatários, flags, fases e hashes em [native-files.csv](native-files.csv)
e [native-files.json](native-files.json). O JSON conserva o stdout histórico do
SignTool e as cadeias por arquivo, sem executar os binários.

Dos 78 unsigned, **77 são de terceiros e um é próprio; 67 foram observados**.
Onze não observados não são dispensáveis por essa razão. Os 177 PE de terceiros
coincidem byte a byte com entradas do builder fixado; nenhum PE tem origem de
builder pendente. Isso distingue bibliotecas oriundas de builds identificados de projetos
legítimos de arquivos desconhecidos, mas **não atesta ausência de vulnerabilidades,
malware, licença suficiente ou correspondência completa com fontes upstream**.
Não foi executada varredura antimalware/CVE neste trabalho; não se atribui risco
zero nem se recomenda assinar indiscriminadamente bibliotecas de terceiros.

### Os 28 NotTimeValid

São 26 arquivos do runtime Python, mais MSVC nas pastas fiona.libs e numpy.libs.
Audit-NativeWindows.ps1 usa X509Chain.Build no relógio atual, revogação Online,
ExcludeRoot e timeout de cinco segundos. Essa consulta não reproduz a verificação
Authenticode com o contexto do carimbo de tempo. Todos os 28 possuem timestamp e
SignTool `verify /pa /all /v /tw` exit 0 registrado. Não apareceram outras flags
nesses 28. A classificação é **expiração atual / assinatura historicamente aceita**,
não certificado revogado, digest inválido ou cadeia atual integralmente aprovada.

Exemplo `_asyncio.pyd`: signatário PSF com validade até 11/04/2025, timestamp em
08/04/2025, intermediária com validade até 13/04/2026; a consulta ocorreu em
15/10/2026. O SignTool validou o timestamp. Seu “Hash of file” é o digest Authenticode
SIP; difere legitimamente do SHA-256 integral registrado no inventário. Não comparar
os dois como se fossem o mesmo algoritmo de cobertura.

A auditoria atual Linux confirma bytes e coerência dos relatórios, **não refaz**
a confiança/revogação Windows. Nenhuma flag de validade foi desabilitada.

## Leitura dos demais resultados

- [Reprodução: prova obtida e lacuna real](reproducibility.md).
- [Licenças e privacidade: revisão vinculada ao snapshot](licenses-privacy.md).
- [Ensaios Windows preparados, gates e critérios](windows-acceptance.md).
- [Correções propostas e bloqueios](blockers-corrections.md).
- [Resultado verificável](audit.json) e [procedimento da ferramenta](../../../tools/artifact-audit/README.md).

Os registros de runtime provam execução **descompactada**, frozen, Qt WebEngine e
Leaflet locais, cinco formatos GIS, edição/reabertura/backup e 22 referências
computacionais. Registram também `packaged=false`, validação MSIX/SAC/rede nativa
física não demonstradas. A presença de libcurl/libpq nos vendors não prova conexão
remota ou exigência de servidor PostgreSQL; exige observar seu uso. O modo offline
não habilita login/colaboração. Um manifesto sem internetClient não bloqueia rede
Win32 e não é prova offline.

O run original informa **224 testes Windows aprovados, 2 skips**. Evidências Linux
e laboratórios Windows posteriores estão no PR #16 e são identificadas como
posteriores: QtCore sintético modificado; GEOS sintético e consumidor congelado.
Não retroagem aprovação para esta cópia nem demonstram recombinação do AgroLines.
Resultados desta nova auditoria constam em [validation.json](validation.json) e
[ci-results.json](ci-results.json): auditor estático e 16 controles aprovados em
Windows/Linux; suíte existente Windows 224/2 skips, Linux 225/1 skip, precisão
22/22 em ambos. Estes resultados pertencem ao SHA de código explicitado no registro;
commits posteriores apenas documentais não mudam o candidato.
