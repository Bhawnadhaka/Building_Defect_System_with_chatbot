# Git Deployment Helper Script
# Run this in PowerShell after creating GitHub repo

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Git Deployment Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit
}

Write-Host "✅ Git is installed" -ForegroundColor Green
Write-Host ""

# Get GitHub username
Write-Host "Enter your GitHub username:" -ForegroundColor Yellow
$username = Read-Host

# Get repository name (default: building-defect-detection)
Write-Host "Enter repository name (press Enter for 'building-defect-detection'):" -ForegroundColor Yellow
$repoName = Read-Host
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "building-defect-detection"
}

Write-Host ""
Write-Host "Repository URL will be: https://github.com/$username/$repoName" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Create this repository on GitHub first!" -ForegroundColor Red
Write-Host "Go to: https://github.com/new" -ForegroundColor Yellow
Write-Host "Repository name: $repoName" -ForegroundColor Yellow
Write-Host "Visibility: Public (required for Render free tier)" -ForegroundColor Yellow
Write-Host "Do NOT initialize with README" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key after creating the repository..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Initializing Git repository..." -ForegroundColor Cyan

# Initialize git
git init

# Add all files
Write-Host "Adding files..." -ForegroundColor Cyan
git add .

# Commit
Write-Host "Committing changes..." -ForegroundColor Cyan
git commit -m "Initial commit - Building Defect Detection System"

# Add remote
Write-Host "Adding remote repository..." -ForegroundColor Cyan
git remote add origin "https://github.com/$username/$repoName.git"

# Set branch
Write-Host "Setting main branch..." -ForegroundColor Cyan
git branch -M main

# Push
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "You may need to enter your GitHub credentials" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code is now on GitHub!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/$username/$repoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Upload best_defect_model.pth to Google Drive" -ForegroundColor White
    Write-Host "2. Get the file ID from the sharing link" -ForegroundColor White
    Write-Host "3. Update render-build.sh with the file ID" -ForegroundColor White
    Write-Host "4. Go to render.com and deploy!" -ForegroundColor White
    Write-Host ""
    Write-Host "See DEPLOY_QUICK.md for detailed instructions" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Red
    Write-Host "❌ ERROR OCCURRED" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error message above" -ForegroundColor Yellow
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Repository doesn't exist on GitHub" -ForegroundColor White
    Write-Host "- Wrong username or repository name" -ForegroundColor White
    Write-Host "- Authentication failed" -ForegroundColor White
    Write-Host ""
    Write-Host "For authentication, you may need a Personal Access Token" -ForegroundColor Yellow
    Write-Host "Create one at: https://github.com/settings/tokens" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
