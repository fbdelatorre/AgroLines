# Never touch the official payload. Modify two LGPL Python files in a fresh lab copy.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Payload,[Parameter(Mandatory)][string]$Copy,[Parameter(Mandatory)][string]$Output)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$payload = [IO.Path]::GetFullPath($Payload)
$copy = [IO.Path]::GetFullPath($Copy)
$output = [IO.Path]::GetFullPath($Output)
if ((Test-Path -LiteralPath $copy) -or $copy.StartsWith($payload + '\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Fresh independent copy required.' }
New-Item $output -ItemType Directory -Force | Out-Null
. (Join-Path $PSScriptRoot '../Run-Frozen.ps1')
function Invoke-BindingReport([string]$Root,[string]$Report) {
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = [Diagnostics.ProcessStartInfo]::new((Join-Path $Root 'AgroLines.exe'))
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.WorkingDirectory = $output
    $process.StartInfo.Environment['PATH'] = Join-Path $env:WINDIR 'System32'
    foreach ($key in @('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','PROJ_LIB','PROJ_DATA','GDAL_DATA')) { $process.StartInfo.Environment.Remove($key) | Out-Null }
    $process.StartInfo.ArgumentList.Add('--binding-report')
    $process.StartInfo.ArgumentList.Add($Report)
    try {
        $process.Start() | Out-Null
        if (-not $process.WaitForExit(60000)) { $process.Kill($true); throw 'Binding probe timed out.' }
        if ($process.ExitCode) { throw 'Binding probe failed.' }
    } finally { $process.Dispose() }
    return (Get-Content $Report -Raw | ConvertFrom-Json)
}
$original = Invoke-BindingReport $payload (Join-Path $output 'bindings-original.json')
Write-Output ('AGROLINES_BINDINGS_ORIGINAL=' + ($original | ConvertTo-Json -Depth 8 -Compress))
$originalManifest = (Get-FileHash (Join-Path $payload 'payload-manifest.json')).Hash
Copy-Item -LiteralPath $payload -Destination $copy -Recurse
$marker = 'synthetic-standalone-lgpl-python-replacement-v1'
foreach ($package in @('PySide6','shiboken6')) {
    $file = Join-Path $copy "_internal/$package/__init__.py"
    # PySide6 replaces its module dictionary at the end of __init__.py. A bare
    # assignment appended afterwards updates the old globals, not the live module.
    # Set the harmless marker on the actual imported module in both packages.
    [IO.File]::AppendAllText($file, "`n# Isolated laboratory modification; no algorithms changed.`nsetattr(sys.modules[__name__], 'AGROLINES_LGPL_LAB_MARKER', '$marker')`n", [Text.UTF8Encoding]::new($false))
}
$modified = Invoke-BindingReport $copy (Join-Path $output 'bindings-modified.json')
Write-Output ('AGROLINES_BINDINGS_MODIFIED=' + ($modified | ConvertTo-Json -Depth 8 -Compress))
foreach ($package in @('PySide6','shiboken6')) {
    $before = @($original.modules | Where-Object module -EQ $package)
    $after = @($modified.modules | Where-Object module -EQ $package)
    if ($before.Count -ne 1 -or $after.Count -ne 1 -or $before[0].marker -or $after[0].marker -cne $marker -or
        -not $after[0].inside_runtime -or -not $after[0].path.StartsWith($copy + '\',[StringComparison]::OrdinalIgnoreCase) -or
        $after[0].sha256 -eq $before[0].sha256) { throw 'External modified package not actually loaded.' }
}
Invoke-AgroFrozenProbe -Executable (Join-Path $copy 'AgroLines.exe') -Report (Join-Path $output 'modified-smoke.json')
Invoke-AgroFrozenProbe -Executable (Join-Path $copy 'AgroLines.exe') -Report (Join-Path $output 'modified-offline.json') -ReportArgument '--offline-network-report'
$smoke = Get-Content (Join-Path $output 'modified-smoke.json') -Raw | ConvertFrom-Json
$offline = Get-Content (Join-Path $output 'modified-offline.json') -Raw | ConvertFrom-Json
if (-not $smoke.checks_passed -or -not $offline.passed -or $smoke.payload_integrity_verified) { throw 'Modified-copy functional/integrity negative control failed.' }
if ((Get-FileHash (Join-Path $payload 'payload-manifest.json')).Hash -cne $originalManifest) { throw 'Original manifest changed.' }
$binaryUnchanged = ((Get-FileHash (Join-Path $payload 'AgroLines.exe')).Hash -ceq (Get-FileHash (Join-Path $copy 'AgroLines.exe')).Hash)
if (-not $binaryUnchanged) { throw 'Laboratory must not modify the own executable.' }
@{ modified_python_bindings_loaded=$true; frozen_agrolines_exercised=$true; computational_precision_checks=@($smoke.precision.checks).Count; offline_passed=$offline.passed; original_binary_unchanged=$binaryUnchanged; native_qt_geos_modified_in_this_experiment=$false; full_lgpl_compliance_approved=$false; sac_approved=$false } |
    ConvertTo-Json -Depth 5 | Set-Content (Join-Path $output 'replacement-result.json') -Encoding utf8
