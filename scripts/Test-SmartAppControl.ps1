# Maintainer acceptance tests on an isolated Windows 11 machine; no security changes.
# Installation/first-run/update acceptance requires a real signed release and manual evidence.
param(
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$Inventory,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT' -or $PSVersionTable.PSVersion.Major -lt 7) {
    throw 'Use PowerShell 7 no Windows 11 de homologacao; nao altere politicas.'
}
. (Join-Path $PSScriptRoot 'Windows-Security.ps1')
$root = Split-Path -Parent $PSScriptRoot
$pythonPath = (Resolve-Path -LiteralPath $Python).Path
$target = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $target -Force | Out-Null
$data = Get-Content -LiteralPath $Inventory -Raw | ConvertFrom-Json
if ($data.schema_version -ne 1 -or -not $data.inspection_complete) { throw 'Inventario incompleto.' }
$names = @($data.files | ForEach-Object { [IO.Path]::GetFileName($_.path) }) + @('python.exe','pythonw.exe','QtWebEngineProcess.exe','AgroLines.exe')
$startState = Get-AgroSacState
$build = [Environment]::OSVersion.Version.Build
$os = Get-CimInstance -ClassName Win32_OperatingSystem
if ($os.ProductType -ne 1) { throw 'Homologacao exige Windows cliente, nao Windows Server.' }
if (@($data.files | Where-Object { $_.path -eq $pythonPath }).Count -ne 1) {
    throw 'Runtime Python precisa estar coberto pelo inventario.'
}
$started = [DateTime]::Now
$startState | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath (Join-Path $target 'preflight-state.json') -Encoding utf8
if ($build -lt 22000 -or -not $startState.active_confirmed) {
    throw 'Windows 11/SAC ativo nao comprovado. Nao altere a politica para executar este teste.'
}
if ($env:QTWEBENGINE_DISABLE_SANDBOX -eq '1' -or $env:QTWEBENGINE_CHROMIUM_FLAGS -match '--no-sandbox') {
    throw 'Teste rejeitado: sandbox Chromium desativado no ambiente.'
}
Get-AgroCodeIntegrityEvents -Since $started | Out-Null
foreach ($file in $data.files) {
    if ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256) {
        throw 'Inventario desatualizado; audite novamente antes de executar os componentes.'
    }
}
$results = @()
$plans = @(
    @{ name = 'numpy'; args = @('-m','scripts.windows_probe','numpy') },
    @{ name = 'shapely-geos'; args = @('-m','scripts.windows_probe','shapely') },
    @{ name = 'fiona-gdal'; args = @('-m','scripts.windows_probe','fiona') },
    @{ name = 'pyproj'; args = @('-m','scripts.windows_probe','pyproj') },
    @{ name = 'pyside6'; args = @('-m','scripts.windows_probe','pyside6') },
    @{ name = 'server-import'; args = @('-m','scripts.windows_probe','server-import') },
    @{ name = 'server-postgis'; args = @('-m','scripts.windows_probe','server-postgis') },
    @{ name = 'shapefile'; args = @('-m','scripts.windows_probe','shapefile') },
    @{ name = 'precision'; args = @('-m','scripts.precision_report','--output',(Join-Path $target 'precision.json')) },
    @{ name = 'webengine-map-vertices'; args = @('-m','scripts.render_desktop','--output',(Join-Path $target 'native-desktop')) }
)
foreach ($plan in $plans) {
    $begin = [DateTime]::Now
    $step = [ordered]@{ name = $plan.name; exit_code = $null; timed_out = $false; errors = @(); events = @(); sac_state = $null; passed = $false }
    $process = [Diagnostics.Process]::new()
    try {
        # Never pass credentials on the command line or dump child output/environment.
        $process.StartInfo = [Diagnostics.ProcessStartInfo]::new($pythonPath)
        $process.StartInfo.WorkingDirectory = $root
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.RedirectStandardOutput = $true
        $process.StartInfo.RedirectStandardError = $true
        foreach ($arg in $plan.args) { $process.StartInfo.ArgumentList.Add($arg) }
        $process.Start() | Out-Null
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(180000)) {
            $step.timed_out = $true
            $process.Kill($true)
            $process.WaitForExit()
        }
        $step.exit_code = $process.ExitCode
        # Full stderr can contain connection URLs/tokens; only status enters evidence.
        $stdout.GetAwaiter().GetResult() | Out-Null
        $stderr.GetAwaiter().GetResult() | Out-Null
    } catch { $step.errors += 'Probe execution failed; inspect locally without publishing secrets.' }
    finally { $process.Dispose() }
    try {
        Start-Sleep -Seconds 2 # Allow asynchronous Code Integrity logging, never clear the log.
        $events = @(Get-AgroCodeIntegrityEvents -Since $begin.AddSeconds(-1))
        $step.events = @(Convert-AgroCodeIntegrityEvents -Events $events -NativeNames $names)
    } catch { $step.errors += 'Code Integrity evidence unreadable; cannot approve.' }
    $step.sac_state = Get-AgroSacState
    $related = @($step.events | Where-Object associated_with_inventory)
    $step.passed = ($step.exit_code -eq 0 -and -not $step.timed_out -and $step.errors.Count -eq 0 -and $related.Count -eq 0 -and $step.sac_state.active_confirmed)
    $results += [PSCustomObject]$step
    $results | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $target 'steps.json') -Encoding utf8
    Write-Output "$($plan.name): passed=$($step.passed); exit=$($step.exit_code); relatedBlocks=$($related.Count)"
}
$endState = Get-AgroSacState
$finalEvents = @()
$errors = @()
try {
    $events = @(Get-AgroCodeIntegrityEvents -Since $started.AddSeconds(-1))
    $finalEvents = @(Convert-AgroCodeIntegrityEvents -Events $events -NativeNames $names)
} catch { $errors += 'Final Code Integrity evidence unreadable.' }
$unchanged = $true
foreach ($file in $data.files) {
    try {
        if ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256) { $unchanged = $false }
    } catch { $unchanged = $false }
}
$report = [ordered]@{
    schema_version = 1; started_utc = $started.ToUniversalTime().ToString('o'); windows_build = $build
    windows_caption = $os.Caption; windows_version = $os.Version
    start_state = $startState; end_state = $endState; steps = $results; events = $finalEvents
    errors = $errors; inventory_unchanged = $unchanged
    functional_sac_checks_passed = ($build -ge 22000 -and $startState.active_confirmed -and $endState.active_confirmed -and $unchanged -and $errors.Count -eq 0 -and @($results | Where-Object { -not $_.passed }).Count -eq 0 -and @($finalEvents | Where-Object associated_with_inventory).Count -eq 0)
    release_acceptance_proven = $false
    pending = @('Clean signed installer', 'First launch of installed application', 'Signed update and data preservation', 'Manual Windows Security evidence and native visual review')
}
$report | ConvertTo-Json -Depth 24 | Set-Content -LiteralPath (Join-Path $target 'acceptance.json') -Encoding utf8
if (-not $report.functional_sac_checks_passed) { exit 1 }
