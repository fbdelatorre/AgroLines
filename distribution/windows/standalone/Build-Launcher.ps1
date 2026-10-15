# Build on maintainer Windows only. No signing, installation or dependency download.
[CmdletBinding()]
param([string]$Output='build/distribution/AgroLinesLauncher.exe')
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$source=Join-Path $PSScriptRoot 'launcher.cpp'
$output=[IO.Path]::GetFullPath($Output)
New-Item (Split-Path -Parent $output) -ItemType Directory -Force | Out-Null
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$installation=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installation) { throw 'MSVC x64 build tools unavailable.' }
$developer=Join-Path $installation 'Common7/Tools/VsDevCmd.bat'
$build=Join-Path (Split-Path -Parent $output) 'compile-launcher.cmd'
$object=Join-Path (Split-Path -Parent $output) 'launcher.obj'
@('@echo off', ('call "' + $developer + '" -arch=x64 -host_arch=x64'), 'if errorlevel 1 exit /b %errorlevel%',
  ('cl /nologo /O2 /MT /W4 /WX /sdl /guard:cf /utf-8 /std:c++17 "' + $source + '" /Fo"' + $object + '" /Fe"' + $output + '" /link /SUBSYSTEM:WINDOWS /DYNAMICBASE /NXCOMPAT /HIGHENTROPYVA shell32.lib advapi32.lib user32.lib'),
  'exit /b %errorlevel%') | Set-Content $build -Encoding ascii
& cmd.exe /d /c $build
if ($LASTEXITCODE) { throw 'Launcher compilation failed.' }
if ((Get-AuthenticodeSignature $output).Status -ne 'NotSigned') { throw 'Unexpected signing in experimental build.' }
@{ source_sha256=(Get-FileHash $source -Algorithm SHA256).Hash.ToLowerInvariant(); file=[IO.Path]::GetFileName($output); sha256=(Get-FileHash $output -Algorithm SHA256).Hash.ToLowerInvariant(); signing_performed=$false; sac_approved=$false } |
    ConvertTo-Json | Set-Content ($output + '.provenance.json') -Encoding utf8
