# Read-only system/package inspection; writes NEW local evidence only. SPDX-License-Identifier: 0BSD
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$OutputDirectory,
    [Parameter(Mandatory)][DateTime]$Since,
    [string]$FunctionalEvidence,
    [string]$StartupLog
)
$ErrorActionPreference = 'Stop'
if ($Since -gt (Get-Date) -or $Since -lt (Get-Date).AddHours(-24)) { throw 'Use a test window within the last 24 hours.' }
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $output) { throw 'Choose a NEW private evidence directory outside the repository/package.' }
$pkg = Get-AppxPackage -Name 'DelatorreCOrporation.AgroLines'
if ($output.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -or
    ($pkg -and $output.StartsWith($pkg.InstallLocation, [StringComparison]::OrdinalIgnoreCase))) { throw 'Evidence must be outside checkout and package.' }
New-Item $output -ItemType Directory | Out-Null
. (Join-Path $root 'scripts/Windows-Security.ps1')
$result = [ordered]@{
    collected_utc = (Get-Date).ToUniversalTime().ToString('o'); since_utc = $Since.ToUniversalTime().ToString('o')
    os = $null; sac = (Get-AgroSacState); defender = $null; package = $null
    observations = @(); event_logs = @(); sac_approved = $false; submission_authorized = $false
}
try { $result.os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture } catch { $result.observations += 'OS query unavailable' }
try { $result.defender = Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled } catch { $result.observations += 'Defender query unavailable' }
$nativeNames = @()
if ($pkg) {
    $result.package = $pkg | Select-Object Name,Publisher,Architecture,Version,PackageFullName,PackageFamilyName,SignatureKind,Status,InstallLocation,IsDevelopmentMode
    if ($pkg.PackageFamilyName -cne 'DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg' -or
        $pkg.Publisher -cne 'CN=43189595-B928-4D57-90A4-24300E4D4976' -or
        $pkg.SignatureKind.ToString() -cne 'Store' -or $pkg.IsDevelopmentMode) { $result.observations += 'Not a confirmed official Store installation; stop functional homologation.' }
    $nativeNames = @(Get-ChildItem -LiteralPath $pkg.InstallLocation -Recurse -File | Where-Object Extension -In @('.dll','.pyd','.exe') | Select-Object -ExpandProperty Name -Unique)
    try {
        & (Join-Path $root 'distribution/windows/signing/Test-StoreDeliveredTrust.ps1') -OutputDirectory (Join-Path $output 'native-trust')
    } catch { $result.observations += ('Native/catalog inspection incomplete: ' + $_.Exception.Message) }
} else { $result.observations += 'Official package not installed; no installation attempted.' }
$pattern = 'AgroLines|DelatorreCOrporation\.AgroLines'
if ($nativeNames.Count) { $pattern += '|' + (($nativeNames | ForEach-Object { [Regex]::Escape($_) }) -join '|') }
foreach ($log in @('Microsoft-Windows-CodeIntegrity/Operational','Microsoft-Windows-AppModel-Runtime/Admin','Application')) {
    $entry = [ordered]@{ log=$log; enabled=$null; query_complete=$false; matched=0; error=$null }
    try {
        $info = Get-WinEvent -ListLog $log -ErrorAction Stop
        $entry.enabled = $info.IsEnabled
        if (-not $info.IsEnabled) { throw 'Log disabled; NOT enabled by collector.' }
        $filter = @{ LogName=$log; StartTime=$Since }
        if ($log -like '*CodeIntegrity*') { $filter.Id = @(3077,3033) }
        $events = @()
        try { $events = @(Get-WinEvent -FilterHashtable $filter -ErrorAction Stop) }
        catch { if ($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') { throw } }
        $related = @($events | Where-Object { $_.ToXml() -match $pattern } | ForEach-Object {
            @{ id=$_.Id; record_id=$_.RecordId; created_utc=$_.TimeCreated.ToUniversalTime().ToString('o'); xml=$_.ToXml() }
        })
        $entry.query_complete = $true; $entry.matched = $related.Count
        $safe = $log.Replace('/','-')
        ConvertTo-Json -InputObject $related -Depth 8 | Set-Content (Join-Path $output ($safe + '.json')) -Encoding utf8
    } catch { $entry.error = $_.Exception.Message }
    $result.event_logs += $entry
}
foreach ($item in @(@{path=$FunctionalEvidence; name='functional-evidence.json'},@{path=$StartupLog; name='startup-log.txt'})) {
    if ($item.path) {
        $file = Get-Item -LiteralPath $item.path
        if ($file.PSIsContainer -or $file.Length -gt 10MB) { throw 'Evidence must be a file <=10MB without projects/secrets.' }
        Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $output $item.name)
        $result.observations += ('Operator-supplied evidence copied, NOT automatically validated: ' + $item.name)
    }
}
$result.observations += 'Local private evidence may contain Windows paths/event data. Review/redact before sharing. No upload, network trace, launch or protection change performed. Absence of matching events is not proof of acceptance. Store receipt/source must be documented separately.'
$result | ConvertTo-Json -Depth 15 | Set-Content (Join-Path $output 'homologation.json') -Encoding utf8
Get-ChildItem -LiteralPath $output -Recurse -File | ForEach-Object {
    @{ path=$_.FullName.Substring($output.Length); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $output 'hashes.json') -Encoding utf8
Write-Output 'Read-only collection finished. Real SAC, offline, update/uninstall and legal approval remain separate.'
