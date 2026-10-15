# Explicit user-authorized installation ONLY on disposable hosted Windows Server.
param([Parameter(Mandatory)][string]$Installer,[Parameter(Mandatory)][string]$Upgrade,[Parameter(Mandatory)][string]$Fixture,[string]$Output='evidence/functional/installed',[string]$Version='1.0.0.5',[string]$UpgradeVersion='1.0.0.6')
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1')
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Disposable builder must already be elevated; no elevation/security change attempted.' }
$fixture=[IO.Path]::GetFullPath($Fixture)
$output=[IO.Path]::GetFullPath($Output)
New-Item $output -ItemType Directory -Force | Out-Null
$lab=Join-Path $env:RUNNER_TEMP ('AgroLines instalação sintética ' + [Guid]::NewGuid().ToString('N'))
$install=Join-Path $lab 'Aplicativo com espaços e acentuação'
$state=Join-Path $env:RUNNER_TEMP ([Guid]::NewGuid().ToString())
function Invoke-Child([string]$Executable,[string[]]$Arguments,[bool]$Shell=$false) {
    $process=[Diagnostics.Process]::new()
    $process.StartInfo=[Diagnostics.ProcessStartInfo]::new([IO.Path]::GetFullPath($Executable))
    $process.StartInfo.UseShellExecute=$Shell
    if (-not $Shell) {
        $process.StartInfo.Environment['PATH']="$env:WINDIR/System32;$env:WINDIR"
        foreach ($key in @('PYTHONHOME','PYTHONPATH','GDAL_DATA','PROJ_DATA','PROJ_LIB','QT_PLUGIN_PATH','QTWEBENGINEPROCESS_PATH','QTWEBENGINE_RESOURCES_PATH','QTWEBENGINE_LOCALES_PATH')) { $process.StartInfo.Environment.Remove($key) | Out-Null }
    }
    foreach ($argument in $Arguments) { $process.StartInfo.ArgumentList.Add($argument) }
    try {
        $process.Start() | Out-Null
        if (-not $process.WaitForExit(300000)) { $process.Kill($true); throw 'Installed process timeout.' }
        if ($process.ExitCode -ne 0) { throw ('Installed process failed: ' + [IO.Path]::GetFileName($Executable) + ', exit ' + $process.ExitCode) }
    } finally { $process.Dispose() }
}
function Install([string]$Package,[string]$Label) {
    Invoke-Child $Package @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-','/TASKS=desktopicon',('/DIR='+$install),('/LOG='+$output+'/'+$Label+'.log'))
}
function Probe([string]$Phase,[string]$Label) {
    Invoke-Child (Join-Path $install 'AgroLines.exe') @('--installed-probe',$Phase,$fixture,$state,(Join-Path $output ($Label+'.json')))
}
$foreign=Join-Path $lab 'Outra instalação preservada'
New-Item $foreign -ItemType Directory -Force | Out-Null
[IO.File]::WriteAllText((Join-Path $foreign 'AgroLines.exe'),'inert foreign-install sentinel')
$refused=$false
try {
    Invoke-Child $Installer @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR='+$foreign),('/LOG='+$output+'/foreign-refusal.log'))
} catch {
    if ($_.Exception.Message -notmatch 'exit [1-9]') { throw }
    $refused=$true
}
if (-not $refused -or [IO.File]::ReadAllText((Join-Path $foreign 'AgroLines.exe')) -cne 'inert foreign-install sentinel' -or
    (Test-Path (Join-Path $foreign 'AgroLines.test-channel'))) { throw 'Unrelated installation was overwritten.' }
Install $Installer 'clean-install'
$registration='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{77EA2840-FDA9-4634-88DA-FC049E901050}_is1'
if ((Get-ItemProperty $registration).DisplayVersion -ne $Version) { throw 'Installed version not registered.' }
$desktopShortcut=Join-Path ([Environment]::GetFolderPath('CommonDesktopDirectory')) 'AgroLines TESTE.lnk'
if (-not (Test-Path $desktopShortcut)) { throw 'Opted-in desktop shortcut missing.' }
$first=Get-Content (Join-Path $install 'AgroLines.current.txt') -Raw
$first=$first.Trim()
$old=Join-Path $install ('versions/'+$first+'/AgroLines.exe')
$oldHash=(Get-FileHash $old -Algorithm SHA256).Hash
$shortcut=Join-Path ([Environment]::GetFolderPath('CommonStartMenu')) 'Programs/AgroLines TESTE/AgroLines TESTE.lnk'
if (-not (Test-Path $shortcut)) { throw 'Start menu shortcut missing.' }
$shell=New-Object -ComObject WScript.Shell
$link=$shell.CreateShortcut($shortcut)
if ($link.TargetPath -ine (Join-Path $install 'AgroLines.exe')) { throw 'Incorrect shortcut target.' }
# Clone only the disposable lab link to pass explicit synthetic test arguments.
$copy=$shell.CreateShortcut((Join-Path $lab 'Atalho de teste.lnk'))
$copy.TargetPath=$link.TargetPath
$copy.WorkingDirectory=$link.WorkingDirectory
$copy.Arguments='--installed-probe initialize "'+$fixture+'" "'+$state+'" "'+(Join-Path $output 'shortcut-initial.json')+'"'
$copy.Save()
Invoke-Child (Join-Path $lab 'Atalho de teste.lnk') @() $true
Probe 'verify' 'reopen-after-install'
Install $Upgrade 'upgrade'
if ((Get-ItemProperty $registration).DisplayVersion -ne $UpgradeVersion) { throw 'Upgrade version not registered.' }
$second=(Get-Content (Join-Path $install 'AgroLines.current.txt') -Raw).Trim()
if ($first -eq $second -or -not (Test-Path $old) -or (Get-FileHash $old -Algorithm SHA256).Hash -cne $oldHash) { throw 'Previous runtime not preserved byte for byte.' }
Probe 'verify' 'after-upgrade'
# Both actual installed versions remain independently executable with their own runtime.
Invoke-Child $old @('--installed-probe','verify',$fixture,$state,(Join-Path $output 'old-version-side-by-side.json'))
$uninstaller=Join-Path $install 'uninstall/unins000.exe'
if (-not (Test-Path $uninstaller)) { throw 'Uninstaller missing.' }
Invoke-Child $uninstaller @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/LOG='+$output+'/uninstall.log'))
if (Test-Path (Join-Path $install 'AgroLines.exe')) { throw 'Owned launcher remained after uninstall.' }
if (Test-Path $registration) { throw 'Owned uninstall registration remained.' }
foreach ($file in @('license.dpapi','projects/project.agrolines','projects/backup.agrolines','projects/restored.agrolines')) {
    if (-not (Test-Path (Join-Path $state $file))) { throw 'User state deleted by uninstall.' }
}
Install $Installer 'reinstall'
Probe 'verify' 'after-reinstall'
Probe 'cleanup' 'cleanup-anchor'
$report=@{clean_install=$true;foreign_installation_refused=$true;installer_executed=$true;start_menu_shortcut_started=$true;optional_desktop_shortcut=$true;version_registration=$true;unicode_and_spaces_path=$true;upgraded=$true;old_runtime_preserved=$true;old_version_executed=$true;uninstalled=$true;reinstalled=$true;projects_preserved=$true;activation_preserved=$true;server_builder_only=$true;windows11_physical=$false;sac_approved=$false;production_https_activation_proven=$false;protections_modified=$false}
$report | ConvertTo-Json | Set-Content (Join-Path $output 'result.json') -Encoding utf8
Write-Output ('AGROLINES_INSTALLATION_CYCLE='+($report | ConvertTo-Json -Compress))
