# Building Defect Detection System - PowerShell Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Defect Detection System" -ForegroundColor Cyan
Write-Host "Advanced AI-Powered Analysis" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if Flask is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$flaskInstalled = pip list | Select-String -Pattern "Flask"

if (-Not $flaskInstalled) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

# Create necessary directories
$directories = @("uploads", "chat_history", "static\temp")
foreach ($dir in $directories) {
    if (-Not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Flask Application..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Green
Write-Host "http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run Flask app
python flask_app.py
