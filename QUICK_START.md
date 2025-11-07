# Quick Start: Push to GitHub

## ⚠️ Important: You need a Personal Access Token (PAT)

GitHub no longer accepts passwords. Follow these steps:

## Step 1: Create a Personal Access Token (2 minutes)

1. Go to: https://github.com/settings/tokens/new
2. Token name: `Flask React Project`
3. Expiration: Choose your preference (90 days recommended)
4. Select scope: **Check `repo`** (this gives full access to repositories)
5. Click **"Generate token"** at the bottom
6. **COPY THE TOKEN** (you'll see it only once!)

## Step 2: Run the push script

Open PowerShell in this directory and run:

```powershell
.\push-to-github.ps1 -GitHubToken "YOUR_PAT_HERE"
```

Replace `YOUR_PAT_HERE` with the token you copied.

## Alternative: Manual Method

If you prefer to create the repository manually:

1. **Create repository on GitHub:**
   - Go to: https://github.com/new
   - Repository name: `flask-react-assessment-Rajeebdas`
   - Choose Public
   - **DO NOT** check any initialization options
   - Click "Create repository"

2. **Push your code:**
   ```powershell
   # Stage changes
   git add .
   
   # Commit
   git commit -m "Initial commit - Flask React Assessment"
   
   # Push (replace YOUR_PAT with your token)
   git push https://Rajeebdas:YOUR_PAT@github.com/Rajeebdas/flask-react-assessment-Rajeebdas.git main
   ```

## Done! 🎉

Your repository will be at: https://github.com/Rajeebdas/flask-react-assessment-Rajeebdas

