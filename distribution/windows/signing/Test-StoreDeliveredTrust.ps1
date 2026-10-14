# Read-only: inspect a Store-installed official package and each embedded/catalog trust path.
# Does not install, register catalogs, change trust/security or approve SAC.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Signing-Helpers.ps1')
. (Join-Path $PSScriptRoot '../../../scripts/Windows-Security.ps1')
$pkg = Get-AppxPackage -Name 'DelatorreCOrporation.AgroLines'
if (-not $pkg -or $pkg.PackageFamilyName -cne 'DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg' -or
    $pkg.SignatureKind.ToString() -cne 'Store' -or $pkg.Status.ToString() -cne 'Ok') { throw 'Official Store-installed package with Store signature/status required.' }
$directory = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path $directory) { throw 'Use a new evidence directory.' }
if ($directory.StartsWith($pkg.InstallLocation,[StringComparison]::OrdinalIgnoreCase)) { throw 'Evidence must be outside package.' }
New-Item $directory -ItemType Directory | Out-Null
$tools = Get-AgroSigningTools
$catalog = Join-Path $pkg.InstallLocation 'AppxMetadata/CodeIntegrity.cat'
$catalogValid = $false
if (Test-Path -LiteralPath $catalog) {
    & $tools.signtool verify /pa /all /v $catalog *> (Join-Path $directory 'catalog-verification.txt')
    $catalogValid = ($LASTEXITCODE -eq 0)
}
$files = @(Get-ChildItem -LiteralPath $pkg.InstallLocation -Recurse -File | Where-Object Extension -In @('.exe','.dll','.pyd'))
if (-not $files.Count) { throw 'No native package files.' }
$results = @(); $i = 0
foreach ($file in $files) {
    $relative = $file.FullName.Substring($pkg.InstallLocation.Length).TrimStart('\').Replace('\','/')
    & $tools.signtool verify /pa /all /v /tw $file.FullName *> (Join-Path $directory "embedded-$i.txt")
    $embedded = $LASTEXITCODE
    $catalogCode = $null
    if ($catalogValid) {
        & $tools.signtool verify /pa /v /c $catalog $file.FullName *> (Join-Path $directory "catalog-member-$i.txt")
        $catalogCode = $LASTEXITCODE
    }
    $results += @{
        path=$relative; sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        embedded_verify_exit=$embedded; explicit_catalog_verify_exit=$catalogCode
        trust_verified=($embedded -eq 0 -or ($catalogValid -and $catalogCode -eq 0))
    }
    $i++
}
@{
    package_full_name=$pkg.PackageFullName; package_family_name=$pkg.PackageFamilyName; signature_kind=$pkg.SignatureKind.ToString()
    catalog_present=(Test-Path -LiteralPath $catalog); catalog_signature_verified=$catalogValid
    files=$results; all_native_trust_verified=(@($results | Where-Object { -not $_.trust_verified }).Count -eq 0)
    sac_state=(Get-AgroSacState); defender=(Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled)
    sac_approved=$false; distribution_approved=$false
    note='Embedded Authenticode and explicit Store catalog membership are different evidence. Real protected offline operation/update still required.'
} | ConvertTo-Json -Depth 12 | Set-Content (Join-Path $directory 'store-native-trust.json') -Encoding utf8
Write-Output 'Read-only Store-native trust collected; SAC approval remains pending physical functional tests.'
