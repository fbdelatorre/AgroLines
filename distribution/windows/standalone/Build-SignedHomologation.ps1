# Prepared for FUTURE authorized protected execution. Never called by PR workflows.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Configuration)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot '../signing/Assert-SigningEnvironment.ps1')
$cfg=Get-Content $Configuration -Raw | ConvertFrom-Json
if ($cfg.authorized -isnot [bool] -or -not $cfg.authorized -or -not $cfg.approval_reference -or
    $cfg.source_commit -cne $env:GITHUB_SHA -or $cfg.candidate_id -cne $env:GITHUB_SHA.Substring(0,12)) { throw 'Explicit source-bound owner authorization missing.' }
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$launcher=Join-Path $root 'build/distribution/AgroLinesLauncher.exe'
& (Join-Path $PSScriptRoot 'Sign-OwnedComponent.ps1') -File $launcher -Configuration $Configuration -Role launcher
$oldTemp=$env:TEMP; $oldTmp=$env:TMP
if (-not $cfg.compiler_temporary_directory -or (Test-Path $cfg.compiler_temporary_directory)) { throw 'Fresh isolated Inno temporary scope required.' }
New-Item $cfg.compiler_temporary_directory -ItemType Directory | Out-Null
try {
    $env:TEMP=$cfg.compiler_temporary_directory; $env:TMP=$cfg.compiler_temporary_directory
    $powershell=(Get-Command pwsh).Source
    $callback=Join-Path $PSScriptRoot 'Inno-SigningCallback.ps1'
    foreach ($path in @($Configuration,$callback,$powershell)) { if ($path -match '["\r\n]') { throw 'Unsafe callback argument.' } }
    $command='$q' + $powershell + '$q -NoProfile -File $q' + $callback + '$q -Configuration $q' + [IO.Path]::GetFullPath($Configuration) + '$q -File $f'
    # No Experimental define: output explicitly identifies signed private homologation.
    $arguments=@('/Qp','/DStandalone',('/DVersion=' + $cfg.version),('/DManufacturer=' + $cfg.manufacturer),('/DCandidateId=' + $cfg.candidate_id),'/DSigningTool=agrolines',('/Sagrolines=' + $command),(Join-Path $PSScriptRoot '../installer.iss'))
    # Generate the exact fixed pointer only after the signed onedir/native gate passed.
    [IO.File]::WriteAllText((Join-Path $root 'build/distribution/AgroLines.current.txt'), "$($cfg.version)-$($cfg.candidate_id)`n", [Text.Encoding]::ASCII)
    & $cfg.compiler_path @arguments
    if ($LASTEXITCODE) { throw 'Signed compilation failed; no release authorization.' }
} finally { $env:TEMP=$oldTemp; $env:TMP=$oldTmp }
Write-Output 'Signed candidate compiled for future physical homologation only; SAC/commercial approval remains pending.'
