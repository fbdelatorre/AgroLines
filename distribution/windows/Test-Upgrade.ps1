# Test an installed PoC update. No customer database is created or changed.
param(
    [Parameter(Mandatory = $true)][string]$FirstInstaller,
    [Parameter(Mandatory = $true)][string]$NextInstaller,
    [Parameter(Mandatory = $true)][string]$InstallDirectory,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$data = Join-Path $env:LOCALAPPDATA 'AgroLinesDistributionPoC\evidence'
New-Item -ItemType Directory -Path $data -Force | Out-Null
$marker = Join-Path $data ('upgrade-preservation-' + [Guid]::NewGuid().ToString() + '.txt')
'Synthetic existing data' | Set-Content -LiteralPath $marker
$markerHash = (Get-FileHash -LiteralPath $marker).Hash
. (Join-Path $PSScriptRoot 'Run-Frozen.ps1')
if (Test-Path -LiteralPath $InstallDirectory) { throw 'Diretorio deve estar vazio.' }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
foreach ($setup in @($FirstInstaller,$NextInstaller)) {
    $p = Start-Process -FilePath (Resolve-Path $setup).Path -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=`"$InstallDirectory`"") -Wait -PassThru
    if ($p.ExitCode -ne 0) { throw 'Instalacao/atualizacao falhou.' }
    $name = if ($setup -eq $FirstInstaller) { 'before' } else { 'after' }
    $output = Join-Path $OutputDirectory "$name.json"
    Invoke-AgroFrozenProbe -Executable (Join-Path $InstallDirectory 'app\AgroLinesPoC.exe') -Report $output
    $report = Get-Content $output -Raw | ConvertFrom-Json
    if (-not $report.checks_passed -or -not $report.payload_integrity_verified) { throw 'Atualizacao incorreta.' }
}
$before = Get-Content (Join-Path $OutputDirectory 'before.json') -Raw | ConvertFrom-Json
$after = Get-Content (Join-Path $OutputDirectory 'after.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $marker).Hash -ne $markerHash) { throw 'Atualizacao alterou dados persistentes.' }
if ($before.metadata.version -eq $after.metadata.version) { throw 'Versao nao foi atualizada.' }
$p = Start-Process (Join-Path $InstallDirectory 'unins000.exe') -ArgumentList @('/VERYSILENT','/NORESTART') -Wait -PassThru
if ($p.ExitCode -ne 0) { throw 'Desinstalacao falhou.' }
Write-Output 'Atualizacao de versao e verificacao do payload passaram; nao implementa atualizador remoto.'
