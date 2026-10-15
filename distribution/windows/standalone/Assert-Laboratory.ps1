# Only the explicitly authorized disposable Actions builder may run the unsigned tree.
# Read state, refuse client/unknown/active SAC; never change a protection setting.
$ErrorActionPreference = 'Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_ENVIRONMENT -ne 'github-hosted') {
    throw 'Unsigned experiment restricted to disposable GitHub-hosted build environment.'
}
. (Join-Path $PSScriptRoot '../../../scripts/Windows-Security.ps1')
$os = Get-CimInstance Win32_OperatingSystem
$sac = Get-AgroSacState
if ($os.ProductType -eq 1 -or $sac.active_confirmed -or $sac.registry_state -eq 1) {
    throw 'Unsigned execution refused on Windows client or active SAC.'
}
$defender = $null
try { $defender = Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled } catch {}
New-Item evidence/standalone -ItemType Directory -Force | Out-Null
@{ os=($os | Select-Object Caption,Version,BuildNumber,ProductType); sac=$sac; defender=$defender; protections_modified=$false; physical_windows11_validated=$false; agrolines_installer_executed=$false } |
    ConvertTo-Json -Depth 12 | Set-Content evidence/standalone/laboratory.json -Encoding utf8
