param (
    [Parameter(Mandatory=$true)]
    [ValidateSet('major', 'minor', 'patch')]
    [string]$versionPart
)

$currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
if ($currentBranch -ne "main") {
    Write-Error "Must be on main branch to release. Currently on: $currentBranch"
    exit 1
}

$status = git status --porcelain
if ($status) {
    Write-Error "You have uncommitted changes. Commit or stash them first."
    exit 1  
}

try {
    poetry version $versionPart
} catch {
    Write-Error "Poetry version bump failed."
    exit 1
}

$tag = "v" + (poetry version -s).Trim()

if (-not $tag) {
    Write-Error "Could not retrieve the new version number from 'poetry version -s'."
    exit 1
}

$repoUrl = "https://github.com/dstoffels/localis"
$tsvUrl = "$repoUrl/releases/download/$tag/cities.tsv"

python -c @"
from localis.data import MetaStore
from localis import CityRegistry
meta = MetaStore()
meta.set(CityRegistry.META_URL_KEY, '$tsvUrl')
print(f'Updated TSV URL to: $tsvUrl')
"@

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to update database metadata."
    exit 1
}

Write-Host "Releasing $tag" -ForegroundColor Green

git add .\pyproject.toml .\src\localis\data\localis.db
git commit -m "Release $tag"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Git commit failed."
    exit 1
}

git tag -a "$tag" -m "Release $tag"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Git tag failed."
    exit 1
}
$confirm = Read-Host "Push $tag to origin/main? (y/n)"
if ($confirm -eq 'y') {
    git push origin main --tags
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Git push failed."
        exit 1
    }
    Write-Host "Release $tag pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "Push cancelled. To push later: git push origin main --tags"
}
