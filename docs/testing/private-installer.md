# Instalador privado para a VM Windows 11

Base: PR #23, `0b530d7933baa8f9d72ff32ae749b6b231dd3c35`. A cadeia #18–#23,
o motor GIS e os controles/documentos jurídicos anteriores permanecem preservados.
Esta etapa não aprova distribuição comercial nem reabre a auditoria jurídica.

## Versões

O novo cliente inclui diagnóstico revisável e confiança TLS de laboratório.
Portanto a candidata passa a **1.0.0.7 TESTE**; **1.0.0.8** é o sucessor de teste.
A versão 1.0.0.6 já havia sido usada no #23. O instalador é
`AgroLines-Setup-1.0.0.7-TESTE-x64.exe`. O candidato 1.0.0.5 e suas evidências
continuam como referência, sem sobrescrever ou reapresentar seu hash como novo.

## Situação da entrega

O repositório `fbdelatorre/AgroLines` é público. Nenhum instalador ou runtime é
enviado aos seus artefatos. Ainda é necessário o titular **selecionar e autorizar
um repositório privado** ou executar a compilação local autorizada abaixo.
Não foi criado recurso externo, copiado código para outro repositório, concedido
acesso ou mudada visibilidade. Não existe link privado de instalador antes disso.

## Opção preferencial: repositório privado do titular

1. O titular cria ou seleciona um repositório com **Visibility: Private** e autoriza
   expressamente a cópia desta revisão. A presente preparação não realiza a cópia.
   Restrinja colaboradores e acesso de terceiros/Apps; não mude a visibilidade
   enquanto os artefatos existirem. Exigir login em repositório público não basta.
2. Prepare o [servidor sintético](test-license-lab.md), na infraestrutura privada
   escolhida pelo titular. Copie somente os quatro arquivos de `client-build-inputs/`
   para uma pasta do checkout privado, por exemplo `lab-public/`. Embora contenham
   somente material público e fixtures sintéticas, não publique os arquivos aqui.
   Nunca copie `test-accounts.json`, SQLite ou arquivos privados do servidor.
3. Coloque a revisão revisada e os workflows na branch padrão **desse repositório
   privado**, sem merge na main do AgroLines público. O botão de execução manual do
   GitHub exige o workflow na branch padrão do destino. Essa operação depende da
   autorização do titular; não é feita automaticamente por este PR.
4. No destino privado: **Settings → Secrets and variables → Actions → Variables →
   New repository variable**. Nome `AUTHORIZED_TEST_BINARY_UPLOAD`, valor `true`.
   Não é segredo. Nenhum token pessoal deve ser incluído nos arquivos ou artefatos.
5. **Actions → Private Windows VM installer delivery → Run workflow**. Escolha a
   revisão autorizada; em `authorized_repository` informe exatamente `dono/nome` do
   destino; em `public_lab_inputs` informe `lab-public` (ou o caminho relativo real).
6. O workflow consulta a API do próprio GitHub e exige `private=true`,
   `visibility=private`, nome exato, variável habilitada e execução manual.
   Repete a verificação antes do empacotamento privado. Erro/estado desconhecido,
   repositório público/interno ou falta de autorização interrompem a entrega.
7. Depois de todos os testes passarem, baixe, na execução privada, o artefato
   **`agrolines-vm-1.0.0.7-PRIVATE-UNSIGNED`**, disponível por **7 dias**. Só pessoas
   autorizadas com acesso ao repositório devem poder baixá-lo. Administre também
   as cópias já baixadas. O workflow não restringe decisões futuras de um administrador.
8. O ZIP contém os dois instaladores, SHA-256, manifestos por versão, relatório de
   dependências, resultados, logs Inno e estes roteiros. **Build logs completos:**
   na mesma execução privada, menu da execução → **Download log archive**.
   A origem exata/commit está nos relatórios e na metadata do aplicativo.
   Confira `handoff-manifest.json` e o hash do EXE após transferir para a VM.

O workflow reutiliza o pipeline funcional do #23; não precisa de certificado
Authenticode nesta fase. Nenhum segredo do servidor é necessário no Actions.
Usar runner privado exigiria configuração explícita adicional e proteção dos
dados desse runner; **não foi cadastrado ou selecionado um self-hosted runner**.

## Alternativa: compilação local em VM de desenvolvimento Hyper-V

Use uma **segunda VM de build**, autorizada e descartável, com acesso restrito e
disco suficiente para as ferramentas e builds. Não é a VM limpa de homologação.
Nesta VM de build são necessários Python 3.12 x64, Git, PowerShell 7, MSVC x64
(Visual Studio Build Tools com C++/Windows SDK/CMake/Ninja) e Git CLI. Obtenha os
instaladores oficiais assinados. Não instale ferramentas de desenvolvimento na
VM destinada à prova de ausência de dependências.

Abra PowerShell 7 **dentro da VM de build**, no checkout autorizado desta revisão:

```powershell
python -m venv build-env
./build-env/Scripts/python.exe -m pip install --require-hashes --only-binary=:all: -r distribution/windows/requirements-commercial.lock
./build-env/Scripts/python.exe -m pip check
./distribution/windows/standalone/Build-PrivateVM.ps1 -PublicLabInputs 'C:/AgroLines-Privado/Lab/client-build-inputs' -AuthorizedHyperVBuildVM
```

Antes de rodar, confirme manualmente `python --version` (3.12 x64) e a revisão
com `git rev-parse HEAD`. O script exige Hyper-V, Defender/Secure Boot/vTPM ativos
e SAC **já desligado por decisão explícita do titular na VM descartável**, pois
testes upstream executam bibliotecas recém-compiladas sem assinatura. Se SAC estiver
ativo, em avaliação ou desconhecido, ele para e não modifica nada. A decisão sobre
SAC deve seguir o [checkpoint e registro inicial](windows11-vm-checklist.md).
Não use esse caminho no hospedeiro. A autorização é **somente build**: não libera
o teste silencioso de instalação do Server em Windows cliente.

Os EXEs ficam em `dist/installers/`, os relatórios em `evidence/functional/` e o
último runtime em `dist/AgroLines/`. O script não sobe arquivos, instala ou abre o
AgroLines. Copie os EXEs e relatórios diretamente para pasta privada escolhida pelo
titular; use o SHA-256 registrado. Logs podem ser guardados por transcrição da sessão
de build, **sem transcrever a preparação de chaves/contas do servidor**.
Não se declara esse caminho local validado até executá-lo em Hyper-V real.

## Instalação manual

Siga o [checklist detalhado](windows11-vm-checklist.md). O instalador é experimental
e não assinado. Se SAC bloquear, registre o fato. Não instale certificados, não
crie exclusões e não tente contornar o bloqueio do Windows hospedeiro.
Dados e backups ficam fora da instalação; runtime fica em `versions/<versão>-<commit>/`.
O canal é **AgroLines TESTE**, com desinstalador próprio e atalhos por versão.
Não é versão Microsoft Store e não há pacote MSIX novo nesta etapa.
