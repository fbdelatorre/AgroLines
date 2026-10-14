param(
    [string]$Version = '0.1.0.1',
    [string]$Manufacturer = 'AgroLines - identidade juridica pendente',
    [string]$CertificateThumbprint
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (-not (Test-Path -LiteralPath $compiler)) { throw 'Instale o compilador Inno Setup 6 no builder, nao no cliente.' }
if ($Manufacturer -match '["\r\n]' -or $Manufacturer.Length -gt 120) { throw 'Fabricante invalido.' }
if ($Version -notmatch '^\d+\.\d+\.\d+\.\d+$') { throw 'Versao invalida.' }
$arguments = @('/Qp', "/DVersion=$Version", "/DManufacturer=$Manufacturer")
if ($CertificateThumbprint) {
    if ($CertificateThumbprint -notmatch '^[0-9a-fA-F]{40}$') { throw 'Thumbprint invalido.' }
    $signTool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin' -Filter signtool.exe -Recurse | Where-Object FullName -match '\\x64\\signtool.exe$' | Sort-Object FullName -Descending | Select-Object -First 1
    if (-not $signTool) { throw 'SignTool SDK indisponivel.' }
    # Inno signs both its embedded uninstaller and final installer.
    $command = '$q' + $signTool.FullName + '$q sign /sha1 ' + $CertificateThumbprint + ' /s My /fd SHA256 /tr https://timestamp.digicert.com /td SHA256 $f'
    $arguments += '/DSigningTool=agrolines'
    $arguments += '/Sagrolines=' + $command
}
$arguments += (Join-Path $PSScriptRoot 'installer.iss')
& $compiler @arguments
if ($LASTEXITCODE -ne 0) { throw 'Compilacao do instalador falhou.' }
if (-not $CertificateThumbprint) { Write-Output 'ARTEFATO INTERNO NAO ASSINADO: nao aprovado para SAC/distribuicao.' }
