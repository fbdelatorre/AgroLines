# Windows 11, Smart App Control e distribuição

## Situação e diagnóstico

**Compatibilidade com Smart App Control ativo ainda não homologada. Não avançar
para a Etapa 3.2 antes de resolver esse bloqueio de aceitação.** O CI Windows testa
comportamento e executa auditoria; seus runners não comprovam Windows 11 com SAC
ativo. Não há instalador profissional assinado nesta entrega.

No ambiente informado pelo usuário, a política `VerifiedAndReputableDesktop`
(`0283ac0f-fff1-49ae-ada1-8a933130cad6`) bloqueou
`numpy\_core\_multiarray_umath.cp312-win_amd64.pyd`, sem assinatura (`NotSigned`),
com eventos Code Integrity 3077/3033. O caminho é uma extensão PE nativa carregada
pelo NumPy. Shapely importa NumPy e GEOS; o servidor importa Shapely durante seu
próprio carregamento. Por isso o bloqueio antecede a inicialização da API.

O usuário informou Python 3.12 e NumPy 2.5.4. Esse relato não identifica a wheel,
origem, hash ou cadeia de todos os demais arquivos. A auditoria registra as versões
e bytes realmente instalados; não atribui o mesmo resultado a qualquer versão.
Instalação pip bem-sucedida, hash da wheel, assinatura do instalador e assinatura
de cada componente são verificações diferentes. Uma assinatura válida também não
comprova reputação ou aceitação pela política ativa.

Não há correção Python que transforme uma biblioteca rejeitada em componente
confiável. Trocar versão sem evidência, renomear/copiar a DLL, adiar a importação
ou ignorar o erro não resolve o requisito. Nenhum script desta entrega modifica
registro, políticas, trust stores, antivírus, arquivos assinados ou logs do Windows.
Não se exige desativar SAC/Defender/WDAC, adicionar exclusões, executar comandos
administrativos para liberar DLLs, usar `Unblock-File` ou mudar ExecutionPolicy.

## Superfície nativa e canais a avaliar

| Componente | Arquivos abrangidos | Situação / decisão |
|---|---|---|
| NumPy | `_multiarray_umath*.pyd`, outras extensões, BLAS e DLLs de `numpy.libs` | O arquivo relatado está sem assinatura e foi bloqueado. Auditar toda a distribuição. |
| Shapely / GEOS | Extensões Shapely e GEOS C/C++ | Não presumir assinatura pela origem PyPI. Mantém-se GEOS e seus algoritmos. |
| Fiona / GDAL | Extensões, GDAL, drivers e dependências transitivas | Auditar DLLs e plugins, não apenas `import fiona`; GDAL aqui é o runtime de Fiona, sem exigir pacote `osgeo`. |
| pyproj / PROJ | Extensões, PROJ e DLLs transitivas | Preservar `proj.db`/grades e versões; repetir testes de SRC/precisão em qualquer build candidato. |
| PySide6 / Shiboken / Qt | `.pyd`, Qt DLLs e plugins (plataforma, imagens etc.) | Identificar assinaturas arquivo a arquivo. Não presumir que todos os módulos Qt têm o mesmo fabricante/assinatura. |
| Qt WebEngine | QtWebEngineProcess.exe, bibliotecas Chromium/Qt e plugins | Validar também o processo filho e mapa real; sandbox Chromium permanece ativo no Windows. |
| Python e outras dependências | python.exe/pythonw.exe, python DLLs, OpenSSL, SQLite, psycopg, Argon2, CFFI, Pydantic, ferramentas nativas | O inventário percorre runtime e ambiente completos, inclusive componentes não pertencentes a pacotes Python. |

O resultado definitivo por arquivo vem de `native-signatures.json`, com SHA-256,
versão/distribuição, tipo Authenticode/catalog, fabricante, thumbprint, timestamp e
verificação online da cadeia. `NotSigned`, assinatura inválida, cadeia desconhecida,
revogação indisponível ou mudança de bytes exigem investigação. Não se carimba toda
uma biblioteca como assinada com base em um único executável.

| Canal candidato | O que oferece | O que ainda precisa provar |
|---|---|---|
| CPython oficial / distribuição oficial Qt / wheels dos mantenedores | Procedência e licenças rastreáveis | Assinatura de todos os arquivos nativos usados e aceitação SAC do conjunto exato. |
| Conda-forge ou distribuição GIS oficial | Conjunto de dependências GIS coordenado | Não implica Authenticode; inventário e homologação iguais. Não vincular a um QGIS externo sem avaliar arquitetura/licenças. |
| Build próprio de fontes verificadas | Controle do conjunto e da assinatura de componentes redistribuíveis | Toolchain, licenças, precisão, certificado de fabricante e cadeia/reputação aceitas. Preservar assinaturas upstream válidas. |
| Microsoft Artifact Signing ou certificado de code signing de CA confiável | Serviço/chave de assinatura com identidade verificável | Elegibilidade, identidade jurídica, cadeia, algoritmos aceitos pela política vigente e teste SAC real; assinatura não garante reputação. |

A escolha inicial é manter Python/GEOS/GDAL/PROJ/Qt e auditar o conjunto exato.
Se faltarem componentes aceitos, produzir distribuição controlada e assinada com
fontes e licenças verificadas. Não instalar certificados autoassinados no computador
do cliente. O pipeline deve conferir suporte do SAC ao certificado/algoritmo escolhido
na documentação vigente; preferir RSA e SHA-256 para essa avaliação. Uma wheel
assinada como arquivo ZIP não substitui a confiança dos PE carregados do seu conteúdo.

## Desenvolvimento enquanto a homologação está pendente

O servidor Linux/PostGIS e os testes Linux já previstos continuam utilizáveis no
ambiente isolado atual. Isso mantém a stack geométrica e o desenvolvimento sem mexer
na segurança do Windows; não é teste de compatibilidade Windows e não executa a DLL
Windows bloqueada por outro carregador. Não se muda a arquitetura do desktop nem se
move o núcleo GIS para a API nesta correção.

No Windows com SAC ativo, primeiro identificar um conjunto efetivamente aceito ou
um build de desenvolvimento assinado e auditado. Enquanto ele não existir, não
recomendar comandos para liberar a extensão rejeitada. Se a única alternativa exigir
alteração arquitetural, apresentar evidência e solicitar aprovação antes de implementá-la.

## Auditoria reproduzível (mantenedores)

Os comandos abaixo são ferramentas de homologação, não passos exigidos do cliente
final. Executar com PowerShell 7 em checkout/ambiente isolado. Um runtime Python
aceito pelo Windows é pré-requisito; o inventário usa somente a biblioteca padrão,
sem importar as bibliotecas GIS bloqueadas. Não instalar pacotes novos antes de
registrar a versão/hash do ambiente que falhou.

```powershell
.\.venv\Scripts\python.exe -m scripts.native_inventory --output evidence\native-inventory.json
.\scripts\Audit-NativeWindows.ps1 -Inventory evidence\native-inventory.json -Output evidence\native-signatures.json
```

Os roots padrão são o ambiente Python e o runtime base. Para instalador futuro,
repetir `--root` para **todos** os diretórios de payload, runtime, plugins, auxiliares
e processos filhos. O relatório só cobre esses roots. Symlinks, falta de permissão,
arquivos alterados e inspeção parcial são falhas, nunca aprovação silenciosa.
`-Strict` retorna falha quando há PE sem assinatura/cadeia verificadas. A cadeia é
consultada com revogação online; falha de rede é evidência incompleta. Um certificado
vencido com assinatura timestamped pode exigir avaliação adicional com SignTool;
o relatório conservador não equivale à decisão final WinVerifyTrust/SAC.

Os relatórios contêm caminhos e eventos potencialmente identificáveis. Guardar em
armazenamento interno; não anexar dados de cliente ao repositório. Inventário e hash
identificam bytes, não autenticam sozinhos o manifesto nem provam SAC.

## Aceitação Windows 11 com SAC ativo

Usar instalação limpa Windows 11 Pro equivalente ao relato, SAC **Ativado**, sem
exceções adicionais de WDAC/Defender. Registrar build, edição, identidade do artefato,
configuração de segurança e captura da página Segurança do Windows. Estado Avaliação
ou Desativado não satisfaz o teste. Não alterar política para alcançar estado de teste.

O helper lê `VerifiedAndReputablePolicyState` e `CiTool -lp -json`, exige evidência
do estado ativo e política informada em enforcement. Consulta sem acesso suficiente
ou mudança de estrutura/ID da política resulta em **não comprovado**, sem elevar
privilégios automaticamente. Não confundir a simples presença da política com ativação.

```powershell
.\scripts\Test-SmartAppControl.ps1 -Python .\.venv\Scripts\python.exe -Inventory evidence\native-inventory.json -OutputDirectory evidence\sac
```

O teste de servidor exige `AGROLINES_DATABASE_URL` em configuração segura já existente,
PostgreSQL/PostGIS de teste migrado até 0005. Não passa senha na linha de comando,
não imprime URL, não migra/recria o banco e executa consultas de leitura antes de
iniciar Uvicorn temporário em loopback. Outros testes usam apenas arquivos/dados
sintéticos e banco efêmero isolado do capturador de interface.

| Teste | Evidência esperada |
|---|---|
| Instalação limpa | Instalador/payload realmente assinados, fabricante/versão corretos, integridade e eventos antes/depois; **pendente: instalador ainda inexistente**. |
| Primeira execução instalada | Desktop e processos filhos reais, sem Python externo/manual; **pendente: build distribuível**. |
| NumPy | Importação e operação array no mesmo runtime. |
| Shapely / GEOS | Importação e distância conhecida. |
| GDAL / Fiona | GDAL runtime disponível e driver SHP; não usar pacote osgeo ausente como falso requisito. |
| PROJ / pyproj | Transformação com referência UTM conhecida. |
| PySide6 | Janela QWidget Windows real. |
| Servidor | Importação, PostGIS acessível e Uvicorn real/HTTP em loopback. |
| Qt WebEngine / Leaflet | Capturas nativas, processo filho, clique real no mapa. |
| Shapefile | SHP/SHX/DBF/PRJ sintéticos, importação e área conhecida. |
| Vértices | Capturador nativo aplica 1 mm, Ctrl+Z/Y e grava nova versão. |
| Precisão | As 22 referências existentes, mesmas tolerâncias e dados originais preservados. |
| Atualização | Release anterior → nova assinada, versão/fabricante, recusa de pacote adulterado e preservação de banco/cadastros/sessões; **pendente: atualizador**. |

Depois de **cada** teste, o script consulta 3077/3033 sem limpar/desativar logs,
registra XML/RecordId/horário e correlaciona nomes nativos inclusive caminhos NT.
Eventos não relacionados permanecem no relatório; correlação conservadora pode
exigir revisão manual. Há nova consulta global ao final para capturar registros
atrasados. Log inacessível/desativado, processo com timeout, alteração de hashes,
SAC não comprovado ou bloqueio relacionado causam falha. Ausência de eventos sozinha
não aprova um teste que não executou. Inspecionar ainda os eventos/manual por período
da instalação, primeira execução e atualização, incluindo componentes do instalador
que não estão nos roots do runtime.

`functional_sac_checks_passed` cobre apenas esses probes executados.
`release_acceptance_proven` permanece falso até existir a evidência de instalação,
primeira execução, atualização e revisão manual. Screenshots/testes comuns de GitHub
Actions, Linux ou offscreen não substituem essa aceitação.

## Plano de instalador e atualização profissional

1. Congelar dependências/fontes/toolchain por versão e plataforma; adquirir de canais
   oficiais com TLS, hashes verificados e licenças/SBOM. Registrar o conjunto exato
   incluindo BLAS, plugins, runtime C/C++, PROJ grids/database e Chromium.
2. Empacotar Python e todas as dependências, sem exigir Python ou pip do cliente.
   Avaliar ferramenta de freezing/instalador em prova técnica; não escolher
   PyInstaller/MSIX como se isso assinasse automaticamente o payload.
3. Preservar assinaturas válidas upstream. Onde redistribuição permitir, assinar PE
   próprios/nativos necessários por serviço de assinatura ou chave protegida, com
   timestamp confiável. Verificar cadeia, revogação e digest; não usar certificado
   autoassinado nem segredo/chave exportável no checkout. SignTool verifica o conjunto
   final (`verify /pa /all /v`); isso ainda não é o teste SAC.
4. Assinar instalador e manifesto de versão/hashes **depois** do processamento final
   dos componentes. Não modificar binários/digests após assinatura. Verificar identidade
   do fabricante e integridade do payload antes de executar componentes instalados.
5. Instalação automática dos pré-requisitos, mensagens claras de fabricante/versão,
   assinatura e erros; sem comandos PowerShell ou exceções de proteção do cliente.
6. Atualizações por HTTPS com manifesto/pacote autenticados, fabricante esperado,
   resistência a downgrade e substituição parcial, staging e recuperação de falha.
   Rejeitar pacote/hash/assinatura adulterados antes de instalar. Backups e migrações
   aditivas preservam dados; nunca reinstalar apagando banco/sessões/propriedades.
7. Homologar os bytes finais em Windows 11/SAC ativo, incluindo download recém-feito,
   instalação limpa, primeira execução e atualização. Repetir matriz geométrica e
   capturas; não promover release por reputação suposta de certificado/empacotador.

Nenhuma destas etapas de release é declarada implementada só porque a auditoria
existe. Faltam identidade jurídica/certificado ou serviço de assinatura configurado,
build distribuível e máquina Windows 11 com SAC ativo para homologação real.

## Referências e limites de pesquisa

Referências oficiais a consultar e reconferir antes do pipeline de release:
[Smart App Control — Microsoft Learn](https://learn.microsoft.com/windows/security/application-security/application-control/smart-app-control/overview),
[Get-AuthenticodeSignature](https://learn.microsoft.com/powershell/module/microsoft.powershell.security/get-authenticodesignature),
[CiTool](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/operations/citool-commands),
[SignTool](https://learn.microsoft.com/windows/win32/seccrypto/signtool).
O acesso ao Microsoft Learn foi bloqueado pela rede do ambiente durante esta entrega;
esses links não são alegação de consulta concluída. O diagnóstico confirmado utiliza
o relato/eventos do usuário; resultados adicionais identificam apenas os arquivos
realmente inspecionados pelo CI e seu ambiente, sem extrapolar ao Windows do usuário.
