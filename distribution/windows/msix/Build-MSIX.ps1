# Maintainer SDK/build helper. Never signs, publishes, changes identity or installs certificates.
[CmdletBinding()]
param(
    [string]$Version = '1.0.0.0',
    [string]$Python = 'build-env/Scripts/python.exe',
    [string]$Payload = 'dist/AgroLinesPoC',
    [string]$OutputDirectory = 'dist/msix',
    [string]$EvidenceDirectory = 'evidence/msix'
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
Push-Location $repoRoot
try {
    $sdkRoot = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits/10/bin'
    $sdkCandidates = Get-ChildItem $sdkRoot -Directory | Where-Object {
        $_.Name -match '^10\.0\.\d+\.\d+$' -and (Test-Path (Join-Path $_.FullName 'x64/makeappx.exe'))
    } | Sort-Object { [version]$_.Name } -Descending
    if (-not $sdkCandidates) { throw 'Windows SDK x64 MakeAppx nao encontrado.' }
    $makeappx = Join-Path $sdkCandidates[0].FullName 'x64/makeappx.exe'
    if ((Get-AuthenticodeSignature $makeappx).Status -ne 'Valid') { throw 'Assinatura do SDK invalida.' }
    New-Item $OutputDirectory,$EvidenceDirectory -ItemType Directory -Force | Out-Null
    $staging = Join-Path $repoRoot "build/msix/$Version"
    $unpacked = Join-Path $repoRoot "build/msix-unpacked/$Version"
    $package = Join-Path $OutputDirectory "AgroLines-$Version-x64-STORE-SUBMISSION-UNSIGNED.msix"
    if (Test-Path $package) { throw 'Pacote ja existe; nao sobrescrever artefato auditado.' }
    & $Python -m distribution.msix --payload $Payload --output $staging --version $Version --report "$EvidenceDirectory/staging-$Version.json"
    if ($LASTEXITCODE) { throw 'Preparacao do MSIX falhou.' }
    & $makeappx pack /d $staging /p $package /h SHA256 /v
    if ($LASTEXITCODE) { throw 'MakeAppx pack/validacao de schema falhou.' }
    & $makeappx unpack /p $package /d $unpacked /v
    if ($LASTEXITCODE) { throw 'MakeAppx unpack falhou.' }
    & $Python -c 'import json,sys; from distribution.payload import verify; from pathlib import Path; root=Path(sys.argv[1]); assert verify(root,json.loads((root/"payload-manifest.json").read_text()))' "$unpacked/VFS/ProgramFilesX64/AgroLines"
    if ($LASTEXITCODE) { throw 'Round-trip MSIX alterou o payload nativo.' }
    $hash = Get-FileHash $package -Algorithm SHA256
    @{
        file = (Split-Path $package -Leaf); sha256 = $hash.Hash; sdk = $sdkCandidates[0].Name
        signature = 'unsigned-store-submission'; installed_msix_validated = $false
        smart_app_control_approved = $false; automatic_store_publication = $false
    } | ConvertTo-Json | Set-Content "$EvidenceDirectory/package-$Version.json" -Encoding utf8
    Write-Output '::warning::MSIX NAO ASSINADO para revisao/submissao manual. Nao e pacote instalado/homologado SAC.'
} finally { Pop-Location }
