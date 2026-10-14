[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Payload,
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$Policy,
    [Parameter(Mandatory)][string]$SourceCommit,
    [Parameter(Mandatory)][string]$CertificateThumbprint,
    [Parameter(Mandatory)][string]$ExpectedSignerSubject,
    [Parameter(Mandatory)][string]$ExpectedKeyProvider,
    [Parameter(Mandatory)][string]$TimestampUrl
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Signing-Helpers.ps1')
# This must precede any access to the certificate store/provider or signing operation.
$files = @(Get-AgroApprovedSigningSet -Payload $Payload -Plan $Plan -Policy $Policy -SourceCommit $SourceCommit)
Assert-AgroTimestampEndpoint $TimestampUrl
$tools = Get-AgroSigningTools
$before = Get-Content -LiteralPath $Plan -Raw | ConvertFrom-Json
foreach ($record in $before.files | Where-Object action -EQ 'preserve_original') {
    & $tools.signtool verify /pa /all /v /tw (Join-Path $Payload $record.path)
    if ($LASTEXITCODE -ne 0) { throw 'Upstream signature no longer accepted; no key access or overwrite.' }
}
$roots = @((Get-Content -LiteralPath $Policy -Raw | ConvertFrom-Json).approved_public_roots)
$cert = Get-AgroPublicSigningCertificate -ApprovedRoots $roots -Thumbprint $CertificateThumbprint -Subject $ExpectedSignerSubject -Provider $ExpectedKeyProvider
foreach ($file in $files) {
    if ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $file.sha256 -or
        (Get-AuthenticodeSignature -LiteralPath $file.path).Status -ne 'NotSigned') { throw 'Approved input changed or already signed; never overwrite vendor signature.' }
    & $tools.signtool sign /sha1 $CertificateThumbprint /s My /fd SHA256 /tr $TimestampUrl /td SHA256 $file.path
    if ($LASTEXITCODE -ne 0) { throw 'Authorized signing failed; candidate must remain quarantined.' }
    & $tools.signtool verify /pa /all /v /tw $file.path
    if ($LASTEXITCODE -ne 0) { throw 'Authenticode/timestamp verification failed.' }
    $after = Get-AuthenticodeSignature -LiteralPath $file.path
    if ($after.Status -ne 'Valid' -or $after.SignerCertificate.Thumbprint -cne $cert.Thumbprint -or -not $after.TimeStamperCertificate) { throw 'Signing identity/timestamp missing.' }
}
Write-Output "Authorized files signed and timestamped: $($files.Count). SAC remains pending."
