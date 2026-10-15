# FUTURE PHYSICAL HOMOLOGATION ONLY. Never called from CI. No protection changes.
[CmdletBinding()]
param(
    [switch]$AuthorizeSyntheticInstallation,
    [Parameter(Mandatory)][string]$FirstInstaller,
    [Parameter(Mandatory)][string]$FirstSha256,
    [Parameter(Mandatory)][string]$NextInstaller,
    [Parameter(Mandatory)][string]$NextSha256,
    [Parameter(Mandatory)][string]$ExpectedSignerSubject,
    [Parameter(Mandatory)][string]$EvidenceDirectory
)
$ErrorActionPreference='Stop'
if (-not $AuthorizeSyntheticInstallation) { throw 'Explicit authorization for synthetic installation required; nothing executed.' }
$os=Get-CimInstance Win32_OperatingSystem
if ($os.ProductType -ne 1 -or [int]$os.BuildNumber -lt 22000 -or [Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') { throw 'Real Windows 11 x64 client required.' }
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Authorized maintainer elevation required for installation tests.' }
. (Join-Path $PSScriptRoot '../../../scripts/Windows-Security.ps1')
$before=Get-AgroSacState
$defender=Get-MpComputerStatus
if (-not $before.active_confirmed -or -not $defender.AMServiceEnabled -or -not $defender.AntivirusEnabled -or -not $defender.RealTimeProtectionEnabled) { throw 'SAC/Defender active evidence required; never weaken protection.' }
if (@(Get-NetAdapter -Physical | Where-Object Status -EQ 'Up').Count) { throw 'Physically disconnect network before this offline test. Script will not alter adapters.' }
$install=Join-Path $env:ProgramFiles 'AgroLines Experimental'
if (Test-Path -LiteralPath $install) { throw 'Clean dedicated test machine required; existing installation is never removed by preflight.' }
$evidence=[IO.Path]::GetFullPath($EvidenceDirectory)
if ((Test-Path $evidence) -or $evidence.StartsWith($install,[StringComparison]::OrdinalIgnoreCase)) { throw 'Fresh evidence directory outside installation required.' }
function Assert-Signed([string]$File,[string]$Hash) {
    if ($Hash -cnotmatch '^[a-f0-9]{64}$' -or (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Hash) { throw 'Installer hash mismatch.' }
    $sig=Get-AuthenticodeSignature -LiteralPath $File
    if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -cne $ExpectedSignerSubject -or
        $sig.SignerCertificate.Issuer -ceq $sig.SignerCertificate.Subject -or -not $sig.TimeStamperCertificate) { throw 'Legitimate matching Authenticode/timestamp required; unsigned/test certificates are not accepted.' }
}
Assert-Signed $FirstInstaller $FirstSha256
Assert-Signed $NextInstaller $NextSha256
New-Item $evidence -ItemType Directory | Out-Null
$projects=Join-Path $env:LOCALAPPDATA ('AgroLines-Homologacao-Sintetica-' + [Guid]::NewGuid().ToString('N'))
New-Item $projects -ItemType Directory | Out-Null
$started=Get-Date
@{ os=($os | Select-Object Caption,Version,BuildNumber); sac=$before; defender=($defender | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled); projects=$projects; protections_modified=$false } |
    ConvertTo-Json -Depth 10 | Set-Content "$evidence/before.json" -Encoding utf8
function Install-Candidate([string]$File) {
    $process=Start-Process -FilePath $File -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="' + $install + '"')) -PassThru -Wait
    if ($process.ExitCode) { throw 'Installation failed; preserve machine/evidence for investigation.' }
    foreach ($file in (Get-ChildItem $install -Recurse -File | Where-Object Extension -In @('.exe','.dll','.pyd'))) {
        if ((Get-AuthenticodeSignature $file.FullName).Status -ne 'Valid') { throw 'Installed native signature failed; never bypass.' }
    }
}
function Probe([string]$Name) {
    $process=[Diagnostics.Process]::new()
    $process.StartInfo=[Diagnostics.ProcessStartInfo]::new((Join-Path $install 'AgroLines.exe'))
    $process.StartInfo.UseShellExecute=$false
    $process.StartInfo.WorkingDirectory=$evidence
    $process.StartInfo.Environment['PATH']=Join-Path $env:WINDIR 'System32'
    foreach ($key in @('PYTHONHOME','PYTHONPATH','GDAL_DATA','PROJ_DATA','PROJ_LIB','QT_PLUGIN_PATH','QTWEBENGINEPROCESS_PATH','QTWEBENGINE_RESOURCES_PATH','QTWEBENGINE_LOCALES_PATH')) { $process.StartInfo.Environment.Remove($key) | Out-Null }
    foreach ($argument in @('--smoke-report',"$evidence/$Name.json",'--offline-project-root',$projects)) { $process.StartInfo.ArgumentList.Add($argument) }
    try {
        $process.Start() | Out-Null
        if (-not $process.WaitForExit(120000)) { $process.Kill($true); throw 'Synthetic probe timed out; inspect event logs.' }
        if ($process.ExitCode) { throw 'Installed synthetic project probe failed.' }
    } finally { $process.Dispose() }
    $report=Get-Content "$evidence/$Name.json" -Raw | ConvertFrom-Json
    if (-not $report.offline_only -or -not $report.checks_passed -or -not $report.offline_projects.passed -or @($report.precision.checks).Count -ne 22) { throw 'Installed GIS/offline/precision check failed.' }
}
function Data-Hashes {
    $rows=@(Get-ChildItem $projects -File | Sort-Object Name | ForEach-Object { [ordered]@{name=$_.Name; sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} })
    return ConvertTo-Json -InputObject $rows -Compress
}
Install-Candidate $FirstInstaller
Probe 'first'
$dataBefore=Data-Hashes
$versionBefore=Get-Content (Join-Path $install 'AgroLines.current.txt') -Raw
Install-Candidate $NextInstaller
$versionAfter=Get-Content (Join-Path $install 'AgroLines.current.txt') -Raw
if ($versionBefore -ceq $versionAfter) { throw 'Update did not select a distinct version.' }
Probe 'updated'
if ((Data-Hashes) -cne $dataBefore) { throw 'Update changed synthetic project/history/backup bytes.' }
$uninstallers=@(Get-ChildItem (Join-Path $install 'uninstall') -Filter 'unins*.exe')
if ($uninstallers.Count -ne 1) { throw 'Expected exactly one trusted uninstaller.' }
$sig=Get-AuthenticodeSignature $uninstallers[0].FullName
if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -cne $ExpectedSignerSubject -or -not $sig.TimeStamperCertificate) { throw 'Uninstaller trust check failed.' }
$process=Start-Process -FilePath $uninstallers[0].FullName -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -PassThru -Wait
if ($process.ExitCode -or (Test-Path (Join-Path $install 'AgroLines.exe')) -or ((Data-Hashes) -cne $dataBefore)) { throw 'Uninstall/data preservation check failed.' }
Install-Candidate $NextInstaller
Probe 'reinstalled'
if ((Data-Hashes) -cne $dataBefore) { throw 'Reinstallation changed project/history/backup bytes.' }
$after=Get-AgroSacState; $defenderAfter=Get-MpComputerStatus
if (-not $after.active_confirmed -or -not $defenderAfter.RealTimeProtectionEnabled) { throw 'Protection evidence changed; acceptance denied.' }
$events=@(Get-AgroCodeIntegrityEvents -Since $started)
$events | ForEach-Object { $_.ToXml() } | Set-Content "$evidence/code-integrity.xml" -Encoding utf8
if (@($events | Where-Object { $_.ToXml().IndexOf('AgroLines',[StringComparison]::OrdinalIgnoreCase) -ge 0 }).Count) { throw 'Relevant Code Integrity event requires investigation before acceptance.' }
@{ installation_update_uninstall_reinstall_exercised=$true; project_history_backup_bytes_preserved=$true; computational_precision='22/22'; sac_active_before_after=$true; protections_modified=$false; native_network_trace_validated=$false; uac_visual_flow_validated=$false; ordinary_user_validated=$false; multiple_users_validated=$false; qgis_coexistence_validated=$false; commercial_approved=$false; signed_app_left_installed=$true } |
    ConvertTo-Json | Set-Content "$evidence/result.json" -Encoding utf8
