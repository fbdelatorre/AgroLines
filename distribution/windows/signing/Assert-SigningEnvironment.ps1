# Refuse signing on PRs, feature branches, unprotected environments or unknown repository.
$ErrorActionPreference = 'Stop'
if ($env:GITHUB_EVENT_NAME -cne 'workflow_dispatch' -or $env:GITHUB_REF -cne 'refs/heads/main' -or
    $env:GITHUB_REPOSITORY -cne 'fbdelatorre/AgroLines' -or $env:GITHUB_SHA -notmatch '^[a-f0-9]{40}$' -or
    -not $env:GITHUB_TOKEN) { throw 'Only an authorized dispatch of protected main can use the signing runner.' }
$headers = @{ Authorization = 'Bearer ' + $env:GITHUB_TOKEN; Accept = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
$base = 'https://api.github.com/repos/fbdelatorre/AgroLines'
try {
    $branch = Invoke-RestMethod -Uri "$base/branches/main" -Headers $headers
    $environment = Invoke-RestMethod -Uri "$base/environments/windows-signing" -Headers $headers
} catch { throw 'Unable to verify protected branch/environment; signing remains disabled.' }
$review = @($environment.protection_rules | Where-Object type -EQ 'required_reviewers')
if (-not $branch.protected -or $branch.commit.sha -cne $env:GITHUB_SHA -or
    -not $environment.deployment_branch_policy.protected_branches -or $review.Count -ne 1 -or
    -not $review[0].reviewers.Count) { throw 'Protected main and manual environment reviewer required; no signing fallback.' }
Write-Output 'Protected main/reviewer/source verified. No key accessed by this guard.'
