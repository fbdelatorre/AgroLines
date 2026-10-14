# Read-only policy verification. Never signs or changes certificate stores/time/security.
[CmdletBinding()]
param([string]$Inventory, [string]$Output)
$ErrorActionPreference = 'Stop'
$data = Get-Content -LiteralPath $Inventory -Raw | ConvertFrom-Json
$sdkRoot = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits/10/bin'
$sdk = Get-ChildItem $sdkRoot -Directory | Where-Object {
    $_.Name -match '^10\.0\.\d+\.\d+$' -and (Test-Path (Join-Path $_.FullName 'x64/signtool.exe'))
} | Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
if (-not $sdk) { throw 'Windows SDK SignTool unavailable.' }
$tool = Join-Path $sdk.FullName 'x64/signtool.exe'
if ((Get-AuthenticodeSignature $tool).Status -ne 'Valid') { throw 'Untrusted SDK verifier.' }
$rows = @()
foreach ($file in $data.files) {
    $before = (Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($before -ne $file.sha256) { throw 'Input changed before verification.' }
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = [Diagnostics.ProcessStartInfo]::new($tool)
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.CreateNoWindow = $true
    foreach ($arg in @('verify','/pa','/all','/v','/tw',$file.path)) { $process.StartInfo.ArgumentList.Add($arg) }
    try {
        $process.Start() | Out-Null
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        $code = $null; $timeout = $false
        if (-not $process.WaitForExit(30000)) { $timeout = $true; $process.Kill($true); $process.WaitForExit() }
        else { $code = $process.ExitCode }
        $after = (Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant()
        $rows += @{
            path = $file.path; sha256 = $before; exit_code = $code; timeout = $timeout
            stdout = $stdout.Result; stderr = $stderr.Result
            integrity_matches = ($after -eq $before); sac_approved = $false
        }
    } finally { $process.Dispose() }
}
@{sdk = $sdk.Name; arguments = 'verify /pa /all /v /tw'; files = $rows; sac_approved = $false} |
    ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $Output -Encoding utf8
