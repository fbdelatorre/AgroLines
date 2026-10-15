param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$Report)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../../distribution/windows/Run-Frozen.ps1')
Invoke-AgroFrozenProbe -Executable $Executable -Report $Report -ReportArgument '--offline-network-report'
