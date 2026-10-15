# Isolated process-level tests only, never runs an installer or changes installed data.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Payload,[Parameter(Mandatory)][string]$Output)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$root=Join-Path $env:RUNNER_TEMP ('agrolines-launcher-' + [Guid]::NewGuid().ToString('N'))
$first='1.0.0.1-aaaaaaaaaaaa'; $second='1.0.0.2-bbbbbbbbbbbb'
New-Item "$root/versions" -ItemType Directory -Force | Out-Null
New-Item $Output -ItemType Directory -Force | Out-Null
$output=[IO.Path]::GetFullPath($Output)
Copy-Item build/distribution/AgroLinesLauncher.exe "$root/AgroLines.exe"
Copy-Item -LiteralPath $Payload -Destination "$root/versions/$first" -Recurse
. (Join-Path $PSScriptRoot '../Run-Frozen.ps1')
function Set-Pointer([string]$Value) { [IO.File]::WriteAllText("$root/AgroLines.current.txt", $Value, [Text.Encoding]::ASCII) }
Set-Pointer $first
Invoke-AgroFrozenProbe -Executable "$root/AgroLines.exe" -Report "$output/first.json"
# Same stable executable/shortcut path, new version directory and selection.
Move-Item "$root/versions/$first" "$root/versions/$second"
Set-Pointer $second
Invoke-AgroFrozenProbe -Executable "$root/AgroLines.exe" -Report "$output/second.json" -ReportArgument '--offline-network-report'
$firstReport=Get-Content "$output/first.json" -Raw | ConvertFrom-Json
$secondReport=Get-Content "$output/second.json" -Raw | ConvertFrom-Json
if (-not $firstReport.checks_passed -or -not $secondReport.passed) { throw 'Launcher functional test failed.' }
# Invalid configuration must exit safely, without launching outside versions.
foreach ($bad in @('../outside','C:\outside','1.0.0.2-zzzzzzzzzzzz','1.0.0.2-bbbbbbbbbbbb/../outside')) {
    Set-Pointer $bad
    $process=Start-Process -FilePath "$root/AgroLines.exe" -PassThru -Wait
    if ($process.ExitCode -ne 5) { throw 'Unsafe launcher pointer accepted.' }
}
@{ full_frozen_app_started=$true; pointer_update_exercised=$true; stable_launcher_unchanged=((Get-FileHash "$root/AgroLines.exe").Hash -ceq (Get-FileHash build/distribution/AgroLinesLauncher.exe).Hash); path_escape_rejected=$true; installer_executed=$false; multiple_real_users_validated=$false; sac_approved=$false } |
    ConvertTo-Json | Set-Content "$output/result.json" -Encoding utf8
Write-Output ('AGROLINES_LAUNCHER=' + (Get-Content "$output/result.json" -Raw))
