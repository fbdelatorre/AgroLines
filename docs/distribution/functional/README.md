# AgroLines 1.0.0.5 TESTE — compilação e homologação funcional

Registro da etapa do PR #23. O incremento para entrega privada/VM e a candidata
1.0.0.7 estão em [docs/testing/private-installer.md](../../testing/private-installer.md).
O workflow atual evoluiu para essas versões; os hashes/evidências 1.0.0.5 permanecem históricos.

Base: HEAD do PR #22, preservando a cadeia #18 → #19 → #20 → #21 → #22.
Investigação jurídica pausada. Avisos, fontes e gates existentes preservados;
não há aprovação jurídica, comercial ou SAC por passar esta validação.

## Candidato e perfis

Instalador solicitado: `AgroLines-Setup-1.0.0.5-TESTE-x64.exe`.
Uma segunda compilação **1.0.0.6, somente laboratório**, exercita a atualização real.
Não substitui o candidato principal. Ambas usam PyInstaller onedir, Inno Setup,
os locks aprovados, ícones oficiais, exclusões Qt, libaec e os dois pares GEOS.
Python3.12/Qt/WebEngine/Leaflet/GIS/SQLite/cripto são incorporados ao runtime.

- **A — TESTE:** origem e chave pública sintéticas fixadas na compilação,
  `TEST_PROFILE=True`, identificação visível TESTE. Licenças sintéticas assinadas
  são usadas somente pelos probes no builder descartável autorizado. Não há senha
  universal, chave privada embarcada ou configuração que converta produção emteste.
  O endpoint `.test` não é um serviço público implantado; o usuário não conseguirá
  uma ativação real por ele. Provas locais não são handshakeHTTPS de produção.
- **B — produção:** compilação comercial com origemHTTPS real e chaves públicas
  próprias de produção. A origem sintética e o identificador reservado de laboratório
  são recusados. Sem licença válida há somente recuperação de dados; permanecem
  obrigatórias ativação real e assinatura criptográfica. Não foi gerado um produto
  comercial com domínio/segredos inventados. Servidor/admin continuam como no#21.

O mecanismo mensal/anual e duas vagas da mesma assinatura não mudou. Semheartbeat
obrigatório, usooffline até expiração, falhasde rede não revogam, decisão assinada
recebida fica persistida. A emissão Ed25519 não é Authenticode doWindows.

## Instalação e dados

O canal tem AppId próprio e pasta padrão **AgroLines TESTE**, distintos daStore e
do candidatoExperimental anterior. O assistente permite escolher pasta, oferece
atalho opcional na área de trabalho, atalhos Iniciar e desinstalador.
Se a pasta contiver outro AgroLines sem o marcador deste canal, a instalação é
recusada. Uma atualização interativa solicita confirmação, com resposta padrãoNão.
A chamada silenciosa do laboratório é uma autorização explícita de teste.

Cada runtime fica em `versions/<versão>-<candidato>/`; um launcher estável aponta
para a versão ativa. Os runtimes anteriores e atalhos porversão são preservados,
permitindo execução lado a lado na mesma instalação. Isso não significa duas
instalaçõesindependentes com dois registros de desinstalação. Não há configuração
manual dePATH, Python, pip, QGIS, GDAL, PostgreSQL ouDocker no computador cliente.

Projetos/backups ficam fora da instalação. LicençasDPAPI e registro independente
também são externos; as provas usam estado e chavesRegistryLab sintéticos porUUID
fora do runtime, sem tocar contas de clientes. O instalador não tem rotinas para
apagar dados pessoais externos. Desinstalar remove arquivos próprios, não equivale
a excluir projetos ou dados tratados pelo serviço remoto.

Diagnósticos locais em `%LOCALAPPDATA%\AgroLines\Diagnostics\desktop.log`, com
rotação por tamanho (1MiB + duas cópias). Registrode início/fim e tipo/localização
lógica dafalha, sem mensagem deexceção, argumentos, variáveis, credenciais, conteúdo
deprojetos ou upload automático. Falha aogravar log não deve impedir recuperação.
Não se promete retenção por número dedias nem eliminação de backups de terceiros.

## O que o workflow realmente executa

[windows-functional.yml](../../../.github/workflows/windows-functional.yml):

1. Recusa execução unsigned emWindows cliente, SACativo ou ambiente não autorizado;
   lê proteção existente, sem mudá-la. Testa emWindowsServer hospedado descartável.
2. Compila o runtime completo e confere materiais, origens, DLLs/PYDs e manifestos.
3. Executa o EXE congelado, GUI, WebEngine/Leaflet, formatosGIS, edição, histórico,
   backup/restauração, cripto/DPAPI, revogação e concorrência. PATH é limitado ao
   sistema; variáveis de desenvolvimento são removidas. Observa módulos do processo
   e descendentes, recusando dependência não sistêmica externa ao payload. Amostragem
   de módulos não é um trace exaustivo de todo carregamento transitório.
4. Compila o instalador1.0.0.5 e o sucessor1.0.0.6 com compiladorInno oficial
   cuja assinatura e hash são verificados; não assina os artefatosAgroLines.
5. Instala em caminho com espaços/acentos, lança cópia descartável do atalho
   Windows com argumentos explícitos deprobe, reabre estado, atualiza, executa ambos
   runtimes instalados, desinstala e reinstala, verificando projetos/backup/DPAPI.
   A cópia permite automação e não altera o atalho original do menuIniciar.
6. Registra versão instalada, tamanhos, contagensDLL/PYD, hashes, resultados e logs.

As suítes gerais Windows/Linux preservam as22referências computacionais e as
regras do servidor. Precisão de campo e compatibilidade Windows11/SAC exigem
homologação própria. O ciclo instalado não demonstraTLS público nem dois PCs físicos.

## Artefatos e acesso restrito

Este repositório é público. **Nenhum instalador, runtime, código próprio empacotado
ou kit completo de fontes é enviado como artefato público.** O workflow envia só
`evidence/`: relatóriosJSON, manifests/hashes e logs sintéticos. Os binários existem
no disco temporário do builder durante o job e não são retidos após sua destruição.
Portanto não há link público legítimo de download do instalador nesta entrega.

Para disponibilizar o candidato a pessoas autorizadas, o titular precisa escolher
um builder/repositório de distribuição privado ou armazenamento restrito aprovado.
Reexecutar a receita nesse ambiente, guardar onedir e instaladores com os manifests,
controlar acesso e retenção e conferir os hashes após transferência. Não basta
exigir loginGitHub em artefato de repositório público; isso não restringe aos testadores.
Nenhum repositório, segredo, fornecedor ou configuração protegida foi criado aqui.

Os workflows antigos não recompilamPoC/MSIX para esta branch: a nova execução
substitui só as tarefas duplicadas desta candidata. Qualidade e gatesdocumentais
continuam. O uploadgenérico standalone de binários exige repositório privado e
autorização explícita, sem alterar essas configurações automaticamente.

## Homologação real futura

**Não instale o unsigned na máquina principal ou emWindows11 comSAC ativo.**
Depois de decidir confiança/assinatura legítima e forma privada de entrega:

1. Conferir assinatura, hash, origem e versão; não adicionar certificados de teste.
2. EmWindows11 descartável comSAC/Defender/SecureBoot preservados, semPython/QGIS/
   PostgreSQL, instalar, abrir pelo atalho e ativar no endpointHTTPS autorizado.
3. Desconectar fisicamente a rede; cumprir a[matriz funcional](matriz.md).
4. Atualizar mantendo projetos/ativação, executar versões anteriores quando cabível,
   desinstalar/reinstalar e confirmar os dados. Conferir logs eCodeIntegrity.
5. Repetir licenciamento emdoisPCs e recusar terceiro, renovação, revogação após
   reconexão, falhasde rede e recuperação apósvencimento. Sem comprovação deSAC porCI.

Estados distintos: **compilado**, **instalado no laboratório**, **funcional nos
cenários testados**, **disponível para teste físico autorizado** e **homologado para
distribuição**. Somente o relatório da execução aprovada pode afirmar os três
primeiros. Os dois últimos permanecem condicionados aos passos acima e revisões.
