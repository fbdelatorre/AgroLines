# Read-only preparation. No certificate/key access, signature or release authorization.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Payload,[Parameter(Mandatory)][string]$SourceCommit,[string]$PythonExecutable='python',[string]$Output='evidence/standalone/signing')
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
Push-Location $root
try {
    New-Item $Output -ItemType Directory -Force | Out-Null
    & $PythonExecutable -m distribution.payload --root $Payload --output "$Output/native.json"
    if ($LASTEXITCODE) { throw 'Native inventory failed.' }
    & ./scripts/Audit-NativeWindows.ps1 -Inventory "$Output/native.json" -Output "$Output/authenticode.json"
    & ./scripts/Test-NativeAuthenticode.ps1 -Inventory "$Output/native.json" -Output "$Output/signtool.json"
    & $PythonExecutable -m scripts.signing_pipeline evaluate --root $Payload --policy "$Payload/native-signing-policy.json" --native "$Output/native.json" --signatures "$Output/authenticode.json" --tools "$Output/signtool.json" --source-commit $SourceCommit --output "$Output/plan.json"
    if ($LASTEXITCODE) { throw 'Signing policy/provenance validation failed; no key accessed.' }
} finally { Pop-Location }
