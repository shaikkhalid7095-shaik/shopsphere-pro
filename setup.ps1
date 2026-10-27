# ShopSphere Pro - one time setup for Windows
#
# Easiest:   powershell -ExecutionPolicy Bypass -File .\setup.ps1
#            (it will ask for your MySQL password)
# One line:  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -DbPassword yourpass

param(
    [string]$DbUser = "",
    [string]$DbPassword = $null,
    [string]$DbName = ""
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:DISABLE_SQLALCHEMY_CEXT_RUNTIME = "1"   # avoids the Windows "Application Control policy" DLL block

function Step($text) { Write-Host "`n>> $text" -ForegroundColor Cyan }
function Fail($text) { Write-Host "`n[X] $text" -ForegroundColor Red; exit 1 }

Write-Host "=== ShopSphere Pro setup ===" -ForegroundColor Green

# 1. python
Step "Checking Python"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { Fail "Python not found. Install Python 3.10+ from python.org and tick 'Add to PATH'." }
python --version

# 2. virtual environment + packages
Step "Creating virtual environment (.venv)"
if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Fail "Could not create .venv - try running: python -m venv .venv" }

Step "Installing packages (takes a minute the first time)"
& $py -m pip install --upgrade pip --quiet --no-warn-script-location
& $py -m pip install -r requirements.txt --quiet --no-warn-script-location
if ($LASTEXITCODE -ne 0) { Fail "pip install failed - check your internet connection" }

# 3. .env file
Step "Setting up .env"
if (Test-Path ".env") {
    Write-Host ".env already exists - keeping it (delete it and rerun to start over)"
} else {
    if (-not $DbUser) { $DbUser = Read-Host "MySQL username [root]" }
    if (-not $DbUser) { $DbUser = "root" }
    if ($null -eq $DbPassword) {
        $secure = Read-Host "MySQL password" -AsSecureString
        $DbPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
    }
    if (-not $DbName) { $DbName = Read-Host "Database name [shopsphere]" }
    if (-not $DbName) { $DbName = "shopsphere" }

    $chars = (48..57) + (65..90) + (97..122)
    $jwt = -join ($chars | Get-Random -Count 48 | ForEach-Object { [char]$_ })

    $lines = Get-Content ".env.example" | ForEach-Object {
        if ($_ -like "DB_USER=*") { "DB_USER=$DbUser" }
        elseif ($_ -like "DB_PASSWORD=*") { "DB_PASSWORD='$DbPassword'" }
        elseif ($_ -like "DB_NAME=*") { "DB_NAME=$DbName" }
        elseif ($_ -like "JWT_SECRET=*") { "JWT_SECRET=`"$jwt`"" }
        else { $_ }
    }
    # write without BOM so python reads it cleanly
    [System.IO.File]::WriteAllLines((Join-Path $PSScriptRoot ".env"), $lines)
    Write-Host ".env created"
}

# 4. database
Step "Creating MySQL database"
& $py create_db.py
if ($LASTEXITCODE -ne 0) { Fail "Fix the MySQL problem above, then run setup.ps1 again" }

Step "Creating tables (alembic upgrade head)"
& $py -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { Fail "Migration failed" }

Step "Loading sample data"
& $py seed.py
if ($LASTEXITCODE -ne 0) { Fail "Seeding failed" }

Write-Host "`n=== Setup done! ===" -ForegroundColor Green
Write-Host "Start the API with:   .\run.ps1"
Write-Host "Run the tests with:   .\test.ps1"