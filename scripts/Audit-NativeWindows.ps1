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
        path = $file.path; resolved_path = $file.resolved_path; sha256 = $file.sha256; packages = @($file.packages)
        status = 'InspectionError'; signature_type = $null; signer = $null
        signer_thumbprint = $null; timestamp_signer = $null
        chain_valid = $false; chain_status = @(); integrity_matches = $false
        status_message = $null; inspection_error = $null
        signer_not_before_utc = $null; signer_not_after_utc = $null
        timestamp_not_before_utc = $null; timestamp_not_after_utc = $null
        chain_elements = @(); public_key_algorithm = $null
    }
    try {
        if ($file.format -ne 'PE') { throw 'Native format is not PE; cannot approve on Windows.' }
        $record.integrity_matches = ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash.ToLowerInvariant() -eq $file.sha256)
        if (-not $record.integrity_matches) { throw 'Arquivo mudou depois do inventario.' }
        $signature = Get-AuthenticodeSignature -LiteralPath $file.path
        $record.status = $signature.Status.ToString()
        $record.status_message = $signature.StatusMessage
        $record.signature_type = $signature.SignatureType.ToString()
        if ($signature.SignerCertificate) {
            $cert = $signature.SignerCertificate
            $record.signer = $cert.Subject
            $record.signer_thumbprint = $cert.Thumbprint
            $record.signer_not_before_utc = $cert.NotBefore.ToUniversalTime().ToString('o')
            $record.signer_not_after_utc = $cert.NotAfter.ToUniversalTime().ToString('o')
            $record.public_key_algorithm = $cert.PublicKey.Oid.Value
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
                        elements = @($chain.ChainElements | ForEach-Object {
                            @{
                                subject = $_.Certificate.Subject; issuer = $_.Certificate.Issuer
                                not_before_utc = $_.Certificate.NotBefore.ToUniversalTime().ToString('o')
                                not_after_utc = $_.Certificate.NotAfter.ToUniversalTime().ToString('o')
                                statuses = @($_.ChainElementStatus | ForEach-Object {
                                    @{ flag = $_.Status.ToString(); information = $_.StatusInformation.Trim() }
                                })
                            }
                        })
                    }
                } finally { $chain.Dispose() }
            }
            $record.chain_valid = $chains[$cert.Thumbprint].valid
            $record.chain_status = $chains[$cert.Thumbprint].status
            $record.chain_elements = $chains[$cert.Thumbprint].elements
        }
        if ($signature.TimeStamperCertificate) {
            $record.timestamp_signer = $signature.TimeStamperCertificate.Subject
            $record.timestamp_not_before_utc = $signature.TimeStamperCertificate.NotBefore.ToUniversalTime().ToString('o')
            $record.timestamp_not_after_utc = $signature.TimeStamperCertificate.NotAfter.ToUniversalTime().ToString('o')
        }
    } catch { $record.status = 'InspectionError'; $record.inspection_error = $_.Exception.Message }
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
    chain_policy = @{
        verification_time = 'Current system time; NOT Authenticode signing/timestamp time'
        revocation_mode = 'Online'; revocation_flag = 'ExcludeRoot'; retrieval_timeout_seconds = 5
        verification_flags = 'Default; no ignored errors'; application_policy = 'Generic X509 chain'
    }
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
if ($env:GITHUB_ACTIONS -eq 'true' -and -not $Strict) {
    $summary = @($results | Group-Object { if ($_.packages.Count) { $_.packages[0].name } else { 'runtime/unowned' } } | ForEach-Object {
        @{
            package = $_.Name
            versions = @($_.Group | ForEach-Object { $_.packages | ForEach-Object version } | Sort-Object -Unique)
            files = $_.Count
            valid_signature = @($_.Group | Where-Object { $_.status -eq 'Valid' }).Count
            valid_chain = @($_.Group | Where-Object chain_valid).Count
            unsigned = @($_.Group | Where-Object { $_.status -eq 'NotSigned' }).Count
            inspection_error = @($_.Group | Where-Object { $_.status -eq 'InspectionError' }).Count
        }
    })
    $line = ($summary | ConvertTo-Json -Depth 8 -Compress).Replace('%','%25').Replace("`r",'%0D').Replace("`n",'%0A')
    Write-Output "::notice title=Native trust audit (SAC unproven)::$line"
}
if ($Strict -and -not $report.signatures_and_chains_verified) { exit 1 }
