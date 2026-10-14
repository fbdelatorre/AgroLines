# Read-only exact builder sources, never a grant of redistribution rights.
[CmdletBinding()]
param([string]$Inputs, [string]$Output)
$ErrorActionPreference = 'Stop'
$data = Get-Content $Inputs -Raw | ConvertFrom-Json
$files = foreach ($entry in $data.files) {
    $path = [IO.Path]::GetFullPath($entry.source)
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $entry.source_sha256) { throw 'Build source changed since Analysis.' }
    $sig = Get-AuthenticodeSignature -LiteralPath $path
    $version = [Diagnostics.FileVersionInfo]::GetVersionInfo($path)
    @{
        source=$path; sha256=$hash; company=$version.CompanyName
        file_version=$version.FileVersion; product=$version.ProductName
        product_version=$version.ProductVersion; original_name=$version.OriginalFilename
        signature_status=$sig.Status.ToString(); signer=$sig.SignerCertificate.Subject
        signer_thumbprint=$sig.SignerCertificate.Thumbprint
        # A signed source on the runner is not a pinned vendor distribution input.
        vendor_download_hash_verified=$false; redistribution_rights_approved=$false
    }
}
@{ files=@($files) } | ConvertTo-Json -Depth 8 | Set-Content $Output -Encoding utf8
