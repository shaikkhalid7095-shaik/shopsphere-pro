# Start the ShopSphere Pro API
# Run:  powershell -ExecutionPolicy Bypass -File .\run.ps1

Set-Location $PSScriptRoot
$env:DISABLE_SQLALCHEMY_CEXT_RUNTIME = "1"   # avoids the Windows "Application Control policy" DLL block
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Run setup.ps1 first" -ForegroundColor Red
    exit 1
}

Write-Host "Swagger docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press CTRL+C to stop`n"
Start-Process "http://127.0.0.1:8000/docs"
& $py -m uvicorn app.main:app --reload --port 8000