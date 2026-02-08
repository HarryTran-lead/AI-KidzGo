@echo off
echo === AI-KidzGo Setup & Run ===

echo.
echo 1. Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo 2. Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo 3. Starting FastAPI server...
echo Swagger UI will be available at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

