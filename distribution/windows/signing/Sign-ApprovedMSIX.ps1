# Optional envelope operation only; a normal PE certificate may not match the Store Publisher GUID.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Package,
    [Parameter(Mandatory)][string]$ExpectedSha256,
    [Parameter(Mandatory)][string]$CertificateThumbprint,
    [Parameter(Mandatory)][string]$ExpectedKeyProvider,
    [Parameter(Mandatory)][string]$TimestampUrl
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Signing-Helpers.ps1')
$identity = Get-Content (Join-Path $PSScriptRoot '../msix/identity.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedSha256) { throw 'MSIX hash differs before optional signing.' }
$archive = [IO.Compression.ZipFile]::OpenRead([IO.Path]::GetFullPath($Package))
try {
    if ($archive.GetEntry('AppxSignature.p7x')) { throw 'Already signed MSIX must not be re-signed.' }
    $entry = $archive.GetEntry('AppxManifest.xml')
    if (-not $entry) { throw 'Missing package manifest.' }
    $reader = [IO.StreamReader]::new($entry.Open())
    try { $xml = $reader.ReadToEnd() } finally { $reader.Dispose() }
    $settings = [Xml.XmlReaderSettings]::new(); $settings.DtdProcessing = 'Prohibit'; $settings.XmlResolver = $null
    $xmlReader = [Xml.XmlReader]::Create([IO.StringReader]::new($xml),$settings)
    try { $doc = [Xml.XmlDocument]::new(); $doc.Load($xmlReader) } finally { $xmlReader.Dispose() }
    $ns = [Xml.XmlNamespaceManager]::new($doc.NameTable); $ns.AddNamespace('f','http://schemas.microsoft.com/appx/manifest/foundation/windows10')
    $declared = $doc.SelectSingleNode('/f:Package/f:Identity',$ns)
    if ($declared.GetAttribute('Name') -cne $identity.name -or $declared.GetAttribute('Publisher') -cne $identity.publisher -or $declared.GetAttribute('ProcessorArchitecture') -cne 'x64') { throw 'Official identity must never be substituted.' }
} finally { $archive.Dispose() }
Assert-AgroTimestampEndpoint $TimestampUrl
$tools = Get-AgroSigningTools
$cert = Get-AgroPublicSigningCertificate -Thumbprint $CertificateThumbprint -Subject $identity.publisher -Provider $ExpectedKeyProvider
& $tools.signtool sign /sha1 $cert.Thumbprint /s My /fd SHA256 /tr $TimestampUrl /td SHA256 $Package
if ($LASTEXITCODE) { throw 'MSIX signing failed.' }
& $tools.signtool verify /pa /all /v /tw $Package
if ($LASTEXITCODE -or -not (Get-AuthenticodeSignature $Package).TimeStamperCertificate) { throw 'MSIX signature/timestamp failed.' }
