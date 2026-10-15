# Fresh copies, synthetic HDF5 only. Never call the original restricted encoder.
param([switch]$AuthorizedHyperVBuildVM)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Assert-Laboratory.ps1') -AuthorizedHyperVBuildVM:$AuthorizedHyperVBuildVM -BuildOnly
$site=[IO.Path]::GetFullPath('build-env/Lib/site-packages')
$lab=Join-Path $env:RUNNER_TEMP ('agrolines-codec-' + [Guid]::NewGuid().ToString('N'))
New-Item $lab -ItemType Directory | Out-Null
$record=Get-Content build/legal-native/provenance.json -Raw | ConvertFrom-Json
foreach ($variant in @('bsd','original-decoder')) {
    $directory=Join-Path $lab $variant
    New-Item $directory -ItemType Directory | Out-Null
    Copy-Item "$site/fiona" "$directory/fiona" -Recurse
    Copy-Item "$site/fiona.libs" "$directory/fiona.libs" -Recurse
    $probeArguments=@('tools/legal-native/hdf5_probe.py','--prefix',$directory,'--file',"$lab/synthetic.h5",'--report',"evidence/standalone/hdf5/$variant.json")
    if ($variant -eq 'bsd') {
        Copy-Item $record.binary (Join-Path $directory ('fiona.libs/' + [IO.Path]::GetFileName($record.replaced_slot))) -Force
        $probeArguments += '--write-with-bsd-codec'
    }
    & ./build-env/Scripts/python.exe @probeArguments
    if ($LASTEXITCODE) { throw 'Codec/HDF5 byte-level interop failed.' }
}
