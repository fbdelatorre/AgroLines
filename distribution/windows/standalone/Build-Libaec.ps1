# Authorized disposable builder only; compile BSD source, never install or sign.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$installation=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installation) { throw 'MSVC x64 build tools required.' }
$developer=Join-Path $installation 'Common7/Tools/VsDevCmd.bat'
$python=[IO.Path]::GetFullPath('build-env/Scripts/python.exe')
$command=Join-Path $env:RUNNER_TEMP 'agrolines-libaec-build.cmd'
@('@echo off',('call "' + $developer + '" -arch=x64 -host_arch=x64'),'if errorlevel 1 exit /b %errorlevel%',('"' + $python + '" -m distribution.libaec_build --build build/legal-native'),'exit /b %errorlevel%') | Set-Content $command -Encoding ascii
& cmd.exe /d /c $command
if ($LASTEXITCODE) { throw 'libaec source build/upstream test failed.' }
Copy-Item build/legal-native/provenance.json evidence/standalone/libaec-build.json
Copy-Item build/legal-native/ctest.txt evidence/standalone/libaec-ctest.txt
