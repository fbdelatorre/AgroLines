# AgroLines standalone offline — experimental

Perfil `standalone-offline`, Windows 11 x64 (build 22000 ou posterior), Python
3.12 integrado pelo PyInstaller **onedir** e Inno Setup. Não requer Python, pip,
PostgreSQL nem login no cliente. O aplicativo usa os mesmos módulos GIS, projetos
SQLite `.agrolines`, mapa local, edição, histórico e backups da base dos PRs #14–#17.
Nenhum algoritmo ou formato foi reimplementado. Não utiliza inscrição, assinatura
ou instalação da Microsoft Store. O MSIX de referência e sua identidade permanecem
intactos; este é outro candidato, com nome e hashes próprios.

**Não instalar/distribuir o experimento sem assinatura.** O artefato serve para
inspeção do build. Executamos a árvore extraída somente no builder descartável
autorizado. Compilar um instalador não comprova instalação, atualização,
desinstalação, segurança SAC ou conformidade comercial.

## Layout e dados

```text
Program Files/AgroLines Experimental/
  versions/<versão>-<commit de build>/
    AgroLines.exe
    _internal/           # layout original do PyInstaller, sem achatamento
      python312.dll
      PySide6/           # .py, .pyd, DLLs, plugins, recursos/WebEngine
      shiboken6/         # fontes Python dos módulos coletados + extensões
      fiona/ ...         # GDAL/GEOS/PROJ/NumPy e dependências preservadas
    third-party-notices/
    standalone-docs/
    native-signing-policy.json
    standalone-layout.json
    payload-manifest.json
  uninstall/
```

O instalador pede elevação para Program Files; a execução cotidiana não pede
administração. Atalhos Iniciar/área de trabalho apontam para a versão instalada.
Interface do instalador em português brasileiro. Não há abertura automática do
experimento ao concluir a instalação. A identidade experimental é distinta da
PoC anterior e do MSIX, inclusive para desinstalação.

Projetos padrão continuam em `%LOCALAPPDATA%\AgroLines\Projects`; projetos e
backups também podem ficar em caminhos locais escolhidos pelo usuário. O
instalador não cria banco, não migra dados e não apaga esses caminhos. Não salvar
projetos dentro de Program Files. A desinstalação remove somente os arquivos
instalados e atalhos; arquivos novos/modificados pelo usuário exigem inspeção.
**Preservação real em atualização/desinstalação aguarda teste controlado.**

Atualização inicial: instalador completo, sem serviço de atualização ou internet
obrigatória. Cada versão/commit tem pasta própria para evitar mistura de DLLs;
versões anteriores ficam até a desinstalação. Não há rollback automático, launcher
novo nem protocolo de downgrade homologado. Fechar o programa e guardar backup
antes de atualizar. O Restart Manager do Inno solicita fechamento quando necessário;
validar esse comportamento com arquivos abertos, cancelamento e múltiplos usuários.

## Build autorizado

Workflow `.github/workflows/windows-standalone.yml`, somente compilação experimental:

```text
python -m venv build-env
build-env/Scripts/python.exe -m pip install --require-hashes --only-binary=:all: -r distribution/windows/requirements.lock
build-env/Scripts/python.exe -m distribution.build --standalone --version 1.0.0.1
distribution/windows/Build-Installer.ps1 -Standalone -Experimental -Version 1.0.0.1 -CandidateId <12 caracteres hex do commit> -Compiler <ISCC.exe verificado> -PythonExecutable <Python do builder>
```

São comandos do mantenedor, não instruções ao cliente. O workflow fixa CPython,
wheels/hashes e o Inno 7.1.0 oficial, verifica SHA-256 e Authenticode do compilador,
preserva exclusões Qt e gera inventário/SignTool, provas GIS/offline e hashes finais.
Não acessa certificado ou chave, não executa o instalador AgroLines, não publica
release/Pages/Store e não faz merge. Inno é ferramenta de build; seus componentes
de runtime incorporados e textos originais de licença são preservados.

Os artefatos são baixados em **Actions → Windows standalone offline experimental
→ execução → Artifacts → agrolines-standalone-EXPERIMENTAL-UNSIGNED**. Contêm
`dist/installers/*.exe`, árvore `dist/AgroLines/` e `evidence/`. A evidência associa
arquivo, versão, commit, tamanho e SHA-256; conferir todos antes de qualquer teste
autorizado futuro. A presença no Actions não é autorização de distribuição.

Ver [LGPL](lgpl-replacement.md) e [assinatura/homologação](validation-and-signing.md).
