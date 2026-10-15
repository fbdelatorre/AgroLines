param(
    [string]$Version = '0.1.0.1',
    [string]$Manufacturer = 'Delatorre Corporation',
    [string]$CertificateThumbprint,
    [switch]$Standalone,
    [switch]$Experimental,
    [string]$CandidateId,
    [string]$Compiler,
    [string]$PythonExecutable = 'python'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $Compiler) {
    $Compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
}
if (-not (Test-Path -LiteralPath $Compiler)) { throw 'Compilador Inno Setup indisponivel no builder.' }
if ((Get-AuthenticodeSignature -LiteralPath $Compiler).Status -ne 'Valid') { throw 'Compilador sem assinatura confiavel.' }
if ($Manufacturer -match '["\r\n]' -or $Manufacturer.Length -gt 120) { throw 'Fabricante invalido.' }
if ($Version -notmatch '^\d+\.\d+\.\d+\.\d+$') { throw 'Versao invalida.' }
$arguments = @('/Qp', "/DVersion=$Version", "/DManufacturer=$Manufacturer")
if ($Standalone) {
    if (-not $Experimental -or $CertificateThumbprint) { throw 'Standalone limitado a compilacao experimental sem assinatura nesta etapa.' }
    if ($CandidateId -notmatch '^[0-9a-f]{12}$') { throw 'Identificador de candidato invalido.' }
    # Validate exact payload/metadata before compiling. Never install or launch it here.
    Push-Location $root
    try {
        & $PythonExecutable -m distribution.standalone_build --root dist/AgroLines --version $Version --manufacturer $Manufacturer
        if ($LASTEXITCODE) { throw 'Payload standalone invalido.' }
    } finally { Pop-Location }
    $launcher=Join-Path $root 'build/distribution/AgroLinesLauncher.exe'
    $launcherProvenance=Get-Content ($launcher + '.provenance.json') -Raw | ConvertFrom-Json
    if ((Get-FileHash $launcher -Algorithm SHA256).Hash.ToLowerInvariant() -cne $launcherProvenance.sha256 -or
        (Get-FileHash (Join-Path $PSScriptRoot 'standalone/launcher.cpp') -Algorithm SHA256).Hash.ToLowerInvariant() -cne $launcherProvenance.source_sha256) { throw 'Launcher build/source changed.' }
    [IO.File]::WriteAllText((Join-Path $root 'build/distribution/AgroLines.current.txt'), "$Version-$CandidateId`n", [Text.Encoding]::ASCII)
    $arguments += @('/DStandalone', '/DExperimental', "/DCandidateId=$CandidateId")
    # Keep compiler inclusion evidence for the actual legal files, without installation.
    $arguments = @($arguments | Where-Object { $_ -cne '/Qp' })
}
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
if ($Standalone) {
    $log=Join-Path $root 'evidence/standalone/inno-compile.log'
    & $Compiler @arguments 2>&1 | Tee-Object -FilePath $log
} else {
    & $Compiler @arguments
}
if ($LASTEXITCODE -ne 0) { throw 'Compilacao do instalador falhou.' }
if ($Standalone) {
    $compiled=Get-Content $log -Raw
    foreach ($name in @('EULA.txt','politica-privacidade.txt','INSTRUCOES-LGPL.txt','THIRD_PARTY_NOTICES.txt','legal-manifest.json')) {
        if ($compiled.IndexOf($name,[StringComparison]::OrdinalIgnoreCase) -lt 0) { throw ('Missing compiler inclusion evidence: ' + $name) }
    }
    & $PythonExecutable -m distribution.legal_materials --payload (Join-Path $root 'dist/AgroLines') --output (Join-Path $root 'evidence/standalone/compiled-legal-materials.json')
    if ($LASTEXITCODE) { throw 'Legal input changed during compilation.' }
}
if (-not $CertificateThumbprint) { Write-Output 'ARTEFATO INTERNO NAO ASSINADO: nao aprovado para SAC/distribuicao.' }
