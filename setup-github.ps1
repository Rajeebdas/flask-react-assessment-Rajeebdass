# PowerShell script to set up and push to GitHub
# Note: GitHub requires a Personal Access Token (PAT), not a password

param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken
)

$repoName = "flask-react-assessment-Rajeebdas"
$username = "Rajeebdas"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host "Setting up GitHub repository: $repoName" -ForegroundColor Cyan

# If token is provided, try to create the repository
if ($GitHubToken) {
    Write-Host "Creating repository on GitHub..." -ForegroundColor Yellow
    $headers = @{
        "Accept" = "application/vnd.github.v3+json"
        "Authorization" = "token $GitHubToken"
    }
    
    $body = @{
        name = $repoName
        private = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
        Write-Host "Repository created successfully!" -ForegroundColor Green
        Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 422) {
            Write-Host "Repository might already exist. Continuing..." -ForegroundColor Yellow
        } else {
            Write-Host "Error creating repository: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "You may need to create it manually at: https://github.com/new" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "No token provided. Please create the repository manually at: https://github.com/new" -ForegroundColor Yellow
    Write-Host "Repository name: $repoName" -ForegroundColor Cyan
    Write-Host "Press Enter after creating the repository to continue..." -ForegroundColor Yellow
    Read-Host
}

# Add the new remote (or update if it exists)
Write-Host "`nConfiguring git remote..." -ForegroundColor Cyan
git remote remove github-user 2>$null
git remote add github-user $repoUrl

Write-Host "Remote 'github-user' added: $repoUrl" -ForegroundColor Green

# Show current remotes
Write-Host "`nCurrent git remotes:" -ForegroundColor Cyan
git remote -v

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Stage your changes: git add ." -ForegroundColor White
Write-Host "2. Commit your changes: git commit -m 'Your commit message'" -ForegroundColor White
Write-Host "3. Push to your GitHub: git push github-user main" -ForegroundColor White
Write-Host "`nOr if you want to push with token: git push https://${username}:<YOUR_PAT>@github.com/${username}/${repoName}.git main" -ForegroundColor Yellow

