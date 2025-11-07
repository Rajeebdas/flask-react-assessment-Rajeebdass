# Script to create GitHub repository and push code
# Requires: Personal Access Token (PAT) from GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$false)]
    [switch]$CreateRepoOnly
)

$ErrorActionPreference = "Stop"

$repoName = "flask-react-assessment-Rajeebdas"
$username = "Rajeebdas"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host "`n=== GitHub Repository Setup ===" -ForegroundColor Cyan
Write-Host "Repository: $repoName" -ForegroundColor White
Write-Host "Username: $username`n" -ForegroundColor White

# Step 1: Create repository on GitHub
Write-Host "Step 1: Creating repository on GitHub..." -ForegroundColor Yellow
$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "token $GitHubToken"
    "User-Agent" = "PowerShell"
}

$body = @{
    name = $repoName
    description = "Flask React Assessment Project"
    private = $false
    auto_init = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "✓ Repository created successfully!" -ForegroundColor Green
    Write-Host "  URL: $($response.html_url)" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 422) {
        Write-Host "⚠ Repository already exists. Continuing..." -ForegroundColor Yellow
    } elseif ($statusCode -eq 401) {
        Write-Host "✗ Authentication failed. Please check your Personal Access Token." -ForegroundColor Red
        Write-Host "  Make sure your token has 'repo' scope enabled." -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "✗ Error creating repository: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

if ($CreateRepoOnly) {
    Write-Host "`nRepository created. Exiting as requested." -ForegroundColor Cyan
    exit 0
}

# Step 2: Configure git remote
Write-Host "`nStep 2: Configuring git remote..." -ForegroundColor Yellow
git remote remove github-user 2>$null
git remote add github-user $repoUrl
Write-Host "✓ Remote 'github-user' configured" -ForegroundColor Green

# Step 3: Stage all changes
Write-Host "`nStep 3: Staging changes..." -ForegroundColor Yellow
git add .
Write-Host "✓ Changes staged" -ForegroundColor Green

# Step 4: Commit changes
Write-Host "`nStep 4: Committing changes..." -ForegroundColor Yellow
$commitMessage = "Initial commit - Flask React Assessment"
try {
    git commit -m $commitMessage
    Write-Host "✓ Changes committed" -ForegroundColor Green
} catch {
    if ($LASTEXITCODE -eq 1) {
        Write-Host "⚠ No changes to commit or commit failed" -ForegroundColor Yellow
    }
}

# Step 5: Push to GitHub
Write-Host "`nStep 5: Pushing to GitHub..." -ForegroundColor Yellow
$pushUrl = "https://${username}:${GitHubToken}@github.com/${username}/${repoName}.git"

try {
    git push $pushUrl main 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "  Repository: $repoUrl" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠ Push completed with warnings. Check output above." -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Error pushing to GitHub: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nYou can manually push using:" -ForegroundColor Yellow
    Write-Host "  git push github-user main" -ForegroundColor White
    exit 1
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Your repository is available at: $repoUrl" -ForegroundColor Cyan

