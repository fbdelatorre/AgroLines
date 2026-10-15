# Invoked only by a future authorized Inno compile, never by experimental PR CI.
param([Parameter(Mandatory)][string]$File,[Parameter(Mandatory)][string]$Configuration)
$ErrorActionPreference='Stop'
$cfg=Get-Content $Configuration -Raw | ConvertFrom-Json
$path=[IO.Path]::GetFullPath($File)
$role=if ($cfg.compiler_temporary_directory -and $path.StartsWith(([IO.Path]::GetFullPath($cfg.compiler_temporary_directory).TrimEnd('\') + '\'),[StringComparison]::OrdinalIgnoreCase)) { 'uninstaller' } else { 'installer' }
& (Join-Path $PSScriptRoot 'Sign-OwnedComponent.ps1') -File $File -Configuration $Configuration -Role $role
