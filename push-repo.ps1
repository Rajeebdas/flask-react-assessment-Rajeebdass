# Push code to GitHub repository: flask-react-assessment-Rajeebdass
param(
    [Parameter(Mandatory=$true)]
    [string]$Token
)

$repoName = "flask-react-assessment-Rajeebdass"
$username = "Rajeebdas"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host "`n=== Pushing to GitHub Repository ===" -ForegroundColor Cyan
Write-Host "Repository: $repoName" -ForegroundColor White
Write-Host "URL: $repoUrl`n" -ForegroundColor White

# Remove old remote if exists and add new one
Write-Host "Configuring git remote..." -ForegroundColor Yellow
git remote remove github-user 2>$null
git remote add github-user $repoUrl
Write-Host "Remote configured: github-user -> $repoUrl" -ForegroundColor Green

# Push using token
$pushUrl = "https://${username}:${Token}@github.com/${username}/${repoName}.git"
Write-Host "`nPushing code to main branch..." -ForegroundColor Yellow

git push $pushUrl main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓✓✓ SUCCESS! ✓✓✓" -ForegroundColor Green
    Write-Host "Your code has been pushed to:" -ForegroundColor Cyan
    Write-Host "  https://github.com/$username/$repoName" -ForegroundColor Cyan
} else {
    Write-Host "`n✗ Push failed!" -ForegroundColor Red
    Write-Host "`nPlease check:" -ForegroundColor Yellow
    Write-Host "  1. Repository exists at: $repoUrl" -ForegroundColor White
    Write-Host "  2. Token has 'repo' scope (create new token at: https://github.com/settings/tokens/new)" -ForegroundColor White
    Write-Host "  3. Repository name is correct: $repoName" -ForegroundColor White
}

