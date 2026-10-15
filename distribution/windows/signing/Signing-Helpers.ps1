# Pure preflight first; certificate/key access occurs only in the explicit signing command.
function Get-AgroSigningTools {
    $sdkRoot = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits/10/bin'
    $sdk = Get-ChildItem $sdkRoot -Directory | Where-Object {
        $_.Name -match '^10\.0\.\d+\.\d+$' -and (Test-Path (Join-Path $_.FullName 'x64/signtool.exe'))
    } | Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
    if (-not $sdk) { throw 'Windows SDK unavailable.' }
    $result = @{}
    foreach ($name in @('signtool','makeappx')) {
        $path = Join-Path $sdk.FullName "x64/$name.exe"
        $sig = Get-AuthenticodeSignature -LiteralPath $path
        if ($sig.Status -ne 'Valid' -or -not $sig.SignerCertificate -or $sig.SignerCertificate.Subject -notmatch 'Microsoft') { throw 'Untrusted Microsoft SDK.' }
        $result[$name] = $path
    }
    return $result
}
function Get-AgroApprovedSigningSet {
    param([string]$Payload,[string]$Plan,[string]$Policy,[string]$SourceCommit)
    $data = Get-Content -LiteralPath $Plan -Raw | ConvertFrom-Json
    $rules = Get-Content -LiteralPath $Policy -Raw | ConvertFrom-Json
    if ($data.schema_version -ne 1 -or $rules.schema_version -ne 1 -or
        $data.ready_for_authorized_signing -isnot [bool] -or -not $data.ready_for_authorized_signing -or $data.violations.Count -ne 0 -or
        $data.source_commit -cne $SourceCommit -or
        $data.policy_sha256 -cne (Get-FileHash -LiteralPath $Policy -Algorithm SHA256).Hash.ToLowerInvariant()) {
        throw 'ASSINATURA PENDENTE: complete authorized policy/source/plan required before key access.'
    }
    $root = [IO.Path]::GetFullPath($Payload).TrimEnd('\')
    $prefix = $root + '\'
    $entries = @(Get-ChildItem -LiteralPath $root -Recurse -Force)
    if ((Get-Item -LiteralPath $root).Attributes -band [IO.FileAttributes]::ReparsePoint -or
        @($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw 'Payload reparse point prohibited.' }
    $actual = @($entries | Where-Object { -not $_.PSIsContainer -and $_.Extension -in @('.dll','.pyd','.exe') })
    if (-not $data.files.Count -or $actual.Count -ne $data.files.Count) { throw 'Signing plan/native tree differ.' }
    $actualPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $actual) { $actualPaths.Add($entry.FullName) | Out-Null }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $approved = [Collections.Generic.List[object]]::new()
    foreach ($file in $data.files) {
        if (-not $seen.Add($file.path) -or $file.path -match '\\|:|(^|/)\.\.?(/|$)' -or $file.path.StartsWith('/')) { throw 'Unsafe/duplicate plan path.' }
        $path = [IO.Path]::GetFullPath((Join-Path $root $file.path))
        if (-not $path.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or
            -not $actualPaths.Contains($path) -or -not (Test-Path -LiteralPath $path -PathType Leaf) -or
            (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $file.sha256) { throw 'Native input changed.' }
        $policyEntry = @($rules.files | Where-Object path -CEQ $file.path)
        if ($policyEntry.Count -ne 1 -or $policyEntry[0].action -cne $file.action) { throw 'Plan not authorized by exact policy entry.' }
        $rule = $policyEntry[0]
        if ($rule.rights_confirmed -isnot [bool] -or $rule.origin_confirmed -isnot [bool] -or $file.sign_authorized -isnot [bool]) { throw 'Explicit boolean rights/origin/action decisions required.' }
        if ($file.sign_authorized) {
            if ($file.authenticode -ne 'NotSigned' -or -not $rule.rights_confirmed -or -not $rule.origin_confirmed -or -not $rule.rights_evidence) { throw 'Signing rights/origin not approved.' }
            if ($rule.action -eq 'sign_own') {
                $ownEntryPoint = if ($rules.profile -eq 'standalone-offline') { 'AgroLines.exe' } else { 'AgroLinesPoC.exe' }
                if ($file.path -cne $ownEntryPoint) { throw 'Own signing restricted to built entrypoint.' }
            } elseif ($rule.action -ne 'sign_third_party' -or $rule.baseline_sha256 -cne $file.sha256) { throw 'Third-party signing not explicitly authorized by hash.' }
            $approved.Add(@{path=$path; sha256=$file.sha256; relative=$file.path})
        } elseif ($rule.action -ne 'preserve_original' -or -not $rule.origin_confirmed -or $rule.baseline_sha256 -cne $file.sha256) { throw 'Original vendor bytes/provenance must be preserved.' }
    }
    return @($approved.ToArray())
}
function Get-AgroPublicSigningCertificate {
    param([string]$Thumbprint,[string]$Subject,[string]$Provider,[object[]]$ApprovedRoots)
    if ($Thumbprint -notmatch '^[0-9a-fA-F]{40}$' -or -not $Subject -or -not $Provider) { throw 'Configure public certificate identity and CA-approved hardware/KSP provider.' }
    if (-not $ApprovedRoots.Count) { throw 'Approved public CA root dossier/allowlist missing; no key access.' }
    $cert = Get-Item -LiteralPath "Cert:\CurrentUser\My\$Thumbprint"
    if (-not $cert.HasPrivateKey -or $cert.Subject -cne $Subject -or $cert.Issuer -eq $cert.Subject -or
        $cert.NotBefore.ToUniversalTime() -gt [DateTime]::UtcNow -or $cert.NotAfter.ToUniversalTime() -le [DateTime]::UtcNow) { throw 'Real valid non-self-signed private-key certificate required.' }
    $usage = $cert.Extensions | Where-Object { $_.Oid.Value -eq '2.5.29.37' }
    if (-not $usage -or @($usage.EnhancedKeyUsages | Where-Object Value -eq '1.3.6.1.5.5.7.3.3').Count -eq 0) { throw 'Code Signing EKU required.' }
    if ($cert.PublicKey.Oid.Value -notin @('1.2.840.113549.1.1.1','1.2.840.10045.2.1')) { throw 'Unreviewed signing algorithm.' }
    $chain = [Security.Cryptography.X509Certificates.X509Chain]::new()
    try {
        $chain.ChainPolicy.RevocationMode = 'Online'
        $chain.ChainPolicy.RevocationFlag = 'ExcludeRoot'
        $chain.ChainPolicy.UrlRetrievalTimeout = [TimeSpan]::FromSeconds(10)
        $chain.ChainPolicy.ApplicationPolicy.Add([Security.Cryptography.Oid]::new('1.3.6.1.5.5.7.3.3')) | Out-Null
        if (-not $chain.Build($cert)) { throw 'Current signing certificate chain/revocation not accepted; no overrides.' }
        $anchor = $chain.ChainElements[$chain.ChainElements.Count - 1].Certificate
        $rootHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($anchor.RawData)).ToLowerInvariant()
        $approved = @($ApprovedRoots | Where-Object { $_.sha256 -cmatch '^[a-f0-9]{64}$' -and $_.sha256 -ceq $rootHash -and $_.evidence })
        if ($approved.Count -ne 1) { throw 'Root not pinned by reviewed public CA dossier; local/private trust alone is insufficient.' }
    } finally { $chain.Dispose() }
    $private = $null
    try {
        if ($cert.PublicKey.Oid.Value -eq '1.2.840.113549.1.1.1') { $private = [Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert) }
        else { $private = [Security.Cryptography.X509Certificates.ECDsaCertificateExtensions]::GetECDsaPrivateKey($cert) }
        if ($private -is [Security.Cryptography.RSACryptoServiceProvider]) {
            $actualProvider = $private.CspKeyContainerInfo.ProviderName
            if (-not $private.CspKeyContainerInfo.HardwareDevice -or $private.CspKeyContainerInfo.Exportable) { throw 'Exportable/software private key rejected.' }
        } elseif ($private -is [Security.Cryptography.RSACng] -or $private -is [Security.Cryptography.ECDsaCng]) {
            $actualProvider = $private.Key.Provider.Provider
            if ($private.Key.ExportPolicy -ne [Security.Cryptography.CngExportPolicies]::None) { throw 'Exportable key rejected.' }
        } else { throw 'Unsupported key provider; no PFX fallback.' }
        if ($actualProvider -cne $Provider -or $actualProvider -in @('Microsoft Software Key Storage Provider','Microsoft Enhanced RSA and AES Cryptographic Provider')) { throw 'Provider mismatch/software key prohibited.' }
        # CNG provider name alone does not prove HSM certification: CA attestation is a manual prerequisite.
    } finally { if ($private) { $private.Dispose() } }
    return $cert
}
function Assert-AgroTimestampEndpoint {
    param([string]$Url)
    $parsed = $null
    if (-not [Uri]::TryCreate($Url,[UriKind]::Absolute,[ref]$parsed) -or $parsed.Scheme -ne 'https' -or $parsed.UserInfo -or -not $parsed.Host -or $parsed.Query) { throw 'Configured HTTPS RFC3161 timestamp endpoint required; no embedded credentials.' }
}
