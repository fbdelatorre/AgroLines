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
$metadata=Get-Content (Join-Path $root 'build/distribution/metadata.json') -Raw | ConvertFrom-Json
$version=$metadata.version.Replace('.',',')
$resource=Join-Path (Split-Path -Parent $output) 'launcher.rc'
$compiledResource=Join-Path (Split-Path -Parent $output) 'launcher.res'
$icon=(Join-Path $root 'build/distribution/AgroLines.ico').Replace('\','/')
@"
1 ICON "$icon"
1 VERSIONINFO
FILEVERSION $version
PRODUCTVERSION $version
FILETYPE 1
BEGIN
 BLOCK "StringFileInfo"
 BEGIN
  BLOCK "041604b0"
  BEGIN
   VALUE "CompanyName", "$($metadata.manufacturer)\0"
   VALUE "FileDescription", "AgroLines Stable Launcher\0"
   VALUE "ProductName", "AgroLines\0"
   VALUE "FileVersion", "$($metadata.version)\0"
   VALUE "OriginalFilename", "AgroLines.exe\0"
  END
 END
 BLOCK "VarFileInfo"
 BEGIN
  VALUE "Translation", 0x0416, 1200
 END
END
"@ | Set-Content $resource -Encoding utf8
@('@echo off', ('call "' + $developer + '" -arch=x64 -host_arch=x64'), 'if errorlevel 1 exit /b %errorlevel%',
  ('rc /nologo /fo "' + $compiledResource + '" "' + $resource + '"'), 'if errorlevel 1 exit /b %errorlevel%',
  ('cl /nologo /O2 /MT /W4 /WX /sdl /guard:cf /utf-8 /std:c++17 "' + $source + '" "' + $compiledResource + '" /Fo"' + $object + '" /Fe"' + $output + '" /link /SUBSYSTEM:WINDOWS /DYNAMICBASE /NXCOMPAT /HIGHENTROPYVA shell32.lib advapi32.lib user32.lib'),
  'exit /b %errorlevel%') | Set-Content $build -Encoding ascii
& cmd.exe /d /c $build
if ($LASTEXITCODE) { throw 'Launcher compilation failed.' }
if ((Get-AuthenticodeSignature $output).Status -ne 'NotSigned') { throw 'Unexpected signing in experimental build.' }
@{ source_sha256=(Get-FileHash $source -Algorithm SHA256).Hash.ToLowerInvariant(); file=[IO.Path]::GetFileName($output); sha256=(Get-FileHash $output -Algorithm SHA256).Hash.ToLowerInvariant(); signing_performed=$false; sac_approved=$false } |
    ConvertTo-Json | Set-Content ($output + '.provenance.json') -Encoding utf8
