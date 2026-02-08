# Script để chạy AI-KidzGo FastAPI service

Write-Host "=== AI-KidzGo Setup & Run ===" -ForegroundColor Green

# Kiểm tra Python
Write-Host "`n1. Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Cài đặt dependencies
Write-Host "`n2. Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Chạy server
Write-Host "`n3. Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "Swagger UI will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

