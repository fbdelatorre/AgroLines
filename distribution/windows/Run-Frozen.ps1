# Maintenance helper: prove the executable does not resolve Python/GIS from builder PATH.
function Invoke-AgroFrozenProbe {
    param(
        [string]$Executable, [string]$Report,
        [ValidateSet('--smoke-report', '--offline-network-report')]
        [string]$ReportArgument = '--smoke-report'
    )
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = [Diagnostics.ProcessStartInfo]::new([IO.Path]::GetFullPath($Executable))
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.WorkingDirectory = Split-Path -Parent ([IO.Path]::GetFullPath($Report))
    $process.StartInfo.ArgumentList.Add($ReportArgument)
    $process.StartInfo.ArgumentList.Add([IO.Path]::GetFullPath($Report))
    $process.StartInfo.Environment['PATH'] = Join-Path $env:WINDIR 'System32'
    foreach ($name in @('PYTHONHOME','PYTHONPATH','PROJ_LIB','PROJ_DATA','GDAL_DATA','QT_PLUGIN_PATH','QTWEBENGINEPROCESS_PATH','QTWEBENGINE_RESOURCES_PATH','QTWEBENGINE_LOCALES_PATH')) {
        $process.StartInfo.Environment.Remove($name) | Out-Null
    }
    try {
        $process.Start() | Out-Null
        if (-not $process.WaitForExit(120000)) {
            $process.Kill($true)
            $process.WaitForExit()
            throw 'Executavel instalado nao respondeu.'
        }
        if ($process.ExitCode -ne 0) { throw 'Executavel instalado falhou; consulte evidencia local.' }
    } finally { $process.Dispose() }
}
