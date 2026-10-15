# Authorized builder only. Same library versions and algorithms; never install/sign.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$installation=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installation) { throw 'MSVC x64 build tools required.' }
$developer=Join-Path $installation 'Common7/Tools/VsDevCmd.bat'
$python=[IO.Path]::GetFullPath('build-env/Scripts/python.exe')
$command=Join-Path $env:RUNNER_TEMP 'agrolines-geos-source-build.cmd'
@('@echo off',('call "' + $developer + '" -arch=x64 -host_arch=x64'),'if errorlevel 1 exit /b %errorlevel%',('"' + $python + '" -m distribution.geos_delivery --work build/legal-geos --cache build/source-cache'),'exit /b %errorlevel%') | Set-Content $command -Encoding ascii
& cmd.exe /d /c $command
if ($LASTEXITCODE) { throw 'GEOS source build failed.' }
Copy-Item build/legal-geos/provenance.json evidence/standalone/geos-source-builds.json
