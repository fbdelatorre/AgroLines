# Regression: blocked policy must stop before any signing/certificate-provider call.
$ErrorActionPreference = 'Stop'
$temporary = Join-Path ([IO.Path]::GetTempPath()) ('agrolines-signing-guard-' + [guid]::NewGuid())
New-Item $temporary -ItemType Directory | Out-Null
try {
    @{schema_version=1; files=@()} | ConvertTo-Json | Set-Content (Join-Path $temporary 'policy.json')
    @{schema_version=1; ready_for_authorized_signing=$false; violations=@()} | ConvertTo-Json | Set-Content (Join-Path $temporary 'plan.json')
    $caught = $false
    try {
        & (Join-Path $PSScriptRoot 'Sign-ApprovedNative.ps1') -Payload $temporary -Plan (Join-Path $temporary 'plan.json') -Policy (Join-Path $temporary 'policy.json') -SourceCommit ('0' * 40) -CertificateThumbprint ('0' * 40) -ExpectedSignerSubject 'NOT-A-CERTIFICATE' -ExpectedKeyProvider 'NOT-A-PROVIDER' -TimestampUrl 'https://invalid.example'
    } catch {
        if ($_.Exception.Message -notlike 'ASSINATURA PENDENTE:*') { throw }
        $caught = $true
    }
    if (-not $caught) { throw 'Blocked signing unexpectedly proceeded.' }
    Write-Output 'Blocked policy stopped before tool/certificate/key access. No test certificate created.'
} finally { Remove-Item -LiteralPath $temporary -Recurse -Force }
