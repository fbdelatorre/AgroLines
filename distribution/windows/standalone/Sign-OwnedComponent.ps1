# FUTURE protected, explicitly authorized execution only. Never called by PR workflows.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$File,[Parameter(Mandatory)][string]$Configuration,
      [ValidateSet('launcher','installer','uninstaller')][Parameter(Mandatory)][string]$Role)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
& (Join-Path $PSScriptRoot '../signing/Assert-SigningEnvironment.ps1')
. (Join-Path $PSScriptRoot '../signing/Signing-Helpers.ps1')
$cfg=Get-Content $Configuration -Raw | ConvertFrom-Json
if ($cfg.schema_version -ne 1 -or $cfg.authorized -isnot [bool] -or -not $cfg.authorized -or
    -not $cfg.approval_reference -or $cfg.source_commit -cne $env:GITHUB_SHA) { throw 'No explicit source-bound signing authorization.' }
foreach ($name in @('licensing','lgpl_mechanism','privacy_readiness','owner_distribution')) {
    $review=$cfg.reviews.$name
    if ($review.approved -isnot [bool] -or -not $review.approved -or -not $review.evidence) { throw 'Unapproved release review; no key access.' }
}
if ($cfg.roles.$Role.authorized -isnot [bool] -or -not $cfg.roles.$Role.authorized -or -not $cfg.roles.$Role.rights_evidence) { throw 'Owned component role not authorized.' }
$file=[IO.Path]::GetFullPath($File)
$expectedPayload=Join-Path $root 'dist/AgroLines'
if (-not $cfg.native_payload -or [IO.Path]::GetFullPath($cfg.native_payload).TrimEnd('\') -cne [IO.Path]::GetFullPath($expectedPayload).TrimEnd('\')) { throw 'Native gate must bind the exact Inno payload, not a different directory.' }
$directory=if ($Role -eq 'uninstaller') { $cfg.compiler_temporary_directory } else { $cfg.owned_output_directory }
if (-not $directory -or -not $file.StartsWith(([IO.Path]::GetFullPath($directory).TrimEnd('\') + '\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Component outside isolated authorized build scope.' }
$item=Get-Item -LiteralPath $file
if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint -or $item.PSIsContainer) { throw 'Unsafe component path.' }
$parent=$item.Directory
while ($parent) {
    if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse directory in signing scope.' }
    $parent=$parent.Parent
}
$version=[Diagnostics.FileVersionInfo]::GetVersionInfo($file)
if ($version.CompanyName -cne $cfg.manufacturer -or $version.FileVersion -cne $cfg.version -or
    $version.ProductName -notlike 'AgroLines*' -or (Get-AuthenticodeSignature $file).Status -ne 'NotSigned') { throw 'Only new unsigned OWN AgroLines components; never overwrite a vendor signature.' }
$hash=(Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Role -eq 'launcher') {
    if ($hash -cne $cfg.launcher_sha256 -or
        (Get-FileHash (Join-Path $PSScriptRoot 'launcher.cpp') -Algorithm SHA256).Hash.ToLowerInvariant() -cne $cfg.launcher_source_sha256) { throw 'Launcher/source binding mismatch.' }
}
if ((Get-FileHash $cfg.compiler_path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $cfg.compiler_sha256 -or
    (Get-AuthenticodeSignature $cfg.compiler_path).Status -ne 'Valid') { throw 'Authorized Inno compiler changed.' }
if ((Get-FileHash $cfg.native_gate_path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $cfg.native_gate_sha256 -or
    (Get-FileHash (Join-Path $cfg.native_payload 'payload-manifest.json') -Algorithm SHA256).Hash.ToLowerInvariant() -cne $cfg.native_payload_manifest_sha256) { throw 'Signed payload/gate binding mismatch.' }
$gate=Get-Content $cfg.native_gate_path -Raw | ConvertFrom-Json
if ($gate.native_signature_gate_passed -isnot [bool] -or -not $gate.native_signature_gate_passed -or
    $gate.source_commit -cne $cfg.source_commit -or $gate.violations.Count) { throw 'Native signing transition not accepted.' }
Push-Location $root
try {
    & $cfg.python_executable -m distribution.standalone_build --root $cfg.native_payload --version $cfg.version --manufacturer $cfg.manufacturer
    if ($LASTEXITCODE) { throw 'Actual signed payload differs from its bound manifest.' }
} finally { Pop-Location }
$tools=Get-AgroSigningTools
foreach ($native in (Get-ChildItem $cfg.native_payload -Recurse -File | Where-Object Extension -In @('.exe','.dll','.pyd'))) {
    & $tools.signtool verify /pa /all /v /tw $native.FullName
    if ($LASTEXITCODE) { throw 'Actual native trust verification failed before own component signing.' }
}
Assert-AgroTimestampEndpoint $cfg.certificate.timestamp_url
if ((Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant() -cne $hash) { throw 'Component changed before signing.' }
Push-Location $root
try {
    $contentBefore=& $cfg.python_executable -c 'import sys; from scripts.signing_pipeline import pe_content_digest; print(pe_content_digest(sys.argv[1], require_unsigned=True))' $file
    if ($LASTEXITCODE) { throw 'Cannot inspect own PE content.' }
} finally { Pop-Location }
$unsignedSize=$item.Length
$cert=Get-AgroPublicSigningCertificate -ApprovedRoots @($cfg.certificate.approved_public_roots) -Thumbprint $cfg.certificate.thumbprint -Subject $cfg.certificate.subject -Provider $cfg.certificate.key_provider
& $tools.signtool sign /sha1 $cert.Thumbprint /s My /fd SHA256 /tr $cfg.certificate.timestamp_url /td SHA256 $file
if ($LASTEXITCODE) { throw 'Signing failed; candidate quarantined.' }
& $tools.signtool verify /pa /all /v /tw $file
$signature=Get-AuthenticodeSignature $file
if ($LASTEXITCODE -or $signature.Status -ne 'Valid' -or $signature.SignerCertificate.Thumbprint -cne $cert.Thumbprint -or -not $signature.TimeStamperCertificate) { throw 'Signature/timestamp verification failed.' }
Push-Location $root
try {
    $contentAfter=& $cfg.python_executable -c 'import sys; from scripts.signing_pipeline import pe_content_digest; print(pe_content_digest(sys.argv[1], expected_unsigned_size=int(sys.argv[2])))' $file $unsignedSize
    if ($LASTEXITCODE -or $contentAfter -cne $contentBefore) { throw 'Unexpected executable changes beyond signature fields.' }
} finally { Pop-Location }
@{ role=$Role; path=$file; source_commit=$cfg.source_commit; unsigned_sha256=$hash; signed_sha256=(Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant(); subject=$signature.SignerCertificate.Subject; timestamp_subject=$signature.TimeStamperCertificate.Subject; sac_approved=$false } |
    ConvertTo-Json | Set-Content ($file + '.signing.json') -Encoding utf8
