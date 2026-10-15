# Isolated synthetic experiment; preserve commercial reference EXE/payload and protections.
param([Parameter(Mandatory)][string]$Payload,[Parameter(Mandatory)][string]$Fixture,[Parameter(Mandatory)][string]$Copy,[Parameter(Mandatory)][string]$Output)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$payload=[IO.Path]::GetFullPath($Payload)
$copy=[IO.Path]::GetFullPath($Copy)
$output=[IO.Path]::GetFullPath($Output)
$fixture=[IO.Path]::GetFullPath($Fixture)
if ((Test-Path $copy) -or $copy.StartsWith($payload,[StringComparison]::OrdinalIgnoreCase)) { throw 'Independent fresh copy required.' }
New-Item $output -ItemType Directory -Force | Out-Null
Copy-Item $payload $copy -Recurse
$original=(Get-FileHash (Join-Path $payload 'AgroLines.exe') -Algorithm SHA256).Hash
$marker='synthetic-commercial-lgpl-substitution-v1'
foreach ($package in @('PySide6','shiboken6')) {
    $path=Join-Path $copy "_internal/$package/__init__.py"
    [IO.File]::AppendAllText($path,"`n# Isolated LGPL library experiment; no application changes.`nsetattr(sys.modules[__name__], 'AGROLINES_LGPL_LAB_MARKER', '$marker')`n",[Text.UTF8Encoding]::new($false))
}
function Invoke-Lab([string[]]$Arguments) {
    $process=[Diagnostics.Process]::new()
    $process.StartInfo=[Diagnostics.ProcessStartInfo]::new((Join-Path $copy 'AgroLines.exe'))
    $process.StartInfo.UseShellExecute=$false
    $process.StartInfo.WorkingDirectory=$copy
    $process.StartInfo.Environment['PATH']="$env:WINDIR/System32;$env:WINDIR"
    foreach ($argument in $Arguments) { $process.StartInfo.ArgumentList.Add($argument) }
    try {
        $process.Start() | Out-Null
        if (-not $process.WaitForExit(180000)) { $process.Kill($true); throw 'Commercial replacement probe timeout.' }
        if ($process.ExitCode) { throw 'Commercial replacement probe failed.' }
    } finally { $process.Dispose() }
}
Invoke-Lab @('--binding-report',(Join-Path $output 'bindings.json'))
$bindings=Get-Content (Join-Path $output 'bindings.json') -Raw | ConvertFrom-Json
foreach ($package in @('PySide6','shiboken6')) {
    $row=@($bindings.modules | Where-Object module -EQ $package)
    if ($row.Count -ne 1 -or $row[0].marker -cne $marker -or -not $row[0].path.StartsWith($copy,[StringComparison]::OrdinalIgnoreCase)) { throw 'Modified commercial binding not actually loaded.' }
}
Invoke-Lab @('--licensing-probe',$fixture,(Join-Path $output 'licensed-gis.json'))
$result=Get-Content (Join-Path $output 'licensed-gis.json') -Raw | ConvertFrom-Json
if (-not $result.passed -or -not $result.offline_valid -or -not $result.dpapi_roundtrip) { throw 'Licensing failed after LGPL library substitution.' }
if ((Get-FileHash (Join-Path $copy 'AgroLines.exe') -Algorithm SHA256).Hash -cne $original -or
    (Get-FileHash (Join-Path $payload 'AgroLines.exe') -Algorithm SHA256).Hash -cne $original) { throw 'Own executable changed during experiment.' }
@{ modified_bindings_loaded=$true; licensed_frozen_gis_passed=$true; own_executable_unchanged=$true; native_qt_rebuilt_in_this_experiment=$false; legal_approved=$false; sac_approved=$false } |
    ConvertTo-Json | Set-Content (Join-Path $output 'result.json') -Encoding utf8

Write-Output ('AGROLINES_COMMERCIAL_BINDING_REPLACEMENT=' + (Get-Content (Join-Path $output 'result.json') -Raw))
