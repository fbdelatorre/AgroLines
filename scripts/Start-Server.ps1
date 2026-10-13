param(
    [string]$DatabaseHost = '127.0.0.1',
    [int]$DatabasePort = 5432,
    [string]$DatabaseName = 'agrolines',
    [string]$DatabaseUser = 'agrolines',
    [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Execute scripts\Configure.ps1 primeiro.' }
Push-Location $root
$originalUrl = $env:AGROLINES_DATABASE_URL
$originalTemporary = $env:AGROLINES_SETUP_DB_PASSWORD
try {
    if (-not $env:AGROLINES_DATABASE_URL) {
        $securePassword = Read-Host 'Senha da conta PostgreSQL (nao sera gravada em arquivo)' -AsSecureString
        try {
            $env:AGROLINES_SETUP_DB_PASSWORD = [System.Net.NetworkCredential]::new('', $securePassword).Password
            $env:AGROLINES_DATABASE_URL = & $python -c "import os,sys; from sqlalchemy import URL; print(URL.create('postgresql+psycopg',username=sys.argv[1],password=os.environ['AGROLINES_SETUP_DB_PASSWORD'],host=sys.argv[2],port=int(sys.argv[3]),database=sys.argv[4]).render_as_string(hide_password=False))" $DatabaseUser $DatabaseHost $DatabasePort $DatabaseName
            if ($LASTEXITCODE -ne 0) { throw 'Falha ao configurar conexao.' }
        } finally {
            if ($null -eq $originalTemporary) {
                Remove-Item Env:AGROLINES_SETUP_DB_PASSWORD -ErrorAction SilentlyContinue
            } else { $env:AGROLINES_SETUP_DB_PASSWORD = $originalTemporary }
            if ($securePassword) { $securePassword.Dispose() }
        }
    }
    # Additive versioned migration only: never creates/drops the database or erases user data.
    & $python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Migracao falhou. Servidor nao sera iniciado.' }
    & $python -m uvicorn server.main:app --host 127.0.0.1 --port $Port
    if ($LASTEXITCODE -ne 0) { throw 'Servidor encerrado com erro.' }
} finally {
    if ($null -eq $originalUrl) {
        Remove-Item Env:AGROLINES_DATABASE_URL -ErrorAction SilentlyContinue
    } else { $env:AGROLINES_DATABASE_URL = $originalUrl }
    Pop-Location
}
