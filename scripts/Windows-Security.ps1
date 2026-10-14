# Read-only evidence helpers. Importing this file changes no Windows setting.
function Get-AgroSacState {
    $evidence = [ordered]@{ registry_state = $null; policies = @(); errors = @(); active_confirmed = $false }
    try {
        $evidence.registry_state = (Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy' -Name VerifiedAndReputablePolicyState).VerifiedAndReputablePolicyState
    } catch { $evidence.errors += 'SAC registry evidence unavailable' }
    try {
        $tool = Join-Path $env:WINDIR 'System32\CiTool.exe'
        $text = & $tool -lp -json
        if ($LASTEXITCODE -ne 0) { throw 'Policy listing failed' }
        $evidence.policies = @(($text | ConvertFrom-Json).Policies)
        $sac = @($evidence.policies | Where-Object {
            $_.PolicyID.ToString().Trim('{}') -eq '0283ac0f-fff1-49ae-ada1-8a933130cad6' -and $_.IsEnforced -eq $true
        })
        $evidence.active_confirmed = ($evidence.registry_state -eq 1 -and $sac.Count -gt 0)
    } catch { $evidence.errors += 'CiTool read-only evidence unavailable' }
    return [PSCustomObject]$evidence
}

function Get-AgroCodeIntegrityEvents {
    param([DateTime]$Since)
    $log = 'Microsoft-Windows-CodeIntegrity/Operational'
    $info = Get-WinEvent -ListLog $log -ErrorAction Stop
    if (-not $info.IsEnabled) { throw 'Code Integrity log disabled; evidence incomplete.' }
    try {
        return @(Get-WinEvent -FilterHashtable @{ LogName = $log; Id = @(3077,3033); StartTime = $Since } -ErrorAction Stop)
    } catch {
        if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { return @() }
        throw
    }
}

function Convert-AgroCodeIntegrityEvents {
    param([object[]]$Events, [string[]]$NativeNames)
    foreach ($event in $Events) {
        $xml = $event.ToXml()
        [xml]$parsed = $xml
        $values = @($parsed.Event.EventData.Data | ForEach-Object { $_.InnerText })
        $related = $false
        foreach ($name in $NativeNames) {
            # File names also match NT-device paths. False positives require review, never exemption.
            if (($values -join "`n").IndexOf($name, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $related = $true
                break
            }
        }
        [PSCustomObject]@{
            id = $event.Id; record_id = $event.RecordId
            created_utc = $event.TimeCreated.ToUniversalTime().ToString('o')
            associated_with_inventory = $related; xml = $xml
        }
    }
}
