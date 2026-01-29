# Complete Setup Script for Windows
# Run this script in PowerShell from the backend folder

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LaNature - Setup Backend (Windows)  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "app")) {
    Write-Host "ERROR: Run this script from the backend folder!" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found! Install Python first." -ForegroundColor Red
    exit 1
}
Write-Host "Python found: $pythonVersion" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Update pip
Write-Host "`nUpdating pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Try to install psycopg2-binary with different approaches
Write-Host "`nInstalling psycopg2-binary..." -ForegroundColor Yellow
Write-Host "Attempt 1: Default version..." -ForegroundColor Cyan
pip install psycopg2-binary --no-cache-dir 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Attempt 2: Latest version..." -ForegroundColor Cyan
    pip install psycopg2-binary --upgrade --no-cache-dir 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nWARNING: Could not install psycopg2-binary automatically" -ForegroundColor Yellow
        Write-Host "`nOptions:" -ForegroundColor Yellow
        Write-Host "1. Install PostgreSQL Client Tools: https://www.postgresql.org/download/windows/" -ForegroundColor White
        Write-Host "2. Use SQLite for development (set DATABASE_URL=sqlite:///./lanature.db in .env)" -ForegroundColor White
        Write-Host "3. Use Docker with PostgreSQL" -ForegroundColor White
        Write-Host "`nContinuing with other dependencies..." -ForegroundColor Yellow
        
        # Install other dependencies without psycopg2-binary
        pip install fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] bcrypt python-multipart pydantic pydantic-settings python-dotenv email-validator
        
        Write-Host "`nTo use SQLite, set DATABASE_URL=sqlite:///./lanature.db in .env file" -ForegroundColor Cyan
    } else {
        Write-Host "psycopg2-binary installed successfully!" -ForegroundColor Green
    }
} else {
    Write-Host "psycopg2-binary installed successfully!" -ForegroundColor Green
}

# Install other dependencies
Write-Host "`nInstalling other dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  Installation completed successfully!     " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Configure the .env file with your credentials" -ForegroundColor White
    Write-Host "2. Create PostgreSQL database or use SQLite" -ForegroundColor White
    Write-Host "3. Run: uvicorn app.main:app --reload" -ForegroundColor White
} else {
    Write-Host "`nERROR: Failed to install some dependencies" -ForegroundColor Red
    Write-Host "Check the errors above and consult README.md" -ForegroundColor Yellow
}
