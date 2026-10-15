# Only the explicitly authorized disposable Actions builder may run the unsigned tree.
# Read state, refuse client/unknown/active SAC; never change a protection setting.
param([switch]$AuthorizedHyperVBuildVM,[switch]$BuildOnly)
$ErrorActionPreference = 'Stop'
if (-not $AuthorizedHyperVBuildVM -and ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_ENVIRONMENT -ne 'github-hosted')) {
    throw 'Unsigned experiment restricted to disposable GitHub-hosted build environment.'
}
. (Join-Path $PSScriptRoot '../../../scripts/Windows-Security.ps1')
$os = Get-CimInstance Win32_OperatingSystem
$sac = Get-AgroSacState
$localBuild=$AuthorizedHyperVBuildVM -and $BuildOnly
if ($AuthorizedHyperVBuildVM -and -not $BuildOnly) { throw 'Local VM authorization is build-only; it never permits unattended product installation.' }
if (($os.ProductType -eq 1 -and -not $localBuild) -or $sac.active_confirmed -or $sac.registry_state -eq 1) {
    throw 'Unsigned execution refused on Windows client or active SAC.'
}
$defender = $null
try { $defender = Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled } catch {}
if ($localBuild) {
    $computer=Get-CimInstance Win32_ComputerSystem
    $tpm=Get-Tpm
    if ($computer.Manufacturer -ne 'Microsoft Corporation' -or $computer.Model -ne 'Virtual Machine' -or
        $os.ProductType -ne 1 -or $sac.registry_state -ne 0 -or -not $defender.RealTimeProtectionEnabled -or
        -not (Confirm-SecureBootUEFI) -or -not $tpm.TpmPresent -or -not $tpm.TpmReady) {
        throw 'Local build requires explicitly authorized Hyper-V Windows VM, SAC already off by owner decision, Defender/Secure Boot/vTPM active. Nothing was changed.'
    }
}
New-Item evidence/standalone -ItemType Directory -Force | Out-Null
@{ os=($os | Select-Object Caption,Version,BuildNumber,ProductType); sac=$sac; defender=$defender; authorized_local_build_vm=[bool]$localBuild; protections_modified=$false; physical_windows11_validated=$false; agrolines_installer_executed=$false } |
    ConvertTo-Json -Depth 12 | Set-Content evidence/standalone/laboratory.json -Encoding utf8
