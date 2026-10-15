# Read-only Windows guest evidence; no host commands or security configuration writes.
param([Parameter(Mandatory)][string]$Output,[ValidateSet('initial','before-install','blocked','after-tests')][string]$Phase='initial',[string]$Installer)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Windows-Security.ps1')
$os=Get-CimInstance Win32_OperatingSystem
$computer=Get-CimInstance Win32_ComputerSystem
$sac=Get-AgroSacState
$secure=$null; $tpm=$null; $defender=$null; $errors=@()
try { $secure=Confirm-SecureBootUEFI } catch { $errors+='Secure Boot read unavailable' }
try { $tpm=Get-Tpm | Select-Object TpmPresent,TpmReady } catch { $errors+='TPM read unavailable' }
try { $defender=Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled } catch { $errors+='Defender read unavailable' }
$package=$null
if ($Installer) {
    $file=Get-Item -LiteralPath $Installer
    $signature=Get-AuthenticodeSignature -LiteralPath $Installer
    $package=@{name=$file.Name;bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant();authenticode_status=$signature.Status.ToString()}
}
$report=@{correlation_id=[Guid]::NewGuid().ToString();phase=$Phase;time_utc=[DateTime]::UtcNow.ToString('o');windows=($os|Select-Object Caption,Version,BuildNumber,ProductType);hyper_v_guest=($computer.Manufacturer -eq 'Microsoft Corporation' -and $computer.Model -eq 'Virtual Machine');logical_processors=$computer.NumberOfLogicalProcessors;memory_bytes=$computer.TotalPhysicalMemory;secure_boot=$secure;tpm=$tpm;defender=$defender;sac=@{registry_state=$sac.registry_state;active_confirmed=$sac.active_confirmed;errors=$sac.errors};installer=$package;errors=$errors;protections_modified_by_script=$false;sac_approved=$false}
$target=[IO.Path]::GetFullPath($Output)
if (Test-Path -LiteralPath $target) { throw 'Choose a fresh evidence filename; existing evidence is never overwritten.' }
[IO.Directory]::CreateDirectory((Split-Path -Parent $target)) | Out-Null
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $target -Encoding utf8
Write-Output 'Read-only evidence saved. Review it before sharing; unknown states are not approval.'
