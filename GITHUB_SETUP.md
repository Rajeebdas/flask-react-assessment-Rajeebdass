# GitHub Repository Setup Guide

## Important: GitHub requires a Personal Access Token (PAT)

GitHub no longer accepts passwords for authentication. You need to create a Personal Access Token.

## Step 1: Create a Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "Flask React Project")
4. Select scopes: at minimum, check `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

## Step 2: Create the Repository

You have two options:

### Option A: Create via GitHub Web Interface (Recommended)
1. Go to: https://github.com/new
2. Repository name: `flask-react-assessment-Rajeebdas`
3. Choose Public or Private
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

### Option B: Use the setup script (requires PAT)
Run: `.\setup-github.ps1 -GitHubToken <YOUR_PAT>`

## Step 3: Push to GitHub

After you have the PAT and repository created, run these commands:

```powershell
# Add your GitHub remote
git remote add github-user https://github.com/Rajeebdas/flask-react-assessment-Rajeebdas.git

# Stage all changes
git add .

# Commit changes
git commit -m "Initial commit - Flask React Assessment"

# Push to your GitHub (replace <YOUR_PAT> with your actual token)
git push https://Rajeebdas:<YOUR_PAT>@github.com/Rajeebdas/flask-react-assessment-Rajeebdas.git main
```

Or set up credential helper:
```powershell
# Configure git to use your PAT
git config --global credential.helper store
# Then when you push, enter your username and use PAT as password
git push github-user main
```

