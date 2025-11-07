# Script to push code to existing GitHub repository
# Use this after creating the repository manually on GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$Token
)

$repoName = "flask-react-assessment-Rajeebdas"
$username = "Rajeebdas"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host "`n=== Pushing Code to GitHub ===" -ForegroundColor Cyan

# Configure remote
Write-Host "Configuring remote..." -ForegroundColor Yellow
git remote remove github-user 2>$null
git remote add github-user $repoUrl
Write-Host "Remote configured" -ForegroundColor Green

# Push using token
$pushUrl = "https://${username}:${Token}@github.com/${username}/${repoName}.git"
Write-Host "Pushing to main branch..." -ForegroundColor Yellow

git push $pushUrl main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS! Code pushed to GitHub" -ForegroundColor Green
    Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
} else {
    Write-Host "`nPush failed. Please check:" -ForegroundColor Red
    Write-Host "1. Repository exists at: $repoUrl" -ForegroundColor Yellow
    Write-Host "2. Token has 'repo' scope" -ForegroundColor Yellow
    Write-Host "3. You have write access to the repository" -ForegroundColor Yellow
}

