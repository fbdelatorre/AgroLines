# Read-only Authenticode audit. Never changes trust stores, policies or executable bytes.
param(
    [Parameter(Mandatory = $true)][string]$Inventory,
    [Parameter(Mandatory = $true)][string]$Output,
    [switch]$Strict
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Esta auditoria exige Windows.' }
$data = Get-Content -LiteralPath $Inventory -Raw | ConvertFrom-Json
if ($data.schema_version -ne 1 -or -not $data.inspection_complete) {
    throw 'Inventario incompleto; nao pode fundamentar aprovacao.'
}
$chains = @{}
$results = @()
foreach ($file in $data.files) {
    $record = [ordered]@{
        path = $file.path; sha256 = $file.sha256; packages = @($file.packages)
        status = 'InspectionError'; signature_type = $null; signer = $null
        signer_thumbprint = $null; timestamp_signer = $null
        chain_valid = $false; chain_status = @(); integrity_matches = $false
    }
    try {
        if ($file.format -ne 'PE') { throw 'Native format is not PE; cannot approve on Windows.' }
        $record.integrity_matches = ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant() -eq $file.sha256)
        if (-not $record.integrity_matches) { throw 'Arquivo mudou depois do inventario.' }
        $signature = Get-AuthenticodeSignature -LiteralPath $file.path
        $record.status = $signature.Status.ToString()
        $record.signature_type = $signature.SignatureType.ToString()
        if ($signature.SignerCertificate) {
            $cert = $signature.SignerCertificate
            $record.signer = $cert.Subject
            $record.signer_thumbprint = $cert.Thumbprint
            if (-not $chains.ContainsKey($cert.Thumbprint)) {
                $chain = [System.Security.Cryptography.X509Certificates.X509Chain]::new()
                try {
                    $chain.ChainPolicy.RevocationMode = 'Online'
                    $chain.ChainPolicy.RevocationFlag = 'ExcludeRoot'
                    $chain.ChainPolicy.UrlRetrievalTimeout = [TimeSpan]::FromSeconds(5)
                    $valid = $chain.Build($cert)
                    $chains[$cert.Thumbprint] = @{
                        valid = $valid
                        status = @($chain.ChainStatus | ForEach-Object { $_.Status.ToString() })
                    }
                } finally { $chain.Dispose() }
            }
            $record.chain_valid = $chains[$cert.Thumbprint].valid
            $record.chain_status = $chains[$cert.Thumbprint].status
        }
        if ($signature.TimeStamperCertificate) {
            $record.timestamp_signer = $signature.TimeStamperCertificate.Subject
        }
    } catch { $record.status = 'InspectionError' }
    $results += [PSCustomObject]$record
}
$unverified = @($results | Where-Object { $_.status -ne 'Valid' -or -not $_.chain_valid -or -not $_.integrity_matches })
$report = [ordered]@{
    schema_version = 1; generated_utc = [DateTime]::UtcNow.ToString('o')
    python_version = $data.python_version; packages = $data.packages
    roots = $data.roots; files = $results
    inspected_pe_files = $results.Count; unverified_files = $unverified.Count
    signatures_and_chains_verified = ($results.Count -gt 0 -and $unverified.Count -eq 0)
    smart_app_control_compatibility_proven = $false
    note = 'Assinatura/cadeia valida nao comprova reputacao nem aceitacao pelo SAC.'
}
$parent = Split-Path -Parent ([IO.Path]::GetFullPath($Output))
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Output -Encoding utf8
Write-Output "PE inspecionados: $($results.Count); sem verificacao completa: $($unverified.Count). SAC nao homologado."
foreach ($group in ($results | Group-Object { if ($_.packages.Count) { $_.packages[0].name } else { 'runtime/unowned' } })) {
    $valid = @($group.Group | Where-Object { $_.status -eq 'Valid' }).Count
    $unsigned = @($group.Group | Where-Object { $_.status -eq 'NotSigned' }).Count
    Write-Output "$($group.Name): total=$($group.Count), assinaturaValid=$valid, NotSigned=$unsigned"
}
if ($Strict -and -not $report.signatures_and_chains_verified) { exit 1 }
