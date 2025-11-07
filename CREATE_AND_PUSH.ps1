# Simple script to create GitHub repo and push code
# Run this AFTER creating your Personal Access Token

param(
    [Parameter(Mandatory=$true, HelpMessage="Enter your GitHub Personal Access Token")]
    [string]$Token
)

$repoName = "flask-react-assessment-Rajeebdas"
$username = "Rajeebdas"

Write-Host "`n=== Creating GitHub Repository ===" -ForegroundColor Cyan

# Create repository
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}
$body = @{
    name = $repoName
    private = $false
} | ConvertTo-Json

try {
    $repo = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Repository created: $($repo.html_url)" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 422) {
        Write-Host "Repository already exists" -ForegroundColor Yellow
    } else {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n=== Pushing Code to GitHub ===" -ForegroundColor Cyan

# Configure remote if not exists
$remotes = git remote -v
if ($remotes -notmatch "github-user") {
    git remote add github-user "https://github.com/$username/$repoName.git"
    Write-Host "Remote configured" -ForegroundColor Green
}

# Push using token
$pushUrl = "https://${username}:${Token}@github.com/${username}/${repoName}.git"
Write-Host "Pushing to main branch..." -ForegroundColor Yellow

git push $pushUrl main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/$username/$repoName" -ForegroundColor Cyan
} else {
    Write-Host "`nPush completed with issues. Check output above." -ForegroundColor Yellow
}
