# Compatibility entrypoint. Blind signing of every unsigned file has been removed.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Payload,
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$Policy,
    [Parameter(Mandatory)][string]$SourceCommit,
    [Parameter(Mandatory)][string]$CertificateThumbprint,
    [Parameter(Mandatory)][string]$ExpectedSignerSubject,
    [Parameter(Mandatory)][string]$ExpectedKeyProvider,
    [Parameter(Mandatory)][string]$TimestampUrl
)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'signing/Sign-ApprovedNative.ps1') @PSBoundParameters
