# Negative control: unauthorized invocation must fail before any certificate/key access.
$ErrorActionPreference='Stop'
$before=$env:GITHUB_EVENT_NAME
try {
    $env:GITHUB_EVENT_NAME='pull_request'
    foreach ($script in @('Sign-OwnedComponent.ps1','Build-SignedHomologation.ps1')) {
        $denied=$false
        try {
            if ($script -eq 'Sign-OwnedComponent.ps1') { & (Join-Path $PSScriptRoot $script) -File nonexistent.exe -Configuration nonexistent.json -Role launcher }
            else { & (Join-Path $PSScriptRoot $script) -Configuration nonexistent.json }
        } catch {
            if ($_.Exception.Message -notlike 'Only an authorized dispatch*') { throw }
            $denied=$true
        }
        if (-not $denied) { throw 'Unapproved signing entry point did not refuse.' }
    }
} finally { $env:GITHUB_EVENT_NAME=$before }
$denied=$false
try {
    & (Join-Path $PSScriptRoot 'Test-SignedLifecycle.ps1') -FirstInstaller nonexistent.exe -FirstSha256 nonexistent -NextInstaller nonexistent.exe -NextSha256 nonexistent -ExpectedSignerSubject nonexistent -ApprovedPublicRootSha256 nonexistent -EvidenceDirectory nonexistent
} catch {
    if ($_.Exception.Message -notlike 'Explicit authorization for synthetic installation required*') { throw }
    $denied=$true
}
if (-not $denied) { throw 'Unapproved installation test did not refuse before system/file access.' }
Write-Output 'Unapproved own component/Inno signing refused before configuration, files or certificate access.'
