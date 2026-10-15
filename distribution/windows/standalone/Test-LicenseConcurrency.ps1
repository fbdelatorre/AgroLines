# Two synthetic frozen processes, application-owned lab registry keys only.
param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$Fixture,[Parameter(Mandatory)][string]$Output)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$executable=[IO.Path]::GetFullPath($Executable)
$fixture=[IO.Path]::GetFullPath($Fixture)
$directory=Join-Path $env:RUNNER_TEMP ([guid]::NewGuid().ToString())
New-Item $Output -ItemType Directory -Force | Out-Null
function Start-Lab([string]$Mode) {
    $process=[Diagnostics.Process]::new()
    $process.StartInfo=[Diagnostics.ProcessStartInfo]::new($executable)
    $process.StartInfo.UseShellExecute=$false
    $process.StartInfo.Environment['PATH']="$env:WINDIR/System32;$env:WINDIR"
    foreach ($arg in @('--license-concurrency',$Mode,$fixture,$directory)) { $process.StartInfo.ArgumentList.Add($arg) }
    $process.Start() | Out-Null
    return $process
}
function Finish-Lab($Process) {
    try {
        if (-not $Process.WaitForExit(30000)) { $Process.Kill($true); throw 'Concurrent-license laboratory timeout.' }
        if ($Process.ExitCode) {
            Get-ChildItem $env:RUNNER_TEMP -Filter 'license-concurrency-*-error.json' | ForEach-Object { Get-Content $_.FullName -Raw }
            throw 'Concurrent-license laboratory process failed.'
        }
    } finally { $Process.Dispose() }
}
$observer=$null
try {
    Finish-Lab (Start-Lab 'init')
    $observer=Start-Lab 'observer'
    $deadline=[datetime]::UtcNow.AddSeconds(15)
    while (-not (Test-Path (Join-Path $directory 'observer.ready'))) {
        if ($observer.HasExited -or [datetime]::UtcNow -gt $deadline) { throw 'Observer did not become ready.' }
        Start-Sleep -Milliseconds 50
    }
    Finish-Lab (Start-Lab 'writer')
    try { Finish-Lab $observer } finally { $observer=$null }
    Copy-Item (Join-Path $directory 'observer.json') (Join-Path $Output 'two-process-state.json')
} finally {
    if ($observer) { if (-not $observer.HasExited) { $observer.Kill($true) }; $observer.Dispose() }
    Finish-Lab (Start-Lab 'cleanup')
    # DPAPI blobs, not published, stay in the disposable runner temp until job disposal.
}
