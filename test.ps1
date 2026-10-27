# Run all unit + integration tests (uses a temporary sqlite file, your MySQL data is not touched)
# Run:  powershell -ExecutionPolicy Bypass -File .\test.ps1
# To test against MySQL instead:  .\test.ps1 -MySql

param([switch]$MySql)

Set-Location $PSScriptRoot
$env:DISABLE_SQLALCHEMY_CEXT_RUNTIME = "1"   # avoids the Windows "Application Control policy" DLL block
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Host "Run setup.ps1 first" -ForegroundColor Red; exit 1 }

if ($MySql) {
    # makes a separate shopsphere_test database using the login in .env
    $env:DB_NAME = "shopsphere_test"
    & $py create_db.py
    $env:TEST_DATABASE_URL = & $py -c "from app.config import settings; print(settings.db_url)"
    Remove-Item Env:DB_NAME
}

& $py -m pytest -v
Remove-Item Env:TEST_DATABASE_URL -ErrorAction SilentlyContinue