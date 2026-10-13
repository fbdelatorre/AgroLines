param([switch]$Desktop)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3.12 -m venv .venv
        } else {
            & python -c "import sys; assert sys.version_info[:2] == (3,12), 'Instale Python 3.12'"
            if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 obrigatorio.' }
            & python -m venv .venv
        }
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar ambiente Python 3.12.' }
    }
    $python = Join-Path $root '.venv\Scripts\python.exe'
    & $python -c "import sys; assert sys.version_info[:2] == (3,12)"
    if ($LASTEXITCODE -ne 0) { throw 'O ambiente existente deve usar Python 3.12.' }
    $extras = '.[dev]'
    if ($Desktop) { $extras = '.[dev,desktop]' }
    & $python -m pip install -e $extras
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependencias.' }
    & $python -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependencias incompativeis.' }
    Write-Host 'Configuracao concluida. Execute scripts\Start-Server.ps1 apos preparar PostgreSQL/PostGIS.'
} finally {
    Pop-Location
}
