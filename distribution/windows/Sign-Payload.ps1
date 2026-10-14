# Run on a trusted signing builder. Uses an existing non-exported certificate; no PFX/password.
param(
    [Parameter(Mandatory = $true)][string]$Payload,
    [Parameter(Mandatory = $true)][string]$CertificateThumbprint,
    [Parameter(Mandatory = $true)][string]$ExpectedSignerSubject
)
$ErrorActionPreference = 'Stop'
if ($CertificateThumbprint -notmatch '^[0-9a-fA-F]{40}$') { throw 'Thumbprint invalido.' }
$cert = Get-Item -LiteralPath "Cert:\CurrentUser\My\$CertificateThumbprint"
if (-not $cert.HasPrivateKey -or $cert.Subject -ne $ExpectedSignerSubject) { throw 'Certificado/identidade nao correspondem.' }
$signTool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin' -Filter signtool.exe -Recurse | Where-Object FullName -match '\\x64\\signtool.exe$' | Sort-Object FullName -Descending | Select-Object -First 1
if (-not $signTool) { throw 'SignTool SDK indisponivel.' }
$files = @(Get-ChildItem -LiteralPath $Payload -Recurse -File | Where-Object Extension -in @('.exe','.dll','.pyd'))
if (-not $files.Count) { throw 'Payload vazio.' }
foreach ($file in $files) {
    $signature = Get-AuthenticodeSignature -LiteralPath $file.FullName
    if ($signature.Status -eq 'NotSigned') {
        & $signTool.FullName sign /sha1 $CertificateThumbprint /s My /fd SHA256 /tr https://timestamp.digicert.com /td SHA256 $file.FullName
        if ($LASTEXITCODE -ne 0) { throw "Assinatura falhou: $($file.Name)" }
    } elseif ($signature.Status -ne 'Valid' -or $signature.SignatureType -ne 'Authenticode') {
        throw "Assinatura existente exige investigacao: $($file.Name)"
    }
    & $signTool.FullName verify /pa /all /v $file.FullName
    if ($LASTEXITCODE -ne 0) { throw "Verificacao falhou: $($file.Name)" }
}
Write-Output 'Assinaturas verificadas pelo Windows/SignTool. Aceitacao SAC ainda exige homologacao real.'
