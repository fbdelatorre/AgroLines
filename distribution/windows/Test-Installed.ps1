# Maintenance automation only. The installed application requires no Python or PowerShell.
param(
    [Parameter(Mandatory = $true)][string]$Installer,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [Parameter(Mandatory = $true)][string]$InstallDirectory,
    [switch]$RequireSac
)
$ErrorActionPreference = 'Stop'
$install = [IO.Path]::GetFullPath($InstallDirectory)
if (Test-Path -LiteralPath $install) { throw 'Use diretorio de homologacao novo; nao sobrescrever produto existente.' }
$target = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $target -Force | Out-Null
$started = [DateTime]::Now
if ($RequireSac) {
    . (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'scripts\Windows-Security.ps1')
    $state = Get-AgroSacState
    if (-not $state.active_confirmed) { throw 'SAC ativo nao comprovado. Nao alterar protecoes.' }
    if ((Get-AuthenticodeSignature -LiteralPath $Installer).Status -ne 'Valid') { throw 'Instalador deve ter assinatura valida.' }
}
$setup = Start-Process -FilePath (Resolve-Path -LiteralPath $Installer).Path -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=`"$install`"") -Wait -PassThru
if ($setup.ExitCode -ne 0) { throw 'Instalacao falhou.' }
$executable = Join-Path $install 'app\AgroLinesPoC.exe'
$reportPath = Join-Path $target 'installed-run.json'
if ($RequireSac) {
    foreach ($file in (Get-ChildItem -LiteralPath $install -Recurse -File | Where-Object Extension -in @('.exe','.dll','.pyd'))) {
        if ((Get-AuthenticodeSignature -LiteralPath $file.FullName).Status -ne 'Valid') { throw "PE sem assinatura valida: $($file.Name)" }
    }
}
. (Join-Path $PSScriptRoot 'Run-Frozen.ps1')
Invoke-AgroFrozenProbe -Executable $executable -Report $reportPath
$result = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if (-not $result.frozen -or -not $result.checks_passed -or -not $result.payload_integrity_verified) { throw 'Runtime/precisao/mapa/integridade nao comprovados.' }
if ($RequireSac -and -not $result.sac_run_observed) { throw 'Execucao com SAC ativo nao comprovada.' }
# Retain diagnostic data through uninstall. No agricultural data or database is touched.
$dataDirectory = Join-Path $env:LOCALAPPDATA 'AgroLinesDistributionPoC\evidence'
if (-not (Test-Path -LiteralPath $dataDirectory)) { New-Item -ItemType Directory -Path $dataDirectory -Force | Out-Null }
$marker = Join-Path $dataDirectory ('preservation-' + [Guid]::NewGuid().ToString() + '.txt')
'Synthetic preservation marker' | Set-Content -LiteralPath $marker
$hash = (Get-FileHash -LiteralPath $marker).Hash
$uninstall = Start-Process -FilePath (Join-Path $install 'unins000.exe') -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait -PassThru
if ($uninstall.ExitCode -ne 0 -or (Test-Path -LiteralPath $executable)) { throw 'Desinstalacao falhou.' }
if ((Get-FileHash -LiteralPath $marker).Hash -ne $hash) { throw 'Desinstalacao alterou dados persistentes.' }
if ($RequireSac) {
    $events = @(Get-AgroCodeIntegrityEvents -Since $started)
    $related = @(Convert-AgroCodeIntegrityEvents -Events $events -NativeNames @('AgroLinesPoC.exe','unins000.exe',[IO.Path]::GetFileName($Installer)))
    if (@($related | Where-Object associated_with_inventory).Count -gt 0 -or -not (Get-AgroSacState).active_confirmed) { throw 'Bloqueio/mudanca de SAC durante homologacao.' }
    $related | ConvertTo-Json -Depth 12 | Set-Content (Join-Path $target 'installer-events.json')
}
@{ installed_app_passed = $true; sac_required = [bool]$RequireSac; approved_for_distribution = $false; manual_review_pending = $true } | ConvertTo-Json | Set-Content (Join-Path $target 'installation-summary.json')
Write-Output 'Instalacao, executavel sem Python externo e desinstalacao verificados; aprovacao depende de revisao real.'
