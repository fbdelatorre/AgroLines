# Real signed-package gate; read-only security checks. No self-signed cert, bypass or Developer Mode.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$FirstPackage,
    [Parameter(Mandatory)][string]$UpdatePackage,
    [string]$OutputDirectory = 'evidence/msix-installed',
    [switch]$RequireSac,
    [switch]$RequireCleanMachine,
    [switch]$RequireDisconnected
)
$ErrorActionPreference = 'Stop'
function Assert-AgroDefenderActive {
    $state = Get-MpComputerStatus -ErrorAction Stop
    if (-not $state.AMServiceEnabled -or -not $state.AntivirusEnabled -or -not $state.RealTimeProtectionEnabled) { throw 'Active Defender and real-time protection required; script changes no settings.' }
    return ($state | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled)
}
$defenderBefore = Assert-AgroDefenderActive
. (Join-Path $PSScriptRoot 'Activate-Packaged.ps1')
. (Join-Path $PSScriptRoot '../../../scripts/Windows-Security.ps1')
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Read-AgroSignedPackage([string]$File) {
    $signature = Get-AuthenticodeSignature $File
    if ($signature.Status -ne 'Valid' -or -not $signature.SignerCertificate -or
        $signature.SignerCertificate.Subject -eq $signature.SignerCertificate.Issuer) {
        throw 'Exigir pacote com assinatura confiavel; nao instalar certificado autoassinado.'
    }
    $archive = [IO.Compression.ZipFile]::OpenRead([IO.Path]::GetFullPath($File))
    try {
        $entry = $archive.GetEntry('AppxManifest.xml')
        if (-not $entry) { throw 'Manifesto ausente.' }
        $settings = [Xml.XmlReaderSettings]::new()
        $settings.DtdProcessing = [Xml.DtdProcessing]::Prohibit
        $settings.XmlResolver = $null
        $stream = $entry.Open()
        try {
            $reader = [Xml.XmlReader]::Create($stream, $settings)
            try { $manifest = [Xml.XmlDocument]::new(); $manifest.Load($reader) }
            finally { $reader.Dispose() }
        } finally { $stream.Dispose() }
        $ns = [Xml.XmlNamespaceManager]::new($manifest.NameTable)
        $ns.AddNamespace('f','http://schemas.microsoft.com/appx/manifest/foundation/windows10')
        $declared = $manifest.SelectSingleNode('/f:Package/f:Identity',$ns)
        $publisherName = $manifest.SelectSingleNode('/f:Package/f:Properties/f:PublisherDisplayName',$ns).InnerText
        if ($declared.GetAttribute('Name') -cne 'DelatorreCOrporation.AgroLines' -or
            $declared.GetAttribute('Publisher') -cne 'CN=43189595-B928-4D57-90A4-24300E4D4976' -or
            $declared.GetAttribute('ProcessorArchitecture') -cne 'x64' -or $publisherName -cne 'Delatorre COrporation') {
            throw 'Identidade oficial divergente; nao substituir Publisher.'
        }
        return [version]($declared.GetAttribute('Version'))
    } finally { $archive.Dispose() }
}
$firstVersion = Read-AgroSignedPackage $FirstPackage
$nextVersion = Read-AgroSignedPackage $UpdatePackage
if ($nextVersion -le $firstVersion) { throw 'Atualizacao deve aumentar a versao.' }
$alreadyInstalled = Get-AppxPackage -Name 'DelatorreCOrporation.AgroLines'
if ($alreadyInstalled) { throw 'Use bancada limpa: nao alterar/remover aplicativo existente do usuario.' }
if ($RequireCleanMachine) {
    $uninstallRoots = @('HKLM:/Software/Microsoft/Windows/CurrentVersion/Uninstall/*',
        'HKLM:/Software/WOW6432Node/Microsoft/Windows/CurrentVersion/Uninstall/*',
        'HKCU:/Software/Microsoft/Windows/CurrentVersion/Uninstall/*')
    $software = Get-ItemProperty $uninstallRoots -ErrorAction SilentlyContinue
    if ($software.DisplayName -match '(?i)\b(Python|PostgreSQL)\b' -or
        (Get-Service | Where-Object Name -Match '(?i)postgres') -or
        (Get-AppxPackage -Name '*PythonSoftwareFoundation*')) { throw 'Bancada deve estar sem Python/PostgreSQL instalados.' }
}
if ($RequireDisconnected -and (Get-NetAdapter -ErrorAction Stop | Where-Object Status -EQ 'Up')) {
    throw 'Desconecte todos os adaptadores da bancada; script nao altera rede/protecoes.'
}
if ($RequireSac) {
    $security = Get-AgroSacState
    $os = Get-CimInstance Win32_OperatingSystem
    if ($os.ProductType -ne 1 -or [int]$os.BuildNumber -lt 22000 -or -not $security.active_confirmed) { throw 'Exigir Windows 11 real com SAC On.' }
}
if ((Test-Path "$OutputDirectory/first.json") -or (Test-Path "$OutputDirectory/update.json")) {
    throw 'Use pasta de evidencias nova antes de instalar.'
}
New-Item $OutputDirectory -ItemType Directory -Force | Out-Null
$started = [DateTime]::Now
$nativeNames = @('AgroLinesPoC.exe','QtWebEngineProcess.exe','_multiarray_umath')
$projectDirectory = Join-Path $env:LOCALAPPDATA ('AgroLines/Projects/msix-validation-' + [guid]::NewGuid())
$initialPath = $env:PATH
$removedVariables = @{}
$summary = @{ installed_msix_validated=$false; real_clean_disconnected_sac_acceptance=$false; projects_preserved=$false }
$summary.defender_before = $defenderBefore
try {
    $env:PATH = Join-Path $env:WINDIR 'System32'
    foreach ($name in @('PYTHONHOME','PYTHONPATH','PROJ_LIB','PROJ_DATA','GDAL_DATA','QT_PLUGIN_PATH','QTWEBENGINEPROCESS_PATH')) {
        $removedVariables[$name] = [Environment]::GetEnvironmentVariable($name,'Process')
        [Environment]::SetEnvironmentVariable($name,$null,'Process')
    }
    Add-AppxPackage -Path ([IO.Path]::GetFullPath($FirstPackage)) -ErrorAction Stop
    $installed = Get-AppxPackage -Name 'DelatorreCOrporation.AgroLines'
    if ($installed.PackageFamilyName -cne 'DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg' -or $installed.Version -ne $firstVersion) { throw 'Instalacao divergente.' }
    $nativeNames = @(Get-ChildItem $installed.InstallLocation -Recurse -File | Where-Object Extension -In @('.dll','.pyd','.exe') | Select-Object -ExpandProperty Name -Unique)
    $first = Invoke-AgroPackageProbe -Report "$OutputDirectory/first.json" -ProjectDirectory $projectDirectory
    $formats = Invoke-AgroPackageOfflineFormatsProbe -Report "$OutputDirectory/formats.json"
    $before = (Get-FileHash "$projectDirectory/project.agrolines" -Algorithm SHA256).Hash
    Add-AppxPackage -Path ([IO.Path]::GetFullPath($UpdatePackage)) -ErrorAction Stop
    $installed = Get-AppxPackage -Name 'DelatorreCOrporation.AgroLines'
    if ($installed.Version -ne $nextVersion) { throw 'Versao MSIX nao atualizada.' }
    $next = Invoke-AgroPackageProbe -Report "$OutputDirectory/update.json" -ProjectDirectory $projectDirectory
    if (-not $next.offline_projects.existing_project_preserved -or
        (Get-FileHash "$projectDirectory/project.agrolines" -Algorithm SHA256).Hash -ne $before) { throw 'Projeto mudou na atualizacao.' }
    if ($RequireSac -and (-not $first.sac_run_observed -or -not $next.sac_run_observed)) { throw 'Evidencia SAC/CodeIntegrity insuficiente.' }
    Remove-AppxPackage -Package $installed.PackageFullName -ErrorAction Stop
    if ((Get-FileHash "$projectDirectory/project.agrolines" -Algorithm SHA256).Hash -ne $before) { throw 'Desinstalacao removeu/alterou projeto.' }
    if ($RequireSac) {
        $events = @(Get-AgroCodeIntegrityEvents -Since $started)
        $related = @(Convert-AgroCodeIntegrityEvents -Events $events -NativeNames $nativeNames)
        $related | ConvertTo-Json -Depth 12 | Set-Content "$OutputDirectory/package-events.json" -Encoding utf8
        if (@($related | Where-Object associated_with_inventory).Count -gt 0 -or -not (Get-AgroSacState).active_confirmed) {
            throw 'Bloqueio/mudanca de SAC durante instalacao/atualizacao/desinstalacao.'
        }
    }
    if ($RequireDisconnected -and (Get-NetAdapter -ErrorAction Stop | Where-Object Status -EQ 'Up')) {
        throw 'Bancada reconectada antes de concluir a validacao offline.'
    }
    $summary.installed_msix_validated = $true
    $summary.projects_preserved = $true
    $summary.real_clean_disconnected_sac_acceptance = [bool]($RequireSac -and $RequireCleanMachine -and $RequireDisconnected)
    $summary.first_version = "$firstVersion"
    $summary.update_version = "$nextVersion"
    $summary.project_sha256 = $before
    $summary.project_directory = $projectDirectory
    $summary.local_formats = $formats.local_formats
    $summary.defender_after = Assert-AgroDefenderActive
} finally {
    $env:PATH = $initialPath
    foreach ($name in $removedVariables.Keys) { [Environment]::SetEnvironmentVariable($name,$removedVariables[$name],'Process') }
    $summary | ConvertTo-Json | Set-Content "$OutputDirectory/summary.json" -Encoding utf8
}
