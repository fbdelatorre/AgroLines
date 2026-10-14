# Synthetic CI checks: validates evidence processing, not SAC compatibility.
param([Parameter(Mandatory = $true)][string]$Python)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Windows-Security.ps1')
function SyntheticEvent([string]$Path) {
    $event = [PSCustomObject]@{ Id = 3077; RecordId = 42; TimeCreated = [DateTime]::Now; File = $Path }
    $event | Add-Member -MemberType ScriptMethod -Name ToXml -Value {
        return '<Event><EventData><Data Name="FileName">' + [Security.SecurityElement]::Escape($this.File) + '</Data></EventData></Event>'
    }
    return $event
}
$events = @((SyntheticEvent '\Device\HarddiskVolume3\venv\numpy\BLOCKED.pyd'), (SyntheticEvent 'C:\unrelated\elsewhere.dll'))
$converted = @(Convert-AgroCodeIntegrityEvents -Events $events -NativeNames @('blocked.pyd'))
if ($converted.Count -ne 2 -or -not $converted[0].associated_with_inventory -or $converted[1].associated_with_inventory) {
    throw 'Event correlation failed.'
}
if ($converted[0].record_id -ne 42 -or $converted[0].xml -notmatch 'FileName') { throw 'Lost original event evidence.' }
$temporary = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $temporary | Out-Null
try {
    $inventory = Join-Path $temporary 'inventory.json'
    $output = Join-Path $temporary 'signatures.json'
    @{ schema_version = 1; inspection_complete = $true; files = @(@{
        path = (Resolve-Path -LiteralPath $Python).Path; sha256 = ('0' * 64); format = 'PE'; packages = @()
    }) } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $inventory -Encoding utf8
    & pwsh -NoProfile -File (Join-Path $PSScriptRoot 'Audit-NativeWindows.ps1') -Inventory $inventory -Output $output -Strict
    if ($LASTEXITCODE -ne 1) { throw 'Tampered inventory must fail strict verification.' }
    $result = Get-Content -LiteralPath $output -Raw | ConvertFrom-Json
    if ($result.files[0].status -ne 'InspectionError' -or $result.signatures_and_chains_verified -or $result.smart_app_control_compatibility_proven) {
        throw 'Tampered bytes were incorrectly approved.'
    }
    $global:LASTEXITCODE = 0 # Expected failure was asserted above.
    Write-Output 'Synthetic event correlation and tamper rejection passed; SAC not tested.'
} finally { Remove-Item -LiteralPath $temporary -Recurse -Force }
