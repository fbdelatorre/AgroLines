# Build tool only: verify pinned official download AND Authenticode before executing.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Directory)
$ErrorActionPreference = 'Stop'
$pin = Get-Content (Join-Path $PSScriptRoot 'inno-toolchain.json') -Raw | ConvertFrom-Json
$directory = [IO.Path]::GetFullPath($Directory)
if (Test-Path -LiteralPath $directory) { throw 'Compiler output must be fresh.' }
New-Item $directory -ItemType Directory | Out-Null
$download = Join-Path $directory 'compiler-setup.exe'
Invoke-WebRequest -Uri $pin.url -OutFile $download
$hash = (Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash.ToLowerInvariant()
$signature = Get-AuthenticodeSignature -LiteralPath $download
if ($hash -cne $pin.sha256 -or $signature.Status -ne 'Valid') { throw 'Compiler provenance/trust verification failed; nothing executed.' }
$destination = Join-Path $directory 'compiler'
$process = Start-Process -FilePath $download -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="' + $destination + '"')) -PassThru -Wait
if ($process.ExitCode -ne 0) { throw 'Build tool preparation failed.' }
$compiler = Join-Path $destination 'ISCC.exe'
if ((Get-AuthenticodeSignature -LiteralPath $compiler).Status -ne 'Valid') { throw 'Compiler executable trust failed.' }
@{ version=$pin.version; url=$pin.url; download_sha256=$hash; signer=$signature.SignerCertificate.Subject; compiler=$compiler; agrolines_installed=$false } |
    ConvertTo-Json | Set-Content (Join-Path $directory 'provenance.json') -Encoding utf8
Write-Output $compiler
