# Observe only processes we start and their descendants. No injection or global ETW trace.
[CmdletBinding()]
param([string]$Executable, [string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent ([IO.Path]::GetFullPath($Executable))
$prefix = $root.TrimEnd('\') + '\'
$windowsPrefix = $env:WINDIR.TrimEnd('\') + '\'
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$directory = [IO.Path]::GetFullPath($OutputDirectory)
$allErrors = [Collections.Generic.List[object]]::new()
function Observe-Probe {
    param([string]$Name, [string]$Argument)
    $proc = [Diagnostics.Process]::new()
    $proc.StartInfo = [Diagnostics.ProcessStartInfo]::new([IO.Path]::GetFullPath($Executable))
    $proc.StartInfo.UseShellExecute = $false
    $proc.StartInfo.WorkingDirectory = $directory
    $proc.StartInfo.Environment['PATH'] = Join-Path $env:WINDIR 'System32'
    foreach ($key in @('PYTHONHOME','PYTHONPATH','PROJ_LIB','PROJ_DATA','GDAL_DATA','QT_PLUGIN_PATH','QTWEBENGINEPROCESS_PATH','QTWEBENGINE_RESOURCES_PATH','QTWEBENGINE_LOCALES_PATH')) {
        $proc.StartInfo.Environment.Remove($key) | Out-Null
    }
    if ($Argument) {
        $proc.StartInfo.ArgumentList.Add($Argument)
        $proc.StartInfo.ArgumentList.Add((Join-Path $directory "$Name-probe.json"))
    }
    $known = [Collections.Generic.HashSet[int]]::new()
    $seen = @{}; $errorKeys = [Collections.Generic.HashSet[string]]::new()
    $timer = [Diagnostics.Stopwatch]::StartNew(); $closeSent = $false
    try {
        $proc.Start() | Out-Null
        $known.Add($proc.Id) | Out-Null
        while (-not $proc.HasExited -and $timer.ElapsedMilliseconds -lt 120000) {
            $entries = @(Get-CimInstance Win32_Process -Filter "Name = 'AgroLinesPoC.exe' OR Name = 'QtWebEngineProcess.exe'")
            $changed = $true
            while ($changed) {
                $changed = $false
                foreach ($entry in $entries) {
                    if ($known.Contains([int]$entry.ParentProcessId) -and $known.Add([int]$entry.ProcessId)) { $changed = $true }
                }
            }
            foreach ($entry in $entries) {
                if (-not $known.Contains([int]$entry.ProcessId)) { continue }
                $target = $null
                try {
                    $target = [Diagnostics.Process]::GetProcessById([int]$entry.ProcessId)
                    foreach ($module in $target.Modules) {
                        if (-not $module.FileName) { continue }
                        # Qt helper image paths can use forward slashes. Normalize
                        # before attributing an image to the immutable payload.
                        $path = [IO.Path]::GetFullPath($module.FileName)
                        $key = "$($entry.ProcessId)|$path"
                        $relative = $null; $scope = 'external'
                        if ($path.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { $scope = 'payload'; $relative = $path.Substring($prefix.Length).Replace('\','/') }
                        elseif ($path.StartsWith($windowsPrefix,[StringComparison]::OrdinalIgnoreCase)) { $scope = 'windows-system' }
                        if (-not $seen.ContainsKey($key)) {
                            $seen[$key] = @{
                                path = $path; payload_relative = $relative; scope = $scope
                                process = $entry.Name; pid = [int]$entry.ProcessId
                                first_observed_ms = $timer.ElapsedMilliseconds; last_observed_ms = $timer.ElapsedMilliseconds
                            }
                        } else { $seen[$key].last_observed_ms = $timer.ElapsedMilliseconds }
                    }
                } catch {
                    if ($null -ne $target -and -not $target.HasExited -and $errorKeys.Add("$($entry.ProcessId)|$($_.Exception.GetType().Name)")) {
                        $allErrors.Add(@{phase = $Name; pid = [int]$entry.ProcessId; error = $_.Exception.GetType().Name; detail = $_.Exception.Message})
                    }
                } finally { if ($null -ne $target) { $target.Dispose() } }
            }
            if (-not $Argument -and $timer.ElapsedMilliseconds -gt 6000 -and -not $closeSent) {
                $closeSent = $proc.CloseMainWindow()
            }
            if (-not $Argument -and $timer.ElapsedMilliseconds -gt 15000) { break }
            Start-Sleep -Milliseconds 100
        }
        if (-not $proc.HasExited) { $allErrors.Add(@{phase = $Name; error = 'timeout-or-no-graceful-close'}); $proc.Kill($true); $proc.WaitForExit() }
        $exit = $proc.ExitCode
        if ($Argument -and $exit -ne 0) { throw "Synthetic probe failed: $Name" }
        return @{name = $Name; exit_code = $exit; modules = @($seen.Values); duration_ms = $timer.ElapsedMilliseconds; configured_poll_ms = 100; not_complete_image_load_trace = $true}
    } finally {
        if ($proc.Id -and -not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit() }
        $proc.Dispose()
    }
}
$phases = @(
    (Observe-Probe -Name 'normal-offline-startup' -Argument '')
    (Observe-Probe -Name 'smoke-startup-and-gis' -Argument '--smoke-report')
    (Observe-Probe -Name 'offline-import-edit-backup' -Argument '--offline-network-report')
)
@{
    phases = $phases; errors = @($allErrors.ToArray()); sac_approved = $false
    method = 'Read-only Process.Modules snapshots and descendant discovery; transient loads/access failures may be missed'
    installed_msix_validated = $false
} | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $directory 'loads.json') -Encoding utf8
if (@($phases | Where-Object { $_.exit_code -ne 0 }).Count -or $allErrors.Count) {
    throw 'Startup/probe/module observation failed; see loads.json. No acceptance claim.'
}
if (-not @($phases.modules | Where-Object { $_.process -eq 'QtWebEngineProcess.exe' }).Count) {
    throw 'Qt WebEngine helper was not observed; investigate before accepting the reduced payload.'
}
$external = @($phases.modules | Where-Object {
    $_.scope -eq 'external' -and
    -not $_.path.StartsWith((Join-Path $env:ProgramData 'Microsoft\Windows Defender\'), [StringComparison]::OrdinalIgnoreCase)
})
if ($external.Count) {
    throw 'Non-system module outside payload observed. Review exact paths in loads.json; no builder runtime fallback accepted.'
}
