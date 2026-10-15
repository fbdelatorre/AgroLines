# Local owner-authorized Hyper-V BUILD VM only. Never installs/starts AgroLines.
param([Parameter(Mandatory)][string]$PublicLabInputs,[switch]$AuthorizedHyperVBuildVM)
$ErrorActionPreference='Stop'
if (-not $AuthorizedHyperVBuildVM) { throw 'Explicit owner authorization of the disposable build VM required.' }
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1') -AuthorizedHyperVBuildVM -BuildOnly
if (-not (Test-Path build-env/Scripts/python.exe)) { throw 'Prepare the locked build environment first; see docs/testing/private-installer.md.' }
$savedTemp=$env:RUNNER_TEMP
try {
    $env:RUNNER_TEMP=[IO.Path]::GetFullPath('build/private-lab-temp')
    New-Item $env:RUNNER_TEMP -ItemType Directory -Force | Out-Null
    $origin=./build-env/Scripts/python.exe -m distribution.private_delivery lab-inputs $PublicLabInputs
    if ($LASTEXITCODE) { throw 'Invalid public laboratory input bundle.' }
    $env:SOURCE_DATE_EPOCH=git show -s --format=%ct HEAD
    $env:PYTHONHASHSEED='0'
    ./distribution/windows/standalone/Build-Libaec.ps1 -AuthorizedHyperVBuildVM
    ./distribution/windows/standalone/Test-Libaec.ps1 -AuthorizedHyperVBuildVM
    ./build-env/Scripts/python.exe -m distribution.source_bundle --cache build/source-cache --output build/source-delivery/AgroLines-Third-Party-Sources.zip
    if ($LASTEXITCODE) { throw 'Source bundle failed.' }
    ./distribution/windows/standalone/Build-GeosSources.ps1 -AuthorizedHyperVBuildVM
    ./distribution/windows/standalone/Prepare-Compiler.ps1 -Directory "$env:RUNNER_TEMP/inno"
    $candidate=(git rev-parse HEAD).Substring(0,12)
    foreach ($version in @('1.0.0.7','1.0.0.8')) {
        ./build-env/Scripts/python.exe -m distribution.build --commercial --version $version --license-origin $origin --public-keys "$PublicLabInputs/public.json" --experimental-licensing --lab-tls-ca "$PublicLabInputs/tls-ca.pem"
        if ($LASTEXITCODE) { throw 'Complete client build failed.' }
        ./distribution/windows/standalone/Build-Launcher.ps1
        ./distribution/windows/Build-Installer.ps1 -Standalone -Experimental -FunctionalTest -Version $version -CandidateId $candidate -Compiler "$env:RUNNER_TEMP/inno/compiler/ISCC.exe" -PythonExecutable ./build-env/Scripts/python.exe
        New-Item evidence/functional -ItemType Directory -Force | Out-Null
        ./build-env/Scripts/python.exe -m distribution.functional_report --payload dist/AgroLines --installer "dist/installers/AgroLines-Setup-$version-TESTE-x64.exe" --commit (git rev-parse HEAD) --output "evidence/functional/artifact-$version.json"
        if ($LASTEXITCODE) { throw 'Candidate measurements failed.' }
        Copy-Item dist/AgroLines/payload-manifest.json "evidence/functional/payload-$version.json"
        Copy-Item evidence/standalone/inno-compile.log "evidence/functional/inno-$version.log"
    }
    Write-Output 'Built locally only; no upload or installation. Perform the separate manual VM checklist. No Windows 11/SAC approval.'
} finally { $env:RUNNER_TEMP=$savedTemp }
